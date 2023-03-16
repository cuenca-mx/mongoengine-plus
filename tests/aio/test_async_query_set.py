import pytest
from mongoengine import Q

from tests.aio.cities import City


@pytest.mark.asyncio
async def test_count(cities):
    count = await City.objects.async_count()
    assert len(cities) == count
    filtered = await City.objects(state='Chiapas').async_count()
    assert filtered == 2
    filtered = await City.objects.filter(
        Q(state='Chiapas') | Q(state='Tabasco')
    ).async_count()
    assert filtered == 3


@pytest.mark.asyncio
async def test_to_list(cities):
    cities_from_db = await City.objects.async_to_list()
    assert len(cities_from_db) == len(cities)
    assert all(a.id == b.id for a, b in zip(cities, cities_from_db))
    filtered = await City.objects.filter(
        Q(state='Chiapas') | Q(state='Tabasco')
    ).async_to_list()
    assert len(filtered) == 3


@pytest.mark.asyncio
async def test_first(cities):
    first_city = await City.objects(state='Tabasco').async_first()
    assert first_city.state == 'Tabasco'


@pytest.mark.asyncio
async def test_update(cities):
    await City.objects(name='San Cristobal').async_update(
        set__name='San Cristobal de las Casas'
    )
    sancris = await City.objects.async_get(name__contains='San Cristobal')
    assert sancris.name == 'San Cristobal de las Casas'


@pytest.mark.asyncio
async def test_bulk_insert():
    cities = [
        City(name='Villahermosa', state='Tabasco'),
        City(name='Ciudad de México', state='CDMX'),
        City(name='Monterrey', state='Nuevo León'),
        City(name='San Cristobal', state='Chiapas'),
        City(name='Tuxtla Gutiérrez', state='Chiapas'),
    ]
    cities.sort(key=lambda c: c.name)
    await City.objects.async_insert(cities, load_bulk=False)

    cities_db = list(await City.objects.order_by('+name').async_to_list())
    assert len(cities_db) == len(cities)
    assert all(a.name == b.name for a, b in zip(cities, cities_db))
