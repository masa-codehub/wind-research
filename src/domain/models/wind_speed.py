from dataclasses import dataclass

@dataclass(frozen=True)
class WindSpeedValue:
    """
    風速値を表す値オブジェクト。不変・等価性・自己検証を持つ。
    """
    value_mps: float

    @staticmethod
    def from_text(text: str) -> 'WindSpeedValue':
        try:
            speed = float(text)
            if speed < 0:
                # 物理的にありえない値
                return WindSpeedValue(value_mps=-1.0)
            return WindSpeedValue(value_mps=speed)
        except (ValueError, TypeError):
            # 欠損や不正値は-1.0
            return WindSpeedValue(value_mps=-1.0)
