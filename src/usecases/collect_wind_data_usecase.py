from dataclasses import dataclass
from src.domain.models.date import DateValue
from src.domain.services.wind_data_converter import WindDataConverterService
from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher, HtmlFetchingError
from src.usecases.ports.url_builder_port import IUrlBuilder
from datetime import timedelta
import logging
from src.domain.models.observation_point import ObservationPointValue

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CollectWindDataInput:
    prefecture_no: str
    block_no: str
    start_date_str: str
    days: int
    interval_sec: float = 5.0  # デフォルト値


class CollectWindDataUsecase:
    def __init__(self, page_fetcher: IJmaPageFetcher, url_builder: IUrlBuilder = None):
        self.converter = WindDataConverterService()
        self.page_fetcher = page_fetcher
        from src.adapters.web.jma_url_builder import JmaUrlBuilder
        self.url_builder = url_builder or JmaUrlBuilder()

    def execute(self, input_data: CollectWindDataInput):
        try:
            start_date = DateValue(input_data.start_date_str)
            if not (1 <= input_data.days <= 366):
                raise ValueError("取得期間は1日から366日の間で指定してください。")
        except ValueError as e:
            raise e
        logger.info(
            f"データ収集中...: {input_data.prefecture_no}, {input_data.block_no}, from {start_date.value} for {input_data.days} days")
        current_date = start_date.value
        for i in range(input_data.days):
            target_date = current_date + timedelta(days=i)
            point = ObservationPointValue(
                input_data.prefecture_no, input_data.block_no)
            url = self.url_builder.build_jma_10min_data_url(point, target_date)
            logger.info(f"{target_date} のデータ取得処理を開始します。URL: {url}")
            try:
                html_content = self.page_fetcher.fetch(
                    url, user_interval_sec=input_data.interval_sec)
                msg = f"{target_date} のHTML取得成功。"
                logger.info(msg)
                for raw_direction in self._fetch_and_process_daily_data_stub(input_data):
                    wind_direction_vo = self.converter.convert_wind_direction_from_text(
                        raw_direction)
                    if wind_direction_vo.degree == -1.0 and raw_direction not in ("静穏", "///", "", None):
                        logger.warning(
                            f"未定義の風向文字列を検出しました: '{raw_direction}'。-1.0として処理します。")
            except HtmlFetchingError as e:
                logger.warning(f"{target_date} のデータ取得をスキップします。理由: {e}")
                continue
        logger.info("全てのデータ取得処理が完了しました。")

    def _fetch_and_process_daily_data_stub(self, input_data: CollectWindDataInput):
        return ["北東", "静穏", "///", "未知の方向"]
