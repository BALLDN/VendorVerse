from flask import request

class bookings:
    
    def __init__(self, date, deal, location, additional_info, vendor_ID, status):
        self.date = date
        self.deal = deal
        self.location = location
        self.additional_info = additional_info
        self.vendor_ID = vendor_ID
        self.status = status
        
        
    def display(self):
        print(self.date, self.deal, self.location, self.additional_info, self.vendor_ID, self.status)
        
    def add_booking(database_connection, vendor_id):
        
        #adds a user to db
        status = "P"
        date= request.form['Date']
        location= request.form['Location']
        additional_info = request.form['additional_info']
        vendor_id = vendor_id
        
        '''In case discount checkbox isn't checked'''
        if request.form.get('discount_checkbox') is None or request.form('discount') is None:
            deal = "No Discount"
        else:
            deal= request.form['discount']
        
        booking_details = bookings(date, deal, location, additional_info, vendor_id, status)
        
        booking = {"Date": booking_details.date, "Deal": booking_details.deal, "Location": booking_details.location,"Additional Info": booking_details.additional_info, "Vendor_ID": booking_details.vendor_ID, "Status": booking_details.status}
        database_connection.collection("Bookings").add(booking) 
        return booking
    
    
    def get_users(database_connection):
        #gets all users from db
        users_ref = database_connection.collection('Users')
        docs = users_ref.get()
        for doc in docs:
            return('{} => {}'.format(doc.id, doc.to_dict()))
        return docs
    
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
    
        
        

        
        
       
        
   