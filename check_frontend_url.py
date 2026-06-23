import urllib.request
import re

html = urllib.request.urlopen('https://psicosystem-frontend-21h1.onrender.com/').read().decode('utf-8')
js_path_match = re.search(r'/static/js/main.[a-z0-9]+.js', html)
if js_path_match:
    js_path = js_path_match.group(0)
    js = urllib.request.urlopen('https://psicosystem-frontend-21h1.onrender.com' + js_path).read().decode('utf-8')
    urls = re.findall(r'https?://[^\s"\'\\]+', js)
    print("Found URLs in JS:")
    for url in set(urls):
        print(url)
else:
    print("Could not find JS file path in HTML")
