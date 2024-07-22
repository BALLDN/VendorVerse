import datetime
from dotenv import load_dotenv
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for, make_response, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired
from models.user_model import User
from models.booking_model import Booking
from models.vendor_model import Vendor
from models.polls_model import Polls

# Configure logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
app = Flask(__name__)
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
    additional_info = TextAreaField('Additional Information', validators=[InputRequired()])
    
    
@app.route('/get_bookings_for_calendar', methods=['GET'])
def get_bookings():
    try:
        # Determine user type and get appropriate bookings
        if request.cookies.get('user_type') == "V":
            bookings_ref = Booking.get_bookings_by_vendor_id(db, Booking.get_user_id(db, request.cookies.get('login_email')))
        elif request.cookies.get('user_type') == "A":
            bookings_ref = Booking.get_approved_bookings(db)
        else:
            bookings_ref = Booking.get_approved_bookings(db)

        bookings = []
        # Iterate over the list of booking documents
        for doc in bookings_ref:
            booking = doc.to_dict()
            booking['id'] = doc.id  # Add the document ID to the booking dictionary
            if(booking.get("Status") != "D"):
                bookings.append(booking)
        
        # Return the bookings as a JSON response
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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


def create_poll(database_connection):
    # Ensure we're handling form data
    data = request.form
    title = data.get('PollTitle')
    vendor_id = data.get('VendorName')
    
    # Set vendor information based on availability
    if vendor_id:
        vendor_ref = database_connection.collection('Vendors').document(vendor_id)
        vendor = vendor_ref.get()
        name = vendor.get("Vendor_Name") if vendor.exists else "No Vendor"
    else:
        vendor_id = "No Vendor"
        name = "No Vendor"
    
    amount = int(data.get('Amount'))
    
    choices = []
    for i in range(1, amount + 1):
        choice = data.get(f'choice{i}')
        if choice:
            choices.append(choice)

    if not title or not choices:
        flash('Missing fields')
        return redirect(url_for('admin_polls'))

    poll_ref = database_connection.collection('Polls').add({
        'Title': title,
        'Vendor_ID': vendor_id,
        'options': choices,
        'createdAt': datetime.datetime.now(),
        'Vendor_Name': name
    })
    
    # Get the ID of the newly created poll
    poll_id = poll_ref[1].id
    
    flash("A poll has been created. To view the poll, navigate to the View/Create Polls Page")
    return redirect(url_for('admin_polls'))



@app.route('/admin_polls', methods=['GET', 'POST'])
def admin_polls():
    
      
    polls = Polls.get_polls(db)
    
    poll_results = []
    
    if request.method == 'GET':
        vendors = Vendor.get_users(db)
        for poll in polls:
            poll_info = poll.to_dict()
            option_percentages, total_responses = Polls.get_poll_results(db, poll.id)
            
            poll_result = {
                'poll_id': poll.id,
                'poll_data': poll_info,
                'option_percentages': option_percentages,
                'total_responses': total_responses
            }
            poll_results.append(poll_result)
            print(poll_results)
            
        return render_template('admin_polls_page.html', vendors=vendors, poll_results=poll_results)
    if request.method == 'POST':
        create_poll(db)
        return redirect(url_for('admin'))
    return render_template('admin_polls_page.html')


@app.route('/employee_polls', methods=['GET', 'POST'])
def employee_polls():
    polls = Polls.get_polls(db)
    if request.method == 'GET':
        return render_template('employee_polls_page.html', polls=polls)
    if request.method == 'POST':
        Polls.submit_response(db)
                
    return render_template('employee_polls_page.html', polls=polls)
                
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        User.add_user(db)

        # Get username + user_type used in register form
        login_email = request.form['Email']
        user_type = request.form['User_Type']

        if user_type == "Vendor":
            url_response = make_response(redirect(url_for('vendor_details_page')))
        else:
            url_response = make_response(redirect(url_for('index')))
            flash("Your Account is Pending Approval")

        # Set cookies for login details + user type
        url_response.set_cookie('login_email', login_email)
        url_response.set_cookie('user_type', User.validate_user(db))

        return url_response

    return render_template('register.html')


@app.route('/')
def index():
    return render_template('public_home_page.html')


