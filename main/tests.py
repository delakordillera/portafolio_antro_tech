import json
import re
import tempfile

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Proyecto


class ProyectoModelTests(TestCase):
    def test_orden_puta_el_destacado_primero(self):
        Proyecto.objects.all().delete()
        normal = Proyecto.objects.create(titulo="Normal", descripcion_corta="x")
        destacado = Proyecto.objects.create(
            titulo="Destacado", descripcion_corta="x", destacado=True
        )
        self.assertEqual(list(Proyecto.objects.all()), [destacado, normal])

    def test_etapas_caen_a_los_campos_sueltos(self):
        proyecto = Proyecto.objects.create(
            titulo="Sin lista",
            descripcion_corta="x",
            problema="Observación",
            traduccion="Traducción",
        )
        etiquetas = [e["etiqueta"] for e in proyecto.etapas_narradas]
        self.assertEqual(etiquetas, ["Observación", "Traducción"])

    def test_la_lista_de_etapas_manda_si_esta_llena(self):
        proyecto = Proyecto.objects.create(
            titulo="Con lista",
            descripcion_corta="x",
            problema="No debería aparecer",
            etapas=[
                {"etiqueta": "Otra cosa", "texto": "Sí"},
                {"etiqueta": "Vacía", "texto": ""},
            ],
        )
        narradas = proyecto.etapas_narradas
        self.assertEqual(len(narradas), 1)
        self.assertEqual(narradas[0]["etiqueta"], "Otra cosa")

    def test_metricas_incompletas_se_descartan(self):
        proyecto = Proyecto.objects.create(
            titulo="Métricas",
            descripcion_corta="x",
            metricas=[
                {"valor": "10.111", "etiqueta": "personas"},
                {"valor": "", "etiqueta": "sin cifra"},
                {"valor": "5", "etiqueta": ""},
                {"texto": "basura"},
            ],
        )
        self.assertEqual(len(proyecto.metricas_validas), 1)

    def test_terminos_se_ordenan_de_mayor_a_menor(self):
        proyecto = Proyecto.objects.create(
            titulo="Términos",
            descripcion_corta="x",
            terminos=[
                {"termino": "comida", "busquedas": 792},
                {"termino": "restaurants", "busquedas": 3679},
                {"termino": "sin cifra"},
            ],
        )
        self.assertEqual(
            [t["termino"] for t in proyecto.terminos_validos],
            ["restaurants", "comida"],
        )
        self.assertEqual(proyecto.total_terminos, 4471)

    def test_captura_portada_respeta_el_orden(self):
        proyecto = Proyecto.objects.create(
            titulo="Capturas",
            descripcion_corta="x",
            capturas=[
                {"src": "a.webp"},
                {"src": "portada.webp", "portada": True},
            ],
        )
        self.assertEqual(proyecto.captura_portada["src"], "portada.webp")

    def test_captura_por_rol_devuelve_none_si_no_existe(self):
        proyecto = Proyecto.objects.create(
            titulo="Sin roles",
            descripcion_corta="x",
            capturas=[{"src": "a.webp"}],
        )
        self.assertIsNone(proyecto.captura_por_rol("movil"))
        self.assertIsNone(proyecto.dispositivos["escritorio"])

    def test_dispositivos_toma_escritorio_y_movil_por_rol(self):
        proyecto = Proyecto.objects.create(
            titulo="Con roles",
            descripcion_corta="x",
            capturas=[
                {"src": "pag.webp", "rol": "paginas"},
                {"src": "movil.webp", "rol": "movil"},
                {"src": "desk.webp", "rol": "escritorio"},
            ],
        )
        dispositivos = proyecto.dispositivos
        self.assertEqual(dispositivos["escritorio"]["src"], "desk.webp")
        self.assertEqual(dispositivos["movil"]["src"], "movil.webp")
        # El pantallazo de pagina completa no se muestra en la galeria.
        self.assertNotIn("pag.webp", [c["src"] for c in dispositivos.values()])

    def test_url_destino_prioriza_produccion_sobre_github(self):
        proyecto = Proyecto.objects.create(
            titulo="Enlaces",
            descripcion_corta="x",
            link_interno="/ecommerce/",
            link_github="https://github.com/delakordillera/x",
            url_produccion="https://ejemplo.cl/",
        )
        self.assertEqual(proyecto.url_destino, "https://ejemplo.cl/")
        self.assertTrue(proyecto.es_externo)

    def test_ruta_interna_no_se_marca_como_externa(self):
        proyecto = Proyecto.objects.create(
            titulo="Interno", descripcion_corta="x", link_interno="/apoyo-mutuo/"
        )
        self.assertFalse(proyecto.es_externo)


