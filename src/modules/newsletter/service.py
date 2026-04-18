from src.core.config import settings
from src.core.exceptions import EmailSendError
from src.modules.newsletter.schema import RenderedNewsletter, SendResult, FailedDelivery
from src.modules.subscribers.schema import Subscriber
from src.services import renderer_service, email_service


def render(md_file_path: str) -> RenderedNewsletter:
    return renderer_service.render(md_file_path)


def send(newsletter: RenderedNewsletter, subscribers: list[Subscriber]) -> SendResult:
    success_count = 0
    failed = []

    for sub in subscribers:
        # Personalise unsubscribe link per recipient
        personalized_html = newsletter.html.replace(
            "{unsubscribe_url}",
            f"mailto:{settings.from_email}?subject=Unsubscribe&body=Please%20unsubscribe%20{sub.email}",
        )
        try:
            email_service.send_email(to=sub.email, subject=newsletter.subject, html=personalized_html)
            success_count += 1
        except EmailSendError as e:
            failed.append(FailedDelivery(email=sub.email, error=e.message))

    return SendResult(success_count=success_count, failed=failed)
