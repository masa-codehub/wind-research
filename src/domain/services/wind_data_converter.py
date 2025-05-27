from src.domain.models.wind_direction import WindDirectionValue
from src.domain.models.wind_speed import WindSpeedValue


class WindDataConverterService:
    def convert_wind_direction_from_text(self, text: str | None) -> WindDirectionValue:
        """文字列形式の風向をWindDirectionValueオブジェクトに変換します。

        Args:
            text: 風向を表す文字列 (例: "北西", "静穏", "///")。

        Returns:
            変換されたWindDirectionValueオブジェクト。未定義の入力の場合はdegreeが-1.0になります。
        """
        return WindDirectionValue.from_text(text)

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
