// Delete Modal Functions
function showModal(orderId) {
    const modal = document.getElementById('deleteModal');
    const confirmBtn = document.getElementById('confirmDelete');
    modal.style.display = 'block';
    confirmBtn.onclick = function() {
        document.getElementById('deleteForm-' + orderId).submit();
    };
}

function closeModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

// Interactive Menu Functions
document.addEventListener('DOMContentLoaded', function() {
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // Toggle active class and details visibility
            const isActive = this.classList.contains('active');
            menuItems.forEach(i => {
                i.classList.remove('active');
                const details = i.querySelector('.menu-details');
                if (details) details.style.display = 'none';
            });
            
            if (!isActive) {
                this.classList.add('active');
                const details = this.querySelector('.menu-details');
                if (details) details.style.display = 'block';
            }
        });
    });
});