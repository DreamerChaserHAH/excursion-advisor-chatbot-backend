
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
import os

load_dotenv()

app = FastAPI()
uri = os.getenv("URI")

def add_image(title, image_url):
    return {
        "card": {
            "title": title,
            "imageUri": image_url
        }
    }

def get_city_as_context(city_name):
    return {"sessionInfo": {
                "parameters": {
                "City": city_name
        }
    }}

def get_fulfillment_message(text):
    return {
        "fulfillmentMessages": [
        ]
    }

def get_country(country_name):
    country_information = client.ExcursionData.Countries.find_one({"name": country_name.lower()})
    if country_information is None:
        final_response = get_fulfillment_message()
        final_response["fulfillmentMessages"].append({
            "text": {
                "text": [
                    "Oops! It seems that I don't have information about the country of your choice yet! But no worries, I will notify the developers about your interest. Thank you!"
                ]
            }
        })
        return final_response
    
    cities_list = client.ExcursionData.Cities.find({"country": ObjectId(country_information["_id"])})

    content = get_fulfillment_message()
    content["fulfillmentMessages"].append({
        "text": {
            "text": [
                country_information["description"] + "\n\n" + "Here are some of the cities in " + country_name.capitalize() + ":" + "\n" + ", ".join([city["name"].capitalize() for city in cities_list]) + "."
            ]
        },
    })
    content['fulfillmentMessages'].append(add_image(country_name.capitalize() + "'s Flag", country_information["flag"]))
    for image in country_information["highlights"]:
        content["fulfillmentMessages"].append(add_image("Highlight", image))
    return content

def get_city(cityname):
    city_information = client.ExcursionData.Cities.find_one({"name": cityname.lower()})
    if city_information is None:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Oops! It seems that I don't have information about the city of your choice yet! But no worries, I will notify the developers about your interest. Thank you!"
                        ]
                    }
                }
            ]
        }

    content =  {
        "fulfillmentMessages": [
            { 
                "text": {
                    "text": [
                        city_information["description"]
                    ]
                }
            }
        ]
    }
    for image in city_information["highlights"]:
        content["fulfillmentMessages"].append(add_image("Highlight", image))
    return content

def random_country_recommendation():
    countries = list(client.ExcursionData.Countries.aggregate([{"$sample": {"size": 1}}]))
    random_country = countries[0]
    content =  {
        "fulfillmentMessages": [
            { 
                "text": {
                    "text": [
                        "How about " + random_country["name"].capitalize() + "?",
                        "Is " + random_country["name"].capitalize() + " within your consideration?"
                    ]
                }
            },
            add_image(random_country["name"].capitalize() + "'s Flag", random_country["flag"])
        ]
    }
    return content

def random_city_recommendation(country_name):
    country_information = client.ExcursionData.Countries.find_one({"name": country_name.lower()})
    if(country_information is None):
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
    cities = list(client.ExcursionData.Cities.aggregate([
        {"$match": {"country": ObjectId(country_information["_id"])}},
        {"$sample": {"size": 1}}
    ]))
    random_city = cities[0]
    content =  {
        "fulfillmentMessages": [
            { 
                "text": {
                    "text": [
                        "How about " + random_city["name"].capitalize() + "?",
                        "Is " + random_city["name"].capitalize() + " within your consideration?"
                    ]
                }
            },
        ]
    }
    for image in random_city["highlights"]:
        content["fulfillmentMessages"].append(add_image("Highlight", image))
    return content

def get_country_plan(from_country, to_country):
    if from_country is None:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "From which city will you be departing?",
                            "Which city are you situated in right now?"
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
                        "I see that you are departing from " + from_country + ".",
                        "Alright! You are coming from " + from_country + "."
                    ]
                }
            },
            {
                "text": {
                    "text": [
                        "Do you have a specific city in mind that you would like to visit in " + to_country + "?"
                    ]
                }
            },
            {
                "text": {
                    "text": [
                        "Would you like some recommendations?"
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
    intent_display_name = data["queryResult"]["intent"]["displayName"]
    if intent_display_name == "Plan your Trip.Country":
        country_name = data["queryResult"]["parameters"]["country"]
        return get_country(country_name)
    if intent_display_name == "Plan your Trip.City":
        city_name = data["queryResult"]["parameters"]["City"]
        return get_city(city_name)
    if intent_display_name == "user.location":
        city_name = data["queryResult"]["parameters"]["City"]
        get_city_as_context(city_name)
    if intent_display_name == "unsure where":
        country_name = data['queryResult']["parameters"]["country"]
        if country_name is not None:
            return random_city_recommendation(country_name)
        return random_country_recommendation()
    return {}
        
