import pytest
import requests
import requests_mock
from src.adapters.web.jma_page_fetcher_adapter import JmaPageFetcherAdapter
from src.usecases.ports.jma_page_fetcher_port import HtmlFetchingError


class DummyThrottler:
    def wait_if_needed(self, url, user_interval_sec):
        self.called = True
        self.url = url
        self.interval = user_interval_sec


@pytest.fixture
def patch_throttler(monkeypatch):
    # Throttlerをダミーに差し替え
    from src.adapters.web import jma_page_fetcher_adapter
    dummy = DummyThrottler()
    monkeypatch.setattr(jma_page_fetcher_adapter,
                        "RequestThrottler", lambda policies: dummy)
    return dummy


@pytest.fixture
def patch_user_agent(monkeypatch):
    # USER_AGENTをテスト用に差し替え
    monkeypatch.setattr("src.infrastructure.config.USER_AGENT", "pytest-agent")


def test_fetch_success(requests_mock, patch_throttler, patch_user_agent):
    url = "https://data.jma.go.jp/test"
    html = "<html>ok</html>"
    requests_mock.get(url, text=html)
    fetcher = JmaPageFetcherAdapter()
    result = fetcher.fetch(url, user_interval_sec=1.0)
    assert result == html
    assert patch_throttler.called
    assert patch_throttler.url == url
    assert patch_throttler.interval == 1.0


def test_fetch_http_error(requests_mock, patch_throttler, patch_user_agent):
    url = "https://data.jma.go.jp/404"
    requests_mock.get(url, status_code=404)
    fetcher = JmaPageFetcherAdapter()
    with pytest.raises(HtmlFetchingError):
        fetcher.fetch(url, user_interval_sec=1.0)


def test_fetch_network_error(monkeypatch, patch_throttler, patch_user_agent):
    url = "https://data.jma.go.jp/timeout"

    def raise_conn_error(*a, **k):
        raise requests.ConnectionError("fail")
    monkeypatch.setattr(requests.Session, "get", raise_conn_error)
    fetcher = JmaPageFetcherAdapter()
    with pytest.raises(HtmlFetchingError):
        fetcher.fetch(url, user_interval_sec=1.0)


def test_user_agent_header(requests_mock, patch_throttler, patch_user_agent):
    url = "https://data.jma.go.jp/ua"
    html = "<html>ua</html>"
    matcher = requests_mock.get(url, text=html)
    fetcher = JmaPageFetcherAdapter(user_agent="pytest-agent")
    fetcher.fetch(url, user_interval_sec=1.0)
    assert matcher.last_request.headers["User-Agent"] == "pytest-agent"
