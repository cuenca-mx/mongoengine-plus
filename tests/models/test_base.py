from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    StringField,
)

from mongoengine_plus.models import BaseModel


class File(EmbeddedDocument):
    url = StringField()
    file_type = StringField()


class Address(EmbeddedDocument, BaseModel):
    # Inheritance from BaseModel, to use _excluded and _hidden
    _excluded = ['reference']
    _hidden = ['secret_code']
    street = StringField()
    secret_code = StringField()
    reference = StringField()


class TestModel(BaseModel, Document):
    id = StringField(primary_key=True)
    secret_field = StringField()
    address = EmbeddedDocumentField(Address)
    document = EmbeddedDocumentField(File)

    __test__ = False
    _hidden = ['secret_field']


def test_hide_field():
    address = Address(
        street='123 Main St',
        reference='not display this',
        secret_code='898612',
    )
    doc = File(url='https://example.com', file_type='pdf')
    model = TestModel(
        id='12345',
        secret_field='secret',
        document=doc,
        address=address,
    )
    model_dict = model.to_dict()
    expected = {
        'id': '12345',
        'secret_field': '********',
        'address': {
            'street': '123 Main St',
            'secret_code': '********',
        },
        'document': {
            'url': 'https://example.com',
            'file_type': 'pdf',
        },
    }
    assert model_dict == expected