@app.route('/vendor',methods=['GET', 'POST'])
def vendor():
    if request.method == 'POST':
         # Handle POST request to process form submission
        booking_action = request.form.get('booking-action')
        event_id = request.form.get('event-id')
        print(event_id)

        if not booking_action:
            return jsonify({'error': 'Action Undefined'}), 400
        
        if(event_id and booking_action):
            try:
                booking_ref = db.collection('Bookings').document(event_id)
                booking = booking_ref.get()
                
                if not booking.exists:
                    return jsonify({'error': 'Booking not found'}), 404
                
                if booking_action == 'cancel':
                    booking_ref.update({'Status': 'D'})
                    print(jsonify({'message': 'Booking cancelled successfully'}), 200)
                    return redirect(url_for('vendor'))
                elif booking_action == 'modify':
                    
                    print(event_id)
                    print("Form Data: ", request.form)  # Add this line to print the form data
                    
                    if booking_ref.get().exists:
                        user_type = request.cookies.get('user_type')
                        if user_type == "V":
                            status = "P"
                        else:
                            status = "A"

                        date = request.form.get('date')
                        location = request.form.get('location')
                        additional_info = request.form.get('additional-info')

                        discount = request.form.get('deal', "No Discount")

                        booking_ref.update({
                            "Status": status, 
                            "Date": date, 
                            "Location": location, 
                            "Deal": discount, 
                            "`Additional Info`": additional_info
                        })
                        return redirect(url_for('vendor'))  # Redirect to the admin page after modification
                    else:
                        return "No Booking Found!"
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            
    
    
    return render_template('vendor_home_page.html')


@app.route('/create_booking', methods=['GET', 'POST'])
def create_booking():
    if request.method == 'GET':
        Booking.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = Booking.get_user_id(db, request.cookies.get('login_email'))
        Booking.add_booking(db, user_id)
        flash("Your Booking has been created and is pending Admin approval")
        return redirect(url_for('vendor'))
    return render_template('create_booking_vendor.html')


@app.route('/create_booking_admin', methods=['GET', 'POST'])
def create_booking_admin():
    if request.method == 'GET':
        Booking.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = Booking.get_user_id(db, request.form.get('Email'))
        Booking.add_booking(db, user_id)
        flash("A Booking has been created. Navigate to Manage Bookings to Edit/Delete this booking")
        return redirect(url_for('admin'))
    return render_template('create_booking_admin.html')


