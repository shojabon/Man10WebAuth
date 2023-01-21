import glob
import json
import os
from functools import wraps

import humps
from flask import request, Response

error_codes = {}
for path in glob.glob("error_codes/*.json"):
    code_name = os.path.basename(path)[:-5]
    file = open(path, "r", encoding="utf-8")
    error_codes[code_name] = json.loads(file.read())
    file.close()
def get_error_message(error_code: str, language: str = "jp"):
    result = "不明なエラーが発生しました"
    if error_code in error_codes:
        status_data = error_codes[error_code]
    else:
        status_data = error_codes["unknown_response"]
    if "message" in status_data:
        if language in status_data["message"]:
            result = status_data["message"][language]
        else:
            result = status_data["message"]["en"]
    return result


def convert_response_to_json_response(response: dict, language: str = "en"):
    if type(response) == str:
        response = (response, [])

    result = {}
    status_name = response[0]
    data = response[1]
    result["data"] = data
    result["status"] = status_name

    if status_name in error_codes:
        status_data = error_codes[status_name]
    else:
        status_data = error_codes["unknown_response"]

    status_code = 206
    if "code" in status_data:
        status_code = status_data["code"]
    if "message" in status_data:
        if language in status_data["message"]:
            result["message"] = status_data["message"][language]
        else:
            result["message"] = status_data["message"]["en"]

    result = humps.camelize(result)
    return result, status_code


def flask_mat_response_wrapper():
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)
            print(response)

            user_defined_language = request.args.get('lang')
            if user_defined_language is None:
                user_defined_language = "jp"

            result = convert_response_to_json_response(response, user_defined_language)
            return Response(response=json.dumps(result[0], ensure_ascii=False), status=result[1])

        return wrapped

    return decorator
