import pytest
from bson import Binary
from mongoengine import Document, StringField
from pymongo import MongoClient
from pymongo.encryption import Algorithm, ClientEncryption

from mongoengine_plus.models import uuid_field
from mongoengine_plus.types import EncryptedString
from mongoengine_plus.types.encrypted_string.base import (
    create_data_key,
    get_data_key,
)
from mongoengine_plus.types.encrypted_string.exc import NoDataKeyFound
from mongoengine_plus.types.encrypted_string.fields import CODEC_OPTION


class User(Document):
    id = StringField(primary_key=True, default=uuid_field('US'))
    name = StringField()
    nss = EncryptedString(
        algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
        required=True,
        unique=True,
    )


@pytest.fixture
def user() -> User:
    user = User(name='Frida Kahlo', nss='secret')
    user.save()
    yield user
    user.delete()


def test_configure_encrypted_string():
    EncryptedString.configure_aws_kms(
        'foo.bar',
        'keyname',
        'test',
        'test',
        'us-east-1',
    )
    assert EncryptedString.key_namespace == 'foo.bar'
    assert EncryptedString.key_name == 'keyname'
    assert EncryptedString.aws_region_name == 'us-east-1'
    assert EncryptedString.kms_provider == dict(
        aws=dict(accessKeyId='test', secretAccessKey='test')
    )


def test_get_data_key_not_found() -> None:
    with pytest.raises(NoDataKeyFound):
        get_data_key('foo.bar', 'thekey')


def test_create_data_key(
    kms_key_arn: str, kms_connection_url: str, db_connection: MongoClient
) -> None:
    db_name = 'encryption'
    collection_name = '__keyVault'
    key_name = 'thekey'
    kms_region_name = 'us-east-1'

    EncryptedString.configure_aws_kms(
        f'{db_name}.{collection_name}',
        key_name,
        'test',
        'test',
        kms_region_name,
    )
    create_data_key(
        EncryptedString.kms_provider,
        EncryptedString.key_namespace,
        kms_key_arn,
        key_name,
        kms_connection_url,
        kms_region_name,
    )
    data_key = db_connection[db_name][collection_name].find_one(
        ({"keyAltNames": key_name})
    )

    assert data_key['keyAltNames'] == [key_name]
    assert type(data_key['keyMaterial']) is bytes
    assert data_key['masterKey'] == dict(
        provider='aws',
        region=EncryptedString.aws_region_name,
        key=kms_key_arn,
        endpoint=kms_connection_url.replace('https://', ''),
    )


@pytest.mark.usefixtures('setup_encrypted_string_data_key')
def test_encrypted_string_on_saving_and_reading(
    kms_key_arn: str, user: User, db_connection: MongoClient
) -> None:
    same_user = User.objects.get(id=user.id)
    # The EncryptedString field should encrypt the data when saving to MongoDB
    # and decrypt it when reading from MongoDB
    assert same_user.nss == 'secret'

    # Attempting to read the same field using PyMongo or any other library
    # should only retrieve the encrypted bytes
    user_dict = User._collection.find_one({'_id': user.id})
    client = db_connection

    assert user_dict['_id'] == user.id
    assert user_dict['name'] == user.name
    assert type(user_dict['nss']) == Binary

    with ClientEncryption(
        EncryptedString.kms_provider,
        EncryptedString.key_namespace,
        client,
        CODEC_OPTION,
    ) as client_encryption:
        # The ClientEncryption object should be able to decrypt the encrypted
        # value stored in MongoDB
        assert client_encryption.decrypt(user_dict['nss']) == 'secret'


@pytest.mark.usefixtures('setup_encrypted_string_data_key')
def test_query_encrypted_data(user: User) -> None:
    user_db = User.objects(nss=user.nss).first()
    assert user_db.id == user.id
