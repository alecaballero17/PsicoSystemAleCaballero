import urllib.request
import json
import sys

def fetch_url(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        return {"error": str(e)}

print("=== CLÍNICAS EN PRODUCCIÓN ===")
clinicas = fetch_url('https://psicosystem-web.onrender.com/api/clinicas/')
print(json.dumps(clinicas, indent=2, ensure_ascii=False))

print("\n=== INTENTANDO OBTENER USUARIOS (Si es público) ===")
usuarios = fetch_url('https://psicosystem-web.onrender.com/api/usuarios/')
print(json.dumps(usuarios, indent=2, ensure_ascii=False))
