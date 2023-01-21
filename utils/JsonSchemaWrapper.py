from functools import wraps

import humps
from flask import request
from jsonschema.validators import validate


def merge_dictionaries(origin: dict, target: dict):
    for key in target.keys():
        v = target[key]
        if key not in origin:
            origin[key] = target[key]
            continue

        if type(v) != dict:
            origin[key] = target[key]
            continue
        origin[key] = merge_dictionaries(origin[key], target[key])
    return origin


def flask_json_schema(schema: dict):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if schema is None:
                return f(*args, **kwargs)
            body = request.get_json()

            try:
                validate(instance=body, schema=schema)

                variables = list(f.__code__.co_varnames)
                if "json_body" in variables:
                    kwargs["json_body"] = humps.decamelize(body)

                if "raw_json_body" in variables:
                    kwargs["raw_json_body"] = body
            except Exception as e:
                print(e)
                return "post_body_invalid"
            return f(*args, **kwargs)

        return wrapped

    return decorator
