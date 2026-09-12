#!/usr/bin/env python3
"""EDU FORGE — frontend maximo del campus (anti-AI-slop, WCAG, offline-first).

Genera en <repo>/campus/: index.html, tokens.css, app.js, sw.js,
manifest.webmanifest. Reglas aplicadas (banco UI anti-'IA generica'):
  - un solo acento (hue 222), 80-90% neutros
  - jerarquia por luminancia/tamano, contenido REAL de los cursos
  - estados completos, AA 4.5:1, targets 44px, reduced-motion
  - sin gradientes violeta/cian por defecto, sin glass total, sin copy vacio
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eduforge import content  # noqa: E402
from eduforge.curriculum import REPO_COURSES  # noqa: E402

TOKENS_CSS = """/* campus tokens — un solo acento, AA, dark-first */
:root {
  --u: 1; --motion: 1; --hue: 222; --sat: 62%;
  --font-sans: ui-sans-serif, system-ui, "Segoe UI", Roboto, Arial, sans-serif;
  --font-mono: ui-monospace, "Cascadia Code", Consolas, monospace;
  --fs-xs: .875rem; --fs-sm: .98rem; --fs-md: 1.125rem;
  --fs-lg: 1.35rem; --fs-xl: 1.7rem; --fs-2xl: 2.2rem; --fs-3xl: 2.9rem;
  --sp-1: .25rem; --sp-2: .5rem; --sp-3: .75rem; --sp-4: 1rem;
  --sp-5: 1.25rem; --sp-6: 1.5rem; --sp-8: 2rem; --sp-12: 3rem;
  --r-sm: .5rem; --r-md: .75rem; --r-lg: 1rem; --r-full: 999px;
  --dur-fast: 120ms; --dur-base: 180ms; --dur-slow: 280ms;
  --ease-out: cubic-bezier(.2,.7,.2,1);
  --bg-page: hsl(222 30% 7%);
  --bg-surface: hsl(222 26% 11%);
  --bg-sunken: hsl(222 30% 5%);
  --bg-muted: hsl(222 22% 16%);
  --bg-hover: hsl(222 20% 20%);
  --text-1: hsl(220 25% 96%);
  --text-2: hsl(220 15% 78%);
  --text-3: hsl(220 10% 62%);
  --border: hsl(222 18% 20%);
  --accent: hsl(var(--hue) var(--sat) 66%);
  --accent-soft: hsl(var(--hue) 45% 20%);
  --accent-ink: hsl(222 30% 8%);
  --success: hsl(145 70% 52%);
  --danger: hsl(358 85% 64%);
  --warning: hsl(38 95% 58%);
  --focus-ring: 0 0 0 3px hsl(var(--hue) var(--sat) 66% / .35);
  --shadow: 0 8px 24px hsl(222 50% 2% / .5);
}
@media (prefers-reduced-motion: reduce) { :root { --motion: 0; } }

*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0; min-height: 100dvh;
  font: 400 var(--fs-md)/1.55 var(--font-sans);
  background: var(--bg-page); color: var(--text-1);
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3 { margin: 0; line-height: 1.15; letter-spacing: -.02em; }
h1 { font-size: var(--fs-3xl); } h2 { font-size: var(--fs-2xl); }
h3 { font-size: var(--fs-xl); }
p { max-width: 68ch; }
a { color: var(--accent); text-underline-offset: 3px; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
::selection { background: var(--accent); color: var(--accent-ink); }

.wrap { width: min(72rem, 100% - 2rem); margin-inline: auto; }
.skip-link {
  position: absolute; left: -999px; background: var(--bg-surface);
  color: var(--text-1); padding: var(--sp-3) var(--sp-4);
  border-radius: var(--r-md); z-index: 10;
}
.skip-link:focus { left: var(--sp-4); top: var(--sp-4); }

.topbar {
  position: sticky; top: 0; z-index: 5;
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--sp-4); min-height: 64px; padding-inline: var(--sp-5);
  background: hsl(222 30% 7% / .9); backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}
.brand { font-weight: 800; letter-spacing: -.03em; font-size: var(--fs-lg); }
.brand span { color: var(--accent); }

.hero { padding: var(--sp-12) 0 var(--sp-8); }
.hero p.lead { font-size: var(--fs-lg); color: var(--text-2); }

