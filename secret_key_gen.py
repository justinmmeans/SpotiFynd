import secrets
import os
from dotenv import load_dotenv, set_key

def generate_secret_key():# Load existing .env file
    
    load_dotenv()

    #Generate a new secret key
    new_secret_key = secrets.token_hex(16)
    
    print('New secret key:', new_secret_key)

    #Write the new secret key to the .env file
    set_key('.env', 'SECRET_KEY', new_secret_key)

    