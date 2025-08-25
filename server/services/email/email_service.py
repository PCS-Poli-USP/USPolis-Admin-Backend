import asyncio

# from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from jinja2 import Environment, FileSystemLoader
from server.config import CONFIG
from server.models.database.solicitation_db_model import (
    Solicitation,
)
from server.models.database.user_db_model import User
from server.models.http.requests.solicitation_request_models import (
    SolicitationApprove,
    SolicitationDeny,
    SolicitationUpdated,
)
from server.models.http.requests.email_request_models import (
    BCCMailSend,
    MailSend,
    SolicitationApprovedMail,
    SolicitationCancelledMail,
    SolicitationDeletedMail,
    SolicitationDeniedMail,
    SolicitationRequestedMail,
)
from server.logger import logger
from pathlib import Path

template_path = Path(__file__).resolve().parent.parent.parent / "templates"
image_path = Path(__file__).resolve().parent.parent.parent / "static" / "assets"
env = Environment(loader=FileSystemLoader(template_path))


RESERVATION_SUBJECT = "Reserva de Sala - USPolis"


class EmailService:
    @staticmethod
    def send_bcc_email_sync(context: BCCMailSend) -> None:
        try:
            msg = MIMEMultipart()
            msg["Subject"] = context.subject
            msg["From"] = f"{CONFIG.mail_address}"
            msg["To"] = f"{CONFIG.mail_address}"
            msg["Reply-To"] = f"no-reply-{CONFIG.mail_address}"
            msg.attach(MIMEText(context.body, "html"))
            with SMTP_SSL(CONFIG.mail_host, CONFIG.mail_port) as smtp:
                smtp.login(CONFIG.mail_address, CONFIG.mail_password)
                smtp.send_message(msg, to_addrs=context.bcc_list)

        except Exception as e:
            logger.error(f"Error sending BCC email: {e}")

    @staticmethod
    def send_email_sync(context: MailSend) -> None:
        try:
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

        except Exception as e:
            logger.error(f"Error sending email: {e}")

    @staticmethod
    async def send_email(context: MailSend) -> None:
        await asyncio.to_thread(EmailService.send_email_sync, context)

    @staticmethod
    async def send_bcc_email(context: BCCMailSend) -> None:
        await asyncio.to_thread(EmailService.send_bcc_email_sync, context)

    @staticmethod
    async def send_solicitation_request_email(
        users: list[User],
        solicitation: Solicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-requested.html")
        bcc_list = [user.email for user in users]
        body = template.render(
            data=SolicitationRequestedMail.from_solicitation(solicitation)
        )
        subject = RESERVATION_SUBJECT

        context = BCCMailSend(
            bcc_list=bcc_list,
            subject=subject,
            body=body,
        )
        await EmailService.send_bcc_email(context)

    @staticmethod
    async def send_solicitation_approved_email(
        input: SolicitationApprove,
        solicitation: Solicitation,
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
        input: SolicitationUpdated,
        solicitation: Solicitation,
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
        solicitation: Solicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-deleted.html")
        body = template.render(
            data=SolicitationDeletedMail.from_solicitation(solicitation=solicitation)
        )
        subject = RESERVATION_SUBJECT
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        await EmailService.send_email(context)

    @staticmethod
    async def send_solicitation_denied_email(
        input: SolicitationDeny,
        solicitation: Solicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-denied.html")
        body = template.render(
            data=SolicitationDeniedMail.from_solicitation(input, solicitation)
        )
        subject = RESERVATION_SUBJECT
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        await EmailService.send_email(context)

    @staticmethod
    async def send_solicitation_cancelled_email(
        users: list[User],
        solicitation: Solicitation,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-cancelled.html")
        bcc_list = [user.email for user in users]
        body = template.render(
            data=SolicitationCancelledMail.from_solicitation(solicitation)
        )
        subject = RESERVATION_SUBJECT

        context = BCCMailSend(
            bcc_list=bcc_list,
            subject=subject,
            body=body,
        )
        await EmailService.send_bcc_email(context)
