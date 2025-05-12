#tests/conftest.py

import pytest
from src.api.client import BookerClient
from src.config import settings


@pytest.fixture(scope="session")
def client():
    client = BookerClient()
    yield client
    client.close()

@pytest.fixture(scope="session")
def get_auth_token(client: BookerClient):
    auth_response = client.authenticate(settings.user_name, settings.password, settings.base_url)
    return auth_response.token