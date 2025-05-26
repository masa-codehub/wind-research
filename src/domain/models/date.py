from datetime import date
import re


class DateValue:
    def __init__(self, value: str):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError("日付のフォーマットが不正です。YYYY-MM-DD形式で指定してください。")
        try:
            self.value: date = date.fromisoformat(value)
        except ValueError as e:
            raise ValueError(f"無効な日付です: {e}")

    def __eq__(self, other):
        if isinstance(other, DateValue):
            return self.value == other.value
        return False

    def __str__(self):
        return self.value.isoformat()
