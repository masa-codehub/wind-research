import pytest
from src.domain.services.wind_data_converter import WindDataConverterService
from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_speed import WindSpeedValue

# 代表的なケースのテスト


def test_convert_wind_direction_from_text_valid():
    service = WindDataConverterService()
    result = service.convert_wind_direction_from_text("北西")
    assert isinstance(result, WindDirectionValue)
    assert result.degree == 315.0


def test_convert_wind_speed_from_text_valid():
    service = WindDataConverterService()
    result = service.convert_wind_speed_from_text("10.5")
    assert isinstance(result, WindSpeedValue)
    assert result.value_mps == 10.5


@pytest.mark.parametrize("text, expected_degree", [
    ("北", 0.0),
    ("南", 180.0),
    ("西", 270.0),
    ("静穏", -1.0),
    ("///", -1.0),
    ("未知の方向", -1.0),
    ("", -1.0),
    (None, -1.0)
])
def test_convert_wind_direction(text, expected_degree):
    service = WindDataConverterService()
    result = service.convert_wind_direction_from_text(text)
    assert result.degree == expected_degree


@pytest.mark.parametrize("text, expected_speed", [
    ("25.3", 25.3),
    ("10", 10.0),
    ("///", -1.0),
    ("abc", -1.0),
    ("", -1.0),
    (None, -1.0)
])
def test_convert_wind_speed(text, expected_speed):
    service = WindDataConverterService()
    result = service.convert_wind_speed_from_text(text)
    assert result.value_mps == expected_speed


def test_convert_wind_direction_nan_sei_no_kaze():
    from src.domain.services.wind_data_converter import WindDataConverterService
    service = WindDataConverterService()
    result = service.convert_wind_direction_from_text("南西の風")
    assert result.degree == -1.0
    assert result.direction == "欠損"
    assert result.original_text == "南西の風"
