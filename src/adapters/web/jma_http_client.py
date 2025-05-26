import requests
from requests import Session
from src.infrastructure import config


class JmaHttpClient:
    def __init__(self):
        self.session: Session = self._create_session()

    def _create_session(self) -> Session:
        """User-Agentが設定されたrequests.Sessionを生成する"""
        session = requests.Session()
        session.headers.update({"User-Agent": config.USER_AGENT})
        return session

    def get(self, url: str, **kwargs) -> requests.Response:
        """指定されたURLからGETリクエストでコンテンツを取得する"""
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response


jma_http_client = JmaHttpClient()
