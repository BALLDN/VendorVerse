import firebase_admin
from user_model import users
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)

#Put in to Flash Error Message, need to improve sessions later
app.secret_key = "Secret Key"

# Use the application default credentials.

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        users.get_users(db)
        
    if request.method == 'POST':
        if(users.validate_user(db) == "V"):
            return redirect(url_for('vendor'))
        elif(users.validate_user(db) == "E"):
            return redirect(url_for('employee'))
        elif(users.validate_user(db) == "A"):
            return redirect(url_for('admin'))
        else:
            #Error Message displays as appropriate
            flash(users.validate_user(db))
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = users.add_user(db)
        flash("Your Account is Pending Approval")
        return redirect(url_for('register'))
        
        
    return render_template('register.html')


@app.route('/')
def index():
    return render_template('public_home_page.html')


@app.route('/vendor')
def vendor():
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