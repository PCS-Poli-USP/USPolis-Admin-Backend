import boto3
import os

UserExistsException = type("CustomUserExistsException", (Exception,), {})


def cognito_create_user(username: str, email: str):
    user_pool_id = os.environ.get("USER_POOL_ID")
    client = boto3.client(
        "cognito-idp",
        region_name=os.environ.get("AWS_REGION"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )
    try:
        response = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[{"Name": "email", "Value": email}],
        )
        cognito_id = response["User"]["Attributes"][0]["Value"]
        return cognito_id
    except client.exceptions.UsernameExistsException:
        raise UserExistsException("Username already exists")
    finally:
        client.close()
