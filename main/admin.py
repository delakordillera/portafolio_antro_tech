from django.contrib import admin
from django.utils.html import format_html
from django.templatetags.static import static

from .models import Interes, Perfil, Proyecto, Skill


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'categoria',
        'destacado',
        'visible',
        'cliente',
        'anio',
        'portada_admin',
    )
    list_display_links = ('titulo',)
    list_filter = ('categoria', 'destacado', 'visible')
    search_fields = ('titulo', 'descripcion_corta', 'cliente', 'tecnologias')
    list_editable = ('destacado', 'visible')
    ordering = ('-destacado', 'id')
    readonly_fields = ('portada_admin',)
    fieldsets = (
        (None, {
            'fields': ('titulo', 'descripcion_corta', 'categoria', 'visible', 'destacado'),
        }),
        ('Encabezado del caso de estudio', {
            'description': 'Datos que aparecen en la tarjeta y en la portada del caso.',
            'fields': ('cliente', 'rol', 'anio', 'url_produccion', 'link_github'),
        }),
        ('Narrativa', {
            'description': 'La estructura de abajo es la que se lee en la portada: '
                           'Observación → Método → Traducción → Resultado.',
            'fields': ('problema', 'metodo', 'traduccion', 'resultado', 'etapas'),
        }),
        ('Evidencia', {
            'description': 'Métricas y capturas. Formato de cada métrica: '
                           '{"valor": "10.111", "etiqueta": "personas vieron el perfil", '
                           '"nota": "Google · últimos 28 días"}.',
            'fields': ('metricas', 'capturas', 'tecnologias', 'portada_admin'),
        }),
        ('Imagen de portada', {
            'description': 'Se usa en la grilla de proyectos si el archivo existe en el servidor. '
                           'Si lo dejas vacío, la tarjeta usa la captura marcada como portada.',
            'fields': ('imagen',),
        }),
    )

    @admin.display(description='Portada')
    def portada_admin(self, obj):
        if not obj.pk:
            return '—'
        captura = obj.captura_portada
        if obj.imagen_existe:
            return format_html(
                '<img src="{}" style="height:44px;border-radius:4px;'
                'border:1px solid #ccc" alt="">',
                obj.imagen.url,
            )
        if captura:
            return format_html(
                '<img src="{}" style="height:44px;border-radius:4px;'
                'border:1px solid #ccc" alt=""><div style="font-size:11px">'
                'captura estática</div>',
                static(captura['src']),
            )
        return format_html('<span style="color:#999">sin portada</span>')


admin.site.register(Perfil)
admin.site.register(Skill)
admin.site.register(Interes)
