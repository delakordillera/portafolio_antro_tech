from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. El Sujeto Social (Perfil)
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True)
    puntos_confianza = models.IntegerField(default=0)

    @property
    def rango(self):
        if self.puntos_confianza >= 15:
            return "Pilar del Barrio"
        elif self.puntos_confianza >= 5:
            return "Vecino Colaborador"
        else:
            return "Vecino Nuevo"

    @property
    def rango_clase(self):
        if self.puntos_confianza >= 15:
            return "bg-danger"
        elif self.puntos_confianza >= 5:
            return "bg-success"
        else:
            return "bg-secondary"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

# 2. El Objeto del Intercambio (Habilidad/Don)
class Habilidad(models.Model):
    ofertante = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50)
    
    # NUEVA MEJORA: Campo para imagen del oficio
    # null=True y blank=True permiten que subir una foto sea opcional
    imagen = models.ImageField(upload_to='habilidades/', null=True, blank=True)

    def __str__(self):
        return self.titulo

# 3. El Vínculo (Intercambio)
class Intercambio(models.Model):
    solicitante = models.ForeignKey(User, related_name='solicitudes', on_delete=models.CASCADE)
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    comentario_gratitud = models.TextField(blank=True)
    completado = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['solicitante', 'habilidad'], name='uniq_solicitante_habilidad')
        ]

    def __str__(self):
        return f"{self.solicitante.username} solicitó {self.habilidad.titulo}"

# --- SECCIÓN DE SIGNALS ---

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()