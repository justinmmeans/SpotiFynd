from app import app
from flask import render_template

@app.route('/')
def home(): #corresponds to home.html in templates
    return render_template('home.html')

@app.route('/index')
def index():
    return "Hello, World!"
