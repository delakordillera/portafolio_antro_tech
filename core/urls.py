from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from core.security import csp_report, admin_2fa_verify

SECURITY_TXT = """Contact: mailto:delakordillera@gmail.com
Expires: 2027-01-01T00:00:00.000Z
Preferred-Languages: es en
Canonical: https://delakordillera.pythonanywhere.com/.well-known/security.txt
Policy: https://delakordillera.pythonanywhere.com/
"""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/2fa-verify/', admin_2fa_verify, name='admin_2fa_verify'),
    path('.well-known/security.txt', lambda r: HttpResponse(SECURITY_TXT, content_type='text/plain'), name='security_txt'),
    path('csp-report/', csp_report, name='csp_report'),
    path('apoyo-mutuo/', include('comunidad.urls')),
    path('ecommerce/', include('ecommerce.urls')),
    path('', include('main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)