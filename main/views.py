from django.shortcuts import render
from .models import Perfil, Proyecto, Skill, Interes
import requests

def home(request):
    # 1. Obtención de datos de tus modelos existentes
    perfil = Perfil.objects.first()
    proyectos = Proyecto.objects.all()
    skills = Skill.objects.all()
    intereses = Interes.objects.all()

    # 2. Consumo de API Externa: Indicadores Económicos (mindicador.cl)
    try:
        # Establecemos un timeout de 5 segundos para no ralentizar la carga si la API falla
        response = requests.get("https://mindicador.cl/api", timeout=5)
        data = response.json()
        valor_dolar = f"${data['dolar']['valor']}"
    except Exception:
        valor_dolar = "No disponible"

    # 3. Datos Dinámicos para el Panel de Administración (Competencia Bootcamp)
    stats = {
        'total_proyectos': proyectos.count(),
        'total_skills': skills.count(),
        'clima_stgo': "22°C Despejado", # Simulación para Santiago
        'server_status': "Operativo (PythonAnywhere)"
    }

    # 4. Contexto unificado
    context = {
        'perfil': perfil,
        'proyectos': proyectos,
        'skills': skills,
        'intereses': intereses,
        'dolar': valor_dolar,
        'stats': stats
    }

    return render(request, 'main/home.html', context)