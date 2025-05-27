import sys
import logging
from src.infrastructure.logger_setup import setup_logging
from src.adapters.cui.argument_parser import parse_args
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
from src.adapters.web.jma_html_parser import JmaHtmlParser
from src.adapters.web.jma_page_fetcher_adapter import JmaPageFetcherAdapter  # mainブランチの変更
from src.adapters.web.jma_url_builder import JmaUrlBuilder  # 追加: JmaUrlBuilderのインポート

# issue#21_01ブランチの sys.path.insert は、
# プロジェクト構造とPYTHONPATHが適切に設定されていれば通常不要なため、
# よりクリーンな import logging のみを残します。


def main():
    """アプリケーションのメインエントリーポイント"""
    setup_logging()  # issue#21_01ブランチの変更
    logger = logging.getLogger(__name__)  # issue#21_01ブランチの変更
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
        # 依存性を注入
        html_parser = JmaHtmlParser()  # issue#21_01ブランチの変更
        page_fetcher = JmaPageFetcherAdapter()  # mainブランチの変更
        url_builder = JmaUrlBuilder()  # 追加: url_builderのインスタンス生成

        # CollectWindDataUsecase のコンストラクタに合わせて引数を設定
        # issue#21_01 では (parser, logger), main では (page_fetcher)
        # 両方の機能が必要になるため、CollectWindDataUsecase のコンストラクタが
        # これら両方（または必要なもの）を受け取るように変更されていることを想定します。
        # ここでは、両方のブランチの意図を汲み、全てを渡す形を仮定します。
        # 実際の CollectWindDataUsecase の定義に合わせて調整が必要です。
        usecase = CollectWindDataUsecase(
            parser=html_parser,
            logger=logger,
            page_fetcher=page_fetcher,
            url_builder=url_builder
        )
        usecase.execute(input_dto)

    except ValueError as e:
        logger.error(f"パラメータが不正です: {e}")  # issue#21_01ブランチの変更
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
