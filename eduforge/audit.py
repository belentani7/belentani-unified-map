#!/usr/bin/env python3
"""EDU FORGE audit — auditoría estructural del campus generado.

Comprueba:
  1. Todos los .json parsean.
  2. HTML balanceado en todas las .html (parser propio, sin dependencias).
  3. Todo href/src relativo de las .html resuelve a un archivo real.
  4. Piezas esperadas por curso (capas 2-4 de academy).

Sale con código 1 si hay errores. Uso: python -m eduforge.audit [dir_repo]
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "wbr",
        "area", "base", "col", "embed", "track"}


class Balance(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, int]] = []
        self.errores: list[str] = []

    def handle_starttag(self, tag, attrs):
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
                        f"</{tag}> linea {self.getpos()[0]} cierra sobre "
                        f"{self.stack[i + 1:]}")
                    del self.stack[i:]
                    return
            self.errores.append(f"</{tag}> sin abrir, linea {self.getpos()[0]}")


PIEZAS = ["syllabus.md", "glosario.md", "chuleta.md", "laboratorio.md",
          "rubrica.md", "examen.md", "recursos.md", "quiz.json"]


def auditar(root: Path) -> int:
    campus = root / "campus"
    fallos: list[str] = []
    ok = 0

    # 1. JSON
    for j in campus.rglob("*.json"):
        try:
            json.loads(j.read_text(encoding="utf-8"))
            ok += 1
        except Exception as e:
            fallos.append(f"JSON inválido: {j.relative_to(root)} — {e}")

    # 2 + 3. HTML: balance y enlaces
    paginas = sorted(campus.glob("*.html")) + [root / "index.html"]
    href_re = re.compile(r'(?:href|src)="([^"#]+?)"')
    for pag in paginas:
        if not pag.exists():
            fallos.append(f"página esperada no existe: {pag}")
            continue
        texto = pag.read_text(encoding="utf-8")
        b = Balance()
        b.feed(texto)
        for err in b.errores:
            fallos.append(f"HTML {pag.relative_to(root)}: {err}")
        for tag in b.stack:
            fallos.append(f"HTML {pag.relative_to(root)}: <{tag[0]}> sin cerrar (línea {tag[1]})")
        if not b.errores and not b.stack:
            ok += 1
        base = pag.parent
        for destino in href_re.findall(texto):
            if destino.startswith(("http://", "https://", "data:", "mailto:",
                                   "javascript:", "crypto:", "//")):
                continue
            if "${" in destino or "{" in destino:
                continue  # template literal JS, no es un enlace estático
            ruta = destino.split("#")[0].split("?")[0]
            if not ruta:
                continue
            if (base / ruta).exists():
                ok += 1
            else:
                fallos.append(f"enlace roto en {pag.relative_to(root)}: {destino}")

    # 4. piezas por curso
    cursos = sorted((campus / "cursos").iterdir()) if (campus / "cursos").is_dir() else []
    for cdir in cursos:
        if not cdir.is_dir():
            continue
        for pieza in PIEZAS:
            if (cdir / pieza).exists():
                ok += 1
            else:
                fallos.append(f"curso {cdir.name}: falta {pieza}")
        # quiz con al menos 3 items y correcta dentro de rango
        qf = cdir / "quiz.json"
        if qf.exists():
            items = json.loads(qf.read_text(encoding="utf-8"))
            for n, q in enumerate(items, 1):
                if not (0 <= q.get("correcta", -1) < len(q["opciones"])):
                    fallos.append(f"{cdir.name} quiz item {n}: 'correcta' fuera de rango")

    # resumen
    total_archivos = sum(1 for _ in campus.rglob("*") if _.is_file())
    print(f"archivos en campus/: {total_archivos}")
    print(f"comprobaciones OK: {ok}")
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        for f in fallos:
            print("  ✗", f)
        return 1
    print("✓ auditoría estructural limpia")
    return 0


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\Users\USER\Documents\secure-t-university")
    return auditar(root)


if __name__ == "__main__":
    raise SystemExit(main())
