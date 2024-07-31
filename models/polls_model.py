import datetime
from flask import flash, redirect, request, jsonify, url_for, session
from firebase_admin import firestore


class Polls:

    @staticmethod
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

        print(jsonify({'message': 'Poll created',
              'poll_id': poll_ref[1].id}), 201)

        return poll_ref

    @staticmethod
    def get_polls():
        db = firestore.client()
        polls_ref = db.collection('Polls')
        docs = polls_ref.get()

        return docs

    @staticmethod
    def get_polls_by_vendor_id(database_connection, vendor_id):
        polls_ref = database_connection.collection(
            'Polls').where('Vendor_ID', '==', vendor_id)
        docs = polls_ref.get()

        return docs

    @staticmethod
    def submit_response(poll_id, selected_option):
        db = firestore.client()

        user_id = session['user_id']

        poll_ref = db.collection('Polls').document(poll_id)
        responses_ref = poll_ref.collection('Responses')

        existing_response = responses_ref.document(user_id).get()
        if existing_response.exists:
            raise Exception('You have already responded to this poll')

        # Store the response
        return responses_ref.document(user_id).set({
            'selected_option': selected_option,
            'responded_at': datetime.datetime.now()
        })

    @staticmethod
    def get_poll_results(database_connection, poll_id):
        poll_ref = database_connection.collection('Polls').document(poll_id)
        responses_ref = poll_ref.collection('Responses')

        # Retrieve all responses
        responses = responses_ref.get()

        # If there are no responses, return empty results
        if not responses:
            return {}, 0

        # Count the total number of responses and responses for each option
        total_responses = len(responses)
        option_counts = {}

        for response in responses:
            selected_option = response.get('selected_option')
            if selected_option:
                if selected_option in option_counts:
                    option_counts[selected_option] += 1
                else:
                    option_counts[selected_option] = 1

        # Calculate the percentage for each option
        option_percentages = {
            option: (count / total_responses) * 100
            for option, count in option_counts.items()
        }

        return option_percentages, total_responses
