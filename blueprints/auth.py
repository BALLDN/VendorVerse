from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, abort
import logging
from firebase_admin import firestore, auth
from firebase_admin._user_mgt import UserRecord


from models.user_model import User
from util import FlashCategory


# For Auth Audit only
auth_logger = logging.getLogger('auth_audit')


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type'][0].upper()

        if password != confirm_password:
            flash("Passwords Must Be The Same!", FlashCategory.ERROR.value)
            return redirect(url_for('auth.register'))

        flash("Your Account is Pending Approval", FlashCategory.SUCCESS.value)
        user: UserRecord = auth.create_user(email=email, password=password)
        if user_type == "V":
            url_response = make_response(
                redirect(url_for('vendor.vendor_details_page')))
        elif user_type == "E":
            uid = user.uid
            User.add_user(uid, email, user_type)
            url_response = make_response(redirect(url_for('index')))

        return url_response

    if request.method == 'GET':
        return render_template('register.html')


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


@auth_bp.route('/logout')
def logout():

    login_email = request.cookies.get('login_email')
    user_type = request.cookies.get('user_type')

    if (login_email and user_type):
        url_response = make_response(redirect(url_for("index")))
        url_response.delete_cookie('login_email')
        url_response.delete_cookie('user_type')

        return url_response
    else:
        return redirect(url_for("index"))


@auth_bp.route('/reset')
def reset():
    return render_template('forgot_password.html')
