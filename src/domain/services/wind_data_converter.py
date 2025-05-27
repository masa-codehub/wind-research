from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_speed import WindSpeedValue
from typing import Dict


class WindDataConverterService:
    _WIND_DIRECTION_MAP: Dict[str, float] = {
        "北": 0.0, "北北東": 22.5, "北東": 45.0, "東北東": 67.5,
        "東": 90.0, "東南東": 112.5, "南東": 135.0, "南南東": 157.5,
        "南": 180.0, "南南西": 202.5, "南西": 225.0, "西南西": 247.5,
        "西": 270.0, "西北西": 292.5, "北西": 315.0, "北北西": 337.5,
        "静穏": -1.0,
        "///": -1.0,
    }

    def convert_wind_direction_from_text(self, text: str | None) -> WindDirectionValue:
        """文字列形式の風向をWindDirectionValueオブジェクトに変換します。

        Args:
            text: 風向を表す文字列 (例: "北西", "静穏", "///")。

        Returns:
            変換されたWindDirectionValueオブジェクト。未定義の入力の場合はdegreeが-1.0になります。
        """
        if not text:
            return WindDirectionValue(degree=-1.0, original_text=text)
        degree = self._WIND_DIRECTION_MAP.get(text, -1.0)
        return WindDirectionValue(degree=degree, original_text=text)

    def convert_wind_speed_from_text(self, text: str | None) -> WindSpeedValue:
        """文字列形式の風速をWindSpeedValueオブジェクトに変換します。

        Args:
            text: 風速を表す文字列 (例: "10.5", "///")。

        Returns:
            変換されたWindSpeedValueオブジェクト。未定義や非数値入力の場合はvalue_mpsが-1.0になります。
        """
        try:
            value = float(text)
        except (ValueError, TypeError):
            value = -1.0
        return WindSpeedValue(value_mps=value)
