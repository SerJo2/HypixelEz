import os
import pytest

from dotenv import load_dotenv
from src.hypixelez import hypixel_api, HypixelClient
import src.hypixelez.logger

load_dotenv()

@pytest.fixture
def api_key():
    key = os.getenv("API_KEY")
    if not key:
        pytest.skip("Key is not set up")
    return key

@pytest.fixture
def api_client(api_key):
    client = HypixelClient(api_key)
    # Добавить таймаут для тестов
    client.session.timeout = 5
    return client

