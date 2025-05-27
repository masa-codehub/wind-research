import requests
import logging
from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher, HtmlFetchingError
from src.app.adapters.web.throttler import RequestThrottler
from src.app.adapters.web.config import ACCESS_POLICIES
from src.infrastructure.config import USER_AGENT

logger = logging.getLogger(__name__)


class JmaPageFetcherAdapter(IJmaPageFetcher):
    def __init__(self, user_agent: str = None):
        self._throttler = RequestThrottler(ACCESS_POLICIES)
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent or USER_AGENT})

    def fetch(self, url: str, user_interval_sec: float = 5.0) -> str:
        try:
            self._throttler.wait_if_needed(url, user_interval_sec)
            logger.info(f"Fetching HTML from: {url}")
            response = self._session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to fetch HTML from {url}. Error: {e}", exc_info=True)
            raise HtmlFetchingError(f"HTML取得に失敗しました: {url}") from e
