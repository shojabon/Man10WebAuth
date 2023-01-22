from __future__ import annotations

import datetime
import json
import traceback
import uuid
from typing import TYPE_CHECKING, Optional

import humps
import jwt
import requests
from pymongo.errors import DuplicateKeyError

if TYPE_CHECKING:
    from Man10WebAuth import Man10WebAuth


class Man10WebAuthAPI:

    def __init__(self, main: Man10WebAuth):
        self.main = main

    def get_minecraft_player(self, mcid: str):
        cache = self.main.mongo["man10_web_auth"]["mcid_uuid"].find_one({"name": mcid})
        if cache is not None:
            if datetime.datetime.now().timestamp() - cache["requestTime"].timestamp() < self.main.config["mojangAPICacheTTL"]:
                del cache["_id"]
                if cache["id"] is None:
                    return None
                return cache

        username_request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + str(mcid))
        if username_request.status_code != 200:
            no_data = {"name": mcid, "uuid": None, "requestTime": datetime.datetime.now()}
            self.main.mongo["man10_web_auth"]["mcid_uuid"].insert_one(no_data)
            return None
        username_request = json.loads(username_request.text)
        username_request["requestTime"] = datetime.datetime.now()
        username_request["id"] = str(uuid.UUID(hex=username_request["id"]))
        self.main.mongo["man10_web_auth"]["mcid_uuid"].update_one({"id": username_request["id"]}, {"$set": username_request})
        return username_request

    def http_request(self, path: str, method: str = "POST", payload: dict = None,
                     return_json: bool = True):
        try:
            req = {}
            if method == "GET":
                req = requests.get(self.main.config["kongEndpoint"] + path,
                                   data=payload)
            if method == "POST":
                req = requests.post(self.main.config["kongEndpoint"] + path,
                                    data=payload)
            if method == "DELETE":
                req = requests.delete(self.main.config["kongEndpoint"] + path,
                                    data=payload)
            if req.text == "":
                return None

            if return_json:
                return json.loads(req.text)
            else:
                return req.text
        except Exception as e:
            traceback.print_exc()
            return None

    def get_user_object(self, minecraft_uuid: str=None, username: str=None, kong_id: str=None):
        try:
            query = {}
            if minecraft_uuid is not None:
                query["minecraftUUID"] = minecraft_uuid
            if username is not None:
                query["username"] = username
            if kong_id is not None:
                query["kongId"] = kong_id
            user_object = self.main.mongo["man10_web_auth"]["accounts"].find_one(query)
            return "success", user_object
        except Exception:
            return "error_internal", None

    def register_account(self, username: str, password: str):
        try:

            minecraft_user_data = self.get_minecraft_player(username)
            if minecraft_user_data is None:
                return "minecraft_account_invalid", False

            minecraft_uuid = minecraft_user_data["id"]

            self.main.mongo["man10_web_auth"]["accounts"].update_one({
                "minecraftUUID": minecraft_uuid
            }, {
                "$set": {
                    "username": username,
                    "password": password
                }
            }, upsert=True)

            request_data = self.http_request("/consumers", "POST", {
                "custom_id": minecraft_uuid,
                "username": minecraft_uuid
            })
            if request_data is None:
                return "kong_consumer_exists", False
            if "id" not in request_data:
                return "kong_consumer_exists", False
            kong_id = request_data["id"]

            self.main.mongo["man10_web_auth"]["accounts"].update_one({
                "minecraftUUID": minecraft_uuid
            }, {
                "$set": {
                    "kongId": kong_id
                }
            }, upsert=True)

            result = self.http_request("/consumers/" + request_data["id"] + "/acls", "POST", {
                "group": "Guest"
            })
            if "code" in result:
                return "kong_consumer_group_error", False
            return "success", True
        except DuplicateKeyError:
            traceback.print_exc()
            return "account_exists", False
        except Exception:
            traceback.print_exc()
            return "error_internal", False

    def login(self, name: str, password: str):
        try:
            minecraft_player = self.get_minecraft_player(name)
            if minecraft_player is None:
                return "minecraft_account_invalid", None
            print({
                "minecraftUUID": minecraft_player["id"],
                "password": password
            })
            result = self.main.mongo["man10_web_auth"]["accounts"].find_one({
                "minecraftUUID": minecraft_player["id"],
                "password": password
            })
            if result is None:
                return "account_invalid", None

            jwt_request: dict = self.http_request("/consumers/" + result["kongId"] + "/jwt", "POST", {})
            jwt_token = jwt.encode({
                "iss": jwt_request["key"],
                "minecraftUUID": result["minecraftUUID"],
                "exp": round(datetime.datetime.now().timestamp() + self.main.config["jwtExpiration"])
            }, jwt_request["secret"])
            return "success", jwt_token
        except Exception:
            traceback.print_exc()
            return "error_internal",None

    def logout(self, minecraft_uuid: str):
        try:
            request_result, user_data = self.get_user_object(minecraft_uuid=minecraft_uuid)
            if user_data is None:
                return request_result, False
            tokens: dict = self.http_request("/consumers/" + str(user_data["kongId"]) + "/jwt", "GET", {})
            if tokens is None:
                return "account_invalid", False
            tokens = [x["id"] for x in tokens["data"]]
            for token in tokens:
                self.http_request("/consumers/" + user_data["kongId"] + "/jwt/" + token, "DELETE", {})
            return "success", True
        except Exception:
            traceback.print_exc()
            return "error_internal",False

    def update_information(self, minecraft_uuid: str, data: dict):
        try:
            request_status, user_object = self.get_user_object(minecraft_uuid)
            if user_object is None:
                return "account_invalid", False
            self.main.mongo["man10_web_auth"]["accounts"].update_one({"minecraftUUID": minecraft_uuid}, {"$set": data})
            return "success", True
        except DuplicateKeyError:
            traceback.print_exc()
            return "account_exists", False
        except Exception:
            traceback.print_exc()
            return "error_internal", False