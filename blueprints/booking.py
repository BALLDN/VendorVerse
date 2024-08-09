import logging

from flask import Blueprint, request, flash, jsonify, url_for, redirect, session
from models.booking_model import Booking
from blueprints.auth import role_required
from util import FlashCategory, send_admin_notif, send_mail

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
            success = Booking.create_booking(
                title, location, date, deal, vendor_email)
        else:
            success = Booking.create_booking(
                title, location, date, deal, session['user_id'])
        if success:
            if session['user_type'] == 'V':
                flash("Your Booking has been created and is pending approval",
                  FlashCategory.SUCCESS.value)
                send_admin_notif("BOOKING")
            elif session['user_type'] == 'A':
                flash("Booking has been created successfully and is auto-approved",
                      FlashCategory.SUCCESS.value)
    except Exception as e:
        flash('An error was encountered during the attempt of creating a Booking. Please try again.',
              FlashCategory.ERROR.value)
    return redirect(url_for('index'))


@booking_bp.route('/<booking_id>/edit', methods=['POST'])
@role_required(['A', 'V'])
def update_booking(booking_id):
    try:
        form = request.form
        title = form.get('title')
        location = form.get('location')
        date = form.get('date')
        deal = form.get('deal')
        result = Booking.update_booking(
            booking_id, title, location, date, deal)

        if result.update_time:
            if session['user_type'] == 'V':
                flash("Booking has been updated successfully and is pending approval",
                      FlashCategory.SUCCESS.value)
                send_admin_notif("BOOKING")
            elif session['user_type'] == 'A':
                flash("Booking has been updated successfully",
                      FlashCategory.SUCCESS.value)

    except Exception as e:
        flash("An error has occured during amendment of Booking. Please try again.",
              FlashCategory.ERROR.value)
        logging.error(str(e))
    return redirect(url_for('index'))


@booking_bp.route('/<booking_id>/cancel', methods=['POST'])
@role_required(['A', 'V'])
def delete_booking(booking_id):
    try:

        Booking.delete_booking(booking_id)
        flash("Booking has been cancelled successfully.",
              FlashCategory.SUCCESS.value)
        Booking.get_vendor_email_by_booking_id(booking_id)
        send_mail("Your Booking has been cancelled by the Admin",
                  Booking.get_vendor_email_by_booking_id(booking_id), "Please login to verify.")

    except Exception as e:
        flash("An error has occured during cancellation of Booking. Please try again.",
              FlashCategory.ERROR.value)
        logging.error(str(e))

    return redirect(url_for('index'))


@booking_bp.route('/<booking_id>', methods=['GET'])
@role_required(['A', 'V'])
def get_booking_by_id(booking_id):
    return jsonify(Booking.read_booking(booking_id))


@booking_bp.route('/calendar', methods=['GET'])
def get_calendar_bookings():
    try:
        bookings = Booking.get_approved_bookings()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
