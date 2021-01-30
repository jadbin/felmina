from abc import abstractmethod, ABCMeta

from elasticsearch import Elasticsearch

from felmina.client.core import KGClient


class NamespacedClient:
    def __init__(self, client: KGClient):
        self.client = client

    @property
    def es(self) -> Elasticsearch:
        return self.client.es


class IndexedClient(NamespacedClient, metaclass=ABCMeta):
    INDEX_PREFIX: str

    def __init__(self, client: KGClient):
        super().__init__(client)

        self.index_exists = set()

    def get_index(self, kg_id: str = None, auto_create=True):
        if kg_id is None:
            kg_id = self.client.current_kg_id() or self.client.DEFAULT_KG_ID
        index = f'{self.INDEX_PREFIX}.{kg_id}'

        if auto_create and index not in self.index_exists:
            if not self.es.indices.exists(index):
                self.init_index(index)
            self.index_exists.add(index)

        return index

    def init_index(self, index: str):
        self.es.indices.create(index, body=self._get_index_settings(), ignore=400)

    @abstractmethod
    def _get_index_settings(self) -> dict:
        pass
