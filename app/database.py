from flask import Flask
from pymongo import MongoClient


def init(app: Flask) -> MongoClient:
    user = app.config['MONGO_USER']
    password = app.config['MONGO_PASSWORD']
    host = app.config['MONGO_HOST']
    port = app.config['MONGO_PORT']
    uri = (f'mongodb://{user}:{password}@{host}:{port}/?authSource=admin')

    return MongoClient(uri, tz_aware=True)
