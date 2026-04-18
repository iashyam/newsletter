from pydantic import BaseModel


class RenderedNewsletter(BaseModel):
    html: str
    subject: str
    warnings: list[str] = []


class FailedDelivery(BaseModel):
    email: str
    error: str


class SendResult(BaseModel):
    success_count: int
    failed: list[FailedDelivery] = []
