import asyncio

# from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from jinja2 import Environment, FileSystemLoader
from server.config import CONFIG
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
    ClassroomSolicitationDeny,
    ClassroomSolicitationUpdated,
)
from server.models.http.requests.email_request_models import (
    MailSend,
    SolicitationApprovedMail,
    SolicitationDeletedMail,
    SolicitationDeniedMail,
    SolicitationRequestedMail,
)
from pathlib import Path

template_path = Path(__file__).resolve().parent.parent.parent / "templates"
image_path = Path(__file__).resolve().parent.parent.parent / "static" / "assets"
env = Environment(loader=FileSystemLoader(template_path))


RESERVATION_SUBJECT = "Reserva de Sala - USPolis"


class EmailService:
    @staticmethod
    def send_email_sync(context: MailSend) -> None:
        # create email
        msg = MIMEMultipart()
        msg["Subject"] = context.subject
        msg["From"] = f"{CONFIG.mail_address}"
        msg["Reply-To"] = f"no-reply-{CONFIG.mail_address}"
        msg["To"] = ",".join(context.to)
        msg.attach(MIMEText(context.body, "html"))

        with SMTP_SSL(CONFIG.mail_host, CONFIG.mail_port) as smtp:
            smtp.login(CONFIG.mail_address, CONFIG.mail_password)
            smtp.send_message(msg)

    @staticmethod
    async def send_email(context: MailSend) -> None:
        await asyncio.to_thread(EmailService.send_email_sync, context)

    @staticmethod
    async def send_solicitation_request_email(
        users: list[User],
        solicitation: ClassroomSolicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-requested.html")
        for user in users:
            body = template.render(
                data=SolicitationRequestedMail.from_solicitation(user, solicitation)
            )
            subject = RESERVATION_SUBJECT
            context = MailSend(to=[user.email], subject=subject, body=body)
            await EmailService.send_email(context)

    @staticmethod
    async def send_solicitation_approved_email(
        input: ClassroomSolicitationApprove,
        solicitation: ClassroomSolicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-approved.html")
        body = template.render(
            data=SolicitationApprovedMail.from_solicitation(input, solicitation)
        )
        subject = RESERVATION_SUBJECT
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        await EmailService.send_email(context)

    @staticmethod
    async def send_solicitation_updated_email(
        input: ClassroomSolicitationUpdated,
        solicitation: ClassroomSolicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-updated.html")
        body = template.render(
            data=SolicitationApprovedMail.from_solicitation(input, solicitation)
        )
        subject = RESERVATION_SUBJECT
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        await EmailService.send_email(context)

    @staticmethod
    async def send_solicitation_deleted_email(
        reservation: Reservation,
        solicitation: ClassroomSolicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-deleted.html")
        body = template.render(
            data=SolicitationDeletedMail.from_reservation_and_solicitation(
                solicitation, reservation
            )
        )
        subject = RESERVATION_SUBJECT
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        await EmailService.send_email(context)

    @staticmethod
    async def send_solicitation_denied_email(
        input: ClassroomSolicitationDeny,
        solicitation: ClassroomSolicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-denied.html")
        body = template.render(
            data=SolicitationDeniedMail.from_solicitation(input, solicitation)
        )
        subject = RESERVATION_SUBJECT
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        await EmailService.send_email(context)
