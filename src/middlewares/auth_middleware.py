from flask import request
import boto3


def auth_middleware():
    client = boto3.client("cognito-idp")
    try:
        authorization = request.headers.get("Authorization")
        token = authorization.split(" ")[1]
        if token is None:
            return {"message": "Missing authorization header"}, 400

        response = client.get_user(
            AccessToken=token
        )

        request.user = response
    
    except Exception as e:
        return {"message": "Invalid token"}, 400

    finally:
        client.close()