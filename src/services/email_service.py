from pathlib import Path

import resend
from src.core.config import settings
from src.core.exceptions import EmailSendError

resend.api_key = settings.resend_api_key

_WELCOME_TEMPLATE = Path(__file__).parent.parent / "templates" / "welcome.md"


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


def send_welcome_email(to: str, name: str = "") -> None:
    from src.services.renderer_service import render
    newsletter = render(str(_WELCOME_TEMPLATE))
    html = newsletter.html.replace("[[name]]", name.strip() if name.strip() else "there")
    send_email(to=to, subject=newsletter.subject, html=html)
