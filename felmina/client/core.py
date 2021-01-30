from typing import Optional

from elasticsearch import Elasticsearch
from werkzeug.local import LocalStack


class KGClient:
    DEFAULT_KG_ID = 'default'

    def __init__(self, es_hosts, es_client_factory=None):
        if es_client_factory is None:
            self.es = Elasticsearch(es_hosts)
        else:
            self.es = es_client_factory()

        from felmina.client.entity import EntityClient
        from felmina.client.relation import RelationClient
        from felmina.client.schema import SchemaClient

        self.entity = EntityClient(self)
        self.relation = RelationClient(self)
        self.schema = SchemaClient(self)

    def use(self, kg_id: str):
        return KGContext(self, kg_id)

    def current_kg_id(self) -> Optional[str]:
        top: KGContext = _client_ctx_stack.top
        if top is None:
            return
        return top.kg_id

    def _entity_type_id_to_name(self, entity_type_id: str):
        pass

    def _entity_type_name_to_id(self, entity_type_name: str, auto_create=True):
        pass

    def _property_type_id_to_name(self, property_type_id: str):
        pass

    def _property_type_name_to_id(self, property_type_name: str, auto_create=True):
        pass

    def _relation_type_id_to_name(self, relation_type_id: str):
        pass

    def _relation_type_name_to_id(self, relation_type_name: str, auto_create=True):
        pass


_client_ctx_stack = LocalStack()


class KGContext:
    def __init__(self, client: KGClient, kg_id: str):
        self.client = client
        self.kg_id = kg_id

    def push(self):
        _client_ctx_stack.push(self)

    def pop(self):
        _client_ctx_stack.pop()

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()
