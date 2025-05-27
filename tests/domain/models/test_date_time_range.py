import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from dataclasses import FrozenInstanceError
from datetime import date
from src.domain.models.date_time_range import DateTimeRangeValue

class TestDateTimeRangeValue:
    def test_create_valid(self):
        rng = DateTimeRangeValue(start_date=date(2025, 5, 1), end_date=date(2025, 5, 31))
        assert rng.start_date == date(2025, 5, 1)
        assert rng.end_date == date(2025, 5, 31)

    def test_start_after_end_raises(self):
        with pytest.raises(ValueError):
            DateTimeRangeValue(start_date=date(2025, 6, 1), end_date=date(2025, 5, 31))

    def test_equality(self):
        r1 = DateTimeRangeValue(start_date=date(2025, 5, 1), end_date=date(2025, 5, 31))
        r2 = DateTimeRangeValue(start_date=date(2025, 5, 1), end_date=date(2025, 5, 31))
        assert r1 == r2

    def test_immutability(self):
        rng = DateTimeRangeValue(start_date=date(2025, 5, 1), end_date=date(2025, 5, 31))
        with pytest.raises(FrozenInstanceError):
            rng.start_date = date(2025, 5, 2)
