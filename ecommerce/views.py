from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.http import require_POST
from django.views.decorators.session import cycle_session_key
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from core.security import get_client_ip
from comunidad.forms import LoginForm, RegistroForm
from .models import Producto

LOGIN_ATTEMPTS_LIMIT = 5

# ==========================================
# 1. FUNCIÓN PRINCIPAL (Catálogo y Filtros)
# ==========================================
def lista_productos(request):
    productos = Producto.objects.all()

    query = request.GET.get('q')
    categoria = request.GET.get('categoria')
    ofertas = request.GET.get('ofertas')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    if categoria:
        if categoria == 'gpu':
            productos = productos.filter(
                Q(nombre__icontains='tarjeta de video') | Q(nombre__icontains='gráfica') |
                Q(nombre__icontains='grafica') | Q(nombre__icontains='rtx') |
                Q(nombre__icontains='rx') | Q(nombre__icontains='gtx') | Q(nombre__icontains='gpu')
            )
        elif categoria == 'cpu':
            productos = productos.filter(
                Q(nombre__icontains='procesador') | Q(nombre__icontains='ryzen') |
                Q(nombre__icontains='intel') | Q(nombre__icontains='core') | Q(nombre__icontains='cpu')
            )
        elif categoria == 'ram':
            productos = productos.filter(
                Q(nombre__icontains='ram') | Q(nombre__icontains='memoria') |
                Q(nombre__icontains='nvme') | Q(nombre__icontains='ssd') | Q(nombre__icontains='disco')
            )
        else:
            productos = productos.filter(nombre__icontains=categoria)

    if ofertas:
        productos = productos.order_by('precio')[:8]

    carrito = request.session.get('carrito', {})
    total_items = sum(carrito.values())

    context = {
        'productos': productos,
        'total_items': total_items
    }
    return render(request, 'ecommerce/lista_productos.html', context)


# ==========================================
# 2. FUNCIONES DEL CARRITO DE COMPRAS
# ==========================================
@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto_id_str = str(producto_id)

    carrito = request.session.get('carrito', {})

    if producto_id_str in carrito:
        carrito[producto_id_str] += 1
    else:
        carrito[producto_id_str] = 1

    request.session['carrito'] = carrito
    request.session.modified = True

    return redirect('ver_carrito')


def ver_carrito(request):
    carrito_session = request.session.get('carrito', {})
    items_carrito = []
    total_compra = 0
    total_items = 0

    for producto_id_str, cantidad in carrito_session.items():
        producto = get_object_or_404(Producto, id=int(producto_id_str))
        subtotal = producto.precio * cantidad
        total_compra += subtotal
        total_items += cantidad

        items_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })

    context = {
        'items_carrito': items_carrito,
        'total_compra': total_compra,
        'total_items': total_items
    }
    return render(request, 'ecommerce/carrito.html', context)


@require_POST
def limpiar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
        request.session.modified = True
    return redirect('ver_carrito')


# ==========================================
# 3. AUTENTICACIÓN EXCLUSIVA ECOMMERCE
# ==========================================
@cycle_session_key
def registro_ecommerce(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_productos')
    else:
        form = RegistroForm()
    return render(request, 'ecommerce/registro.html', {'form': form})

@cycle_session_key
def login_ecommerce(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('lista_productos')
            else:
                from django.contrib import messages
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'ecommerce/login.html', {'form': form})

@require_POST
def logout_ecommerce(request):
    logout(request)
    return redirect('lista_productos')