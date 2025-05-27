from src.domain.models.wind_speed import WindSpeedValue
from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_data_record import WindDataRecord
from src.domain.models.observation_point import ObservationPointValue
from src.domain.models.daily_wind_report import DailyWindReport
from uuid import UUID
from datetime import date, datetime
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../')))


class TestDailyWindReport:
    def setup_method(self):
        self.observation_point = ObservationPointValue(
            prefecture_no="01", block_no="1234")
        self.report_date = date(2025, 5, 27)
        self.report = DailyWindReport(
            observation_point=self.observation_point, report_date=self.report_date)

    def test_create_valid(self):
        assert self.report.observation_point == self.observation_point
        assert self.report.report_date == self.report_date
        assert isinstance(self.report.id, UUID)
        assert self.report.records == []

    def test_add_record(self):
        self.report.add_record(
            observed_at=datetime.combine(
                self.report_date, datetime.min.time()),
            average_wind_direction=WindDirectionValue.from_text("北"),
            average_wind_speed=WindSpeedValue(5.0),
            max_wind_direction=WindDirectionValue.from_text("南"),
            max_wind_speed=WindSpeedValue(10.0),
        )
        assert len(self.report.records) == 1
        assert isinstance(self.report.records[0], WindDataRecord)

    def test_add_record_over_limit(self):
        for _ in range(144):
            self.report.add_record(
                observed_at=self.report_date,
                average_wind_direction=WindDirectionValue.from_text("北"),
                average_wind_speed=WindSpeedValue(5.0),
                max_wind_direction=WindDirectionValue.from_text("南"),
                max_wind_speed=WindSpeedValue(10.0),
            )
        with pytest.raises(ValueError):
            self.report.add_record(
                observed_at=self.report_date,
                average_wind_direction=WindDirectionValue.from_text("北"),
                average_wind_speed=WindSpeedValue(5.0),
                max_wind_direction=WindDirectionValue.from_text("南"),
                max_wind_speed=WindSpeedValue(10.0),
            )

    def test_records_are_copied(self):
        self.report.add_record(
            observed_at=self.report_date,
            average_wind_direction=WindDirectionValue.from_text("北"),
            average_wind_speed=WindSpeedValue(5.0),
            max_wind_direction=WindDirectionValue.from_text("南"),
            max_wind_speed=WindSpeedValue(10.0),
        )
        records = self.report.records
        records.append("dummy")
        assert len(self.report.records) == 1  # 内部リストは不変

    def test_equality_id(self):
        report2 = DailyWindReport(
            observation_point=self.observation_point, report_date=self.report_date)
        assert self.report != report2  # UUIDが異なるため