.grid-cursos {
  display: grid; gap: var(--sp-5); padding: var(--sp-8) 0;
  grid-template-columns: repeat(auto-fit, minmax(min(19rem, 100%), 1fr));
}
.card {
  background: var(--bg-surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: var(--sp-5);
  display: grid; gap: var(--sp-3); align-content: start;
  transition: border-color var(--dur-fast) var(--ease-out);
}
.card:hover { border-color: var(--accent); }
.card .meta { color: var(--text-3); font-size: var(--fs-xs); }
.card h3 a { color: var(--text-1); text-decoration: none; }
.card h3 a:hover { color: var(--accent); }

.badge {
  display: inline-flex; padding: .25rem .6rem; width: fit-content;
  border-radius: var(--r-full); font-size: var(--fs-xs);
  font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  background: var(--accent-soft); color: var(--accent);
}

.btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: .5em; min-height: 44px; padding: .6em 1.1em;
  border-radius: var(--r-md); border: 1px solid transparent;
  font: 600 var(--fs-sm) var(--font-sans); cursor: pointer;
  background: var(--accent); color: var(--accent-ink);
  transition: background-color var(--dur-fast) var(--ease-out);
  text-decoration: none;
}
.btn:hover { background: hsl(var(--hue) var(--sat) 72%); }
.btn:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.btn-ghost {
  background: transparent; color: var(--text-2); border-color: var(--border);
}
.btn-ghost:hover { background: var(--bg-hover); color: var(--text-1); }

.quiz-box {
  background: var(--bg-surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: var(--sp-5);
  margin: var(--sp-6) 0; display: grid; gap: var(--sp-4);
}
.quiz-box .opciones { display: grid; gap: var(--sp-2); }
.quiz-box .opcion {
  text-align: left; min-height: 48px; padding: .7em 1em;
  background: var(--bg-muted); border: 1px solid var(--border);
  border-radius: var(--r-md); color: var(--text-1); cursor: pointer;
  font: 500 var(--fs-sm) var(--font-sans);
}
.quiz-box .opcion:hover { background: var(--bg-hover); }
.quiz-box .opcion.correcta { border-color: var(--success); color: var(--success); }
.quiz-box .opcion.fallo { border-color: var(--danger); color: var(--danger); }
.quiz-box .feedback { min-height: 1.5em; color: var(--text-2); }
.marcador { font: 700 var(--fs-sm) var(--font-mono); color: var(--accent); }

.voz-player {
  display: flex; align-items: center; gap: var(--sp-3); flex-wrap: wrap;
  padding: var(--sp-4); background: var(--bg-sunken);
  border: 1px solid var(--border); border-radius: var(--r-lg);
  margin: var(--sp-4) 0;
}
.voz-player audio { width: 100%; min-width: 260px; }

.semanas { display: grid; gap: var(--sp-3); margin: var(--sp-5) 0; }
.semana {
  display: flex; gap: var(--sp-4); align-items: baseline;
  padding: var(--sp-4); background: var(--bg-surface);
  border: 1px solid var(--border); border-radius: var(--r-md);
  color: var(--text-1); text-decoration: none;
}
.semana:hover { border-color: var(--accent); }
.semana .n { font: 800 var(--fs-lg) var(--font-mono); color: var(--accent); }

footer { padding: var(--sp-8) 0; border-top: 1px solid var(--border);
  color: var(--text-3); font-size: var(--fs-xs); }

@media (max-width: 640px) {
  h1 { font-size: var(--fs-2xl); }
  .topbar { padding-inline: var(--sp-4); }
}
"""

APP_JS = """// campus app: quiz player + stagger + audit (sin dependencias)
document.documentElement.classList.add('js');

const $ = (sel, root = document) => root.querySelector(sel);

function loadQuiz(url) {
  const box = $('.quiz-box');
  if (!box) return;
  fetch(url).then(r => r.json()).then(items => {
    let idx = 0, score = 0;
    const titulo = $('.quiz-titulo', box);
    const opciones = $('.opciones', box);
    const feedback = $('.feedback', box);
    const marcador = $('.marcador', box);
    const btn = $('.quiz-siguiente', box);
    const render = () => {
      const q = items[idx];
      titulo.textContent = `${idx + 1}/${items.length} · ${q.pregunta}`;
      opciones.innerHTML = '';
      q.opciones.forEach((o, i) => {
        const b = document.createElement('button');
        b.className = 'opcion';
        b.textContent = o;
        b.addEventListener('click', () => {
          [...opciones.children].forEach((el, j) => {
            el.classList.add(j === q.correcta ? 'correcta' : 'fallo');
            el.disabled = true;
          });
          const ok = i === q.correcta;
          if (ok) score++;
          feedback.textContent = ok
            ? `Correcto. ${q.explicacion}`
            : `Incorrecto. ${q.explicacion}`;
          marcador.textContent = `Aciertos: ${score}`;
          btn.hidden = false;
        });
        opciones.appendChild(b);
      });
      btn.hidden = true;
    };
    btn.addEventListener('click', () => {
      idx++;
      if (idx >= items.length) {
        titulo.textContent = `Terminado: ${score}/${items.length}`;
        opciones.innerHTML = '';
        feedback.textContent = score >= items.length * 0.7
          ? 'Nivel superado.' : 'Repasa y vuelve a intentarlo.';
        btn.hidden = true;
        marcador.textContent = '';
        return;
      }
      render();
    });
    render();
  }).catch(() => {
    $('.quiz-titulo', box).textContent = 'Quiz no disponible offline.';
  });
}

// stagger sutil de tarjetas (respeta reduced-motion)
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduced) {
  document.querySelectorAll('.card').forEach((el, i) => {
    el.style.animation = 'rise var(--dur-slow) var(--ease-out) both';
    el.style.animationDelay = `${Math.min(i * 60, 300)}ms`;
  });
  const st = document.createElement('style');
  st.textContent = '@keyframes rise{from{opacity:0;transform:translateY(8px)}}';
  document.head.appendChild(st);
}

