from services.email.email_service import EmailService
import smtplib
from email.message import EmailMessage
from core.config import mail_setting
from core.exceptions import EmailSendFailed
import logging

logger = logging.getLogger(__name__)


class SmtpProvider(EmailService):

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = mail_setting.SMTP_USER
        msg["To"] = to_email

        if html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        try:
            with smtplib.SMTP_SSL(
                host="smtp.gmail.com",
                port=465,
                timeout=10
            ) as server:

                server.login(
                    mail_setting.SMTP_USER,
                    mail_setting.SMTP_PASS
                )

                server.send_message(msg)

        except smtplib.SMTPException as e:
            logger.error("SMTP error while sending email", exc_info=True)
            raise EmailSendFailed("SMTP error occurred") from e

        except TimeoutError as e:
            logger.error("SMTP connection timed out", exc_info=True)
            raise EmailSendFailed("Email sending timed out") from e

        except Exception as e:
            logger.error("Unexpected error while sending email", exc_info=True)
            raise EmailSendFailed("Unexpected email error") from e
