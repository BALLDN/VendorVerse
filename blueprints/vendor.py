from flask import Blueprint, redirect, render_template, request, url_for, flash
from models.user_model import User
from models.vendor_model import Vendor

vendor_bp = Blueprint('vendor', __name__)


@vendor_bp.route('/vendor')
def vendor():
    return render_template('vendor_home_page.html')


@vendor_bp.route('/vendor_details', methods=['GET', 'POST'])
def vendor_details_page():
    db = firestore.client()
    email = request.cookies.get('login_email')
    user_id = User.get_user_id_from_email(db, email)
    if request.method == 'POST':
        Vendor.add_vendor_details(db, user_id)
        flash(
            "Your Details have been saved and your account is pending approval")
        return redirect(url_for('index'))

    return render_template('vendor_details_page.html')
