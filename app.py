from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('home_page.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')
