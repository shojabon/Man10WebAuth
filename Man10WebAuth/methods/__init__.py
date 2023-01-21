from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

from Man10WebAuth.methods.sub_methods.LoginAccountMethod import LoginAccountMethod
from Man10WebAuth.methods.sub_methods.RegisterAccountMethod import RegisterAccountMethod
from Man10WebAuth.methods.sub_methods.UpdateInformationMethod import UpdateInformationMethod

if TYPE_CHECKING:
    from Man10WebAuth import Man10WebAuth


class Man10WebAuthMethods:

    def __init__(self, main: Man10WebAuth):
        self.main = main
        self.blueprint = Blueprint('auth', __name__)

        LoginAccountMethod(self)
        RegisterAccountMethod(self)
        UpdateInformationMethod(self)

        self.main.flask.register_blueprint(self.blueprint)
