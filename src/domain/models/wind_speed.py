from dataclasses import dataclass


@dataclass(frozen=True)
class WindSpeedValue:
    value_mps: float
