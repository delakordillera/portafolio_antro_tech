import time
import re
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.contrib import messages
from django.urls import reverse

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
    # PythonAnywhere sets REMOTE_ADDR to the real client IP.
    # Never trust X-Forwarded-For from the client — it's trivially spoofable
    # and would allow complete bypass of the rate limiter.
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


RATE_LIMITED_LOGIN_PATHS = {
    '/comunidad/login/',
    '/ecommerce/login/',
    '/admin/login/',
}


class RateLimitLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)

        key = f'login_fail:{ip}'
        attempts = cache.get(key, 0)
        if attempts >= LOGIN_ATTEMPTS_LIMIT:
            if request.path in RATE_LIMITED_LOGIN_PATHS:
                if request.headers.get('Accept', '').startswith('application/json'):
                    return JsonResponse(
                        {'error': 'Demasiados intentos. Intenta en 15 minutos.'},
                        status=429
                    )
                redirect_url = request.path
                response = HttpResponseRedirect(redirect_url)
                messages.warning(
                    request,
                    'Demasiados intentos. Espera 15 minutos para volver a intentar.'
                )
                return response

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

        # 3. Headers de seguridad
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '0'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'

        # 4. Content-Security-Policy (relajado para permitir CDN de Bootstrap/Icons)
        if request.headers.get('Accept') == 'text/html' or request.path.endswith('/'):
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.jsdelivr.net/npm; "
                "img-src 'self' data: https: blob:; "
                "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "upgrade-insecure-requests"
            )
            response['Content-Security-Policy'] = csp

        return response
