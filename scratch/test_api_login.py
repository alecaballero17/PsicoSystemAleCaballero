import urllib.request
import json

url = 'https://psicosystem-api.onrender.com/api/auth/login/'
data = json.dumps({"username": "administrador", "password": "admin123"}).encode('utf-8')
headers = {'Content-Type': 'application/json'}
req = urllib.request.Request(url, data=data, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Success:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Failed with status:", e.code)
    body = e.read()
    with open("scratch/last_login_error.html", "wb") as f:
        f.write(body)
    print("Error body written to scratch/last_login_error.html")
except Exception as e:
    print("Error:", e)
