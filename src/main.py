
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Form
import os

load_dotenv()

app = FastAPI()
uri = os.getenv("URI")

class RequestEntity(BaseModel):
    city: str
    country: str
    place: str
    budget: int
    date: str
    adventurous: bool

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
async def get_data(city: str = Form(default=None), country: str = Form(default=None), place: str = Form(default=None), budget: bool = Form(default=None), date: str = Form(default=None), adventurous: bool = Form(default=None), airline : str = Form(default=None), to : str = Form(default=None), from_ : str = Form(default=None)):
    
    if from_ is not None:
        # User has specified a starting point for his journey
        if to is not None:
            # User has specified a destination
            if airline is not None:
                # User has specified an airline
                return {"message": "Query the data for the specified airline and return the flight details"}
            else:
                # User has not specified an airline
                return {"message": "Query the data for all possible airlines and return the flight details"}
              
    if place is not None:
        # user has a specific place he wants to go. We query the data for that place.
        # depending on the budget of the user we will try to recommend
        if budget is None:
            # USer has not specified a budget. We will return general information about the place.
            return {"message", "Information related to the place will be here"}
        else:
            if budget:
                # User has specified that he wants a place that is cheap
                # if not cheap, recommend an adventurous or not (depending on the variable) place in the same city
                return {"message": "Check if the place is cheap or not. If yes, recommend it. If not, recommend a similar place but cheaper (possibly in the same city)."}
            else:
                # User has specified that he wants a place that is expensive.
                # if expensive, recommend an adventurous or not (depending on the variable) place in the same city
                return {"message": "Check if the place is expensive or not. If yes, recommend it. If not, recommend a similar place but more expensive (possibly in the same city)."}

    if city is not None:
        # User has a specific city he wants to visit but he didn't specify a place
        if budget is None:
            # User has not specified a budget. We will return general information about the city.
            return {"message", "Information related to the city will be here"}
        else:
            if budget:
                # User has specified that he wants the city to be cheap
                # if not cheap, recommend an adventurous or not (depending on the variable) place in the same city
                return {"message": "Query all possible places in the city and return a list of cheaper ones"}
            else:
                # User has specified that he wants the city to be expensive
                # if expensive, recommend an adventurous or not (depending on the variable) place in the same city
                return {"message": "Query all possible places in the city and return a list of more expensive ones"}

    if country is not None:
        # User specify a country he wants to visit
        if budget is None:
            # User has not specified a budget. We will return general information about the country.
            return {"message": "Return general information about the country"};
        else:
            if budget:
                # User has specified that he wants the country to be cheap
                # if not cheap, recommend an adventurous or not (depending on the variable) city in the same country
                return {"message": "Query all possible cities in the country and return a list of cheaper ones"}
            else:
                # User has specified that he wants the country to be expensive
                # if expensive, recommend an adventurous or not (depending on the variable) city in the same country
                return {"message": "Query all possible cities in the country and return a list of more expensive ones"}    
   
        
