from datetime import datetime
from pydantic import BaseModel, EmailStr


class Subscriber(BaseModel):
    email: EmailStr
    name: str = ""
    active: bool = True
    subscribed_at: datetime | None = None


class SubscriberCreate(BaseModel):
    email: EmailStr
    name: str = ""


class ImportResult(BaseModel):
    added: int
    skipped: int
