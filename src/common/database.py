import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

uri = os.environ.get("CONN_STR")
db_name = os.environ.get("DB_NAME") or "uspolis"
mongo_client = MongoClient(uri, 27017)

database = mongo_client[db_name]
