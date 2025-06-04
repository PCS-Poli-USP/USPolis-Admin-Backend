"""FastAPI server configuration."""

from decouple import config, RepositoryEnv, Config as DConfig, Csv  # type: ignore [import-untyped]
from pydantic import BaseModel

# Mapeamento dos arquivos por ambiente
env_files = {
    "DEVELOPMENT": ".env.dev",
    "PRODUCTION": ".env.prod",
}

base_config = DConfig(RepositoryEnv(".env"))
env = base_config("ENVIRONMENT", default="DEVELOPMENT", cast=str).upper()  # type: ignore
env_path = env_files.get(env, ".env.dev")
config = DConfig(RepositoryEnv(env_path))  # noqa: F811


class Settings(BaseModel):
    """Server config settings."""

    enviroment: str = config("ENVIRONMENT", default="DEVELOPMENT", cast=str)  # type: ignore
    # CORS
    allowed_origins: list[str] = config(
        "ALLOWED_ORIGINS",
        default=["http://localhost:3000", "https://www.uspolis.com.br"],
        cast=Csv(),
    )  # type: ignore

    root_url: str = config("ROOT_URL", default="http://localhost:8000")  # type: ignore
    port: str = config("PORT", default="8000")  # type: ignore
    debug: bool = config("DEBUG", default=False, cast=bool)  # type: ignore

    # SQLAlchemy settings
    db_uri: str = config("DATABASE_URI")  # type: ignore
    db_database: str = config("DATABASE_NAME")  # type: ignore
    alembic_url: str = config("ALEMBIC_URL")  # type: ignore

    first_superuser_email: str = config("FIRST_SUPERUSER_EMAIL", "amdmin@uspolis.com")  # type: ignore
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
    test_db_uri: str = config("TEST_DATABASE_URI", default="")  # type: ignore
    test_db_database: str = config("TEST_DATABASE_NAME", default="")  # type: ignore
    test_alembic_url: str = config("TEST_ALEMBIC_URL", default="")  # type: ignore
    testing: bool = config("TESTING", default=False, cast=bool)
    override_auth: bool = config("OVERRIDE_AUTH", default=False, cast=bool)
    mock_email: str = config("MOCK_EMAIL", default="uspolis@usp.br")  # type: ignore


CONFIG = Settings()
