import sys
import logging
from src.infrastructure.logger_setup import setup_logging
# 引数解析部をインポート
from src.adapters.cui.argument_parser import parse_args
# UsecaseとInput DTOをインポート
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
from src.adapters.web.jma_html_parser import JmaHtmlParser


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
            days=args.days
        )

        # Usecaseを実行
        parser = JmaHtmlParser()
        usecase = CollectWindDataUsecase(parser=parser, logger=logger)
        usecase.execute(input_dto)

    except ValueError as e:
        logger.error(f"パラメータが不正です: {e}")
        print(f"エラー: パラメータが不正です。\n{e}", file=sys.stderr)
        sys.exit(1)
    except SystemExit as e:
        # 引数解析レベルのエラーハンドリング
        # ヘルプ表示など正常終了時は何もしない
        if e.code == 0:
            sys.exit(0)
        # argparseによる引数エラー時
        # argparseが既定のエラーメッセージを出力するため、ここでは追加のメッセージは不要
        sys.exit(e.code)


if __name__ == "__main__":
    main()
