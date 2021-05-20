from mongoengine import Document

from .async_query_set import AsyncQuerySet
from .utils import create_awaitable


class AsyncDocument(Document):
    meta = dict(
        abstract=True,
        queryset_class=AsyncQuerySet,
    )

    async def async_save(self, *args, **kwargs):
        return await create_awaitable(self.save, *args, **kwargs)

    async def async_reload(self, *fields, **kwargs):
        return await create_awaitable(self.reload, *fields, **kwargs)

    async def async_delete(self, signal_kwargs=None, **write_concern):
        return await create_awaitable(
            self.delete, signal_kwargs, **write_concern
        )
