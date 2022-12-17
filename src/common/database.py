from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")

# check databases
# databases = cliente.database_names()
# collections = database.collection_names()

database = mongo_client["uspolis"]
