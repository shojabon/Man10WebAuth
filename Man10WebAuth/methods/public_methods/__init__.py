from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

from Man10WebAuth.methods.public_methods.LoginAccountMethod import LoginAccountMethod

if TYPE_CHECKING:
    from Man10WebAuth import Man10WebAuth


class Man10WebAuthPublicMethods:

    def __init__(self, main: Man10WebAuth):
        self.main = main
        self.blueprint = Blueprint('auth_public', __name__,url_prefix="/public")

        LoginAccountMethod(self)

        self.main.flask.register_blueprint(self.blueprint)
