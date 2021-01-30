from felmina import KGClient
from felmina.models.data import Entity


def test_create_entity(client: KGClient):
    data = {
        'entity_name': 'entity name',
        'entity_type': 'entity type',
        'properties': [
            {'name': 'name', 'value': 'value1'},
            {'name': 'name', 'value': 'value2'},
        ]
    }

    entity = Entity(**data)
    try:
        client.entity.add_entity(entity)

        _entity = client.entity.get_entity_by_id(entity.id)
        assert _entity.id == entity.id
        assert _entity.dict(exclude={'id', 'create_time'}) == data

    finally:
        if entity.id:
            client.entity.delete_entity_by_id(entity.id)
