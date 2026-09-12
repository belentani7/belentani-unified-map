#!/usr/bin/env python3
"""EDU FORGE audit — auditoría automática del campus generado.

Secciones: STRUCTURE / CONTENT / LINKS / I18N / HTML / JS / PYTHON /
SECURITY / ACADEMIC. Cada hallazgo lleva severidad (CRITICAL/HIGH/MEDIUM/LOW).
Exit 1 si hay CRITICAL o HIGH. Warns no bloquean, pero se reportan.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "wbr",
        "area", "base", "col", "embed", "track"}

PIEZAS = ["index.html", "syllabus.md", "glosario.md", "chuleta.md",
          "laboratorio.md", "rubrica.md", "examen.md", "recursos.md", "quiz.json"]
GLOBALES = ["index.html", "progreso.html", "credencial.html", "buscar.html",
            "indice.json", "idiomas.md", "manifest.webmanifest", "sw.js",
            "tokens.css", "app.js"]

SECRET_PAT = re.compile(
    r"(ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|xox[baprs]-[A-Za-z0-9-]{10,})", re.IGNORECASE)


class Balance(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, int]] = []
        self.ids: list[str] = []
        self.errores: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.append(d["id"])
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    self.errores.append(
                        f"</{tag}> l.{self.getpos()[0]} cierra sobre {self.stack[i + 1:]}")
                    del self.stack[i:]
                    return
            self.errores.append(f"</{tag}> sin abrir, l.{self.getpos()[0]}")


class Auditor:
    def __init__(self, root: Path):
        self.root = root
        self.campus = root / "campus"
        self.ok = 0
        self.hallazgos: list[tuple[str, str, str]] = []  # (sev, seccion, msg)

    def pasa(self) -> None:
        self.ok += 1

    def fallo(self, sev: str, seccion: str, msg: str) -> None:
        self.hallazgos.append((sev, seccion, msg))

    # ---------------- STRUCTURE ----------------
    def estructura(self) -> None:
        cursos = sorted(d for d in (self.campus / "cursos").iterdir()
                        if d.is_dir()) if (self.campus / "cursos").is_dir() else []
        if not cursos:
            self.fallo("CRITICAL", "STRUCTURE", "sin cursos en campus/cursos/")
            return
        for cdir in cursos:
            for pieza in PIEZAS:
                if (cdir / pieza).exists():
                    self.pasa()
                else:
                    self.fallo("HIGH", "STRUCTURE", f"{cdir.name}: falta {pieza}")
        for g in GLOBALES:
            if (self.campus / g).exists():
                self.pasa()
            else:
                self.fallo("HIGH", "STRUCTURE", f"global: falta {g}")
        # huérfanos: archivos no referenciados por ninguna página ni el índice
        referencias = ""
        for pag in self.campus.rglob("*.html"):
            referencias += pag.read_text(encoding="utf-8", errors="replace")
        indice = (self.campus / "indice.json")
        if indice.exists():
            referencias += indice.read_text(encoding="utf-8", errors="replace")
        for f in self.campus.rglob("*"):
            if not f.is_file() or f.suffix in {".mp3"}:
                continue
            rel = f.relative_to(self.campus).as_posix()
            if rel in ("sw.js", "manifest.webmanifest", "tokens.css", "app.js"):
                continue  # referenciados por nombre en plantillas
            if rel.startswith("agente/") or rel.endswith("quiz.json") \
                    or rel == "voces/manifest.json":
                continue  # artefactos del motor consumidos por workflows/JS
            if f.suffix in {".md", ".json", ".html", ".py"} and rel not in referencias:
                self.fallo("MEDIUM", "STRUCTURE", f"posible huérfano: {rel}")

    # ---------------- CONTENT ----------------
    BANNED = ("drivedopobre", "example.com/")

    def contenido(self) -> None:
        if not (self.campus / "cursos").is_dir():
            self.fallo("CRITICAL", "CONTENT", "campus/cursos/ no existe")
            return
        # cero referencias prohibidas en todo el repo (fuente de verdad excluida del motor)
        for f in list(self.root.rglob("*.md")) + list(self.root.rglob("*.html")) \
                + list(self.root.rglob("*.js")) + list(self.root.rglob("*.json")):
            if ".git" in f.parts:
                continue
            texto = f.read_text(encoding="utf-8", errors="replace").lower()
            for prohibido in self.BANNED:
                if prohibido in texto:
                    self.fallo("HIGH", "CONTENT",
                               f"referencia prohibida '{prohibido}' en "
                               f"{f.relative_to(self.root)}")
        cursos = sorted(d for d in (self.campus / "cursos").iterdir() if d.is_dir())
        for cdir in cursos:
            qf = cdir / "quiz.json"
            if not qf.exists():
                continue
            items = json.loads(qf.read_text(encoding="utf-8"))
            if len(items) < 6:
                self.fallo("MEDIUM", "CONTENT",
                           f"{cdir.name}: quiz con {len(items)} items (<6, checkpoint débil)")
            for n, q in enumerate(items, 1):
                if len(q.get("opciones", [])) != 4:
                    self.fallo("HIGH", "CONTENT",
                               f"{cdir.name} quiz item {n}: se esperaban 4 opciones")
                if not (0 <= q.get("correcta", -1) < len(q.get("opciones", []))):
                    self.fallo("HIGH", "CONTENT",
                               f"{cdir.name} quiz item {n}: 'correcta' fuera de rango")
                if not q.get("explicacion", "").strip():
                    self.fallo("MEDIUM", "CONTENT",
                               f"{cdir.name} quiz item {n}: sin explicación")
                self.pasa()
            # coherencia de evaluación 30/30/40
            rub = (cdir / "rubrica.md").read_text(encoding="utf-8") \
                if (cdir / "rubrica.md").exists() else ""
            if rub and not all(p in rub for p in ("30", "40")):
                self.fallo("HIGH", "CONTENT",
                           f"{cdir.name}: rúbrica sin pesos 30/30/40")
            elif rub:
                self.pasa()
            exa = (cdir / "examen.md").read_text(encoding="utf-8") \
                if (cdir / "examen.md").exists() else ""
            if exa and ("Proyecto" not in exa or "Entregables" not in exa):
                self.fallo("MEDIUM", "CONTENT",
                           f"{cdir.name}: examen sin brief de proyecto con entregables")
            elif exa:
                self.pasa()
            # recursos con repos GitHub verificados (≥2 por curso)
            rec = (cdir / "recursos.md").read_text(encoding="utf-8") \
                if (cdir / "recursos.md").exists() else ""
            n_github = rec.count("https://github.com/")
            if n_github < 2:
                self.fallo("MEDIUM", "CONTENT",
                           f"{cdir.name}: recursos sin repos verificados ({n_github})")
            else:
                self.pasa()

    # ---------------- LINKS ----------------
    def enlaces(self) -> None:
        paginas = sorted(self.campus.rglob("*.html")) + [self.root / "index.html",
                                                         self.root / "404.html"]
        href_re = re.compile(r'(?:href|src)="([^"]+?)"')
        for pag in paginas:
            if not pag.exists():
                continue
            texto = pag.read_text(encoding="utf-8", errors="replace")
            ids = set(re.findall(r'id="([^"]+)"', texto))
            base = pag.parent
            for destino in href_re.findall(texto):
                if destino.startswith(("http", "data:", "mailto:", "javascript:",
                                       "crypto:", "//")):
                    if destino.startswith("http://") and "localhost" not in destino:
                        self.fallo("MEDIUM", "SECURITY",
                                   f"{pag.name}: URL no-https {destino[:60]}")
                    continue
                if "{" in destino:
                    continue  # template literal JS
                if destino.startswith("#"):
                    if destino[1:] and destino[1:] not in ids:
                        self.fallo("HIGH", "LINKS",
                                   f"{pag.name}: ancla rota {destino}")
                    else:
                        self.pasa()
                    continue
                ruta = destino.split("#")[0].split("?")[0]
                if not ruta:
                    continue
                base_abs = self.root if ruta.startswith("/") else base
                if (base_abs / ruta.lstrip("/")).exists():
                    self.pasa()
                else:
                    self.fallo("HIGH", "LINKS",
                               f"{pag.relative_to(self.root)}: enlace roto {destino}")

    # ---------------- I18N ----------------
    def i18n(self) -> None:
        f = self.root / "ui" / "i18n.js"
        if not f.exists():
            self.fallo("HIGH", "I18N", "ui/i18n.js no existe")
            return
        if not shutil.which("node"):
            self.fallo("MEDIUM", "I18N", "node no disponible: paridad no verificada")
            return
        f_js = str(f).replace("\\", "/")
        script = (
            "global.window={};global.navigator={language:'pt'};"
            "global.location={search:''};"
            "global.localStorage={getItem:()=>null,setItem:()=>{}};"
            "global.document={documentElement:{lang:'pt'},querySelectorAll:()=>[],"
            "title:'',querySelector:()=>null};"
            f'require("{f_js}");'
            "const a=window.SecureTI18n;"
            "const d={pt:a.dict('pt'),es:a.dict('es'),en:a.dict('en')};"
            "const ks=Object.fromEntries(Object.keys(d).map(l=>[l,new Set(Object.keys(d[l]))]));"
            "let bad=0;"
            "for(const [x,y] of [['pt','es'],['pt','en'],['es','en']]){"
            "for(const k of ks[x]) if(!ks[y].has(k)){console.log('missing '+y+' '+k);bad++;}}"
            "const html=require('fs').readFileSync(process.argv[1],'utf8');"
            "const used=[...html.matchAll(/data-i18n(?:-html|-aria)?=\"([^\"]+)\"/g)].map(m=>m[1]);"
            "for(const k of new Set(used)) if(!ks.pt.has(k)||!ks.es.has(k)||!ks.en.has(k)){"
            "console.log('unused-or-missing '+k);bad++;}"
            "process.exit(bad?1:0);")
        r = subprocess.run(["node", "-e", script, str(self.root / "index.html")],
                           capture_output=True, text=True)
        if r.returncode == 0:
            self.pasa()
        else:
            self.fallo("MEDIUM", "I18N", f"paridad/referencias i18n: {r.stdout.strip()[:200]}")

    # ---------------- HTML ----------------
    def html(self) -> None:
        paginas = sorted(self.campus.rglob("*.html")) + [self.root / "index.html"]
        for pag in paginas:
            if not pag.exists():
                continue
            b = Balance()
            b.feed(pag.read_text(encoding="utf-8", errors="replace"))
            for err in b.errores:
                self.fallo("HIGH", "HTML", f"{pag.relative_to(self.root)}: {err}")
            for tag, linea in b.stack:
                self.fallo("HIGH", "HTML",
                           f"{pag.relative_to(self.root)}: <{tag}> sin cerrar (l.{linea})")
            dup = {i for i in b.ids if b.ids.count(i) > 1}
            if dup:
                self.fallo("MEDIUM", "HTML",
                           f"{pag.name}: ids duplicados {sorted(dup)[:5]}")
            if not b.errores and not b.stack and not dup:
                self.pasa()

    # ---------------- JS ----------------
    def js(self) -> None:
        if not shutil.which("node"):
            self.fallo("MEDIUM", "JS", "node no disponible: sintaxis no verificada")
            return
        objetivos: list[tuple[str, str]] = []
        i18n = self.root / "ui" / "i18n.js"
        if i18n.exists():
            objetivos.append(("ui/i18n.js", i18n.read_text(encoding="utf-8")))
        for pag in self.campus.rglob("*.html"):
            texto = pag.read_text(encoding="utf-8", errors="replace")
            for bloque in re.findall(r"<script>(.*?)</script>", texto, re.S):
                objetivos.append((f"{pag.name}#script", bloque))
        with tempfile.TemporaryDirectory() as td:
            for nombre, codigo in objetivos:
                tf = Path(td) / "check.js"
                tf.write_text(codigo, encoding="utf-8")
                r = subprocess.run(["node", "--check", str(tf)],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    self.fallo("HIGH", "JS",
                               f"sintaxis en {nombre}: {r.stderr.strip()[:150]}")
                else:
                    self.pasa()

    # ---------------- PYTHON ----------------
    def python(self) -> None:
        motor = Path(__file__).resolve().parent
        fallos = 0
        for py in sorted(motor.glob("*.py")):
            r = subprocess.run([sys.executable, "-m", "py_compile", str(py)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                self.fallo("CRITICAL", "PYTHON", f"no compila {py.name}")
                fallos += 1
            else:
                self.pasa()
        if fallos == 0:
            self.pasa()

    # ---------------- SECURITY ----------------
    def seguridad(self) -> None:
        archivos: list[Path] = []
        for pat in ("*.py", "*.js", "*.html", "*.yml", "*.md", "*.json", "*.toml",
                    "*.xml", "*.txt"):
            archivos += list(self.root.rglob(pat))
        archivos += [self.root / "index.html"]
        vistos = set()
        for f in archivos:
            if ".git" in f.parts or f in vistos or not f.exists():
                continue
            vistos.add(f)
            m = SECRET_PAT.search(f.read_text(encoding="utf-8", errors="replace"))
            if m:
                self.fallo("CRITICAL", "SECURITY",
                           f"posible secreto en {f.relative_to(self.root)}: {m.group(1)[:12]}…")
            else:
                self.pasa()
        wfs = list((self.root / ".github" / "workflows").glob("*.yml")) \
            if (self.root / ".github" / "workflows").is_dir() else []
        if not wfs:
            self.fallo("MEDIUM", "SECURITY", "sin workflows que auditar")
        for wf in wfs:
            if "permissions:" in wf.read_text(encoding="utf-8"):
                self.pasa()
            else:
                self.fallo("HIGH", "SECURITY", f"{wf.name} sin permissions declarado")

    # ---------------- ACADEMIC ----------------
    def academico(self) -> None:
        try:
            from eduforge import content
            from eduforge.curriculum import REPO_COURSES
        except ImportError:
            self.fallo("MEDIUM", "ACADEMIC", "motor no importable: skipped")
            return
        slugs = REPO_COURSES.get(self.root.name, [])
        if not slugs:
            self.fallo("MEDIUM", "ACADEMIC", "repo sin cursos registrados en REPO_COURSES")
            return
        for slug in slugs:
            c = content.CURSOS.get(slug)
            if not c:
                self.fallo("HIGH", "ACADEMIC", f"{slug}: registrado pero no existe en content")
                continue
            if len(c["objetivos"]) < 3:
                self.fallo("MEDIUM", "ACADEMIC", f"{slug}: <3 learning outcomes")
            if len(c["semanas"]) < 4:
                self.fallo("MEDIUM", "ACADEMIC", f"{slug}: <4 semanas")
            if len(c["quiz"]) < 6:
                self.fallo("MEDIUM", "ACADEMIC", f"{slug}: quiz <6 items")
            self.pasa()

    # ---------------- CSS ----------------
    def css(self) -> None:
        paginas = sorted(self.campus.rglob("*.html")) + [self.root / "index.html"]
        for pag in paginas:
            if not pag.exists():
                continue
            for hoja in re.findall(r'href="([^"]+\.css)"',
                                   pag.read_text(encoding="utf-8", errors="replace")):
                if hoja.startswith("http"):
                    continue
                if (pag.parent / hoja).exists():
                    self.pasa()
                else:
                    self.fallo("HIGH", "CSS", f"{pag.name}: hoja inexistente {hoja}")
        tokens = self.campus / "tokens.css"
        if tokens.exists():
            texto = tokens.read_text(encoding="utf-8")
            if "focus-visible" in texto:
                self.pasa()
            else:
                self.fallo("MEDIUM", "ACCESSIBILITY",
                           "tokens.css sin :focus-visible")
            if "prefers-reduced-motion" in texto:
                self.pasa()
            else:
                self.fallo("MEDIUM", "ACCESSIBILITY",
                           "tokens.css sin prefers-reduced-motion")

    # ---------------- ACCESSIBILITY (basico automatizado) ----------------
    def accesibilidad(self) -> None:
        # NOTA: revis manual WCAG completa no realizada; esto es el subconjunto automatizable
        paginas = [self.root / "index.html", self.campus / "index.html"]
        for pag in paginas:
            if not pag.exists():
                continue
            texto = pag.read_text(encoding="utf-8", errors="replace")
            if re.search(r"<html[^>]+lang=", texto):
                self.pasa()
            else:
                self.fallo("HIGH", "ACCESSIBILITY", f"{pag.name}: sin lang")
            if "skip-link" in texto:
                self.pasa()
            else:
                self.fallo("MEDIUM", "ACCESSIBILITY",
                           f"{pag.name}: sin skip-link")
        for pag in self.campus.rglob("*.html"):
            texto = pag.read_text(encoding="utf-8", errors="replace")
            for img in re.findall(r"<img\b[^>]*>", texto):
                if "alt=" not in img:
                    self.fallo("HIGH", "ACCESSIBILITY",
                               f"{pag.name}: img sin alt")
        # enlaces solo-icono necesitan aria-label
        for pag in sorted(self.campus.rglob("*.html")) + [self.root / "index.html"]:
            if not pag.exists():
                continue
            texto = pag.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"<a\b[^>]*>\s*<i\b[^>]*>.*?</i>\s*</a>",
                                 texto, re.S):
                if "aria-label" not in m.group(0) and not re.search(
                        r">[^<]*\S[^<]*<", m.group(0).split(">", 1)[1].rsplit("<", 1)[0]):
                    self.fallo("MEDIUM", "ACCESSIBILITY",
                               f"{pag.name}: enlace solo-icono sin aria-label")

    # ---------------- PERFORMANCE (REVIEW con datos) ----------------
    def rendimiento(self) -> None:
        for pag in sorted(self.campus.rglob("*.html")) + [self.root / "index.html"]:
            if not pag.exists():
                continue
            texto = pag.read_text(encoding="utf-8", errors="replace")
            kb = len(texto.encode("utf-8")) / 1024
            if kb > 150:
                self.fallo("MEDIUM", "PERFORMANCE",
                           f"{pag.name}: {kb:.0f} KB de HTML")
            else:
                self.pasa()
            cdns = len(re.findall(r'src="https?://', texto))
            if cdns > 3:
                self.fallo("MEDIUM", "PERFORMANCE",
                           f"{pag.name}: {cdns} dependencias CDN")
            elif cdns:
                self.pasa()
        # audios de voces ligeros (PWA offline razonable)
        for mp3 in (self.campus / "voces").glob("*.mp3") \
                if (self.campus / "voces").is_dir() else []:
            kb = mp3.stat().st_size / 1024
            if kb > 300:
                self.fallo("MEDIUM", "PERFORMANCE",
                           f"{mp3.name}: {kb:.0f} KB (>300 KB)")
            else:
                self.pasa()

    # ---------------- DOCUMENTATION ----------------
    def documentacion(self) -> None:
        readme = self.root / "README.md"
        if not readme.exists():
            self.fallo("HIGH", "DOCUMENTATION", "sin README")
            return
        texto = readme.read_text(encoding="utf-8")
        if len(texto) < 1500:
            self.fallo("MEDIUM", "DOCUMENTATION",
                       f"README esqueleto ({len(texto)} chars)")
        for palabra in ("pytest", "eduforge", "audit"):
            if palabra in texto:
                self.pasa()
            else:
                self.fallo("MEDIUM", "DOCUMENTATION",
                           f"README no documenta {palabra}")
        story = self.root / "STORY.md"
        if story.exists():
            sv = story.read_text(encoding="utf-8")
            if "READY FOR PRODUCTION" in sv:
                self.fallo("HIGH", "DOCUMENTATION",
                           'STORY afirma "READY FOR PRODUCTION"')
            else:
                self.pasa()
        # security.txt: canal de contacto de seguridad declarado
        if (self.root / "public" / "security.txt").exists():
            self.pasa()
        else:
            self.fallo("MEDIUM", "DOCUMENTATION", "sin public/security.txt")

    # ---------------- DEPLOY ----------------
    def deploy(self) -> None:
        sm = self.root / "public" / "sitemap.xml"
        if not sm.exists():
            self.fallo("MEDIUM", "DEPLOY", "sin public/sitemap.xml")
            return
        texto = sm.read_text(encoding="utf-8")
        if "example.com" in texto or "/about" in texto or "/contact" in texto:
            self.fallo("HIGH", "DEPLOY", "sitemap con rutas/dominio ficticios")
        else:
            self.pasa()
        for loc in re.findall(r"<loc>([^<]+)</loc>", texto):
            ruta = loc.replace("__BASE_URL__", "")
            destino = self.root / ruta.lstrip("/")
            if destino.exists() or (destino / "index.html").exists():
                self.pasa()
            else:
                self.fallo("HIGH", "DEPLOY", f"sitemap apunta a ruta inexistente: {ruta}")
        robots = self.root / "public" / "robots.txt"
        if robots.exists():
            rv = robots.read_text(encoding="utf-8")
            # el contenido real vive en /campus: no debe estar desindexado
            if "Disallow: /campus" in rv:
                self.fallo("HIGH", "DEPLOY", "robots desindexa /campus")
            else:
                self.pasa()
        else:
            self.fallo("MEDIUM", "DEPLOY", "sin public/robots.txt")
        # 404 real: página dedicada, no la landing enmascarando
        if (self.root / "404.html").exists():
            self.pasa()
        else:
            self.fallo("MEDIUM", "DEPLOY", "sin 404.html dedicado")
        # SITE_URL sin fijar: WARN documentado (dominio pendiente), no FAIL
        if "__BASE_URL__" in texto:
            self.fallo("MEDIUM", "DEPLOY",
                       "SITE_URL sin fijar: sitemap/robots usan placeholder "
                       "(documentado; fijar al desplegar)")
        netlify = self.root / "netlify.toml"
        if netlify.exists():
            nv = netlify.read_text(encoding="utf-8")
            if re.search(r'from = "/\*"', nv) and 'status = 200' in nv:
                self.fallo("MEDIUM", "DEPLOY",
                           "redirect SPA /* → 200 enmascara 404 reales")

    # ---------------- INFORME ----------------
    def informe(self) -> int:
        secciones = ["STRUCTURE", "CONTENT", "LINKS", "I18N", "HTML", "CSS",
                     "JS", "PYTHON", "SECURITY", "ACCESSIBILITY",
                     "PERFORMANCE", "ACADEMIC", "DOCUMENTATION", "DEPLOY"]
        print("EDUFORGE AUDIT")
        print("=" * 46)
        bloqueantes = 0
        for sec in secciones:
            mios = [h for h in self.hallazgos if h[1] == sec]
            criticos = sum(1 for h in mios if h[0] in ("CRITICAL", "HIGH"))
            estado = "FAIL" if criticos else ("WARN" if mios else "PASS")
            print(f"{sec:<15} {estado}")
            for sev, _, msg in mios:
                print(f"    [{sev}] {msg}")
        conteo = {s: sum(1 for h in self.hallazgos if h[0] == s)
                  for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
        print(f"\ncomprobaciones OK: {self.ok}")
        print(f"CRITICAL: {conteo['CRITICAL']}  HIGH: {conteo['HIGH']}  "
              f"MEDIUM: {conteo['MEDIUM']}  LOW: {conteo['LOW']}")
        bloqueantes = conteo["CRITICAL"] + conteo["HIGH"]
        if bloqueantes:
            print(f"RESULTADO: FAIL ({bloqueantes} bloqueantes)")
            return 1
        if conteo["MEDIUM"] or conteo["LOW"]:
            print("RESULTADO: PASS WITH WARNINGS")
        else:
            print("RESULTADO: PASS")
        return 0


def auditar(root: Path) -> int:
    a = Auditor(root)
    a.estructura()
    a.contenido()
    a.enlaces()
    a.i18n()
    a.html()
    a.js()
    a.python()
    a.seguridad()
    a.academico()
    a.css()
    a.accesibilidad()
    a.rendimiento()
    a.documentacion()
    a.deploy()
    return a.informe()


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\Users\USER\Documents\secure-t-university")
    return auditar(root)


if __name__ == "__main__":
    raise SystemExit(main())