// auditoria rapida de accesibilidad (consola)
window.uiAudit = () => {
  const issues = [];
  document.querySelectorAll('img:not([alt])').forEach(() =>
    issues.push('img sin alt'));
  document.querySelectorAll('a, button').forEach(el => {
    const r = el.getBoundingClientRect();
    if ((r.width < 44 || r.height < 44) && !el.disabled)
      issues.push(`Target pequeno: ${el.tagName}`);
  });
  return issues;
};

// registro offline
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}

document.querySelectorAll('.quiz-json').forEach(el => loadQuiz(el.dataset.src));
"""

SW_JS = """// campus sw — offline-first (cache de lectura, red para lo nuevo)
const CACHE = 'campus-v1';
const CORE = ['./', './index.html', './tokens.css', './app.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request).then(r => {
      const copy = r.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
      return r;
    }).catch(() => caches.match(e.request).then(r => r || caches.match('./')))
  );
});
"""


def _index_html(repo_name: str, extras: set[str] | None = None,
                globales: bool = False, gobierno: bool = False) -> str:
    extras = extras or set()
    cursos = []
    for slug in REPO_COURSES.get(repo_name, []):
        c = content.CURSOS[slug]
        enlaces_extra = ""
        if slug in extras:
            enlaces_extra = (f"""
        <p class="meta">
          <a href="cursos/{slug}/glosario.md">Glosario</a> ·
          <a href="cursos/{slug}/chuleta.md">Chuleta</a> ·
          <a href="cursos/{slug}/laboratorio.md">Laboratorio</a> ·
          <a href="cursos/{slug}/rubrica.md">Rúbrica</a> ·
          <a href="cursos/{slug}/examen.md">Examen final</a>
        </p>""")
        cursos.append(f"""
      <article class="card">
        <span class="badge">{c['idioma'].upper()} · {c['nivel']}</span>
        <h3><a href="cursos/{slug}/index.html">{c['titulo']}</a></h3>
        <p>{c['descripcion'][:130]}…</p>
        <p class="meta">{len(c['semanas'])} semanas · {c['horas']} h · quiz {len(c['quiz'])} items</p>{enlaces_extra}
        <div><a class="btn" href="cursos/{slug}/index.html">Entrar al curso</a></div>
      </article>""")
    voces = "\n".join(
        f'          <option value="{lang}">{lang.upper()}</option>'
        for lang in ("es", "ca", "pt", "en"))
    nav_extra = (
        '\n      <a class="btn btn-ghost" href="buscar.html">Buscar</a>'
        '\n      <a class="btn btn-ghost" href="progreso.html">Progreso</a>'
        '\n      <a class="btn btn-ghost" href="credencial.html">Credencial</a>'
        if globales else "")
    seccion_gobierno = (
        """
    <section id="gobierno" aria-label="Gobierno académico">
      <h2>Gobierno académico</h2>
      <p class="meta">
        <a href="calendario.md">Calendario académico (4 años)</a> ·
        <a href="mapa-curricular.md">Mapa curricular NICE/CAE</a>
      </p>
    </section>
