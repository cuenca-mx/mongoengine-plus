from bson import Binary
from mongoengine import Document, StringField
from pymongo.encryption import Algorithm, ClientEncryption

from mongoengine_plus.models import uuid_field
from mongoengine_plus.types import EncryptedString
from mongoengine_plus.types.encrypted_string.base import (
    KEY_NAMESPACE,
    KMS_PROVIDER,
)
from mongoengine_plus.types.encrypted_string.fields import CODEC_OPTION


class User(Document):
    id = StringField(primary_key=True, default=uuid_field('US'))
    name = StringField()
    nss = EncryptedString(
        algorithm=Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
        required=True,
        unique=True,
    )


def test_encrypted_string_on_saving_and_reading(
    kms_key_arn, create_data_key, connect_database
) -> None:
    user = User(name='Frida Kahlo', nss='secret')
    user.save()
    assert user

    same_user = User.objects.get(id=user.id)
    # The EncryptedString field should encrypt the data when saving to MongoDB
    # and decrypt it when reading from MongoDB
    assert same_user.nss == 'secret'

    # Attempting to read the same field using PyMongo or any other library
    # should only retrieve the encrypted bytes
    user_json = User._collection.find_one({'_id': user.id})
    client = connect_database

    assert user_json['_id'] == user.id
    assert user_json['name'] == user.name
    assert type(user_json['nss']) == Binary

    with ClientEncryption(
        KMS_PROVIDER, KEY_NAMESPACE, client, CODEC_OPTION
    ) as client_encryption:
        # The ClientEncryption object should be able to decrypt the encrypted
        # value stored in MongoDB
        assert client_encryption.decrypt(user_json['nss']) == 'secret'
