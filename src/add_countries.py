import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from fastapi import FastAPI
import csv

load_dotenv()

countries = []
with open('countryinfo.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        countries.append((row[0], row[1]))

uri = os.getenv("URI")
client = MongoClient(uri, server_api=ServerApi('1'))

for country in countries:
    client.ExcursionData.Countries.insert_one({"country": country[0].lower(), "gdppc": int(country[1])})