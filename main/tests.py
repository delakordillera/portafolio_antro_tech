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

    def _home(self):
        return self.client.get(reverse("home")).content.decode()

    def test_portada_muestra_los_proyectos_visibles_con_su_caso(self):
        html = self._home()
        for p in Proyecto.objects.filter(visible=True):
            with self.subTest(proyecto=p.titulo):
                self.assertIn(p.titulo, html)
        self.assertIn(reverse("proyecto", args=["la-otra-estacion"]), html)

    def test_proyecto_oculto_no_aparece(self):
        Proyecto.objects.filter(titulo="Red de Apoyo Mutuo").update(visible=False)
        html = self._home()
        self.assertNotIn("Red de Apoyo Mutuo", html)
        respuesta = self.client.get(reverse("proyecto", args=["red-de-apoyo-mutuo"]))
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_proyectos_la_portada_no_rompe(self):
        Proyecto.objects.all().delete()
        respuesta = self.client.get(reverse("home"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Estoy publicando los casos", respuesta.content.decode())

    def test_la_pagina_del_caso_responde_y_su_jsonld_es_valido(self):
        html = self.client.get(reverse("proyecto", args=["la-otra-estacion"])).content.decode()
        bloque = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(bloque)
        datos = json.loads(bloque.group(1))
        self.assertEqual(datos["name"], "La Otra Estación")

    def test_caso_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("proyecto", args=["no-existe"])).status_code, 404)

    def test_el_cotizador_recibe_los_casos_como_json(self):
        html = self._home()
        bloque = re.search(r'<script id="datos-casos" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(bloque)
        slugs = {c["slug"] for c in json.loads(bloque.group(1))}
        self.assertIn("la-otra-estacion", slugs)

    def test_la_portada_no_muestra_el_nombre_personal(self):
        html = self._home().replace("alexis-lara-viveros", "")
        self.assertNotIn("Alexis", html)

    def test_todos_los_scripts_inline_llevan_nonce(self):
        html = self._home()
        for etiqueta in re.findall(r"<script(?![^>]*\bsrc=)[^>]*>", html):
            if 'application/json' in etiqueta or 'application/ld+json' in etiqueta:
                continue
            with self.subTest(etiqueta=etiqueta):
                self.assertIn("nonce=", etiqueta)

    def test_sin_js_el_asistente_muestra_todos_los_pasos(self):
        """Los pasos solo se ocultan bajo .js: sin JavaScript se ve el formulario completo."""
        html = self._home()
        self.assertIn(".js .asistente .paso:not(.activo) { display: none; }", html)
        self.assertEqual(len(re.findall(r'class="paso( activo)?" data-paso', html)), 3)

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



class PieYErroresTests(TestCase):
    def setUp(self):
        Proyecto.objects.create(titulo='La Otra Estación', descripcion_corta='Restobar', tecnologias='HTML',
                                visible=True, url_produccion='https://example.com')
        Proyecto.objects.create(titulo='Proyecto oculto', descripcion_corta='x', tecnologias='HTML',
                                visible=False, url_produccion='https://example.org')

    def test_pie_lista_solo_trabajos_visibles(self):
        html = self.client.get('/').content.decode()
        pie = html[html.index('<footer'):]
        self.assertIn('/proyectos/la-otra-estacion/', pie)
        self.assertNotIn('Proyecto oculto', pie)
        self.assertNotIn('sin plantillas', pie)

    def test_sin_selector_de_tema(self):
        html = self.client.get('/').content.decode()
        self.assertNotIn('boton-tema', html)
        self.assertNotIn('data-elegir-tema', html)

    @override_settings(DEBUG=False)
    def test_404_con_diseno_propio(self):
        r = self.client.get('/no-existe/')
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, 'Esta página no existe', status_code=404)


class MedicionTests(TestCase):
    UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile'

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def enviar(self, datos, ua=None):
        return self.client.post('/m/', data=json.dumps(datos), content_type='application/json',
                                HTTP_USER_AGENT=ua or self.UA)

    def test_guarda_visita_sin_ip_y_con_origen(self):
        from .models import Evento
        r = self.enviar({'t': 'visita', 'p': '/', 'r': 'https://www.google.com/search?q=x'})
        self.assertEqual(r.status_code, 204)
        e = Evento.objects.get()
        self.assertEqual((e.tipo, e.ruta, e.origen, e.dispositivo), ('visita', '/', 'google.com', 'celular'))
        self.assertFalse(any('127.0.0.1' in str(getattr(e, f.name)) for f in Evento._meta.fields))

    def test_ignora_tipos_desconocidos_y_bots(self):
        from .models import Evento
        self.enviar({'t': 'hackeo', 'p': '/'})
        self.enviar({'t': 'visita', 'p': '/'}, ua='Googlebot/2.1')
        self.assertEqual(Evento.objects.count(), 0)

    def test_limite_por_visitante(self):
        from .models import Evento
        for _ in range(125):
            self.enviar({'t': 'cotizar', 'p': '/'})
        self.assertEqual(Evento.objects.count(), 120)

    def test_solo_post(self):
        self.assertEqual(self.client.get('/m/').status_code, 405)

    def test_panel_privado(self):
        from django.contrib.auth.models import User
        self.assertEqual(self.client.get('/panel/metricas/').status_code, 302)
        User.objects.create_user('admin', password='clave-larga-123', is_staff=True)
        self.client.login(username='admin', password='clave-larga-123')
        self.enviar({'t': 'visita', 'p': '/'})
        self.enviar({'t': 'cotizar', 'p': '/'})
        r = self.client.get('/panel/metricas/')
        self.assertContains(r, 'Métricas del sitio')
        self.assertEqual(r['X-Robots-Tag'], 'noindex')


class SinGithubTests(TestCase):
    def test_no_hay_enlaces_a_github(self):
        html = self.client.get('/').content.decode()
        self.assertNotIn('github.com', html)
