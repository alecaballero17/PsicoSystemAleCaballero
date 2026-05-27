import urllib.request

url = "https://www.google.com"
print(f"Probando {url}...")
try:
    with urllib.request.urlopen(url, timeout=5) as r:
        print(f"SUCCESS: {r.status}")
except Exception as e:
    print(f"ERROR: {e}")
