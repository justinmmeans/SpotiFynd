from flask import Flask
from flask_bootstrap import Bootstrap
from secret_key_gen import generate_secret_key
from dotenv import load_dotenv
import os

generate_secret_key()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
Bootstrap(app)

from app import routes