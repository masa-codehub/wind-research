from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4
from typing import List
from src.domain.models.observation_point import ObservationPointValue
from src.domain.models.wind_data_record import WindDataRecord
from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_speed import WindSpeedValue

@dataclass
class DailyWindReport:
    observation_point: ObservationPointValue
    report_date: date
    id: UUID = field(default_factory=uuid4)
    _records: List[WindDataRecord] = field(default_factory=list, init=False, repr=False)

    def add_record(self, observed_at: datetime, average_wind_direction: WindDirectionValue,
                   average_wind_speed: WindSpeedValue, max_wind_direction: WindDirectionValue,
                   max_wind_speed: WindSpeedValue) -> None:
        if len(self._records) >= 144:
            raise ValueError("1日に追加できる観測データは144件までです。")
        record = WindDataRecord(
            observed_at=observed_at,
            average_wind_direction=average_wind_direction,
            average_wind_speed=average_wind_speed,
            max_wind_direction=max_wind_direction,
            max_wind_speed=max_wind_speed
        )
        self._records.append(record)

    @property
    def records(self) -> List[WindDataRecord]:
        return list(self._records)
