from django.db import migrations

TITULO = "La Otra Estación"

NUEVO = {
    "problema": (
        "La Otra Estación es un restaurante con historia y tradición: comida que destaca y un "
        "espacio que acompaña, pero con una desventaja. No estaba optimizando su atención al no "
        "tener una web con la carta y el detalle de todo lo que ofrece el local. Tampoco contaba "
        "con SEO web, así que no se daba a conocer más allá del boca a boca entre clientes. Todo "
        "funcionaba con un menú escrito y con la misma conversación resuelta a diario."
    ),
    "metodo": (
        "Me encargué de convivir, compartir y comprender cómo es este espacio para sus clientes, "
        "la forma en que se consume y se diversifica la comunicación, considerando siempre la "
        "tradición del lugar. Comprendí que la gente que llega acá busca entender de manera "
        "sencilla qué se ofrece en el menú disponible. Por eso, tener un buen diseño para quienes "
        "accedan a la web se volvió fundamental."
    ),
    "traduccion": (
        "Una portada que resuelve las cuatro preguntas de quien llega desde el móvil: qué se come, "
        "dónde queda, a qué hora abre y cómo pedir. Más una sección para empresas y eventos y las "
        "páginas legales que exige operar en Chile. Cada botón de WhatsApp viaja con el mensaje ya "
        "redactado, así el cliente escribe y solo pulsa enviar. Todo el sitio es HTML, CSS y "
        "JavaScript planos. Y acá me encargo de mantener y optimizar cada nueva idea de mi cliente "
        "para sacar el máximo provecho a nuestra implementación web."
    ),
    "resultado": (
        "Creamos el sitio donde los dueños del local comunican todo lo que ofrecen, y llegó el "
        "resultado esperado: el Perfil de Negocio en Google se convirtió en el canal principal de "
        "descubrimiento, con 10.111 personas que lo vieron en 28 días y un 87% que llegó desde "
        "Google Maps en celular —exactamente el dispositivo para el que se diseñó la portada. "
        "Priorizamos el diseño responsive para que rinda óptimo en cada dispositivo nuevo que se "
        "acerque al local."
    ),
}

ANTERIOR = {
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
}


def actualizar(apps, schema_editor):
    Proyecto = apps.get_model("main", "Proyecto")
    Proyecto.objects.filter(titulo=TITULO).update(**NUEVO)


def revertir(apps, schema_editor):
    Proyecto = apps.get_model("main", "Proyecto")
    Proyecto.objects.filter(titulo=TITULO).update(**ANTERIOR)


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0010_corregir_etiqueta_busquedas"),
    ]

    operations = [
        migrations.RunPython(actualizar, revertir),
    ]