from flask import request


class User:

    def __init__(self, email, password, user_type, status):
        self.email = email
        self.password = password
        self.user_type = user_type
        self.status = status

    def display(self):
        print(self.email, self.password, self.user_type, self.status)

    @staticmethod
    def add_user(database_connection):

        # adds a user to db
        status = "P"
        email = request.form['Email']
        password = request.form['Password']
        user_type = request.form['User_Type'][0]

        user_credentials = User(email, password, user_type, status)

        user = {"Email": user_credentials.email, "Password": user_credentials.password,
                "User_Type": user_credentials.user_type, "Status": user_credentials.status}
        database_connection.collection("Users").add(user)
        return user

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
