from dataclasses import dataclass
from src.domain.models.date import DateValue
from src.domain.services.wind_data_converter import WindDataConverterService
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CollectWindDataInput:
    prefecture_no: str
    block_no: str
    start_date_str: str
    days: int


class CollectWindDataUsecase:
    def __init__(self):
        self.converter = WindDataConverterService()

    def execute(self, input_data: CollectWindDataInput):
        try:
            start_date = DateValue(input_data.start_date_str)
            if not (1 <= input_data.days <= 366):
                raise ValueError("取得期間は1日から366日の間で指定してください。")
        except ValueError as e:
            raise e
        print(
            f"データ収集中...: {input_data.prefecture_no}, {input_data.block_no}, from {start_date.value} for {input_data.days} days")
        # データ取得・変換・ロギングの主フロー
        for raw_direction in self._fetch_and_process_daily_data(input_data):
            wind_direction_vo = self.converter.convert_wind_direction_from_text(
                raw_direction)
            if wind_direction_vo.degree == -1.0 and raw_direction not in ("静穏", "///", "", None):
                logger.warning(
                    f"未定義の風向文字列を検出しました: '{raw_direction}'。-1.0として処理します。")
        # ...後続処理...

    def _fetch_and_process_daily_data(self, input_data: CollectWindDataInput):
        # 本来はHTML等から日次データを抽出する。今はテスト容易性のためスタブ実装。
        return []
