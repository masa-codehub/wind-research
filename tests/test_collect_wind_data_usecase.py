from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock
from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher, HtmlFetchingError
from src.usecases.ports.wind_data_parser_port import IWindDataParser, HtmlParsingError
from src.usecases.ports.url_builder_port import IUrlBuilder
from src.usecases.ports.wind_data_output_port import IWindDataOutputPort
import logging
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
    dummy_parser = Mock(spec=IWindDataParser)
    dummy_parser.parse.return_value = []
    dummy_logger = Mock(spec=logging.Logger)
    dummy_url_builder = Mock(spec=IUrlBuilder)
    dummy_page_fetcher = Mock(spec=IJmaPageFetcher)
    dummy_output_port = Mock(spec=IWindDataOutputPort)
    dummy_output_port.save.return_value = "dummy/path/output.csv"
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=dummy_logger,
                                     page_fetcher=dummy_page_fetcher, url_builder=dummy_url_builder, output_port=dummy_output_port)
    usecase.execute(input_data)
    dummy_logger.info.assert_any_call("全てのデータ取得・処理が完了しました。")
    dummy_logger.info.assert_any_call("ファイル出力完了: dummy/path/output.csv")


def test_execute_invalid_days():
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=0
    )
    dummy_parser = Mock(spec=IWindDataParser)
    dummy_logger = Mock(spec=logging.Logger)
    dummy_url_builder = Mock(spec=IUrlBuilder)
    dummy_page_fetcher = Mock(spec=IJmaPageFetcher)
    dummy_output_port = Mock(spec=IWindDataOutputPort)
    usecase = CollectWindDataUsecase(parser=dummy_parser, logger=dummy_logger,
                                     page_fetcher=dummy_page_fetcher, url_builder=dummy_url_builder, output_port=dummy_output_port)
    with pytest.raises(ValueError) as e:
        usecase.execute(input_data)
    assert "取得期間" in str(e.value)


def test_execute_logs_warning_for_unknown_direction(monkeypatch):
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=1
    )
    mock_fetcher = Mock(spec=IJmaPageFetcher)
    mock_fetcher.fetch.return_value = "dummy_html_content"
    mock_parser = Mock(spec=IWindDataParser)
    mock_parser.parse.return_value = [RawWindDataDto(
        time_str="00:10",
        avg_wind_direction_str="南西の風",  # 未定義の風向
        avg_wind_speed_str="1.0",
        max_wind_direction_str="北",
        max_wind_speed_str="2.0"
    )]
    logger_mock = Mock(spec=logging.Logger)
    mock_url_builder = Mock(spec=IUrlBuilder)
    mock_url_builder.build_jma_10min_data_url.return_value = "http://dummy.url"
    mock_output_port = Mock(spec=IWindDataOutputPort)
    usecase = CollectWindDataUsecase(
        parser=mock_parser,
        page_fetcher=mock_fetcher,
        url_builder=mock_url_builder,
        output_port=mock_output_port,
        logger=logger_mock
    )
    usecase.execute(input_data)
    args, kwargs = logger_mock.warning.call_args
    assert "未定義の平均風向文字列を検出しました: '南西の風'" in args[0]


def test_from_html_missing_column(monkeypatch):
    mock_page_fetcher = Mock(spec=IJmaPageFetcher)
    mock_page_fetcher.fetch.return_value = "dummy_html_content_for_parsing_error"
    mock_parser = Mock(spec=IWindDataParser)
    mock_parser.parse.side_effect = HtmlParsingError("不足列: 風向")
    mock_logger = Mock(spec=logging.Logger)
    mock_url_builder = Mock(spec=IUrlBuilder)
    mock_url_builder.build_jma_10min_data_url.return_value = "http://dummy.url"
    mock_output_port = Mock(spec=IWindDataOutputPort)
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=1
    )
    usecase = CollectWindDataUsecase(
        parser=mock_parser,
        page_fetcher=mock_page_fetcher,
        url_builder=mock_url_builder,
        output_port=mock_output_port,
        logger=mock_logger
    )
    result = usecase.execute(input_data)
    args, kwargs = mock_logger.error.call_args
    assert "のデータ解析をスキップします（HTML解析エラー）。理由: 不足列: 風向" in args[0]
    mock_output_port.save.assert_called_once_with([], input_data.output_path)


