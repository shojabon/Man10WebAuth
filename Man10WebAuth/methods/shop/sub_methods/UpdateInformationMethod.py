from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Optional

from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10WebAuth.methods.shop import Man10WebAuthMethods


class UpdateInformationMethod:

    def __init__(self, methods: Man10WebAuthMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "minecraftUuid": {
                    "type": "string"
                },
                "data": {
                    "type": "object"
                }
            },
            "required": ["minecraftUuid", "data"]
        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("update", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def update_info(json_body: dict):
            try:
                result = self.methods.main.api.update_information(json_body["minecraft_uuid"], json_body["data"])
                if result[1] is None:
                    return result[0]
                return "success", result[1]
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
