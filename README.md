<!-- filepath: /app/README.md -->
# wind-research

## 概要

本プロジェクトは、気象庁ウェブサイトから指定した地点・期間の10分毎風況データ（風向・風速）を自動収集・変換し、分析に適したCSV形式で出力するコマンドラインツールです。従来手作業で行っていたデータ収集・変換・統合作業を自動化し、作業効率とデータ品質の向上を目指します。

## 主な機能

- コマンドラインからの柔軟なパラメータ指定によるデータ収集
- 気象庁ウェブサイトからの10分毎風況データの自動取得
- HTMLテーブルからのデータ抽出と解析
- 風向・風速データの数値形式への変換（北=0度、欠損=-1等）
- 指定期間のデータの時系列統合
- UTF-8エンコーディングCSV形式でのファイル出力（同名ファイルは自動リネーム）
- 処理進捗のCUI表示とログ出力による運用支援

## 実行環境

- 本リポジトリのセットアップおよび利用ワークフローは以下の通りです。

1. **リポジトリのクローン**
   - 任意のディレクトリ（例: `~/work` など。以下「ルートディレクトリ」と呼びます）で、リポジトリを `git clone` します。
   - 例：
     ```bash
     cd ~/work           # ここがルートディレクトリ
     git clone https://github.com/masa-codehub/wind-research.git
     ```

2. **ビルド用コンテキストの配置**
   - ルートディレクトリ直下に `wind-research/.build/context` の内容をコピーします。
   - 例：
     ```bash
     cp -r wind-research/.build/context/* .
     ```

3. **環境変数ファイル（.env）の設定**
   - ルートディレクトリ直下に `.env` ファイルを作成し、必要な環境変数（プロキシ設定等が必要な場合のみ）を記述します。
   - 通常は空ファイルでも動作します。

4. **Dockerコンテナのビルド・起動**
   - ルートディレクトリで以下のコマンドを実行し、Dockerイメージのビルドとコンテナの起動を行います。
     ```bash
     docker compose up -d --build
     ```

5. **コンテナへのアクセスとツール実行**
   - ルートディレクトリで wind-research コンテナにシェルで入ります。
     ```bash
     docker compose exec wind-research bash
     ```
   - コンテナ内で `python main.py ...` の形式でコマンドを実行してください。
   - **VS CodeのDev Container機能を利用する場合**：
     - `.devcontainer/devcontainer.json` の `service` プロパティが `wind-research` になっていることを確認し、必要に応じて修正してください。
     - 例：
       ```json
       {
         "service": "wind-research",
         // ...その他の設定...
       }
       ```

- 詳細なコマンド例やオプションは、下記「使い方」セクションを参照してください。

## 使い方

### 基本コマンド例

```bash
# 1日分のデータを取得（デフォルト出力パス）
python main.py --prefecture_no 44 --block_no 47662 --start_date 2024-01-01 --days 1

# 7日分のデータを取得し、出力ファイル名を指定
python main.py --prefecture_no 51 --block_no 1638 --start_date 2024-01-01 --days 7 --output custom_output.csv

# ヘルプ表示
python main.py --help
```

## コマンドラインオプション

| オプション            | 必須/任意 | 説明                                                                 |
| --------------------- | --------- | -------------------------------------------------------------------- |
| --prefecture_no       | 必須      | 都道府県番号 (例: 44)                                                |
| --block_no            | 必須      | 地点番号 (例: 47662)                                                 |
| --start_date          | 必須      | データ取得開始日 (YYYY-MM-DD)                                        |
| --days                | 必須      | データ取得日数 (整数)                                                |
| --output              | 任意      | 出力CSVファイルのパス。省略時は自動命名                              |
| -h, --help            | 任意      | ヘルプメッセージを表示                                               |

## 出力形式

- 生成されるCSVファイルのヘッダー：

```
observed_at,avg_wind_direction_deg,avg_wind_speed_mps,max_wind_direction_deg,max_wind_speed_mps
```

- データ例：

```csv
observed_at,avg_wind_direction_deg,avg_wind_speed_mps,max_wind_direction_deg,max_wind_speed_mps
2024-01-01T00:10:00,337.5,3.3,315.0,6.4
2024-01-01T00:20:00,337.5,4.1,337.5,6.8
...
```

- 欠損値は空欄として出力されます。

## データソースと出典表記

- 本ツールは気象庁ウェブサイトから提供される過去の気象データを利用しています。
- 取得データの利用時は、気象庁の定める利用規約に従い、適切に出典を明記してください。
- 詳細は [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) を参照してください。

## ライセンス

このプロジェクトは MIT License の下で公開されています。詳細は `LICENSE` ファイルをご覧ください。