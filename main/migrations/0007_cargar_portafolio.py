"""
Carga inicial del portafolio: los cuatro proyectos con su contenido.

Es idempotente: si el proyecto ya existe por título, no lo duplica ni pisa
lo que hayas editado a mano en el admin. Para recargar desde cero, borra los
registros en /admin/ y vuelve a correr `python manage.py migrate main 0006`.
"""

from django.db import migrations

# Métricas reales reportadas por el cliente en Google Business Profile.
# Período: últimos 28 días. NO editar a mano sin cambiar también el período
# en las notas de la etiqueta.
METRICAS_ESTACION = [
    {
        "valor": "10.111",
        "etiqueta": "personas vieron el Perfil de Negocio",
        "nota": "Google Business Profile · últimos 28 días",
    },
    {
        "valor": "5.557",
        "etiqueta": "búsquedas de Google que mostraron el restaurante",
        "nota": "Google · últimos 28 días",
    },
    {
        "valor": "382",
        "etiqueta": "interacciones del Perfil de Negocio",
        "nota": "Google · últimos 28 días",
    },
    {
        "valor": "87%",
        "etiqueta": "de esas visitas llegaron desde Google Maps en celular",
        "nota": "8.763 de 10.111 · últimos 28 días",
    },
]

TERMINOS_ESTACION = [
    {"termino": "restaurants", "busquedas": 3679},
    {"termino": "comida", "busquedas": 792},
    {"termino": "restaurant", "busquedas": 328},
    {"termino": "restaurantes", "busquedas": 281},
    {"termino": "restaurante", "busquedas": 156},
]

CAPTURAS_ESTACION = [
    {
        "src": "main/estacion/portada-desktop.webp",
        "alt": "Portada de laotraestacionrestaurant.cl vista en un escritorio",
        "pie": "Portada — el menú del día, la reserva y el pedido con delivery, sin salir de la pantalla.",
        "portada": True,
    },
    {
        "src": "main/estacion/empresas.webp",
        "alt": "Página de empresas y eventos de La Otra Estación",
        "pie": "Empresas y eventos — el camino que convierte un almuerzo en un contrato recurrente.",
    },
    {
        "src": "main/estacion/portada-movil.webp",
        "alt": "La Otra Estación visto en un teléfono",
        "pie": "En celular — el 87% de quien encuentra el restaurante llega desde el móvil.",
    },
    {
        "src": "main/estacion/portada-completa.webp",
        "alt": "Página completa del sitio La Otra Estación",
        "pie": "La página completa, de arriba abajo: cinco secciones y nada que sobra.",
    },
]

