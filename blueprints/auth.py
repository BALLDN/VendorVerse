import array
from functools import wraps
from re import T
from time import sleep
from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, make_response, session
import logging
from firebase_admin import firestore, auth, exceptions
from uuid import uuid4


from models.user_model import User
from models.vendor_model import Vendor
from util import FlashCategory, send_mail, send_admin_notif


# For Auth Audit only
auth_logger = logging.getLogger('auth_audit')


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('access_token'):
            return redirect(url_for('index'))
        else:
            return render_template('auth_register.html')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type'][0].upper()

        if password != confirm_password:
            flash("Passwords Must Be The Same!", FlashCategory.ERROR.value)
            return redirect(url_for('auth.register'))

        uid = uuid4().hex

        try:
            auth.create_user(
                uid=uid, email=email, password=password)
        except exceptions.InvalidArgumentError as e:
            flash('Invalid Email!', FlashCategory.ERROR.value)
            return redirect(url_for('auth.register'))
        except Exception as e:
            flash(str(e), FlashCategory.ERROR.value)
            return redirect(url_for('auth.register'))

        if user_type == "V":
            session['UID'] = uid
            session['user_email'] = email
            url_response = make_response(
                redirect(url_for('auth.vendor_details_page')))
        elif user_type == "E":
            send_mail('Welcome to VendorVerse!', email,
                      'Your account is pending approval. We will let you know when your account has been approved and you can login to our site.')

            send_admin_notif("EMPLOYEE")
            flash("Your Account is Pending Approval",
                  FlashCategory.SUCCESS.value)
            url_response = make_response(redirect(url_for('index')))
        else:
            flash('Invalid User Type. Please Try Again',
                  FlashCategory.ERROR.value)
            url_response = make_response(
                redirect(url_for('index')))

        User.add_user(uid, email, user_type)

        return url_response


@auth_bp.route('/vendor-details', methods=['GET', 'POST'])
def vendor_details_page():
    db = firestore.client()
    uid = session['UID']
    if request.method == 'POST':
        Vendor.add_vendor_details(db, uid)
        send_mail('Welcome to VendorVerse!', session['user_email'],
                  'Your account is pending approval. We will let you know when your account has been approved and you can login to our site.')
        send_admin_notif("VENDOR")

        session.clear()
        flash(
            "Your details have been saved and your account is pending approval", FlashCategory.SUCCESS.value)
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('auth_register_vendor.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('access_token'):
            return redirect(url_for('index'))

        login_email = request.cookies.get('login_email')

        return render_template('auth_login.html', login_email=login_email)

    if request.method == 'POST':
        access_token = request.authorization.token

        try:
            sleep(0.1)
            decoded_token = auth.verify_id_token(access_token)
            uid = decoded_token['uid']
            session['user_id'] = uid
            session['access_token'] = access_token
            user = User.get_user_by_user_id(session['user_id'])
            session['user_type'] = user.get('User_Type')
            status = user.get('Status')
            if status == 'P':
                session.clear()
                return redirect(url_for('index', status='PENDING'))
            if status == 'D':
                session.clear()
                return redirect(url_for('index', status='DENIED'))

            if session['user_type'] == "A":
                return redirect(
                    url_for('admin.view_admin_dashboard'))
            elif session['user_type'] == "V":
                return redirect(
                    url_for('vendor.view_vendor_dashboard'))
            elif session['user_type'] == "E":
                return redirect(url_for('employee'))
            else:
                raise Exception('Invalid User Type.')
        except Exception as e:
            session.clear()
            flash(f'An error has occured during sign in. {str(e)} Please try again.',
                  FlashCategory.ERROR.value)
            logging.error(str(e))
            return abort(make_response({'code': 'auth/invalid-login-credentials'}, 500))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have logged out successfully.", FlashCategory.SUCCESS.value)
    return redirect(url_for('index'))


@auth_bp.route('/password-reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        is_email_sent = request.form.get('is_email_sent')
        if is_email_sent == 'SUCCESS':
            flash('Password reset email has been sent.\nPlease check your inbox and reset your password accordingly.',
                  FlashCategory.SUCCESS.value)
        else:
            flash('Error sending password reset email. Please try again.',
                  FlashCategory.ERROR.value)
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('auth_password_reset.html')


def role_required(user_type: array):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'access_token' not in session:
                flash("Please log in to access this page.",
                      FlashCategory.INFO.value)
                return redirect(url_for('auth.login'))
            if session.get('user_type') not in user_type:
                flash(f"You need escalated privileges to access this page.",
                      FlashCategory.INFO.value)
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
