from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.muro_comunitario, name='muro'),
    path('ofrecer/', views.ofrecer_habilidad, name='ofrecer'),

    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Verificación de email
    path('verificar/<str:uidb64>/<str:token>/', views.verificar_email, name='verificar_email'),

    # Restablecimiento de contraseña
    path('restablecer/', views.password_reset_request, name='password_reset'),
    path('restablecer/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),

    # Gestión de Habilidades (CRUD)
    path('solicitar/<int:habilidad_id>/', views.solicitar_intercambio, name='solicitar_intercambio'),
    path('habilidad/editar/<int:habilidad_id>/', views.editar_habilidad, name='editar_habilidad'),
    path('habilidad/eliminar/<int:habilidad_id>/', views.eliminar_habilidad, name='eliminar_habilidad'),

    # Gestión de Vínculos y Perfil
    path('perfil/', views.mi_perfil, name='perfil'),
    path('completar/<int:intercambio_id>/', views.completar_intercambio, name='completar_intercambio'),
    path('agradecer/<int:intercambio_id>/', views.dejar_agradecimiento, name='dejar_agradecimiento'),

    # 2FA Admin
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('2fa/disable/', views.disable_2fa, name='disable_2fa'),
]