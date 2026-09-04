from server.models.database.solicitation_db_model import Solicitation
from server.models.http.requests.email_request_models import (
    BugReportMail,
    FeedbackMail,
    SolicitationApprovedMail,
    SolicitationDeletedMail,
    SolicitationDeniedMail,
    SolicitationMailBase,
    SolicitationRequestedMail,
)
from server.models.http.requests.solicitation_request_models import (
    SolicitationApprove,
    SolicitationDeny,
)
from server.utils.enums.bug_enums import BugPriority, BugType
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.week_day import WeekDay
from tests.utils.academic_test_utils import (
    make_building,
    make_classroom,
    make_reservation,
    make_solicitation,
    make_user,
)
from tests.utils.bug_report_test_utils import make_bug_report
from tests.utils.feedback_test_utils import make_feedback
from tests.utils.time_test_utils import make_schedule


def _make_solicitation_with_reservation(*, reason: str | None = None) -> Solicitation:
    building = make_building(name="Bloco A")
    classroom = make_classroom(building=building, name="Sala 1")
    user = make_user(name="Ana")
    schedule = make_schedule(
        classroom=classroom, week_day=WeekDay.MONDAY, all_day=False
    )
    reservation = make_reservation(
        schedule=schedule, type_=ReservationType.MEETING, title="Reunião de equipe"
    )
    # make_reservation's _given() helper drops None kwargs (falling through to
    # a random default) rather than forcing the field to None, so an
    # explicit "no reason" case has to be set directly instead.
    reservation.reason = reason
    solicitation = make_solicitation(building=building, user=user, capacity=10)
    solicitation.reservation = reservation
    solicitation.solicited_classroom = classroom
    return solicitation


class TestSolicitationMailBase:
    def test_from_solicitation(self) -> None:
        solicitation = _make_solicitation_with_reservation()

        mail = SolicitationMailBase.from_solicitation(solicitation)

        assert mail.title == "Reunião de equipe"
        assert mail.building == "Bloco A"
        assert mail.classroom == "Sala 1"
        assert mail.capacity == 10

    def test_from_solicitation_without_a_classroom(self) -> None:
        solicitation = _make_solicitation_with_reservation()
        solicitation.solicited_classroom = None

        mail = SolicitationMailBase.from_solicitation(solicitation)

        assert mail.classroom == "Não especificada"


class TestSolicitationDeniedMail:
    def test_from_solicitation(self) -> None:
        solicitation = _make_solicitation_with_reservation()
        input = SolicitationDeny(justification="Sala já reservada")

        mail = SolicitationDeniedMail.from_solicitation(input, solicitation)

        assert mail.username == "Ana"
        assert mail.justification == "Sala já reservada"


class TestSolicitationApprovedMail:
    def test_from_solicitation(self) -> None:
        solicitation = _make_solicitation_with_reservation()
        input = SolicitationApprove(classroom_id=1, classroom_name="Sala 2")

        mail = SolicitationApprovedMail.from_solicitation(input, solicitation)

        assert mail.username == "Ana"
        assert mail.approved_classroom == "Sala 2"


class TestSolicitationRequestedMail:
    def test_from_solicitation_with_a_reason(self) -> None:
        solicitation = _make_solicitation_with_reservation(reason="Aula de reposição")

        mail = SolicitationRequestedMail.from_solicitation(solicitation)

        assert mail.requester == "Ana"
        assert mail.reason == "Aula de reposição"

    def test_from_solicitation_without_a_reason(self) -> None:
        solicitation = _make_solicitation_with_reservation(reason=None)

        mail = SolicitationRequestedMail.from_solicitation(solicitation)

        assert mail.reason == "Não informado"


class TestSolicitationDeletedMail:
    def test_from_solicitation(self) -> None:
        solicitation = _make_solicitation_with_reservation()

        mail = SolicitationDeletedMail.from_solicitation(solicitation)

        assert mail.username == "Ana"


class TestFeedbackMail:
    def test_from_feedback(self) -> None:
        user = make_user(name="Ana")
        feedback = make_feedback(user=user)

        mail = FeedbackMail.from_feedback(feedback)

        assert mail.user_name == "Ana"
        assert mail.title == feedback.title


class TestBugReportMail:
    def test_from_report(self) -> None:
        user = make_user(name="Ana")
        report = make_bug_report(user=user)

        mail = BugReportMail.from_report(report)

        assert mail.user_name == "Ana"
        assert mail.type == BugType.to_ptBr(report.type)
        assert mail.priority == BugPriority.to_ptBr(report.priority)
