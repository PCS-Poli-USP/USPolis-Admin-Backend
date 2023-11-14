import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

uri = os.environ.get("CONN_STR")
mongo_client = MongoClient(uri, 27017)

# check databases
# databases = cliente.database_names()
# collections = database.collection_names()

database = mongo_client["uspolis"]
