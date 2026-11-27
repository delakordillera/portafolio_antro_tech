/* delakordillera: interacciones del portafolio.
   Todo es mejora progresiva: sin JS, sin WebGL o con "reducir movimiento",
   el contenido se ve completo y quieto. */
(function () {
    'use strict';

    var sinMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var punteroFino = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    /* ------------------------------------------------------------------
       1. Topografía WebGL de la portada: curvas de nivel doradas que se
          levantan como un cerro bajo el cursor.
    ------------------------------------------------------------------ */
    function iniciarTopografia(canvas) {
        var gl = canvas.getContext('webgl', { antialias: false, alpha: true, premultipliedAlpha: false });
        if (!gl) { canvas.remove(); return; }

        var vert = 'attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }';
        // fwidth necesita una extensión en WebGL1; si no está, se usa un grosor fijo.
        var conDerivadas = !!gl.getExtension('OES_standard_derivatives');
        var frag = (conDerivadas ? '#extension GL_OES_standard_derivatives : enable\n' : '') + [
            'precision mediump float;',
            'uniform vec2 res; uniform float t; uniform vec2 m; uniform float mFuerza;',
            'float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }',
            'float ruido(vec2 p){ vec2 i = floor(p), f = fract(p); vec2 u = f * f * (3.0 - 2.0 * f);',
            '  return mix(mix(h(i), h(i + vec2(1.0, 0.0)), u.x), mix(h(i + vec2(0.0, 1.0)), h(i + vec2(1.0, 1.0)), u.x), u.y); }',
            'float fbm(vec2 p){ float v = 0.0; float a = 0.5; for (int k = 0; k < 5; k++){ v += a * ruido(p); p *= 2.02; a *= 0.5; } return v; }',
            'void main(){',
            '  vec2 uv = gl_FragCoord.xy / res.y;',
            '  vec2 mm = m / res.y;',
            '  float alt = fbm(uv * 2.2 + vec2(t * 0.012, t * 0.006));',
            '  float d = distance(uv, mm);',
            '  alt += mFuerza * 0.32 * exp(-d * d * 9.0);',
            '  float n = alt * 16.0;',
            conDerivadas ? '  float w = fwidth(n) * 1.6;' : '  float w = 0.08;',
            '  float dist = 0.5 - abs(fract(n) - 0.5);',
            '  float linea = 1.0 - smoothstep(0.0, w, dist);',
            '  float mayor = step(0.75, fract(n / 4.0 + 0.125));',
            '  float brillo = 0.30 + 0.30 * mayor + 0.45 * mFuerza * exp(-d * d * 6.0);',
            '  gl_FragColor = vec4(vec3(0.79, 0.64, 0.40), linea * brillo);',
            '}'
        ].join('\n');

        function shader(tipo, src) {
            var s = gl.createShader(tipo); gl.shaderSource(s, src); gl.compileShader(s);
            if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { throw new Error(gl.getShaderInfoLog(s)); }
            return s;
        }
        var prog;
        try {
            prog = gl.createProgram();
            gl.attachShader(prog, shader(gl.VERTEX_SHADER, vert));
            gl.attachShader(prog, shader(gl.FRAGMENT_SHADER, frag));
            gl.linkProgram(prog);
            if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error('link');
        } catch (e) { canvas.remove(); return; }
        gl.useProgram(prog);

        var buf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
        var loc = gl.getAttribLocation(prog, 'p');
        gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

        var uRes = gl.getUniformLocation(prog, 'res');
        var uT = gl.getUniformLocation(prog, 't');
        var uM = gl.getUniformLocation(prog, 'm');
        var uF = gl.getUniformLocation(prog, 'mFuerza');

        var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        var w = 0, h = 0;
        var mouse = { x: -9999, y: -9999, tx: -9999, ty: -9999, f: 0, tf: 0 };
        var visible = true, raf = 0, t0 = performance.now();

        function medir() {
            var r = canvas.getBoundingClientRect();
            w = Math.max(1, Math.round(r.width * dpr));
            h = Math.max(1, Math.round(r.height * dpr));
            canvas.width = w; canvas.height = h;
            gl.viewport(0, 0, w, h);
        }
        function dibujar(ahora) {
            mouse.x += (mouse.tx - mouse.x) * 0.08;
            mouse.y += (mouse.ty - mouse.y) * 0.08;
            mouse.f += (mouse.tf - mouse.f) * 0.05;
            gl.uniform2f(uRes, w, h);
            gl.uniform1f(uT, sinMovimiento ? 0 : (ahora - t0) / 1000);
            gl.uniform2f(uM, mouse.x, mouse.y);
            gl.uniform1f(uF, mouse.f);
            gl.clearColor(0, 0, 0, 0);
            gl.clear(gl.COLOR_BUFFER_BIT);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        }
        function asentado() { return Math.abs(mouse.tx - mouse.x) < 0.5 && Math.abs(mouse.ty - mouse.y) < 0.5 && Math.abs(mouse.tf - mouse.f) < 0.01; }
        function bucle(ahora) {
            dibujar(ahora);
            // Sin "reducir movimiento" la topografía deriva sola; con él, solo responde al cursor.
            var seguir = visible && !document.hidden && (!sinMovimiento || !asentado());
            raf = seguir ? requestAnimationFrame(bucle) : 0;
        }
        function arrancar() { if (!raf) raf = requestAnimationFrame(bucle); }

        medir();
        dibujar(performance.now());
        window.addEventListener('resize', function () { medir(); dibujar(performance.now()); }, { passive: true });

        {
            new IntersectionObserver(function (e) { visible = e[0].isIntersecting; if (visible) arrancar(); }).observe(canvas);
            document.addEventListener('visibilitychange', arrancar);
            var zona = canvas.parentElement;
            zona.addEventListener('pointermove', function (e) {
                var r = canvas.getBoundingClientRect();
                mouse.tx = (e.clientX - r.left) * dpr;
                mouse.ty = (r.bottom - e.clientY) * dpr;
                if (mouse.x < -1000) { mouse.x = mouse.tx; mouse.y = mouse.ty; }
                mouse.tf = 1;
                arrancar();
            }, { passive: true });
            zona.addEventListener('pointerleave', function () { mouse.tf = 0; arrancar(); });
            arrancar();
        }
    }
    var topo = document.getElementById('topografia');
    if (topo) iniciarTopografia(topo);

    /* ------------------------------------------------------------------
       2. Inclinación 3D de las capturas al pasar el mouse.
    ------------------------------------------------------------------ */
    if (punteroFino) {
        var grados = sinMovimiento ? 3 : 7;
        document.querySelectorAll('[data-inclinar]').forEach(function (el) {
            var objetivo = el.querySelector('.lamina-escritorio') || el;
            el.addEventListener('pointermove', function (e) {
                var r = el.getBoundingClientRect();
                var x = (e.clientX - r.left) / r.width - 0.5;
                var y = (e.clientY - r.top) / r.height - 0.5;
                objetivo.style.transform = 'perspective(1100px) rotateY(' + (x * grados).toFixed(2) + 'deg) rotateX(' + (-y * grados * 0.85).toFixed(2) + 'deg)';
            });
            el.addEventListener('pointerleave', function () { objetivo.style.transform = ''; });
        });
    }

    /* ------------------------------------------------------------------
       3. Foco de luz que sigue al cursor en las tarjetas de servicios.
    ------------------------------------------------------------------ */
    if (punteroFino) {
        document.querySelectorAll('[data-foco]').forEach(function (grupo) {
            grupo.addEventListener('pointermove', function (e) {
                grupo.querySelectorAll('.foco').forEach(function (c) {
                    var r = c.getBoundingClientRect();
                    c.style.setProperty('--x', (e.clientX - r.left) + 'px');
                    c.style.setProperty('--y', (e.clientY - r.top) + 'px');
                });
            }, { passive: true });
        });
    }

    /* ------------------------------------------------------------------
       4. GSAP: un solo momento de entrada en la portada y tarjetas de
          proyecto que se apilan al hacer scroll.
    ------------------------------------------------------------------ */
    if (window.gsap && !sinMovimiento) {
        var gsap = window.gsap;
        if (window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);
        if (window.SplitText) gsap.registerPlugin(window.SplitText);

        var titulo = document.querySelector('[data-titulo-portada]');
        if (titulo && window.SplitText) {
            document.fonts.ready.then(function () {
                var split = new window.SplitText(titulo, { type: 'lines', mask: 'lines', linesClass: 'linea-titulo' });
                gsap.from(split.lines, { yPercent: 110, duration: 0.9, ease: 'expo.out', stagger: 0.09, delay: 0.1 });
                gsap.from('[data-entra]', { y: 18, opacity: 0, duration: 0.8, ease: 'expo.out', stagger: 0.08, delay: 0.35 });
            });
        }

        if (window.ScrollTrigger) {
            var mm = gsap.matchMedia();
            mm.add('(min-width: 1024px)', function () {
                var tarjetas = gsap.utils.toArray('.obra');
                tarjetas.forEach(function (t, i) {
                    if (i === tarjetas.length - 1) return;
                    gsap.to(t, {
                        scale: 0.94, filter: 'brightness(0.82)', ease: 'none',
                        scrollTrigger: { trigger: tarjetas[i + 1], start: 'top bottom', end: 'top 20%', scrub: true }
                    });
                });
                var collage = document.querySelector('.collage');
                if (collage) {
                    gsap.to(collage, { yPercent: -10, ease: 'none', scrollTrigger: { trigger: '.portada', start: 'top top', end: 'bottom top', scrub: true } });
                }
            });
        }
    }
})();
