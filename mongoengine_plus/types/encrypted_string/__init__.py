__all__ = ['EncryptedStringField', 'cache_kms_data_key']

import codecs

import boto3
from pymongo.encryption import _EncryptionIO

from .fields import EncryptedStringField


def cache_kms_data_key(
    key_namespace: str,
    key_name: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_region_name: str,
    kms_endpoint_url: str,
) -> None:
    """
    Retrieve the KMS Key used to encrypt and decrypt data and creates a cache
    to optimize the usage of `EncryptedString`. You should execute this
    function once before making any database write or read operations
    """
    from .base import get_data_key

    data_key = get_data_key(
        key_namespace,
        key_name,
    )
    kms = boto3.client(
        'kms',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region_name,
        endpoint_url=kms_endpoint_url,
    )
    response = kms.decrypt(
        CiphertextBlob=data_key['keyMaterial'],
    )
    decrypted_data_key = codecs.encode(
        response['Plaintext'], 'base64'
    ).decode()
    decrypted_data_key = decrypted_data_key.replace('\n', '\\n')
    content = (
        '{'
        '"EncryptionAlgorithm":"SYMMETRIC_DEFAULT",'
        f'"Plaintext": "{decrypted_data_key}"'
        '}'
    )

    content_length = len(content)

    kms_response_template = (
        f'HTTP/1.1 200 OK\r\n'
        f'Content-Type: application/x-amz-json-1.1\r\n'
        f'Content-Length: {content_length}\r\n'
        f'Connection: close\r\n\r\n{content}'
    ).encode()

    def kms_request_with_cache(_, kms_context):
        kms_context.feed(kms_response_template)

    setattr(_EncryptionIO, 'kms_request', kms_request_with_cache)
