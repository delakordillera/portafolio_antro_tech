from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('proyectos/<slug:slug>/', views.proyecto, name='proyecto'),
    path('m/', views.medir, name='medir'),
    path('panel/metricas/', views.metricas, name='metricas'),
]
