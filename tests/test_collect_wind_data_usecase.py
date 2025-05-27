from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
import logging
from src.usecases.ports.wind_data_parser_port import HtmlParsingError
from src.domain.dtos.raw_wind_data_dto import RawWindDataDto
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
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=dummy_logger)
    usecase.execute(input_data)
    dummy_logger.info.assert_called()
    assert "データ収集中..." in dummy_logger.info.call_args[0][0]


def test_execute_invalid_days():
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=0
    )
    dummy_parser = Mock()
    dummy_logger = Mock()
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=dummy_logger)
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
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=logger_mock)
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
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=1
    )
    from datetime import date
    usecase = CollectWindDataUsecase(parser=mock_parser, logger=mock_logger)
    usecase._fetch_and_process_daily_data = lambda _: [
        (date(2025, 5, 26), "dummy_html")
    ]
    result = usecase.execute(input_data)
    assert result == []  # スキップされる
    mock_logger.error.assert_called_once()
    assert "不足列" in mock_logger.error.call_args[0][0]
