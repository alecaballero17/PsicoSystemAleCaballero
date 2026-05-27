import requests
import time
import sys

url = "https://psicosystem-api.onrender.com/"
print(f"Monitoreando {url}...")

start_time = time.time()
while True:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code < 500:
            print(f"\n[OK] SERVIDOR LISTO! Codigo: {response.status_code} - Response: {response.text[:100]}")
            sys.exit(0)
        else:
            print(f"[REINICIANDO] Codigo {response.status_code}...")
    except requests.exceptions.RequestException as e:
        print(f"[ESPERANDO] Servidor inaccesible: {e}...")
    
    if time.time() - start_time > 600:
        print("\n[ERROR] Tiempo de espera agotado.")
        sys.exit(1)
        
    time.sleep(10)
