import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from datetime import datetime, date
from uuid import UUID
from src.domain.models.wind_data_record import WindDataRecord
from src.domain.models.observation_point import ObservationPointValue
from src.domain.models.wind_speed import WindSpeedValue
from src.domain.models.wind_direction import WindDirectionValue

class TestWindDataRecord:
    def test_create_valid(self):
        record = WindDataRecord(
            observed_at=datetime(2025, 5, 27, 10, 0),
            average_wind_direction=WindDirectionValue.from_text("北"),
            average_wind_speed=WindSpeedValue(5.0),
            max_wind_direction=WindDirectionValue.from_text("南"),
            max_wind_speed=WindSpeedValue(10.0),
        )
        assert record.average_wind_speed.value_mps == 5.0
        assert record.max_wind_direction.direction == "南"
        assert isinstance(record.id, UUID)

    def test_equality_id(self):
        record1 = WindDataRecord(
            observed_at=datetime(2025, 5, 27, 10, 0),
            average_wind_direction=WindDirectionValue.from_text("北"),
            average_wind_speed=WindSpeedValue(5.0),
            max_wind_direction=WindDirectionValue.from_text("南"),
            max_wind_speed=WindSpeedValue(10.0),
        )
        record2 = WindDataRecord(
            observed_at=datetime(2025, 5, 27, 10, 0),
            average_wind_direction=WindDirectionValue.from_text("北"),
            average_wind_speed=WindSpeedValue(5.0),
            max_wind_direction=WindDirectionValue.from_text("南"),
            max_wind_speed=WindSpeedValue(10.0),
        )
        assert record1 != record2  # UUIDが異なるため

    def test_id_is_uuid(self):
        record = WindDataRecord(
            observed_at=datetime(2025, 5, 27, 10, 0),
            average_wind_direction=WindDirectionValue.from_text("北"),
            average_wind_speed=WindSpeedValue(5.0),
            max_wind_direction=WindDirectionValue.from_text("南"),
            max_wind_speed=WindSpeedValue(10.0),
        )
        assert isinstance(record.id, UUID)
