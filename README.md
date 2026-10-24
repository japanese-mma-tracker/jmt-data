# jmt-data

JAPANESE MMA TRACKER（Web版）が読む試合データです。

- `data.json` — アプリと通知サーバーが読むファイル。週に1回、自動で更新します。
- `scripts/export.py` — アプリのデータベースの書き出しから `data.json` を作るスクリプト。中身がおかしいときは書き出しません。

`data.json` の中身は `events`（大会）、`fighters`（選手）、`results`（結果）、`videos`、`meta`（更新日と出典）です。日付と時刻はすべて日本時間です。
