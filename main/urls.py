from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('proyectos/<slug:slug>/', views.proyecto, name='proyecto'),
]