def test_execute_with_one_day_fetch_error_generates_empty_records_for_that_day_and_calls_save():
    """
    1日間のデータ取得でfetchエラーが発生した場合、
    その日の処理はスキップされるが、最終的にoutput_port.saveが空のレコードリストで呼び出されることを確認する。
    (FR-005-02の振る舞いは、現状のUsecaseでは1日単位のエラーは空のレコードを明示的に作らず、
    結果としてall_wind_data_recordsがその日の分だけ空になることを意味すると解釈)
    """
    from datetime import date
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=1 # 1日のみのテスト
    )
    dummy_parser = Mock(spec=IWindDataParser) # fetchエラーなのでparserは呼ばれないはず
    mock_logger = Mock(spec=logging.Logger)
    mock_url_builder = Mock(spec=IUrlBuilder)
    mock_url_builder.build_jma_10min_data_url.return_value = "http://dummy.url/2025-05-26"

    mock_page_fetcher = Mock(spec=IJmaPageFetcher)
    mock_page_fetcher.fetch.side_effect = HtmlFetchingError("Simulated fetch failure for 2025-05-26")

    mock_output_port = Mock(spec=IWindDataOutputPort)
    mock_output_port.save.return_value = "dummy/output.csv"

    usecase = CollectWindDataUsecase(
        parser=dummy_parser,
        logger=mock_logger,
        page_fetcher=mock_page_fetcher,
        url_builder=mock_url_builder,
        output_port=mock_output_port
    )
    
    saved_file_path = usecase.execute(input_data)
    
    # fetchエラーのログが出力されることを確認
    mock_logger.warning.assert_any_call("2025-05-26 のデータ取得をスキップします（HTML取得エラー）。理由: Simulated fetch failure for 2025-05-26")
    
    # all_wind_data_records は空のはず
    mock_output_port.save.assert_called_once_with([], input_data.output_path)
    assert saved_file_path == "dummy/output.csv"


def test_execute_with_one_day_success_and_one_day_fetch_error():
    """2日間のうち1日目が成功、2日目が取得失敗した場合、
    成功した日のデータと、失敗した日の空データ(ここでは0件として扱われる)が結合されsaveが呼ばれる"""
    from datetime import date
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=2
    )
    
    # 1日目のデータ (RawWindDataDtoのリスト)
    day1_raw_dtos = [RawWindDataDto(
        time_str="00:10", avg_wind_direction_str="北", avg_wind_speed_str="1.0",
        max_wind_direction_str="北", max_wind_speed_str="2.0"
    )]

    mock_parser = Mock(spec=IWindDataParser)
    # fetchが成功した最初の呼び出しに対してのみday1_raw_dtosを返す
    mock_parser.parse.return_value = day1_raw_dtos

    mock_logger = Mock(spec=logging.Logger)
    
    mock_url_builder = Mock(spec=IUrlBuilder)
    # 2回呼ばれることを想定
    mock_url_builder.build_jma_10min_data_url.side_effect = [
        "http://dummy.url/2025-05-26", 
        "http://dummy.url/2025-05-27"
    ]

    mock_page_fetcher = Mock(spec=IJmaPageFetcher)
    mock_page_fetcher.fetch.side_effect = [
        "<html>day1_content</html>", # 1日目成功
        HtmlFetchingError("Simulated fetch failure for 2025-05-27") # 2日目失敗
    ]

    mock_output_port = Mock(spec=IWindDataOutputPort)
    mock_output_port.save.return_value = "dummy/output_mixed.csv"

    usecase = CollectWindDataUsecase(
        parser=mock_parser,
        logger=mock_logger,
        page_fetcher=mock_page_fetcher,
        url_builder=mock_url_builder,
        output_port=mock_output_port
    )
    
    saved_file_path = usecase.execute(input_data)
    
    # 2日目のfetchエラーのログ
    mock_logger.warning.assert_any_call("2025-05-27 のデータ取得をスキップします（HTML取得エラー）。理由: Simulated fetch failure for 2025-05-27")
    
    # output_port.save が呼び出された際の引数 (records) をキャプチャ
    # 1日目のデータ(1件)のみが含まれるはず
    assert mock_output_port.save.call_count == 1
    called_with_records = mock_output_port.save.call_args[0][0]
    assert len(called_with_records) == 1 # 1日目の RawWindDataDto 1件から1 WindDataRecord ができる
    assert called_with_records[0].average_wind_speed.value_mps == 1.0 # 変換後の値を確認

    assert saved_file_path == "dummy/output_mixed.csv"


def test_interval_sec_below_minimum_raises_error():
    """ interval_sec が3秒未満の場合にValueErrorが発生することを確認する。"""
    start = datetime.now()

    with pytest.raises(ValueError, match="interval_sec 3 秒以上である必要があります。"):
        CollectWindDataInput(
            prefecture_no="01",
            block_no="001",
            start_date_str=start.strftime("%Y-%m-%d"),
            days=1,
            interval_sec=2.0,  # 3秒未満の値
        )
