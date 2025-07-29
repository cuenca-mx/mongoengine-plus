import pytest
from mongoengine import StringField

from mongoengine_plus.aio.async_document import AsyncDocument
from mongoengine_plus.aio.async_signals import post_save, pre_save
from mongoengine_plus.models.event_handlers import handler


@pytest.mark.asyncio
async def test_async_signal_handler_on_asyncdocument():
    pre_calls = []
    post_calls = []

    @handler(pre_save)
    async def my_async_pre_handler(cls, document, **kwargs):
        pre_calls.append((document.name, getattr(document, "updated", False)))

    @handler(post_save)
    async def my_async_post_handler(cls, document, **kwargs):
        post_calls.append((document.name, getattr(document, "updated", False)))

    @my_async_pre_handler.apply
    @my_async_post_handler.apply
    class User(AsyncDocument):
        name = StringField(required=True)
        updated = StringField()

    user = User(name="Jane")
    await user.async_save()
    assert pre_calls[-1][0] == "Jane"
    assert post_calls[-1][0] == "Jane"

    user.name = "John"
    user.updated = "yes"
    await user.async_save()

    # The handlers should have been called again with updated data
    assert pre_calls[-1][0] == "John"
    assert pre_calls[-1][1] == "yes"
    assert post_calls[-1][0] == "John"
    assert post_calls[-1][1] == "yes"
    assert len(pre_calls) == 2
    assert len(post_calls) == 2
