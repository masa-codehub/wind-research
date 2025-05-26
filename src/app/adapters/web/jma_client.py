from .throttler import RequestThrottler
from .config import ACCESS_POLICIES
import requests

class JmaPageFetcher:
    """
    気象庁ページ取得用クライアント。リクエストスロットリングを内包。
    """
    def __init__(self):
        self._throttler = RequestThrottler(ACCESS_POLICIES)

    def fetch(self, url: str, user_interval_sec: float = 0.0) -> str:
        self._throttler.wait_if_needed(url, user_interval_sec)
        response = requests.get(url)
        response.raise_for_status()
        return response.text
