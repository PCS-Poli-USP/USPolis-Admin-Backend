import os
from dotenv import load_dotenv
import boto3

load_dotenv()


def write_access_token():
    client = boto3.client(
        "cognito-idp",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    try:
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': os.getenv("AWS_COGNITO_USERNAME"),
                'PASSWORD': os.getenv("AWS_COGNITO_PASSWORD")
            },
            ClientId=os.getenv("AWS_COGNITO_CLIENT_ID"),
            # UserPoolId=os.getenv("AWS_USER_POOL_ID"),
        )

        access_token = response['AuthenticationResult']['AccessToken']

    except Exception as e:
        print(e)
        access_token = "Error in authentication"

    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", ".."))
    file_path = os.path.join(path, "access_token.txt")

    with open(file_path, 'w') as file:
        file.write(access_token)


if __name__ == "__main__":
    write_access_token()
