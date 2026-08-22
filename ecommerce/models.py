from django.db import models
from django.core.validators import FileExtensionValidator

MAX_UPLOAD_SIZE_MB = 5


def validate_producto_image_size(file):
    if file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        from django.core.exceptions import ValidationError
        raise ValidationError(f'La imagen no puede superar {MAX_UPLOAD_SIZE_MB} MB.')


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.IntegerField(default=0, help_text="Precio en CLP (sin puntos ni comas)")
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True, null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']),
            validate_producto_image_size,
        ]
    )
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre