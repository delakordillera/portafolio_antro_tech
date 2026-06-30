from django.shortcuts import render
from .models import Perfil, Proyecto, Skill

def home(request):
    perfil = Perfil.objects.first()
    proyectos = Proyecto.objects.all()
    skills = Skill.objects.all()

    # Convertir tecnologias string a lista para iterar en template
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
    }

    return render(request, 'main/home.html', context)

import os, subprocess
from django.http import HttpResponse

def sync(request):
    os.chdir('/home/delakordillera/red-apoyo-mutuo')
    result = subprocess.run(['git', 'stash'], capture_output=True, text=True)
    result2 = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
    result3 = subprocess.run(['git', 'stash', 'pop'], capture_output=True, text=True)
    output = f"stash: {result.stdout}{result.stderr}\npull: {result2.stdout}{result2.stderr}\npop: {result3.stdout}{result3.stderr}"
    return HttpResponse(f"<pre>{output}</pre>")