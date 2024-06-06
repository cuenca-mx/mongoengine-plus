from functools import lru_cache
from typing import Dict

from bson import CodecOptions
from bson.binary import STANDARD, UUID_SUBTYPE, Binary
from mongoengine import get_connection
from pymongo.encryption import ClientEncryption

from .exc import NoDataKeyFound


def get_data_key(key_namespace: str, key_name: str) -> Dict:
    connection = get_connection()
    key_db, key_coll = key_namespace.split(".", 1)
    vault = connection[key_db][key_coll]

    # Buscamos el data key
    data_key = vault.find_one({"keyAltNames": key_name})
    if not data_key:
        raise NoDataKeyFound
    return data_key


@lru_cache(maxsize=1)
def get_data_key_binary(key_namespace: str, key_name: str) -> Binary:
    """
    Get the data_key from mongo, there is only one data_key so this
    method always retrieve the same value, that's why we use the
    `lru_cache`
    """

    # Buscamos el data key
    data_key = get_data_key(key_namespace, key_name)
    uuid_data_key = data_key['_id']
    return Binary(uuid_data_key.bytes, UUID_SUBTYPE)


def create_data_key(
    kms_provider: Dict,
    key_namespace: str,
    key_arn: str,
    key_name: str,
    kms_connection_url: str,
    kms_region_name: str,
) -> None:
    connection = get_connection()
    db_name, collection_name = key_namespace.split(".", 1)
    key_vault = connection[db_name][collection_name]
    key_vault.create_index(
        "keyAltNames",
        unique=True,
        partialFilterExpression={"keyAltNames": {"$exists": True}},
    )

    with ClientEncryption(
        kms_provider,
        key_namespace,
        connection,
        CodecOptions(uuid_representation=STANDARD),
    ) as client_encryption:
        client_encryption.create_data_key(
            'aws',
            key_alt_names=[key_name],
            master_key=dict(
                key=key_arn,
                region=kms_region_name,
                endpoint=kms_connection_url,
            ),
        )
