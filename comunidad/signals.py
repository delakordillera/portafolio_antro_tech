from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from core.security import get_client_ip
import logging

security_logger = logging.getLogger('security')


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    security_logger.info(
        'Login success: %s from IP %s',
        user.username, get_client_ip(request) if request else 'unknown'
    )
