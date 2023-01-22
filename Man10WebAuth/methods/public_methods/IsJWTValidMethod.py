from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10WebAuth.methods import Man10WebAuthMethods


class IsJWTValidMethod:

    def __init__(self, methods: Man10WebAuthMethods):
        self.methods = methods

        self.register_endpoint()

    def register_endpoint(self):

        @self.methods.blueprint.route("/info", methods=["GET"])
        @flask_mat_response_wrapper()
        def info():
            return "success"
