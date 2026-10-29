import os

from pymongo import MongoClient


def get_events_collection():
    client = MongoClient(os.environ["TELEMETRY_MONGO_URI"])
    return client["telemetry"]["events"]
