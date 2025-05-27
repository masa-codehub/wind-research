from dataclasses import dataclass
from typing import ClassVar, Dict

@dataclass(frozen=True)
class WindDirectionValue:
    """
    風向値を表す値オブジェクト。不変・等価性・自己検証を持つ。
    direction: 16方位または特殊値（静穏/欠損）
    degree: 方位角（0-360, 静穏・欠損は-1.0）
    """
    direction: str
    degree: float

    _DIRECTION_TO_DEGREE: ClassVar[Dict[str, float]] = {
        "北": 0.0, "北北東": 22.5, "北東": 45.0, "東北東": 67.5, "東": 90.0, "東南東": 112.5,
        "南東": 135.0, "南南東": 157.5, "南": 180.0, "南南西": 202.5, "南西": 225.0, "西南西": 247.5,
        "西": 270.0, "西北西": 292.5, "北西": 315.0, "北北西": 337.5
    }
    _DEGREE_TO_DIRECTION: ClassVar[Dict[float, str]] = {v: k for k, v in _DIRECTION_TO_DEGREE.items()}

    @staticmethod
    def from_text(text: str) -> 'WindDirectionValue':
        if text == "静穏":
            return WindDirectionValue(direction="静穏", degree=-1.0)
        if text == "///":
            return WindDirectionValue(direction="欠損", degree=-1.0)
        if text in WindDirectionValue._DIRECTION_TO_DEGREE:
            return WindDirectionValue(direction=text, degree=WindDirectionValue._DIRECTION_TO_DEGREE[text])
        try:
            deg = float(text)
            if 0.0 <= deg <= 360.0:
                closest = min(WindDirectionValue._DIRECTION_TO_DEGREE.values(), key=lambda x: abs(x-deg))
                return WindDirectionValue(direction=WindDirectionValue._DEGREE_TO_DIRECTION[closest], degree=closest)
        except (ValueError, TypeError):
            pass
        return WindDirectionValue(direction="欠損", degree=-1.0)