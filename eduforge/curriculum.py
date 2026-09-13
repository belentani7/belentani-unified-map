#!/usr/bin/env python3
"""EDU FORGE — genera la estructura campus/ estilo Harvard/Coursera en cada repo.

Por target:
  campus/
    index.html          (hub premium, generado por frontend.py)
    tokens.css
    manifest.webmanifest
    sw.js               (offline-first)
    cursos/<slug>/
      syllabus.md
      semana-01.md .. semana-N.md
      quiz.json
      recursos.md       (bancos abiertos + drivedopobre.com)
    juegos/             (los 5 juegos Python del alumno William)
    voces/manifest.json (guion de voces por idioma)
    capsulas/           (capsula del dia, la agrega el agente GitHub)
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eduforge import content  # noqa: E402

# Patch: load expanded weeks for Secure-T University courses
try:
    import json
    expanded_path = Path(__file__).parent / "content_expanded.json"
    if expanded_path.exists():
        with expanded_path.open(encoding="utf-8") as f:
            expanded = json.load(f)
        for slug, curso in expanded.items():
            if slug in content.CURSOS:
                content.CURSOS[slug]["semanas"] = curso["semanas"]
except Exception:
    pass  # fallback to default content.CURSOS

HERE = Path(__file__).resolve().parent

# cursos que van a cada repo target
REPO_COURSES = {
    "ManosAbiertas": ["alfabetizacion-ia", "office-sin-miedo",
                      "falsos-amigos-pt-es"],
    "lingua-aberta": ["falsos-amigos-pt-es", "catalan-a1-brasileiros",
                      "espanol-academico-eso"],
    "ux-academy-professional-program": ["ux-profesional"],
    "linguaforge": ["forja-linguistica"],
    "open-school": ["ciberseguridad-5-anios"],
    # 2a sala: la universidad de ciber/IA, con sus 4 cursos principales
    "secure-t-university": ["ciber-ofensiva", "ciber-defensiva",
                            "ia-aplicada-segura", "gobernanza-compliance"],
}

VOICE_SCRIPTS = {
    "pt": ("pt-BR-FranciscaNeural",
           "Bem-vindo ao seu campus aberto. Aprenda no seu ritmo, com material "
           "gratuito e sem barreiras."),
    "es": ("es-ES-ElviraNeural",
           "Bienvenido a tu campus abierto. Aprende a tu ritmo, con material "
           "gratuito y sin barreras."),
    "en": ("en-US-AriaNeural",
           "Welcome to your open campus. Learn at your own pace, with free "
           "materials and no barriers."),
    "ca": ("ca-ES-JoanaNeural",
           "Benvingut al teu campus obert. Aprèn al teu ritme, amb material "
           "gratuït i sense barreres."),
}


def _md_syllabus(curso) -> str:
    sem = "\n".join(
        f"## Semana {s['n']}: {s['titulo']}\n\n"
        + "\n".join(f"- [{l['tipo'].upper()}] {l['titulo']}"
                    for l in s["lecciones"])
        for s in curso["semanas"])
    obj = "\n".join(f"- {o}" for o in curso["objetivos"])
    return f"""# {curso['titulo']}

> Nivel: {curso['nivel']} · {curso['horas']} horas · Idioma principal: {curso['idioma'].upper()}

## Descripcion

{curso['descripcion']}

## Objetivos de aprendizaje (evidencia)

{obj}

## Evaluacion estilo Harvard

- Participacion y ejercicios semanales: 30%
- Quizzes formativos por semana: 30%
- Proyecto final con evidencia: 40%
- Todo se aprueba demostrando, no adivinando.

## Cronograma

{sem}

## Recursos

Ver [recursos.md](recursos.md) — bancos abiertos + Drive do Pobre.
"""


def _md_semana(curso, semana) -> str:
    from eduforge.didactico import material as _mat
    from eduforge.profundidad import PROFUNDIDAD
    rico = _mat(curso["slug"], semana["n"])
    if rico:
        return _md_semana_rica(curso, semana, rico)
    lec = "\n\n".join(
        f"## {l['tipo'].upper()}: {l['titulo']}\n\n{l['texto']}"
        for l in semana["lecciones"])
    # capa de profundidad: semanas con lectura densa + práctica guiada
    prof = PROFUNDIDAD.get(curso["slug"], {}).get(semana["n"])
    extra = ""
    if prof:
        extra = (f"\n## 🎯 Objetivo de la semana\n\n{prof['objetivo']}\n\n"
                 f"## 📖 Lectura principal\n\n{prof['lectura']}\n\n"
                 f"## 🛠️ Práctica guiada\n\n{prof['practica']}\n")
    return f"""# Semana {semana['n']}: {semana['titulo']}

Curso: [{curso['titulo']}](../syllabus.md) · Semana {semana['n']} de {len(curso['semanas'])}

