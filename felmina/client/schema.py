from hashlib import sha1
from typing import Optional

from elasticsearch import NotFoundError, ConflictError

from felmina.client.namespaced import IndexedClient
from felmina.models.data import SchemaType, SCHEMA_TYPE
from felmina.utils import get_current_datetime


class SchemaClient(IndexedClient):
    INDEX_PREFIX = 'felmina.schema'

    def _get_index_settings(self) -> dict:
        return {
            'mappings': {
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'schema_type': {
                        'type': 'keyword',
                    },
                    'created_time': {
                        'type': 'date',
                    }
                }
            }
        }

    def get_or_create_entity_type(self, name: str) -> SchemaType:
        return self._get_or_create_type(name, SCHEMA_TYPE.ENTITY)

    def get_or_create_relation_type(self, name: str) -> SchemaType:
        return self._get_or_create_type(name, SCHEMA_TYPE.RELATION)

    def get_or_create_property_type(self, name: str) -> SchemaType:
        return self._get_or_create_type(name, SCHEMA_TYPE.PROPERTY)

    def _get_or_create_type(self, name: str, schema_type: str) -> SchemaType:
        type_id = self.get_type_id(name, schema_type)
        _type = self.get_type_by_id(type_id)
        if _type is None:
            create_time = get_current_datetime()
            _type = SchemaType(
                id=type_id,
                name=name,
                schema_type=schema_type,
                create_time=create_time,
            )
            data = _type.dict()
            try:
                self.es.create(self.get_index(), type_id, body=data, refresh=True)
            except ConflictError:
                result = self.es.get(self.get_index(), type_id)
                _type = SchemaType(**result['_source'])
        return _type

    def get_type_id(self, name: str, schema_type: str) -> str:
        type_id = sha1(f'{schema_type}:{name}'.encode()).hexdigest()
        return type_id

    def get_type_by_id(self, type_id: str) -> Optional[SchemaType]:
        try:
            result = self.es.get(self.get_index(), type_id)
            return SchemaType(**result['_source'])
        except NotFoundError:
            pass

    def delete_type_by_id(self, type_id: str) -> bool:
        try:
            self.es.delete(self.get_index(), type_id)
        except NotFoundError:
            return False
        return True
