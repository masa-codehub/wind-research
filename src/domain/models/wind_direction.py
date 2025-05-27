from dataclasses import dataclass


@dataclass(frozen=True)
class WindDirectionValue:
    degree: float
    original_text: str | None = None
