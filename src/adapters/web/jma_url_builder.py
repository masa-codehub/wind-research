from datetime import date
from src.adapters.web.jma_config import JMA_10MIN_DATA_URL_TEMPLATE
from src.domain.models.observation_point import ObservationPointValue
from src.usecases.ports.url_builder_port import IUrlBuilder
import sys
import os
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../')))


class JmaUrlBuilder(IUrlBuilder):
    def build_jma_10min_data_url(self, point: ObservationPointValue, target_date: date) -> str:
        """設定されたテンプレートに基づきURLを生成する"""
        url = JMA_10MIN_DATA_URL_TEMPLATE.format(
            prefecture_no=point.prefecture_no,
            block_no=point.block_no,
            year=target_date.year,
            month=target_date.month,
            day=target_date.day
        )
        return url
