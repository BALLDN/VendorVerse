from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, session
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
        flash(
            "Your Details have been saved and your account is pending approval")
        session.clear()
        return redirect(url_for('index'))

    if request.method == 'GET':
        return render_template('vendor_details_page.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        login_email = request.cookies.get('login_email')

        if login_email:
            return render_template('login.html', login_email=login_email)

        return render_template('login.html')

    if request.method == 'POST':
        id_token = request.authorization.token

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            session['user_id'] = uid
            user_type = User.get_user_type_from_uid(uid)
            if user_type == "V":
                url_response = make_response(
                    redirect(url_for('vendor.vendor')))
            elif user_type == "E":
                url_response = make_response(redirect(url_for('employee')))
            elif user_type == "A":
                url_response = make_response(
                    redirect(url_for('admin.show_admin_dashboard')))
            else:
                flash(user_type)
                return render_template('login.html')

            return url_response
        except Exception as e:
            return f"An error occurred: {e}"


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
