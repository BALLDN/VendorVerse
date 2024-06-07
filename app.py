import firebase_admin
from user_model import users
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# Use the application default credentials.

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        users.get_users(db)
        
    if request.method == 'POST':
        if(users.validate_user(db)):
            return redirect(url_for('home'))
        else:
            return "Invalid Credentials"
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users.add_user(db)
        return redirect(url_for('home'))
        
    return render_template('register.html')


@app.route('/')
def hello():
    return render_template('public_home_page.html')


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