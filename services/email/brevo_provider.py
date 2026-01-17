from services.email.email_service import EmailService
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from core.config import mail_setting
from core.exceptions import EmailSendFailed
import logging

logger = logging.getLogger(__name__)


class BrevoProvider(EmailService):
    """
    Brevo (formerly Sendinblue) email provider implementation.
    Uses Brevo API v3 for sending transactional emails.
    """

    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = mail_setting.BREVO_API_KEY

        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
    ):
        """
        Send email via Brevo API.
        """
        try:
            # Sender (MUST be verified in Brevo)
            sender = {
                "email": mail_setting.EMAIL_FROM,
                "name": mail_setting.EMAIL_FROM_NAME or "EduStore",
            }

            # Reply-To (REQUIRED for freemail senders like gmail.com)
            reply_to = {
                "email": mail_setting.EMAIL_FROM,
                "name": mail_setting.EMAIL_FROM_NAME or "EduStore",
            }

            # Recipient
            to = [{"email": to_email}]

            # Build email
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                sender=sender,
                reply_to=reply_to,
                subject=subject,
                html_content=body if html else None,
                text_content=None if html else body,
            )

            # Send email
            api_response = self.api_instance.send_transac_email(send_smtp_email)

            logger.info(
                f"Email sent successfully via Brevo to {to_email}. "
                f"Message ID: {api_response.message_id}"
            )

        except ApiException as e:
            logger.error(
                f"Brevo API error while sending email to {to_email}: {e}",
                exc_info=True,
            )
            raise EmailSendFailed("Brevo API error while sending email") from e

        except Exception as e:
            logger.error(
                f"Unexpected error while sending email via Brevo to {to_email}: {e}",
                exc_info=True,
            )
            raise EmailSendFailed("Unexpected email error") from e
