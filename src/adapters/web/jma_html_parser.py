import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from typing import List

from src.usecases.ports.wind_data_parser_port import IWindDataParser, HtmlParsingError
from src.domain.dtos.raw_wind_data_dto import RawWindDataDto


class JmaHtmlParser(IWindDataParser):
    """
    気象庁HTMLテーブルから10分毎の風向・風速等を抽出し、RawWindDataDtoとして返すパーサー。
    テーブル列名はJMAのHTML構造に強く依存するため、rename_mapはHTML仕様変更時に要調整。
    """

    def parse(self, html_content: str) -> List[RawWindDataDto]:
        try:
            soup = BeautifulSoup(html_content, "lxml")
            table_element = soup.find("table", id="tablefix1")
            if not table_element:
                raise HtmlParsingError("目的のテーブル(id='tablefix1')が見つかりません。")

            # header=1で2行目をヘッダーとして読み込むことで、列名がフラットになる
            df = pd.read_html(StringIO(str(table_element)),
                              header=1, na_values=[], keep_default_na=False)[0]
            # JMA HTMLの列名に合わせてマッピング
            rename_map = {
                '時分': 'time_str',
                '風向': 'avg_wind_direction_str',
                '平均': 'avg_wind_speed_str',
                '風向.1': 'max_wind_direction_str',
                '最大瞬間': 'max_wind_speed_str',
            }
            df = df.rename(columns=rename_map)
            required_columns = [
                'time_str', 'avg_wind_direction_str', 'avg_wind_speed_str',
                'max_wind_direction_str', 'max_wind_speed_str'
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise HtmlParsingError(
                    f"不足列: {missing} 存在する列: {df.columns.tolist()}")
            raw_data_list: List[RawWindDataDto] = []
            for _, row in df.iterrows():
                raw_data_list.append(RawWindDataDto(
                    time_str=str(row['time_str']),
                    avg_wind_direction_str=str(row['avg_wind_direction_str']),
                    avg_wind_speed_str=str(row['avg_wind_speed_str']),
                    max_wind_direction_str=str(row['max_wind_direction_str']),
                    max_wind_speed_str=str(row['max_wind_speed_str']),
                ))
            return raw_data_list
        except Exception as e:
            raise HtmlParsingError(f"HTML解析中に予期せぬエラーが発生しました: {e}")
