from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
import logging
from src.usecases.ports.wind_data_parser_port import HtmlParsingError
from src.usecases.ports.jma_page_fetcher_port import HtmlFetchingError
from src.domain.dtos.raw_wind_data_dto import RawWindDataDto
from src.domain.models.wind_data_record import WindDataRecord
from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_speed import WindSpeedValue
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))


def test_execute_valid(capsys):
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=10
    )
    dummy_parser = Mock()
    dummy_parser.parse.return_value = []
    dummy_logger = Mock()
    dummy_url_builder = Mock()
    dummy_page_fetcher = Mock()
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=dummy_logger,
                                     page_fetcher=dummy_page_fetcher, url_builder=dummy_url_builder)
    usecase.execute(input_data)
    dummy_logger.info.assert_called()
    assert "全てのデータ取得・処理が完了しました。" in dummy_logger.info.call_args[0][0]


def test_execute_invalid_days():
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=0
    )
    dummy_parser = Mock()
    dummy_logger = Mock()
    dummy_url_builder = Mock()
    dummy_page_fetcher = Mock()
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=dummy_logger,
                                     page_fetcher=dummy_page_fetcher, url_builder=dummy_url_builder)
    with pytest.raises(ValueError) as e:
        usecase.execute(input_data)
    assert "取得期間" in str(e.value)


def test_execute_logs_warning_for_unknown_direction():
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=1
    )
    dummy_parser = Mock()
    # parser.parseはRawWindDataDtoのリストを返す
    dummy_parser.parse.return_value = [RawWindDataDto(
        time_str="00:10",
        avg_wind_direction_str="南西の風",
        avg_wind_speed_str="1.0",
        max_wind_direction_str="北",
        max_wind_speed_str="2.0"
    )]

    class LoggerMock:
        def __init__(self):
            self.warning_called = False
            self.last_msg = None

        def warning(self, msg):
            self.warning_called = True
            self.last_msg = msg

        def info(self, msg):
            pass
    logger_mock = LoggerMock()
    dummy_url_builder = Mock()
    dummy_page_fetcher = Mock()
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=logger_mock,
                                     page_fetcher=dummy_page_fetcher, url_builder=dummy_url_builder)
    from datetime import date
    usecase._fetch_and_process_daily_data = lambda _: [
        (date(2025, 5, 26), "dummy_html")
    ]
    usecase.execute(input_data)
    assert logger_mock.warning_called
    assert "南西の風" in logger_mock.last_msg


def test_from_html_missing_column():
    # パーサーがHtmlParsingErrorをraiseした場合のログ記録とスキップ処理を検証
    mock_parser = Mock()
    mock_parser.parse.side_effect = HtmlParsingError("不足列: 風向")
    mock_logger = Mock()
    dummy_url_builder = Mock()
    dummy_page_fetcher = Mock()
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=1
    )
    from datetime import date
    usecase = CollectWindDataUsecase(parser=mock_parser, logger=mock_logger,
                                     page_fetcher=dummy_page_fetcher, url_builder=dummy_url_builder)
    result = usecase.execute(input_data)
    # 解析エラー時もスキップ日レコード（144件）が返る
    assert len(result) == 144
    for rec in result:
        assert rec.average_wind_direction.degree == -1.0
        assert rec.average_wind_speed.value_mps == -1.0
        assert rec.max_wind_direction.degree == -1.0
        assert rec.max_wind_speed.value_mps == -1.0
    mock_logger.error.assert_called_once()
    assert "不足列" in mock_logger.error.call_args[0][0]


def test_execute_with_skipped_day():
    """2日間のうち1日が取得失敗した場合、スキップ日には144個の空WindDataRecordが追加される"""
    from datetime import date
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=2
    )
    # 1日目は正常、2日目はfetch失敗
    dummy_parser = Mock()
    dummy_parser.parse.return_value = [RawWindDataDto(
        time_str="00:10",
        avg_wind_direction_str="北",
        avg_wind_speed_str="1.0",
        max_wind_direction_str="北",
        max_wind_speed_str="2.0"
    )]
    dummy_logger = Mock()
    dummy_url_builder = Mock()
    dummy_url_builder.build_jma_10min_data_url.return_value = "dummy_url"
    dummy_page_fetcher = Mock()
    dummy_page_fetcher.fetch.side_effect = [
        "<html>ok</html>", HtmlFetchingError("fail")]  # 2日目失敗
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=dummy_logger,
                                     page_fetcher=dummy_page_fetcher, url_builder=dummy_url_builder)
    result = usecase.execute(input_data)
    # 1日目: 1件, 2日目: 144件（空）
    assert len(result) == 145
    # 2日目のレコードは全て欠損値（24:00は翌日の日付になるので両方含めてカウント）
    skipped_records = [r for r in result if r.observed_at.date() in (
        date(2025, 5, 27), date(2025, 5, 28))]
    assert len(skipped_records) == 144
    for rec in skipped_records:
        assert rec.average_wind_direction.degree == -1.0
        assert rec.average_wind_speed.value_mps == -1.0
        assert rec.max_wind_direction.degree == -1.0
        assert rec.max_wind_speed.value_mps == -1.0
