import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from dataclasses import FrozenInstanceError
from src.domain.models.observation_point import ObservationPointValue

class TestObservationPointValue:
    def test_create_valid(self):
        op = ObservationPointValue(prefecture_no="01", block_no="1234")
        assert op.prefecture_no == "01"
        assert op.block_no == "1234"

    def test_empty_prefecture_no_raises(self):
        with pytest.raises(ValueError):
            ObservationPointValue(prefecture_no="", block_no="1234")

    def test_empty_block_no_raises(self):
        with pytest.raises(ValueError):
            ObservationPointValue(prefecture_no="01", block_no="")

    def test_equality(self):
        op1 = ObservationPointValue(prefecture_no="01", block_no="1234")
        op2 = ObservationPointValue(prefecture_no="01", block_no="1234")
        assert op1 == op2

    def test_immutability(self):
        op = ObservationPointValue(prefecture_no="01", block_no="1234")
        with pytest.raises(FrozenInstanceError):
            op.prefecture_no = "02"
