from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher
from src.usecases.ports.wind_data_parser_port import IWindDataParser, HtmlParsingError
from src.usecases.ports.url_builder_port import IUrlBuilder
from src.usecases.ports.wind_data_output_port import IWindDataOutputPort
import logging
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
    dummy_url_builder = Mock()
    dummy_page_fetcher = Mock()
    dummy_output_port = Mock()
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
    dummy_parser = Mock()
    dummy_logger = Mock()
    dummy_url_builder = Mock()
    dummy_page_fetcher = Mock()
    dummy_output_port = Mock()
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
    # page_fetcher.fetch がダミーHTMLを返すようにモック
    from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher
    mock_fetcher = Mock(spec=IJmaPageFetcher)
    mock_fetcher.fetch.return_value = "dummy_html_content"
    # parser.parse が問題の RawWindDataDto を返すようにモック
    from src.usecases.ports.wind_data_parser_port import IWindDataParser
    mock_parser = Mock(spec=IWindDataParser)
    mock_parser.parse.return_value = [RawWindDataDto(
        time_str="00:10",
        avg_wind_direction_str="南西の風",  # 未定義の風向
        avg_wind_speed_str="1.0",
        max_wind_direction_str="北",
        max_wind_speed_str="2.0"
    )]
    import logging
    logger_mock = Mock(spec=logging.Logger)
    from src.usecases.ports.url_builder_port import IUrlBuilder
    mock_url_builder = Mock(spec=IUrlBuilder)
    mock_url_builder.build_jma_10min_data_url.return_value = "http://dummy.url"
    from src.usecases.ports.wind_data_output_port import IWindDataOutputPort
    mock_output_port = Mock(spec=IWindDataOutputPort)
    usecase = CollectWindDataUsecase(
        parser=mock_parser,
        page_fetcher=mock_fetcher,
        url_builder=mock_url_builder,
        output_port=mock_output_port,
        logger=logger_mock
    )
    usecase.execute(input_data)
    # logger_mock.warning が期待通りに呼び出されたか検証
    args, kwargs = logger_mock.warning.call_args
    assert "未定義の平均風向文字列を検出しました: '南西の風'" in args[0]


def test_from_html_missing_column(monkeypatch):
    from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher
    mock_page_fetcher = Mock(spec=IJmaPageFetcher)
    mock_page_fetcher.fetch.return_value = "dummy_html_content_for_parsing_error"
    from src.usecases.ports.wind_data_parser_port import IWindDataParser
    mock_parser = Mock(spec=IWindDataParser)
    mock_parser.parse.side_effect = HtmlParsingError("不足列: 風向")
    import logging
    mock_logger = Mock(spec=logging.Logger)
    from src.usecases.ports.url_builder_port import IUrlBuilder
    mock_url_builder = Mock(spec=IUrlBuilder)
    mock_url_builder.build_jma_10min_data_url.return_value = "http://dummy.url"
    from src.usecases.ports.wind_data_output_port import IWindDataOutputPort
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
    # エラーログの呼び出しを検証
    args, kwargs = mock_logger.error.call_args
    assert "のデータ解析をスキップします（HTML解析エラー）。理由: 不足列: 風向" in args[0]
    # output_port.save が空のリストで呼び出されることを確認
    mock_output_port.save.assert_called_once_with([], input_data.output_path)
