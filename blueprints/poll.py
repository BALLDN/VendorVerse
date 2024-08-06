import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from firebase_admin import firestore

from blueprints import vendor
from blueprints.auth import role_required
from models.poll_model import Poll
from models.vendor_model import Vendor
from util import FlashCategory

poll_bp = Blueprint('poll', __name__, url_prefix='/poll')


@poll_bp.route('/create', methods=['GET', 'POST'])
@role_required(['A'])
def create_poll():

    form = request.form.to_dict()
    title = form['title']
    vendor_name = form['vendor_name'] or None
    options = [value for key, value in form.items()
               if key.startswith('option')]

    try:
        Poll.create_poll(title, options, vendor_name)

        flash("Poll has been created successfully.",
              FlashCategory.SUCCESS.value)

    except Exception as e:
        flash("An error has occured during the creation of a Poll. Please try again.",
              FlashCategory.ERROR.value)
        logging.error(e)

    finally:
        return redirect(url_for('admin.view_polls_manager'))


@ poll_bp.route('/submit_poll_response', methods=['POST'])
@ role_required(['E'])
def submit_poll_response():
    try:
        poll_id = request.form.get('poll_id')
        selected_option = request.form.get('selected_option')

        if not poll_id:
            raise Exception(
                'We have encountered an issue submitting your response. Please try again.')

        if (not selected_option):
            raise Exception('You have not selected an option!')

        result = Poll.submit_response(poll_id, selected_option)
        if result.update_time:
            flash('Your response has been submitted successfully.',
                  FlashCategory.SUCCESS.value)
    except Exception as e:
        flash(str(e), FlashCategory.ERROR.value)
    finally:
        return redirect(url_for('employee'))
