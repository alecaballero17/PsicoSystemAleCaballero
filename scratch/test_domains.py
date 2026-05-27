import urllib.request
import json

domains = [
    "https://psicosystem-web.onrender.com",
    "https://psicosystem-api.onrender.com"
]

endpoints = [
    "/api/docs/",
    "/api/clinicas/",
    "/"
]

for domain in domains:
    print(f"\n--- Probando Dominio: {domain} ---")
    for endpoint in endpoints:
        url = f"{domain}{endpoint}"
        print(f"Pinging {url}...")
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                print(f"SUCCESS: {r.status}")
                body = r.read().decode("utf-8")
                print("Response:", body[:200])
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}: {e.reason}")
            try:
                print("Body:", e.read().decode("utf-8")[:200])
            except:
                pass
        except Exception as e:
            print("ERROR:", e)
