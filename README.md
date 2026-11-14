# yakitori-nextcircle.com

焼鳥 ネクストサークル の公式サイト用リポジトリです。

## 構成

- `index.html` – トップページ（雛形）
- `css/style.css` – スタイル
- `images/` – 店舗写真・ロゴ置き場
- `site.config.json` – 店名・住所・営業時間などのサイト情報
- `CNAME` – GitHub Pages で独自ドメインを使うための設定（yakitori-nextcircle.com）

## ローカルで確認

```bash
python -m http.server 8000
```

ブラウザで http://localhost:8000 を開きます。

## 公開までの流れ

1. GitHub にこのリポジトリを push する
2. Settings → Pages で `main` ブランチ / ルートを公開元に設定する
3. Squarespace のドメイン管理で DNS を GitHub Pages に向ける（A レコード 4 件 + www の CNAME）
4. Pages 設定で "Enforce HTTPS" を有効にする
