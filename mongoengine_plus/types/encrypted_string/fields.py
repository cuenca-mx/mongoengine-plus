from typing import Any, ClassVar, Dict

from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from mongoengine import get_connection
from mongoengine.base import BaseField
from pymongo.encryption import Algorithm, ClientEncryption

from .base import get_data_key_binary

CODEC_OPTION = CodecOptions(uuid_representation=STANDARD)


class EncryptedStringField(BaseField):
    """
    Represents an encrypted string. Supports two types of
    encryption algorithms: Deterministic and Random.
    """

    kms_provider: ClassVar[Dict[str, Any]]
    key_namespace: ClassVar[str]
    key_name: ClassVar[str]
    _aws_access_key_id: ClassVar[str]
    _aws_secret_access_key: ClassVar[str]
    aws_region_name: ClassVar[str]

    algorithm: Algorithm

    def __init__(self, algorithm: Algorithm, **kwargs) -> None:
        self.algorithm = algorithm
        super().__init__(**kwargs)

    @classmethod
    def configure_aws_kms(
        cls,
        key_namespace: str,
        key_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region_name: str,
    ) -> None:
        cls.key_namespace = key_namespace
        cls.key_name = key_name
        cls._aws_access_key_id = aws_access_key_id
        cls._aws_secret_access_key = aws_secret_access_key
        cls.aws_region_name = aws_region_name
        cls.kms_provider = dict(
            aws=dict(
                accessKeyId=aws_access_key_id,
                secretAccessKey=aws_secret_access_key,
            )
        )

    def to_python(self, value: Any) -> Any:
        if value is None or isinstance(value, str):
            return value

        connection = get_connection()

        with ClientEncryption(
            self.kms_provider, self.key_namespace, connection, CODEC_OPTION
        ) as client_encryption:
            return client_encryption.decrypt(value)

    def to_mongo(self, value: Any) -> Any:
        connection = get_connection()
        data_key = get_data_key_binary(self.key_namespace, self.key_name)

        with ClientEncryption(
            self.kms_provider, self.key_namespace, connection, CODEC_OPTION
        ) as client_encryption:
            return client_encryption.encrypt(value, self.algorithm, data_key)

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(op, self.to_mongo(value))
