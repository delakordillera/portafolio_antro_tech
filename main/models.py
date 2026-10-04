from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# 1. TUS HABILIDADES
class Skill(models.Model):
    CATEGORIAS = [
        ('TECH', 'Technical (Python/Django)'),
        ('UX', 'UX Research & Anthropology'),
        ('SOFT', 'Soft Skills'),
    ]
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=4, choices=CATEGORIAS)
    nivel = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Del 1 al 100"
    )

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

# 2. TUS PROYECTOS
class Proyecto(models.Model):
    CATEGORIAS = [
        ('investigacion', 'Investigación + código'),
        ('producto', 'Producto real'),
        ('demo', 'Demo técnica'),
    ]
    titulo = models.CharField(max_length=200)
    descripcion_corta = models.TextField()
    contexto_social = models.TextField(help_text="¿Qué problema humano o social resuelve?")
    metodologia_ux = models.TextField(blank=True, help_text="¿Usaste entrevistas, observación, encuestas?")
    tecnologias = models.CharField(max_length=200, help_text="Ej: Python, Django, SQLite")
    imagen = models.ImageField(upload_to='proyectos/')
    link_github = models.URLField(blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='investigacion')

    # --- Presentación en el portafolio ---
    visible = models.BooleanField(
        default=True,
        help_text="Desmarca para ocultarlo del portafolio sin borrarlo"
    )
    destacado = models.BooleanField(
        default=False,
        help_text="Lo convierte en el caso de estudio destacado sobre el hero"
    )
    anio = models.CharField(max_length=20, blank=True, help_text="Año o período, ej: 2026")
    cliente = models.CharField(max_length=120, blank=True, help_text="Cliente o negocio")
    rol = models.CharField(max_length=160, blank=True, help_text="Qué hiciste tú, en una línea")
    url_produccion = models.URLField(blank=True, help_text="Sitio en producción (no es repositorio)")
    link_interno = models.CharField(
        max_length=200, blank=True,
        help_text="Ruta dentro de este sitio, ej: /apoyo-mutuo/ (se abre en la misma pestaña)"
    )
    advertencia = models.TextField(
        blank=True, verbose_name="Advertencia",
        help_text="Aviso visible en la tarjeta, ej: 'Demo técnica, no es un producto en producción'"
    )

    # --- Narrativa del caso de estudio ---
    problema = models.TextField(
        blank=True, verbose_name="Observación", help_text="Qué encontré en terreno"
    )
    metodo = models.TextField(
        blank=True, verbose_name="Método", help_text="Cómo investigué o cómo decidí construirlo"
    )
    traduccion = models.TextField(
        blank=True, verbose_name="Traducción", help_text="Qué construiste"
    )
    resultado = models.TextField(
        blank=True, verbose_name="Resultado", help_text="Qué cambió. Solo hechos verificables"
    )
    etapas = models.JSONField(
        default=list, blank=True, verbose_name="Etapas del proceso",
        help_text='Lista de pasos, ej: [{"etiqueta": "Observación", "titulo": "Cero presencia digital", "texto": "..."}]'
    )
    metricas = models.JSONField(
        default=list, blank=True, verbose_name="Métricas",
        help_text='Cifras reales con su fuente, ej: [{"valor": "10.111", "etiqueta": "personas vieron el perfil", "nota": "Google · últimos 28 días"}]'
    )
    capturas = models.JSONField(
        default=list, blank=True, verbose_name="Capturas",
        help_text='Rutas de static + pie de foto, ej: [{"src": "main/estacion/portada-desktop.webp", "alt": "Portada", "pie": "Portada del sitio", "portada": true}]'
    )
    terminos = models.JSONField(
        default=list, blank=True, verbose_name="Términos de búsqueda",
        help_text='Qué búsquedas muestran el proyecto, ej: [{"termino": "restaurants", "busquedas": 3679}]'
    )

    class Meta:
        ordering = ['-destacado', 'id']

    def __str__(self):
        return self.titulo

    @property
    def etapas_narradas(self):
        """Etapas con texto; cae a los campos sueltos si no se llenó la lista."""
        etapas = [e for e in (self.etapas or []) if e.get('texto')]
        if etapas:
            return etapas
        return [
            {'etiqueta': etiqueta, 'texto': texto}
            for etiqueta, texto in [
                ('Observación', self.problema),
                ('Método', self.metodo),
                ('Traducción', self.traduccion),
                ('Resultado', self.resultado),
            ]
            if texto
        ]

    @property
    def metricas_validas(self):
        """Métricas que tienen cifra y etiqueta (evita cajas vacías si el JSON se editó mal)."""
        return [m for m in (self.metricas or []) if m.get('valor') and m.get('etiqueta')]

    @property
    def captura_portada(self):
        """Captura marcada como portada; si ninguna lo está, usa la primera."""
        capturas = [c for c in (self.capturas or []) if c.get('src')]
        for captura in capturas:
            if captura.get('portada'):
                return captura
        return capturas[0] if capturas else None

    def captura_por_rol(self, rol):
        """Captura con el rol pedido, o None.

        El rol vive en el admin, no en el template: la galería no debe saber
        nombres de archivo. "portada" cae a la portada si nadie asignó el rol.
        """
        if rol == 'portada':
            return self.captura_portada
        for captura in self.capturas or []:
            if captura.get('src') and captura.get('rol') == rol:
                return captura
        return None

    @property
    def dispositivos(self):
        """Las dos capturas que se muestran como evidencia: escritorio y celular.

        Escritorio a la izquierda porque es la vista de referencia; el celular
        al lado, recortado a la misma altura, porque el 87% del tráfico del
        cliente llega desde ahí.
        """
        return {
            'escritorio': self.captura_por_rol('escritorio'),
            'movil': self.captura_por_rol('movil'),
        }

    @property
    def imagen_existe(self):
        """True solo si el archivo de imagen está realmente en el disco."""
        if not self.imagen:
            return False
        try:
            return self.imagen.storage.exists(self.imagen.name)
        except (NotImplementedError, ValueError, OSError):
            return False

    @property
    def url_destino(self):
        """A dónde debe apuntar la tarjeta: producción, repositorio, ruta interna o '#'."""
        return self.url_produccion or self.link_github or self.link_interno or '#'

    @property
    def es_externo(self):
        """True si la tarjeta debe abrirse en pestaña nueva."""
        return self.url_destino.startswith('http')

    @property
    def terminos_validos(self):
        """Términos de búsqueda ordenados de mayor a menor, sin los que no tienen cifra."""
        validos = [t for t in (self.terminos or []) if t.get('termino') and t.get('busquedas')]
        return sorted(validos, key=lambda t: t['busquedas'], reverse=True)

    @property
    def total_terminos(self):
        return sum(t['busquedas'] for t in self.terminos_validos)

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