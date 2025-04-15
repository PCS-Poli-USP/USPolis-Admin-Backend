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

    # GOOGLE AUTH
    google_auth_client_id: str = config("GOOGLE_AUTH_CLIENT_ID")  # type: ignore
    google_auth_client_secret: str = config("GOOGLE_AUTH_CLIENT_SECRET")  # type: ignore
    google_auth_redirect_uri: str = config("GOOGLE_AUTH_REDIRECT_URI")  # type: ignore

    # Testing / Development:
    test_db_uri: str = config("TEST_DATABASE_URI")  # type: ignore
    test_db_database: str = config("TEST_DATABASE_NAME")  # type: ignore
    testing: bool = config("TESTING", default=False, cast=bool)
    override_auth: bool = config("OVERRIDE_AUTH", default=False, cast=bool)
    mock_email: str = config("MOCK_EMAIL", default="uspolis@usp.br")  # type: ignore


CONFIG = Settings()
