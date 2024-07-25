from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired
from firebase_admin import firestore

from models.booking_model import Booking
from models.user_model import User
from models.vendor_model import Vendor

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/create_booking_admin', methods=['GET', 'POST'])
def create_booking_admin():
    db = firestore.client()
    if request.method == 'GET':
        Booking.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = Booking.get_user_id(db, request.form.get('Email'))
        Booking.add_booking(db, user_id)
        return redirect(url_for('create_booking_admin'))
    return render_template('create_booking_admin.html', user_type='A')


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
        return render_template('create_booking_vendor.html', user_type='V')
    return render_template('create_booking_vendor.html', user_type='V')


@booking_bp.route('/manage_booking', methods=['GET', 'POST'])
def manage_bookings():

    db = firestore.client()
    form = BookingForm()
    bookings = []

    if request.cookies.get('user_type') == "V":
        bookings = Booking.get_bookings_by_vendor_id(
            db, Booking.get_user_id(db, request.cookies.get('login_email')))
    elif request.cookies.get('user_type') == "A":
        bookings = Booking.get_approved_bookings(db)

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

        return render_template('booking.manage_bookings', bookings=bookings, form=form)

    if request.method == 'GET':
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


@booking_bp.route('/account', methods=['GET', 'POST'])
def account():
    db = firestore.client()
    # TODO: get uid from session
    email = request.cookies.get('login_email')
    user_id = User.get_user_id_from_email(db, email)

    vendor = Vendor.get_vendor_by_user_id(db, user_id)

    if request.method == 'GET':
        return render_template('account_details.html', vendor=vendor)

    if request.method == 'POST':
        Vendor.edit_vendor_details(db, user_id)
        flash("Your Details have been edited")
        return redirect(url_for('vendor'))

    return render_template('account_details.html', vendor=vendor)


class BookingForm(FlaskForm):
    date = DateField('Date', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    discount = TextAreaField('Discount', validators=[InputRequired()])
    additional_info = TextAreaField(
        'Additional Information', validators=[InputRequired()])
