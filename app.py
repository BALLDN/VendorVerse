import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, flash, request, redirect, url_for

from blueprints.auth import auth_bp, role_required
from blueprints.admin import admin_bp
from blueprints.vendor import vendor_bp
from blueprints.booking import booking_bp
from blueprints.poll import poll_bp

from models.poll_model import Poll
from util import *


load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = '4c6dc14e4a73d4'
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    Mail(app)

    app.secret_key = os.environ.get('APP_SECRET_KEY')
    if test_config:
        app.config.from_object(test_config)

    init_firebase()
    setup_logging()

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
        if request.args.get('status') == 'DENIED':
            flash("Your registration has been denied by the Admin.",
                  FlashCategory.ERROR.value)

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

    @app.route('/about', methods=['GET'])
    def about():
        return render_template('about_us.html')

    @app.route('/employee', methods=['GET'])
    @role_required(['E'])
    def employee():
        polls = Poll.get_unresponded_polls(session['user_id'])
        return render_template('employee_home_page.html', home_url=url_for('employee'), polls=polls)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error_404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error_500.html'), 500

    return app

    #         # Set cookies for login details + user type
    #         url_response.set_cookie('login_email', login_email)
    #         url_response.set_cookie('user_type', User.validate_user(db))

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
