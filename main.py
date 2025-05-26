from adapters.cui.argument_parser import parse_args

def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        args = parse_args()
        print("引数の解析に成功しました。")
        # 今後、ここでargsを使ってUseCaseを呼び出す
    except SystemExit as e:
        # argparseはヘルプ表示時やエラー時にSystemExitを発生させる
        # 正常終了(コード0)の場合、ここでは何もせず終了させる
        if e.code != 0:
            # エラーの場合は、必要に応じてログ出力など
            print(f"引数解析エラー: {e}")

if __name__ == "__main__":
    main()
