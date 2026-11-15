
import pytest
import respx

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def merchant_1_headers():
    return {
        "Authorization": "Bearer fashion_token_123"
    }


@pytest.fixture
def merchant_2_headers():
    return {
        "Authorization": "Bearer electronics_token_456"
    }


@pytest.fixture
def orphan_headers():
    return {
        "Authorization": "Bearer orphan_token_589"
    }


@pytest.fixture
def mock_store_api():
    with respx.mock(assert_all_called=False) as mock:
        yield mock
