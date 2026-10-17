"""FastAPI server configuration."""

import os
import tempfile

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

    environment: str = config("ENVIRONMENT", default="DEVELOPMENT", cast=str)  # pyright: ignore[reportAssignmentType]
    log_max_size: int = config("LOG_MAX_SIZE", default=1_073_741_824, cast=int)  # pyright: ignore[reportAssignmentType]
    log_backup_count: int = config("LOG_BACKUP_COUNT", default=2, cast=int)  # pyright: ignore[reportAssignmentType]
    error_metrics_retention_days: int = config(
        "ERROR_METRICS_RETENTION_DAYS", default=31, cast=int
    )  # pyright: ignore[reportAssignmentType]
    # CORS
    allowed_origins: list[str] = config(
        "ALLOWED_ORIGINS",
        default=[
            "http://localhost:3000",
            "https://uspolis.com.br",
            "https://localhost:3000",
        ],
        cast=Csv(),
    )  # pyright: ignore[reportAssignmentType]

    root_url: str = config("ROOT_URL", default="http://localhost:8000")  # pyright: ignore[reportAssignmentType]
    # Where the frontend lives: links sent to people (e.g. API key delivery
    # links) point here.
    frontend_url: str = config("FRONTEND_URL", default="http://localhost:3000")  # pyright: ignore[reportAssignmentType]
    port: str = config("PORT", default="5000")  # pyright: ignore[reportAssignmentType]
    debug: bool = config("DEBUG", default=False, cast=bool)  # pyright: ignore[reportAssignmentType]

    # SQLAlchemy settings
    db_uri: str = config("DATABASE_URI")  # pyright: ignore[reportAssignmentType]
    db_database: str = config("DATABASE_NAME")  # pyright: ignore[reportAssignmentType]
    # SQLAlchemy pool, per worker process (see server/db.py).
    db_pool_size: int = config("DB_POOL_SIZE", default=5, cast=int)  # pyright: ignore[reportAssignmentType]
    db_max_overflow: int = config("DB_MAX_OVERFLOW", default=10, cast=int)  # pyright: ignore[reportAssignmentType]
    db_pool_recycle_seconds: int = config(
        "DB_POOL_RECYCLE_SECONDS", default=1800, cast=int
    )  # pyright: ignore[reportAssignmentType]
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

    allowed_gmails_domains: list[str] = config(
        "ALLOWED_GMAILS_DOMAINS",
        default="",
        cast=Csv(),
    )  # pyright: ignore[reportAssignmentType]
    allowed_gmails: list[str] = config(
        "ALLOWED_GMAILS",
        default="",
        cast=Csv(),
    )  # pyright: ignore[reportAssignmentType]

    # Monitoring and Analytics Services
    health_api_key: str = config("HEALTH_API_KEY", default="")  # pyright: ignore[reportAssignmentType]

    # Rate limiting (see docs/RATE_LIMIT.md)
    redis_url: str = config("REDIS_URL", default="")  # pyright: ignore[reportAssignmentType]
    rate_limit_mode: str = config("RATE_LIMIT_MODE", default="off")  # pyright: ignore[reportAssignmentType]
    # "max/window_seconds" rules, all enforced together, per client IP.
    # Defaults come from the 2025-12 → 2026-10 production traffic analysis.
    anon_rate_limits: str = config(
        "ANON_RATE_LIMITS", default="40/10,150/60,5000/86400"
    )  # pyright: ignore[reportAssignmentType]

    # Partner API keys (see docs/API_KEYS.md). The secret HMACs every key
    # before it's stored: 32+ random bytes, different per environment.
    api_key_secret: str = config("API_KEY_SECRET", default="")  # pyright: ignore[reportAssignmentType]
    # Used for keys without their own `apikeyratelimit` rows, so a key is
    # never unlimited. Browser keys get their own default (shared by every
    # visitor of the partner's site).
    api_key_default_limits: str = config(
        "API_KEY_DEFAULT_LIMITS", default="30/10,120/60,10000/86400"
    )  # pyright: ignore[reportAssignmentType]
    api_key_browser_default_limits: str = config(
        "API_KEY_BROWSER_DEFAULT_LIMITS", default="60/10,300/60,20000/86400"
    )  # pyright: ignore[reportAssignmentType]

    # JupiterWeb schedule import (see server/services/jupiter_crawler/crawl_limiter.py).
    # Each crawl runs a headless Chromium (200-500 MB): this caps them per host.
    jupiter_crawl_max_concurrent: int = config(
        "JUPITER_CRAWL_MAX_CONCURRENT", default=2, cast=int
    )
    # How long a request waits for a free slot before getting a 503.
    jupiter_crawl_queue_seconds: float = config(
        "JUPITER_CRAWL_QUEUE_SECONDS", default=15, cast=float
    )
    # Hard cap on one crawl, browser launch included (504 when exceeded).
    jupiter_crawl_timeout_seconds: float = config(
        "JUPITER_CRAWL_TIMEOUT_SECONDS", default=60, cast=float
    )
    # Must be shared by every worker of the host (same machine/container).
    jupiter_crawl_lock_dir: str = config(
        "JUPITER_CRAWL_LOCK_DIR",
        default=os.path.join(tempfile.gettempdir(), "uspolis-jupiter-crawl"),
    )  # pyright: ignore[reportAssignmentType]

    # Testing / Development:
    test_db_uri: str = config("TEST_DATABASE_URI", default="")  # pyright: ignore[reportAssignmentType]
    test_db_database: str = config("TEST_DATABASE_NAME", default="")  # pyright: ignore[reportAssignmentType]
    test_alembic_url: str = config("TEST_ALEMBIC_URL", default="")  # pyright: ignore[reportAssignmentType]
    testing: bool = config("TESTING", default=False, cast=bool)
    development: bool = environment.lower() == "development"
    override_auth: bool = config("OVERRIDE_AUTH", default=False, cast=bool)
    mock_email: str = config("MOCK_EMAIL", default="uspolis@usp.br")  # pyright: ignore[reportAssignmentType]


CONFIG = Settings()
