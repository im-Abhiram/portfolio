"""
Centralized Application Security Helpers:
- Trusted-proxy-aware client IP extraction (guards against X-Forwarded-For spoofing).
- Security event telemetry logging with CRLF / log-injection sanitization.
"""

import ipaddress
import logging
import re

from django.conf import settings

security_logger = logging.getLogger('security')

_SECRET_PATTERN = re.compile(r'(AIza[0-9A-Za-z\-_]{20,}|AQ\.[0-9A-Za-z\-_]{20,})')


def _sanitize_log_text(value: str, max_len: int = 300) -> str:
    """Strips newlines, carriage returns, null bytes, and potential secret tokens before logging."""
    if not value:
        return ''
    text = str(value).replace('\r', ' ').replace('\n', ' ').replace('\0', '')
    text = _SECRET_PATTERN.sub('[REDACTED_KEY]', text)
    return text.strip()[:max_len]


def get_client_ip(request) -> str:
    """
    Safely extracts and validates the client IP address.
    If DJANGO_TRUST_PROXY_HEADERS is False (default local dev), ignores client-supplied
    X-Forwarded-For headers completely to prevent rate-limit bypass spoofing.
    If True (PythonAnywhere behind nginx reverse proxy), uses HTTP_X_REAL_IP or the
    rightmost valid hop in HTTP_X_FORWARDED_FOR appended by the proxy.
    """
    trust_proxy = getattr(settings, 'TRUST_PROXY_HEADERS', False)
    remote_addr = (request.META.get('REMOTE_ADDR') or '127.0.0.1').strip()

    if trust_proxy:
        x_real_ip = (request.META.get('HTTP_X_REAL_IP') or '').strip()
        if x_real_ip:
            try:
                ipaddress.ip_address(x_real_ip)
                return x_real_ip
            except ValueError:
                pass

        x_forwarded_for = (request.META.get('HTTP_X_FORWARDED_FOR') or '').strip()
        if x_forwarded_for:
            # Rightmost entry is the IP connected directly to our trusted reverse proxy
            parts = [p.strip() for p in x_forwarded_for.split(',') if p.strip()]
            for candidate in reversed(parts):
                try:
                    ipaddress.ip_address(candidate)
                    return candidate
                except ValueError:
                    continue

    try:
        ipaddress.ip_address(remote_addr)
        return remote_addr
    except ValueError:
        return '127.0.0.1'


def log_security_event(event_type: str, details: str, request=None, level: str = 'warning'):
    """Records security audit telemetry without ever logging secrets, passwords, or cookies."""
    ip = get_client_ip(request) if request is not None else 'cli/system'
    path = _sanitize_log_text(getattr(request, 'path', ''), max_len=120) if request is not None else ''
    clean_event = _sanitize_log_text(event_type, max_len=60)
    clean_details = _sanitize_log_text(details, max_len=280)

    msg = f"[{clean_event}] ip={ip} path={path} | {clean_details}"
    log_fn = getattr(security_logger, level if level in ('info', 'warning', 'error') else 'warning')
    log_fn(msg)
