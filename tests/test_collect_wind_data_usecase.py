from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import logging
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))


def test_execute_valid(capsys):
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=10
    )
    usecase = CollectWindDataUsecase()
    usecase.execute(input_data)
    captured = capsys.readouterr()
    assert "データ収集中..." in captured.out


def test_execute_invalid_days():
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=0
    )
    usecase = CollectWindDataUsecase()
    with pytest.raises(ValueError) as e:
        usecase.execute(input_data)
    assert "取得期間" in str(e.value)


def test_execute_logs_warning_for_unknown_direction(monkeypatch):
    """execute処理中に未定義の風向文字列が取得された場合、警告ログが出力されることを確認"""
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=1
    )
    usecase = CollectWindDataUsecase()
    # データ取得部分をモンキーパッチし、未定義の風向文字列を返す
    monkeypatch.setattr(CollectWindDataUsecase,
                        '_fetch_and_process_daily_data', lambda self, _: ["南西の風"])
    # ロガーをモック化

    class LoggerMock:
        def __init__(self):
            self.warning_called = False
            self.last_msg = None

        def warning(self, msg):
            self.warning_called = True
            self.last_msg = msg
    logger_mock = LoggerMock()
    monkeypatch.setattr(
        'src.usecases.collect_wind_data_usecase.logger', logger_mock)
    usecase.execute(input_data)
    assert logger_mock.warning_called
    assert "南西の風" in logger_mock.last_msg
