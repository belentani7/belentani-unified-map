"""Tests de comportamiento del motor eduforge.

Ejecutar desde belentani-unified:  python -m pytest tests/ -q
"""
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from eduforge import academy, audit, content  # noqa: E402


def _hash_dir(d: Path) -> dict[str, str]:
    out = {}
    for f in sorted(d.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            out[str(f.relative_to(d))] = hashlib.sha256(
                f.read_bytes()).hexdigest()[:12]
    return out


def test_md2html_renderiza_estructuras():
    md = ('# Titulo\n\n- uno **negrita**\n- dos `codigo`\n\n'
          '| A | B |\n|---|---|\n| 1 | 2 |\n\n> cita\n')
    html = academy._md2html(md)
    assert "<h1>" in html
    assert "<li>" in html and "<strong>" in html and "<code>" in html
    assert "<table>" in html and "<th>" in html and "<td>" in html
    assert "<blockquote>" in html


def test_md2html_convierte_enlaces():
    html = academy._md2html("ver [recursos](recursos.md) ya")
    assert '<a href="recursos.md">recursos</a>' in html


def test_quiz_data_coherente():
    """Todo curso registrado tiene quiz válido contra content.CURSOS."""
    for slug, c in content.CURSOS.items():
        for q in c["quiz"]:
            assert 0 <= q["correcta"] < len(q["opciones"]), f"{slug}: correcta rota"
        assert len(c["objetivos"]) >= 3, f"{slug}: outcomes insuficientes"


def test_generacion_determinista(tmp_path):
    """Dos builds del mismo repo producen bytes idénticos."""
    resultados = []
    for i in (1, 2):
        destino = tmp_path / f"repo{i}"
        destino.mkdir()
        academy.generate(destino, "secure-t-university")
        resultados.append(_hash_dir(destino))
    assert resultados[0] == resultados[1], "la generación no es determinista"


def test_audit_caza_enlace_roto(tmp_path):
    """El auditor debe fallar (exit 1) ante un enlace roto real."""
    campus = tmp_path / "campus"
    (campus / "cursos" / "x").mkdir(parents=True)
    (campus / "index.html").write_text(
        '<a href="no-existe.html">roto</a>', encoding="utf-8")
    (campus / "no-existe-ref").mkdir()
    codigo = audit.auditar(tmp_path)
    assert codigo == 1, "audit no detectó el enlace roto"


def test_audit_caza_secreto(tmp_path):
    campus = tmp_path / "campus"
    campus.mkdir()
    (tmp_path / "mal.js").write_text('const t = "ghp_' + "A" * 36 + '";',
                                     encoding="utf-8")
    codigo = audit.auditar(tmp_path)
    assert codigo == 1, "audit no detectó el secreto"
