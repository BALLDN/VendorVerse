from google.cloud.firestore import Client
from flask.wrappers import Request
from flask import jsonify, Blueprint, redirect, render_template, abort, request, url_for, flash
from jinja2 import TemplateNotFound
import logging

from models.booking_model import Booking
from models.user_model import User
from models.vendor_model import Vendor
from firebase_admin import firestore


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin', methods=['GET'])
def show_admin_dashboard():
    try:
        detailed_bookings, users, vendor_users = _get_data()
        return render_template('admin_home_page.html', bookings=detailed_bookings, users=users, vendor_users=vendor_users, user_type='A')
    except TemplateNotFound:
        abort(404)


@admin_bp.route('/admin', methods=['POST'])
def handle_approvals():
    action = request.form.get('action').upper()
    booking_id = request.form.get('bookingIdField')
    user_id = request.form.get('userIdField')

    if not action:
        return jsonify({'error': 'Action Undefined'}), 400

    if (booking_id):
        return _approve_entity('Bookings', booking_id, action)

    elif (user_id):
        return _approve_entity('Users', user_id, action)


def _approve_entity(collection_name, entity_id, action):
    try:
        db = firestore.client()

        entity_ref = db.collection(collection_name).document(entity_id)

        if not entity_ref.get().exists:
            flash(f'{collection_name.capitalize()} not found', 'error')
            return redirect(url_for('admin.show_admin_dashboard'))

        if action == 'APPROVE':
            entity_ref.update({'Status': 'A'})
            flash(
                {'message': f'{collection_name.capitalize()} approved successfully'})
        elif action == 'DENY':
            entity_ref.update({'Status': 'D'})
            flash(
                {'message': f'{collection_name.capitalize()} denied successfully'})

        else:
            flash('Invalid action', 'error')
            return redirect(url_for('admin.show_admin_dashboard'))

        return redirect(url_for('admin.show_admin_dashboard'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _get_data():
    db = firestore.client()
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
        logging.info(f"Fetched vendor details for Vendor_ID {
                     vendor_id}: {vendor_details}")

        # Ensure vendor_details is a dictionary and log any potential issues
        if vendor_details:
            booking['vendor_name'] = vendor_details.get('Vendor_Name')
            booking['vendor_phone'] = vendor_details.get(
                'Phone_Number')
            booking['vendor_address'] = vendor_details.get('Address')
            logging.info(f"Vendor details added to booking: {
                         vendor_details}")
        else:
            logging.warning(
                f"No vendor details found for Vendor_ID: {vendor_id}")

        detailed_bookings.append(booking)

    for user_snapshot in users:
        user = user_snapshot.to_dict()  # Convert DocumentSnapshot to dictionary
        try:
            if (user["User_Type"] == "V"):
                user['id'] = user_snapshot.id

                vendor_details = Vendor.get_vendor_by_user_id(db, user['id'])

                # Log vendor details fetched

                # Ensure vendor_details is a dictionary and log any potential issues
                if vendor_details:
                    user['vendor_name'] = vendor_details.get('Vendor_Name')
                    user['vendor_phone'] = vendor_details.get(
                        'Phone_Number')
                    user['vendor_address'] = vendor_details.get('Address')
                    logging.info(f"Vendor details added to User: {
                        vendor_details}")
                else:
                    logging.warning(
                        f"No vendor details found for Vendor_ID: {user['id']}")

                vendor_users.append(user)
        except Exception as e:
            logging.error(e)

        # Log the detailed bookings list
    logging.info(f"Detailed bookings: {detailed_bookings}")
    logging.info(f"Vendors: {vendor_users}")

    return detailed_bookings, users, vendor_users
