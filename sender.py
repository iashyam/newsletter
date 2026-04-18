import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]


def send_newsletter(html: str, subject: str, subscribers: list[dict]) -> dict:
    """
    Send the newsletter to all active subscribers.
    Returns a summary dict with counts of successes and failures.
    """
    from_field = f"{os.environ.get('FROM_NAME', 'Newsletter')} <{os.environ['FROM_EMAIL']}>"

    success, failed = 0, []

    for sub in subscribers:
        email = sub["email"]
        name = sub.get("name", "")

        # Personalize unsubscribe placeholder (hook this up to real URLs later)
        personalized_html = html.replace(
            "{unsubscribe_url}",
            f"mailto:{os.environ['FROM_EMAIL']}?subject=Unsubscribe&body=Please%20unsubscribe%20{email}",
        )

        try:
            resend.Emails.send({
                "from": from_field,
                "to": [email],
                "subject": subject,
                "html": personalized_html,
            })
            success += 1
        except Exception as e:
            failed.append({"email": email, "error": str(e)})

    return {"success": success, "failed": failed}
