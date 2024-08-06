from flask import Blueprint, redirect, render_template, request, url_for, flash

from blueprints.auth import role_required
from models.booking_model import Booking
from models.user_model import User
from models.vendor_model import Vendor
from models.poll_model import Poll
from firebase_admin import firestore, auth

from util import *


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/', methods=['GET'])
@role_required(['A'])
def view_admin_dashboard():
    bookings, vendors, employees = _get_pending_approvals()
    return render_template(
        'admin_home_page.html',
        bookings=bookings,
        vendors=vendors,
        employees=employees,
        home_url=url_for('admin.view_admin_dashboard')
    )


@admin_bp.route('/manage-bookings', methods=['GET'])
@role_required(['A'])
def view_manage_bookings():

    bookings = Booking.get_all_bookings()

    return render_template('bookings_manager.html', bookings=bookings, form=BookingForm())


@admin_bp.route('/create-booking', methods=['GET'])
@role_required(['A'])
def view_create_booking():
    return render_template('admin_create_booking.html')


@admin_bp.route('/manage-polls', methods=['GET'])
@role_required(['A'])
def view_polls_manager():
    polls = Poll.get_all_polls()
    vendors = Vendor.get_all_vendors()

    poll_results = []

    for poll in polls:
        poll_info = poll.to_dict()
        option_percentages, total_responses = Poll.get_poll_results(poll.id)

        poll_result = {
            'poll_id': poll.id,
            'poll_data': poll_info,
            'option_percentages': option_percentages,
            'total_responses': total_responses
        }
        poll_results.append(poll_result)
        print(poll_results)

    return render_template('admin_polls_page.html', poll_results=poll_results, vendors=vendors)


@admin_bp.route('/approve', methods=['POST'])
def handle_approvals():
    action = request.form.get('action').upper()
    booking_id = request.form.get('bookingIdField')
    user_id = request.form.get('userIdField')

    try:
        if (booking_id):
            approve_booking(booking_id, action)
            msg = "Booking approved successfully."

        elif (user_id):
            approve_user(user_id, action)
            msg = "User approved successfully."

        flash(msg, FlashCategory.SUCCESS.value)

    except Exception as e:
        flash(str(e), FlashCategory.ERROR.value)

    finally:
        return redirect(url_for('admin.view_admin_dashboard'))


def approve_booking(booking_id, action):
    _approve_entity('Bookings', booking_id, action)

    vendor_email = Booking.get_vendor_email_by_booking_id(booking_id)
    send_mail("Your Booking has been approved",
              vendor_email, "Please login to verify.")
    return


def approve_user(user_id, action):
    _approve_entity('Users', user_id, action)
    user_email = auth.get_user(user_id).email
    send_mail("Your account has been approved",
              user_email, "Please login to verify.")
    return


def _approve_entity(collection_name: str, entity_id, action):
    db = firestore.client()

    entity_ref = db.collection(collection_name).document(entity_id)

    if not entity_ref.get().exists:
        raise Exception(f'{collection_name.capitalize()[:-1]} not found')

    if action == 'APPROVE':
        entity_ref.update({'Status': 'A'})
    elif action == 'DENY':
        entity_ref.update({'Status': 'D'})
    else:
        raise Exception("Invalid Action.")


def _get_pending_approvals():
    bookings = Booking.get_pending_bookings_with_details()
    vendors = User.get_pending_vendors_with_details()
    employees = User.get_pending_employees()

    return bookings, vendors, employees
