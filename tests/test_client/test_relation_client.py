from felmina import KGClient
from felmina.models.data import Entity, Relation


def test_create_relation(client: KGClient):
    r = 'some relation type'
    e1 = 'some entity'
    e2 = 'another entity'

    entity1 = Entity(entity_name=e1)
    entity2 = Entity(entity_name=e2)
    relation = None

    try:
        client.entity.add_entity(entity1)
        client.entity.add_entity(entity2)
        relation = Relation(start_entity_id=entity1.id, relation_type=r, end_entity_id=entity2.id)
        client.relation.add_relation(relation)
        _relation = client.relation.get_relation_by_id(relation.id)
        assert _relation.id == relation.id
        assert _relation.start_entity_id == entity1.id
        assert _relation.relation_type == r
        assert _relation.end_entity_id == entity2.id
    finally:
        if entity1.id:
            client.entity.delete_entity_by_id(entity1.id)
        if entity2.id:
            client.entity.delete_entity_by_id(entity2.id)
        if relation:
            client.relation.delete_relation_by_id(
                client.relation.get_relation_id(
                    relation.start_entity_id,
                    relation.relation_type,
                    relation.end_entity_id,
                )
            )
