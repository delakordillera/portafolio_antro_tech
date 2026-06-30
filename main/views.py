from django.shortcuts import render
from .models import Perfil, Proyecto, Skill
import os, subprocess
from django.http import HttpResponse

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
    }

    return render(request, 'main/home.html', context)

def git_sync(request):
    os.chdir('/home/delakordillera/red-apoyo-mutuo')
    r1 = subprocess.run(['git', 'add', '-A'], capture_output=True, text=True)
    r2 = subprocess.run(['git', 'commit', '-m', 'sync: merge servidor con GitHub'], capture_output=True, text=True)
    r3 = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
    output = 'add: ' + r1.stdout + r1.stderr + '\ncommit: ' + r2.stdout + r2.stderr + '\npush: ' + r3.stdout + r3.stderr
    return HttpResponse('<pre>' + output + '</pre>')