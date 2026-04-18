import resend
from src.core.config import settings
from src.core.exceptions import EmailSendError

resend.api_key = settings.resend_api_key


def send_email(to: str, subject: str, html: str) -> None:
    """Low-level email sender. Raises EmailSendError on failure."""
    try:
        resend.Emails.send({
            "from": f"{settings.from_name} <{settings.from_email}>",
            "to": [to],
            "subject": subject,
            "html": html,
        })
    except Exception as e:
        raise EmailSendError(to, str(e))
