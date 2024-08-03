from sys import prefix
from flask import jsonify, Blueprint, redirect, render_template, abort, request, url_for, flash
from jinja2 import TemplateNotFound
import logging

from blueprints.auth import role_required
from models.booking_model import Booking
from models.user_model import User
from models.vendor_model import Vendor
from firebase_admin import firestore

from util import *


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/', methods=['GET'])
@role_required(['A'])
def view_admin_dashboard():
    try:
        bookings, vendors, employees = _get_pending_approvals()
        return render_template(
            'admin_home_page.html',
            bookings=bookings,
            vendors=vendors,
            employees=employees,
            home_url=url_for('admin.view_admin_dashboard')
        )
    except TemplateNotFound:
        abort(404)


@admin_bp.route('/manage-bookings', methods=['GET'])
@role_required(['A'])
def view_manage_bookings():

    bookings = Booking.get_all_bookings()

    return render_template('manage_bookings_page.html', bookings=bookings, form=BookingForm())


@admin_bp.route('/create-booking', methods=['GET'])
@role_required(['A'])
def view_create_booking():
    return render_template('create_booking_admin.html')


@admin_bp.route('/approve', methods=['POST'])
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


def _approve_entity(collection_name: str, entity_id, action):
    try:
        db = firestore.client()

        entity_ref = db.collection(collection_name).document(entity_id)

        if not entity_ref.get().exists:
            flash(f'{collection_name.capitalize()[:-1]} not found', 'error')
            return redirect(url_for('admin.view_admin_dashboard'))

        if action == 'APPROVE':
            entity_ref.update({'Status': 'A'})
            flash(
                f'{collection_name.capitalize()[:-1]} approved successfully', FlashCategory.SUCCESS.value)
        elif action == 'DENY':
            entity_ref.update({'Status': 'D'})
            flash(
                f'{collection_name.capitalize()[:-1]} denied successfully', FlashCategory.ERROR.value)

        else:
            flash('Invalid action', 'error')
            return redirect(url_for('admin.view_admin_dashboard'))

        return redirect(url_for('admin.view_admin_dashboard'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _get_pending_approvals():
    bookings = Booking.get_pending_bookings_with_details()
    vendors = User.get_pending_vendors_with_details()
    employees = User.get_pending_employees()

    return bookings, vendors, employees
