import time
from urllib.parse import urlparse
from typing import Dict

class RequestThrottler:
    """
    ドメインごとのリクエスト間隔を制御するクラス
    """
    def __init__(self, policies: Dict[str, float]):
        self._policies = policies
        self._last_request_times: Dict[str, float] = {}

    def _get_domain(self, url: str) -> str:
        return urlparse(url).netloc

    def wait_if_needed(self, url: str, user_interval_sec: float = 0.0) -> None:
        domain = self._get_domain(url)
        system_min_interval = self._policies.get(domain, 0.0)
        effective_interval = max(system_min_interval, user_interval_sec)
        last_request_time = self._last_request_times.get(domain)
        now = time.monotonic()
        if last_request_time is not None:
            elapsed_time = now - last_request_time
            wait_time = effective_interval - elapsed_time
            if wait_time > 0:
                time.sleep(wait_time)
        # テスト容易性のため、nowを使う（2回呼ばない）
        self._last_request_times[domain] = now
