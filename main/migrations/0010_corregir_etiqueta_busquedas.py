"""Corrige la etiqueta de la metrica de busquedas de Google.

Por que una migracion y no solo editar 0007: 0007 ya esta aplicada en
produccion, asi que corregir el archivo solo arregla las instalaciones nuevas.
Esta migracion pisa el dato en las bases que ya tienen el texto roto.

No se busca la cadena corrupta literal: se compara contra la etiqueta correcta.
 Asi el script es idempotente y no depende de reproducir los caracteres que se
colaron.

Sin reversa: deshacer devolveria el texto roto, que no es un estado en el que
convenga volver a quedar.
"""

from django.db import migrations

ETIQUETA_ROTA = "5.557"
ETIQUETA_CORRECTA = "búsquedas de Google que mostraron el restaurante"


def corregir(apps, schema_editor):
    Proyecto = apps.get_model("main", "Proyecto")
    for proyecto in Proyecto.objects.filter(capturas__isnull=False).distinct():
        metricas = proyecto.metricas or []
        cambio = False
        for metrica in metricas:
            if metrica.get("valor") == ETIQUETA_ROTA and metrica.get(
                "etiqueta"
            ) != ETIQUETA_CORRECTA:
                metrica["etiqueta"] = ETIQUETA_CORRECTA
                cambio = True
        if not cambio:
            continue
        proyecto.metricas = metricas
        proyecto.save(update_fields=["metricas"])


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0009_optimalizar_miniaturas"),
    ]

    operations = [
        migrations.RunPython(corregir, migrations.RunPython.noop),
    ]