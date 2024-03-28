
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

def from_city_empty_response(session_string, context):
    content = get_fulfillment_message()
    content["fulfillmentMessages"].append({
        "text": {
            "text": [
                 "From which city will you be departing?",
                "Which city are you situated in right now?"
            ]
        }
    })
    content["outputContexts"] = []
    content["outputContexts"].append(
        {
            "name": session_string + "/contexts/from-city-setting",
            "lifespanCount": 1,
            "parameters": {
                "coming-from": context
            }
        }
    )
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
def whatiknow():
    countries = client.ExcursionData.Countries.find({}, {"name": 1})
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "However, here is a list of countries 𝗪𝗮𝗻𝗱𝗲𝗿 know at this particular moment:\n" + ",\n ".join([country["name"].capitalize() for country in countries]) + ".",
                    ]
                }
            }
        ]
    }

def no_country_in_database_response():
    countries = client.ExcursionData.Countries.find({}, {"name": 1})
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Oops! It seems that 𝗪𝗮𝗻𝗱𝗲𝗿 doesn't have information about the country of your choice yet! But no worries, 𝗪𝗮𝗻𝗱𝗲𝗿 will notify the developers about your interest~"
                    ]
                }
            },
            {
                "text": {
                    "text": [
                        "However, here is a list of countries 𝗪𝗮𝗻𝗱𝗲𝗿 know at this particular moment:\n" + ",\n ".join([country["name"].capitalize() for country in countries]) + ".",
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

def from_city_as_context(city_name, session):
    return {
        "outputContexts": [
            {
                "name":  session + "/contexts/from-city",
                "lifespanCount": 9999,
                "parameters": {
                    "from-city": city_name
                }
            }
        ]
    }
def to_city_as_context(city_name, session):
    return {
        "outputContexts": [
            {
                "name":  session + "/contexts/to-city",
                "lifespanCount": 9999,
                "parameters": {
                    "to-city": city_name
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
        return no_country_in_database_response()
    
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
def random_country_recommendation(session_string):
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
                },
            },
            add_image(random_country["name"].capitalize() + "'s Flag", random_country["flag"]),
            {
                "text": {
                    "text": [
                        "Do you want to me to tell you what I know about it?"
                    ]
                }
            }
        ],
        "outputContexts": [
            {
                "name": session_string + "/contexts/random-country-recommendation",
                "lifespanCount": 1,
                "parameters": {
                    "country": random_country["name"]
                }
            }
        ]
    }
    return content
def random_city_recommendation(country_name, session_string):
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
                },
            },
            {
                "text": {
                    "text": [
                        "Do you want to me to tell you what I know about it?"
                    ]
                }
            }
        ],
        "outputContexts": [
            {
                "name": session_string + "/contexts/random-city-recommendation",
                "lifespanCount": 1,
                "parameters": {
                    "city": random_city["name"]
                }
            }
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
        return from_city_empty_response(session_string, "country-trip-plan")
    
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
def get_city_trip_plan(from_city, to_city, activity_type, budget, session_string):
    city_information = client.ExcursionData.Cities.find_one({"name": to_city.lower()})
    if city_information is None:
        return no_city_in_database_response()   
    if from_city is None:
        content = from_city_empty_response(session_string, "city-trip-plan")
        content["outputContexts"].append(
            {
                "name": session_string + "/contexts/to-city",
                "lifespanCount": 9999,
                "parameters": {
                    "to-city": to_city
                }
            }
        )
        return content
    if activity_type is None:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "What kind of activities are you interested in near " + to_city + "?\nMy creators have created 2 categories of activities: 𝗔𝗱𝘃𝗲𝗻𝘁𝘂𝗿𝗲𝘀 and Sightseeing.",
                        ]
                    }
                }
            ],
            "outputContexts": [
                {
                    "name": session_string + "/contexts/activities-setting",
                    "lifespanCount": 1,
                },
                {
                    "name": session_string + "/contexts/to-city",
                    "lifespanCount": 9999,
                    "parameters": {
                        "to-city": to_city
                    }
                }
            ]
        }
    if budget is None:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "What is your budget for the trip to " + to_city + "?",
                            "How much are you planning to spend for your trip to " + to_city + "?"
                        ]
                    }
                }
            ],
            "outputContexts": [
                {
                    "name": session_string + "/contexts/budget-setting",
                    "lifespanCount": 1,
                },
                {
                    "name": session_string + "/contexts/to-city",
                    "lifespanCount": 9999,
                    "parameters": {
                        "to-city": to_city,
                        "activity-type": activity_type
                    }
                }
            ]
        }

    
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "I see that you are departing from " + from_city + ".",
                        "Alright! You are coming from " + from_city + "."
                    ]
                }
            }
        ],
        "BudgetEvent": {
            "name": "RandomRecommendations",
            "parameters": {
                "City": to_city,
                "Budget": budget
            }
        },
        "outputContexts": [
                {
                    "name": session_string + "/contexts/to-city",
                    "lifespanCount": 9999,
                    "parameters": {
                        "to-city": to_city
                    }
                },
                {
                    "name": session_string + "/contexts/budget",
                    "lifespanCount": 9999,
                    "parameters": {
                        "budget": budget
                    }
                }
            ]
    }
