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


# Edit this template with your welcome message before deploying.
_WELCOME_HTML = """
<div style="font-family: Georgia, 'Times New Roman', serif; max-width: 600px; margin: 0 auto; padding: 40px 20px; color: #1a1a1a;">
  <p>Hi{name_part},</p>
  <p><!-- YOUR WELCOME MESSAGE HERE --></p>
  <p>Talk soon.</p>
</div>
"""


def send_welcome_email(to: str, name: str = "") -> None:
    name_part = f" {name.strip()}" if name.strip() else ""
    send_email(to=to, subject=f"Welcome to {settings.from_name}!", html=_WELCOME_HTML.format(name_part=name_part))
