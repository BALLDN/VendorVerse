import os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for, make_response, jsonify

from models.user_model import User
from models.booking_model import Booking
from firebase_admin import credentials, firestore, auth
from flask import Flask, flash, redirect, render_template, request, url_for, make_response, jsonify
from firebase_admin import credentials, firestore, auth
from flask import Flask, flash, redirect, render_template, request, url_for, make_response, jsonify

load_dotenv()
app = Flask(__name__)

# Put in to Flash Error Message, need to improve sessions later
app.secret_key = os.environ.get('APP_SECRET_KEY')

try:
    cred = credentials.Certificate(os.environ.get('FIREBASE_PRIVATE_KEY'))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logging.info("Firebase initialized successfully")
except Exception as e:
    logging.exception("Failed to initialize Firebase: %s", e)

db = firestore.client()


class modifyForm(FlaskForm):
    date = DateField('Date', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    discount = TextAreaField('Discount', validators=[InputRequired()])
    additional_info = TextAreaField(

        'Additional Information', validators=[InputRequired()])

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
        # login_email = request.form['Email']

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

    #         if user_type == "Vendor":
    #             url_response = make_response(
    #                 redirect(url_for('vendor_details_page')))
    #             flash("Your Account is Pending Approval")

    #         else:
    #             url_response = make_response(redirect(url_for('register')))

    #         flash("Your Account is Pending Approval")

    #         # Set cookies for login details + user type
    #         url_response.set_cookie('login_email', login_email)
    #         url_response.set_cookie('user_type', User.validate_user(db))

    #         return url_response

    #     return render_template('register.html')

    @app.route('/vendor')
    def vendor():
        return render_template('vendor_home_page.html')

    @app.route('/create_booking', methods=['GET', 'POST'])
    def create_booking():
        if request.method == 'GET':
            Booking.get_user_id(db, request.cookies.get('login_email'))
        if request.method == "POST":
            user_id = Booking.get_user_id(
                db, request.cookies.get('login_email'))
            Booking.add_booking(db, user_id)
            flash("Your Booking has been created and is pending approval")
            return render_template('create_booking_vendor.html')
        return render_template('create_booking_vendor.html')

    @app.route('/create_booking_admin', methods=['GET', 'POST'])
    def create_booking_admin():
        if request.method == 'GET':
            Booking.get_user_id(db, request.cookies.get('login_email'))
        if request.method == "POST":
            user_id = Booking.get_user_id(db, request.form.get('Email'))
            Booking.add_booking(db, user_id)
            return redirect(url_for('create_booking_admin'))
        return render_template('create_booking_admin.html')

    @app.route('/manage_booking', methods=['GET', 'POST'])
    def manage_bookings():

        form = BookingForm()

        if request.cookies.get('user_type') == "V":
            bookings = Booking.get_bookings_by_vendor_id(
                db, Booking.get_user_id(db, request.cookies.get('login_email')))
        elif request.cookies.get('user_type') == "A":
            bookings = Booking.get_approved_bookings(db)

        if request.method == 'GET':
            return render_template('manage_bookings_page.html', bookings=bookings, form=form)

        if request.method == 'POST':
            action = request.form.get('action')
            booking_id = request.form.get('options')

            if action == 'cancel':
                if booking_id:
                    booking_ref = db.collection(
                        'Bookings').document(booking_id)
                    if booking_ref.get().exists:
                        booking_ref.update({"Status": "D"})
                        print(f"Booking {booking_id} status updated to D")
                    else:
                        print("No booking found with the provided ID")
                else:
                    print("No booking ID provided")

            elif action == 'modify':
                # Store Booking ID
                booking_id = request.form['options']
                print(booking_id)
                Booking.modify_booking(db, booking_id)

                # Display Updated Bookings
                if (request.cookies.get('user_type') == "V"):
                    bookings = Booking.get_bookings_by_vendor_id(
                        db, Booking.get_user_id(db, request.cookies.get('login_email')))
                elif (request.cookies.get('user_type') == "A"):
                    bookings = Booking.get_approved_bookings(db)

            # Reload the bookings after any action
            if request.cookies.get('user_type') == "V":
                bookings = Booking.get_bookings_by_vendor_id(
                    db, Booking.get_user_id(db, request.cookies.get('login_email')))
            elif request.cookies.get('user_type') == "A":
                bookings = Booking.get_approved_bookings(db)

            return render_template('manage_bookings_page.html', bookings=bookings, form=form)

        return render_template('manage_bookings_page.html', bookings=bookings, form=form)

    @app.route('/get_booking/<booking_id>', methods=['GET'])
    def get_booking(booking_id):
        booking_ref = db.collection('Bookings').document(booking_id)
        results = booking_ref.get()

        if results.exists:
            booking_data = results.to_dict()
            response_data = {
                "date": booking_data.get("Date"),
                "location": booking_data.get("Location"),
                "discount": booking_data.get("Deal"),
                "additional_info": booking_data.get("Additional Info")
            }
            return jsonify(response_data)
        else:
            return jsonify({"error": "Booking not found"}), 404

    @app.route('/employee')
    def employee():
        return render_template('employee_home_page.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return render_template('admin_home_page.html', bookings=bookings)

    return render_template('admin_home_page.html')

    @app.route('/reset')
    def reset():
        return render_template('forgot_password.html')


@app.route('/vendor_details', methods=['GET', 'POST'])
def vendor_details_page():
    email = request.cookies.get('login_email')
    user_id = User.get_user_id_from_email(db, email)
    if request.method == 'POST':
        Vendor.add_vendor_details(db, user_id)
        flash("Your Details have been saved and your account is pending approval")
        return redirect(url_for('index'))

    return render_template('vendor_details_page.html')


<< << << < HEAD


@app.route('/logout')
def logout():

    login_email = request.cookies.get('login_email')
    user_type = request.cookies.get('user_type')

    if (login_email and user_type):
        url_response = make_response(redirect(url_for("index")))
        url_response.delete_cookie('login_email')
        url_response.delete_cookie('user_type')


== == == =


@app.route('/logout')
def logout():

        login_email = request.cookies.get('login_email')
        user_type = request.cookies.get('user_type')

        if (login_email and user_type):
            url_response = make_response(redirect(url_for("index")))
            url_response.delete_cookie('login_email')
            url_response.delete_cookie('user_type')


>>>>>> > 9a1d41e(abc)
        return url_response
    else:
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(port=5000)