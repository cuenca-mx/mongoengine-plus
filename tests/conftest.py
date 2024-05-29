from functools import partial
from typing import Generator

import mongomock
import pytest
from _pytest.monkeypatch import MonkeyPatch

# DATABASE_URI = 'mongodb://localhost:27017/db'


@pytest.fixture(scope='session')
def mongo_connection_url() -> Generator[str, None, None]:
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer() as mongo:
        yield (
            mongo.get_connection_url()
            + '/db?authSource=admin&retryWrites=true&w=majority'
        )


@pytest.fixture(autouse=True)
def connect_database(mongo_connection_url: str) -> None:
    import mongoengine

    mongoengine.connect(host=mongo_connection_url)
