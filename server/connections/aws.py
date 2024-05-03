import boto3

from server.config import CONFIG

aws_client = boto3.client(
    "cognito-idp",
    region_name=CONFIG.aws_region_name,
    aws_access_key_id=CONFIG.aws_access_key_id,
    aws_secret_access_key=CONFIG.aws_secret_access_key,
)
