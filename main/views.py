import json

from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.urls import reverse
from django.http import Http404
from django.shortcuts import render
from django.utils.text import slugify

from .models import Perfil, Proyecto

SITIO = "https://delakordillera.pythonanywhere.com"

# Color de marca de cada cliente, tomado de su propio sitio. Se usa como
# fondo de las capturas: cada proyecto se presenta con su identidad.
MARCAS = {
    'la-otra-estacion': '#B3121D',
    'ps-franco-alvarez': '#24453A',
    'red-de-apoyo-mutuo': '#0D5FD8',
    'plataforma-ecommerce': '#0B3A4A',
}
MARCA_POR_DEFECTO = '#3C4658'


def _jsonld(proyecto, request):
    """Schema.org del proyecto. Se arma en Python para no arriesgar JSON
    inválido por interpolar texto del admin dentro del <script>."""
    if not proyecto:
        return ""

    datos = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": proyecto.titulo,
        "url": proyecto.url_produccion or request.build_absolute_uri(),
        "description": proyecto.descripcion_corta,
        "creator": {
            "@type": "Organization",
            "name": "delakordillera",
            "url": SITIO,
        },
    }
    if proyecto.anio:
        datos["dateCreated"] = proyecto.anio
    if proyecto.cliente:
        datos["about"] = {"@type": "Organization", "name": proyecto.cliente}
    if proyecto.tech_list:
        datos["keywords"] = ", ".join(proyecto.tech_list)

    return json.dumps(datos, ensure_ascii=False)


def _variante(src, ancho):
    """Ruta de la versión reducida de una captura (foo.webp -> foo-900.webp),
    solo si el archivo existe."""
    if not src or not src.endswith('.webp'):
        return None
    candidata = src[:-5] + f'-{ancho}.webp'
    return candidata if finders.find(candidata) else None


def _preparar(proyectos):
    for proy in proyectos:
        proy.slug = slugify(proy.titulo)
        proy.marca = MARCAS.get(proy.slug, MARCA_POR_DEFECTO)
        proy.tech_list = [t.strip() for t in (proy.tecnologias or '').split(',') if t.strip()]
        # La imagen del admin solo se usa si el archivo existe en el servidor.
        proy.cover_url = proy.imagen.url if proy.imagen_existe else None

        escritorio = proy.captura_por_rol('escritorio') or proy.captura_portada
        movil = proy.captura_por_rol('movil')
        proy.shot = escritorio
        proy.shot_900 = _variante(escritorio.get('src'), 900) if escritorio else None
        # Precedencia: imagen subida en el admin > captura estática.
        if proy.cover_url:
            proy.shot_url, proy.shot_900_url = proy.cover_url, None
        else:
            proy.shot_url = static(escritorio['src']) if escritorio else None
            proy.shot_900_url = static(proy.shot_900) if proy.shot_900 else None
        proy.shot_movil = movil
        # Capturas extra para la página del caso (ni portada ni celular).
        usadas = {c.get('src') for c in (escritorio, movil) if c}
        proy.extras = [
            c for c in (proy.capturas or [])
            if c.get('src') and c.get('src') not in usadas and c.get('pie')
        ]
    return proyectos


def _visibles():
    # Destacado primero, luego trabajos para clientes (con sitio en producción).
    proyectos = sorted(
        Proyecto.objects.filter(visible=True),
        key=lambda p: (not p.destacado, not p.url_produccion, p.id),
    )
    return _preparar(proyectos)


def home(request):
    proyectos = _visibles()
    # Datos mínimos para el armador de proyecto (se leen con json_script).
    casos_json = [
        {
            'slug': p.slug,
            'titulo': p.titulo,
            'marca': p.marca,
            'url': reverse('proyecto', args=[p.slug]),
            'imagen': p.shot_900_url or p.shot_url or '',
        }
        for p in proyectos
    ]
    # La tienda de práctica no está en la galería, pero sí sirve como ejemplo
    # en el cotizador para "Comercio o tienda".
    tienda = Proyecto.objects.filter(titulo='Plataforma Ecommerce').first()
    if tienda:
        _preparar([tienda])
        casos_json.append({
            'slug': tienda.slug,
            'titulo': 'Tienda en línea',
            'marca': tienda.marca,
            'url': tienda.link_interno or '/ecommerce/',
            'imagen': tienda.shot_900_url or tienda.shot_url or '',
        })
    return render(request, 'main/home.html', {
        'perfil': Perfil.objects.first(),
        'proyectos': proyectos,
        'casos_json': casos_json,
    })


