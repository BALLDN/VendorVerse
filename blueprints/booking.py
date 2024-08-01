from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, session
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, DateField
from wtforms.validators import InputRequired
from firebase_admin import firestore

from models.booking_model import Booking
from blueprints.auth import role_required
from util import FlashCategory

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/create_booking_admin', methods=['GET', 'POST'])
@role_required('A')
def create_booking_admin():
    db = firestore.client()
    if request.method == 'GET':
        Booking.get_user_id(db, request.cookies.get('login_email'))
    if request.method == "POST":
        user_id = Booking.get_user_id(db, request.form.get('Email'))
        Booking.add_booking(db, user_id)
        return redirect(url_for('create_booking_admin'))
    return render_template('create_booking_admin.html', user_type='A')


@booking_bp.route('/manage_booking_admin', methods=['GET', 'POST'])
@role_required('A')
def manage_booking_admin():

    db = firestore.client()
    form = BookingForm()
    bookings = Booking.get_approved_bookings()

    if request.method == 'GET':
        return render_template('manage_booking_page.html', bookings=bookings, form=form)

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
            bookings = Booking.get_approved_bookings()

        # Reload the bookings after any action

        bookings = Booking.get_approved_bookings()

        return render_template('booking.manage_booking_admin', bookings=bookings, form=form)

@booking_bp.route('/create_booking', methods=['GET', 'POST'])
@role_required('V')
def create_booking():
    if request.method == 'GET':
        return render_template('create_booking_vendor.html')
    if request.method == "POST":

        Booking.add_booking(session['user_id'])
        flash("Your Booking has been created and is pending approval",
              FlashCategory.SUCCESS.value)
        return redirect(url_for('booking.create_booking'))
        # return render_template('create_booking_vendor.html')
        
        
@booking_bp.route('/manage_booking', methods=['GET', 'POST'])
@role_required('V')
def manage_booking():
    db = firestore.client()
    form = BookingForm()

    bookings = Booking.get_bookings_by_vendor_id(db, session['user_id'])

    if request.method == 'GET':
        return render_template('manage_booking_page.html', bookings=bookings, form=form)

    if request.method == 'POST':
        action = request.form.get('action')
        booking_id = request.form.get('booking_id')

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
            if booking_id:
                Booking.modify_booking(db, booking_id)
            else:
                print("No booking ID provided")

        bookings = Booking.get_bookings_by_vendor_id(db, session['user_id'])
        return render_template('manage_booking_page.html', bookings=bookings, form=form)

@booking_bp.route('/get_bookings_for_calendar', methods=['GET'])
def get_bookings():
    try:
        bookings = Booking.get_approved_bookings()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


class BookingForm(FlaskForm):
    date = DateField('Date', validators=[InputRequired()])
    location = SelectField('Location', choices=[('Front Car Park', 'Front Car Park'), ('Back Car Park', 'Back Car Park')]) 
    discount = TextAreaField('Discount', validators=[InputRequired()])
    additional_info = TextAreaField('Additional Information', validators=[InputRequired()])
