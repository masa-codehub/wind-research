import argparse


def parse_args(args=None):
    """コマンドライン引数を解析して返す。argsが指定された場合はそれを使う（テスト用）"""
    parser = argparse.ArgumentParser(description="風況データ収集ツール")
    parser.add_argument("--prefecture_no", required=True, help="都道府県番号")
    parser.add_argument("--block_no", required=True, help="地点番号")
    parser.add_argument("--start_date", required=True,
                        help="開始年月日 (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, required=True, help="取得日数")

    return parser.parse_args(args)
