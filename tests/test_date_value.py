from src.domain.models.date import DateValue
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))


def test_valid_date():
    d = DateValue("2025-05-26")
    assert str(d) == "2025-05-26"


def test_invalid_format():
    with pytest.raises(ValueError) as e:
        DateValue("2025/05/26")
    assert "フォーマット" in str(e.value)


def test_nonexistent_date():
    with pytest.raises(ValueError) as e:
        DateValue("2025-02-30")
    assert "無効な日付" in str(e.value)
