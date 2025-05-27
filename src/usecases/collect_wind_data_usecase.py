from dataclasses import dataclass
from datetime import datetime
from src.domain.models.date import DateValue
from src.domain.models.wind_data_record import WindDataRecord
from src.domain.services.wind_data_converter import WindDataConverterService
from src.usecases.ports.wind_data_parser_port import IWindDataParser, HtmlParsingError
from src.adapters.web.jma_html_parser import JmaHtmlParser
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CollectWindDataInput:
    prefecture_no: str
    block_no: str
    start_date_str: str
    days: int


class CollectWindDataUsecase:
    def __init__(self, parser: IWindDataParser, logger=logger):
        self.converter = WindDataConverterService()
        self.parser = parser
        self.logger = logger

    def execute(self, input_data: CollectWindDataInput):
        try:
            start_date = DateValue(input_data.start_date_str)
            if not (1 <= input_data.days <= 366):
                raise ValueError("取得期間は1日から366日の間で指定してください。")
        except ValueError as e:
            raise e
        self.logger.info(
            f"データ収集中...: {input_data.prefecture_no}, {input_data.block_no}, from {start_date.value} for {input_data.days} days")
        results = []
        for target_date, html in self._fetch_and_process_daily_data(input_data):
            try:
                raw_data_dtos = self.parser.parse(html)
                for raw_dto in raw_data_dtos:
                    avg_wind_direction_vo = self.converter.convert_wind_direction_from_text(
                        raw_dto.avg_wind_direction_str)
                    if avg_wind_direction_vo.degree == -1.0 and \
                       raw_dto.avg_wind_direction_str not in ("静穏", "///", "", None, "--"):
                        self.logger.warning(
                            f"未定義の平均風向文字列を検出しました: '{raw_dto.avg_wind_direction_str}'。-1.0として処理します。"
                        )
                    avg_wind_speed_vo = self.converter.convert_wind_speed_from_text(
                        raw_dto.avg_wind_speed_str)
                    max_wind_direction_vo = self.converter.convert_wind_direction_from_text(
                        raw_dto.max_wind_direction_str)
                    max_wind_speed_vo = self.converter.convert_wind_speed_from_text(
                        raw_dto.max_wind_speed_str)
                    # 日付と時刻を組み合わせてdatetimeを生成。24:00は当日23:59として記録。
                    try:
                        hour, minute = map(int, raw_dto.time_str.split(":"))
                        if hour == 24 and minute == 0:
                            observed_at = datetime(
                                target_date.year, target_date.month, target_date.day, 23, 59)
                        else:
                            observed_at = datetime(
                                target_date.year, target_date.month, target_date.day, hour, minute)
                    except Exception:
                        observed_at = None  # パース失敗時はNone
                    record = WindDataRecord(
                        observed_at=observed_at,
                        average_wind_direction=avg_wind_direction_vo,
                        average_wind_speed=avg_wind_speed_vo,
                        max_wind_direction=max_wind_direction_vo,
                        max_wind_speed=max_wind_speed_vo
                    )
                    results.append(record)
            except HtmlParsingError as e:
                self.logger.error(f"HTMLパースエラー: {e}")
                continue
        return results

    def _fetch_and_process_daily_data(self, input_data: CollectWindDataInput):
        # 本来はHTML等から日次データを抽出し、(date, html)タプルをyieldする。今はテスト容易性のためスタブ実装。
        return []
