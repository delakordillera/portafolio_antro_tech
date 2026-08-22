import os
import re
import secrets
import logging
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse

security_logger = logging.getLogger('security')

REQUEST_BODY_LIMIT = 1048576  # 1 MB

BLOCKED_USER_AGENTS = [
    r'nikto', r'nmap', r'sqlmap', r'nessus', r'openvas',
    r'w3af', r'arachni', r'husk', r'dirbuster', r'gobuster',
    r'ffuf', r'wfuzz', r'burpsuite', r'owasp', r'masscan',
    r'havij', r'acunetix', r'qualys', r'zaproxy', r'medusa',
    r'hhydra', r'brutus', r'hydra', r'ncrack',
]


def get_client_ip(request):
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class NonceMiddleware:
    """
    Generates a cryptographically secure nonce per request for CSP.
    Accessible in templates as {{ request.nonce }}.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.nonce = secrets.token_urlsafe(32)
        response = self.get_response(request)
        return response


class SecurityMiddleware:
    """
    Bot blocking, body size limit, security headers, CSP with nonces.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Block scanner bots
        ua = request.META.get('HTTP_USER_AGENT', '').lower()
        for pattern in BLOCKED_USER_AGENTS:
            if re.search(pattern, ua, re.IGNORECASE):
                security_logger.warning(
                    'Blocked scanner bot: UA=%s IP=%s path=%s',
                    ua[:100], get_client_ip(request), request.path
                )
                return HttpResponseForbidden('Access denied.')

        # 2. Body size limit (POST/PUT)
        if request.method in ('POST', 'PUT', 'PATCH'):
            content_length = request.META.get('CONTENT_LENGTH', '')
            if content_length and content_length.isdigit():
                if int(content_length) > REQUEST_BODY_LIMIT:
                    return JsonResponse({'error': 'Request too large.'}, status=413)

        # 3. Security headers
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '0'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'

        # 4. Content-Security-Policy with nonce (no unsafe-inline/unsafe-eval)
        nonce = getattr(request, 'nonce', '')
        is_html = (
            request.headers.get('Accept', '').startswith('text/html')
            or request.path.endswith('/')
            or request.path == ''
        )
        if is_html and nonce:
            csp = (
                f"default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                f"img-src 'self' data: https: blob:; "
                f"font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com data:; "
                f"connect-src 'self'; "
                f"frame-ancestors 'none'; "
                f"base-uri 'self'; "
                f"form-action 'self'; "
                f"upgrade-insecure-requests"
            )
            response['Content-Security-Policy'] = csp

        return response
