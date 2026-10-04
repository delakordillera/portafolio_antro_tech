# Notas del rediseño (2026-08-19)

Contexto para retomar esto en Claude Code.

## Por qué esta carpeta se ve así

Encontré dos copias de tu proyecto que habían divergido:

1. **`github.com/delakordillera/portafolio_antro_tech`** — la que has estado
   actualizando. Tiene la app `comunidad` (Red de Apoyo Mutuo) completa y
   funcionando, y el `ecommerce` con login/registro.
2. **Esta carpeta (`mi_web` en tu escritorio)** — un prototipo más antiguo:
   Bootstrap genérico sin personalizar, la app `apoyo_mutuo` vacía (sin
   modelos ni templates), y un `ecommerce` con un flujo de checkout/carrito
   distinto (`carrito.py`, `checkout.html`, `success.html`) que **no existe**
   en la versión de GitHub.

Como confirmaste que GitHub es la fuente que realmente mantienes, reconstruí
esta carpeta a partir de esa versión: traje `core/`, `main/`, `comunidad/`,
`ecommerce/`, `manage.py`, `requirements.txt` desde el repo, con el rediseño
ya aplicado y las correcciones de seguridad de abajo.

**No pude borrar nada en tu computador** (esta sesión solo puede leer y
escribir archivos, no eliminarlos), así que las carpetas viejas siguen ahí.
Antes de hacer `git init` o subir esto al repo, borra manualmente:

- `portfolio/` (el proyecto Django viejo, reemplazado por `core/`)
- `apoyo_mutuo/` (la app vacía, reemplazada por `comunidad/`)
- `static/estilos.css` (el CSS viejo; el nuevo diseño va inline en cada
  template)
- `db.sqlite3` (base de datos del prototipo viejo — está en `.gitignore`,
  no debería subirse igual)
- `env/` (tu virtualenv — **nunca debería estar dentro de la carpeta del
  proyecto**; bórralo y crea uno nuevo con `python -m venv venv` cuando
  vayas a correr el proyecto)
- `vecino1.jpg`, `vecino2.jpg`, `vecina3.jpg`, `vecino4.jpeg` sueltos en la
  raíz — ya están reorganizados y optimizados en `media/habilidades/`
- Si `media/cv/CV_ALEXIS_LARA.pdf` (4.9 MB) sigue ahí: revisa si todavía lo
  necesitas. Dejé solo el CV formato Harvard (83 KB, 2 páginas) en
  `media/cv/`, que es el que coincide con tu proyecto de CV — el otro pesa
  60x más y probablemente es una versión vieja.

## Seguridad (lo que pediste explícitamente)

**Encontré un problema real:** el `SECRET_KEY` de Django estaba escrito en
texto plano en `core/settings.py`, y esa versión quedó pública en tu repo de
GitHub. Esa clave firma cookies de sesión, tokens CSRF y de recuperación de
contraseña — expuesta, alguien podría falsificarlos.

Arreglé esto:

- `SECRET_KEY` ahora se lee de la variable de entorno `DJANGO_SECRET_KEY`
  (con un fallback obviamente marcado como "solo local" para que puedas
  correr el proyecto sin configurar nada en tu máquina)
- **Tienes que rotar la clave en producción.** Genera una nueva con:
  `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  En PythonAnywhere: pestaña **Web** → agrega antes del import de la app:
  ```python
  import os
  os.environ['DJANGO_SECRET_KEY'] = 'PEGA_AQUÍ_LA_CLAVE_NUEVA'
  ```
  **Guárdala en un gestor de contraseñas. NUNCA la subas al código.**
- `DEBUG` también se lee de `DJANGO_DEBUG` (por defecto `False`, igual que
  ahora)
- Agregué cabeceras de seguridad estándar para producción (activadas solo
  cuando `DEBUG=False`): `SECURE_SSL_REDIRECT`, cookies de sesión/CSRF con
  `Secure`, `SECURE_HSTS_SECONDS`, `X_FRAME_OPTIONS`. Incluí
  `SECURE_PROXY_SSL_HEADER`, que es necesario específicamente en
  PythonAnywhere para que Django detecte HTTPS correctamente detrás de su
  proxy — sin esto, `SECURE_SSL_REDIRECT` causaría un loop de redirects y
  tumbaría el sitio.

## Diseño

Portada (`main/templates/main/home.html`): mismo rediseño "cuaderno de campo
+ terminal" (terracota `#d9773f` + musgo `#8aa888`, Space Grotesk + JetBrains
Mono, sin Bootstrap Icons ni AOS) que ya habíamos revisado, más la sección
nueva de **Formación & Certificaciones**.

