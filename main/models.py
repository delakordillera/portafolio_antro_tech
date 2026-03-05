from django.db import models

# 1. TUS HABILIDADES
class Skill(models.Model):
    CATEGORIAS = [
        ('TECH', 'Technical (Python/Django)'),
        ('UX', 'UX Research & Anthropology'),
        ('SOFT', 'Soft Skills'),
    ]
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=4, choices=CATEGORIAS)
    nivel = models.IntegerField(help_text="Del 1 al 100")

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

# 2. TUS PROYECTOS
class Proyecto(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion_corta = models.TextField()
    contexto_social = models.TextField(help_text="¿Qué problema humano o social resuelve?")
    metodologia_ux = models.TextField(blank=True, help_text="¿Usaste entrevistas, observación, encuestas?")
    tecnologias = models.CharField(max_length=200, help_text="Ej: Python, Django, SQLite")
    imagen = models.ImageField(upload_to='proyectos/')
    link_github = models.URLField(blank=True)

    def __str__(self):
        return self.titulo

# 3. PERFIL: SOLO TU NOMBRE, RELATO Y CONTACTOS
class Perfil(models.Model):
    nombre = models.CharField(max_length=100, default="Alexis Lara Viveros")
    # Agregamos blank=True y null=True para que no de error al migrar
    contar_sobre_mi = models.TextField(blank=True, null=True, help_text="Cuenta aquí tu historia de forma cercana")
    cv_pdf = models.FileField(upload_to='cv/', blank=True, null=True, help_text="Sube tu CV en formato PDF")
    link_linkedin = models.URLField(blank=True, help_text="Tu enlace de LinkedIn")
    link_github = models.URLField(blank=True, help_text="Tu enlace de GitHub principal")
    correo = models.EmailField(blank=True, help_text="Tu correo de contacto profesional")

    def __str__(self):
        return f"Perfil de {self.nombre}"

# 4. TUS IMÁGENES INTERESANTES (EL MURAL)
class Interes(models.Model):
    titulo = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='intereses/')
    descripcion = models.CharField(max_length=200, blank=True, help_text="¿Por qué te interesa esta imagen?")

    def __str__(self):
        return self.titulo