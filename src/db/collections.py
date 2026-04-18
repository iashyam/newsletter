from pymongo import MongoClient
from src.core.config import settings

_client: MongoClient | None = None


def _get_db():
    global _client
    if _client is None:
        _client = MongoClient(settings.mongodb_uri)
    return _client[settings.mongodb_db]


# All collection references live here — import these, never construct db[...] elsewhere
subscriber_collection = lambda: _get_db()["subscribers"]
