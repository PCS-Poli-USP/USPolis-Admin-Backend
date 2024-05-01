"""FastAPI server configuration."""

from decouple import config
from pydantic import BaseModel


class Settings(BaseModel):
    """Server config settings."""

    root_url: str = config("ROOT_URL", default="http://localhost:8080")

    # Mongo Engine settings
    mongo_uri: str = config("MONGO_URI")
    mongo_db_name: str = config("MONGO_DB_NAME")

    # AWS
    aws_region_name: str = config("AWS_REGION")
    aws_access_key_id: str = config("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = config("AWS_SECRET_ACCESS_KEY")

    testing: bool = config("TESTING", default=False, cast=bool)


CONFIG = Settings()
