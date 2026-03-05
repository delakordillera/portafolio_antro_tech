from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal del catálogo
    path('', views.lista_productos, name='lista_productos'),

    # Rutas del carrito
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
]