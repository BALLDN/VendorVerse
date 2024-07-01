import firebase_admin
from models.user_model import User
from models.booking_model import Booking
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, flash, redirect, render_template, request, url_for, make_response
import os
from dotenv import load_dotenv

load_dotenv
app = Flask(__name__)

# Put in to Flash Error Message, need to improve sessions later
app.secret_key = os.environ.get('APP_SECRET_KEY')

# Use the application default credentials.
firebase_creds = {
    "type": "service_account",
    "project_id": "balldn",
    "private_key_id": "bf5b714cd50ab8a9b9947d5c897e6a5621b84471",
    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY'),
    "client_email": "firebase-adminsdk-o8cke@balldn.iam.gserviceaccount.com",
    "client_id": "110934915845662067518",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-o8cke%40balldn.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
cred = credentials.Certificate("firebase_creds.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':

        # Get Cookies containing login info
        login_email = request.cookies.get('login_email')

        if login_email:
            return render_template('login.html', login_email=login_email)

        return render_template('login.html')

    if request.method == 'POST':

        # Get username used in login form
        login_email = request.form['Email']

        if (User.validate_user(db) == "V"):
            url_response = make_response(redirect(url_for('vendor')))
        elif (User.validate_user(db) == "E"):
            url_response = make_response(redirect(url_for('employee')))
        elif (User.validate_user(db) == "A"):
            url_response = make_response(redirect(url_for('admin')))
        else:
            # Error Message displays as appropriate
            flash(User.validate_user(db))
            return render_template('login.html')

        # Set cookies for login details + user type
        url_response.set_cookie('login_email', login_email)
        url_response.set_cookie('user_type', User.validate_user(db))

        return url_response
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        User.add_user(db)

        # Get username + user_type used in register form
        login_email = request.form['Email']
        user_type = request.form['User_Type']

        if user_type == "Vendor":
            url_response = make_response(
                redirect(url_for('vendor_details_page')))
            flash("Your Account is Pending Approval")

        else:
            url_response = make_response(redirect(url_for('register')))

        flash("Your Account is Pending Approval")

        # Set cookies for login details + user type
        url_response.set_cookie('login_email', login_email)
        url_response.set_cookie('user_type', User.validate_user(db))

        return url_response

    return render_template('register.html')


@app.route('/')
def index():
    return render_template('public_home_page.html')


@app.route('/vendor')
def vendor():
    return render_template('vendor_home_page.html')


@app.route('/create_booking', methods=['GET', 'POST'])
def create_booking():
    if request.method == 'GET':
        Booking.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = Booking.get_user_id(db, request.cookies.get('login_email'))
        Booking.add_booking(db, user_id)
        flash("Your Booking has been created and is pending approval")
        return render_template('create_booking_vendor.html')
    return render_template('create_booking_vendor.html')


'''Only Temporary until sessions are introduced'''


@app.route('/create_booking_admin', methods=['GET', 'POST'])
def create_booking_admin():
    if request.method == 'GET':
        Booking.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = Booking.get_user_id(db, request.form.get('Email'))
        Booking.add_booking(db, user_id)
        return redirect(url_for('create_booking_admin'))
    return render_template('create_booking_admin.html')


@app.route('/manage_booking')
def manage_bookings():
    return render_template('manage_bookings_page.html')


@app.route('/employee')
def employee():
    return render_template('employee_home_page.html')


@app.route('/admin')
def admin():
    return render_template('admin_home_page.html')


@app.route('/reset')
def reset():
    return render_template('forgot_password.html')


@app.route('/vendor_details')
def vendor_details_page():
    return render_template('vendor_details_page.html')


@app.route('/logout')
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

