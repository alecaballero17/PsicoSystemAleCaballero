import urllib.request
import json
import sys

url = "https://psicosystem-web.onrender.com/api/clinicas/"
print(f"Probando clinicas URL {url}...")

try:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"[STATUS] {r.status}")
        print("[BODY]")
        print(json.dumps(json.loads(r.read().decode()), indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    print(f"[HTTP ERROR] Code: {e.code}")
    try:
        body = e.read().decode("utf-8", errors="replace")[:500]
        print(f"[HTTP BODY] {body}")
    except Exception as ex:
        print(f"[COULD NOT READ HTTP BODY] {ex}")
except Exception as ex:
    print(f"[ERROR] {ex}")
