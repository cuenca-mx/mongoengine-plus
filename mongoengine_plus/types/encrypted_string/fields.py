from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from mongoengine import get_connection
from mongoengine.base import BaseField
from pymongo.encryption import Algorithm, ClientEncryption

from .base import KEY_NAMESPACE, KMS_PROVIDER, get_data_key_binary

CODEC_OPTION = CodecOptions(uuid_representation=STANDARD)


class EncryptedString(BaseField):
    """
    Representa una cadena encriptada, soporta dos tipos de algoritmos:
    Deterministico y Random.
    """

    algorithm: Algorithm

    def __init__(self, algorithm: Algorithm, **kwargs):
        self.algorithm = algorithm
        super().__init__(**kwargs)

    def to_python(self, value):
        if value is None or isinstance(value, str):
            return value

        client = get_connection()

        with ClientEncryption(
            KMS_PROVIDER, KEY_NAMESPACE, client, CODEC_OPTION
        ) as client_encryption:
            return client_encryption.decrypt(value)

    def to_mongo(self, value):
        client = get_connection()
        data_key = get_data_key_binary()

        with ClientEncryption(
            KMS_PROVIDER, KEY_NAMESPACE, client, CODEC_OPTION
        ) as client_encryption:
            return client_encryption.encrypt(value, self.algorithm, data_key)

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(op, self.to_mongo(value))
