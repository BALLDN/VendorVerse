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
    def get_user_by_user_id(user_id):
        user_doc = firestore.client().collection('Users').document(user_id).get()
        return user_doc.to_dict()
