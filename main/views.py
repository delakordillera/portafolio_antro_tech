import json

from django.shortcuts import render

from .models import Perfil, Proyecto, Skill

SITIO = "https://delakordillera.pythonanywhere.com"


def _jsonld(proyecto, request):
    """Schema.org del proyecto destacado. Se arma en Python para no arriesgar
    JSON inválido por interpolar texto del admin dentro del <script>."""
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


def home(request):
    perfil = Perfil.objects.first()
    proyectos = list(Proyecto.objects.filter(visible=True))

    destacado = next((p for p in proyectos if p.destacado), None)

    for proy in proyectos:
        if proy.tecnologias:
            proy.tech_list = [t.strip() for t in proy.tecnologias.split(',') if t.strip()]
        else:
            proy.tech_list = []
        # La imagen del admin solo se usa si el archivo existe en el servidor;
        # si no, la tarjeta cae a la captura estática o al placeholder.
        proy.cover_url = proy.imagen.url if proy.imagen_existe else None

    context = {
        'perfil': perfil,
        'proyectos': proyectos,
        'destacado': destacado,
        'jsonld_destacado': _jsonld(destacado, request),
        'skills_tech': Skill.objects.filter(categoria='TECH'),
        'skills_ux': Skill.objects.filter(categoria='UX'),
        'skills_soft': Skill.objects.filter(categoria='SOFT'),
        # 'credenciales' no tiene modelo propio todavía: la plantilla usa un
        # fallback fijo (ver {% empty %} en home.html). Si más adelante se
        # agrega un modelo Credencial, basta con pasarlo aquí como queryset.
        'credenciales': [],
    }

    return render(request, 'main/home.html', context)
