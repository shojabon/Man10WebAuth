from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

from flask import Blueprint

from Man10WebAuth.methods.shop.sub_methods.LoginAccountMethod import LoginAccountMethod
from Man10WebAuth.methods.shop.sub_methods.RegisterAccountMethod import RegisterAccountMethod

if TYPE_CHECKING:
    from Man10WebAuth import Man10WebAuth


class Man10WebAuthMethods:

    def __init__(self, main: Man10WebAuth):
        self.main = main
        self.blueprint = Blueprint('auth', __name__, url_prefix="")

        LoginAccountMethod(self)
        RegisterAccountMethod(self)

        self.main.flask.register_blueprint(self.blueprint)
