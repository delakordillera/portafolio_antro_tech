from django.db import OperationalError
from .models import Intercambio

def notificaciones_pendientes(request):
    if request.user.is_authenticated:
        try:
            conteo = Intercambio.objects.filter(
                habilidad__ofertante=request.user, 
                completado=False
            ).count()
            return {'notificaciones_conteo': conteo}
        except (OperationalError, Intercambio.DoesNotExist):
            return {'notificaciones_conteo': 0}
    return {'notificaciones_conteo': 0}