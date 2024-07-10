from google.cloud.firestore import Client
from flask.wrappers import Request

from flask import redirect, url_for, jsonify


def handle_approvals(db: Client, request: Request):
    action = request.form.get('action').upper()
    booking_id = request.form.get('bookingIdField')
    user_id = request.form.get('userIdField')

    if not action:
        return jsonify({'error': 'Action Undefined'}), 400

    if (booking_id):
        return approve_booking(db, booking_id, action)

    elif (user_id):
        return approve_account(db, user_id, action)


def approve_booking(db: Client, booking_id, action):
    try:
        booking_ref = db.collection('Bookings').document(booking_id)

        if not booking_ref.get().exists:
            return jsonify({'error': 'Booking not found'}), 404

        if action == 'APPROVE':
            booking_ref.update({'Status': 'A'})
            print(
                jsonify({'message': 'Booking approved successfully'}), 200)
            return redirect(url_for('admin'))
        elif action == 'DENY':
            booking_ref.update({'Status': 'D'})
            print(
                jsonify({'message': 'Booking cancelled successfully'}), 200)
            return redirect(url_for('admin'))
        else:
            return jsonify({'error': 'Invalid action'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def approve_account(db: Client, user_id, action):
    try:
        users_ref = db.collection('Users').document(user_id)

        if not users_ref.get().exists:
            return jsonify({'error': 'User not found'}), 404

        if action == 'APPROVE':
            users_ref.update({'Status': 'A'})
            print(
                jsonify({'message': 'User Approved successfully'}), 200)
            return redirect(url_for('admin'))
        elif action == 'DENY':
            users_ref.update({'Status': 'D'})
            print(
                jsonify({'message': 'User Denied successfully'}), 200)
            return redirect(url_for('admin'))
        else:
            return jsonify({'error': 'Invalid action'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
