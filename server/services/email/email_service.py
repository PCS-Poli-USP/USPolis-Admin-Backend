from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from fastapi.background import BackgroundTasks
from jinja2 import Environment, FileSystemLoader
from server.config import CONFIG
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
    ClassroomSolicitationDeny,
)
from server.models.http.requests.email_request_models import (
    MailSend,
    SolicitationApprovedMail,
    SolicitationDeniedMail,
    SolicitationRequestedMail,
)
from pathlib import Path

template_path = Path(__file__).resolve().parent.parent.parent / "templates"
image_path = Path(__file__).resolve().parent.parent.parent / "static" / "assets"
env = Environment(loader=FileSystemLoader(template_path))


class EmailService:
    @staticmethod
    def send_email(context: MailSend, background_tasks: BackgroundTasks) -> None:
        background_tasks.add_task(EmailService.__send_email, context)

    @staticmethod
    def __send_email(context: MailSend) -> None:
        # create email
        msg = MIMEMultipart()
        # msg = MIMEText(context.body, "html")
        msg["Subject"] = context.subject
        msg["From"] = CONFIG.mail_address
        msg["To"] = ",".join(context.to)
        msg.attach(MIMEText(context.body, "html"))
        # send email

        # Anexa a imagem
        with open(f"{image_path}/uspolis.logo.png", "rb") as img:
            img_data = img.read()
            image = MIMEImage(img_data, name="logo.png")
            image.add_header("Content-ID", "<logo>")
            msg.attach(image)

        with SMTP_SSL(CONFIG.mail_host, CONFIG.mail_port) as smtp:
            smtp.login(CONFIG.mail_address, CONFIG.mail_password)
            smtp.send_message(msg)

    @staticmethod
    def send_solicitation_request_email(
        users: list[User],
        solicitation: ClassroomSolicitation,
        background_tasks: BackgroundTasks,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-requested.html")
        for user in users:
            body = template.render(
                data=SolicitationRequestedMail.from_solicitation(user, solicitation)
            )
            subject = "Reserva de Sala - USPolis"
            context = MailSend(to=[user.email], subject=subject, body=body)
            EmailService.send_email(context, background_tasks)

    @staticmethod
    def send_solicitation_approved_email(
        input: ClassroomSolicitationApprove,
        solicitation: ClassroomSolicitation,
        background_tasks: BackgroundTasks,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-approved.html")
        body = template.render(
            data=SolicitationApprovedMail.from_solicitation(input, solicitation)
        )
        subject = "Reserva de Sala - USPolis"
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        EmailService.send_email(context, background_tasks)

    @staticmethod
    def send_solicitation_denied_email(
        input: ClassroomSolicitationDeny,
        solicitation: ClassroomSolicitation,
        background_tasks: BackgroundTasks,
    ) -> None:
        template = env.get_template("/solicitations/solicitation-denied.html")
        body = template.render(
            data=SolicitationDeniedMail.from_solicitation(input, solicitation)
        )
        subject = "Reserva de Sala - USPolis"
        context = MailSend(to=[solicitation.user.email], subject=subject, body=body)
        EmailService.send_email(context, background_tasks)
