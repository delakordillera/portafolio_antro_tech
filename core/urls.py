from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Panel de Administración (Solo va aquí, en ningún otro archivo)
    path('admin/', admin.site.urls),

    # 2. Tu Red de Apoyo Mutuo (¡Va primero para que nada la tape!)
    path('apoyo-mutuo/', include('comunidad.urls')),

    # 3. Tu E-commerce
    path('ecommerce/', include('ecommerce.urls')),

    # 4. Tu Portafolio (Va al final como ruta base)
    path('', include('main.urls')),
]

# Configuración de archivos estáticos y multimedia
if settings.DEBUG or not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)