from mongoengine import QuerySet

from .utils import create_awaitable


class AsyncQuerySet(QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def async_get(self, *q_objs, **query):
        return await create_awaitable(self.get, *q_objs, **query)

    async def async_count(self, with_limit_and_skip=False):
        return await create_awaitable(self.count, with_limit_and_skip)

    async def async_to_list(self):
        return await create_awaitable(list, self)
