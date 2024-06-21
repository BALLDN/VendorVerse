from flask import request


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

    @staticmethod
    def add_booking(database_connection, vendor_id):

        # adds a user to db
        if (request.cookies.get('user_type') == "V"):
            status = "P"
        else:
            status = "A"
        date = request.form['Date']
        location = request.form['Location']
        additional_info = request.form['additional_info']

        '''In case discount checkbox isn't checked'''
        if request.form.get('discount_checkbox') is None or request.form('discount') is None:
            deal = "No Discount"
        else:
            deal = request.form['discount']

        booking_details = Booking(
            date, deal, location, additional_info, vendor_id, status)

        booking = {"Date": booking_details.date, "Deal": booking_details.deal, "Location": booking_details.location,
                   "Additional Info": booking_details.additional_info, "Vendor_ID": booking_details.vendor_id, "Status": booking_details.status}
        database_connection.collection("Bookings").add(booking)
        return booking

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

    def get_bookings_by_vendor_id(database_connection, vendor_id):
        booking_ref = database_connection.collection('Bookings')
        docs = booking_ref.get()
        for doc in docs:
            print('{} => {}'.format(doc.id, doc.to_dict()))
            return ('{} => {}'.format(doc.id, doc.to_dict()))
        return docs

    def remove_booking(database_connection, booking_id):

        booking_ref = database_connection.collection('Users')

        query = booking_ref.where(__name__, "==", booking_id)
        results = query.get()

        for doc in results:
            user_id = doc.id

        if len(results) > 0:
            print("found")
            print(user_id)
            return user_id
        else:
            return "No User Found!"
