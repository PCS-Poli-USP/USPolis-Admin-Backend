from sqlmodel import select

from server.deps.session_dep import get_db
from server.models.database.user_db_model import User


class TestGetDb:
    def test_yields_a_working_session_and_closes_it_after(self) -> None:
        generator = get_db()
        session = next(generator)

        session.exec(select(User)).all()

        with_no_more_values = False
        try:
            next(generator)
        except StopIteration:
            with_no_more_values = True

        assert with_no_more_values
