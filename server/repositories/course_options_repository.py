from sqlmodel import Session, select
from server.models.database.course_options_db_model import CourseOptions

class CourseOptionRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_all(self) -> list[CourseOptions]:
        statement = select(CourseOptions).order_by(CourseOptions.name)
        return list(self.session.exec(statement).all())

    def upsert_many(self, options: list[CourseOptions]) -> None:
        for option in options:
            existing = self.session.get(
                CourseOptions,
                (option.codcur, option.codhab)
            )

            if existing:
                existing.name = option.name
            else:
                self.session.add(option)

        self.session.commit()