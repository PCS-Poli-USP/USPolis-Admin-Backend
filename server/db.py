from collections.abc import Generator

from sqlmodel import Session, create_engine

from server.config import CONFIG

engine = create_engine(str(CONFIG.sql_alchemy_db_uri))


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
