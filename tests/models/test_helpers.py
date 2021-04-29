from mongoengine_plus.models.helpers import uuid_field


def test_uuid_field_generator():
    prefix = 'PK'
    create_id = uuid_field(prefix)
    custom_id = create_id()
    custom_id.startswith(prefix)
    assert len(custom_id) == 24