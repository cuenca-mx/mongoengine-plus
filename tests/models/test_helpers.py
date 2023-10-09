from datetime import datetime as dt
from enum import Enum

from mongoengine import (
    BooleanField,
    ComplexDateTimeField,
    DateTimeField,
    DecimalField,
    DictField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    GenericLazyReferenceField,
    IntField,
    LazyReferenceField,
    ListField,
    StringField,
)

from mongoengine_plus.models.helpers import mongo_to_dict, uuid_field
from mongoengine_plus.types.enum_field import EnumField


class Reference(Document):
    pass


class EnumType(Enum):
    member = 'name'


class IntEnum(int, Enum):
    exito = 0
    invalid = 1


class Embedded(EmbeddedDocument):
    meta = {'allow_inheritance': True}
    name = StringField()


class HeritageEmbedded(Embedded):
    lastname = StringField()


class TestModel(Document):
    id = StringField(default=uuid_field('PK'), primary_key=True)
    str_field = StringField()
    int_field = IntField(default=1)
    float_field = FloatField(default=1.1)
    decimal_field = DecimalField(default=1.2)
    boolean_field = BooleanField(default=True)
    none_field = StringField(default=None)
    dict_field = DictField(default=dict(one=1, two=2))
    date_time_field = DateTimeField(default=dt.now)
    complex_date_time_field = ComplexDateTimeField(default=dt.now)
    enum_field = EnumField(EnumType, default=EnumType.member)
    list_field = ListField(IntField(), default=lambda: [42])
    enum_list_field = ListField(EnumField(EnumType), default=[EnumType.member])
    embedded_list_field = ListField(EmbeddedDocumentField(Embedded))
    embedded_field = EmbeddedDocumentField(Embedded)
    heritage_field = EmbeddedDocumentField(HeritageEmbedded)
    lazzy_field = LazyReferenceField(Reference)
    lazzy_list_field = ListField(LazyReferenceField(Reference))
    generic_lazzy_field = GenericLazyReferenceField()
    code = EnumField(IntEnum)

    __test__ = False


def test_mongo_to_dict():
    reference = Reference()
    reference.save()
    model = TestModel(
        embedded_list_field=[Embedded(name='')],
        lazzy_list_field=[reference],
        embedded_field=Embedded(name='Peter'),
        heritage_field=HeritageEmbedded(name='some', lastname='other'),
        code=IntEnum.exito,
    )
    model.save()
    model_dict = mongo_to_dict(model, exclude_fields=['str_field'])
    assert model_dict['id'].startswith('PK')
    assert 'date_time_field' in model_dict
    assert 'complex_date_time_field' in model_dict
    assert model_dict['int_field'] == 1
    assert model_dict['float_field'] == '1.1'
    assert model_dict['decimal_field'] == 1.2
    assert model_dict['dict_field']['one'] == 1
    assert model_dict['enum_field'] == 'name'
    assert model_dict['boolean_field'] is True
    assert model_dict['none_field'] is None
    assert model_dict['list_field'] == ['42']
    assert model_dict['enum_list_field'] == ['name']
    assert model_dict['embedded_list_field'] == [{'name': ''}]
    assert model_dict['embedded_field'] == {'name': 'Peter'}
    assert model_dict['lazzy_field_uri'] is None
    assert model_dict['generic_lazzy_field_uri'] is None
    assert model_dict['lazzy_list_field_uris'] == ["Reference object"]
    assert model_dict['heritage_field'] == {
        'name': 'some',
        'lastname': 'other',
    }
    assert model_dict['code'] == 0
