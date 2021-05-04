from mongoengine import StringField

from mongoengine_plus.aio import AsyncDocument
from mongoengine_plus.models import uuid_field


class City(AsyncDocument):
    id = StringField(primary_key=True, default=uuid_field('C'))
    name = StringField()
    state = StringField()
