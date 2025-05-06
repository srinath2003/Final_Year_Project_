from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import db
from functools import wraps

user_bp = Blueprint('user', __name__, url_prefix='')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_id = session['user_id']

    if request.method == 'POST':
        form = request.form
        try:
            db.cursor.execute("""
                UPDATE user_details 
                SET email = %s, first_name = %s, last_name = %s, 
                    phone_number = %s, address = %s, city = %s, 
                    state = %s, country = %s, postal_code = %s, 
                    date_of_birth = %s, gender = %s 
                WHERE user_id = %s
            """, (
                form['email'], form['first_name'], form['last_name'],
                form['phone_number'], form['address'], form['city'],
                form['state'], form['country'], form['postal_code'],
                form['date_of_birth'], form['gender'], user_id
            ))
            db.conn.commit()
            flash("Profile updated successfully!", "success")
        except Exception as err:
            db.conn.rollback()
            flash(f"Error updating profile: {err}", "error")
        return redirect(url_for('user.account'))

    db.cursor.execute("SELECT * FROM user_details WHERE user_id = %s", (user_id,))
    user = db.cursor.fetchone()
    return render_template("account.html", user=user)

@user_bp.route('/wishlist', methods=['GET'])
@login_required
def wishlist():
    return render_template("wishlist.html")

@user_bp.route('/orderdetails', methods=['GET'])
@login_required
def orderdetails():
    return render_template("orderdetails.html")
@user_bp.route('/report', methods=['GET'])
@login_required
def report():
    return render_template("report.html")

