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


def ensure_workers_subdomain():
    """workers.dev サブドメインが未登録なら登録する（アカウント共通・1 回だけ）。"""
    if not TOKEN or not ACCOUNT:
        return
    cur = api("GET", f"/accounts/{ACCOUNT}/workers/subdomain")
    if cur.get("success") and (cur.get("result") or {}).get("subdomain"):
        print(f"[cloudflare] workers.dev サブドメイン: {cur['result']['subdomain']}.workers.dev")
        return
    for name in ("pay-it-forward", "pif-stores", "pif-sites", "pif-" + ACCOUNT[:8]):
        res = api("PUT", f"/accounts/{ACCOUNT}/workers/subdomain", {"subdomain": name})
        if res.get("success"):
            print(f"[cloudflare] workers.dev サブドメインを登録: {name}.workers.dev")
            return
        print(f"[cloudflare] サブドメイン {name} は登録できず: {res.get('errors')}")
    print("[cloudflare] workers.dev サブドメインを登録できませんでした。ダッシュボード Workers & Pages で手動登録してください")


ensure_workers_subdomain()


def ensure_dns_records():
    """site.config.json の dns_records（メール用 MX/SPF など）が無ければ作成する。ゾーンが pending でも作れる。"""
    recs = site.get("dns_records") or []
    if not recs or not TOKEN:
        return
    z = api("GET", "/zones?name=" + urllib.parse.quote(domain))
    zones = z.get("result") or []
    if not zones:
        print(f"[cloudflare] {domain}: ゾーン未作成のため dns_records をスキップ")
        return
    zid = zones[0]["id"]
    for rec in recs:
        name = domain if rec["name"] in ("@", domain) else f"{rec['name']}.{domain}"
        cur = api("GET", f"/zones/{zid}/dns_records?type={rec['type']}&name=" + urllib.parse.quote(name))
        if cur.get("result"):
            print(f"[cloudflare] DNS {rec['type']} {name}: 既存")
            continue
        body = {"type": rec["type"], "name": name, "content": rec["content"], "ttl": 1,
                "proxied": bool(rec.get("proxied", False))}
        if rec["type"] == "MX":
            body["priority"] = int(rec.get("priority", 0))
        if rec["type"] in ("MX", "TXT"):
            body.pop("proxied", None)
        res = api("POST", f"/zones/{zid}/dns_records", body)
        ok = "作成" if res.get("success") else res.get("errors")
        print(f"[cloudflare] DNS {rec['type']} {name} -> {rec['content']}: {ok}")


ensure_dns_records()

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
