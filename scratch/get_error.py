import urllib.request
import re

url = "https://psicosystem-api.onrender.com/api/auth/login/"
data = b'{"username": "admin.basico", "password": "Password123"}'
headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=data, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    # strip HTML tags to read traceback clearly
    clean = re.sub('<[^<]+?>', '', body)
    clean_lines = [line.strip() for line in clean.splitlines() if line.strip()]
    with open("scratch/django_error.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(clean_lines))
    print("Wrote cleaned error log to scratch/django_error.txt")
except Exception as e:
    print("Error:", e)
