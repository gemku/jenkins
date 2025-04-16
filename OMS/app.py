from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Sample data for demonstration purposes
orders = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/orders')
def orders_page():
    return render_template('orders.html', orders=orders)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        # Logic to add an item to the order
        return redirect(url_for('orders_page'))
    return render_template('add_item.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Logic for user login
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/receipt/<int:order_id>')
def receipt(order_id):
    order = next((o for o in orders if o['order_id'] == order_id), None)
    if order:
        total_price = sum(item['price'] for item in order['items'])
        return render_template('receipt.html', order=order, total_price=total_price)
    return redirect(url_for('orders_page'))

if __name__ == '__main__':
    app.run(debug=True)