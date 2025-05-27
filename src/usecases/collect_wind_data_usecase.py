from dataclasses import dataclass
from datetime import datetime, timedelta  # timedelta を main ブランチから取り込み
from src.domain.models.date import DateValue
from src.domain.models.wind_data_record import WindDataRecord
from src.domain.services.wind_data_converter import WindDataConverterService
# issue#21_01 ブランチの import
from src.usecases.ports.wind_data_parser_port import IWindDataParser, HtmlParsingError
# from src.adapters.web.jma_html_parser import JmaHtmlParser # 具体的なパーサーはDIされるため、ここでは不要
# main ブランチの import
from src.usecases.ports.jma_page_fetcher_port import IJmaPageFetcher, HtmlFetchingError
from src.usecases.ports.url_builder_port import IUrlBuilder
import logging
from src.domain.models.observation_point import ObservationPointValue

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CollectWindDataInput:
    prefecture_no: str
    block_no: str
    start_date_str: str
    days: int
    interval_sec: float = 5.0  # main ブランチのデフォルト値を取り込み


class CollectWindDataUsecase:
    # 両方のブランチの依存性をマージ
    def __init__(self,
                 parser: IWindDataParser,
                 page_fetcher: IJmaPageFetcher,
                 url_builder: IUrlBuilder,  # main ブランチの url_builder を必須引数に変更
                 logger=None):  # logger を明示的な引数に
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.converter = WindDataConverterService()
        self.parser = parser
        self.page_fetcher = page_fetcher
        self.url_builder = url_builder
        self.logger = logger  # main.py から渡されるloggerを使用

    def execute(self, input_data: CollectWindDataInput):
        try:
            start_date_obj = DateValue(input_data.start_date_str)
            if not (1 <= input_data.days <= 366):
                raise ValueError("取得期間は1日から366日の間で指定してください。")
        except ValueError as e:
            # ここでログを出すか、呼び出し元 (main.py) に委ねるか検討。
            # main.pyでもログしているので、ここではそのままraiseする方がシンプル。
            raise e

        self.logger.info(
            f"データ収集中...: {input_data.prefecture_no}, {input_data.block_no}, from {start_date_obj.value} for {input_data.days} days, interval: {input_data.interval_sec}s"
        )

        all_wind_data_records = []
        current_date = start_date_obj.value

        for i in range(input_data.days):
            target_date = current_date + timedelta(days=i)
            point = ObservationPointValue(
                input_data.prefecture_no, input_data.block_no)
            url = self.url_builder.build_jma_10min_data_url(point, target_date)
            self.logger.info(f"{target_date} のデータ取得処理を開始します。URL: {url}")

            try:
                # 1. HTMLコンテンツの取得 (mainブランチのロジック)
                html_content = self.page_fetcher.fetch(
                    url, user_interval_sec=input_data.interval_sec)
                self.logger.info(f"{target_date} のHTML取得成功。")

                # 2. HTML解析 (issue#21_01ブランチのロジック)
                raw_data_dtos = self.parser.parse(html_content)

                # 3. DTOからドメインモデルへの変換と処理 (issue#21_01ブランチのロジック)
                for raw_dto in raw_data_dtos:
                    avg_wind_direction_vo = self.converter.convert_wind_direction_from_text(
                        raw_dto.avg_wind_direction_str)
                    if avg_wind_direction_vo.degree == -1.0 and \
                       raw_dto.avg_wind_direction_str not in ("静穏", "///", "", None, "--"):
                        self.logger.warning(
                            f"対象日[{target_date}] 時刻[{raw_dto.time_str}]: 未定義の平均風向文字列を検出しました: '{raw_dto.avg_wind_direction_str}'。-1.0として処理します。"
                        )

                    avg_wind_speed_vo = self.converter.convert_wind_speed_from_text(
                        raw_dto.avg_wind_speed_str)
                    max_wind_direction_vo = self.converter.convert_wind_direction_from_text(
                        raw_dto.max_wind_direction_str)
                    max_wind_speed_vo = self.converter.convert_wind_speed_from_text(
                        raw_dto.max_wind_speed_str)

                    try:
                        hour, minute = map(int, raw_dto.time_str.split(":"))
                        observed_at_dt: datetime
                        if hour == 24 and minute == 0:
                            observed_at_dt = datetime(
                                target_date.year, target_date.month, target_date.day, 23, 59)
                        else:
                            observed_at_dt = datetime(
                                target_date.year, target_date.month, target_date.day, hour, minute)

                        record = WindDataRecord(
                            observed_at=observed_at_dt,
                            average_wind_direction=avg_wind_direction_vo,
                            average_wind_speed=avg_wind_speed_vo,
                            max_wind_direction=max_wind_direction_vo,
                            max_wind_speed=max_wind_speed_vo
                        )
                        all_wind_data_records.append(record)
                    except ValueError:  # 時刻文字列のパース失敗など
                        self.logger.error(
                            f"対象日[{target_date}] 時刻[{raw_dto.time_str}]のパースに失敗したため、このレコードをスキップします。")
                        continue  # このDTOの処理をスキップ

            except HtmlFetchingError as e:  # mainブランチのエラーハンドリング
                self.logger.warning(
                    f"{target_date} のデータ取得をスキップします（HTML取得エラー）。理由: {e}")
                continue  # 次の日付の処理へ
            except HtmlParsingError as e:  # issue#21_01ブランチのエラーハンドリング
                self.logger.error(
                    f"{target_date} のデータ解析をスキップします（HTML解析エラー）。理由: {e}")
                continue  # 次の日付の処理へ
            except Exception as e:  # その他の予期せぬエラー
                self.logger.error(
                    f"{target_date} の処理中に予期せぬエラーが発生しました。処理をスキップします。理由: {e}", exc_info=True)
                continue  # 次の日付の処理へ

        self.logger.info("全てのデータ取得・処理が完了しました。")
        return all_wind_data_records

    # _fetch_and_process_daily_data 及び _fetch_and_process_daily_data_stub は
    # execute メソッド内で日次ループとHTML取得・解析が統合されたため不要。
    # 実際のHTML取得は self.page_fetcher.fetch() で行い、
    # 解析は self.parser.parse() で行う。
