import os

import boto3
from flask import request

from src.repository.user_repository import UserRepository

client = boto3.client(
    "cognito-idp",
    region_name=os.environ.get("AWS_REGION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)


def auth_middleware():
    try:
        if request.method != "OPTIONS":
            authorization = request.headers.get("Authorization")
            token = authorization.split(" ")[1]
            if token is None:
                return {"message": "Missing authorization header"}, 400

            response = client.get_user(AccessToken=token)
            request.user = response

    except Exception as e:
        return {"message": "Invalid token"}, 400

    finally:
        client.close()


def admin_middleware():
    if request.method != "OPTIONS":
        user_repository = UserRepository()

        auth_middleware_response = auth_middleware()

        if auth_middleware_response is not None:
            return auth_middleware_response

        if not user_repository.is_admin(request.user["Username"]):
            return {"message": "Unauthorized"}, 401
