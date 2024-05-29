__all__ = ['EncryptedString', 'patch_kms_request']

import codecs
import os

import boto3
from pymongo.encryption import _EncryptionIO

from .fields import EncryptedString


def patch_kms_request():
    from .base import get_data_key

    data_key = get_data_key()
    kms = boto3.client(
        'kms',
        region_name=os.environ.get('KMS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ['KMS_AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['KMS_AWS_SECRET_ACCESS_KEY'],
        endpoint_url=f'https://{os.environ["KMS_ENDPOINT"]}/',
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
        f'"Plaintext":"{decrypted_data_key}"'
        '}'
    )

    content_length = len(content)

    # En las pruebas
    kms_response_template = (
        f'HTTP/1.1 200 OK\r\n'
        f'Content-Type: application/x-amz-json-1.1\r\n'
        f'Content-Length: {content_length}\r\n'
        f'Connection: close\r\n\r\n{content}'
    ).encode()

    def kms_request_with_cache(_, kms_context):
        kms_context.feed(kms_response_template)

    setattr(_EncryptionIO, 'kms_request', kms_request_with_cache)