PROYECTOS = [
    {
        "titulo": "La Otra Estación",
        "descripcion_corta": (
            "Sitio en producción para un restaurante de comida casera chilena en Peñalolén, "
            "construido desde cero: la carta a un clic, los pedidos y las reservas por WhatsApp "
            "con el mensaje ya escrito, y presencia real en Google y Maps."
        ),
        "contexto_social": (
            "Un negocio con más de veinte años de trayectoria en el barrio y ninguna presencia "
            "digital propia. Todo el descubrimiento pasaba por el boca a boca."
        ),
        "metodologia_ux": "",
        "problema": (
            "La Otra Estación trabaja en Peñalolén desde 2002 y no tenía nada digital: la carta "
            "circulaba como un PDF suelto por WhatsApp y cada reserva era un hilo de mensajes sin "
            "orden. Para un restaurante cuyo activo real es el menus del día, eso significaba "
            "que la información que lo sostenía —qué se come hoy, a qué hora, si hay mesa— "
            "vivía en el privado de una aplicación de mensajería."
        ),
        "metodo": (
            "Definí el alcance por lo que el local ya hace todos los días, no por lo que un sitio "
            "de restaurante suele traer. De ahí salieron tres requisitos no negociables: que la "
            "carta se alcanzara en un toque, que pedir no exigiera instalar nada y que el sitio no "
            "fuera invisible para quien busca comida en el barrio desde el celular. La carta "
            "siguió siendo un PDF —es el formato que el negocio ya conoce y actualiza— pero "
            "enlazada desde cada punto de entrada."
        ),
        "traduccion": (
            "Una portada que resuelve las cuatro preguntas de quien llega desde el móvil —qué se "
            "come, dónde queda, a qué hora abre y cómo pedir— más una sección para empresas y "
            "eventos y las páginas legales que exige operar en Chile. Cada botón de WhatsApp "
            "viaja con el mensaje ya redactado, así el cliente escribe y solo pulsa enviar. "
            "Todo el sitio es HTML, CSS y JavaScript planos: sin dependencias, sin build, sin "
            "mantenimiento."
        ),
        "resultado": (
            "El sitio está en producción desde 2026 y el Perfil de Negocio en Google se "
            "convirtió en el canal principal de descubrimiento: 10.111 personas lo vieron en 28 "
            "días y el 87% llegó desde Google Maps en celular, exactamente el dispositivo para el "
            "que se diseñó la portada."
        ),
        "tecnologias": "HTML, CSS, JavaScript, SEO local, Schema.org, WebP",
        "categoria": "producto",
        "destacado": True,
        "anio": "2026",
        "cliente": "La Otra Estación · Peñalolén, Santiago",
        "rol": "Diseño, desarrollo y despliegue end-to-end · freelance",
        "url_produccion": "https://laotraestacionrestaurant.cl/",
        "metricas": METRICAS_ESTACION,
        "terminos": TERMINOS_ESTACION,
        "capturas": CAPTURAS_ESTACION,
    },
    {
        "titulo": "Red de Apoyo Mutuo",
        "descripcion_corta": (
            "Digitalización de la reciprocidad barrial en Peñalolén: un muro de oficios, "
            "solicitudes de intercambio y un registro público de gratitud."
        ),
        "contexto_social": (
            "El prestigio comunitario, no el dinero, mueve la reciprocidad barrial."
        ),
        "metodologia_ux": "Entrevistas en terreno con libreta de campo a vecinos de Peñalolén.",
        "traduccion": (
            "Sistema de Puntos de Confianza y Círculo de la Gratitud sobre Django, sin "
            "dependencias externas para que funcione en conexiones inestables."
        ),
        "tecnologias": "Etnografía, Entrevistas, Python, Django",
        "categoria": "investigacion",
        "destacado": False,
        "link_interno": "/apoyo-mutuo/",
        "imagen": "apoyo-mutuo.jpg",
    },
    {
        "titulo": "Dr. Franco Álvarez",
        "descripcion_corta": (
            "Sitio web para psicólogo clínico con testing de usabilidad, agenda propia y una "
            "base de datos que administra el profesional."
        ),
        "contexto_social": (
            "Fricción real en agendas manuales y WhatsApp desordenado."
        ),
        "metodologia_ux": (
            "Mapeo del flujo de atención junto al psicólogo, con lápiz y papel."
        ),
        "traduccion": (
            "Base de datos Django autoadministrable, notificaciones automáticas y guía "
            "descargable sobre ansiedad."
        ),
        "tecnologias": "Testing UX, Django, Hardening",
        "categoria": "producto",
        "destacado": False,
        "url_produccion": "https://pagina-web-franco-alvarez.vercel.app/",
        "imagen": "franco-alvarez.jpg",
    },
    {
        "titulo": "Plataforma Ecommerce",
        "descripcion_corta": (
            "Ventas con integración de indicadores financieros reales vía API pública."
        ),
        "contexto_social": (
            "Precios indexados a la API mindicador.cl (UF, USD)."
        ),
        "traduccion": (
            "Catálogo dinámico, carrito con sesiones, autenticación de usuarios, panel de "
            "administración con CRUD y backend relacional en SQLite."
        ),
        "tecnologias": "Python, Django, API, SQLite",
        "categoria": "demo",
        "destacado": False,
        "link_interno": "/ecommerce/",
        "imagen": "ecommerce.jpg",
        "advertencia": (
            "Demo técnica — no es un producto en producción. Proyecto construido para "
            "demostrar un stack full end-to-end: catálogo dinámico, carrito de compras con "
            "sesiones, autenticación de usuarios (Django auth), panel de administración "
            "(/admin/) con CRUD sobre modelos, integración de API REST externa "
            "(mindicador.cl) para datos financieros en tiempo real, y backend relacional con "
            "SQLite. Desplegada en PythonAnywhere con Gunicorn."
        ),
    },
]


def cargar(apps, schema_editor):
    Proyecto = apps.get_model("main", "Proyecto")
    for datos in PROYECTOS:
        if not Proyecto.objects.filter(titulo=datos["titulo"]).exists():
            Proyecto.objects.create(**datos)


def descargar(apps, schema_editor):
    Proyecto = apps.get_model("main", "Proyecto")
    Proyecto.objects.filter(titulo__in=[p["titulo"] for p in PROYECTOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_alter_proyecto_options_proyecto_advertencia_and_more"),
    ]

    operations = [
        migrations.RunPython(cargar, descargar),
    ]
