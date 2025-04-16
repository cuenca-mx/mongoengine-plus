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


@pytest.mark.asyncio
async def test_async_delete(cities):
    city = await City.objects(state='CDMX').async_first()
    assert city
    await City.objects(state='CDMX').async_delete()
    city = await City.objects(state='CDMX').async_first()
    assert not city


@pytest.mark.asyncio
async def test_async_modify(cities):
    # Test modifying a document and returning the updated version
    city = await City.objects(name='San Cristobal').async_modify(
        set__name='San Cristobal de las Casas', new=True
    )
    assert city.name == 'San Cristobal de las Casas'

    # Verify the change was saved to the database
    db_city = await City.objects(
        name='San Cristobal de las Casas'
    ).async_first()
    assert db_city is not None
    assert db_city.name == 'San Cristobal de las Casas'

    # Test modifying a document and returning the original version
    city = await City.objects(name='Tuxtla Gutiérrez').async_modify(
        set__name='Tuxtla', new=False
    )
    assert city.name == 'Tuxtla Gutiérrez'

    # Verify the change was still made
    db_city = await City.objects(name='Tuxtla').async_first()
    assert db_city is not None

    # Test upsert when document doesn't exist
    new_city = await City.objects(name='Cancún').async_modify(
        set__state='Quintana Roo', upsert=True, new=True
    )
    assert new_city is not None
    assert new_city.name == 'Cancún'
    assert new_city.state == 'Quintana Roo'

    # Test remove option
    city = await City.objects(name='Cancún').async_modify(remove=True)
    assert city.name == 'Cancún'

    # Verify the document was removed
    db_city = await City.objects(name='Cancún').async_first()
    assert db_city is None
