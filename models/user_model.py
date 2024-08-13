from firebase_admin import firestore
import logging

from models.vendor_model import Vendor


class User:

    def __init__(self, email, password, user_type, status):
        self.email = email
        self.password = password
        self.user_type = user_type
        self.status = status

    @staticmethod
    def add_user(uid, email, user_type):

        data = {"Email": email,
                "User_Type": user_type, "Status": "P"}
        firestore.client().collection("Users").document(uid).set(data)

    @staticmethod
    def get_all_users():
        users_ref = firestore.client().collection('Users')
        docs = users_ref.get()
        for doc in docs:
            return (f'{doc.id} => {doc.to_dict()}')
        return docs

    @staticmethod
    def get_pending_employees():
        return firestore.client().collection('Users').where("Status", "==", "P").where(
            "User_Type", "==", "E").get()

    @staticmethod
    def get_pending_vendors_with_details():
        pending_vendors_with_details = []
        pending_vendors = firestore.client().collection('Users').where("Status", "==", "P").where(
            "User_Type", "==", "V").get()

        for vendor_snapshot in pending_vendors:
            vendor = vendor_snapshot.to_dict()
            vendor['id'] = vendor_snapshot.id

            vendor_details = Vendor.get_vendor_by_user_id(vendor['id'])

            if vendor_details:
                vendor['vendor_name'] = vendor_details.get('Vendor_Name')
                vendor['vendor_phone'] = vendor_details.get(
                    'Phone_Number')
                vendor['vendor_address'] = vendor_details.get('Address')

            pending_vendors_with_details.append(vendor)

        return pending_vendors_with_details

    @staticmethod
    def get_user_by_user_id(user_id):
        user_doc = firestore.client().collection('Users').document(user_id).get()
        if not user_doc.exists:
            raise Exception('User not found.')
        return user_doc.to_dict()
