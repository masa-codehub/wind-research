import abc


class HtmlFetchingError(Exception):
    """HTML取得時に発生したエラーを示すカスタム例外"""
    pass


class IJmaPageFetcher(abc.ABC):
    @abc.abstractmethod
    def fetch(self, url: str, user_interval_sec: float) -> str:
        """
        指定されたURLからHTMLコンテンツを取得する。
        成功した場合はHTMLコンテンツ(str)を返す。
        ネットワークエラーやHTTPエラーは内部で捕捉し、HtmlFetchingErrorを発生させる。
        """
        raise NotImplementedError
