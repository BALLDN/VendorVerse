from datetime import datetime
from turtle import up
from flask import flash, redirect, request, jsonify, session
from firebase_admin import firestore


class Poll:

    @staticmethod
    def create_poll(title, options, vendor_name=None):

        firestore.client().collection('Polls').add({
            'title': title,
            'vendor_name': vendor_name,
            'options': options,
            'created_at': datetime.now(),
        })

    @staticmethod
    def get_all_polls():
        return firestore.client().collection('Polls').stream()

    @staticmethod
    def get_unresponded_polls(user_id):
        db = firestore.client()
        polls_ref = db.collection('Polls')
        polls = polls_ref.stream()

        unresponded_polls = []

        for poll in polls:
            responses_ref = polls_ref.document(poll.id).collection('Responses')
            response = responses_ref.document(user_id).get()
            if not response.exists:
                poll_data = poll.to_dict()
                poll_data['id'] = poll.id
                unresponded_polls.append(poll_data)

        return unresponded_polls

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

        return responses_ref.document(user_id).set({
            'selected_option': selected_option,
            'responded_at': datetime.now()
        })

    @staticmethod
    def get_poll_results(poll_id):
        db = firestore.client()
        poll_ref = db.collection('Polls').document(poll_id)
        responses_ref = poll_ref.collection('Responses')

        responses = responses_ref.get()

        if not responses:
            return {}, 0

        total_responses = len(responses)
        option_counts = {}

        for response in responses:
            selected_option = response.get('selected_option')
            if selected_option:
                if selected_option in option_counts:
                    option_counts[selected_option] += 1
                else:
                    option_counts[selected_option] = 1

        option_percentages = {
            option: (count / total_responses) * 100
            for option, count in option_counts.items()
        }

        return option_percentages, total_responses
