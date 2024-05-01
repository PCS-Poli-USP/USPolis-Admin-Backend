"""FastAPI server configuration."""

from decouple import config
from pydantic import BaseModel


class Settings(BaseModel):
    """Server config settings."""

    root_url: str = config("ROOT_URL", default="http://localhost:8080")

    # Mongo Engine settings
    mongo_uri: str = config("MONGO_URI")

    testing: bool = config("TESTING", default=False, cast=bool)


CONFIG = Settings()
