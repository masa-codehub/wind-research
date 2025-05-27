import abc
from typing import List
from src.domain.models.wind_data_record import WindDataRecord


class FileOutputError(Exception):
    """ファイル出力に失敗した場合のカスタム例外"""
    pass


class IWindDataOutputPort(abc.ABC):
    @abc.abstractmethod
    def save(self, records: List[WindDataRecord], output_path: str | None) -> str:
        """
        指定されたレコードを永続化し、実際に保存されたパスを返す。
        output_pathがNoneの場合はデフォルトパスに保存する。
        """
        raise NotImplementedError
