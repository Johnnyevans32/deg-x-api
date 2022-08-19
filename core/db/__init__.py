import certifi
from pymongo import MongoClient

from core.config import settings

db_name = settings.DATABASE["NAME"]
uri = settings.DATABASE["URI"]

client: MongoClient = MongoClient(uri, tlsCAFile=certifi.where())
db = client[db_name]
