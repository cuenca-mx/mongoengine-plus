from asyncer import asyncify
from mongoengine import QuerySet


class AsyncQuerySet(QuerySet):
    async def async_first(self):
        return await asyncify(self.first)()

    async def async_get(self, *q_objs, **query):
        return await asyncify(self.get)(*q_objs, **query)

    async def async_count(self, with_limit_and_skip=False):
        return await asyncify(self.count)(with_limit_and_skip)

    async def async_to_list(self):
        return await asyncify(list)(self)

    async def async_update(self, *u_objs, **query):
        return await asyncify(self.update)(*u_objs, **query)

    async def async_insert(
        self,
        doc_or_docs,
        load_bulk=True,
        write_concern=None,
        signal_kwargs=None,
    ):
        return await asyncify(self.insert)(
            doc_or_docs, load_bulk, write_concern, signal_kwargs
        )

    async def async_delete(
        self, write_concern=None, _from_doc_delete=False, cascade_refs=None
    ):
        return await asyncify(self.delete)(
            write_concern, _from_doc_delete, cascade_refs
        )

    async def async_modify(
        self,
        upsert=False,
        full_response=False,
        remove=False,
        new=False,
        array_filters=None,
        **update,
    ):
        return await create_awaitable(
            self.modify,
            upsert=upsert,
            full_response=full_response,
            remove=remove,
            new=new,
            array_filters=array_filters,
            **update,
        )
