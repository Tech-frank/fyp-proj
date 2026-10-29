from pymongo import MongoClient


def get_events_collection():
    client = MongoClient("mongodb://root:M0ng0Root!x7@mongo-0.cluster.local:27017/?authSource=admin")
    return client["telemetry"]["events"]
