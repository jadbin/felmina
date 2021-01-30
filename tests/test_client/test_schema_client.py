from felmina import KGClient


def test_create_schema(client: KGClient):
    entity_type_name = 'test_entity_type'
    _type = None

    try:
        _type = client.schema.get_or_create_entity_type(entity_type_name)

        result = client.schema.get_type_by_id(_type.id)
        assert result.dict() == _type.dict()
    finally:
        if _type:
            client.schema.delete_type_by_id(_type.id)
