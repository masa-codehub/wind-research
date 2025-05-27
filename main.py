from src.adapters.web.jma_page_fetcher_adapter import JmaPageFetcherAdapter
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput
from src.adapters.cui.argument_parser import parse_args
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# 引数解析部をインポート
# UsecaseとInput DTOをインポート


def main():
    """アプリケーションのメインエントリーポイント"""
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
        page_fetcher = JmaPageFetcherAdapter()
        usecase = CollectWindDataUsecase(page_fetcher=page_fetcher)
        usecase.execute(input_dto)

    except ValueError as e:
        # ドメイン/ユースケースレベルのエラーハンドリング
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
