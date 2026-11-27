import json

from django.contrib.staticfiles import finders
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
            "@type": "Person",
            "name": "Alexis Lara Viveros",
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
    return render(request, 'main/home.html', {
        'perfil': Perfil.objects.first(),
        'proyectos': proyectos,
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
