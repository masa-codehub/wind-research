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


def test_parse_normal(sample_html):
    parser = JmaHtmlParser()
    result = parser.parse(sample_html)
    # サンプルHTMLの仕様に応じて件数を調整
    assert len(result) == 144
    # 先頭・末尾の値を具体的に検証（例: 1行目と最終行）
    assert result[0].time_str == "00:10"
    assert result[-1].time_str == "24:00"
    # 先頭2件の風向・風速値も検証
    assert result[0].avg_wind_direction_str == "北北東"
    assert result[0].avg_wind_speed_str == "1.6"
    assert result[1].avg_wind_direction_str == "北北東"
    assert result[1].avg_wind_speed_str == "1.2"


def test_parse_table_not_found():
    parser = JmaHtmlParser()
    html = "<html><body><table id='other'></table></body></html>"
    with pytest.raises(HtmlParsingError):
        parser.parse(html)


def test_parse_missing_column(sample_html):
    parser = JmaHtmlParser()
    html = sample_html.replace("風向", "風向X")
    with pytest.raises(HtmlParsingError) as e:
        parser.parse(html)
    assert "不足列" in str(e.value)
    assert "風向" in str(e.value)  # 例: 不足列名が含まれる
