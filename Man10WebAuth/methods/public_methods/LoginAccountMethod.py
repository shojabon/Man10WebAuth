from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10WebAuth.methods import Man10WebAuthMethods


class LoginAccountMethod:

    def __init__(self, methods: Man10WebAuthMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "minecraftUsername": {
                    "type": "string"
                },
                "password": {
                    "type": "string"
                }
            },
            "required": ["minecraftUsername", "password"]
        }

        self.register_endpoint()

    def register_endpoint(self):

        @self.methods.blueprint.route("/login", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def login(json_body: dict):
            try:
                result = self.methods.main.api.login(json_body["minecraft_username"], json_body["password"])
                if result[1] is None:
                    return result[0]
                return "success", result[1]
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
