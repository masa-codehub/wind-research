from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_speed import WindSpeedValue

@dataclass
class WindDataRecord:
    """
    風データ記録エンティティ。IDで一意識別。
    """
    observed_at: datetime
    average_wind_direction: WindDirectionValue
    average_wind_speed: WindSpeedValue
    max_wind_direction: WindDirectionValue
    max_wind_speed: WindSpeedValue
    id: UUID = field(default_factory=uuid4)
