# 技術選定: 気象庁HTMLテーブル解析ライブラリ

## 概要
気象庁のWebページから風況データ（時刻・風向・風速など）を抽出するためのHTMLパーサー実装にあたり、
主な候補である `pandas.read_html` と `Beautiful Soup` の比較検証（PoC）を行い、最適なライブラリを選定しました。

## 候補ライブラリ
- pandas.read_html（+ lxml）
- Beautiful Soup（+ lxml）

## PoC実行結果まとめ（2025年5月27日 実施）

### pandas.read_html（BeautifulSoup併用）
- BeautifulSoupでid="tablefix1"のテーブルのみを抽出し、そのHTML断片をpandas.read_htmlに渡す方式に変更。
- これにより「No tables found matching regex」や不要なテーブル混入の問題を回避し、目的のテーブルのみを確実にDataFrame化できた。
- 実行時に「検出されたテーブル数: 1」となり、`display(dfs[0])` で風況データのテーブルが正しく表示された。
- DataFrameとして一括でテーブルを扱えるため、後続処理や分析が容易。
- サンプルコード：

```python
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

with open("sample.html", "r", encoding="utf-8") as f:
    html_content = f.read()
soup = BeautifulSoup(html_content, "lxml")
table = soup.find("table", id="tablefix1")
if table:
    table_html = str(table)
    dfs = pd.read_html(StringIO(table_html), flavor="lxml")
    display(dfs[0])
```

### Beautiful Soup
- `BeautifulSoup` でHTMLをパースし、`id="tablefix1"` のテーブルを抽出できた。
- テーブル行をループし、各セルから時刻・風向・風速をテキストとして抽出できた。
- ヘッダー行のスキップやセル数のチェックなど、やや多くの記述が必要。
- テーブル構造が変化した場合や、テーブル以外の要素抽出には柔軟に対応できる。
- 実行例：

```
00:00, 北, 2.1
01:00, 北北東, 1.8
...
```

## 比較・結論（再掲）
- **実装の容易さ**: pandas.read_html（BeautifulSoup併用）は簡潔かつ堅牢。Beautiful Soup単体は柔軟だが記述量が多い。
- **安定性・保守性**: pandas.read_html（BeautifulSoup併用）は目的テーブルのみを確実に抽出でき、テーブル構造が明確な場合に強い。Beautiful Soup単体はHTML構造の変化や複雑なケースに強い。
- **推奨**: 気象庁のHTMLは整ったテーブル構造なので、pandas.read_html+BeautifulSoupの組み合わせを第一選択とする。Beautiful Soup単体は補助的に利用可能。

## 依存関係
- `requirements.in` には以下を記載済みです。
    - pandas
    - lxml
    - beautifulsoup4（比較用・補助的用途）
- 依存関係の反映:

```sh
pip-compile .build/requirements.in -o requirements.txt
```

## 基本的な使い方（推奨：BeautifulSoup併用）

```python
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

# サンプルHTMLファイルのパス
html_path = "sample.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "lxml")
table_element = soup.find("table", id="tablefix1")  # idでテーブルを特定

if table_element:
    table_html_string = str(table_element)
    # lxmlパーサーは高速かつ堅牢なため推奨
    dfs = pd.read_html(StringIO(table_html_string), flavor="lxml")
    if dfs:
        target_df = dfs[0]  # 通常リストの最初の要素
        # 必要な列を抽出（列名は実際のテーブルに合わせてください）
        # wind_data = target_df[["時刻", "風向", "風速(m/s)"]]
        # display(wind_data)
    else:
        print("指定されたIDのテーブルからDataFrameを生成できませんでした。")
else:
    print("指定されたIDのテーブルが見つかりませんでした。")
```

### サンプルHTMLについて
- 本ドキュメントのサンプルコードは、`tests/resources/sample_jma.html`（気象庁の「過去の気象データ検索」ページを保存したもの）を前提としています。
- サンプルHTMLの取得方法や構造例は、リポジトリ内 `tests/resources/` ディレクトリを参照してください。

---

本決定により、Adapter-Web層のHTMLパーサー実装は `pandas.read_html` を中心に進めてください。
