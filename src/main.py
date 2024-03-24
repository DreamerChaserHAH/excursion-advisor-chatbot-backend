
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

def is_intent_the_same(intent_name_in_request, intent_name):
    return intent_name_in_request == "z."+ intent_name

def from_city_empty_response(session_string):
    content = get_fulfillment_message()
    content["fulfillmentMessages"].append({
        "text": {
            "text": [
                 "From which city will you be departing?",
                "Which city are you situated in right now?"
            ]
        }
    })
    content.append({
        "outputContexts": [
            {
                "name": session_string + "/contexts/from-city-setting",
                "lifespanCount": 1
            }
        ]
    })
    return content
def no_city_in_database_response():
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Oops! It seems that 𝗪𝗮𝗻𝗱𝗲𝗿 doesn't have information about the city of your choice yet! But no worries, 𝗪𝗮𝗻𝗱𝗲𝗿 will notify the developers about your interest. Sank kyu!"
                    ]
                }
            }
        ]
    }
def no_country_in_database_response():
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Oops! It seems that 𝗪𝗮𝗻𝗱𝗲𝗿 doesn't have information about the country of your choice yet! But no worries, 𝗪𝗮𝗻𝗱𝗲𝗿 will notify the developers about your interest. Sank kyu!"
                    ]
                }
            }
        ]
    }

def add_image(title, image_url):
    return {
        "card": {
            "title": title,
            "imageUri": image_url
        }
    }

def get_city_as_context(city_name, session):
    return {
        "outputContexts": [
            {
                "name":  session + "/contexts/from-city",
                "lifespanCount": 9999,
                "parameters": {
                    "name": city_name
                }
            }
        ]
    }

def get_fulfillment_message():
    return {
        "fulfillmentMessages": [
        ]
    }

def get_country(country_name):
    country_information = client.ExcursionData.Countries.find_one({"name": country_name.lower()})
    if country_information is None:
        no_country_in_database_response()
    
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

def get_city(city_name):
    city_information = client.ExcursionData.Cities.find_one({"name": city_name.lower()})
    if city_information is None:
        return no_city_in_database_response()

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

def get_country_trip_plan(from_city, to_country, session_string):
    
    country_information = client.ExcursionData.Countries.find_one({"name": to_country.lower()})
    if country_information is None:
        return no_country_in_database_response()
    
    if from_city is None:
        return from_city_empty_response(session_string)
    
    cities_list = client.ExcursionData.Cities.find({"country": ObjectId(country_information["_id"])})
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "I see that you are departing from " + from_city + ".",
                        "Alright! You are coming from " + from_city + "."
                    ]
                }
            },
            {
                "text": {
                    "text": [
                        "Do you have a specific city in mind that you would like to visit in " + to_country + "?\n𝗪𝗮𝗻𝗱𝗲𝗿 have information on multiple cities :\n " + ",\n ".join([city["name"].capitalize() for city in cities_list])
                    ]
                }
            },
            {
                "text": {
                    "text": [
                        "Or, tell me if you want some random recommendations from "+ to_country + "?"
                    ]
                }
            }
        ],
        "outputContexts": [
                {
                    "name": session_string + "/contexts/to-city-setting",
                    "lifespanCount": 1,
                },
                {
                    "name": session_string + "/contexts/to-country",
                    "lifespanCount": 9999,
                    "parameters": {
                        "to-country": to_country
                    }
                }
            ]
    }

def get_city_trip_plan(from_city, to_city, session_string):
    city_information = client.ExcursionData.Cities.find_one({"name": to_city.lower()})
    
    if city_information is None:
        return no_city_in_database_response()
    
    if from_city is None:
        return from_city_empty_response()
    
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "I see that you are departing from " + from_city + ".",
                        "Alright! You are coming from " + from_city + "."
                    ]
                }
            },
            {
                "text": {
                    "text": [
                        "Do you have a specific city in mind that you would like to visit in " + to_city + "?"
                    ]
                }
            }
        ],
        "outputContexts": [
                {
                    "name": session_string + "/contexts/to-city-setting",
                    "lifespanCount": 1,
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
    intent_display_name = data["queryResult"]["intent"]["displayName"]

    if is_intent_the_same(intent_display_name, "vague.city-livingthere"):
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("vague-city")):
                city_name = context["parameters"]["city"]
                return get_city_as_context(city_name, data["session"])
    
    elif is_intent_the_same(intent_display_name, "vague.city-gothere"):
        return {}
    
    if is_intent_the_same(intent_display_name, "planning.country"):
        from_city_name = None
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("from-city")):
                from_city_name = context["parameters"].get["from-city"]

        to_country_name = data["queryResult"]["parameters"].get["to-country"]
        return get_country_trip_plan(from_city_name, to_country_name, data["session"]) 
    
    elif is_intent_the_same(intent_display_name, "planning.city"):
        from_city_name = None
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("from-city")):
                from_city_name = context["parameters"].get["from-city"]

        to_city_name = data["queryResult"]["parameters"].get["to-city"]
        return get_city_trip_plan(from_city_name, to_city_name, data["session"])
    
    elif is_intent_the_same(intent_display_name,"random.recommendation"):
        to_country_name = None
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("to-country")):
                to_country_name = context["parameters"]["to-country"]

        if to_country_name is not None:
            return random_city_recommendation(to_country_name)
        else:
            return random_country_recommendation()
        
    elif is_intent_the_same(intent_display_name,"explain.about") :
        country_name = data["queryResult"]["parameters"].get("Country")
        if country_name:
            return get_country(country_name)
        city_name = data["queryResult"]["parameters"].get("City")
        if city_name:
            return get_city(city_name)
    return {}
        
