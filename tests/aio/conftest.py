from typing import Generator, List

import pytest

from .cities import City


@pytest.fixture
def cities() -> Generator[List[City], None, None]:
    cities = [
        City(name='Villahermosa', state='Tabasco'),
        City(name='Ciudad de México', state='CDMX'),
        City(name='Monterrey', state='Nuevo León'),
        City(name='San Cristobal', state='Chiapas'),
        City(name='Tuxtla Gutiérrez', state='Chiapas'),
    ]
    for city in cities:
        city.save()
    yield cities
    for city in cities:
        city.delete()
