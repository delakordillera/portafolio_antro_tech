from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('_git/', views.git_sync, name='git_sync'),
]