def get_country_budget_information():
    content = get_fulfillment_message()
    content["fulfillmentMessages"].append({
        "text": {
            "text": [
                "At this particular momemt, 𝗪𝗮𝗻𝗱𝗲𝗿 have no information about specific budget range in specific countries"
            ]
        }
    })
    content["fulfillmentMessages"].append({
        "text": {
            "text": [
                "However, 𝗪𝗮𝗻𝗱𝗲𝗿 can provide budget information about specific cities in specific countries however"
            ]
        }
    })
    return content
def get_city_budget_information(city, nights, budget):
    city_information = client.ExcursionData.Cities.find_one({"name": city.lower()})
    if city_information is None:
        return no_city_in_database_response()
    budget_information = client.ExcursionData.Budget.find_one({"city": ObjectId(city_information["_id"])})
    if budget_information is None:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "At this particular momemt, 𝗪𝗮𝗻𝗱𝗲𝗿 have no information about specific budget range in " + city.capitalize()
                        ]
                    }
                }
            ]
        }
    
    number_of_nights = nights if nights else 1
    if budget is not None and budget != "":
        if int(budget) < int(number_of_nights) * budget_information["low"]:
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "The budget range for a trip to " + city.capitalize() + " is between $" + str(int(number_of_nights) * budget_information["low"]) + " and $" + str(int(number_of_nights) * budget_information["high"]) + " for " + str(number_of_nights) + " nights.",
                                "It seems that your budget is too low for a trip to " + city.capitalize() + "."
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
                    "The budget range for a trip to " + city.capitalize() + " is between $" + str(int(number_of_nights) * budget_information["low"]) + " and $" + str(int(number_of_nights) * budget_information["high"]) + " for " + str(number_of_nights) + " nights."
                ]
            }
        },
        {
            "text":{
                "text":[
                    "Anything else?"
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
 
def get_city_trip_plan_process(data):
    from_city_name = None
    activity_type = None
    budget = None
    to_city_name = data["queryResult"]["parameters"].get("to-city")

    for context in data["queryResult"]["outputContexts"]:
        if(context["name"].endswith("from-city")):
            from_city_name = context["parameters"].get("from-city")
        if(context["name"].endswith("activity")):
            activity_type = context["parameters"].get("activity-type")
        if(context["name"].endswith("budget")):
            budget = context["parameters"].get("budget")
        if(context["name"].endswith("to-city")) and to_city_name is None:
            to_city_name = context["parameters"].get("to-city")

    return get_city_trip_plan(from_city_name, to_city_name, activity_type, budget, data["session"])
def get_country_trip_plan_process(data):
    from_city_name = None
    to_country_name = data["queryResult"]["parameters"].get("to-country")

    for context in data["queryResult"]["outputContexts"]:
        if(context["name"].endswith("from-city")):
            from_city_name = context["parameters"].get("from-city")
        if(context["name"].endswith("to-country")) and to_country_name is None:
            to_country_name = context["parameters"].get("to-country")
    return get_country_trip_plan(from_city_name, to_country_name, data["session"])    

client = MongoClient(uri, server_api=ServerApi('1'))

def travelsafety_process(data):
    country_name = data["queryResult"]["parameters"].get("Country")
    if country_name is None:
        for context in data["queryResult"]["outputContexts"]:
            if context["name"].endswith("random-country-recommendation"):
                country_name = context["parameters"].get("country")
    if country_name is None:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "I'm sorry, I can't find the country you are looking for. Please try again."
                        ]
                    }
                }
            ]
        }
    country_information = client.ExcursionData.Countries.find_one({"name": country_name.lower()})
    if country_information is None:
        return
    if country_information.get("safetydescription") is None:
        return
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Here is the travel safety information for \n'" + country_name.capitalize() + ":\n" + country_information.get("safetydescription") + "'"
                    ]
                }
            }
        ]
    }

