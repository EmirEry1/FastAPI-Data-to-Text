import os
from pymongo import MongoClient
import bcrypt

try:
    db_uri = os.environ["MONGO_URI"] 
except KeyError:
    raise Exception("Requested Environmental Variable does not exist.")

cluster = db_uri
client = MongoClient(cluster)
db = client.user_password
user_db = db.user_password

def get_password_by_user_name(user_name):
    user = user_db.find_one({"user_name": user_name})
    if user == None:
        return None
    else:
        return user["password"]

def insert(user_name, password):
    salt = bcrypt.gensalt(rounds=10)
    return user_db.insert_one({"user_name": user_name, "password": bcrypt.hashpw(password.encode('utf-8'), salt), "salt": salt })


