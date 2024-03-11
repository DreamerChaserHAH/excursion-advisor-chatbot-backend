
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from fastapi import FastAPI
import os

load_dotenv()

app = FastAPI()
uri = os.getenv("URI")

client = MongoClient(uri, server_api=ServerApi('1'))

def ping_mongodb():
    try:
        client.admin.command('ping')
        return True
    except:
        return False

@app.get("/status")
def get_status_check():
    return {"Request Type": "GET", "API Working Status": "Up and Running!", "Mongo Status" : ping_mongodb()}

@app.post("/status")
def post_status_check():
    return {"Request Type": "POST", "API Working Status": "Up and Running!", "Mongo Status": ping_mongodb()}


