import abc
from typing import List
from src.domain.dtos.raw_wind_data_dto import RawWindDataDto


class HtmlParsingError(Exception):
    """HTML解析に失敗した場合のカスタム例外"""
    pass


class IWindDataParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, html_content: str) -> List[RawWindDataDto]:
        """HTMLコンテンツを解析し、生データのDTOリストを返す"""
        raise NotImplementedError
