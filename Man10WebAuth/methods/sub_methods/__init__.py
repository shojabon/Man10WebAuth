from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

from Man10WebAuth.methods.sub_methods.RegisterAccountMethod import RegisterAccountMethod
from Man10WebAuth.methods.sub_methods.UpdateInformationMethod import UpdateInformationMethod

if TYPE_CHECKING:
    from Man10WebAuth import Man10WebAuth


class Man10WebAuthPrivateMethods:

    def __init__(self, main: Man10WebAuth):
        self.main = main
        self.blueprint = Blueprint('auth_private', __name__, url_prefix="/private")

        RegisterAccountMethod(self)
        UpdateInformationMethod(self)

        self.main.flask.register_blueprint(self.blueprint)
