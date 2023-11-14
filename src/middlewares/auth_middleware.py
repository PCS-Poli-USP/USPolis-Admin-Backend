from flask import request
import boto3

client = boto3.client("cognito-idp")

def auth_middleware():
    try:
        if request.method != 'OPTIONS':
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