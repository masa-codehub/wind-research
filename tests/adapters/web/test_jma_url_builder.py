from datetime import date
from src.domain.models.observation_point import ObservationPointValue
from src.adapters.web.jma_url_builder import JmaUrlBuilder
import pytest


def test_build_url_correctly():
    # Arrange
    builder = JmaUrlBuilder()
    point = ObservationPointValue(prefecture_no="44", block_no="47662")
    target_date = date(2024, 5, 27)

    # Act
    actual_url = builder.build_jma_10min_data_url(point, target_date)

    # Assert
    expected_url = "https://www.data.jma.go.jp/stats/etrn/view/10min_s1.php?prec_no=44&block_no=47662&year=2024&month=05&day=27&view=p1"
    assert actual_url == expected_url


def test_build_url_zero_padding():
    builder = JmaUrlBuilder()
    point = ObservationPointValue(prefecture_no="01", block_no="47401")
    target_date = date(2024, 1, 5)
    actual_url = builder.build_jma_10min_data_url(point, target_date)
    expected_url = "https://www.data.jma.go.jp/stats/etrn/view/10min_s1.php?prec_no=01&block_no=47401&year=2024&month=01&day=05&view=p1"
    assert actual_url == expected_url
