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
