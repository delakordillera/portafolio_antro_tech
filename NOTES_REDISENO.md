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
- **Tienes que rotar la clave en producción.** En PythonAnywhere: pestaña
  **Web** → busca la sección de tu archivo WSGI → agrega antes del import de
  la app:
  ```python
  import os
  os.environ['DJANGO_SECRET_KEY'] = 'PEGA_AQUÍ_LA_CLAVE_NUEVA'
  ```
  Clave nueva generada (guárdala en un gestor de contraseñas, no en el
  código): `__1*8ch5+p7-^jhbkk96g=dd8v3cy3l_3z@@v=_zk$@ao^a##7`
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
