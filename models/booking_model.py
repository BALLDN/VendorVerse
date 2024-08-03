from flask import request, session
from firebase_admin import firestore
from models.vendor_model import Vendor


class Booking:

    def __init__(self, date, deal, location, additional_info, vendor_id, status):
        self.date = date
        self.deal = deal
        self.location = location
        self.additional_info = additional_info
        self.vendor_id = vendor_id
        self.status = status

    def display(self):
        print(self.date, self.deal, self.location,
              self.additional_info, self.vendor_id, self.status)

    def get_date(self):
        return self.date

    @staticmethod
    def add_booking(title, location, date, deal, vendor_id):

        status = 'P'
        if (session['user_type'] == 'A'):
            status = "A"

        booking = {"Additional Info": title, "Location": location, "Date": date, "Deal": deal,
                   "Vendor_ID": vendor_id, "Status": status}
        update_time, doc_ref = firestore.client().collection("Bookings").add(booking)
        return update_time

    @staticmethod
    def get_users(database_connection):
        # gets all users from db
        users_ref = database_connection.collection('Users')
        docs = users_ref.get()
        for doc in docs:
            return ('{} => {}'.format(doc.id, doc.to_dict()))
        return docs

    @staticmethod
    def get_user_id(database_connection, email):
        users_ref = database_connection.collection('Users')

        query = users_ref.where("Email", "==", email)
        results = query.get()

        for doc in results:
            user_id = doc.id

        if len(results) > 0:
            return user_id
        else:
            return "No User Found!"

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

            # Log the booking to verify all fields
            print(f"Retrieved Booking: {booking}")

            detailed_bookings.append(booking)

        return detailed_bookings

    @staticmethod
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

    @staticmethod
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

            detailed_bookings.append(booking)

        return detailed_bookings

    @staticmethod
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

    @staticmethod
    def cancel_booking(booking_id):
        db = firestore.client()
        booking_ref = db.collection(
            'Bookings').document(booking_id)
        if booking_ref.get().exists:
            return booking_ref.update({"Status": "D"})
        else:
            raise Exception('Booking not found!')

    def edit_booking(database_connection, booking_id):
        booking_ref = database_connection.collection(
            'Bookings').document(booking_id)
        if booking_ref is not None:
            if (request.cookies.get('user_type') == "V"):
                status = "P"
            else:
                status = "A"
            date = request.form['date']
            location = request.form['location']
            additional_info = request.form['additional-info']

            '''In case discount checkbox isn't checked'''
            if request.form['deal'] is None:
                discount = "No Discount"
            else:
                discount = request.form['deal']

            print(booking_ref)
            booking_ref.update({"Status": status, "Date": date, "Location": location,
                               "Deal": discount, "`Additional Info`": additional_info})
            return booking_ref

        else:
            return "No User Found!"
