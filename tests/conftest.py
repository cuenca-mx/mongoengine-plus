import subprocess
from typing import Generator

import boto3
import pytest
from pymongo import MongoClient

from mongoengine_plus.types import EncryptedString
from mongoengine_plus.types.encrypted_string.base import create_data_key


@pytest.fixture(scope='session')
def mongo_connection_url() -> Generator[str, None, None]:
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer() as mongo:
        yield (
            mongo.get_connection_url()
            + '/db?authSource=admin&retryWrites=true&w=majority'
        )


@pytest.fixture(autouse=True)
def db_connection(mongo_connection_url: str) -> MongoClient:
    import mongoengine

    return mongoengine.connect(host=mongo_connection_url)


@pytest.fixture
def kms_connection_url() -> Generator[str, None, None]:
    process = subprocess.Popen(
        [
            'moto_server',
            '-p',
            '4000',
            '-c',
            'tests/kms_cert.crt',
            '-k',
            'tests/kms_private_key.key',
        ]
    )
    yield 'https://127.0.0.1:4000'
    # import time
    # time.sleep(5)
    process.kill()


KEY_NAMESPACE = 'encryption.__keyVault'
KEY_NAME = 'knox-card-key'


@pytest.fixture
def kms_key_arn(kms_connection_url) -> str:
    """
    Creates new master key in the local kms, only for testing purpose.
    :return: Tuple: master key ARN, kms region, kms host name
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


@pytest.fixture
def setup_encrypted_string_data_key(
    kms_key_arn: str, db_connection, kms_connection_url: str
) -> Generator:
    """
    Creates data keys for testing purpose. It is required in order to use
    Explicit Client-Side Field Level Encryption (CSFLE)

    :param master_key_kms: Tuple: master key ARN, kms region, kms host name
    :return: None
    """
    EncryptedString.configure_aws_kms(
        'encryption.__keyVault',
        'thekey',
        'test',
        'test',
        'us-east-1',
    )

    db_name, key_coll = EncryptedString.key_namespace.split(".", 1)

    key_vault = db_connection[db_name][key_coll]
    key_vault.drop()
    create_data_key(
        EncryptedString.kms_provider,
        EncryptedString.key_namespace,
        kms_key_arn,
        'thekey',
        kms_connection_url,
        'us-east-1',
    )
    yield
    key_vault.drop()
