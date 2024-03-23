
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
import os

load_dotenv()

app = FastAPI()
uri = os.getenv("URI")

def get_country(country_name):
    country_information = client.ExcursionData.Countries.find_one({"name": country_name.lower()})
    if country_information is None:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Oops! It seems that I don't have information about the country of your choice yet! But no worries, I will notify the developers about your interest. Thank you!"
                        ]
                    }
                }
            ]
        }
    return {
        "fulfillmentMessages": [
            { 
                "text": {
                    "text": [
                        country_information["description"]
                    ]
                },
                "carouselBrowse": {
                    "items": [
                        {
                            "title": country_name + "'s Flag",
                            "image": {
                                "url": country_information["flag"]
                            },
                        }
                    ]
                }
            }
        ]
    }

def return_fullfillment():
    return {
    "fulfillmentMessages": [
        {
        "card": {
        "title": "card title",
        "subtitle": "card text",
        "imageUri": "https://example.com/images/example.png",
        "buttons": [
                        {
                            "text": "button text",
                            "postback": "https://example.com/path/for/end-user/to/follow"
                        }
                    ]
                }
            }
        ]
    }
 

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

@app.post("/get_data")
async def get_data(request: Request):
    data = await request.json()
    print(data)
    return get_country("myanmar")
        
