from flask import request


class Vendor:

    def __init__(self, about_us, address, phone_number, user_id, vendor_name):
        self.about_us = about_us
        self.address = address
        self.phone_number = phone_number
        self.user_id = user_id
        self.vendor_name = vendor_name

    def display(self):
        print(self.email, self.password, self.user_type, self.status)

    @staticmethod
    def get_vendor_by_user_id(database_connection, user_id):

        vendors_ref = database_connection.collection('Vendors')

        query = vendors_ref.where("User_ID", "==", user_id)
        results = query.get()

        for result in results:
            return result
        return result

    @staticmethod
    def get_vendor_by_user_id(database_connection, user_id):

        vendors_ref = database_connection.collection('Vendors')

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

    # Change to return entire user credentials
    @staticmethod
    def validate_user(database_connection):
        users_ref = database_connection.collection('Users')
        form_email = request.form['Email']
        password = request.form['Password']

        query = users_ref.where("Email", "==", form_email)
        results = query.get()

        for doc in results:
            found_user_type = doc.to_dict().get("User_Type")
            found_password = doc.to_dict().get("Password")

        if len(results) > 0 and found_password == password:
            # Decides which Homepage to load based on user type
            return found_user_type
        else:
            return "Invalid Email or Password!"
