from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
import os
from dotenv import load_dotenv
from kafka import KafkaProducer
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Connect to MySQL
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor(dictionary=True)

# Kafka Configuration
KAFKA_TOPIC = "user_interactions"
KAFKA_BROKER = "172.22.213.208:9092"
# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


from uuid import UUID
import json

@app.route('/log_interaction', methods=['POST'])
def log_interaction():
    data = request.get_json()
    
    print("Received request data:", data)  # Debugging log

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    required_fields = ['product_id', 'action']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    if 'user_id' not in session:
        return jsonify({"error": "User not authenticated"}), 401

    interaction_data = {
        "product_id": int(data['product_id']),
        "user_id": session['user_id'],
        "action": data['action'],
        "category": data.get('category', 'Unknown'),
        "timestamp": datetime.utcnow().isoformat()
    }

    print(f"Sending interaction data to Kafka: {interaction_data}")

    # Send to Kafka
    producer.send(KAFKA_TOPIC, value=interaction_data)

    return jsonify({"message": "Interaction logged successfully"}), 200


# Route: Landing page (Login)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user from DB
        cursor.execute("SELECT * FROM user_details WHERE username = %s AND password_hash = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            return redirect(url_for('home'))  # Redirect to products page
        else:
            flash("Invalid username or password", "error")  # Show error message
            return redirect(url_for('login'))

    return render_template("login.html")

# Route: Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        country_code = request.form['country_code']
        phone_number = request.form['phone_number']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        postal_code = request.form['postal_code']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        password = request.form['password']

        # Combine country code and phone number
        full_phone_number = country_code + phone_number

        # Check if username or email already exists
        cursor.execute("SELECT * FROM user_details WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username or email already exists. Please choose a different one.", "error")
            return redirect(url_for('signup'))

        # Insert new user into the database
        cursor.execute("""
            INSERT INTO user_details (first_name, last_name, username, email, phone_number, address, city, state, country, postal_code, date_of_birth, gender, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, username, email, full_phone_number, address, city, state, country, postal_code, date_of_birth, gender, password))

        db.commit()
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template("signup.html")


# Route: Products Page (Only accessible after login)
@app.route('/products', methods=['GET'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    return render_template("index.html")

# Route: Fetch all products (for filtering)
@app.route('/jsonproducts', methods=['GET'])
def get_products():
    cursor.execute("SELECT * FROM product_details")
    products = cursor.fetchall()
    return jsonify(products)
# Route: Fetch single product details
@app.route('/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    cursor.execute("SELECT * FROM product_details WHERE ID = %s", (product_id,))
    product = cursor.fetchone()
    if product:
        return render_template("product_details.html", product=product)
    else:
        return "Product not found", 404

# Route: Add to cart
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))

    # Check if the product is already in the cart
    cursor.execute("SELECT * FROM cart_details WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    existing_item = cursor.fetchone()

    if existing_item:
        new_quantity = existing_item['quantity'] + quantity
        cursor.execute("UPDATE cart_details SET quantity = %s WHERE user_id = %s AND product_id = %s", (new_quantity, user_id, product_id))
    else:
        cursor.execute("INSERT INTO cart_details (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity))

    db.commit()
    flash("Item added to cart!", "success")
    return redirect(url_for('get_product_details', product_id=product_id))

# Route: View Cart
@app.route('/cart', methods=['GET'])
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor.execute("""
        SELECT c.cart_id, c.quantity, p.*
        FROM cart_details c
        JOIN product_details p ON c.product_id = p.ID
        WHERE c.user_id = %s
    """, (user_id,))
    
    cart_items = cursor.fetchall()
    return render_template("cart.html", cart_items=cart_items)

# Route: Remove from Cart
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor.execute("DELETE FROM cart_details WHERE cart_id = %s", (cart_id,))
    db.commit()
    flash("Item removed from cart!", "success")
    return redirect(url_for('view_cart'))

# Route: Checkout (Clears the cart)
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    cursor.execute("DELETE FROM cart_details WHERE user_id = %s", (user_id,))
    db.commit()
    
    flash("Checkout successful! Your order has been placed.", "success")
    return redirect(url_for('home'))

# Route: Account Page
@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True) 

    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        postal_code = request.form['postal_code']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']

        try:
            cursor.execute("""
                UPDATE user_details 
                SET email = %s, first_name = %s, last_name = %s, 
                    phone_number = %s, address = %s, city = %s, 
                    state = %s, country = %s, postal_code = %s, 
                    date_of_birth = %s, gender = %s 
                WHERE user_id = %s
            """, (email, first_name, last_name, phone_number, address, city, state, country, postal_code, date_of_birth, gender, user_id))
            db.commit()
            flash("Profile updated successfully!", "success") # add feedback to user
        except mysql.connector.Error as err:
            db.rollback()
            flash(f"Error updating profile: {err}", "error") # add feedback to user

        return redirect(url_for('account'))

    cursor.execute("SELECT * FROM user_details WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    return render_template("account.html", user=user)

# Route: Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear the user session
    return render_template("login.html") # Send an empty success response

if __name__ == '__main__':
    app.run(debug=True)
