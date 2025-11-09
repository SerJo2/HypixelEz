import os
import pytest
from unittest.mock import Mock

from dotenv import load_dotenv
from src.hypixelez import hypixel_api, HypixelClient
import src.hypixelez.logger
from unittest.mock import patch

load_dotenv()


@pytest.fixture
def api_key():
    key = os.getenv("API_KEY")
    if not key:
        pytest.skip("API_KEY is not set up")
    return key


@pytest.fixture
def api_client(api_key):
    return HypixelClient(api_key)


@pytest.fixture
def mock_profile_data():
    """Fixture providing mock profile data"""
    from .mocks import MOCK_PROFILE_DATA
    from src.hypixelez.hypixel_api import SkyblockProfileData

    return SkyblockProfileData(MOCK_PROFILE_DATA, "eca19e2e713d49a98582320229f696ed")


@pytest.fixture
def mock_requests():
    """Fixture to mock requests"""
    with (
        patch("requests.get") as mock_get,
        patch("requests.Session.get") as mock_session_get,
    ):
        yield {"get": mock_get, "session_get": mock_session_get}
