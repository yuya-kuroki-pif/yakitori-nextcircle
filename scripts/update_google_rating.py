"""Google マップの評価（点数・口コミ件数）を Places API (New) から取得して data/ratings.json を更新する。
GitHub Actions から毎日実行される。手元で試す場合:
  GOOGLE_MAPS_API_KEY=... python scripts/update_google_rating.py
"""
import json, os, sys, datetime, urllib.request, urllib.error, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "ratings.json"
API = "https://places.googleapis.com/v1"


def call(method, url, key, field_mask, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": field_mask,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Places API error {e.code}: {e.read().decode('utf-8', 'replace')[:500]}")


def main():
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        sys.exit("GOOGLE_MAPS_API_KEY が設定されていません（リポジトリの Settings > Secrets and variables > Actions に登録してください）")
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    g = doc.setdefault("google", {})

    if not g.get("place_id"):
        res = call("POST", f"{API}/places:searchText", key,
                   "places.id,places.displayName,places.formattedAddress",
                   {"textQuery": g["query"], "languageCode": "ja", "regionCode": "JP", "pageSize": 1})
        places = res.get("places") or []
        if not places:
            sys.exit(f"店舗が見つかりませんでした: {g['query']}")
        g["place_id"] = places[0]["id"]
        g["matched_name"] = places[0].get("displayName", {}).get("text", "")
        g["matched_address"] = places[0].get("formattedAddress", "")
        print("place_id を取得:", g["place_id"], g["matched_name"], g["matched_address"])

    res = call("GET", f"{API}/places/{g['place_id']}?languageCode=ja", key,
               "rating,userRatingCount,googleMapsUri,displayName")
    g["rating"] = res.get("rating")
    g["count"] = res.get("userRatingCount")
    if res.get("googleMapsUri"):
        g["url"] = res["googleMapsUri"]
    jst = datetime.timezone(datetime.timedelta(hours=9))
    g["updated"] = datetime.datetime.now(jst).strftime("%Y-%m-%d")
    DATA.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"更新: rating={g['rating']} count={g['count']} ({g['updated']})")


if __name__ == "__main__":
    main()
