import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr

from src.modules.subscribers.schema import SubscriberCreate
from src.modules.subscribers.service import add as add_subscriber
from src.services.email_service import send_welcome_email
from src.core.exceptions import SubscriberAlreadyExistsError, EmailSendError

logger = logging.getLogger(__name__)

app = FastAPI()


class SubscribeRequest(BaseModel):
    email: EmailStr
    name: str


@app.get("/")
def index():
    return FileResponse("web/static/index.html")


@app.post("/subscribe")
def subscribe(body: SubscribeRequest):
    try:
        subscriber = add_subscriber(SubscriberCreate(email=body.email, name=body.name))
    except SubscriberAlreadyExistsError:
        return JSONResponse(status_code=409, content={"error": "already subscribed"})

    try:
        send_welcome_email(to=subscriber.email, name=subscriber.name)
    except EmailSendError as e:
        logger.error("Welcome email failed for %s: %s", subscriber.email, e)

    return {"ok": True}
