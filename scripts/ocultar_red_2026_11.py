# Saca Red de Apoyo Mutuo del portafolio (nov. 2026). Uso: python manage.py shell < scripts/ocultar_red_2026_11.py
from main.models import Proyecto
n = Proyecto.objects.filter(titulo="Red de Apoyo Mutuo").update(visible=False)
print("ocultos:", n)
for p in Proyecto.objects.all():
    print(p.id, p.visible, p.titulo)
