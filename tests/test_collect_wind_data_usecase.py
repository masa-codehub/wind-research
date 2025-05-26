from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))


def test_execute_valid(monkeypatch):
    called = {}

    def fake_print(msg):
        called['msg'] = msg
    monkeypatch.setattr("builtins.print", fake_print)
    input_data = CollectWindDataInput(
        prefecture_no="01",
        block_no="001",
        start_date_str="2025-05-26",
        days=10
    )
    usecase = CollectWindDataUsecase()
    usecase.execute(input_data)
    assert "データ収集中..." in called['msg']


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
