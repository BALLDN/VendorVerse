import firebase_admin
from models.user_model import User
from models.booking_model import Booking
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, flash, redirect, render_template, request, url_for, make_response
from flask_mail import Mail, Message

app = Flask(__name__)

# Mailing service
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '4a5fd4ae529040'
app.config['MAIL_PASSWORD'] = '1d028d73a0663c'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

sender_address = 'vendorverse@mailtrap.io'

# Put in to Flash Error Message, need to improve sessions later
app.secret_key = "Secret Key"

# Use the application default credentials.

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        User.get_users(db)

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
    #Pull email for user
    user_email = "email@email.com"

    #If Account Approved/Denied 
    account_status = "Approved" #Or "Denied"
    #Send email to vendor after account Approved/Denied
    msg = Message(subject='VendorVerse Account ' + account_status, sender=sender_address, recipients=[user_email])
    msg.body = "Your account has been " + account_status + "."
    if (account_status == "Approved"):
        msg.body += "<br><br>Have a great day!"
    else:
        msg.body += "<br>If you believe your account should have been Approved, please contact " + sender_address + ". <br><br>Have a great day!"
    mail.send(msg)


    #If Booking Approved/Denied
    booking_status = "Approved" #Or "Denied"
    #Send email to vendor after booking Approved/Denied
    msg = Message(subject='VendorVerse Booking ' + booking_status, sender=sender_address, recipients=[user_email])
    msg.body = "Your bookung has been " + booking_status + "."
    if (booking_status == "Approved"):
        msg.body += "<br><br>Have a great day!"
    else:
        msg.body += "<br>If you believe your booking should have been Approved, please contact " + sender_address + ". <br><br>Have a great day!"
    mail.send(msg)


    #If Booking Amendment Approved/Denied
    amend_status = "Approved" #Or "Denied"
    #Send email to vendor after booking amendment Approved/Denied
    msg = Message(subject='VendorVerse Booking Amendment ' + amend_status, sender=sender_address, recipients=[user_email])
    msg.body = "Your booking amendment has been " + amend_status + "."
    if (amend_status == "Approved"):
        msg.body += "<br><br>Have a great day!"
    else:
        msg.body += "<br>If you believe your booking amendment should have been Approved, please contact " + sender_address + ". <br><br>Have a great day!"
    mail.send(msg)


    #If Booking Amended by Admin
    #Send email to vendor after booking has been amended by Admin
    msg = Message(subject='VendorVerse Booking has been Amended', sender=sender_address, recipients=[user_email])
    msg.body = "Your booking has been amended. <br>Your booking had to be altered by our Admins. If there is an issue with this, please contact " + sender_address + ". <br><br>Have a great day!"
    mail.send(msg)


    #If Booking Cancelled by Admin
    #Send email to vendor after booking has been cancelled
    msg = Message(subject='VendorVerse Booking has been Cancelled', sender=sender_address, recipients=[user_email])
    msg.body = "Your booking has been cancelled. <br>Your booking had to be cancelled by our Admins. If there is an issue with this, please contact " + sender_address + ". <br><br>Have a great day!"
    mail.send(msg)


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

    if(login_email and user_type):
        url_response = make_response(redirect(url_for("index")))
        url_response.delete_cookie('login_email')
        url_response.delete_cookie('user_type')
    
        return url_response
    else:
        return redirect(url_for("index"))
