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
        # Configure Brevo API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = mail_setting.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ):
        """
        Send email via Brevo API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: If True, body is treated as HTML; otherwise plain text
        
        Raises:
            EmailSendFailed: If email sending fails
        """
        try:
            # Prepare sender
            sender = {
                "email": mail_setting.EMAIL_FROM,
                "name": mail_setting.EMAIL_FROM_NAME
            }
            
            # Prepare recipient
            to = [{"email": to_email}]
            
            # Prepare email content
            if html:
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender=sender,
                    subject=subject,
                    html_content=body
                )
            else:
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender=sender,
                    subject=subject,
                    text_content=body
                )

            # Send email via Brevo API
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully via Brevo to {to_email}. Message ID: {api_response.message_id}")

        except ApiException as e:
            logger.error(f"Brevo API error while sending email to {to_email}: {e}", exc_info=True)
            # Don't crash the app, just log the error
            # Optionally raise if you want to handle it upstream
            raise EmailSendFailed(f"Brevo API error: {e.status}") from e

        except Exception as e:
            logger.error(f"Unexpected error while sending email via Brevo to {to_email}: {e}", exc_info=True)
            raise EmailSendFailed("Unexpected email error") from e
