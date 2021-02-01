import datetime as dt
import uuid
from typing import List, Optional

from elasticsearch import NotFoundError
from elasticsearch.helpers import bulk

from felmina.client.namespaced import IndexedClient
from felmina.models.data import Entity


class EntityClient(IndexedClient):
    INDEX_PREFIX = 'felmina.entity'

    def _get_index_settings(self) -> dict:
        return {
            'mappings': {
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'entity_type': {
                        'type': 'keyword',
                    },
                    'properties': {
                        'type': 'nested',
                        'properties': {
                            'name': {
                                'type': 'text',
                                'fields': {
                                    'keyword': {
                                        'type': 'keyword',
                                        'ignore_above': 256,
                                    }
                                }
                            },
                            'value': {
                                'type': 'text',
                                'fields': {
                                    'keyword': {
                                        'type': 'keyword',
                                        'ignore_above': 256,
                                    }
                                }
                            }
                        },
                    },
                    'create_time': {
                        'type': 'date',
                    }
                }
            }
        }

    def add_entity(self, entity: Entity):
        self._init_new_entity(entity)
        data = entity.dict()
        self.es.index(self.get_index(), body=data, id=entity.id)

    def add_entities(self, entities: List[Entity]):
        for entity in entities:
            self._init_new_entity(entity)
        data = [{
            '_op_type': 'index',
            '_index': self.get_index(),
            '_id': entity.id,
            '_source': entity.dict()
        } for entity in entities]
        bulk(self.es, data)

    def _init_new_entity(self, entity: Entity):
        if not entity.id:
            entity.id = uuid.uuid4().hex
        if not entity.properties:
            entity.properties = []
        entity.create_time = dt.datetime.now()
        entity.kg_id = self.client.current_kg_id()

    def delete_entity_by_id(self, entity_id: str) -> bool:
        try:
            self.es.delete(self.get_index(), entity_id)
        except NotFoundError:
            return False
        return True

    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        try:
            result = self.es.get(self.get_index(), entity_id)
            return Entity(**result['_source'])
        except NotFoundError:
            pass

    def count_entities(self) -> int:
        resp = self.es.count(index=self.get_index())
        return resp['count']

    def search_entities(self, query_body: dict) -> List[Entity]:
        result = self.es.search(body=query_body, index=self.get_index())
        hits = result['hits']['hits']
        entities = [Entity(**h['_source']) for h in hits]
        return entities
