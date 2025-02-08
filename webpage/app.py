from flask import Flask, render_template, jsonify, request
import mysql.connector

app = Flask(__name__)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '220818',  # Replace with your MySQL password
    'database': 'online_store'
}

@app.route('/product/<int:product_id>')
def product_details(product_id):
    print("Product ID received:", product_id)  # Debugging
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product_details WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        return render_template('product_detail.html', product=product)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)})
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    if not product:
        return render_template('error.html', message="Product not found"), 404
@app.route('/products')
def fetch_products():
    category = request.args.get('category', '')
    price = request.args.get('price', '')
    rating = request.args.get('rating', '')
    search = request.args.get('search', '')

    query = "SELECT * FROM product_details WHERE 1=1"

    if category:
        query += f" AND Category='{category}'"
    if price:
        query += f" AND Price <= {price}"
    if rating:
        query += f" AND Rating >= {rating}"
    if search:
        query += f" AND Name LIKE '%{search}%'"

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        products = cursor.fetchall()
        return jsonify(products)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)})
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
