import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from dataclasses import FrozenInstanceError
from src.domain.models.wind_direction import WindDirectionValue

class TestWindDirectionValue:
    def test_from_text_valid_direction(self):
        wd = WindDirectionValue.from_text("北東")
        assert wd == WindDirectionValue(direction="北東", degree=45.0)

    def test_from_text_valid_degree(self):
        wd = WindDirectionValue.from_text("180")
        assert wd == WindDirectionValue(direction="南", degree=180.0)

    def test_from_text_calm(self):
        wd = WindDirectionValue.from_text("静穏")
        assert wd == WindDirectionValue(direction="静穏", degree=-1.0)

    def test_from_text_missing(self):
        wd = WindDirectionValue.from_text("///")
        assert wd == WindDirectionValue(direction="欠損", degree=-1.0)

    def test_from_text_invalid(self):
        wd = WindDirectionValue.from_text("abc")
        assert wd == WindDirectionValue(direction="欠損", degree=-1.0)

    def test_equality(self):
        wd1 = WindDirectionValue(direction="北", degree=0.0)
        wd2 = WindDirectionValue(direction="北", degree=0.0)
        assert wd1 == wd2

    def test_immutability(self):
        wd = WindDirectionValue(direction="北", degree=0.0)
        with pytest.raises(FrozenInstanceError):
            wd.degree = 90.0
