# yakitori-nextcircle.com

ヤキトリネクストサークル（錦糸町）の公式サイト。既存の WordPress サイトの文章・写真・構成をもとに、
GitHub Pages で公開できる静的 HTML/CSS/JS サイトとして作り直したものです。
外部フレームワーク・CDN は使用していません（Google Fonts の Noto Sans JP / Noto Serif JP のみ読み込み）。

## 構成

```
index.html                トップ（ヒーロー → 写真カルーセル → コース → お料理 → お飲み物 → 席・空間 → お知らせ → Instagram → 店舗情報）
information/index.html    お知らせ一覧（全 11 件の本文を掲載。トップからは #news-<id> で各記事へリンク）
category/index.html       旧 URL (/category/) からの転送ページ → /information/
concept/index.html        こだわり
course/index.html         コース（スタンダードコース・堪能コース・飲み放題内容）
food/index.html           お料理（税込価格）
drink/index.html          お飲み物（税込価格）
space/index.html          席・空間
privacy/index.html        プライバシーポリシー
css/style.css             共通スタイル（配色は既存サイトの Elementor kit の値を踏襲）
js/main.js                ハンバーガーメニュー / ページトップ / カルーセル複製
images/                   既存サイトから取り込んだ写真・ロゴ・背景（59 点）
site.config.json          店名・住所・電話・営業時間などのサイト情報
CNAME                     GitHub Pages の独自ドメイン設定（yakitori-nextcircle.com）
```

- すべてのページで同じヘッダー（ロゴ / グローバルナビ / WEB予約ボタン、スマホはハンバーガー）とフッターを使用
- スマホ幅では画面下に 電話 / 地図 / WEB予約 の固定バーを表示
- リンク・画像パスはルート相対（`/concept/`, `/images/...`）。独自ドメイン直下で公開する前提
- トップのカルーセルは CSS アニメーションによる自動スクロール（JS はトラックの複製のみ）
- 店舗情報の営業時間は通常営業時間。年末年始・臨時休業などの時限的な案内は「お知らせ」側に掲載

## ローカルで確認

```bash
python -m http.server 8000
```

ブラウザで http://localhost:8000 を開きます。

## 公開までの流れ

1. GitHub にこのリポジトリを push する
2. Settings → Pages で `main` ブランチ / ルートを公開元に設定する
3. ドメイン管理側で DNS を GitHub Pages に向ける（A レコード 4 件 + www の CNAME）
4. Pages 設定で "Enforce HTTPS" を有効にする

## 評価表示（トップページの Google / 食べログ）

- 表示データは `data/ratings.json`。トップページの `js/ratings.js` が読み込んで評価帯（`#ratings`）に表示する。
- **Google**: `.github/workflows/update-ratings.yml` が毎日 03:00（JST）に `scripts/update_google_rating.py` を実行し、Places API から点数・口コミ件数を取得して `data/ratings.json` を更新・コミットする。リポジトリの Secrets に `GOOGLE_MAPS_API_KEY` が必要。初回実行時に `google.query` で店舗を検索して `place_id` を保存する（`matched_name` / `matched_address` で正しい店舗か確認する）。
- **食べログ**: 自動取得は利用規約上できないため手入力。`tabelog.score` / `tabelog.count` / `tabelog.asof` を店舗ページを見て月 1 回程度更新する。
- 点数が未取得（null）の間は、その項目は表示されない。

## Cloudflare へのデプロイ

- `main` に push すると `.github/workflows/deploy-cloudflare.yml` が Cloudflare Workers（静的アセット）へデプロイする（Worker 名 `yakitori-nextcircle`）。毎日 03:30 JST にも実行され、評価データの更新を反映する。
- リポジトリの Secrets に `CLOUDFLARE_API_TOKEN` と `CLOUDFLARE_ACCOUNT_ID` が必要。
- `scripts/cloudflare_config.py` が Cloudflare 上のゾーンの状態を見て、ネームサーバー切替済み（active）なら独自ドメインと www を Custom Domain として自動で付ける。切替前は workers.dev の URL のみ。
- 設定本体は `wrangler.json`。デプロイ時に `_site/`（公開ファイルだけを集めたもの）と `wrangler.deploy.json` が生成されるが、どちらも git 管理外。
