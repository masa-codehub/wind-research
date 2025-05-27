import pytest
from unittest.mock import Mock, patch
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher, HtmlFetchingError
from src.adapters.web.jma_url_builder import JmaUrlBuilder
from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_speed import WindSpeedValue


class DummyConverter:
    def convert_wind_direction_from_text(self, raw):
        return WindDirectionValue.from_text("北")

    def convert_wind_speed_from_text(self, raw):
        return WindSpeedValue(1.0)


@pytest.fixture
def patch_converter(monkeypatch):
    monkeypatch.setattr(
        "src.usecases.collect_wind_data_usecase.WindDataConverterService", lambda: DummyConverter())


@pytest.fixture
def mock_url_builder():
    mock_builder = Mock(spec=JmaUrlBuilder)
    mock_builder.build_jma_10min_data_url.return_value = "http://dummy.url/for/date"
    return mock_builder


def test_execute_fetch_error_logs_and_skips(mock_url_builder, caplog, patch_converter):
    fetcher_mock = Mock(spec=IJmaPageFetcher)
    fetcher_mock.fetch.side_effect = HtmlFetchingError(
        "Simulated fetch failure")
    usecase = CollectWindDataUsecase(
        parser=Mock(),
        page_fetcher=fetcher_mock, url_builder=mock_url_builder,
        logger=None
    )
    input_data = CollectWindDataInput("01", "001", "2025-05-27", 2)
    usecase.execute(input_data)
    assert fetcher_mock.fetch.call_count == 2
    skipped_dates = ["2025-05-27", "2025-05-28"]
    for record in caplog.records:
        if record.levelname == "WARNING":
            assert "のデータ取得をスキップします（HTML取得エラー）。理由: Simulated fetch failure" in record.message
            assert any(
                skipped_date in record.message for skipped_date in skipped_dates)


def test_execute_fetch_success_then_error(mock_url_builder, caplog, patch_converter):
    fetcher_mock = Mock(spec=IJmaPageFetcher)
    fetcher_mock.fetch.side_effect = [
        "<html>day1</html>", HtmlFetchingError("Simulated fetch failure for day 2")]
    # parserのMockがイテラブルを返し、必要な属性を持つダミーDTOを返すよう修正

    class DummyRawDto:
        time_str = "00:10"
        avg_wind_direction_str = "北"
        avg_wind_speed_str = "1.0"
        max_wind_direction_str = "北"
        max_wind_speed_str = "2.0"
    parser_mock = Mock()
    parser_mock.parse.return_value = [DummyRawDto()]
    # patch_converterでDummyConverterを使う
    with patch("src.usecases.collect_wind_data_usecase.WindDataConverterService", return_value=DummyConverter()):
        usecase = CollectWindDataUsecase(
            parser=parser_mock,
            page_fetcher=fetcher_mock,
            url_builder=mock_url_builder,
            logger=None
        )
        input_data = CollectWindDataInput("01", "001", "2025-05-27", 2)
        usecase.execute(input_data)
        assert fetcher_mock.fetch.call_count == 2
        # 2日目のスキップWARNINGログのみ検証
        assert any("のデータ取得をスキップします（HTML取得エラー）。理由: Simulated fetch failure for day 2" in r.message and r.levelname ==
                   "WARNING" for r in caplog.records)