{lec}
{extra}
---
[Volver al syllabus](../syllabus.md)
"""


def _md_semana_rica(curso, semana, rico) -> str:
    partes = [
        f"# Semana {semana['n']}: {semana['titulo']}\n",
        f"Curso: [{curso['titulo']}](../syllabus.md) · "
        f"Semana {semana['n']} de {len(curso['semanas'])}\n",
    ]
    if rico.get("objetivos"):
        partes.append("## Objetivos de aprendizaje\n")
        partes.extend(f"- {o}" for o in rico["objetivos"])
        partes.append("")
    for sec in rico.get("secciones", []):
        partes.append(f"## {sec['titulo']}\n")
        partes.append(sec["contenido"])
        if sec.get("referencias"):
            partes.append("\n**Referencias:**")
            partes.extend(f"- {r}" for r in sec["referencias"])
        partes.append("")
    cr = rico.get("caso_real")
    if cr:
        partes.append(f"## Caso real: {cr['titulo']}\n")
        partes.append(cr["descripcion"])
        partes.append("")
    ej = rico.get("ejercicio")
    if ej:
        partes.append(f"## Ejercicio guiado: {ej['titulo']}\n")
        for i, p in enumerate(ej["pasos"], 1):
            partes.append(f"{i}. {p}")
        partes.append("")
    if rico.get("recursos"):
        partes.append("## Recursos abiertos\n")
        for nombre, url in rico["recursos"]:
            partes.append(f"- [{nombre}]({url})")
        partes.append("")
    partes.append("---")
    partes.append("[Volver al syllabus](../syllabus.md)")
    return "\n".join(partes) + "\n"


def _md_recursos(curso) -> str:
    langs = {curso["idioma"]}
    if curso["idioma"] == "ca":
        langs |= {"es", "pt"}
    if curso["idioma"] == "es":
        langs |= {"en", "pt"}
    if curso["idioma"] == "pt":
        langs |= {"es", "en"}
    orden = content.LANG_ORDER  # regla del ecosistema: pt > es > en > ca
    bloques = []
    for lang in sorted(langs, key=lambda l: orden.index(l) if l in orden else 99):
        if lang not in content.OPEN_BANKS:
            continue
        filas = "\n".join(
            f"- [{n}]({u}) — {d}" for n, u, d in content.OPEN_BANKS[lang])
        bloques.append(f"### {lang.upper()}\n\n{filas}")
    repos = "\n".join(
        f"- [{n}]({u}) — {d} ({s})"
        for n, u, d, s in content.REPOS_VERIFICADOS)
    apis = "\n".join(
        f"- [{n}]({u}) — {d}" for n, u, d in content.APIS_VERIFICADAS)
    return f"""# Recursos abiertos — {curso['titulo']}

## Repositorios verificados (GitHub, activos)

{repos}

## APIs abiertas verificadas (sin API key)

{apis}

{chr(10).join(bloques)}

## Regla de oro

Todo recurso externo está verificado (existencia y actividad comprobadas el
2026-09-12 vía GitHub API / HTTP) antes de citarse. Nada de contenido con
licencia dudosa.
"""


def generate(target_root: Path, repo_name: str) -> dict:
    campus = target_root / "campus"
    cursos_dir = campus / "cursos"
    cursos_dir.mkdir(parents=True, exist_ok=True)
    (campus / "capsulas").mkdir(exist_ok=True)
    report = {"repo": repo_name, "cursos": []}

    for slug in REPO_COURSES.get(repo_name, []):
        curso = content.CURSOS[slug]
        cdir = cursos_dir / slug
        (cdir).mkdir(parents=True, exist_ok=True)
        (cdir / "syllabus.md").write_text(_md_syllabus(curso),
                                          encoding="utf-8")
        for s in curso["semanas"]:
            (cdir / f"semana-{s['n']:02d}.md").write_text(
                _md_semana(curso, s), encoding="utf-8")
        (cdir / "quiz.json").write_text(
            json.dumps(curso["quiz"], ensure_ascii=False, indent=2),
            encoding="utf-8")
        (cdir / "recursos.md").write_text(_md_recursos(curso),
                                          encoding="utf-8")
        report["cursos"].append(
            {"slug": slug, "semanas": len(curso["semanas"]),
             "quiz_items": len(curso["quiz"])})

    # juegos educativos (solo donde aplican: PT/ES/CA)
    if repo_name in ("lingua-aberta", "ManosAbiertas"):
        juegos = campus / "juegos"
        juegos.mkdir(exist_ok=True)
        src_games = HERE / "games"
        if src_games.is_dir():
            for fname, *_ in content.GAMES:
                shutil.copy2(src_games / fname, juegos / fname)
        else:
            for fname, *_ in content.GAMES:
                (juegos / fname).write_text(
                    "# Juego generado por edu-forge\n"
                    "# Contenido completo disponible en el banco didactico.\n",
                    encoding="utf-8")
        report["juegos"] = [g[0] for g in content.GAMES]

    # voces: manifiesto de guiones por idioma (los audio los genera voice.py)
    (campus / "voces").mkdir(exist_ok=True)
    (campus / "voces" / "manifest.json").write_text(
        json.dumps({"idiomas": {k: {"voz": v[0], "guion": v[1]}
                                for k, v in VOICE_SCRIPTS.items()},
                    "nota": "audio generado por eduforge.voice (edge-tts "
                            "gratuito o Kokoro via Hugging Face)"},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    report["voces"] = sorted(VOICE_SCRIPTS)
    return report


def main() -> int:
    clones = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\Users\USER\AppData\Local\Temp\opencode\audit-deploys")
    results = []
    for repo in REPO_COURSES:
        root = clones / repo
        if (root / ".git").exists():
            r = generate(root, repo)
            results.append(r)
            cursos = ", ".join(c["slug"] for c in r["cursos"])
            print(f"[{repo}] cursos: {cursos}")
    out = Path(r"C:\Users\USER\belentani-unified\audit\edu-curriculum.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"[+] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
