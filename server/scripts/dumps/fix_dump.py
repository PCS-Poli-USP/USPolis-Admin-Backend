from sqlalchemy import text
from sqlmodel import Session, create_engine
from server.config import CONFIG

# Configure sua conexão com o banco de dados
engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


# Função para atualizar a sequência
def update_sequence(table_name: str, column_name: str) -> None:
    with Session(engine) as session:
        session.execute(
            text(f"""
                SELECT setval(
                    pg_get_serial_sequence(:table_name, :column_name),
                    (SELECT MAX({column_name}) FROM {table_name}) + 1,
                    false
                )
            """),
            {"table_name": table_name, "column_name": column_name}
        )
        session.commit()

# Atualize as tabelas necessárias
update_sequence("buildings", "id")
update_sequence("classrooms", "id")
