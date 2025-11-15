"""FastAPI server configuration."""

from decouple import config, RepositoryEnv, Config as DConfig, Csv  # type: ignore
from pydantic import BaseModel

# Mapeamento dos arquivos por ambiente
env_files = {
    "DEVELOPMENT": ".env.dev",
    "PRODUCTION": ".env.prod",
    "STAGING": ".env.stage",
}

base_config = DConfig(RepositoryEnv(".env"))
env = base_config("ENVIRONMENT", default="DEVELOPMENT", cast=str).upper()  # pyright: ignore[reportAttributeAccessIssue, reportAssignmentType]
env_path = env_files.get(env, ".env.dev")
config = DConfig(RepositoryEnv(env_path))  # noqa: F811


class Settings(BaseModel):
    """Server config settings."""

    environment: str = config("ENVIRONMENT", default="development", cast=str)  # pyright: ignore[reportAssignmentType]
    log_max_size: int = config("LOG_MAX_SIZE", default=1_073_741_824, cast=int)  # pyright: ignore[reportAssignmentType]
    log_backup_count: int = config("LOG_BACKUP_COUNT", default=2, cast=int)  # pyright: ignore[reportAssignmentType]
    # CORS
    allowed_origins: list[str] = config(
        "ALLOWED_ORIGINS",
        default=["http://localhost:3000", "https://uspolis.com.br", "https://localhost:3000"],
        cast=Csv(),
    )  # pyright: ignore[reportAssignmentType]

    root_url: str = config("ROOT_URL", default="http://localhost:8000")  # pyright: ignore[reportAssignmentType]
    port: str = config("PORT", default="5000")  # pyright: ignore[reportAssignmentType]
    debug: bool = config("DEBUG", default=False, cast=bool)  # pyright: ignore[reportAssignmentType]

    # SQLAlchemy settings
    db_uri: str = config("DATABASE_URI")  # pyright: ignore[reportAssignmentType]
    db_database: str = config("DATABASE_NAME")  # pyright: ignore[reportAssignmentType]
    alembic_url: str = config("ALEMBIC_URL")  # pyright: ignore[reportAssignmentType]

    first_superuser_email: str = config("FIRST_SUPERUSER_EMAIL", "amdmin@uspolis.com")  # pyright: ignore[reportAssignmentType]
    first_superuser_name: str = config("FIRST_SUPERUSER_NAME", "admin")  # pyright: ignore[reportAssignmentType]

    # Email
    mail_host: str = config("MAIL_HOST", default="smtp.gmail.com")  # pyright: ignore[reportAssignmentType]
    mail_address: str = config("MAIL_ADDRESS")  # pyright: ignore[reportAssignmentType]
    mail_password: str = config("MAIL_PASSWORD")  # pyright: ignore[reportAssignmentType]
    mail_port: int = config("MAIL_PORT", default=465, cast=int)  # pyright: ignore[reportAssignmentType]

    # GOOGLE AUTH
    google_auth_client_id: str = config("GOOGLE_AUTH_CLIENT_ID")  # pyright: ignore[reportAssignmentType]
    google_auth_client_secret: str = config("GOOGLE_AUTH_CLIENT_SECRET")  # pyright: ignore[reportAssignmentType]
    google_auth_redirect_uri: str = config("GOOGLE_AUTH_REDIRECT_URI")  # pyright: ignore[reportAssignmentType]
    google_auth_domain_name: str = config("G_AUTH_DOMAIN_NAME")  # pyright: ignore[reportAssignmentType]
    google_auth_mobile_client_id: str = config("G_AUTH_CLIENT_ID")  # pyright: ignore[reportAssignmentType]

    # Testing / Development:
    test_db_uri: str = config("TEST_DATABASE_URI", default="")  # pyright: ignore[reportAssignmentType]
    test_db_database: str = config("TEST_DATABASE_NAME", default="")  # pyright: ignore[reportAssignmentType]
    test_alembic_url: str = config("TEST_ALEMBIC_URL", default="")  # pyright: ignore[reportAssignmentType]
    testing: bool = config("TESTING", default=False, cast=bool)
    development: bool = (
        config("ENVIRONMENT", default="development", cast=str) == "development"
    )
    override_auth: bool = config("OVERRIDE_AUTH", default=False, cast=bool)
    mock_email: str = config("MOCK_EMAIL", default="uspolis@usp.br")  # pyright: ignore[reportAssignmentType]


CONFIG = Settings()
