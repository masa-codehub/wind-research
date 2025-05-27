import abc
from datetime import date
from src.domain.models.observation_point import ObservationPointValue


class IUrlBuilder(abc.ABC):
    @abc.abstractmethod
    def build_jma_10min_data_url(self, point: ObservationPointValue, target_date: date) -> str:
        """指定された観測地点と日付の10分値データページのURLを構築する"""
        raise NotImplementedError