@app.route('/manage_booking', methods=['GET', 'POST'])
def manage_bookings():

    form = modifyForm()

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
                booking_ref = db.collection('Bookings').document(booking_id)
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
        if booking_data.get("Status") != "D":
            

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
        bookings = Booking.get_pending_bookings(db)
        users = User.get_pending_users(db)
        detailed_bookings = []
        vendor_users = []
        for booking_snapshot in bookings:
            booking = booking_snapshot.to_dict()  # Convert DocumentSnapshot to dictionary
            booking['id'] = booking_snapshot.id
            
            vendor_id = booking.get("Vendor_ID")
            vendor_details = Vendor.get_vendor_by_user_id(db, vendor_id)
            
            # Log vendor details fetched
            app.logger.info(f"Fetched vendor details for Vendor_ID {vendor_id}: {vendor_details}")
            
            # Ensure vendor_details is a dictionary and log any potential issues
            if vendor_details:
                booking['vendor_name'] = vendor_details.get('Vendor_Name')
                booking['vendor_phone'] = vendor_details.get('Phone_Number')
                booking['vendor_address'] = vendor_details.get('Address')
                app.logger.info(f"Vendor details added to booking: {vendor_details}")
            else:
                app.logger.warning(f"No vendor details found for Vendor_ID: {vendor_id}")
            
            detailed_bookings.append(booking)
        
        for user_snapshot in users:
            if(user_snapshot.get("User_Type") == "V"):
                user = user_snapshot.to_dict()  # Convert DocumentSnapshot to dictionary
                user['id'] = user_snapshot.id
                
                user_id = user_snapshot.id
                vendor_details = Vendor.get_vendor_by_user_id(db, user_id)
                
                # Log vendor details fetched
                app.logger.info(f"Fetched vendor details for Vendor_ID {user_id}: {vendor_details}")
                
                # Ensure vendor_details is a dictionary and log any potential issues
                if vendor_details:
                    user['vendor_name'] = vendor_details.get('Vendor_Name')
                    user['vendor_phone'] = vendor_details.get('Phone_Number')
                    user['vendor_address'] = vendor_details.get('Address')
                    app.logger.info(f"Vendor details added to User: {vendor_details}")
                else:
                    app.logger.warning(f"No vendor details found for Vendor_ID: {user_id}")
            
                vendor_users.append(user)
        
        # Log the detailed bookings list
        app.logger.info(f"Detailed bookings: {detailed_bookings}")
        app.logger.info(f"Vendors: {vendor_users}")
        
        return render_template('admin_home_page.html', bookings=detailed_bookings, users=users, vendor_users=vendor_users)
    
    elif request.method == 'POST':
        # Handle POST request to process form submission
        action = request.form.get('action')
        booking_action = request.form.get('booking-action')
        booking_id = request.form.get('bookingIdField')
        event_id = request.form.get('event-id')
        user_id = request.form.get('userIdField')

        print(event_id)

        if not action and not booking_action:
            return jsonify({'error': 'Action Undefined'}), 400
        
        if(event_id and booking_action):
            try:
                booking_ref = db.collection('Bookings').document(event_id)
                booking = booking_ref.get()
                
                if not booking.exists:
                    return jsonify({'error': 'Booking not found'}), 404
                
                if booking_action == 'cancel':
                    booking_ref.update({'Status': 'D'})
                    print(jsonify({'message': 'Booking cancelled successfully'}), 200)
                    return redirect(url_for('admin'))
                elif booking_action == 'modify':
                    
                    print(event_id)
                    print("Form Data: ", request.form)  # Add this line to print the form data
                    
                    if booking_ref.get().exists:
                        user_type = request.cookies.get('user_type')
                        status = "P" if user_type == "V" else "A"

                        date = request.form.get('date')
                        location = request.form.get('location')
                        additional_info = request.form.get('additional-info')

                        discount = request.form.get('deal', "No Discount")

                        booking_ref.update({
                            "Status": status, 
                            "Date": date, 
                            "Location": location, 
                            "Deal": discount, 
                            "`Additional Info`": additional_info
                        })
                        return redirect(url_for('admin'))  # Redirect to the admin page after modification
                    else:
                        return "No Booking Found!"
            except Exception as e:
                return jsonify({'error': str(e)}), 500
            
        if(booking_id and action):
            try:
                booking_ref = db.collection('Bookings').document(booking_id)
                booking = booking_ref.get()
                
                if not booking.exists:
                    return jsonify({'error': 'Booking not found'}), 404

                if action == 'approve':
                    booking_ref.update({'Status': 'A'})
                    print(jsonify({'message': 'Booking approved successfully'}), 200)
                    return redirect(url_for('admin'))
                elif action == 'cancel':
                    booking_ref.update({'Status': 'D'})
                    print(jsonify({'message': 'Booking cancelled successfully'}), 200)
                    return redirect(url_for('admin'))
                else:
                    return jsonify({'error': 'Invalid action'}), 400

            except Exception as e:
                return jsonify({'error': str(e)}), 500
        elif(user_id):
            try:
                users_ref = db.collection('Users').document(user_id)
                user = users_ref.get()
                
                if not user.exists:
                    return jsonify({'error': 'Booking not found'}), 404

                if action == 'approve':
                    users_ref.update({'Status': 'A'})
                    print(jsonify({'message': 'User approved successfully'}), 200)
                    return redirect(url_for('admin'))
                elif action == 'cancel':
                    users_ref.update({'Status': 'D'})
                    print(jsonify({'message': 'User Denied successfully'}), 200)
                    return redirect(url_for('admin'))
                else:
                    return jsonify({'error': 'Invalid action'}), 400

            except Exception as e:
                return jsonify({'error': str(e)}), 500


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        email = request.form.get('Email')
        current_password = request.form.get('Current_Password')
        new_password = request.form.get('Password')
        confirmed_password = request.form.get('Confirm_Password')

        # Call the reset_user_password method
        result = User.reset_user_password(db, email, current_password, new_password, confirmed_password)

        # Check the result and flash the appropriate message
        flash(result['message'])

        if result['status'] == 'success':
            return redirect(url_for('login'))
        else:
            return redirect(url_for('reset'))

    return render_template('forgot_password.html')


@app.route('/vendor_details', methods=['GET','POST'])
def vendor_details_page():
    email = request.cookies.get('login_email')
    user_id = User.get_user_id_from_email(db, email)
    if request.method == 'POST':
        Vendor.add_vendor_details(db, user_id)
        flash("Your Details have been saved and your account is pending approval")
        return redirect(url_for('index'))
        
    return render_template('vendor_details_page.html')

@app.route('/account', methods=['GET','POST'])
def account():
    email = request.cookies.get('login_email')
    user_id = User.get_user_id_from_email(db, email)
    vendor = Vendor.get_vendor_by_user_id(db,user_id)
    
    if request.method == 'GET':
        return render_template('account_details.html', vendor=vendor)
    
    if request.method == 'POST':
        Vendor.edit_vendor_details(db, user_id)
        flash("Your Details have been edited")
        return redirect(url_for('vendor'))
    
    return render_template('account_details.html',vendor=vendor)


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
    

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')