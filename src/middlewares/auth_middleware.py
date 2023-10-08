from flask import request

def auth_middleware():
    if request.method != "GET":
        if request.headers.get("username") is None:
            return {"message": "Missing username header"}, 400