import datetime
from flask import flash, redirect, request, jsonify, url_for
from models.user_model import User

class Polls:

    def create_poll(database_connection):
        data = request.json
        title = data.get('PollTitle')
        User_ID = data.get('VendorName')
        amount = int(request.form.get('Amount'))
        
        choices = []
        for i in range(1, amount + 1):
            choice = request.form.get(f'choice{i}')
            if choice:
                choices.append(choice)

        if not title or not choices:
            print(jsonify({'error': 'Missing fields'}), 400)

        poll_ref = database_connection.collection('Polls').add({
            'Title': title,
            'Vendor_Name': User_ID,
            'options': choices,
            'createdAt': datetime.now(),
        })
        
        print(jsonify({'message': 'Poll created', 'poll_id': poll_ref[1].id}), 201)
        
        return poll_ref
    
    
        
    def get_polls(database_connection):
        polls_ref = database_connection.collection('Polls')
        docs = polls_ref.get()
        
        return docs
    
    def submit_response(database_connection):
        poll_id = request.form.get('poll_id')
        selected_option = request.form.get('selected_option')
        user_id = User.get_user_id_from_email(database_connection, request.cookies.get('login_email'))
        
        if not poll_id or not user_id:
            flash('You are not logged in!')
            return redirect(url_for('employee_polls'))
        
        if(not selected_option):
            flash('You have not selected an option!')
            return redirect(url_for('employee_polls'))

        poll_ref = database_connection.collection('Polls').document(poll_id)
        responses_ref = poll_ref.collection('Responses')

        # Check if the user has already responded to the poll
        existing_response = responses_ref.where('user_id', '==', user_id).get()

        if existing_response:
            flash('You have already responded to this poll')
            return redirect(url_for('employee_polls'))

        # Store the response
        responses_ref.add({
            'user_id': user_id,
            'selected_option': selected_option,
            'createdAt': datetime.datetime.now()
        })

        flash('Your response has been recorded')
        return redirect(url_for('employee_polls'))