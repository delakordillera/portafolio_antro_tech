from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroForm, HabilidadForm, PerfilForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Habilidad, Intercambio, Perfil
from django.contrib import messages
from django.db.models import Q, F
from django.views.decorators.http import require_POST

# --- GESTIÓN DEL MURO Y BÚSQUEDA ---

def muro_comunitario(request):
    """
    Visualización principal con filtros de búsqueda y testimonios.
    Implementación del Paso 4: Visibilización del Círculo de Gratitud.
    """
    query = request.GET.get('q')
    habilidades = Habilidad.objects.all().order_by('-id')

    # --- NUEVA LÓGICA PASO 4 ---
    # Traemos los últimos 5 testimonios (intercambios completados con comentario)
    agradecimientos = Intercambio.objects.filter(
        completado=True
    ).exclude(comentario_gratitud="").order_by('-id')[:5]

    if query:
        habilidades = habilidades.filter(
            Q(titulo__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(categoria__icontains=query)
        )

    return render(request, 'comunidad/muro.html', {
        'habilidades': habilidades,
        'agradecimientos': agradecimientos, # Enviamos los testimonios al muro
        'query': query
    })

# --- GESTIÓN DE HABILIDADES (CRUD) ---

@login_required
def ofrecer_habilidad(request):
    if request.method == 'POST':
        form = HabilidadForm(request.POST, request.FILES) 
        if form.is_valid():
            habilidad = form.save(commit=False)
            habilidad.ofertante = request.user
            habilidad.save()
            messages.success(request, "¡Excelente! Tu oficio ya está disponible.")
            return redirect('muro')
    else:
        form = HabilidadForm()
    return render(request, 'comunidad/ofrecer.html', {'form': form})

@login_required
def editar_habilidad(request, habilidad_id):
    habilidad = get_object_or_404(Habilidad, id=habilidad_id, ofertante=request.user)
    
    if request.method == 'POST':
        form = HabilidadForm(request.POST, request.FILES, instance=habilidad)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu oficio ha sido actualizado exitosamente.")
            return redirect('perfil')
    else:
        form = HabilidadForm(instance=habilidad)
    
    return render(request, 'comunidad/ofrecer.html', {
        'form': form,
        'editando': True 
    })

@login_required
def eliminar_habilidad(request, habilidad_id):
    habilidad = get_object_or_404(Habilidad, id=habilidad_id, ofertante=request.user)
    
    if request.method == 'POST':
        habilidad.delete()
        messages.warning(request, "Has retirado tu oficio de la red comunitaria.")
        return redirect('perfil')
    
    return render(request, 'comunidad/confirmar_eliminar.html', {'habilidad': habilidad})

# --- GESTIÓN DE INTERCAMBIOS Y CAPITAL SOCIAL ---

@login_required
@require_POST
def solicitar_intercambio(request, habilidad_id):
    habilidad = get_object_or_404(Habilidad, id=habilidad_id)
    
    if habilidad.ofertante == request.user:
        messages.warning(request, "No puedes solicitar tu propio oficio.")
        return redirect('muro')
    
    ya_existe = Intercambio.objects.filter(solicitante=request.user, habilidad=habilidad).exists()
    
    if not ya_existe:
        Intercambio.objects.create(solicitante=request.user, habilidad=habilidad)
        messages.success(request, f'Has solicitado con éxito "{habilidad.titulo}"')
    else:
        messages.info(request, "Ya has solicitado esto.")
    
    return redirect('muro')

@login_required
@require_POST
def completar_intercambio(request, intercambio_id):
    intercambio = get_object_or_404(Intercambio, id=intercambio_id)
    
    if intercambio.habilidad.ofertante == request.user and not intercambio.completado:
        intercambio.completado = True
        intercambio.save()
        
        perfil_solicitante, created = Perfil.objects.get_or_create(usuario=intercambio.solicitante)
        Perfil.objects.filter(pk=perfil_solicitante.pk).update(puntos_confianza=F('puntos_confianza') + 1)
        
        messages.success(request, f"¡Favor completado! Has fortalecido el vínculo con {intercambio.solicitante.username}.")
    else:
        messages.error(request, "Acción no permitida o ya completada.")
    
    return redirect('perfil')

@login_required
@require_POST
def dejar_agradecimiento(request, intercambio_id):
    intercambio = get_object_or_404(Intercambio, id=intercambio_id)
    
    if intercambio.solicitante == request.user and intercambio.completado:
        comentario = request.POST.get('comentario', '').strip()
        if comentario:
            intercambio.comentario_gratitud = comentario
            intercambio.save()
            messages.success(request, "¡Agradecimiento enviado! Tu testimonio fortalece la confianza.")
    
    return redirect('perfil')

# --- USUARIOS Y PERFILES ---

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido/a {user.username}! Ya eres parte de esta red.")
            return redirect('muro')
    else:
        form = RegistroForm()
    return render(request, 'comunidad/registro.html', {'form': form})

@login_required
def mi_perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Tu biografía ha sido actualizada!")
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'comunidad/perfil.html', {
        'form': form,
        'mis_habilidades': Habilidad.objects.filter(ofertante=request.user),
        'mis_pedidos': Intercambio.objects.filter(solicitante=request.user),
        'pedidos_recibidos': Intercambio.objects.filter(habilidad__ofertante=request.user),
        'puntos': perfil.puntos_confianza
    })