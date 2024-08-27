"""FastAPI server configuration."""

from decouple import config  # type: ignore [import-untyped]
from pydantic import BaseModel


class Settings(BaseModel):
    """Server config settings."""

    root_url: str = config("ROOT_URL", default="http://localhost:8000")  # type: ignore
    port: str = config("PORT", default="8000")  # type: ignore

    # SQLAlchemy settings
    db_uri: str = config("DATABASE_URI")  # type: ignore
    db_database: str = config("DATABASE_NAME")  # type: ignore
    first_superuser_email: str = config("FIRST_SUPERUSER_EMAIL", "amdmin@uspolis.com")  # type: ignore
    first_superuser_password: str = config("FIRST_SUPERUSER_PASSWORD", "admin")  # type: ignore
    first_superuser_name: str = config("FIRST_SUPERUSER_NAME", "admin")  # type: ignore
    first_superuser_username: str = config("FIRST_SUPERUSER_USERNAME", "admin")  # type: ignore

    # AWS
    aws_region_name: str = config("AWS_REGION")  # type: ignore
    aws_access_key_id: str = config("AWS_ACCESS_KEY_ID")  # type: ignore
    aws_secret_access_key: str = config("AWS_SECRET_ACCESS_KEY")  # type: ignore
    aws_user_pool_id: str = config("AWS_USER_POOL_ID")  # type: ignore

    # Testing / Development:
    testing: bool = config("TESTING", default=False, cast=bool)
    override_auth: bool = config("OVERRIDE_AUTH", default=False, cast=bool)
    override_cognito_client: bool = config(
        "OVERRIDE_COGNITO_CLIENT", default=False, cast=bool
    )

    mock_username: str = config("MOCK_USERNAME", default="admin")  # type: ignore


CONFIG = Settings()
