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

    # Email
    mail_host: str = config("MAIL_HOST", default="smtp.gmail.com")  # type: ignore
    mail_address: str = config("MAIL_ADDRESS")  # type: ignore
    mail_password: str = config("MAIL_PASSWORD")  # type: ignore
    mail_port: int = config("MAIL_PORT", default=465, cast=int)  # type: ignore

    # AWS
    aws_region_name: str = config("AWS_REGION")  # type: ignore
    aws_access_key_id: str = config("AWS_ACCESS_KEY_ID")  # type: ignore
    aws_secret_access_key: str = config("AWS_SECRET_ACCESS_KEY")  # type: ignore
    aws_user_pool_id: str = config("AWS_USER_POOL_ID")  # type: ignore

    # GOOGLE AUTH
    google_auth_secret: str = config("GOOGLE_AUTH_SECRET") # type: ignore

    # Testing / Development:
    testing: bool = config("TESTING", default=False, cast=bool)
    override_auth: bool = config("OVERRIDE_AUTH", default=False, cast=bool)
    override_cognito_client: bool = config(
        "OVERRIDE_COGNITO_CLIENT", default=False, cast=bool
    )
    mock_email: str = config("MOCK_EMAIL", default="uspolis@usp.br")  # type: ignore


CONFIG = Settings()
