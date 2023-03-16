from mongoengine import QuerySet

from .utils import create_awaitable


class AsyncQuerySet(QuerySet):
    async def async_first(self):
        return await create_awaitable(self.first)

    async def async_get(self, *q_objs, **query):
        return await create_awaitable(self.get, *q_objs, **query)

    async def async_count(self, with_limit_and_skip=False):
        return await create_awaitable(self.count, with_limit_and_skip)

    async def async_to_list(self):
        return await create_awaitable(list, self)

    async def async_update(self, *u_objs, **query):
        return await create_awaitable(self.update, *u_objs, **query)

    async def async_insert(
        self,
        doc_or_docs,
        load_bulk=True,
        write_concern=None,
        signal_kwargs=None,
    ):
        return await create_awaitable(
            self.insert, doc_or_docs, load_bulk, write_concern, signal_kwargs
        )
