from dataclasses import dataclass


@dataclass(frozen=True)
class RawWindDataDto:
    """HTMLから抽出した生データを保持するDTO。バリデーションは行わない。"""
    time_str: str                      # 例: "00:10"
    avg_wind_direction_str: str        # 例: "北北東"
    avg_wind_speed_str: str            # 例: "1.6"
    max_wind_direction_str: str        # 例: "北東"
    max_wind_speed_str: str            # 例: "3.4"
    # ... 他に必要な項目があれば追加
