from functools import partial

import mongomock
import pytest
from _pytest.monkeypatch import MonkeyPatch

DATABASE_URI = 'mongodb://localhost:27017/db'


@pytest.fixture(autouse=True)
def connect_database(monkeypatch: MonkeyPatch):
    import mongoengine

    connect = partial(
        mongoengine.connect, mongo_client_class=mongomock.MongoClient
    )
    monkeypatch.setattr(mongoengine, 'connect', connect)

    connect(host=DATABASE_URI)
