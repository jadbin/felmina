from hashlib import sha1
from typing import List, Optional

from elasticsearch import NotFoundError
from elasticsearch.helpers import bulk

from felmina.client.namespaced import IndexedClient
from felmina.models.data import Relation
from felmina.utils import get_current_datetime


class RelationClient(IndexedClient):
    INDEX_PREFIX = 'felmina.relation'

    def _get_index_settings(self) -> dict:
        return {
            'mappings': {
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'relation_type': {
                        'type': 'keyword',
                    },
                    'start_entity_id': {
                        'type': 'keyword',
                    },
                    'start_entity_kg_id': {
                        'type': 'keyword',
                    },
                    'end_entity_id': {
                        'type': 'keyword',
                    },
                    'end_entity_kg_id': {
                        'type': 'keyword',
                    },
                    'created_time': {
                        'type': 'date',
                    }
                }
            }
        }

    def get_relation_id(self, start_entity_id: str, relation_type: str, end_entity_id: str):
        relation_id = sha1(f'{start_entity_id}:{relation_type}:{end_entity_id}'.encode()).hexdigest()
        return relation_id

    def delete_entity_relations(self, entity_id: str):
        q = {
            'query': {
                'bool': {
                    'should': [
                        {'term': {'start_entity_id': entity_id}},
                        {'term': {'end_entity_id': entity_id}},
                    ]
                }
            }
        }
        self.es.delete_by_query(self.get_index(), body=q)

    def delete_relations_start_from(self, entity_id: str):
        q = {
            'query': {
                'term': {
                    'start_entity_id': entity_id,
                }
            }
        }
        self.es.delete_by_query(self.get_index(), body=q)

    def delete_relations_end_to(self, entity_id: str):
        q = {
            'query': {
                'term': {
                    'end_entity_id': entity_id,
                }
            }
        }
        self.es.delete_by_query(self.get_index(), body=q)

    def add_relation(self, relation: Relation):
        relation.id = self.get_relation_id(
            relation.start_entity_id,
            relation.relation_type,
            relation.end_entity_id,
        )
        relation.create_time = get_current_datetime()

        data = relation.dict()
        self.es.index(self.get_index(), body=data, id=relation.id)

    def add_relations(self, relations: List[Relation]):
        for r in relations:
            r.id = self.get_relation_id(r.start_entity_id, r.relation_type, r.end_entity_id)
            r.create_time = get_current_datetime()

        data = [{
            '_op_type': 'index',
            '_index': self.get_index(),
            '_id': r.id,
            '_source': r.dict(),
        } for r in relations]
        bulk(self.es, data)

    def delete_relation_by_id(self, relation_id: str) -> bool:
        try:
            self.es.delete(self.get_index(), relation_id)
        except NotFoundError:
            return False
        return True

    def get_relation_by_id(self, relation_id: str) -> Optional[Relation]:
        try:
            result = self.es.get(self.get_index(), relation_id)
            return Relation(**result['_source'])
        except NotFoundError:
            pass

    def get_relations_start_from(self, entity_id: str, max_count: int = 1000) -> List[Relation]:
        q = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'term': {'end_entity_id': entity_id},
                        },
                    ]
                }
            },
            'size': max_count,
        }

        result = self.es.search(body=q, index=self.get_index())
        hits = result['hits']['hits']
        relations = [Relation(**h['_source']) for h in hits]
        return relations

    def get_relations_end_from(self, entity_id: str, max_count: int = 1000) -> List[Relation]:
        q = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'term': {'start_entity_id': entity_id},
                        },
                    ]
                }
            },
            'size': max_count,
        }

        result = self.es.search(body=q, index=self.get_index())
        hits = result['hits']['hits']
        relations = [Relation(**h['_source']) for h in hits]
        return relations

    def get_relations_related_to(self, entity_id: str, max_count: int = 1000) -> List[Relation]:
        q = {
            'query': {
                'bool': {
                    'should': [
                        {
                            'term': {'start_entity_id': entity_id},
                        },
                        {
                            'term': {'end_entity_id': entity_id},
                        },
                    ]
                }
            },
            'size': max_count,
        }

        result = self.es.search(body=q, index=self.get_index())
        hits = result['hits']['hits']
        relations = [Relation(**h['_source']) for h in hits]
        return relations

    def count_relations(self) -> int:
        resp = self.es.count(index=self.get_index())
        return resp['count']
