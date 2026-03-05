from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Producto

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
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto_id_str = str(producto_id)

    # Recuperar el carrito actual de la sesión (o crear uno vacío)
    carrito = request.session.get('carrito', {})

    # Sumar 1 a la cantidad si ya existe, o crearlo con cantidad 1
    if producto_id_str in carrito:
        carrito[producto_id_str] += 1
    else:
        carrito[producto_id_str] = 1

    # Guardar los cambios en la sesión
    request.session['carrito'] = carrito
    request.session.modified = True  # Fuerza el guardado inmediato

    # EL CAMBIO CLAVE: Ahora redirige al carrito en lugar de la tienda
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
    # Asegúrate de tener este archivo HTML creado en tu carpeta templates
    return render(request, 'ecommerce/carrito.html', context)


def limpiar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
        request.session.modified = True
    return redirect('ver_carrito')