import pytest
import requests_mock
from src.adapters.web.jma_http_client import JmaHttpClient
from src.infrastructure import config


def test_get_request_includes_custom_user_agent():
    """GETリクエストにカスタムUser-Agentが含まれることを確認する"""
    client = JmaHttpClient()
    test_url = "https://www.jma.go.jp/test"

    with requests_mock.Mocker() as m:
        m.get(test_url, text="response")
        client.get(test_url)
        history = m.request_history
        assert len(history) == 1
        request_headers = history[0].headers
        assert "User-Agent" in request_headers
        assert request_headers["User-Agent"] == config.USER_AGENT