def proyecto(request, slug):
    proyectos = _visibles()
    for i, proy in enumerate(proyectos):
        if proy.slug == slug:
            siguiente = proyectos[(i + 1) % len(proyectos)] if len(proyectos) > 1 else None
            return render(request, 'main/proyecto.html', {
                'perfil': Perfil.objects.first(),
                'proyecto': proy,
                'siguiente': siguiente,
                'jsonld': _jsonld(proy, request),
            })
    raise Http404("Proyecto no encontrado")


# --- Medición propia: sin cookies, sin IP, sin terceros -------------------
import hashlib
from datetime import timedelta
from urllib.parse import urlparse

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Evento

_TIPOS_VALIDOS = {t for t, _ in Evento.TIPOS}
_BOTS = ('bot', 'crawl', 'spider', 'slurp', 'preview', 'headless', 'lighthouse')


@csrf_exempt
@require_POST
def medir(request):
    """Recibe un evento por sendBeacon. Siempre responde 204 para no filtrar nada."""
    agente = request.META.get('HTTP_USER_AGENT', '').lower()
    if not agente or any(b in agente for b in _BOTS) or request.META.get('HTTP_SEC_PURPOSE', '').startswith('prefetch'):
        return HttpResponse(status=204)
    # Tope de 120 eventos por hora por visitante, sin guardar la IP (solo un hash temporal en caché).
    huella = hashlib.sha256((request.META.get('REMOTE_ADDR', '') + agente).encode()).hexdigest()[:24]
    clave = f'medir:{huella}'
    usados = cache.get(clave, 0)
    if usados >= 120:
        return HttpResponse(status=204)
    cache.set(clave, usados + 1, 3600)
    try:
        datos = json.loads(request.body[:2000] or b'{}')
    except ValueError:
        return HttpResponse(status=204)
    tipo = str(datos.get('t', ''))[:20]
    if tipo not in _TIPOS_VALIDOS:
        return HttpResponse(status=204)
    origen = urlparse(str(datos.get('r', ''))[:300]).netloc.lower().removeprefix('www.')
    if origen == request.get_host().lower():
        origen = ''
    Evento.objects.create(
        tipo=tipo,
        ruta=str(datos.get('p', ''))[:200],
        origen=origen[:120],
        dispositivo='celular' if any(m in agente for m in ('mobile', 'android', 'iphone')) else 'computador',
    )
    return HttpResponse(status=204)


@staff_member_required
def metricas(request):
    """Resumen privado de los últimos 7 y 30 días."""
    ahora = timezone.now()
    nombres = dict(Evento.TIPOS)

    def periodo(dias):
        qs = Evento.objects.filter(fecha__gte=ahora - timedelta(days=dias))
        conteo = {f['tipo']: f['n'] for f in qs.values('tipo').annotate(n=Count('id'))}
        visitas = conteo.get('visita', 0)
        cotizar = conteo.get('cotizar', 0) + conteo.get('burbuja', 0)
        return {
            'filas': [(nombres[t], conteo.get(t, 0)) for t, _ in Evento.TIPOS],
            'visitas': visitas,
            'tasa': round(100 * conteo.get('consulta', 0) / visitas, 1) if visitas else 0,
            'interes': round(100 * cotizar / visitas, 1) if visitas else 0,
            'origenes': list(qs.filter(tipo='visita').exclude(origen='').values('origen').annotate(n=Count('id')).order_by('-n')[:8]),
            'paginas': list(qs.filter(tipo='visita').values('ruta').annotate(n=Count('id')).order_by('-n')[:8]),
            'dispositivos': list(qs.filter(tipo='visita').values('dispositivo').annotate(n=Count('id')).order_by('-n')),
        }

    respuesta = render(request, 'main/metricas.html', {'periodos': [('Últimos 7 días', periodo(7)), ('Últimos 30 días', periodo(30))]})
    respuesta['X-Robots-Tag'] = 'noindex'
    return respuesta
