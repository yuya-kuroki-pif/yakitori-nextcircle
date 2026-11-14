# yakitori-nextcircle.com

ヤキトリネクストサークル（錦糸町）の公式サイト。既存の WordPress サイトの文章・写真・構成をもとに、
GitHub Pages で公開できる静的 HTML/CSS/JS サイトとして作り直したものです。
外部フレームワーク・CDN は使用していません（Google Fonts の Noto Sans JP / Noto Serif JP のみ読み込み）。

## 構成

```
index.html                トップ（ヒーロー → 写真カルーセル → コース → お料理 → お飲み物 → 席・空間 → お知らせ → Instagram → 店舗情報 → 系列店バナー）
information/index.html    お知らせ一覧（全 11 件の本文を掲載。トップからは #news-<id> で各記事へリンク）
category/index.html       旧 URL (/category/) からの転送ページ → /information/
concept/index.html        こだわり
course/index.html         コース（入門コース・満腹コース・飲み放題プラン）
food/index.html           お料理（税込価格）
drink/index.html          お飲み物（税込価格）
space/index.html          席・空間
sister-store/index.html   系列店紹介（自店を除く 6 店舗）
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
