from flask import Blueprint, render_template, request, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired
from firebase_admin import firestore

from models.booking_model import Booking

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/create_booking', methods=['GET', 'POST'])
def create_booking():
    db = firestore.client()

    if request.method == 'GET':
        Booking.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = Booking.get_user_id(
            db, request.cookies.get('login_email'))
        Booking.add_booking(db, user_id)
        flash("Your Booking has been created and is pending approval")
        return render_template('create_booking_vendor.html')
    return render_template('create_booking_vendor.html')


@booking_bp.route('/manage_booking', methods=['GET', 'POST'])
def manage_bookings():

    db = firestore.client()
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


@booking_bp.route('/get_bookings_for_calendar', methods=['GET'])
def get_bookings():
    db = firestore.client()

    try:

        bookings_ref = Booking.get_approved_bookings(db)

        bookings = []
        # Iterate over the list of booking documents
        for doc in bookings_ref:
            booking = doc.to_dict()
            # Add the document ID to the booking dictionary
            booking['id'] = doc.id
            bookings.append(booking)

        # Return the bookings as a JSON response
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@booking_bp.route('/get_booking/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    db = firestore.client()

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


class BookingForm(FlaskForm):
    date = DateField('Date', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    discount = TextAreaField('Discount', validators=[InputRequired()])
    additional_info = TextAreaField(
        'Additional Information', validators=[InputRequired()])
