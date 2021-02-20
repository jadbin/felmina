from felmina import KGClient
from felmina.schema.data import Entity, Relation
from tests.test_client.utils import wait_index


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
            _delete_relation(client, relation)


def test_find_neighbors(client: KGClient):
    r1 = 'some relation type'
    r2 = 'another relation type'
    e1 = 'some entity'
    e2 = 'another entity'

    entity1 = Entity(entity_name=e1)
    entity2 = Entity(entity_name=e2)
    client.entity.add_entity(entity1)
    client.entity.add_entity(entity2)
    client.entity.flush_index()

    relation1 = Relation(start_entity_id=entity1.id, relation_type=r1, end_entity_id=entity2.id)
    relation2 = Relation(start_entity_id=entity2.id, relation_type=r2, end_entity_id=entity1.id)
    client.relation.add_relation(relation1)
    client.relation.add_relation(relation2)
    client.relation.flush_index()

    wait_index()

    relations = client.relation.get_relations_start_from(entity_id=entity1.id)
    assert len(relations) == 1 and relations[0].id == relation1.id
    relations = client.relation.get_relations_end_to(entity_id=entity1.id)
    assert len(relations) == 1 and relations[0].id == relation2.id
    relations = client.relation.get_relations_related_to(entity_id=entity1.id)
    assert len(relations) == 2 and {relations[0].id, relations[1].id} == {relation1.id, relation2.id}

    client.entity.delete_entity_by_id(entity1.id)
    client.entity.delete_entity_by_id(entity2.id)
    _delete_relation(client, relation1)
    _delete_relation(client, relation2)


def _delete_relation(client: KGClient, relation: Relation):
    client.relation.delete_relation_by_id(
        client.relation.get_relation_id(
            relation.start_entity_id,
            relation.relation_type,
            relation.end_entity_id,
        )
    )
