import sys
# mainブランチの構造を採用し、引数解析部を別ファイルからインポート
from adapters.cui.argument_parser import parse_args 
# issue#16_01のロジックを採用し、UsecaseとInput DTOをインポート
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput

def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        # mainブランチの呼び出し構造を採用
        args = parse_args()
        
        # issue#16_01の実装を統合
        # argsからDTOを作成
        input_dto = CollectWindDataInput(
            prefecture_no=args.prefecture_no,
            block_no=args.block_no,
            start_date_str=args.start_date,
            days=args.days
        )

        # issue#16_01の実装を統合
        # Usecaseを実行
        usecase = CollectWindDataUsecase()
        usecase.execute(input_dto)

    except ValueError as e:
        # issue#16_01のドメイン/ユースケースレベルのエラーハンドリングを採用
        print(f"エラー: パラメータが不正です。\n{e}", file=sys.stderr)
        sys.exit(1)
    except SystemExit as e:
        # mainブランチの引数解析レベルのエラーハンドリングを採用
        # ヘルプ表示など正常終了時は何もしない
        if e.code == 0:
            sys.exit(0)
        # argparseによる引数エラー時
        # argparseが既定のエラーメッセージを出力するため、ここでは追加のメッセージは不要
        sys.exit(e.code)

if __name__ == "__main__":
    main()