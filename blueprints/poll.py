from flask import Blueprint, render_template, request, flash, redirect, url_for
from firebase_admin import firestore

from blueprints.auth import role_required
from models.polls_model import Polls
from models.vendor_model import Vendor
from util import FlashCategory

poll_bp = Blueprint('polls', __name__)


@poll_bp.route('/admin_polls', methods=['GET', 'POST'])
@role_required('A')
def admin_polls():
    db = firestore.client()

    polls = Polls.get_polls()

    poll_results = []

    if request.method == 'GET':
        vendors = Vendor.get_users(db)
        for poll in polls:
            poll_info = poll.to_dict()
            option_percentages, total_responses = Polls.get_poll_results(
                db, poll.id)

            poll_result = {
                'poll_id': poll.id,
                'poll_data': poll_info,
                'option_percentages': option_percentages,
                'total_responses': total_responses
            }
            poll_results.append(poll_result)
            print(poll_results)

        return render_template('admin_polls_page.html', vendors=vendors, poll_results=poll_results)

    if request.method == 'POST':
        _create_poll(db)
        return redirect(url_for('admin.view_admin_dashboard'))
    return render_template('poll.admin_polls')


@poll_bp.route('/submit_poll_response', methods=['POST'])
@role_required('E')
def submit_poll_response():
    try:
        poll_id = request.form.get('poll_id')
        selected_option = request.form.get('selected_option')

        if not poll_id:
            raise Exception(
                'We have encountered an issue submitting your response. Please try again.')

        if (not selected_option):
            raise Exception('You have not selected an option!')

        result = Polls.submit_response(poll_id, selected_option)
        if result.update_time:
            flash('Your response has been recorded',
                  FlashCategory.SUCCESS.value)
    except Exception as e:
        flash(str(e), FlashCategory.ERROR.value)
    finally:
        return redirect(url_for('employee'))


def _create_poll(database_connection):
    # Ensure we're handling form data
    data = request.form
    title = data.get('PollTitle')
    vendor_id = data.get('VendorName')

    # Set vendor information based on availability
    if vendor_id:
        vendor_ref = database_connection.collection(
            'Vendors').document(vendor_id)
        vendor = vendor_ref.get()
        name = vendor.get("Vendor_Name") if vendor.exists else "No Vendor"
    else:
        vendor_id = "No Vendor"
        name = "No Vendor"

    amount = int(data.get('Amount'))

    choices = []
    for i in range(1, amount + 1):
        choice = data.get(f'choice{i}')
        if choice:
            choices.append(choice)

    if not title or not choices:
        flash('Missing fields')
        return redirect(url_for('admin_polls'))

    poll_ref = database_connection.collection('Polls').add({
        'Title': title,
        'Vendor_ID': vendor_id,
        'options': choices,
        'createdAt': datetime.datetime.now(),
        'Vendor_Name': name
    })

    # Get the ID of the newly created poll
    poll_id = poll_ref[1].id

    flash("A poll has been created. To view the poll, navigate to the View/Create Polls Page")
    return redirect(url_for('admin_polls'))
