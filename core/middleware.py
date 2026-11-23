"""
Custom Security Headers Middleware for Abhiram Anil Portfolio.
Applies Content-Security-Policy (CSP), Permissions-Policy, Cross-Origin-Opener-Policy,
and defensive headers to protect against XSS, clickjacking, MIME-sniffing, and data exfiltration.
"""

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Robust Content-Security-Policy
        self.csp_header = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
        )

        # Strict Permissions-Policy (Feature Policy)
        self.permissions_policy = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=(), "
            "interest-cohort=()"
        )

    def __call__(self, request):
        response = self.get_response(request)

        # Security Headers
        response['Content-Security-Policy'] = self.csp_header
        response['Permissions-Policy'] = self.permissions_policy
        response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'

        # Information disclosure minimization: strip server signature headers if present
        if 'Server' in response:
            del response['Server']
        if 'X-Powered-By' in response:
            del response['X-Powered-By']

        return response
