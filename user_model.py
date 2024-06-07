from flask import request

class users:
    
    def __init__(self, email, password, user_type, status):
        self.email = email
        self.password = password
        self.user_type = user_type
        self.status = status
        
    def display(self):
        print(self.email, self.password, self.user_type, self.status)
        
    def add_user(database_connection):
        
        #adds a user to db
        status = "P"
        email= request.form['Email']
        password= request.form['Password']
        user_type= request.form['User_Type'][0]
        
        user_credentials = users(email, password, user_type, status)
        
        user = {"Email": user_credentials.email, "Password": user_credentials.password, "User_Type": user_credentials.user_type,"Status": user_credentials.status}
        database_connection.collection("Users").add(user) 
        return "User has been added"
    
    def get_users(database_connection):
        #gets all users from db
        users_ref = database_connection.collection('Users')
        docs = users_ref.get()
        for doc in docs:
            print('{} => {}'.format(doc.id, doc.to_dict()))
        return docs
    
    def validate_user(database_connection):
        users_ref = database_connection.collection('Users')
        docs = users_ref.get()
        for doc in docs:
            if(doc.select("Email") ==  request.form['Email'] & doc.select("Password") ==  request.form['Email']):
                return True
        return False
   