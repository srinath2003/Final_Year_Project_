from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from extensions import db, r
import json
from functools import wraps

products_bp = Blueprint('products', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@products_bp.route('/products', methods=['GET'])
@login_required
def home():
    return render_template(("index.html"),current_user_id=session.get("user_id"))

@products_bp.route('/jsonproducts', methods=['GET'])
def get_products():
    cached_products = r.client.get('all_products')
    if cached_products:
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX USING REDIS for products viewing XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        return jsonify(json.loads(cached_products))
        
    db.cursor.execute("SELECT * FROM product_details WHERE Stock_Quantity > 0")
    products = db.cursor.fetchall()
    r.client.set('all_products', json.dumps(products), ex=300)
    return jsonify(products)

@products_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    cache_key = f"product_{product_id}"
    cached_product = r.client.get(cache_key)

    if cached_product:
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX USING REDIS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        return render_template("product_details.html", product=json.loads(cached_product))
        
    db.cursor.execute("SELECT * FROM product_details WHERE ID = %s", (product_id,))
    product = db.cursor.fetchone()

    if product:
        r.client.set(cache_key, json.dumps(product), ex=600)
        return render_template("product_details.html", product=product)
    else:
        return "Product not found", 404

@products_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))

    db.cursor.execute("SELECT * FROM cart_details WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    existing_item = db.cursor.fetchone()

    if existing_item:
        new_quantity = existing_item['quantity'] + quantity
        db.cursor.execute("UPDATE cart_details SET quantity = %s WHERE user_id = %s AND product_id = %s", (new_quantity, user_id, product_id))
    else:
        db.cursor.execute("INSERT INTO cart_details (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity))

    db.conn.commit()
    flash("Item added to cart!", "success")
    return redirect(url_for('products.get_product_details', product_id=product_id))

@products_bp.route('/cart', methods=['GET'])
@login_required
def view_cart():
    user_id = session['user_id']
    db.cursor.execute("""
        SELECT c.cart_id, c.quantity, p.*
        FROM cart_details c
        JOIN product_details p ON c.product_id = p.ID
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = db.cursor.fetchall()
    return render_template("cart.html", cart_items=cart_items)

@products_bp.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    db.cursor.execute("DELETE FROM cart_details WHERE cart_id = %s", (cart_id,))
    db.conn.commit()
    flash("Item removed from cart!", "success")
    return redirect(url_for('products.view_cart'))

@products_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user_id = session['user_id']
    db.cursor.execute("DELETE FROM cart_details WHERE user_id = %s", (user_id,))
    db.conn.commit()
    flash("Checkout successful! Your order has been placed.", "success")
    return redirect(url_for('products.home'))
