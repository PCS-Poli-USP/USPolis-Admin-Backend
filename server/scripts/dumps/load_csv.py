import csv
from sqlmodel import Session, create_engine
from server.config import CONFIG

from server.models.database import (  # noqa
    building_db_model,
    calendar_db_model,
    calendar_holiday_category_link,
    class_calendar_link,
    class_db_model,
    classroom_db_model,
    forum_db_model,
    forum_post_reacts_link,
    forum_post_report_link,
    holiday_category_db_model,
    holiday_db_model,
    institutional_event_db_model,
    mobile_comments_db_model,
    mobile_user_db_model,
    occurrence_db_model,
    reservation_db_model,
    schedule_db_model,
    subject_building_link,
    subject_db_model,
    user_building_link,
    user_db_model,
    classroom_solicitation_db_model,
)


# Cria o engine de conexão com o banco de dados
engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


# Função para ler o CSV e salvar no banco de dados
def load_csv_to_db(csv_file: str) -> None:
    try:
        with open(csv_file, encoding="utf-8") as file:
            # Lê os dados do CSV
            reader = csv.DictReader(file)  # Leitor com cabeçalho do CSV

            with Session(engine) as session:
                for row in reader:
                    # # Cria a instância da entidade Building
                    # building = building_db_model.Building(
                    #     id=row['id'], # type: ignore
                    #     name=row['name'],
                    #     created_by_id=1, # type: ignore
                    #     updated_at=row['updated_at'] # type: ignore
                    # )

                    # # Adiciona o Building ao banco de dados
                    # session.add(building)

                    # Caso você tenha uma tabela Classroom também no CSV
                    if True:
                        classroom = classroom_db_model.Classroom(
                            name=row["name"],  # type: ignore
                            capacity=row["capacity"],  # type: ignore
                            floor=row["floor"],  # type: ignore
                            ignore_to_allocate=True
                            if row["ignore_to_allocate"] == "t"
                            else False,  # type: ignore
                            accessibility=True
                            if row["accessibility"] == "t"
                            else False,  # type: ignore
                            projector=True if row["projector"] == "t" else False,  # type: ignore
                            air_conditioning=True
                            if row["air_conditioning"] == "t"
                            else False,  # type: ignore
                            updated_at=row["updated_at"],  # type: ignore
                            created_by_id=1,  # type: ignore
                            building_id=row["building_id"],  # type: ignore
                            id=row["id"],  # type: ignore
                        )
                        session.add(classroom)

                # Commit para salvar todas as instâncias no banco
                session.commit()

        print("Dados carregados com sucesso no banco de dados!")

    except Exception as e:
        print(f"Erro ao carregar os dados do CSV: {e}")


# Caminho para o arquivo CSV
csv_file = "classroom.csv"

# Chama a função para carregar os dados
load_csv_to_db(csv_file)
