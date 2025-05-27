from src.usecases.ports.wind_data_output_port import FileOutputError
from src.adapters.file.csv_output_adapter import CsvOutputAdapter
from src.adapters.web.jma_url_builder import JmaUrlBuilder
from src.adapters.web.jma_page_fetcher_adapter import JmaPageFetcherAdapter
from src.adapters.web.jma_html_parser import JmaHtmlParser
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
from src.adapters.cui.argument_parser import parse_args
from src.infrastructure.logger_setup import setup_logging
import sys
import logging


def main():
    """アプリケーションのメインエントリーポイント"""
    setup_logging()
    logger = logging.getLogger(__name__)
    try:
        # 引数を解析
        args = parse_args()

        # DTOを作成
        input_dto = CollectWindDataInput(
            prefecture_no=args.prefecture_no,
            block_no=args.block_no,
            start_date_str=args.start_date,
            days=args.days,
            output_path=args.output
        )

        # Usecaseを実行
        # 依存性を注入
        html_parser = JmaHtmlParser()
        page_fetcher = JmaPageFetcherAdapter()
        url_builder = JmaUrlBuilder()
        csv_output_adapter = CsvOutputAdapter()
        usecase = CollectWindDataUsecase(
            parser=html_parser,
            logger=logger,
            page_fetcher=page_fetcher,
            url_builder=url_builder,
            output_port=csv_output_adapter
        )
        usecase.execute(input_dto)

    except ValueError as e:
        logger.error(f"パラメータが不正です: {e}")
        print(f"エラー: パラメータが不正です。\n{e}", file=sys.stderr)
        sys.exit(1)
    except FileOutputError as e:
        logger.error(f"ファイル出力エラー: {e}")
        print(f"エラー: ファイル出力に失敗しました。\n{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
