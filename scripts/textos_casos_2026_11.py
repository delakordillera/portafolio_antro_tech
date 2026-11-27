# Textos de los casos (nov. 2026). Uso: python manage.py shell < scripts/textos_casos_2026_11.py
from main.models import Proyecto

P = {p.id: p for p in Proyecto.objects.all()}

loe = P.get(1)
if loe:
    loe.descripcion_corta = ("Sitio para un restaurante de comida casera chilena en Santiago, construido desde cero: "
                             "la carta a un clic, pedidos y reservas por WhatsApp con el mensaje ya escrito, "
                             "y presencia real en Google y Maps.")
    loe.cliente = "La Otra Estación, restaurante en Santiago"
    loe.rol = "Diseño, desarrollo, publicación y mantención (freelance)"
    loe.problema = loe.problema.replace(
        "Todo funcionaba con un menú escrito y con la misma conversación resuelta a diario.",
        "Todo dependía de un menú escrito y de responder las mismas preguntas una y otra vez.")
    loe.save()

franco = P.get(3)
if franco:
    franco.descripcion_corta = ("Sitio para un psicólogo clínico con agenda de horas en línea, aviso automático "
                                "de cada reserva y contenidos que él mismo administra.")
    franco.cliente = "Franco Álvarez, psicólogo clínico"
    franco.rol = "Investigación, diseño y desarrollo (freelance)"
    franco.tecnologias = "Python, Django, Bootstrap 5, Flatpickr, ReportLab"
    franco.problema = ("Franco coordinaba sus horas a mano, conversación por conversación en WhatsApp. Cada paciente "
                       "nuevo significaba varios mensajes para encontrar un horario, y no tenía un lugar propio donde "
                       "explicar su enfoque y sus especialidades.")
    franco.metodo = ("Mapeamos juntos, con lápiz y papel, cómo llega una persona a pedir hora: qué busca, qué necesita "
                     "saber antes de escribir y en qué momento decide agendar. Ese recorrido ordenó las secciones del "
                     "sitio y sus textos.")
    franco.traduccion = ("Un sitio en Django con calendario de horas disponibles por bloque, aviso por correo de cada "
                         "reserva y un botón de WhatsApp con el mensaje listo. Sumé un blog, una guía descargable sobre "
                         "ansiedad en PDF y un panel para que Franco actualice sus contenidos. La configuración de "
                         "producción quedó protegida: claves fuera del código y modo de depuración apagado.")
    franco.resultado = ("El sitio está publicado y probado en Android e iOS. Las solicitudes de hora llegan al correo "
                        "de Franco con los datos completos.")
    franco.capturas = [
        {"src": "main/proyectos/franco-escritorio.webp", "alt": "Portada del sitio de Franco Álvarez en escritorio",
         "rol": "escritorio", "portada": True},
        {"src": "main/proyectos/franco-movil.webp", "alt": "Sitio de Franco Álvarez en celular", "rol": "movil"},
    ]
    franco.save()

red = P.get(2)
if red:
    red.descripcion_corta = ("Plataforma para intercambiar ayuda entre vecinos: un muro de oficios, solicitudes de "
                             "intercambio y un registro público de agradecimientos.")
    red.metodologia_ux = "Entrevistas en terreno con libreta de campo a vecinos del barrio."
    red.tecnologias = "Python, Django"
    red.rol = "Investigación, diseño y desarrollo"
    red.problema = ("¿Cómo llevar a lo digital la ayuda entre vecinos sin convertirla en un mercado de servicios "
                    "pagados? En el barrio, la ayuda circula por confianza y entre conocidos.")
    red.metodo = ("Hice entrevistas en terreno a cuatro vecinos, con libreta de campo. El hallazgo principal: lo que "
                  "mueve la ayuda mutua es el prestigio dentro de la comunidad, no el dinero.")
    red.traduccion = ("Convertí ese hallazgo en dos mecanismos: Puntos de Confianza, que reconocen a quien ayuda, y el "
                      "Círculo de la Gratitud, un registro público de agradecimientos. Todo en Django y sin "
                      "dependencias externas, para que funcione con conexiones inestables.")
    red.resultado = ("Un prototipo funcional publicado, con muro de oficios, solicitudes de intercambio y registro de "
                     "agradecimientos, listo para probarse con más vecinos.")
    red.capturas = [
        {"src": "main/proyectos/apoyo-mutuo.webp", "alt": "Muro de oficios de Red de Apoyo Mutuo",
         "rol": "escritorio", "portada": True},
    ]
    red.save()

demo = P.get(4)
if demo:
    demo.visible = False
    demo.save()

for p in Proyecto.objects.all():
    print(p.id, p.visible, p.titulo, "|", p.descripcion_corta[:60])
