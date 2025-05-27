import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from dataclasses import FrozenInstanceError
from src.domain.models.wind_speed import WindSpeedValue

class TestWindSpeedValue:
    def test_from_text_valid(self):
        ws = WindSpeedValue.from_text("10.5")
        assert ws == WindSpeedValue(10.5)

    def test_from_text_missing(self):
        ws = WindSpeedValue.from_text("///")
        assert ws == WindSpeedValue(-1.0)

    def test_from_text_invalid(self):
        ws = WindSpeedValue.from_text("abc")
        assert ws == WindSpeedValue(-1.0)

    def test_from_text_negative(self):
        ws = WindSpeedValue.from_text("-5.0")
        assert ws == WindSpeedValue(-1.0)

    def test_equality(self):
        ws1 = WindSpeedValue(1.0)
        ws2 = WindSpeedValue(1.0)
        assert ws1 == ws2

    def test_immutability(self):
        ws = WindSpeedValue(2.0)
        with pytest.raises(FrozenInstanceError):
            ws.value_mps = 3.0