Extendí la misma paleta a `comunidad/templates/comunidad/base.html` y
`ecommerce/templates/ecommerce/base.html` (navbar, modal "Sobre el
proyecto", variables de Bootstrap `--bs-primary` remapeadas a terracota) para
que el resto del sitio no se sienta como una app distinta. **Ojo:** solo
retoqué los `base.html` — las páginas internas (`muro.html`, `perfil.html`,
`lista_productos.html`, etc.) siguen usando clases utilitarias de Bootstrap
(`btn-primary`, `bg-primary`) que heredan el color nuevo automáticamente,
pero no revisé el detalle fino de cada una.

## Responsive y calidad

- Verifiqué el hero, skills, proyectos, formación, contacto y el modal en
  desktop (1440px) y mobile (390px) con capturas reales — colapsan bien, el
  menú hamburguesa y el modal funcionan.
- `vecino1.jpg` era una foto de cámara DSLR sin comprimir (3600×2400,
  6.67 MB) — la reduje a 1200px de ancho / ~197 KB manteniendo buena calidad.
  El resto de las imágenes de `habilidades/` ya estaban en un tamaño
  razonable.
- Corregí un bug real: `perfil.cv_pdf.url` tiraba error 500 si `Perfil`
  existía sin archivo de CV subido. Ahora ese ícono solo aparece si hay CV.

## Pendiente (contenido, no diseño ni seguridad)

No inventé datos que no me confirmaste. Esto le daría más peso al
portafolio si lo completas con información real:

1. **Experiencia** — no hay sección de trayectoria/freelance con fechas.
2. **Métricas de los casos de estudio** — números concretos (entrevistas
   realizadas, tiempo reducido, usuarios activos).
3. **Testimonios** — nada de terceros (Franco Álvarez, algún vecino).
4. Verifica que `media/proyectos/apoyo-mutuo.jpg`, `ecommerce.jpg` y
   `franco-alvarez.jpg` existan subidos en el admin de Django en producción
   — el home.html los referencia directo. Solo tengo una captura
   (`Captura_de_pantalla_2026-02-12_003504.png`) que dejé en
   `media/proyectos/` sin renombrar porque no sé a cuál de los tres
   corresponde.

## Deploy

1. Borra las carpetas/archivos viejos listados arriba.
2. Revisa que todo funcione local: `pip install -r requirements.txt`,
   `python manage.py migrate`, `python manage.py runserver`.
3. `git add -A && git commit -m "..." && git push`.
4. En PythonAnywhere: configura `DJANGO_SECRET_KEY` en el WSGI (ver arriba),
   pestaña **Web** → **Reload**.

---

## Actualización 2026-10-03 — La Otra Estación como caso insignia

## Lo que cambió en esta última pasada

**La Otra Estación pasó a ser el caso insignia del portafolio.** Antes era una
tarjeta más, hardcodeada al final de la grilla. Ahora es:

1. Una sección completa (`#caso-destacado`) que aparece **justo debajo del
   hero**, antes que habilidades y antes que la grilla de proyectos.
2. La primera tarjeta de la grilla, con el distintivo "Proyecto destacado".
3. El destino del botón principal del hero y el destino del enlace "Portafolio"
   en `comunidad/base.html` y `ecommerce/base.html`.

La narrativa sigue la misma voz del resto del portafolio:
**Observación → Método → Traducción → Resultado**, más un bloque de evidencia
con las métricas reales del cliente.

## Decisiones que conviene no revertir sin pensar

**El contenido vive en la base de datos, no en el HTML.** `main/models.py`
extiende `Proyecto` con campos para el caso de estudio (`problema`, `metodo`,
`traduccion`, `resultado`, `metricas`, `terminos`, `capturas`, `destacado`,
`cliente`, `rol`, `anio`, `url_produccion`, `link_interno`, `advertencia`,
`visible`). Todo se edita desde `/admin/` → Proyectos. La migración
`0007_cargar_portafolio` siembra los cuatro proyectos con su contenido actual y
es idempotente: si ya existe un proyecto con ese título, no lo pisa.

Antes, la grilla de proyectos tenía dos juegos de markup —el loop sobre la base
de datos y un bloque `{% else %}` con los cuatro proyectos hardcodeados— y
 siempre ganaba el segundo, porque la base de datos estaba vacía. Eso se eliminó.
Ahora el bloque vacío es un mensaje honesto, no 170 líneas de HTML duplicado.

**Las capturas van en `static/`, no en `media/`.** Motivo concreto: `media/`
está en `.gitignore`, así que cualquier imagen nueva tendría que subirla a mano
al servidor. `staticfiles/` sí se versiona en git, así que las capturas viajan
solas con el deploy. Están en `main/static/main/estacion/` (fuente) y se copian
a `staticfiles/main/estacion/` con `collectstatic`.

**`Proyecto.imagen` es opcional a propósito.** Las tres imágenes viejas
(`/media/apoyo-mutuo.jpg`, `/media/ecommerce.jpg`, `/media/franco-alvarez.jpg`)
no existen en el repositorio, solo en el disco del servidor. La tarjeta resuelve
en este orden: `imagen` si el archivo está realmente en disco
(`Proyecto.imagen_existe`) → la captura marcada como portada → un placeholder
con textura. Así nunca sale una imagen rota, ni en local ni en producción.

## Métricas: de dónde salen y cuándo caducan

Son del **Google Business Profile** del restaurante, período **últimos 28 días**:

| Cifra | Qué es |
| --- | --- |
| 10.111 | Personas que vieron el Perfil de Negocio |
| 5.557 | Búsquedas de Google que mostraron el Perfil de Negocio |
| 382 | Interacciones del Perfil de Negocio |
| 87% | De las visitas llegaron desde Google Maps en celular (8.763 de 10.111) |

Los cinco términos de búsqueda (`restaurants` 3.679, `comida` 792, `restaurant`
328, `restaurantes` 281, `restaurante` 156) **suman 5.236, no 5.557**. Google
solo muestra los principales, así que en la plantilla están rotulados
"principales 5" y la cifra de 5.557 se muestra aparte como total. No cambiar
uno sin revisar el otro.

Estas cifras son de una ventana móvil: en unos meses dejórán de ser ciertas.
Para refrescarlas, edita el proyecto en `/admin/` → *Métricas* y *Términos de
búsqueda*, y actualiza el período en las etiquetas `nota`.

## Lo que sigue pendiente de contenido

1. **El campo `metodo` del caso destacado está redactado con las decisiones de
   diseño verificables en el sitio entregable, no con investigación de campo
   declarada.** Si hubo entrevistas, observación en el local o mapeo del flujo
   con el dueño, eso va en `metodo` y es exactamente el tipo de detalle que
   diferencia este portafolio. Reeditado en `/admin/`.
2. **Métricas del sitio propio** (clics en los botones de WhatsApp, clics en la
   carta PDF, visitas). Hay números de llamadas y clics del perfil en Google,
   pero no están desglosados en la web todavía. Si existen, van en
   `main/views.py` → `_jsonld()` y en el bloque de evidencia.
3. **Testimonio del cliente.** No hay ninguno de terceros.
4. Verificar que las imágenes de `media/` que existen solo en el servidor sigan
   ahí. Si desaparecieron, las tarjetas de Red de Apoyo Mutuo, Dr. Franco Álvarez
   y Ecommerce muestran el placeholder con textura, no se rompen.

## Pendientes técnicos del rediseño anterior (siguen abiertos)

- Las páginas internas de `comunidad/` y `ecommerce/` (`muro.html`,
  `perfil.html`, `lista_productos.html`) usan clases utilitarias de Bootstrap
  (`btn-primary`, `bg-primary`) que heredan la paleta nueva, pero el detalle fino
  de cada una no está revisado.
- El admin tiene 2FA obligatorio (`Admin2FAMiddleware`). Si pierdes el dispositivo
  TOTP, entra por consola con `python manage.py shell` y usa
  `django_otp.plugins.otp_totp.models.TOTPDevice.objects.all().delete()`.

## Deploy

```bash
git add -A && git commit -m "..." && git push
```

En PythonAnywhere:

```bash
source ~/venvs/mi_web/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

Y después **Web → Reload**.

Lo que corre en el servidor que no está en el repo:

- `db.sqlite3` (está en `.gitignore`): las migraciones `0006` y `0007` crean los
  campos nuevos y siembran los cuatro proyectos.
- `DJANGO_SECRET_KEY` en el entorno.
- `media/`.

## Seguridad (lo que se hizo en la pasada anterior)

- `SECRET_KEY` se lee de `DJANGO_SECRET_KEY`, sin fallback. La clave que estuvo
  escrita en `core/settings.py` y se publicó en GitHub **está rota**: hay que
  rotarla en producción si no se ha hecho ya.
- `DEBUG` se lee de `DJANGO_DEBUG` y por defecto es `False`.
- CSP con nonce: los `<style>` inline están permitidos
  (`style-src 'unsafe-inline'`), pero **todo `<script>` inline necesita
  `nonce="{{ request.nonce }}"`**. Si agregas JavaScript a una plantilla y no
  le pones el nonce, el navegador lo bloquea sin avisar en la consola.
- `django-axes` está en `AXES_ENABLED = not DEBUG`, pero el middleware está
  comentado en `MIDDLEWARE` (línea 61) y el backend no está en
  `AUTHENTICATION_BACKENDS`. Está así a propósito, por un problema de login del
  admin. Si lo reactivas, Cambia `AxesStandaloneBackend`, no `AxesModelBackend`
  (renombrado en django-axes 5.0).
