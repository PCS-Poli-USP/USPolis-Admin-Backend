"""The app's emails (sent through the Gmail API) render from templates."""

from datetime import datetime
from unittest.mock import patch

from server.models.database.forum_db_model import ForumPost
from server.models.database.mobile_user_db_model import MobileUser
from server.models.http.requests.email_request_models import (
    ForumPostReportedMail,
    MobileCommentMail,
)
from server.services.email.email_service import EmailService


def _user() -> MobileUser:
    return MobileUser(
        id=7, sub="s", email="ana@usp.br", given_name="Ana", family_name="Souza"
    )


class TestMobileComment:
    def test_renders_the_message_and_the_sender(self) -> None:
        body = EmailService.render_mobile_comment(
            MobileCommentMail.from_comment(comment="Olá!", email=None, user=_user())
        )

        assert "Olá!" in body
        assert "Ana Souza" in body
        assert "ana@usp.br" in body  # falls back to the app user's email
        assert "FALE CONOSCO" in body

    def test_anonymous_message(self) -> None:
        body = EmailService.render_mobile_comment(
            MobileCommentMail.from_comment(comment="Olá!", email=None, user=None)
        )

        assert "Não identificado" in body
        assert "Não informado" in body

    def test_escapes_what_the_sender_wrote(self) -> None:
        body = EmailService.render_mobile_comment(
            MobileCommentMail.from_comment(
                comment="<script>alert(1)</script>", email=None, user=None
            )
        )

        assert "<script>" not in body
        assert "&lt;script&gt;" in body


class TestForumPostReported:
    def _post(self, content: str) -> ForumPost:
        post = ForumPost(
            id=1287,
            subject_id=1,
            content=content,
            user_id=7,
            created_at=datetime(2026, 11, 21, 22, 14),
            report_count=10,
        )
        post.user = _user()
        return post

    def test_renders_the_post_and_its_author(self) -> None:
        body = EmailService.render_forum_post_reported(
            ForumPostReportedMail.from_post(self._post("Respostas?"), "MAC0110")
        )

        assert "1287" in body
        assert "MAC0110" in body
        assert "Respostas?" in body
        assert "Ana Souza" in body
        assert "21/11/2026 às 22:14" in body
        assert "10 VEZES" in body

    def test_escapes_the_post_content(self) -> None:
        body = EmailService.render_forum_post_reported(
            ForumPostReportedMail.from_post(self._post("<img src=x>"), "MAC0110")
        )

        assert "<img src=x>" not in body


def test_comment_route_sends_the_template_with_its_subject() -> None:
    from server.routes.public import mobile_comments_routes

    with (
        patch.object(mobile_comments_routes, "gmail_login"),
        patch.object(mobile_comments_routes, "gmail_send_message") as send,
    ):
        mobile_comments_routes.send_email("Olá!", "ana@usp.br", None)

    _, html = send.call_args.args
    assert "FALE CONOSCO" in html
    assert send.call_args.kwargs["subject"] == "Fale conosco - App USPolis"


def test_report_route_sends_the_template_with_its_subject() -> None:
    from server.routes.public import forum_routes

    post = TestForumPostReported()._post("Respostas?")
    with (
        patch.object(forum_routes, "gmail_login"),
        patch.object(forum_routes, "gmail_send_message") as send,
    ):
        forum_routes.send_email(post, "MAC0110")

    _, html = send.call_args.args
    assert "POSTAGEM DENUNCIADA" in html
    assert send.call_args.kwargs["subject"] == (
        "Postagem denunciada no fórum - App USPolis"
    )
