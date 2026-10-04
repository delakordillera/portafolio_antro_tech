Portafolio Full Stack | Antropología Digital & Desarrollo de Software

Bienvenidos a mi repositorio principal. Este espacio consolida mis proyectos de desarrollo Full Stack, marcando el cierre de mi especialización intensiva en Python (Bootcamp SENCE Talento Digital). 

Mi perfil profesional se construye en la intersección entre la Antropología Social y la Ingeniería de Software. Entiendo el código no solo como una herramienta técnica, sino como un vehículo para traducir dinámicas sociales, comunitarias y comerciales en arquitecturas digitales robustas y escalables. Integro el rigor de la investigación etnográfica y la experiencia de usuario (UX) con el desarrollo backend para crear plataformas que realmente respondan a las necesidades de las personas.


Stack Tecnológico Dominado

- Backend: Python 3, Django (Arquitectura MVT), lógica de QuerySets avanzados.
- Base de Datos: SQLite (Desarrollo), ORM de Django para modelado relacional.
- Frontend: HTML5, CSS3 modular, Bootstrap 5 (Diseño responsivo y UI/UX).
- Control de Versiones: Git, GitHub, despliegue en servidores Linux (PythonAnywhere).


Proyectos Destacados en Producción

1. LA OTRA ESTACIÓN (Cliente real · Freelance · 2026)
Sitio en producción para un restaurante de comida casera chilena en Peñalolén, construido desde cero: https://laotraestacionrestaurant.cl/

Es el caso que abre el portafolio, y el que mejor resume el perfil: un encargo real de un cliente real, resuelto de punta a punta (relevamiento, diseño, desarrollo, despliegue) y con resultado medible.

- El problema: un negocio con más de veinte años de trayectoria y ninguna presencia digital propia. La carta circulaba como PDF por WhatsApp y cada reserva era un hilo de mensajes sin orden.
- La traducción: portada que resuelve qué se come, dónde queda, a qué hora abre y cómo pedir; sección de empresas y eventos; botones de WhatsApp con el mensaje ya redactado; páginas legales; datos estructurados Schema.org para aparecer en Google y Maps.
- La construcción: HTML, CSS y JavaScript planos. Sin dependencias, sin build, sin mantenimiento.
- El resultado (Google Business Profile, últimos 28 días): 10.111 personas vieron el Perfil de Negocio, 5.557 búsquedas de Google mostraron el restaurante, 382 interacciones. El 87% de las visitas llegó desde Google Maps en celular, que es exactamente el dispositivo para el que se diseñó la portada.

2. Red de Apoyo Mutuo (Enfoque Social y Comunitario)
Plataforma web orientada a fortalecer el tejido social barrial mediante una economía comunitaria de reciprocidad y el intercambio solidario de oficios. Este sistema nace de la intersección entre la Antropología Digital y el desarrollo Full Stack, digitalizando las lógicas tradicionales de ayuda comunitaria para trascender las lógicas monetarias convencionales.

- Stack Específico: Frontend sin JavaScript para máxima compatibilidad en conexiones inestables, apoyado puramente en CSS3 y Bootstrap 5.
- Características Principales:
  - Muro Comunitario: Visualización de habilidades y oficios disponibles en el territorio.
  - Sistema de Solicitudes: Lógica de base de datos para solicitar intercambios y ofrecer ayuda.
  - La Voz del Barrio: Registro público de gratitud que fomenta el reconocimiento social y la confianza comunitaria.
  - Accesibilidad: Diseño mobile-first.


3. ANTRO-TECH CORE (Enfoque Comercial y Lógica de Negocios)
Plataforma eCommerce de alto rendimiento orientada a la venta de componentes de hardware (GPUs, CPUs, almacenamiento). Construida para demostrar el dominio de la lógica transaccional y el manejo de flujos de usuario.

- El Enfoque UX/UI: Diseño inmersivo Dark Mode estructurado para retener al usuario, con blindaje estricto de contenedores (overflow: hidden) para mantener la simetría perfecta del catálogo sin importar las dimensiones de las imágenes subidas a la base de datos.
- Características Técnicas:
  - Filtros Inteligentes (Django Q objects): Implementación de búsquedas avanzadas con lógica booleana estricta para cruzar variables (nombres, categorías, descripciones) y aislar productos exactos sin falsos positivos.
  - Motor de Carrito de Compras en Memoria: Gestión temporal de interacciones mediante el uso de Sesiones de Usuario (request.session), permitiendo una navegación de compra fluida sin saturar las peticiones a la base de datos antes del checkout final.
  - Cálculo dinámico: Renderizado de subtotales y totales matemáticos en tiempo real desde el backend hacia el frontend.


Cómo se edita el portafolio

Todo el contenido de la portada vive en el admin de Django (`/admin/` → Proyectos), no en el HTML:

- `destacado`: sube el proyecto a la sección de caso de estudio que aparece justo bajo el hero. Solo uno a la vez.
- `problema` / `metodo` / `traduccion` / `resultado`: son los cuatro bloques de la narrativa (Observación → Método → Traducción → Resultado). Si los dejas vacíos, el bloque simplemente no aparece.
- `metricas`: lista JSON con cifras reales y su fuente, ej. `[{"valor": "10.111", "etiqueta": "personas vieron el Perfil de Negocio", "nota": "Google · últimos 28 días"}]`.
- `terminos`: términos de búsqueda, ej. `[{"termino": "restaurants", "busquedas": 3679}]`.
- `capturas`: rutas dentro de `static/` con su pie de foto, ej. `[{"src": "main/estacion/portada-desktop.webp", "alt": "...", "pie": "...", "portada": true}]`.
- `url_produccion` para sitios en vivo, `link_interno` para rutas de este mismo proyecto (ej. `/ecommerce/`), `link_github` para repositorios.
- `visible`: desmarca para ocultar un proyecto sin borrarlo.

Las capturas de pantalla viven en `main/static/main/estacion/` (y se publican con `collectstatic`). Se generaron con Playwright contra el sitio en producción; para actualizarlas hay que repetir el proceso. El campo `imagen` es opcional: la tarjeta usa la captura marcada como portada, y solo recurre a `imagen` si el archivo existe en el servidor.


Instalación y Ejecución Local

Para probar este ecosistema de proyectos en tu propia máquina, clona este repositorio ejecutando el siguiente comando en tu terminal:

git clone https://github.com/delakordillera/portafolio_antro_tech.git

En Settings de Django la clave secreta se lee de la variable de entorno `DJANGO_SECRET_KEY` (no existe fallback: si falta, la aplicación no arranca, a propósito). Con `DJANGO_DEBUG=True` el servidor de desarrollo incluye `localhost` en `ALLOWED_HOSTS`.

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    $env:DJANGO_SECRET_KEY="clave-local-de-prueba"
    python manage.py migrate
    python manage.py runserver


Próximos Pasos y Visión

Como desarrollador, mi objetivo continuo es utilizar las herramientas tecnológicas para lograr impactos positivos. Estoy activamente buscando oportunidades en el ecosistema TI (desarrollo web, UX Research, análisis de datos) donde pueda aportar mi capacidad de aprendizaje autodidacta, mi perspectiva crítica y mi código estructurado.

Contacto: https://www.linkedin.com/in/alexis-lara-viveros - delakordillera@proton.me - https://delakordillera.pythonanywhere.com/

   
