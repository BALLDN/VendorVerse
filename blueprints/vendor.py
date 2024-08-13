from flask import Blueprint, redirect, render_template, request, url_for, flash, jsonify, session, abort
from jinja2 import TemplateNotFound
from firebase_admin import firestore
import logging

from models.vendor_model import Vendor
from models.booking_model import Booking
from blueprints.auth import role_required
from util import FlashCategory, BookingForm


vendor_bp = Blueprint('vendor', __name__, url_prefix='/vendor')


@vendor_bp.route('/', methods=['GET'])
@role_required(['V'])
def view_vendor_dashboard():
    return render_template('vendor_home_page.html', home_url=url_for('vendor.view_vendor_dashboard'))


@vendor_bp.route('/profile', methods=['GET'])
@role_required(['V'])
def view_profile():
    try:
        vendor = Vendor.get_vendor_by_user_id(session['user_id'])
        return render_template('vendor_profile.html', vendor=vendor)

    except TemplateNotFound:
        abort(404)


@vendor_bp.route('/manage-bookings', methods=['GET'])
@role_required(['V'])
def view_manage_bookings():
    bookings = Booking.get_bookings_by_vendor_id(session['user_id'])

    return render_template('bookings_manager.html', bookings=bookings, form=BookingForm())


@vendor_bp.route('/create-booking', methods=['GET'])
@role_required(['V'])
def view_create_booking():
    return render_template('vendor_create_booking.html')


@vendor_bp.route('/vendor', methods=['POST'])
def vendor():
    db = firestore.client()

    booking_action = request.form.get('booking-action')
    event_id = request.form.get('event-id')

    if not booking_action:
        return jsonify({'error': 'Action Undefined'}), 400

    if (event_id and booking_action):
        try:
            booking_ref = db.collection('Bookings').document(event_id)
            booking = booking_ref.get()

            if not booking.exists:
                return jsonify({'error': 'Booking not found'}), 404

            if booking_action == 'cancel':
                booking_ref.update({'Status': 'D'})
                print(
                    jsonify({'message': 'Booking cancelled successfully'}), 200)
                return redirect(url_for('vendor'))
            elif booking_action == 'modify':

                print(event_id)
                # Add this line to print the form data
                print("Form Data: ", request.form)

                if booking_ref.get().exists:
                    user_type = request.cookies.get('user_type')
                    if user_type == "V":
                        status = "P"
                    else:
                        status = "A"

                    date = request.form.get('date')
                    location = request.form.get('location')
                    title = request.form.get('title')

                    discount = request.form.get('deal', "No Discount")

                    booking_ref.update({
                        "Status": status,
                        "Date": date,
                        "Location": location,
                        "Deal": discount,
                        "Title": title
                    })
                    # Redirect to the admin page after modification
                    return redirect(url_for('vendor'))
                else:
                    return "No Booking Found!"
        except Exception as e:
            logging.error(str(e))
            return jsonify({'error': 'An internal error occurred. Please try again later.'}), 500


@vendor_bp.route('/profile/edit', methods=['POST'])
def account():
    db = firestore.client()

    user_id = session['user_id']

    Vendor.edit_vendor_details(db, user_id)
    flash("Your details have been updated and saved.",
          FlashCategory.SUCCESS.value)
    return redirect(url_for('vendor.view_profile'))
