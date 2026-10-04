"""Apunta las miniaturas de tarjeta a la version optimizada en static/.

Por que: los tres JPEG que estaban en media/ pesan 856 KB en conjunto y cada
uno tiene una proporcion distinta (1.76, 1.28, 1.62), lo que dejaba las
tarjetas con alturas diferentes. Las versiones en static/main/proyectos/ son
4:3 (720x540), WebP y pesan entre 29 y 40 KB.

Se limpia `imagen` a proposito: mientras apunte al JPEG, el template prioriza el
upload del admin y la version optimizada nunca se ve. El campo sigue editable
en el admin, asi que subir una foto nueva vuelve a tomar precedencia sobre el
archivo estatico. El JPEG no se borra de media/, queda como respaldo.

Idempotente: si ya hay capturas con rol "tarjeta", no toca nada.
"""

from django.db import migrations

MINIATURAS = {
    "Red de Apoyo Mutuo": {
        "src": "main/proyectos/apoyo-mutuo.webp",
        "alt": "Portada de Red de Apoyo Mutuo, el muro de oficios del barrio",
        "imagen_anterior": "apoyo-mutuo.jpg",
    },
    "Plataforma Ecommerce": {
        "src": "main/proyectos/ecommerce.webp",
        "alt": "Portada de la plataforma de ventas",
        "imagen_anterior": "ecommerce.jpg",
    },
    "Dr. Franco Álvarez": {
        "src": "main/proyectos/franco-alvarez.webp",
        "alt": "Portada del sitio del psicologo clinico",
        "imagen_anterior": "franco-alvarez.jpg",
    },
}


def _objetivos(apps):
    Proyecto = apps.get_model("main", "Proyecto")
    encontrados = []
    for titulo, datos in MINIATURAS.items():
        proyecto = Proyecto.objects.filter(titulo=titulo).first()
        if proyecto is None:
            continue
        encontrados.append((proyecto, datos))
    return encontrados


def aplicar(apps, schema_editor):
    for proyecto, datos in _objetivos(apps):
        if any(c.get("rol") == "tarjeta" for c in (proyecto.capturas or [])):
            continue
        proyecto.capturas = [
            {
                "src": datos["src"],
                "alt": datos["alt"],
                "rol": "tarjeta",
                "portada": True,
            }
        ]
        proyecto.imagen = ""
        proyecto.save(update_fields=["capturas", "imagen"])


def revertir(apps, schema_editor):
    # Se restaura el nombre de archivo real de cada JPEG. No se puede derivar
    # del titulo: "Red de Apoyo Mutuo" daria "red.jpg" y "Dr. Franco Alvarez"
    # daria "dr.jpg", que no son los archivos que estan en media/.
    for proyecto, datos in _objetivos(apps):
        capturas = [
            c for c in (proyecto.capturas or []) if c.get("rol") != "tarjeta"
        ]
        proyecto.capturas = capturas
        proyecto.imagen = datos["imagen_anterior"]
        proyecto.save(update_fields=["capturas", "imagen"])


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_asignar_roles_capturas"),
    ]

    operations = [
        migrations.RunPython(aplicar, revertir),
    ]