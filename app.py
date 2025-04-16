from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime
from functools import wraps
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# Data Structures
class MenuItem:
    def __init__(self, name, price, category, stock=10):
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock
        self.available = stock > 0

class Order:
    def __init__(self, order_id, customer_name, items, placed_by, status="Waiting/Pending"):
        self.order_id = order_id
        self.customer_name = customer_name
        self.items = items
        self.status = status
        self.total_price = sum(item.price for item in items)
        self.timestamp = datetime.now()
        self.placed_by = placed_by

class CafeOrderSystem:
    def __init__(self):
        self.menu = [
            MenuItem("Croissant", 2.50, "Food", 10),
            MenuItem("Muffin", 3.00, "Food", 8),
            MenuItem("Sandwich", 5.00, "Food", 15),
            MenuItem("Iced Coffee", 3.75, "Drinks", 10),
            MenuItem("Lemonade", 2.50, "Drinks", 12),
            MenuItem("Espresso", 3.50, "Hot Drinks", 20),
            MenuItem("Latte", 4.00, "Hot Drinks", 15),
            MenuItem("Orange Juice", 3.00, "Juice", 10),
            MenuItem("Apple Juice", 3.00, "Juice", 8)
        ]
        self.orders = []
        self.order_counter = 1000
        self.users = {
            "customer1": {"password": "pass1", "role": "customer"},
            "staff1": {"password": "pass2", "role": "staff"},
            "manager1": {"password": "pass3", "role": "manager"}
        }

    def update_inventory(self, items):
        for item in items:
            for menu_item in self.menu:
                if menu_item.name == item.name:
                    if menu_item.stock >= 1:
                        menu_item.stock -= 1
                        menu_item.available = menu_item.stock > 0
                    else:
                        return False
        return True

    def get_latest_order_by_customer(self, customer_name):
        return max((o for o in self.orders if o.customer_name == customer_name), default=None, key=lambda x: x.timestamp)

cafe = CafeOrderSystem()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Role required decorator
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session or cafe.users[session['username']]['role'] not in role:
                return "Access Denied", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in cafe.users and cafe.users[username]['password'] == password:
            session['username'] = username
            session['role'] = cafe.users[username]['role']
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    current_user = session['username']
    user_role = session['role']

    if request.method == 'POST':
        if user_role not in ['customer', 'staff']:
            return "Managers cannot place orders.", 403
        
        customer_name = request.form.get('customer_name') or current_user
        selected_items = request.form.getlist('items')
        item_indices = [int(i) for i in selected_items]
        items_to_order = [cafe.menu[i] for i in item_indices if 0 <= i < len(cafe.menu) and cafe.menu[i].available]

        if items_to_order and cafe.update_inventory(items_to_order):
            # Check for existing order by the same customer
            existing_order = cafe.get_latest_order_by_customer(customer_name)
            if existing_order:
                # Merge new items into existing order
                existing_order.items.extend(items_to_order)
                existing_order.total_price = sum(item.price for item in existing_order.items)
                existing_order.timestamp = datetime.now()  # Update timestamp
                order = existing_order
            else:
                # Create new order
                order = Order(cafe.order_counter, customer_name, items_to_order, current_user)
                cafe.orders.append(order)
                cafe.order_counter += 1

            # Check if the total items exceed 2 for receipt
            if len(order.items) > 2:
                total_price = order.total_price
                return render_template('receipt.html', order=order, total_price=total_price)
            else:
                return redirect(url_for('orders'))
        else:
            return "Error: Invalid items or out of stock.", 400
    
    return render_template('menu.html', menu=cafe.menu, enumerate=enumerate, role=user_role, current_user=current_user)

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    current_user = session['username']
    user_role = session['role']

    if request.method == 'POST':
        order_id = int(request.form['order_id'])
        action = request.form['action']
        order = next((o for o in cafe.orders if o.order_id == order_id), None)

        if order and (user_role == 'manager' or order.placed_by == current_user):
            if action == 'update_status' and user_role == 'manager':
                new_status = request.form['status']
                if new_status in ['Waiting/Pending', 'Ready', 'Served', 'Paid']:
                    order.status = new_status
            elif action == 'delete_order':
                cafe.orders.remove(order)
        return redirect(url_for('orders'))

    # Filtering
    filter_status = request.args.get('filter_status')
    search_query = request.args.get('search', '').lower()
    orders_list = cafe.orders.copy()

    if filter_status and filter_status != "All":
        orders_list = [o for o in orders_list if o.status == filter_status]
    if search_query:
        orders_list = [o for o in orders_list if search_query in o.customer_name.lower() or any(search_query in item.name.lower() for item in o.items)]

    # Pagination
    per_page = 10
    page = int(request.args.get('page', 1))
    start = (page - 1) * per_page
    end = start + per_page
    paginated_orders = orders_list[start:end]
    total_orders = len(orders_list)
    total_pages = (total_orders + per_page - 1) // per_page

    if user_role == 'manager':
        filtered_orders = [o for o in paginated_orders if cafe.users[o.placed_by]['role'] == 'customer']
    else:
        filtered_orders = [o for o in paginated_orders if o.placed_by == current_user]

    return render_template('orders.html', orders=filtered_orders, role=user_role, filter_status=filter_status, search_query=search_query, page=page, total_pages=total_pages)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
@role_required(['manager'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        stock = int(request.form['stock'] or 10)
        cafe.menu.append(MenuItem(name, price, category, stock))
        flash(f"Item '{name}' added successfully!", "success")
        return redirect(url_for('menu'))
    return render_template('add_item.html')

@app.route('/download_receipt/<int:order_id>')
@login_required
def download_receipt(order_id):
    order = next((o for o in cafe.orders if o.order_id == order_id), None)
    if not order:
        return "Order not found", 404

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"Receipt")
    p.drawString(100, 730, f"Order #{order.order_id}")
    p.drawString(100, 710, f"Customer: {order.customer_name}")
    p.drawString(100, 690, f"Date: {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 650, "Items Ordered:")
    y = 630
    for item in order.items:
        p.drawString(120, y, f"{item.name} - ${item.price:.2f}")
        y -= 20
    p.drawString(100, y - 20, f"Total Price: ${order.total_price:.2f}")
    p.showPage()
    p.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"receipt_order_{order.order_id}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)