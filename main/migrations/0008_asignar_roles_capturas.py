"""Asigna un rol a cada captura de La Otra Estación.

Por qué una migración de datos y no un cambio de template: el template no
debe saber nombres de archivo. El rol ("escritorio", "movil", "empresas",
"paginas") vive en el admin, y la galería solo pide el rol que necesita.

Idempotente: si una captura ya tiene rol, no se toca. Se aplica por nombre de
archivo en vez de por índice para que reordenar la lista en el admin no rompa
nada.
"""

from django.db import migrations

ROLES_POR_ARCHIVO = {
    "portada-desktop.webp": "escritorio",
    "portada-movil.webp": "movil",
    "empresas.webp": "empresas",
    "portada-completa.webp": "paginas",
}

PIES_POR_ROL = {
    "escritorio": (
        "La portada resuelve qué se come, dónde queda y cómo pedir, sin salir "
        "de la pantalla."
    ),
    "movil": (
        "El 87% de quien encuentra el restaurante llega desde el celular: por eso "
        "esta vista es la que manda."
    ),
}


def _proyectos_con_capturas(apps):
    Proyecto = apps.get_model("main", "Proyecto")
    # Ojo: los lookups JSON (has_key y compañía) no están soportados en SQLite,
    # que es lo que corre en PythonAnywhere. Se filtra en Python.
    return [
        proyecto
        for proyecto in Proyecto.objects.all()
        if any(captura.get("src") for captura in (proyecto.capturas or []))
    ]


def asignar_roles(apps, schema_editor):
    for proyecto in _proyectos_con_capturas(apps):
        capturas = proyecto.capturas or []
        cambio = False
        for captura in capturas:
            nombre = (captura.get("src") or "").rsplit("/", 1)[-1]
            rol = ROLES_POR_ARCHIVO.get(nombre)
            if rol and captura.get("rol") != rol:
                captura["rol"] = rol
                cambio = True
            if rol in PIES_POR_ROL and not captura.get("pie"):
                captura["pie"] = PIES_POR_ROL[rol]
                cambio = True
            # La portada del proyecto es la captura de escritorio, no la
            # página completa: 1040x2475 recortada se ve mal de tarjeta.
            if rol == "escritorio" and not captura.get("portada"):
                captura["portada"] = True
                cambio = True
        if cambio:
            proyecto.capturas = capturas
            proyecto.save(update_fields=["capturas"])


def quitar_roles(apps, schema_editor):
    for proyecto in _proyectos_con_capturas(apps):
        capturas = proyecto.capturas or []
        cambio = False
        for captura in capturas:
            if captura.pop("rol", None) is not None:
                cambio = True
        if cambio:
            proyecto.capturas = capturas
            proyecto.save(update_fields=["capturas"])


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_cargar_portafolio"),
    ]

    operations = [
        migrations.RunPython(asignar_roles, quitar_roles),
    ]