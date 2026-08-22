import os
import re
import secrets
import logging
import json
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse

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


class AdminIPMiddleware:
    """
    Restricts /admin/ access to whitelisted IPs.
    Set ADMIN_ALLOWED_IPS in settings.py or env var.
    Empty list = no restriction (open).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_ips = getattr(settings, 'ADMIN_ALLOWED_IPS', [])
        if allowed_ips and request.path.startswith('/admin/'):
            client_ip = get_client_ip(request)
            if client_ip not in allowed_ips:
                security_logger.warning(
                    'Admin access denied: IP=%s path=%s UA=%s',
                    client_ip, request.path,
                    request.META.get('HTTP_USER_AGENT', '')[:100]
                )
                return HttpResponseForbidden(
                    'Access denied. Your IP is not authorized for admin access.'
                )
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
            csp_directives = (
                f"default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                f"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                f"img-src 'self' data: https: blob:; "
                f"font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com data:; "
                f"connect-src 'self'; "
                f"frame-ancestors 'none'; "
                f"base-uri 'self'; "
                f"form-action 'self'; "
                f"upgrade-insecure-requests; "
                f"report-uri /csp-report/"
            )
            csp_header = 'Content-Security-Policy-Report-Only' if getattr(settings, 'CSP_REPORT_ONLY', False) else 'Content-Security-Policy'
            response[csp_header] = csp_directives

        # 5. No-cache on HTML (prevents browser caching of authenticated pages)
        if is_html:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'

        return response


def cycle_session_key(view_func):
    """
    Decorator that regenerates the session key to prevent session fixation.
    Creates a fresh session and copies old data over.
    """
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        old_session = dict(request.session)
        old_key = request.session.session_key
        request.session.create()
        request.session.update(old_session)
        request.session.modified = True
        return view_func(request, *args, **kwargs)
    return wrapper


def csp_report(request):
    """
    Receives Content-Security-Policy violation reports from browsers.
    Logs the violation for monitoring.
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8', errors='replace'))
            report = body.get('csp-report', {})
            security_logger.warning(
                'CSP violation: directive=%s blocked=%s source=%s page=%s',
                report.get('violated-directive', 'unknown'),
                report.get('blocked-uri', 'none'),
                report.get('source-file', 'none'),
                report.get('document-uri', 'none'),
            )
        except Exception:
            security_logger.warning('Malformed CSP report received')
    return HttpResponse(status=204)


class Admin2FAMiddleware:
    """
    Enforces 2FA verification for admin users.
    If user is staff and has a confirmed TOTP device, they must verify
    via 2FA before accessing /admin/.
    Stores verification status in session.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path.startswith('/admin/')
            and request.user.is_authenticated
            and request.user.is_staff
            and request.path not in ('/admin/login/', '/admin/logout/')
        ):
            from django_otp import user_is_verified
            from django_otp.plugins.otp_totp.models import TOTPDevice

            has_totp = TOTPDevice.objects.filter(
                user=request.user, confirmed=True
            ).exists()

            if has_totp and not user_is_verified(request.user):
                if request.path != '/admin/2fa-verify/':
                    security_logger.warning(
                        'Admin 2FA required: %s from IP %s',
                        request.user.username, get_client_ip(request)
                    )
                    return HttpResponseRedirect('/admin/2fa-verify/')

        response = self.get_response(request)
        return response


class RateLimitPasswordReset:
    """
    Rate-limits password reset requests: max 3 per IP per hour.
    """
    MAX_REQUESTS = 3
    WINDOW = 3600  # 1 hour

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/apoyo-mutuo/restablecer/' and request.method == 'POST':
            from django.core.cache import cache
            ip = get_client_ip(request)
            cache_key = f'pwd_reset_{ip}'
            count = cache.get(cache_key, 0)
            if count >= self.MAX_REQUESTS:
                security_logger.warning(
                    'Password reset rate limit hit: IP=%s', ip
                )
                return HttpResponse(
                    'Demasiadas solicitudes. Intenta más tarde.',
                    status=429
                )
            cache.set(cache_key, count + 1, self.WINDOW)

        response = self.get_response(request)
        return response


def admin_2fa_verify(request):
    """
    Handles 2FA TOTP verification for admin access.
    GET: show code form
    POST: verify code, mark session as verified, redirect to admin
    """
    from django.shortcuts import render
    from django.contrib.auth import redirect_to_login
    from django.contrib import messages

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect_to_login(request.get_full_path())

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        from django_otp import login as otp_login
        from django_otp.plugins.otp_totp.models import TOTPDevice

        device = TOTPDevice.objects.filter(
            user=request.user, confirmed=True
        ).first()

        if device and device.verify_token(code):
            otp_login(request, device)
            security_logger.info(
                'Admin 2FA verified: %s from IP %s',
                request.user.username, get_client_ip(request)
            )
            return HttpResponseRedirect('/admin/')
        else:
            security_logger.warning(
                'Admin 2FA failed: %s from IP %s',
                request.user.username, get_client_ip(request)
            )
            messages.error(request, 'Código 2FA incorrecto.')

    return render(request, 'admin/2fa_verify.html')
