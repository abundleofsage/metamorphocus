import os
import requests
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from database import get_db, init_db, Inventory, Order, OrderItem
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
CORS(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple user class for manager access
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'manager':
        return User('manager')
    return None

# --- Unified Database Setup ---
# The database engine and session management are now imported from the centralized database.py.
# This ensures the Flask app uses the same settings, including the SQLite fallback.

# Initialize database tables on startup
init_db()

@app.route('/')
def index():
    """Serve the sales page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Manager login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        # Use "admin" as the default password if the environment variable is not set.
        manager_password = os.getenv('MANAGER_PASSWORD', 'admin')
        
        if password == manager_password:
            user = User('manager')
            login_user(user)
            return redirect(url_for('manager'))
        else:
            return render_template('login.html', error='Invalid password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout from manager"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/manager')
@login_required
def manager():
    """Proxy to Streamlit manager backend"""
    # Redirect to Streamlit on port 8000
    # Note: This simple redirect assumes the Streamlit app is running on the same host.
    # For production, a more robust reverse proxy setup (e.g., with Nginx) would be better.
    streamlit_url = f"http://{request.host.split(':')[0]}:8000"
    return render_template('manager_redirect.html', streamlit_url=streamlit_url)


@app.route('/static/product_images/<path:filename>')
def serve_product_image(filename):
    """Serve product images"""
    return send_from_directory('static/product_images', filename)

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all available products with stock > 0"""
    db = get_db()
    try:
        products = db.query(Inventory).filter(Inventory.stock_level > 0).all()
        
        products_data = [{
            'id': p.id,
            'name': p.product_name,
            'category': p.category,
            'price': p.unit_price,
            'image': p.image_url or f'https://via.placeholder.com/400x500/272b33/e2e8f0?text={p.category}',
            'desc': p.description or f'{p.product_name} - {p.category}',
            'stock': p.stock_level
        } for p in products]
        
        return jsonify(products_data)
    finally:
        db.close()

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    db = get_db()
    try:
        data = request.json
        
        # Validate request
        if not data.get('customer_name') or not data.get('customer_email'):
            return jsonify({'error': 'Name and email required'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Calculate total and check stock
        total_amount = 0
        order_items = []
        
        for item in data['items']:
            product = db.query(Inventory).filter(Inventory.id == item['id']).first()
            
            if not product:
                return jsonify({'error': f'Product {item["id"]} not found'}), 404
            
            if product.stock_level < item['qty']:
                return jsonify({'error': f'Insufficient stock for {product.product_name}'}), 400
            
            order_items.append({
                'product_id': product.id,
                'product_name': product.product_name,
                'quantity': item['qty'],
                'price': product.unit_price
            })
            
            total_amount += product.unit_price * item['qty']
        
        # Create order
        order = Order(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data.get('customer_phone'),
            total_amount=total_amount,
            status='pending',
            notes=data.get('notes')
        )
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items and update stock
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                product_name=item_data['product_name'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.add(order_item)
            
            # Update stock
            product = db.query(Inventory).filter(Inventory.id == item_data['product_id']).first()
            product.stock_level -= item_data['quantity']
        
        db.commit()
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'total': total_amount,
            'message': 'Order placed successfully!'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
