from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, session

from firebase_admin import firestore

from models.booking_model import Booking
from blueprints.auth import role_required
from util import FlashCategory
import logging

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')


@booking_bp.route('/create', methods=['POST'])
@role_required(['A', 'V'])
def create_booking():
    try:
        form = request.form
        vendor_email = form.get('vendor_email')
        title = form.get('title')
        location = form.get('location')
        date = form.get('date')
        deal = form.get('deal')
        if vendor_email:
            success = Booking.add_booking(
                title, location, date, deal, vendor_email)
        else:
            success = Booking.add_booking(
                title, location, date, deal, session['user_id'])
        if success:
            flash("Your Booking has been created and is pending approval",
                  FlashCategory.SUCCESS.value)
    except Exception as e:
        flash('An error was encountered during the attempt of creating a Booking. Please try again.',
              FlashCategory.ERROR.value)
    return redirect(url_for('index'))


@booking_bp.route('/action', methods=['POST'])
@role_required(['V', 'A'])
def manage_booking_action():
    action = request.form.get('action')
    booking_id = request.form.get('bookingIdField')

    try:
        if action == 'edit':
            result = Booking.edit_booking(booking_id)

        if action == 'cancel':
            result = Booking.cancel_booking(booking_id)

        if not result.update_time:
            raise Exception('Booking update failed')

    except Exception as e:
        flash("An error has occuring during cancellation of Booking. Please try again.",
              FlashCategory.ERROR.value)
        logging.ERROR(str(e))

    return redirect(url_for('booking.manage_booking'))


@booking_bp.route('/calendar', methods=['GET'])
def get_bookings():
    try:
        bookings = Booking.get_approved_bookings()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
