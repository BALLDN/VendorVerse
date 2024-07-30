from flask import request
from firebase_admin import firestore


class Vendor:

    def __init__(self, vendor_name, phone_number, address, about_us, user_id):
        self.about_us = about_us
        self.address = address
        self.phone_number = phone_number
        self.user_id = user_id
        self.vendor_name = vendor_name

    @staticmethod
    def get_vendor_by_user_id(user_id):
        db = firestore.client()

        vendors_ref = db.collection('Vendors')

        query = vendors_ref.where("User_ID", "==", user_id)
        results = query.get()

        for result in results:
            return result
        else:
            dictionary = {
                "About_Us": "None",
                "Address": "None",
                "Phone_Number": "None",
                "User_ID": "None",
                "Vendor_Name": "None"
            }

            return dictionary

    @staticmethod
    def get_users(database_connection):
        # gets all users from db
        users_ref = database_connection.collection('Vendors')
        docs = users_ref.get()
        return docs

    def add_vendor_details(database_connection, user_id):
        # adds a vendors details to db
        vendor_name = request.form['vendor_name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        about_us = request.form['about_us']

        vendor_details = Vendor(vendor_name, phone_number,
                                address, about_us, user_id)

        details = {"Vendor_Name": vendor_details.vendor_name, "Phone_Number": vendor_details.phone_number,
                   "Address": vendor_details.address, "About_Us": vendor_details.about_us, "User_ID": user_id}
        database_connection.collection("Vendors").add(details)
        return details

    def edit_vendor_details(database_connection, user_id):
        vendor_ref = database_connection.collection(
            'Vendors').where('User_ID', '==', user_id).get()

        vendor = vendor_ref[0]

        # edits a vendors details to db
        vendor_name = request.form['vendor_name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        about_us = request.form['about_us']

        updated_details = {
            "Vendor_Name": vendor_name,
            "Phone_Number": phone_number,
            "Address": address,
            "About_Us": about_us,
        }

        database_connection.collection('Vendors').document(
            vendor.id).update(updated_details)

        return updated_details
