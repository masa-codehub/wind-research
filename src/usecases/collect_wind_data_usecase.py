from dataclasses import dataclass
from src.domain.models.date import DateValue


@dataclass(frozen=True)
class CollectWindDataInput:
    prefecture_no: str
    block_no: str
    start_date_str: str
    days: int


class CollectWindDataUsecase:
    def execute(self, input_data: CollectWindDataInput):
        try:
            start_date = DateValue(input_data.start_date_str)
            if not (1 <= input_data.days <= 366):
                raise ValueError("取得期間は1日から366日の間で指定してください。")
        except ValueError as e:
            raise e
        print(
            f"データ収集中...: {input_data.prefecture_no}, {input_data.block_no}, from {start_date.value} for {input_data.days} days")
        # ここで後続処理（スタブ）を呼び出す
        pass
