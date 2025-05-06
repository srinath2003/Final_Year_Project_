from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db.cursor.execute(
            "SELECT * FROM user_details WHERE username = %s AND password_hash = %s",
            (username, password)
        )
        user = db.cursor.fetchone()

        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            return redirect(url_for('products.home'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('auth.login'))

    return render_template("login.html")

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        form = request.form
        full_phone_number = form['country_code'] + form['phone_number']

        db.cursor.execute(
            "SELECT * FROM user_details WHERE username = %s OR email = %s",
            (form['username'], form['email'])
        )
        existing_user = db.cursor.fetchone()

        if existing_user:
            flash("Username or email already exists. Please choose a different one.", "error")
            return redirect(url_for('auth.login'))

        db.cursor.execute("""
            INSERT INTO user_details (
                first_name, last_name, username, email, phone_number, address, city, 
                state, country, postal_code, date_of_birth, gender, password_hash
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            form['first_name'], form['last_name'], form['username'], form['email'], full_phone_number,
            form['address'], form['city'], form['state'], form['country'], form['postal_code'],
            form['date_of_birth'], form['gender'], form['password']
        ))

        db.conn.commit()
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template("signup.html")


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('auth.login'))