def get_budget_range_process(data):
    city = data["queryResult"]["parameters"].get("City")
    budget = data["queryResult"]["parameters"].get("Budget")
    nights = data["queryResult"]["parameters"].get("Nights")
    if city is not None:
        return get_city_budget_information(city, nights, budget)
    return get_country_budget_information()

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

    if is_intent_the_same(intent_display_name, "city.from.settings.yes") or is_intent_the_same(intent_display_name, "vague.gothere.yes") or is_intent_the_same(intent_display_name, "country.from.yes") or is_intent_the_same(intent_display_name, "city.from.settings.yes") or is_intent_the_same(intent_display_name, "random.recommendation.no") or is_intent_the_same(intent_display_name, "city.from.default.yes") :
       return {
            "followupEventInput": {
                "name": "RandomRecommendations"
            }
        }
    elif is_intent_the_same(intent_display_name, "vague.city-livingthere"):
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("vague-city")):
                city_name = context["parameters"]["city"]
                return from_city_as_context(city_name, data["session"])    
    elif is_intent_the_same(intent_display_name, "vague.city.go.there"):
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("vague-city")):
                city_name = context["parameters"]["city"]  
                data["queryResult"]["outputContexts"].append(
                    {
                        "name": data["session"] + "/contexts/to-city",
                        "lifespanCount": 1,
                        "parameters": {
                    "to-city": city_name
                        }
                    }
                )
                return get_city_trip_plan_process(data) 
    elif is_intent_the_same(intent_display_name, "planning.country"):
        return get_country_trip_plan_process(data)
        return get_city_trip_plan_process(data)    
    elif is_intent_the_same(intent_display_name,"random.recommendation"):
        to_country_name = None
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("to-country")):
                to_country_name = context["parameters"].get("to-country")

        if to_country_name is not None:
            return random_city_recommendation(to_country_name, data["session"])
        else:
            return random_country_recommendation(data["session"])   
    elif is_intent_the_same(intent_display_name,"explain.about") or is_intent_the_same(intent_display_name, "random.recommendation.yes") :
        country_name = data["queryResult"]["parameters"].get("Country")
        if country_name is None:
            for context in data["queryResult"]["outputContexts"]:
                if context["name"].endswith("random-country-recommendation"):
                    country_name = context["parameters"].get("country")

        if country_name:
            return get_country(country_name)
        city_name = data["queryResult"]["parameters"].get("City")
        for context in data["queryResult"]["outputContexts"]:
            if context["name"].endswith("random-city-recommendation"):
                city_name = context["parameters"].get("city")
        if city_name:
            return get_city(city_name)
    elif is_intent_the_same(intent_display_name,"vague.country.yes"):
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("vague-country")):
                country_name = context["parameters"]["country"]
                return get_country(country_name)
    elif is_intent_the_same(intent_display_name,"vague.city.yes"):
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("vague-city")):
                city_name = context["parameters"]["city"]
                return get_city(city_name)           
    elif is_intent_the_same(intent_display_name,"city.from.settings"):
        for context in data["queryResult"]["outputContexts"]:
            if(context["name"].endswith("from-city-setting")):
                coming_from = context["parameters"].get("coming-from")
        if coming_from == "city-trip-plan":
            return get_city_trip_plan_process(data)
        if coming_from == "country-trip-plan":
            return get_country_trip_plan_process(data)
    elif is_intent_the_same(intent_display_name,"budget.setting") or is_intent_the_same(intent_display_name, "city.to.settings") or is_intent_the_same(intent_display_name,"activities.setting") or is_intent_the_same(intent_display_name, "planning.city") or is_intent_the_same(intent_display_name, "planning.country.specificcity"):
        return get_city_trip_plan_process(data)
    elif is_intent_the_same(intent_display_name,"whatyouknow"):
        return whatiknow()
    elif is_intent_the_same(intent_display_name, "travel.safety"):
        return travelsafety_process(data)
    elif is_intent_the_same(intent_display_name, "budget.range"):
        return get_budget_range_process(data)
    return {}
        
