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

        vendor_email = db.collection('Users').document(
            user_id).get().get('Email')

        vendors_ref = db.collection('Vendors')
        query = vendors_ref.where("User_ID", "==", user_id)
        results = query.get()

        if len(results) == 0:
            vendors_ref.add({"Vendor_Name": vendor_email, "Phone_Number": "N/A",
                             "Address": "N/A", "About_Us": "N/A", "User_ID": user_id})
            query = vendors_ref.where("User_ID", "==", user_id)
            results = query.get()

        for result in results:
            vendor = result.to_dict()
            vendor['Email'] = vendor_email
            return vendor

    @staticmethod
    def get_all_vendors():
        return firestore.client().collection('Vendors').stream()

    @staticmethod
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

    @staticmethod
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
