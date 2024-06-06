import subprocess
from typing import Generator

import boto3
import pytest
from pymongo import MongoClient

from mongoengine_plus.types import EncryptedStringField
from mongoengine_plus.types.encrypted_string.base import create_data_key


@pytest.fixture(scope='session', autouse=True)
def mongo_connection_url() -> Generator[str, None, None]:
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer() as mongo:
        yield (
            mongo.get_connection_url()
            + '/db?authSource=admin&retryWrites=true&w=majority'
        )


@pytest.fixture(scope='session', autouse=True)
def db_connection(mongo_connection_url: str) -> MongoClient:
    import mongoengine

    return mongoengine.connect(host=mongo_connection_url)


@pytest.fixture(scope='session')
def kms_connection_url() -> Generator[str, None, None]:
    process = subprocess.Popen(
        [
            'moto_server',
            '-p',
            '4000',
            '-c',
            'tests/localhost.crt',
            '-k',
            'tests/localhost.key',
        ]
    )
    yield 'https://127.0.0.1:4000'
    process.kill()


@pytest.fixture(scope='session')
def kms_key_arn(kms_connection_url: str) -> str:
    """
    Creates new master key in the local kms, only for testing purpose.
    """
    kms = boto3.client(
        'kms',
        endpoint_url=kms_connection_url,
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        verify=False,
    )
    kms_key = kms.create_key()
    return kms_key['KeyMetadata']['Arn']


@pytest.fixture(scope='session')
def setup_encrypted_string_data_key(
    kms_key_arn: str, db_connection: MongoClient, kms_connection_url: str
) -> Generator:
    """
    Creates data keys for testing purpose. It is required in order to use
    Explicit Client-Side Field Level Encryption (CSFLE)
    """
    EncryptedStringField.configure_aws_kms(
        'encryption.__keyVault',
        'thekey',
        'test',
        'test',
        'us-east-1',
    )

    db_name, key_coll = EncryptedStringField.key_namespace.split(".", 1)

    key_vault = db_connection[db_name][key_coll]
    key_vault.drop()
    create_data_key(
        EncryptedStringField.kms_provider,
        EncryptedStringField.key_namespace,
        kms_key_arn,
        'thekey',
        kms_connection_url,
        'us-east-1',
    )
    yield
    key_vault.drop()
