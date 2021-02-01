from typing import Optional

from elasticsearch import Elasticsearch
from werkzeug.local import LocalStack


class KGClient:
    DEFAULT_KG_ID = 'default'

    def __init__(self, es_hosts, kg_id=None, es_client_factory=None):
        if es_client_factory is None:
            self.es = Elasticsearch(es_hosts)
        else:
            self.es = es_client_factory()
        if kg_id is None:
            self.default_kg_id = self.DEFAULT_KG_ID
        else:
            self.default_kg_id = kg_id

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
