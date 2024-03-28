import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import csv

load_dotenv()

# Assuming the csv file is in the same directory as the script
csv_file = "cities_info.txt"

# Connect to MongoDB
client = MongoClient(os.getenv("URI"))

# Access the database
db = client["ExcursionData"]

# Access the collection
collection = db["Budget"]

# Read the csv file
with open(csv_file, "r") as file:
    reader = csv.reader(file)
    for row in reader:
        # Insert each row into the collection
        # Get the ObjectId from another collection
        another_collection = db["Cities"]
        document = another_collection.find_one({"name": row[0].lower()})

        if document is None:
            print("cannot find city : " + row[0])
            continue

        object_id = document["_id"]

        existing_document = collection.find_one({"city": object_id})
        if existing_document is not None:
            print("Collection with city parameter already exists for city: " + row[0])
            continue

        if object_id is None:
            print("cannot find city : " + row[0])
            continue
        # Insert each row into the collection
        collection.insert_one({
            "city": object_id,
            "low": int(row[1]),
            "high": int(row[2])
        })