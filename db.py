import os
import csv
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_collection():
    global _client
    if _client is None:
        _client = MongoClient(os.environ["MONGODB_URI"])
    db = _client[os.environ.get("MONGODB_DB", "newsletter")]
    return db["subscribers"]


def list_subscribers():
    return list(get_collection().find({}, {"_id": 0}))


def add_subscriber(email: str, name: str = ""):
    col = get_collection()
    email = email.strip().lower()
    if col.find_one({"email": email}):
        return False, "already exists"
    col.insert_one({
        "email": email,
        "name": name.strip(),
        "subscribed_at": datetime.now(timezone.utc),
        "active": True,
    })
    return True, "added"


def remove_subscriber(email: str):
    col = get_collection()
    result = col.delete_one({"email": email.strip().lower()})
    return result.deleted_count > 0


def get_active_subscribers():
    return list(get_collection().find({"active": True}, {"_id": 0}))


def import_from_csv(filepath: str):
    added, skipped = 0, 0
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalize headers — Google Forms uses full question text as header
        for row in reader:
            # Try common column name patterns
            email = (
                row.get("email")
                or row.get("Email")
                or row.get("Email Address")
                or row.get("email_address")
                or ""
            ).strip().lower()
            name = (
                row.get("name")
                or row.get("Name")
                or row.get("Full Name")
                or row.get("full_name")
                or ""
            ).strip()
            if not email:
                skipped += 1
                continue
            ok, _ = add_subscriber(email, name)
            if ok:
                added += 1
            else:
                skipped += 1
    return added, skipped
