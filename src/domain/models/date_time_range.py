from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class DateTimeRangeValue:
    """
    日付範囲を表す値オブジェクト。不変・等価性・自己検証を持つ。
    start_date <= end_date の不変条件を保証。
    """
    start_date: date
    end_date: date

    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("開始日は終了日以前でなければなりません。")
