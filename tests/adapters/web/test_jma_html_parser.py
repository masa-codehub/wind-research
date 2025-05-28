import pytest
from pathlib import Path
from src.adapters.web.jma_html_parser import JmaHtmlParser
from src.usecases.ports.wind_data_parser_port import HtmlParsingError
from src.domain.dtos.raw_wind_data_dto import RawWindDataDto


@pytest.fixture
def sample_html():
    path = Path(__file__).parent.parent.parent / \
        "resources" / "sample_jma.html"
    return path.read_text(encoding="utf-8")


def sample_html_a1_p51_b1638_20240101():
    path = Path(__file__).parent.parent.parent / "resources" / \
        "sample_jma_a1_p51_b1638_20240101.html"
    return path.read_text(encoding="utf-8")


def test_parse_normal(sample_html):
    parser = JmaHtmlParser()
    result = parser.parse(sample_html)
    assert len(result) == 144
    assert result[0].time_str == "00:10"
    assert result[-1].time_str == "24:00"
    assert result[0].avg_wind_direction_str == "北北西"
    assert result[0].avg_wind_speed_str == "3.3"
    assert result[1].avg_wind_direction_str == "北北西"
    assert result[1].avg_wind_speed_str == "4.1"


def test_parse_normal_a1():
    parser = JmaHtmlParser()
    html = sample_html_a1_p51_b1638_20240101()
    result = parser.parse(html)
    assert len(result) == 3  # サンプルデータ行数に合わせて
    assert result[0].time_str == "00:10"
    assert result[-1].time_str == "24:00"
    assert result[0].avg_wind_direction_str == "北北西"
    assert result[0].avg_wind_speed_str == "3.3"
    assert result[1].avg_wind_direction_str == "北北西"
    assert result[1].avg_wind_speed_str == "4.1"


def test_parse_table_not_found():
    parser = JmaHtmlParser()
    html = "<html><body><table id='other'></table></body></html>"
    with pytest.raises(HtmlParsingError):
        parser.parse(html)


def test_parse_missing_column():
    parser = JmaHtmlParser()
    path = Path(__file__).parent.parent.parent / \
        "resources" / "sample_jma_no_wind_dir.html"
    html = path.read_text(encoding="utf-8")
    with pytest.raises(HtmlParsingError) as e:
        parser.parse(html)
    assert "avg_wind_direction_str" in str(e.value)
