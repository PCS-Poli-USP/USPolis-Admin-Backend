from sqlmodel import create_engine

from server.config import CONFIG

engine = create_engine(str(CONFIG.sql_alchemy_db_uri))
