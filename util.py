from firebase_admin import credentials, firestore, App, initialize_app
from google.cloud.firestore import Client
import logging
import os


import logging


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


def init_firebase_admin() -> App:
    try:
        cred = credentials.Certificate(os.environ.get('FIREBASE_PRIVATE_KEY'))
        admin = initialize_app(cred)
        logging.info("Firebase Admin initialized successfully")
        return admin
    except Exception as e:
        logging.exception("Failed to initialize Firebase Admin: %s", e)


def init_firestore() -> Client:
    try:
        db = firestore.client(init_firebase_admin())
        logging.info("Cloud Firestore initialized successfully")
    except Exception as e:
        logging.exception("Failed to initialize Cloud Firestore: %s", e)

    return db
