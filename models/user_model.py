from flask import flash, redirect, request, url_for
from firebase_admin import firestore


class User:

    def __init__(self, email, password, user_type, status):
        self.email = email
        self.password = password
        self.user_type = user_type
        self.status = status

    def display(self):
        print(self.email, self.password, self.user_type, self.status)

    @staticmethod
    def add_user(uid, email, user_type,):
        db = firestore.client()
        data = {"Email": email, "User_Type": user_type, "Status": "P"}
        db.collection("Users").document(uid).set(data)

    @staticmethod
    def get_user_id_from_email(database_connection, email):
        users_ref = database_connection.collection('Users')
        query = users_ref.where("Email", "==", email)
        results = query.get()

        for doc in results:
            user_id = doc.id

        if len(results) > 0:
            return user_id
        else:
            return "No User Found!"

    @staticmethod
    def get_users(database_connection):
        # gets all users from db
        users_ref = database_connection.collection('Users')
        docs = users_ref.get()
        for doc in docs:
            return ('{} => {}'.format(doc.id, doc.to_dict()))
        return docs

    @staticmethod
    def get_pending_users(database_connection):
        users_ref = database_connection.collection('Users')
        query = users_ref.where("Status", "==", "P")
        results = query.get()
        return results

    @staticmethod
    def reset_user_password(database_connection, email, current_password, new_password, confirmed_password):
        users_ref = database_connection.collection('Users')
        query = users_ref.where("Email", "==", email)
        results = query.get()

        if not results:
            return {'status': 'error', 'message': 'This User does not exist'}

        user = results[0]
        user_data = user.to_dict()

        # Validate current password
        if user_data['Password'] != current_password:
            return {'status': 'error', 'message': 'Current password is incorrect'}

        # Validate new password and confirmed password
        if new_password != confirmed_password:
            print(new_password)
            print(confirmed_password)
            return {'status': 'error', 'message': 'New password and confirm password do not match'}

        user.reference.update({"Password": new_password})

        return {'status': 'success', 'message': 'Password reset successfully!'}

    @staticmethod
    def get_user_by_user_id(database_connection, user_id):
        users_ref = database_connection.collection('Users')
        query = users_ref.where("User_ID", "==", user_id)
        results = query.get()
        return results

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
