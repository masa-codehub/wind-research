import argparse
import sys
from src.usecases.collect_wind_data_usecase import CollectWindDataUsecase, CollectWindDataInput


def main():
    parser = argparse.ArgumentParser(description="風況データ収集ツール")
    parser.add_argument("--prefecture_no", required=True, help="都道府県番号")
    parser.add_argument("--block_no", required=True, help="地点番号")
    parser.add_argument("--start_date", required=True,
                        help="開始年月日 (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, required=True, help="取得日数")

    args = parser.parse_args()

    input_dto = CollectWindDataInput(
        prefecture_no=args.prefecture_no,
        block_no=args.block_no,
        start_date_str=args.start_date,
        days=args.days
    )

    usecase = CollectWindDataUsecase()
    try:
        usecase.execute(input_dto)
    except ValueError as e:
        print(f"エラー: パラメータが不正です。\n{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
