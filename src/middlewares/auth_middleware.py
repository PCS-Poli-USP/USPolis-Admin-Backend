from flask import request
import boto3
import os


def auth_middleware():
    client = boto3.client(
        "cognito-idp",
        region_name=os.environ.get("AWS_REGION"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )
    try:
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
