from mongoengine import Document

from .async_query_set import AsyncQuerySet
from .async_signals import post_save, pre_save
from .utils import create_awaitable


class AsyncDocument(Document):
    meta = dict(
        abstract=True,
        queryset_class=AsyncQuerySet,
    )

    async def async_save(self, *args, **kwargs):
        signal_kwargs = kwargs.pop("signal_kwargs", {})
        await pre_save.send_async(
            self.__class__, document=self, **signal_kwargs
        )
        result = await create_awaitable(self.save, *args, **kwargs)
        await post_save.send_async(
            self.__class__, document=self, **signal_kwargs
        )
        return result

    async def async_reload(self, *fields, **kwargs):
        return await create_awaitable(self.reload, *fields, **kwargs)

    async def async_delete(self, signal_kwargs=None, **write_concern):
        return await create_awaitable(
            self.delete, signal_kwargs, **write_concern
        )
