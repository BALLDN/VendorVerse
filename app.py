import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, flash, request, redirect, url_for

from blueprints.auth import auth_bp, role_required
from blueprints.admin import admin_bp
from blueprints.vendor import vendor_bp
from blueprints.booking import booking_bp
from blueprints.poll import poll_bp

from models.polls_model import Polls
from util import *


load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get('APP_SECRET_KEY')
    if test_config:
        app.config.from_object(test_config)

    init_firebase()

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(poll_bp)

    @app.route('/', methods=['GET'])
    def index():
        if request.args.get('status') == 'PENDING':
            flash("Your account is still pending approval. Please come back later.",
                  FlashCategory.INFO.value)

        user_type = session.get('user_type')
        if user_type and session.get('access_token'):
            if user_type == 'A':
                return redirect(url_for('admin.view_admin_dashboard'))
            elif user_type == 'V':
                return redirect(url_for('vendor.view_vendor_dashboard'))
            elif user_type == 'E':
                return redirect(url_for('employee'))
        else:
            return render_template('public_home_page.html')

    @app.route('/employee', methods=['GET'])
    @role_required('E')
    def employee():
        polls = Polls.get_polls()
        return render_template('employee_home_page.html', home_url=url_for('employee'), polls=polls)

    @app.route('/about', methods=['GET'])
    def about():
        return render_template('about_us.html')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
