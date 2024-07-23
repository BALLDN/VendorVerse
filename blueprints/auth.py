from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
import logging
from firebase_admin import firestore

from models.user_model import User


# For Auth Audit only
auth_logger = logging.getLogger('auth_audit')


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = firestore.client()
    if request.method == 'GET':
        # Get Cookies containing login info
        login_email = request.cookies.get('login_email')

        if login_email:
            return render_template('login.html', login_email=login_email)

        return render_template('login.html')

    if request.method == 'POST':
        login_email = request.form['Email']

        user_type = User.validate_user(db)

        if user_type == "V":
            url_response = make_response(redirect(url_for('vendor')))
        elif user_type == "E":
            url_response = make_response(redirect(url_for('employee')))
        elif user_type == "A":
            url_response = make_response(redirect(url_for('admin')))
        else:
            flash(user_type)
            return render_template('login.html')

        url_response.set_cookie('login_email', login_email)
        url_response.set_cookie('user_type', user_type)

        return url_response

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    db = firestore.client()

    if request.method == 'POST':
        User.add_user(db)

        login_email = request.form['Email']
        user_type = request.form['User_Type']

        if user_type == "Vendor":
            url_response = make_response(
                redirect(url_for('vendor_details_page')))
            flash("Your Account is Pending Approval")
        else:
            url_response = make_response(redirect(url_for('register')))
            flash("Your Account is Pending Approval")

        url_response.set_cookie('login_email', login_email)
        url_response.set_cookie('user_type', User.validate_user(db))

        return url_response

    return render_template('register.html')
