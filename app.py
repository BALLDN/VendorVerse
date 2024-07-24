import os
from dotenv import load_dotenv
from flask import Flask, render_template
from firebase_admin import firestore

from firebase_config import init_firebase_admin
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.vendor import vendor_bp
from blueprints.booking import booking_bp
from util import *
from models.booking_model import Booking


load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get('APP_SECRET_KEY')
    if test_config:
        app.config.from_object(test_config)

    init_firebase_admin()

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(booking_bp)

    @app.route('/', methods=['GET'])
    def index():
        bookings = Booking.get_approved_bookings(firestore.client())

        return render_template('public_home_page.html', bookings=bookings)

    @app.route('/employee')
    def employee():
        return render_template('employee_home_page.html', user_type='E')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
