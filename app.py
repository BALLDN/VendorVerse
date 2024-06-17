<<<<<<< HEAD
import firebase_admin
<<<<<<< HEAD
from models.user_model import User
from models.booking_model import bookings
=======
from user_model import users
from booking_model import bookings
>>>>>>> 6943fd0 (Create Booking page is now functional for vendors)
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, flash, redirect, render_template, request, url_for, make_response

app = Flask(__name__)

# Put in to Flash Error Message, need to improve sessions later
app.secret_key = "Secret Key"

=======
<<<<<<< Updated upstream
from flask import Flask, redirect, render_template, request, url_for
from flask import jsonify
=======
import firebase_admin
from user_model import users
from firebase_admin import credentials
from firebase_admin import firestore
<<<<<<< HEAD
from flask import Flask, redirect, render_template, request, url_for
>>>>>>> Stashed changes
=======
from flask import Flask, flash, redirect, render_template, request, url_for, make_response
>>>>>>> bcbbbc5 (Cookies pull username from login from and user type from database connected to user.)

app = Flask(__name__)

>>>>>>> 45527d8 (Registration Page now Functional)
# Use the application default credentials.

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
<<<<<<< HEAD
        User.get_users(db)

        # Get Cookies containing login info
=======
        users.get_users(db)

        #Get Cookies containing login info
>>>>>>> bcbbbc5 (Cookies pull username from login from and user type from database connected to user.)
        login_email = request.cookies.get('login_email')

        if login_email:
            return render_template('login.html', login_email=login_email)
<<<<<<< HEAD

        return render_template('login.html')

    if request.method == 'POST':
<<<<<<< HEAD

        # Get username used in login form
        login_email = request.form['Email']

        if (User.validate_user(db) == "V"):
            url_response = make_response(redirect(url_for('vendor')))
        elif (User.validate_user(db) == "E"):
            url_response = make_response(redirect(url_for('employee')))
        elif (User.validate_user(db) == "A"):
=======
        
        return render_template('login.html')
        
        
    if request.method == 'POST':

        #Get username used in login form
        login_email = request.form['Email']


        if(users.validate_user(db) == "V"):
            url_response = make_response(redirect(url_for('vendor')))
        elif(users.validate_user(db) == "E"):
            url_response = make_response(redirect(url_for('employee')))
        elif(users.validate_user(db) == "A"):
>>>>>>> bcbbbc5 (Cookies pull username from login from and user type from database connected to user.)
            url_response = make_response(redirect(url_for('admin')))
        else:
            # Error Message displays as appropriate
            flash(User.validate_user(db))
            return render_template('login.html')
<<<<<<< HEAD

        # Set cookies for login details + user type
        url_response.set_cookie('login_email', login_email)
        url_response.set_cookie('user_type', User.validate_user(db))
=======
        
        
        #Set cookies for login details + user type
        url_response.set_cookie('login_email',login_email)
        url_response.set_cookie('user_type',users.validate_user(db))
>>>>>>> bcbbbc5 (Cookies pull username from login from and user type from database connected to user.)

        return url_response
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
<<<<<<< HEAD
        User.add_user(db)

        # Get username + user_type used in register form
=======
        users.add_user(db)

        #Get username + user_type used in register form
>>>>>>> bcbbbc5 (Cookies pull username from login from and user type from database connected to user.)
        login_email = request.form['Email']
        user_type = request.form['User_Type']

        if user_type == "Vendor":
<<<<<<< HEAD
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

=======
<<<<<<< Updated upstream
        return redirect(url_for('vendor_details_page'))
    return render_template('login.html')


@app.route('/register')
=======
        users.get_users(db)
        return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
>>>>>>> Stashed changes
def register():
    if request.method == 'POST':
        users.set_user(db)
        return redirect(url_for('home'))
        
>>>>>>> 45527d8 (Registration Page now Functional)
=======
            url_response = make_response(redirect(url_for('vendor_details_page')))
            flash("Your Account is Pending Approval")
        
        else:
            url_response = make_response(redirect(url_for('register')))
         

        flash("Your Account is Pending Approval")
        
        #Set cookies for login details + user type
        url_response.set_cookie('login_email',login_email)
        url_response.set_cookie('user_type',users.validate_user(db))

        return url_response
        
>>>>>>> bcbbbc5 (Cookies pull username from login from and user type from database connected to user.)
    return render_template('register.html')


@app.route('/')
def index():
    return render_template('public_home_page.html')


@app.route('/vendor')
def vendor():
    return render_template('vendor_home_page.html')

<<<<<<< HEAD

=======
>>>>>>> 6943fd0 (Create Booking page is now functional for vendors)
@app.route('/create_booking', methods=['GET', 'POST'])
def create_booking():
    if request.method == 'GET':
        bookings.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = bookings.get_user_id(db, request.cookies.get('login_email'))
        bookings.add_booking(db, user_id)
        flash("Your Booking has been created and is pending approval")
        return render_template('create_booking_vendor.html')
<<<<<<< HEAD
=======
    else:
        return render_template('create_booking_admin.html')
    '''
    if request.method == 'GET':
        bookings.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = bookings.get_user_id(db, request.cookies.get('login_email'))
        bookings.add_booking(db, user_id)
        flash("Your Booking has been created and is pending approval")
        return render_template('create_booking_vendor.html')
        
            
        
>>>>>>> 6943fd0 (Create Booking page is now functional for vendors)
    return render_template('create_booking_vendor.html')


'''Only Temporary until sessions are introduced'''


@app.route('/create_booking_admin', methods=['GET', 'POST'])
def create_booking_admin():
    if request.method == 'GET':
        bookings.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = bookings.get_user_id(db, request.form.get('Email'))
        bookings.add_booking(db, user_id)
        return redirect(url_for('create_booking_admin'))
    return render_template('create_booking_admin.html')


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
