import os

import pytest

from felmina import KGClient


@pytest.fixture
def client():
    hosts = os.environ.get('TEST_ES_HOSTS')
    if not hosts:
        hosts = 'localhost:9200'
    client = KGClient(hosts)
    yield client