class PortadaTests(TestCase):
    """Comprueba que la migración de datos deja la portada en estado publicable."""

    def test_la_migracion_siembra_los_cuatro_proyectos(self):
        titulos = set(Proyecto.objects.values_list("titulo", flat=True))
        self.assertEqual(
            titulos,
            {
                "La Otra Estación",
                "Red de Apoyo Mutuo",
                "Dr. Franco Álvarez",
                "Plataforma Ecommerce",
            },
        )

    def test_hay_exactamente_un_proyecto_destacado(self):
        destacados = list(Proyecto.objects.filter(destacado=True))
        self.assertEqual(len(destacados), 1)
        self.assertEqual(destacados[0].titulo, "La Otra Estación")

    def test_portada_responde_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_portada_incluye_el_caso_destacado(self):
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn('id="caso-destacado"', html)
        self.assertIn("La Otra Estación", html)
        self.assertIn("laotraestacionrestaurant.cl", html)

    def test_portada_muestra_las_cuatro_etapas(self):
        html = self.client.get(reverse("home")).content.decode()
        for etiqueta in ("Observación", "Método", "Traducción", "Resultado"):
            self.assertIn(f">{etiqueta}<", html)

    def test_portada_muestra_las_metricas_del_cliente(self):
        html = self.client.get(reverse("home")).content.decode()
        for cifra in ("10.111", "5.557", "382", "87%", "3.679"):
            self.assertIn(cifra, html)
        self.assertIn("últimos 28 días", html)

    def test_el_jsonld_del_caso_es_json_valido(self):
        html = self.client.get(reverse("home")).content.decode()
        bloques = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S
        )
        tipos = {json.loads(b)["@type"] for b in bloques}
        self.assertIn("Person", tipos)
        self.assertIn("CreativeWork", tipos)
        obra = next(
            json.loads(b) for b in bloques if json.loads(b)["@type"] == "CreativeWork"
        )
        self.assertEqual(obra["name"], "La Otra Estación")
        self.assertEqual(obra["url"], "https://laotraestacionrestaurant.cl/")

    def test_la_tarjeta_del_destacado_no_abre_pestana_nueva(self):
        proyecto = Proyecto.objects.get(titulo="Red de Apoyo Mutuo")
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn(f'href="{proyecto.link_interno}"', html)
        self.assertNotIn(f'href="{proyecto.link_interno}" target="_blank"', html)

    def test_la_tarjeta_externa_si_abre_pestana_nueva(self):
        proyecto = Proyecto.objects.get(titulo="La Otra Estación")
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn(f'href="{proyecto.url_produccion}" target="_blank"', html)

    def test_proyecto_oculto_no_aparece(self):
        Proyecto.objects.filter(titulo="Red de Apoyo Mutuo").update(visible=False)
        html = self.client.get(reverse("home")).content.decode()
        self.assertEqual(html.count('class="project-card"'), 3)

    def test_sin_proyectos_la_portada_no_rompe(self):
        Proyecto.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertNotIn('id="caso-destacado"', html)
        self.assertIn("projects-empty", html)

    def test_caso_destacado_sin_campos_narrativos_no_rompe(self):
        Proyecto.objects.filter(destacado=True).update(
            problema="", metodo="", traduccion="", resultado="",
            etapas=[], capturas=[], metricas=[], terminos=[],
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('id="caso-destacado"', html)
        self.assertNotIn('<ol class="caso-etapas">', html)
        self.assertNotIn('<dl class="caso-metricas">', html)
        self.assertNotIn('class="caso-dispositivos"', html)

    def test_la_galeria_muestra_escritorio_y_movil(self):
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn('class="caso-dispositivos"', html)
        self.assertIn("portada-desktop.webp", html)
        self.assertIn("portada-movil.webp", html)
        # La captura de pagina completa queda fuera: recortada a 430px se ve
        # larga y vacia.
        self.assertNotIn("portada-completa.webp", html)

    def test_la_galeria_apunta_al_sitio_real(self):
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn("Ver el sitio en producci", html)

    def test_sin_js_el_contenido_no_queda_invisible(self):
        """Sin IntersectionObserver el sitio entero quedaria en opacity 0."""
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn("<noscript>", html)
        self.assertIn(".anim{opacity:1}", html)

    def test_las_tres_tarjetas_usan_la_miniatura_optimizada(self):
        """Las miniaturas 4:3 viven en static/, no en media/.

        Si el campo `imagen` vuelve a apuntar al JPEG, el template prioriza el
        upload del admin y la version de 30 KB nunca se ve.
        """
        html = self.client.get(reverse("home")).content.decode()
        for archivo in ("apoyo-mutuo.webp", "ecommerce.webp", "franco-alvarez.webp"):
            self.assertIn(archivo, html)
        for proyecto in Proyecto.objects.exclude(destacado=True):
            with self.subTest(proyecto=proyecto.titulo):
                self.assertEqual(proyecto.imagen, "")
                tarjetas = [
                    c for c in (proyecto.capturas or []) if c.get("rol") == "tarjeta"
                ]
                self.assertEqual(len(tarjetas), 1)
                self.assertTrue(tarjetas[0]["portada"])

    def test_el_upload_del_admin_sigue_ganando(self):
        """La precedencia documentada: admin > captura 'tarjeta' > placeholder.

        cover_url no es un campo del modelo: lo arma la vista y solo si el
        archivo existe en disco, para que un upload roto no deje la tarjeta sin
        imagen. Si el template dejara de mirar cover_url, la miniatura estatica
        volveria a ganarle siempre al upload del admin.
        """
        proyecto = Proyecto.objects.filter(destacado=False).first()
        proyecto.capturas = [
            {"src": "main/proyectos/estatica.webp", "rol": "tarjeta", "portada": True}
        ]
        proyecto.save(update_fields=["capturas"])

        # Sin archivo en disco: la vista deja cover_url en None y gana la captura.
        html = self.client.get(reverse("home")).content.decode()
        self.assertIn("estatica.webp", html)

        # Con archivo en disco: manda /media/. El ImageField tiene upload_to y
        # sufijo aleatorio, asi que el nombre se toma del propio campo y no se
        # hardcodea. MEDIA_ROOT va a un temporal para no escribir en media/.
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                proyecto.imagen.save("test.webp", ContentFile(b"contenido"), save=True)
                self.assertTrue(proyecto.imagen_existe)
                url_admin = proyecto.imagen.url
                html = self.client.get(reverse("home")).content.decode()
        self.assertIn(url_admin, html)
        self.assertNotIn("estatica.webp", html)

    def test_solo_el_destacado_lleva_barra_de_navegador(self):
        """La barra es del caso insignia; las otras tres miniaturas van limpias.

        Se prueba sobre el HTML renderizado y no sobre el modelo: Dr. Franco
        Alvarez tambien tiene url_produccion (su Vercel), asi que la condicion
        no puede ser "tiene URL de produccion" sino "es el destacado".
        """
        html = self.client.get(reverse("home")).content.decode()
        # El caso insignia usa `project-browser caso-browser`; el literal
        # `class="project-browser"` solo existe en las tarjetas de proyecto.
        self.assertEqual(html.count('class="project-browser"'), 1)
        proyecto_destacado = Proyecto.objects.filter(destacado=True).first()
        self.assertIn(proyecto_destacado.url_produccion, html)

    def test_el_alternado_usa_el_enlace_como_clave(self):
        """.project-card:nth-child(even) nunca matchea: cuelga de un <a>.

        Cada tarjeta es la primera hija de su project-link-wrap, asi que el
        alternado tiene que colgar del nth-child del propio <a>. Si se vuelve
        al selector sobre .project-card, la mitad de las tarjetas queda con la
        imagen siempre en la misma columna.
        """
        html = self.client.get(reverse("home")).content.decode()
        # Los comentarios del CSS mencionan el selector viejo para explicar el
        # bug, asi que la comparacion se hace solo sobre las reglas.
        css = re.sub(r"/\*.*?\*/", "", html, flags=re.S)
        self.assertIn(".projects-list > .project-link-wrap:nth-child(even)", css)
        self.assertNotIn(".project-card:nth-child(even)", css)

    def test_las_cajas_de_imagen_declaran_4_3(self):
        """Todas las miniaturas en la misma proporcion, con el alto flexible."""
        html = self.client.get(reverse("home")).content.decode()
        self.assertRegex(html, r"\.project-media\s*\{[^}]*aspect-ratio:\s*4\s*/\s*3")
        self.assertRegex(html, r"\.project-media\s*\{[^}]*align-self:\s*center")
        self.assertNotIn("min-height: 260px", html)

    def test_la_migracion_0009_guarda_el_jpeg_original(self):
        """revertir() restaura el nombre real del archivo.

        Si el nombre se derivara del titulo, "Red de Apoyo Mutuo" volveria
        como red.jpg y "Dr. Franco Alvarez" como dr.jpg, y ninguno de los dos
        archivos existe en media/.
        """
        import importlib

        from django.apps import apps as django_apps

        modulo = importlib.import_module(
            "main.migrations.0009_optimalizar_miniaturas"
        )
        esperados = {
            "Red de Apoyo Mutuo": "apoyo-mutuo.jpg",
            "Plataforma Ecommerce": "ecommerce.jpg",
            "Dr. Franco Álvarez": "franco-alvarez.jpg",
        }
        objetivos = modulo._objetivos(django_apps)
        self.assertEqual(len(objetivos), 3)
        for proyecto, datos in objetivos:
            with self.subTest(proyecto=proyecto.titulo):
                self.assertEqual(datos["imagen_anterior"], esperados[proyecto.titulo])

    def test_la_migracion_0009_no_toca_el_destacado(self):
        import importlib

        from django.apps import apps as django_apps

        modulo = importlib.import_module(
            "main.migrations.0009_optimalizar_miniaturas"
        )
        destacados = {p.titulo for p, _ in modulo._objetivos(django_apps)}
        self.assertNotIn("La Otra Estación", destacados)
