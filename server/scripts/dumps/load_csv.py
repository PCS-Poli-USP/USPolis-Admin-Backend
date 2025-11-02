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
    solicitation_db_model,
    subject_building_link,
    subject_db_model,
    user_building_link,
    user_db_model,
)

engine = create_engine(f"{CONFIG.db_uri}/{CONFIG.db_database}")


def load_user_csv_to_db(csv_file: str) -> None:
    try:
        with open(csv_file, encoding="utf-8") as file:
            reader = csv.DictReader(file)

    except Exception as e:
        print(f"Erro ao carregar os dados do CSV (Usuários): {e}")


def load_building_csv_to_db(csv_file: str) -> None:
    try:
        sucess = 0
        total = 0
        with open(csv_file, encoding="utf-8") as file:
            reader = csv.DictReader(file)

            with Session(engine) as session:
                for row in reader:
                    total += 1
                    building = building_db_model.Building(
                        name=row["name"],
                        created_by_id=row["created_by_id"],  # type: ignore
                        updated_at=row["updated_at"],  # type: ignore
                    )
                    try:
                        session.add(building)
                        session.commit()
                        sucess += 1
                    except Exception as e:
                        print(f"Erro ao carregar o prédio {building.name}: {e}")
                        session.rollback()

        print(f"Prédios carregados com sucesso ({sucess}/{total}) no banco de dados!")

    except Exception as e:
        print(f"Erro ao carregar os dados do CSV (Prédios): {e}")


def load_classroom_csv_to_db(csv_file: str) -> None:
    try:
        success = 0
        total = 0
        with open(csv_file, encoding="utf-8") as file:
            reader = csv.DictReader(file)

            with Session(engine) as session:
                for row in reader:
                    total += 1
                    classroom = classroom_db_model.Classroom(
                        name=row["name"],  # type: ignore
                        capacity=row["capacity"],  # type: ignore
                        floor=row["floor"],  # type: ignore
                        ignore_to_allocate=True
                        if row["ignore_to_allocate"] == "t"
                        else False,  # type: ignore
                        accessibility=True if row["accessibility"] == "t" else False,  # type: ignore
                        projector=True if row["projector"] == "t" else False,  # type: ignore
                        air_conditioning=True
                        if row["air_conditioning"] == "t"
                        else False,  # type: ignore
                        updated_at=row["updated_at"],  # type: ignore
                        created_by_id=row["created_by_id"],  # type: ignore
                        building_id=row["building_id"],  # type: ignore
                    )
                    try:
                        session.add(classroom)
                        session.commit()
                        success += 1
                    except Exception as e:
                        print(f"Erro ao carregar a sala {classroom.name}: {e}")
                        session.rollback()

        print(f"Salas carregadas com sucesso ({success}/{total}) no banco de dados!")

    except Exception as e:
        print(f"Erro ao carregar os dados do CSV (Salas): {e}")


# Chama a função para carregar os dados
# load_building_csv_to_db("buildings.csv")
# load_classroom_csv_to_db("classroom.csv")
