import json
import re

from django.test import TestCase
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
        self.assertIn("'IntersectionObserver' in window", html)
