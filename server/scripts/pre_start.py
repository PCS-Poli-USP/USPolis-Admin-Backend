import logging

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import Engine, inspect
from sqlmodel import Session, SQLModel, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from server.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init(engine)
    logger.info("Service finished initializing")
    # The migration history can't build the schema from an empty database (its
    # first revision already assumes the base tables exist), so a fresh database
    # gets the current models via create_all() and is stamped at head. Running
    # create_all() on a database Alembic already manages would instead create
    # tables ahead of the pending migrations that create them, which then fail
    # with DuplicateTable.
    if inspect(engine).has_table("alembic_version"):
        logger.info("Existing database, leaving schema changes to Alembic")
        return
    SQLModel.metadata.create_all(engine)
    logger.info("Tables created successfully")
    alembic_command.stamp(AlembicConfig("alembic.ini"), "head")
    logger.info("Database stamped at Alembic head")


if __name__ == "__main__":
    main()
