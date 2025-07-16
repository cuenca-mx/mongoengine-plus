from asyncer import asyncify
from mongoengine import Document

from .async_query_set import AsyncQuerySet


class AsyncDocument(Document):
    meta = dict(
        abstract=True,
        queryset_class=AsyncQuerySet,
    )

    async def async_save(self, *args, **kwargs):
        return await asyncify(self.save)(*args, **kwargs)

    async def async_reload(self, *fields, **kwargs):
        return await asyncify(self.reload)(*fields, **kwargs)

    async def async_delete(self, signal_kwargs=None, **write_concern):
        return await asyncify(self.delete)(signal_kwargs, **write_concern)
