from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('registro/', views.registro_ecommerce, name='registro_ecommerce'),
    path('login/', views.login_ecommerce, name='login_ecommerce'),
    path('logout/', views.logout_ecommerce, name='logout_ecommerce'),
]