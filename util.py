import os
import logging
from enum import Enum
from firebase_admin import credentials, initialize_app
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import InputRequired


def send_mail(subject, recipient, message):
    try:
        msg = Message(subject=subject,
                      sender='no-reply@vendorverse.com', recipients=[recipient])
        msg.html = message
        logging.info(f'Sending email {subject} to {recipient}...')
        Mail().send(msg)
    except Exception as e:
        logging.error(str(e))


def send_admin_notif(type):
    if type == "VENDOR":
        subject = "A New Vendor Registration is Pending Approval."

    elif type == "EMPLOYEE":
        subject = "A New Employee Registration is Pending Approval."

    elif type == "BOOKING":
        subject = "A New Booking is Pending Approval."

    else:
        return None

    send_mail(subject=subject, recipient=os.environ.get(
        'ADMIN_MAIL'), message="Please login to review Approval.")


def init_firebase():
    try:
        cred = credentials.Certificate(
            os.environ.get('FIREBASE_PRIVATE_KEY'))
        initialize_app(cred)
        logging.info("Firebase Admin initialized successfully")

    except Exception as e:
        logging.exception("Failed to initialize Firebase Admin: %s", e)


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


# config.py
class TestConfig:
    TESTING = True
    DEBUG = True
    FIRESTORE_PROJECT_ID = 'test-project'


class FlashCategory(Enum):
    SUCCESS = 'success'
    ERROR = 'danger'
    INFO = 'info'
    WARNING = 'warning'

    def __str__(self):
        return self.value


class BookingForm(FlaskForm):
    date = DateField('Date', validators=[InputRequired()])
    location = StringField('Location', validators=[InputRequired()])
    discount = TextAreaField('Discount', validators=[InputRequired()])
    title = TextAreaField(
        'Title', validators=[InputRequired()])
