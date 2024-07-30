from functools import wraps
from time import sleep
from flask import Blueprint, get_flashed_messages, render_template, request, redirect, url_for, flash, make_response, session
import logging
from firebase_admin import firestore, auth
from firebase_admin._user_mgt import UserRecord
from uuid import uuid4


from models.user_model import User
from models.vendor_model import Vendor
from util import FlashCategory


# For Auth Audit only
auth_logger = logging.getLogger('auth_audit')


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('access_token'):
            return redirect(url_for('index'))
        else:
            return render_template('register.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type'][0].upper()

        if password != confirm_password:
            flash("Passwords Must Be The Same!", FlashCategory.ERROR.value)
            return redirect(url_for('auth.register'))

        uid = uuid4().hex

        User.add_user(uid, email, user_type)

        if user_type == "V":
            url_response = make_response(
                redirect(url_for('auth.vendor_details_page')))
            session['UID'] = uid
        elif user_type == "E":
            flash("Your Account is Pending Approval",
                  FlashCategory.SUCCESS.value)
            url_response = make_response(redirect(url_for('index')))
        else:
            flash('Invalid User Type. Please Try Again',
                  FlashCategory.ERROR.value)
            url_response = make_response(
                redirect(url_for('index')))

        try:
            user: UserRecord = auth.create_user(
                uid=uid, email=email, password=password)
        except Exception as e:
            flash(e, FlashCategory.ERROR.value)

        return url_response


@auth_bp.route('/vendor_details', methods=['GET', 'POST'])
def vendor_details_page():
    db = firestore.client()
    uid = session['UID']
    if request.method == 'POST':
        Vendor.add_vendor_details(db, uid)
        session.clear()
        flash(
            "Your Details have been saved and your account is pending approval", FlashCategory.SUCCESS.value)
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('vendor_details_page.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('access_token'):
            return redirect(url_for('index'))

        login_email = request.cookies.get('login_email')

        if login_email:
            return render_template('login.html', login_email=login_email)

        return render_template('login.html')

    if request.method == 'POST':
        access_token = request.authorization.token

        try:
            sleep(0.5)
            decoded_token = auth.verify_id_token(access_token)
            uid = decoded_token['uid']
            session['user_id'] = uid
            session['access_token'] = access_token

            user = User.get_user_by_user_id(session['user_id'])
            session['user_type'] = user.get('User_Type')
            status = user.get('Status')
            if status != 'A':
                session.clear()
                return redirect(url_for('index', status='PENDING'))

            if session['user_type'] == "A":
                return redirect(
                    url_for('admin.view_admin_dashboard'))
            elif session['user_type'] == "V":
                return redirect(
                    url_for('vendor.view_vendor_dashboard'))
            elif session['user_type'] == "E":
                return redirect(url_for('employee'))
            else:
                flash('An error has occured during sign in. Please try again.',
                      FlashCategory.ERROR.value)
                return redirect(url_for('index'))

        except Exception as e:
            flash('An error has occured during sign in. Please try again.',
                  FlashCategory.ERROR.value)
            logging.ERROR(e)
            return redirect(url_for('index'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have logged out successfully.", FlashCategory.SUCCESS.value)
    return redirect(url_for('index'))


@auth_bp.route('/reset')
def reset():
    return render_template('forgot_password.html')


def role_required(user_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'access_token' not in session:
                flash("Please log in to access this page.",
                      FlashCategory.INFO.value)
                return redirect(url_for('auth.login'))
            if session.get('user_type') != user_type:
                flash(f"You need escalated privileges to access this page.",
                      FlashCategory.INFO.value)
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
