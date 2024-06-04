from flask import Flask, redirect, render_template, request, url_for
from flask import jsonify

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('public_home_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('vendor_details_page'))
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/vendor')
def home():
    return render_template('vendor_home_page.html')

@app.route('/employee')
def employee():
    return render_template('employee_home_page.html')

@app.route('/admin')
def admin():
    return render_template('admin_home_page.html')

@app.route('/reset')
def reset():
    return render_template('forgot_password.html')

@app.route('/vendor_details')
def vendor_details_page():
    return render_template('vendor_details_page.html')