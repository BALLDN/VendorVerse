from flask import Blueprint, redirect, render_template, request, url_for, flash, jsonify
from firebase_admin import firestore

from models.user_model import User
from models.vendor_model import Vendor


vendor_bp = Blueprint('vendor', __name__)


@vendor_bp.route('/vendor', methods=['GET', 'POST'])
def vendor():
    db = firestore.client()

    if request.method == 'POST':
        # Handle POST request to process form submission
        booking_action = request.form.get('booking-action')
        event_id = request.form.get('event-id')
        print(event_id)

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
                        additional_info = request.form.get('additional-info')

                        discount = request.form.get('deal', "No Discount")

                        booking_ref.update({
                            "Status": status,
                            "Date": date,
                            "Location": location,
                            "Deal": discount,
                            "`Additional Info`": additional_info
                        })
                        # Redirect to the admin page after modification
                        return redirect(url_for('vendor'))
                    else:
                        return "No Booking Found!"
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    return render_template('vendor_home_page.html', user_type='V')


@vendor_bp.route('/vendor_details', methods=['GET', 'POST'])
def vendor_details_page():
    db = firestore.client()
    email = request.cookies.get('login_email')
    user_id = User.get_user_id_from_email(db, email)
    if request.method == 'POST':
        Vendor.add_vendor_details(db, user_id)
        flash(
            "Your Details have been saved and your account is pending approval")
        return redirect(url_for('index'))

    return render_template('vendor_details_page.html')
