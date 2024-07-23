
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired
from firebase_admin import firestore

import logging
import os


def setup_logging():
    # Configure logging for general messages (e.g., debug, info, error)
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler("logs/vendorverse.log"),  # General log file
            logging.StreamHandler()  # Print logs to console
        ]
    )

    # Setup Auth Audit Logging
    auth_logger = logging.getLogger('auth_audit')
    auth_logger.setLevel(logging.INFO)

    auth_handler = logging.FileHandler("logs/auth_audit.log")
    auth_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))

    auth_logger.addHandler(auth_handler)


class BookingForm(FlaskForm):
    date = DateField('Date', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    discount = TextAreaField('Discount', validators=[InputRequired()])
    additional_info = TextAreaField(
        'Additional Information', validators=[InputRequired()])


# config.py
class TestConfig:
    TESTING = True
    DEBUG = True
    FIRESTORE_PROJECT_ID = 'test-project'
