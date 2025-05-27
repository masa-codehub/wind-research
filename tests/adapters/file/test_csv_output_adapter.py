import pytest
import pandas as pd
from pathlib import Path
from src.adapters.file.csv_output_adapter import CsvOutputAdapter
from src.domain.models.wind_data_record import WindDataRecord
from src.domain.models.wind_direction import WindDirectionValue as WindDirection
from src.domain.models.wind_speed import WindSpeedValue as WindSpeed
from src.usecases.ports.wind_data_output_port import FileOutputError
import datetime

# 正常系: WindDataRecordのリストを与え、CSVが正しく生成されることを検証


def test_save_creates_csv_file(tmp_path):
    adapter = CsvOutputAdapter()
    records = [
        WindDataRecord(
            observed_at=datetime.datetime(2024, 5, 1, 12, 0),
            average_wind_direction=WindDirection(
                direction="東", degree=90.0, original_text="東"),
            average_wind_speed=WindSpeed(5.5),
            max_wind_direction=WindDirection(
                direction="東南東", degree=112.5, original_text="東南東"),
            max_wind_speed=WindSpeed(8.8),
        ),
        WindDataRecord(
            observed_at=datetime.datetime(2024, 5, 1, 13, 0),
            average_wind_direction=WindDirection(
                direction="南", degree=180.0, original_text="南"),
            average_wind_speed=WindSpeed(6.0),
            max_wind_direction=WindDirection(
                direction="南南西", degree=202.5, original_text="南南西"),
            max_wind_speed=WindSpeed(10.0),
        ),
    ]
    output_path = tmp_path / "test_wind.csv"
    saved_path = adapter.save(records, str(output_path))
    assert Path(saved_path).exists()
    # pandasで読み込み、内容・ヘッダー・エンコーディングを検証
    df = pd.read_csv(saved_path, encoding="utf-8-sig")
    assert list(df.columns) == [
        "observed_at",
        "avg_wind_direction_deg",
        "avg_wind_speed_mps",
        "max_wind_direction_deg",
        "max_wind_speed_mps",
    ]
    assert df.shape[0] == 2
    assert df.iloc[0]["avg_wind_direction_deg"] == 90.0
    assert df.iloc[1]["max_wind_speed_mps"] == 10.0

# 欠損値（-1.0）が空欄になることを検証


def test_save_missing_values_are_blank(tmp_path):
    adapter = CsvOutputAdapter()
    records = [
        WindDataRecord(
            observed_at=datetime.datetime(2024, 5, 1, 12, 0),
            average_wind_direction=WindDirection(
                direction="欠損", degree=-1.0, original_text="欠損"),
            average_wind_speed=WindSpeed(-1.0),
            max_wind_direction=WindDirection(
                direction="欠損", degree=-1.0, original_text="欠損"),
            max_wind_speed=WindSpeed(-1.0),
        ),
    ]
    output_path = tmp_path / "missing.csv"
    saved_path = adapter.save(records, str(output_path))
    df = pd.read_csv(saved_path, encoding="utf-8-sig")
    # 欠損値は空欄（NaN）として出力される
    assert pd.isna(df.iloc[0]["avg_wind_direction_deg"])
    assert pd.isna(df.iloc[0]["avg_wind_speed_mps"])
    assert pd.isna(df.iloc[0]["max_wind_direction_deg"])
    assert pd.isna(df.iloc[0]["max_wind_speed_mps"])


def test_save_generates_unique_filename(tmp_path):
    adapter = CsvOutputAdapter()
    records = [
        WindDataRecord(
            observed_at=datetime.datetime(2024, 5, 1, 12, 0),
            average_wind_direction=WindDirection(
                direction="東", degree=90.0, original_text="東"),
            average_wind_speed=WindSpeed(5.5),
            max_wind_direction=WindDirection(
                direction="東南東", degree=112.5, original_text="東南東"),
            max_wind_speed=WindSpeed(8.8),
        ),
    ]
    output_path = tmp_path / "dup.csv"
    # 先に同名ファイルを作成
    output_path.write_text("dummy", encoding="utf-8")
    saved_path = adapter.save(records, str(output_path))
    # 新しいファイル名はdup(1).csvとなるはず
    assert Path(saved_path).name == "dup(1).csv"
    assert Path(saved_path).exists()


def test_save_raises_file_output_error_on_permission(monkeypatch, tmp_path):
    adapter = CsvOutputAdapter()
    records = [
        WindDataRecord(
            observed_at=datetime.datetime(2024, 5, 1, 12, 0),
            average_wind_direction=WindDirection(
                direction="東", degree=90.0, original_text="東"),
            average_wind_speed=WindSpeed(5.5),
            max_wind_direction=WindDirection(
                direction="東南東", degree=112.5, original_text="東南東"),
            max_wind_speed=WindSpeed(8.8),
        ),
    ]
    output_path = tmp_path / "error.csv"

    def raise_permission(*args, **kwargs):
        raise PermissionError("mocked")
    monkeypatch.setattr("pandas.DataFrame.to_csv", raise_permission)
    with pytest.raises(FileOutputError) as excinfo:
        adapter.save(records, str(output_path))
    assert "mocked" in str(excinfo.value)
