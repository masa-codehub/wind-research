import pytest
from unittest.mock import Mock, patch
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher, HtmlFetchingError
from src.adapters.web.jma_url_builder import JmaUrlBuilder


class DummyConverter:
    def convert_wind_direction_from_text(self, raw):
        class DummyVO:
            def __init__(self, degree):
                self.degree = degree
        if raw == "静穏":
            return DummyVO(0.0)
        elif raw == "///":
            return DummyVO(-1.0)
        elif raw == "南西の風":
            return DummyVO(-1.0)
        else:
            return DummyVO(90.0)


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
        page_fetcher=fetcher_mock, url_builder=mock_url_builder)
    input_data = CollectWindDataInput("01", "001", "2025-05-27", 2)
    with patch.object(usecase, '_fetch_and_process_daily_data_stub', return_value=[]):
        usecase.execute(input_data)
    assert fetcher_mock.fetch.call_count == 2
    skipped_dates = ["2025-05-27", "2025-05-28"]
    for record in caplog.records:
        if record.levelname == "WARNING":
            assert "のデータ取得をスキップします。理由: Simulated fetch failure" in record.message
            assert any(
                skipped_date in record.message for skipped_date in skipped_dates)


def test_execute_fetch_success_then_error(mock_url_builder, caplog, patch_converter):
    fetcher_mock = Mock(spec=IJmaPageFetcher)
    fetcher_mock.fetch.side_effect = [
        "<html>day1</html>", HtmlFetchingError("Simulated fetch failure for day 2")]
    usecase = CollectWindDataUsecase(
        page_fetcher=fetcher_mock, url_builder=mock_url_builder)
    input_data = CollectWindDataInput("01", "001", "2025-05-27", 2)
    with patch.object(usecase, '_fetch_and_process_daily_data_stub') as mock_parser_stub:
        mock_parser_stub.return_value = ["北東"]
        usecase.execute(input_data)
    assert fetcher_mock.fetch.call_count == 2
    assert any("2025-05-27 のHTML取得成功。" in r.message and r.levelname ==
               "INFO" for r in caplog.records)
    assert any("2025-05-28 のデータ取得をスキップします。" in r.message and r.levelname ==
               "WARNING" for r in caplog.records)
    mock_parser_stub.assert_called_once()
