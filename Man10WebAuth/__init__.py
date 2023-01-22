import json

import pymongo
from flask import Flask
from pymongo import MongoClient
from flask_cors import CORS
from Man10WebAuth.manager.Man10WebAuthAPI import Man10WebAuthAPI
from Man10WebAuth.methods.public_methods import Man10WebAuthPublicMethods
from Man10WebAuth.methods.sub_methods import Man10WebAuthPrivateMethods


class Man10WebAuth:

    def __init__(self):
        # variables
        self.flask = Flask(__name__)
        CORS(self.flask, resources={'/*': {'origins': 'http://localhost:3000'}})
        self.running = True
        self.flask.url_map.strict_slashes = False
        self.config = {}
        # load config

        config_file = open("config.json", encoding="utf-8")
        self.config = json.loads(config_file.read())
        config_file.close()

        self.mongo = MongoClient(self.config["mongodbConnectionString"])

        # make database unique
        self.mongo["man10_web_auth"]["accounts"].create_index([("minecraftUuid", pymongo.ASCENDING)], unique=True)
        self.mongo["man10_web_auth"]["accounts"].create_index([("username", pymongo.ASCENDING)], unique=True)
        self.api = Man10WebAuthAPI(self)
        # print(self.api.register_account("Sho0", "test", "ffa9b4cb-ada1-4597-ad24-10e318f994c8"))
        # print(self.api.login("Sho0", "test"))
        # print(self.api.logout("a83b045d-9b45-48bb-b2b9-463e73a9024a"))

        self.methods_public = Man10WebAuthPublicMethods(self)
        self.methods_private = Man10WebAuthPrivateMethods(self)

        self.flask.run("0.0.0.0", self.config["hostPort"], threaded=True)
        self.running = False