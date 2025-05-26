import argparse

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    コマンドライン引数を解析し、結果を格納したNamespaceオブジェクトを返す。
    
    Args:
        argv (list[str] | None, optional): 解析する引数のリスト。
                                            Noneの場合はsys.argv[1:]が使われる。
                                            Defaults to None.

    Returns:
        argparse.Namespace: 解析された引数を属性として持つオブジェクト。
    """
    parser = argparse.ArgumentParser(
        description="気象庁のウェブサイトから風況データを収集し、CSV形式で出力するツール。"
    )
    # このタスクでは引数定義は不要。
    # 今後のユーザーストーリーでここに追加していく。
    # 例: parser.add_argument(...)
    return parser.parse_args(argv)
