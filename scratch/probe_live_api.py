import urllib.request
import json

BASE = "https://psicosystem-web.onrender.com/api"

def get(path):
    try:
        req = urllib.request.Request(f"{BASE}{path}", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode("utf-8", errors="replace")[:300]
        except: pass
        return {"http_error": e.code, "body": body}
    except Exception as ex:
        return {"error": str(ex)}

print("=== CLINICAS (endpoint publico) ===")
clinicas = get("/clinicas/")
print(json.dumps(clinicas, indent=2, ensure_ascii=False))

print("\n=== TEST LOGIN con administrador/admin123 ===")
try:
    data = json.dumps({"username": "administrador", "password": "admin123"}).encode()
    req = urllib.request.Request(
        f"{BASE}/auth/login/",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode())
        print("SUCCESS:", json.dumps(resp, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")[:500]
    print(f"HTTP {e.code}: {body}")
except Exception as ex:
    print("Error:", ex)

print("\n=== TEST LOGIN con admin.basico/Password123 ===")
try:
    data = json.dumps({"username": "admin.basico", "password": "Password123"}).encode()
    req = urllib.request.Request(
        f"{BASE}/auth/login/",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode())
        print("SUCCESS:", json.dumps(resp, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")[:500]
    print(f"HTTP {e.code}: {body}")
except Exception as ex:
    print("Error:", ex)
