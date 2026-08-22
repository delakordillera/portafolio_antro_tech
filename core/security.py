import time
import re
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

# ============================================================
# RATE LIMITING — Brute-force protection
# ============================================================

LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 900  # 15 minutos
REQUEST_BODY_LIMIT = 1048576  # 1 MB

BLOCKED_USER_AGENTS = [
    r'nikto', r'nmap', r'sqlmap', r'nessus', r'openvas',
    r'w3af', r'arachni', r'husk', r'dirbuster', r'gobuster',
    r'ffuf', r'wfuzz', r'burpsuite', r'owasp', r'masscan',
    r'havij', r'acunetix', r'qualys', r'zaproxy', r'medusa',
    r'hhydra', r'brutus', r'hydra', r'ncrack', r'medusa',
]


@receiver(user_login_failed)
def record_failed_login(sender, request, credentials, **kwargs):
    username = (credentials or {}).get('username', '')
    ip = get_client_ip(request)
    key = f'login_fail:{ip}'
    attempts = cache.get(key, 0)
    cache.set(key, attempts + 1, LOGIN_ATTEMPTS_TIMEOUT)

    if username:
        user_key = f'login_fail_user:{username}'
        user_attempts = cache.get(user_key, 0)
        cache.set(user_key, user_attempts + 1, LOGIN_ATTEMPTS_TIMEOUT)


def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class RateLimitLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)

        # Bloquear IP con demasiados intentos fallidos
        key = f'login_fail:{ip}'
        attempts = cache.get(key, 0)
        if attempts >= LOGIN_ATTEMPTS_LIMIT:
            if request.path.endswith('/login/') or request.path.endswith('/admin/'):
                return JsonResponse(
                    {'error': 'Demasiados intentos. Intenta en 15 minutos.'},
                    status=429
                )

        response = self.get_response(request)
        return response


class SecurityMiddleware:
    """
    Protecciones generales: user-agent malicioso, body size, headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Bloquear bots de escaneo
        ua = request.META.get('HTTP_USER_AGENT', '').lower()
        for pattern in BLOCKED_USER_AGENTS:
            if re.search(pattern, ua, re.IGNORECASE):
                return HttpResponseForbidden('Access denied.')

        # 2. Limitar tamaño del body (POST/PUT)
        if request.method in ('POST', 'PUT', 'PATCH'):
            content_length = request.META.get('CONTENT_LENGTH', '')
            if content_length and content_length.isdigit():
                if int(content_length) > REQUEST_BODY_LIMIT:
                    return JsonResponse({'error': 'Request too large.'}, status=413)

        # 3. Headers de seguridad adicionales
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'

        return response
