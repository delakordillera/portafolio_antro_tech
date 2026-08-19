from django.shortcuts import render
from .models import Perfil, Proyecto, Skill

def home(request):
    perfil = Perfil.objects.first()
    proyectos = Proyecto.objects.all()
    skills = Skill.objects.all()

    for proy in proyectos:
        if proy.tecnologias:
            proy.tech_list = [t.strip() for t in proy.tecnologias.split(",")]
        else:
            proy.tech_list = []

    context = {
        'perfil': perfil,
        'proyectos': proyectos,
        'skills_tech': skills.filter(categoria='TECH'),
        'skills_ux': skills.filter(categoria='UX'),
        'skills_soft': skills.filter(categoria='SOFT'),
        # 'credenciales' no tiene modelo propio todavía: la plantilla usa un
        # fallback fijo (ver {% empty %} en home.html). Si más adelante se
        # agrega un modelo Credencial, basta con pasarlo aquí como queryset.
        'credenciales': [],
    }

    return render(request, 'main/home.html', context)