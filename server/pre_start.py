import logging

from sqlalchemy import Engine
from sqlmodel import Session, select

from server.connections.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init(db_engine: Engine) -> None:
    with Session(db_engine) as session:
        # Try to create session to check if DB is awake
        session.exec(select(1))


def main() -> None:
    logger.info("Initializing service")
    init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
