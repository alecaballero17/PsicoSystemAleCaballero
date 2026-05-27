import requests
import re

url = 'https://psicosystem-frontend.onrender.com'
try:
    r = requests.get(url)
    js_files = re.findall(r'src="(/static/js/main\.[a-z0-9]+\.js)"', r.text)
    if js_files:
        js_url = url + js_files[0]
        js_r = requests.get(js_url)
        matches = re.findall(r'https?://[a-zA-Z0-9\-\.]+(?::[0-9]+)?(?:/[a-zA-Z0-9\-\.]+)*', js_r.text)
        print('All URLs found in JS:')
        for u in set(matches):
            print('-', u)
    else:
        print('No main.js found')
except Exception as e:
    print('Error:', e)
