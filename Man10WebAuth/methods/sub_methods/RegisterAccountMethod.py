from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Optional

from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10WebAuth.methods.sub_methods import Man10WebAuthPrivateMethods

class RegisterAccountMethod:

    def __init__(self, methods: Man10WebAuthPrivateMethods):
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
        @self.methods.blueprint.route("/register", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def register_account(json_body: dict):
            try:
                result = self.methods.main.api.register_account(json_body["minecraft_username"], json_body["password"])
                if not result[1]:
                    return result[0]
                return "success"
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
