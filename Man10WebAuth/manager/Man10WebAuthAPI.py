from __future__ import annotations

import json
import traceback
import uuid
from typing import TYPE_CHECKING, Optional

import humps
import jwt
import requests

if TYPE_CHECKING:
    from Man10WebAuth import Man10WebAuth


class Man10WebAuthAPI:

    def __init__(self, main: Man10WebAuth):
        self.main = main

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

    def register_account(self, username: str, password: str, account_uuid: str):
        try:
            result: dict = self.http_request("/consumers", "POST", {
                "custom_id": account_uuid,
                "username": account_uuid
            })
            if "id" not in result:
                return "kong_consumer_exists", False
            kong_id = result["id"]

            update_result = self.main.mongo["man10_web_auth"]["accounts"].update_one({
                "minecraftUuid": account_uuid
            }, {
                "$set": {
                    "username": username,
                    "password": password,
                    "kongId": kong_id
                }
            }, upsert=True)

            result = self.http_request("/consumers/" + result["id"] + "/acls", "POST", {
                "group": "Guest"
            })
            if "code" in result:
                return "kong_consumer_group_error", False
            return "success", True
        except Exception:
            traceback.print_exc()
            return "error_internal", False

    def login(self, name: str, password: str):
        try:
            result = self.main.mongo["man10_web_auth"]["accounts"].find_one({
                "username": name,
                "password": password
            })
            if result is None:
                return "account_invalid", None

            jwt_request: dict = self.http_request("/consumers/" + result["kongId"] + "/jwt", "POST", {})
            jwt_token = jwt.encode({
                "iss": jwt_request["key"],
                "minecraftUuid": result["minecraftUuid"]
            }, jwt_request["secret"])
            return "success", jwt_token
        except Exception:
            traceback.print_exc()
            return "error_internal",None

    def logout(self, kong_uuid: str):
        try:
            tokens = self.http_request("/consumers/" + kong_uuid + "/jwt", "GET", {})
            if tokens is None:
                return "account_invalid", False
            tokens = [x["id"] for x in tokens["data"]]
            for token in tokens:
                self.http_request("/consumers/" + kong_uuid + "/jwt/" + token, "DELETE", {})
            return "success", True
        except Exception:
            traceback.print_exc()
            return "error_internal",False

    def update_information(self, minecraft_uuid: str, data: dict):
        try:
            self.main.mongo["man10_web_auth"]["accounts"].update_one({"minecraftUuid": minecraft_uuid}, {"$set": data})
            return "success", True
        except Exception:
            traceback.print_exc()
            return "error_internal", False