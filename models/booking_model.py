from flask import session
from firebase_admin import firestore
from models.vendor_model import Vendor
from util import send_mail


class Booking:

    def __init__(self, date, deal, location, title, vendor_id, status):
        self.date = date
        self.deal = deal
        self.location = location
        self.title = title
        self.vendor_id = vendor_id
        self.status = status

    def display(self):
        print(self.date, self.deal, self.location,
              self.title, self.vendor_id, self.status)

    def get_date(self):
        return self.date

    @staticmethod
    def create_booking(title, location, date, deal, vendor_id):

        status = 'P'
        if (session['user_type'] == 'A'):
            status = "A"

        booking = {"Title": title, "Location": location, "Date": date, "Deal": deal,
                   "Vendor_ID": vendor_id, "Status": status}
        update_time, doc_ref = firestore.client().collection("Bookings").add(booking)
        return update_time

    @staticmethod
    def read_booking(booking_id):
        return firestore.client().collection('Bookings').document(booking_id).get().to_dict()

    @staticmethod
    def update_booking(booking_id, title, location, date, deal):

        booking_ref = firestore.client().collection('Bookings').document(booking_id)
        vendor_id = booking_ref.get().get('Vendor_ID')

        if vendor_id != session['user_id'] and session['user_type'] == 'A':
            send_mail("Your Booking has been updated by the Admin.",
                      Booking.get_vendor_email_by_booking_id(booking_id), "Please login to verify.")

        updated_details = {"Title": title, "Location": location, "Date": date, "Deal": deal,
                           "Status": 'A' if (session['user_type'] == 'A') else 'P'}
        return booking_ref.update(updated_details)

    @staticmethod
    def delete_booking(booking_id):
        db = firestore.client()
        booking_ref = db.collection(
            'Bookings').document(booking_id)
        if booking_ref.get().exists:
            return booking_ref.update({"Status": "D"})
        else:
            raise Exception('Booking not found!')

    @ staticmethod
    def get_all_bookings():
        detailed_bookings = []
        bookings = firestore.client().collection('Bookings').get()
        for booking_snapshot in bookings:
            booking = booking_snapshot.to_dict()  # Convert DocumentSnapshot to dictionary
            booking['id'] = booking_snapshot.id

            vendor_id = booking.get("Vendor_ID")
            vendor_details = Vendor.get_vendor_by_user_id(vendor_id)

            # Ensure vendor_details is a dictionary and log any potential issues
            if vendor_details:
                booking['Vendor_Name'] = vendor_details.get('Vendor_Name')
                booking['Vendor_Phone'] = vendor_details.get(
                    'Phone_Number')
                booking['Vendor_Address'] = vendor_details.get('Address')
                booking['Vendor_Email'] = vendor_details.get('Email')

            detailed_bookings.append(booking)

        return detailed_bookings

    @ staticmethod
    def get_bookings_by_vendor_id(vendor_id):
        detailed_bookings = []
        bookings = firestore.client().collection(
            'Bookings').where("Vendor_ID", "==", vendor_id).get()
        vendor_details = Vendor.get_vendor_by_user_id(vendor_id)

        for booking_snapshot in bookings:
            booking = booking_snapshot.to_dict()
            booking['id'] = booking_snapshot.id

            if vendor_details:
                booking['Vendor_Name'] = vendor_details.get('Vendor_Name')
                booking['Vendor_Phone'] = vendor_details.get('Phone_Number')
                booking['Vendor_Address'] = vendor_details.get('Address')
                booking['Vendor_Email'] = vendor_details.get('Email')

            # Log the booking to verify all fields
            print(f"Retrieved Booking: {booking}")

            detailed_bookings.append(booking)

        return detailed_bookings

    @ staticmethod
    def get_approved_bookings():
        detailed_bookings = []
        bookings = firestore.client().collection(
            'Bookings').where("Status", "==", "A").get()
        for booking_snapshot in bookings:
            booking = booking_snapshot.to_dict()
            booking['id'] = booking_snapshot.id

            vendor_id = booking.get("Vendor_ID")
            vendor_details = Vendor.get_vendor_by_user_id(vendor_id)

            # Ensure vendor_details is a dictionary and log any potential issues
            if vendor_details:
                booking['Vendor_Name'] = vendor_details.get('Vendor_Name')
                booking['Vendor_Phone'] = vendor_details.get('Phone_Number')
                booking['Vendor_Address'] = vendor_details.get('Address')

            # Log the booking to verify all fields
            print(f"Retrieved Booking: {booking}")

            detailed_bookings.append(booking)

        return detailed_bookings

    @ staticmethod
    def get_pending_bookings_with_details():
        db = firestore.client()
        detailed_bookings = []
        booking_ref = db.collection('Bookings')
        pending_bookings = booking_ref.where("Status", "==", "P").get()
        for booking_snapshot in pending_bookings:
            booking = booking_snapshot.to_dict()
            booking['id'] = booking_snapshot.id

            vendor_id = booking.get("Vendor_ID")
            vendor_details = Vendor.get_vendor_by_user_id(vendor_id)

            if vendor_details:
                booking['Vendor_Name'] = vendor_details.get('Vendor_Name')
                booking['Vendor_Phone'] = vendor_details.get(
                    'Phone_Number')
                booking['Vendor_Address'] = vendor_details.get('Address')
                booking['Vendor_Email'] = vendor_details.get('Email')

            detailed_bookings.append(booking)

        return detailed_bookings

    @ staticmethod
    def get_vendor_email_by_booking_id(booking_id):
        db = firestore.client()
        vendor_id = db.collection('Bookings').document(
            booking_id).get().get('Vendor_ID')
        return db.collection('Users').document(vendor_id).get().get('Email')
