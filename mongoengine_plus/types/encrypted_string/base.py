import os
from functools import lru_cache

from bson.binary import UUID_SUBTYPE, Binary
from mongoengine import get_connection

from .exc import NoDataKeyFound

KEY_NAMESPACE = 'encryption.__keyVault'
KEY_NAME = 'knox-card-key'
KMS_PROVIDER = dict(
    aws=dict(
        accessKeyId=os.environ['KMS_AWS_ACCESS_KEY'],
        secretAccessKey=os.environ['KMS_AWS_SECRET_ACCESS_KEY'],
    )
)


def get_data_key():
    client = get_connection()
    key_db, key_coll = KEY_NAMESPACE.split(".", 1)
    vault = client[key_db][key_coll]

    # Buscamos el data key
    data_key = vault.find_one({"keyAltNames": KEY_NAME})
    if not data_key:
        raise NoDataKeyFound
    return data_key


@lru_cache(maxsize=1)
def get_data_key_binary():
    """
    Get the data_key from mongo, there is only one data_key so this
    method always retrieve the same value, that's why we use the
    `lru_cache`
    """

    # Buscamos el data key
    data_key = get_data_key()
    uuid_data_key = data_key['_id']
    return Binary(uuid_data_key.bytes, UUID_SUBTYPE)
