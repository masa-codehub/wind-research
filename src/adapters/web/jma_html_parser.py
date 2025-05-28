import pandas as pd
import re
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

            # pd.read_htmlでテーブルを読み取り（ヘッダー自動判定）
            dfs = pd.read_html(StringIO(str(table_element)),
                               na_values=[], keep_default_na=False)
            if not dfs:
                raise HtmlParsingError("テーブルからデータフレームを取得できませんでした。")

            df = dfs[0]

            # MultiIndexの列名をフラット化（簡潔で一意な名前にする）
            if isinstance(df.columns, pd.MultiIndex):
                new_columns = []
                for col in df.columns:
                    # 最後のレベルを優先し、それが明確でない場合は上位レベルと組み合わせる
                    if len(col) >= 3:
                        # 3レベル構造の場合
                        level2 = str(col[1]) if str(col[1]) != 'nan' else ''
                        level3 = str(col[2]) if str(col[2]) != 'nan' else ''

                        if level3 == '風向' and level2 == '平均':
                            new_columns.append('平均風向')
                        elif level3 == '風速(m/s)' and level2 == '平均':
                            new_columns.append('平均風速')
                        elif level3 == '風向' and level2 == '最大瞬間':
                            new_columns.append('最大瞬間風向')
                        elif level3 == '風速(m/s)' and level2 == '最大瞬間':
                            new_columns.append('最大瞬間風速')
                        else:
                            # その他の列は最初のレベルを使用
                            new_columns.append(str(col[0]))
                    else:
                        new_columns.append(str(col[0]))
                df.columns = new_columns

            # 列名のマッピング（JMAのHTML構造に対応）
            rename_map = {
                '時分': 'time_str',
                '風向': 'avg_wind_direction_str',
                '平均': 'avg_wind_speed_str',
                '風向.1': 'max_wind_direction_str',
                '最大瞬間': 'max_wind_speed_str',
                '風速(m/s)': 'avg_wind_speed_str',
                '風速(m/s).1': 'max_wind_speed_str',
                # フラット化後の列名に対応
                '平均風向': 'avg_wind_direction_str',
                '平均風速': 'avg_wind_speed_str',
                '最大瞬間風向': 'max_wind_direction_str',
                '最大瞬間風速': 'max_wind_speed_str',
            }

            # 列名を変換
            df = df.rename(columns=rename_map)

            # データ行の特定（時刻形式 "HH:MM" のパターンで判定）
            time_pattern = r'^\d{1,2}:\d{2}$'
            if 'time_str' in df.columns:
                data_mask = df['time_str'].astype(
                    str).str.match(time_pattern, na=False)
                df = df[data_mask].reset_index(drop=True)

            # 最大瞬間風向列が存在しない場合は平均風向で補完
            if 'max_wind_direction_str' not in df.columns and 'avg_wind_direction_str' in df.columns:
                df['max_wind_direction_str'] = df['avg_wind_direction_str']

            # 必須列の確認
            required_columns = [
                'time_str', 'avg_wind_direction_str', 'avg_wind_speed_str',
                'max_wind_direction_str', 'max_wind_speed_str'
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise HtmlParsingError(
                    f"必須列が不足しています: {missing}。存在する列: {df.columns.tolist()}")

            # RawWindDataDtoリストの生成
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
        except HtmlParsingError:
            raise
        except Exception as e:
            raise HtmlParsingError(f"HTML解析中に予期せぬエラーが発生しました: {e}")
