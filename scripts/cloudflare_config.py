"""wrangler.json から wrangler.deploy.json を生成する（GitHub Actions 用）。

- Cloudflare 上のゾーン（ドメイン）が active なら、独自ドメインと www を Custom Domain として追加する。
- ゾーンが未作成 / pending（ネームサーバー切替前）なら workers.dev のみでデプロイする。
- site.config.json の "cloudflare_custom_domain": false のサイトは独自ドメインを付けない。
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.cloudflare.com/client/v4"
TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        API + path, method=method, data=data,
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except Exception:
            return {"success": False, "errors": [{"message": str(e)}]}


site = json.load(open("site.config.json", encoding="utf-8"))
domain = site["domain"]
attach = site.get("cloudflare_custom_domain", True)
cfg = json.load(open("wrangler.json", encoding="utf-8"))
cfg["assets"]["directory"] = "./_site"
routes = []

if not attach:
    print(f"[cloudflare] {domain}: 独自ドメインは付けない設定（workers.dev のみ）")
elif not TOKEN:
    print("[cloudflare] CLOUDFLARE_API_TOKEN が無いためドメイン判定をスキップ")
else:
    z = api("GET", "/zones?name=" + urllib.parse.quote(domain))
    zones = z.get("result") or []
    if not z.get("success") or not zones:
        print(f"[cloudflare] {domain}: ゾーン未作成または参照不可 -> workers.dev のみ", z.get("errors"))
    elif zones[0].get("status") != "active":
        print(f"[cloudflare] {domain}: ゾーン status={zones[0].get('status')}（ネームサーバー切替待ち）-> workers.dev のみ")
    else:
        zid = zones[0]["id"]
        hosts = [domain, "www." + domain]
        # 既に Custom Domain が付いているホストはそのまま。未設定なら旧 A/AAAA/CNAME を消して衝突を防ぐ
        existing = set()
        if ACCOUNT:
            d = api("GET", f"/accounts/{ACCOUNT}/workers/domains?zone_id={zid}")
            for item in d.get("result") or []:
                existing.add(item.get("hostname"))
        for h in hosts:
            if h in existing:
                continue
            recs = api("GET", f"/zones/{zid}/dns_records?name=" + urllib.parse.quote(h))
            for r in recs.get("result") or []:
                if r.get("type") in ("A", "AAAA", "CNAME"):
                    res = api("DELETE", f"/zones/{zid}/dns_records/{r['id']}")
                    ok = "OK" if res.get("success") else res.get("errors")
                    print(f"[cloudflare] 旧レコード削除 {h} {r['type']} {r.get('content')}: {ok}")
        routes = [{"pattern": h, "custom_domain": True} for h in hosts]
        print(f"[cloudflare] {domain}: ゾーン active -> Custom Domain を設定 {hosts}")

if routes:
    cfg["routes"] = routes
else:
    cfg.pop("routes", None)

with open("wrangler.deploy.json", "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
print(json.dumps(cfg, ensure_ascii=False, indent=2))
