import pandas as pd
from pathlib import Path
from typing import List
from src.usecases.ports.wind_data_output_port import IWindDataOutputPort, FileOutputError
from src.domain.models.wind_data_record import WindDataRecord


class CsvOutputAdapter(IWindDataOutputPort):
    def save(self, records: List[WindDataRecord], output_path: str | None) -> str:
        if not records:
            return "No data to save."
        if output_path is None:
            first_record_date = records[0].observed_at.strftime('%Y%m%d')
            output_path = f"./wind_data_{first_record_date}.csv"
        final_path_str = self._generate_unique_filepath(output_path)
        final_path = Path(final_path_str)
        df = self._create_dataframe(records)
        try:
            final_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(final_path, index=False, encoding='utf-8-sig')
            return str(final_path)
        except (IOError, PermissionError) as e:
            raise FileOutputError(f"Failed to write to {final_path}: {e}")

    def _generate_unique_filepath(self, filepath: str) -> str:
        path = Path(filepath)
        if not path.exists():
            return str(path)
        i = 1
        while True:
            new_path = path.with_name(f"{path.stem}({i}){path.suffix}")
            if not new_path.exists():
                return str(new_path)
            i += 1

    def _create_dataframe(self, records: List[WindDataRecord]) -> pd.DataFrame:
        data = []
        for r in records:
            data.append({
                "observed_at": r.observed_at.isoformat(),
                "avg_wind_direction_deg": r.average_wind_direction.degree if r.average_wind_direction.degree != -1.0 else None,
                "avg_wind_speed_mps": r.average_wind_speed.value_mps if r.average_wind_speed.value_mps != -1.0 else None,
                "max_wind_direction_deg": r.max_wind_direction.degree if r.max_wind_direction.degree != -1.0 else None,
                "max_wind_speed_mps": r.max_wind_speed.value_mps if r.max_wind_speed.value_mps != -1.0 else None,
            })
        return pd.DataFrame(data)
