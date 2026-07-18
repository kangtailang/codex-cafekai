# 使えるようにするための次の手順

このリポジトリは、現時点では「イベントCSVを入れると、LINEリッチメッセージ用のSVG画像を3枚作る」段階です。
実運用で使い始めるには、以下の順番で進めてください。

## 1. イベント情報をCSVにする

まず、`sample_events.csv` と同じ形式でイベント一覧を作ります。

```csv
location,date,weekday,time,title
天神,2026-06-20,土,11:00,３大価値観トークカフェ会
博多,2026-06-20,土,12:00,40代50代の為のパートナー探しのカフェ会
```

必要な列は以下です。

| 列名 | 内容 | 例 |
| --- | --- | --- |
| `location` | 開催場所 | `天神` |
| `date` | 開催日 | `2026-06-20` |
| `weekday` | 曜日 | `土` |
| `time` | 開始時間 | `11:00` |
| `title` | カフェ会タイトル | `３大価値観トークカフェ会` |

最初は、Claude in Chromeで取得した一覧をCSVに貼り替える運用で十分です。
その後、イベントページからCSVを自動生成する処理を追加すると、さらに省力化できます。

## 2. 生成コマンドを実行する

たとえば、2026年6月20日から6月30日までの日程画像を作る場合は、以下を実行します。

```bash
python3 cafekai_campaign.py --events sample_events.csv --start 2026-06-20 --end 2026-06-30 --output-dir output
```

成功すると、以下の3ファイルができます。

- `output/page-1.svg`
- `output/page-2.svg`
- `output/page-3.svg`

## 3. SVGをPNGに変換する

LINE公式アカウントで配信する場合は、SVGをPNGに変換して使うのが安全です。
一番簡単な方法は、SVGファイルをChromeで開いて、スクリーンショットまたはデザインツールでPNG保存する方法です。

自動変換したい場合は、次のどちらかを追加するのがおすすめです。

- PlaywrightでSVGを開いてPNG化する
- ImageMagickやInkscapeでSVGをPNGに変換する

## 4. 実際の運用フロー

おすすめの運用は以下です。

1. イベント日程ページから指定期間のイベントを取得する。
2. `events.csv` に整える。
3. `cafekai_campaign.py` を実行して3枚のSVGを作る。
4. SVGをPNGに変換する。
5. LINE公式アカウントのリッチメッセージに登録して配信する。

## 5. 次に追加すると便利な機能

優先度順に追加するなら、以下がおすすめです。

1. `https://cafekai.jp/event` から指定期間のイベントをCSV化する自動取得機能。
2. SVGからPNGへの自動変換機能。
3. 文字量が多い場合の自動フォントサイズ調整。
4. LINE配信用の完成PNGを `line-rich-message-1.png` などの名前で出力する機能。
5. 毎月の配信テンプレートを保存して再利用する機能。

## 6. まずやること

今すぐ使い始めるなら、まず以下だけで大丈夫です。

1. `sample_events.csv` をコピーして `events.csv` を作る。
2. 実際のカフェ会日程をCSV形式で入れる。
3. `python3 cafekai_campaign.py --events events.csv --start 開始日 --end 終了日 --output-dir output` を実行する。
4. `output/page-1.svg` から `output/page-3.svg` を確認する。
