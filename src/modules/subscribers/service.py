import csv
from datetime import datetime, timezone

from src.core.exceptions import (
    SubscriberAlreadyExistsError,
    SubscriberNotFoundError,
    InvalidCSVError,
)
from src.db.collections import subscriber_collection
from src.modules.subscribers.schema import Subscriber, SubscriberCreate, ImportResult


def list_all() -> list[Subscriber]:
    docs = subscriber_collection().find({}, {"_id": 0})
    return [Subscriber(**doc) for doc in docs]


def get_active() -> list[Subscriber]:
    docs = subscriber_collection().find({"active": True}, {"_id": 0})
    return [Subscriber(**doc) for doc in docs]


def add(data: SubscriberCreate) -> Subscriber:
    email = data.email.strip().lower()
    if subscriber_collection().find_one({"email": email}):
        raise SubscriberAlreadyExistsError(email)

    doc = {
        "email": email,
        "name": data.name.strip(),
        "subscribed_at": datetime.now(timezone.utc),
        "active": True,
    }
    subscriber_collection().insert_one(doc)
    return Subscriber(**{k: v for k, v in doc.items() if k != "_id"})


def remove(email: str) -> None:
    email = email.strip().lower()
    result = subscriber_collection().delete_one({"email": email})
    if result.deleted_count == 0:
        raise SubscriberNotFoundError(email)


def import_from_csv(filepath: str) -> ImportResult:
    _EMAIL_KEYS = ("email", "Email", "Email Address", "email_address")
    _NAME_KEYS = ("name", "Name", "Full Name", "full_name")

    try:
        file = open(filepath, newline="", encoding="utf-8")
    except OSError as e:
        raise InvalidCSVError(str(e))

    added, skipped = 0, 0
    with file:
        try:
            reader = csv.DictReader(file)
            for row in reader:
                email = next((row[k].strip().lower() for k in _EMAIL_KEYS if k in row and row[k].strip()), "")
                name = next((row[k].strip() for k in _NAME_KEYS if k in row and row[k].strip()), "")

                if not email:
                    skipped += 1
                    continue

                try:
                    add(SubscriberCreate(email=email, name=name))
                    added += 1
                except SubscriberAlreadyExistsError:
                    skipped += 1
        except csv.Error as e:
            raise InvalidCSVError(str(e))

    return ImportResult(added=added, skipped=skipped)
