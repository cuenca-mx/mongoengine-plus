import pytest
from mongoengine import DoesNotExist

from .cities import City


@pytest.mark.asyncio
async def test_save():
    city = City(name='Tuxtla Gutierrez')
    await city.async_save()
    city = await City.objects.async_get()
    assert city.id is not None
    assert city.name == 'Tuxtla Gutierrez'
    await city.async_delete()
    with pytest.raises(DoesNotExist):
        await City.objects.async_get(id=city.id)


@pytest.mark.asyncio
async def test_reload():
    city = City(name='Tuxtla Gutierrez')
    await city.async_save()
    same_city = await City.objects.async_get(id=city.id)
    assert same_city.name == city.name
    city.name = 'Tuxtla'
    await city.async_save()
    await same_city.async_reload()
    assert same_city.id == city.id
    assert same_city.name == city.name
    await city.async_delete()
