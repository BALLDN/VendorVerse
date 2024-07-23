from firebase_admin import credentials, initialize_app
import logging
import os


def init_firebase_admin():
    try:
        cred = credentials.Certificate(
            os.environ.get('FIREBASE_PRIVATE_KEY'))
        initialize_app(cred)
        logging.info("Firebase Admin initialized successfully")
    except Exception as e:
        logging.exception("Failed to initialize Firebase Admin: %s", e)
