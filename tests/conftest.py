import os
import subprocess
from typing import Generator, Tuple

import boto3
import pytest
import requests
from bson import CodecOptions
from bson.binary import STANDARD
from pymongo.encryption import ClientEncryption


@pytest.fixture(scope='session')
def mongo_connection_url() -> Generator[str, None, None]:
    from testcontainers.mongodb import MongoDbContainer

    with MongoDbContainer() as mongo:
        yield (
            mongo.get_connection_url()
            + '/db?authSource=admin&retryWrites=true&w=majority'
        )


@pytest.fixture(autouse=True)
def connect_database(mongo_connection_url: str):
    import mongoengine

    return mongoengine.connect(host=mongo_connection_url)


@pytest.fixture
def kms_connection_url():
    # process = subprocess.Popen(
    #     [
    #         'moto_server',
    #         '-p',
    #         '4000',
    #         '-c',
    #         'tests/kms_cert.crt',
    #         '-k',
    #         'tests/kms_private_key.key',
    #     ]
    # )
    yield 'https://127.0.0.1:4000'
    # import time
    # time.sleep(5)
    # process.kill()


KEY_NAMESPACE = 'encryption.__keyVault'
KEY_NAME = 'knox-card-key'
KMS_PROVIDER = dict(
    aws=dict(
        accessKeyId='test',
        secretAccessKey='test',
    )
)

@pytest.fixture
def master_key_kms(kms_connection_url):
    """
    Creates new master key in the local kms, only for testing purpose.
    :return: Tuple: master key ARN, kms region, kms host name
    """
    kms = boto3.client('kms',
                       endpoint_url=kms_connection_url,
                       region_name='us-east-1',
                       aws_access_key_id='test',
                       aws_secret_access_key='test',
                       verify=False,
                       )
    kms_key = kms.create_key()
    return kms_key


@pytest.fixture
def create_data_key(master_key_kms, connect_database, kms_connection_url) -> Generator:
    """
    Creates data keys for testing purpose. It is required in order to use
    Explicit Client-Side Field Level Encryption (CSFLE)

    :param master_key_kms: Tuple: master key ARN, kms region, kms host name
    :return: None
    """
    # client = connect(host=DB_URI)

    key_name, key_coll = KEY_NAMESPACE.split(".", 1)

    key_vault = connect_database[key_name][key_coll]
    key_vault.drop()
    key_vault.create_index(
        "keyAltNames",
        unique=True,
        partialFilterExpression={"keyAltNames": {"$exists": True}},
    )

    with ClientEncryption(
        KMS_PROVIDER,
        KEY_NAMESPACE,
        connect_database,
        CodecOptions(uuid_representation=STANDARD),
    ) as client_encryption:
        client_encryption.create_data_key(
            'aws',
            key_alt_names=[KEY_NAME],
            master_key=dict(
                key=master_key_kms['KeyMetadata']['Arn'],
                region='us-east-1',
                endpoint=kms_connection_url
            ),
        )
    yield
    key_vault.drop()