""" if gobierno else "")
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0c1018">
  <meta name="description" content="Campus abierto {repo_name}: cursos gratuitos estilo Harvard/Coursera, offline-first.">
  <title>Campus {repo_name}</title>
  <link rel="manifest" href="manifest.webmanifest">
  <link rel="stylesheet" href="tokens.css">
</head>
<body>
  <a class="skip-link" href="#cursos">Saltar al contenido</a>
  <header class="topbar">
    <div class="brand">Campus <span>{repo_name}</span></div>
    <nav aria-label="Principal">
      <a class="btn btn-ghost" href="#cursos">Cursos</a>
      <a class="btn btn-ghost" href="#quiz">Quiz</a>
      <a class="btn btn-ghost" href="#voz">Voz IA</a>{nav_extra}
    </nav>
  </header>

  <main class="wrap">
    <section class="hero">
      <h1>Educación abierta, sin barreras.</h1>
      <p class="lead">Cursos modulares con evidencia, material de bancos
      abiertos y voz humana en 4 idiomas. Funciona sin conexión.</p>
    </section>

    <section id="cursos" class="grid-cursos">{''.join(cursos)}
    </section>

    <section id="quiz" aria-label="Quiz de ejemplo">
      <h2>Quiz interactivo</h2>
      <div class="quiz-box quiz-json"
           data-src="cursos/{REPO_COURSES.get(repo_name, ['x'])[0]}/quiz.json">
        <h3 class="quiz-titulo">Cargando quiz…</h3>
        <div class="opciones"></div>
        <p class="feedback" aria-live="polite"></p>
        <p class="marcador"></p>
        <button class="btn quiz-siguiente" hidden>Siguiente</button>
      </div>
    </section>

    <section id="voz" aria-label="Voz IA">
      <h2>Voz humana por idioma</h2>
      <div class="voz-player">
        <label for="idioma">Idioma:</label>
        <select id="idioma" class="opcion" style="width:auto;min-height:44px">
{voces}
        </select>
        <audio id="audio" controls aria-label="Reproducir bienvenida">
          <source id="audio-src" src="voces/bienvenida-es.mp3" type="audio/mpeg">
        </audio>
      </div>
      <p class="meta">Voces generadas por edge-tts (gratuito) o Kokoro vía
      Hugging Face. Sin coste, con acento humano real.</p>
    </section>
{seccion_gobierno}
    <section id="agente" aria-label="Agente tutor">
      <h2>Agente tutor vivo en GitHub</h2>
      <p>Este campus tiene un agente IA que vive en GitHub Actions
      (caja Linux): responde issues etiquetados <code>tutor</code> y publica
      una cápsula didáctica diaria en <code>campus/capsulas/</code>.</p>
      <p class="meta">Cero secretos: usa el token efímero de GitHub y modelos
      gratuitos con fallback local.</p>
    </section>
  </main>

  <footer class="wrap">
    <p>Material abierto y verificado: Khan Academy · Parla.cat · GCF Global ·
    MIT OCW · OWASP WSTG · Juice Shop · freeCodeCamp. Generado por edu-forge.</p>
  </footer>
  <script>
    const sel = document.getElementById('idioma');
    if (sel) sel.addEventListener('change', e => {{
      const a = document.getElementById('audio-src');
      a.src = `voces/bienvenida-${{e.target.value}}.mp3`;
      document.getElementById('audio').load();
    }});
  </script>
  <script src="app.js"></script>
</body>
</html>
"""


def generate(target_root: Path, repo_name: str) -> None:
    campus = target_root / "campus"
    campus.mkdir(parents=True, exist_ok=True)
    (campus / "tokens.css").write_text(TOKENS_CSS, encoding="utf-8")
    (campus / "app.js").write_text(APP_JS, encoding="utf-8")
    (campus / "sw.js").write_text(SW_JS, encoding="utf-8")
    (campus / "index.html").write_text(
        _index_html(repo_name,
                    extras={s for s in REPO_COURSES.get(repo_name, [])
                            if (campus / "cursos" / s / "glosario.md").exists()},
                    globales=(campus / "progreso.html").exists(),
                    gobierno=(campus / "mapa-curricular.md").exists()),
        encoding="utf-8")
    manifest = {
        "name": f"Campus {repo_name}",
        "short_name": repo_name,
        "start_url": "./",
        "display": "standalone",
        "background_color": "#0c1018",
        "theme_color": "#0c1018",
        "icons": [],
    }
    (campus / "manifest.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    # robots-friendly link from repo root
    root_link = target_root / "campus.html"
    if not root_link.exists():
        root_link.write_text(
            f'<meta http-equiv="refresh" content="0; url=campus/">\n'
            f'<a href="campus/">Ir al campus {repo_name}</a>\n',
            encoding="utf-8")


def main() -> int:
    clones = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\Users\USER\AppData\Local\Temp\opencode\audit-deploys")
    for repo in REPO_COURSES:
        root = clones / repo
        if (root / ".git").exists():
            generate(root, repo)
            print(f"[{repo}] campus/ generado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
