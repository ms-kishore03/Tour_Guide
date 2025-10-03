from pymongo import MongoClient
import bcrypt
import re

client = MongoClient('mongodb+srv://tester_username:tester_password@ai-tour-guide.mzeft5j.mongodb.net/')

# Access the database
db = client['Users_Database']

# Access the correct collection
users = db['Users']

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
        return "All fields are required!"
    
    user = users.find_one({"username": username})
    if not user:
        return "User not found!"
    if user and not bcrypt.checkpw(password.encode("utf-8"), user['password']):
        return "Incorrect password!"
    
    if user and bcrypt.checkpw(password.encode("utf-8"), user['password']):
        login = True
        return login
        
    return "Invalid username or password!"  