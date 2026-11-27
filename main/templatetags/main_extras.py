from django import template

register = template.Library()


@register.filter
def miles(valor):
    """Separador de miles chileno: 3679 -> '3.679'."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return valor
    return f"{numero:,}".replace(",", ".")


@register.simple_tag
def trabajos_pie():
    """Casos visibles con sitio en producción, para la columna del pie."""
    from django.urls import reverse
    from django.utils.text import slugify
    from main.models import Proyecto
    try:
        proyectos = Proyecto.objects.filter(visible=True).exclude(url_produccion='').order_by('-destacado', 'id')
        return [{'titulo': p.titulo, 'url': reverse('proyecto', args=[slugify(p.titulo)])} for p in proyectos[:4]]
    except Exception:
        return []
