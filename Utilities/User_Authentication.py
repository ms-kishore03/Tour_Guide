from pymongo import MongoClient
import bcrypt
import re
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from config import settings
load_dotenv()

client = settings.mongo_db_client

# Access the database
db = client['Tour_Guide']

# Access the correct collection
users = db['Users_Database']

def register(username, password, confirm_password, email):

    if not username or not password or not confirm_password or not email:
        return "All fields are required!"

    if users.find_one({"username": username}):
        print("User already exists...... Proceeding to login")
        login(username, password)
    
    elif users.find_one({"email": email}):
        return "Email already registered! Please use a different email."

    if password != confirm_password:
        return "Passwords do not match!"
    
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return "Invalid email address!"

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed_pw, "email": email})

    return "User registered successfully!"

def login(username, password):

    login = False

    if not username or not password:
        return False
    
    user = users.find_one({"username": username})
    if not user:
        return False
    
    if user and not bcrypt.checkpw(password.encode("utf-8"), user['password']):
        return False
    
    if user and bcrypt.checkpw(password.encode("utf-8"), user['password']):
        login = True
        return login
        
    return False  

