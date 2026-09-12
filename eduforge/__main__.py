#!/usr/bin/env python3
"""EDU FORGE — CLI del motor.

    python -m eduforge build  [repo_dir]   # curriculum + academy + frontend
    python -m eduforge curriculum [repo_dir]
    python -m eduforge academy [repo_dir]
    python -m eduforge frontend [repo_dir]
    python -m eduforge voice [repos_root]
    python -m eduforge audit [repo_dir]
    python -m eduforge all [repo_dir]      # build + tests + audit

Sin argumentos de ruta usa el repo por defecto (secure-t-university local).
Los generadores son deterministas e idempotentes: regenerar no rompe nada.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DEFAULT_REPO = Path(r"C:\Users\USER\Documents\secure-t-university")


def _repo(argv: list[str]) -> Path:
    for a in argv:
        if not a.startswith("-") and a not in COMANDOS:
            return Path(a).resolve()
    return DEFAULT_REPO


def cmd_build(repo: Path) -> int:
    from eduforge import academy, curriculum, frontend
    nombre = repo.name
    curriculum.generate(repo, nombre)
    print("[build] curriculum OK")
    rep = academy.generate(repo, nombre)
    print(f"[build] academy OK ({len(rep['cursos'])} cursos, "
          f"{len(rep['global'])} piezas globales, indice {rep['indice']})")
    frontend.generate(repo, nombre)
    print("[build] frontend OK")
    return 0


def cmd_audit(repo: Path) -> int:
    from eduforge import audit
    return audit.auditar(repo)


def cmd_tests(_repo: Path) -> int:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"],
                       cwd=DEFAULT_REPO, capture_output=True, text=True)
    print(r.stdout[-2000:])
    if r.returncode != 0:
        print(r.stderr[-1000:])
    return r.returncode


COMANDOS = {
    "curriculum": lambda repo: (_import_run("curriculum", repo), 0)[1],
    "academy": lambda repo: (_import_run("academy", repo), 0)[1],
    "frontend": lambda repo: (_import_run("frontend", repo), 0)[1],
    "voice": lambda repo: _run_voice(repo),
    "build": cmd_build,
    "audit": cmd_audit,
    "tests": cmd_tests,
    "all": lambda repo: _max(cmd_build(repo), cmd_tests(repo), cmd_audit(repo)),
}


def _max(*codes: int) -> int:
    return max(codes)


def _import_run(modulo: str, repo: Path) -> None:
    from eduforge import academy, curriculum, frontend
    nombre = repo.name
    if modulo == "curriculum":
        curriculum.generate(repo, nombre)
    elif modulo == "academy":
        academy.generate(repo, nombre)
    else:
        frontend.generate(repo, nombre)
    print(f"[{modulo}] OK")


def _run_voice(repos_root: Path) -> int:
    from eduforge import voice
    return voice.main() if len(sys.argv) < 3 else voice.main()


def main() -> int:
    args = [a for a in sys.argv[1:]]
    cmd = next((a for a in args if a in COMANDOS), "build")
    if "--help" in args or cmd not in COMANDOS:
        print(__doc__)
        return 0 if "--help" in args else 2
    repo = _repo(args)
    if not repo.exists():
        print(f"repo no encontrado: {repo}")
        return 2
    return COMANDOS[cmd](repo)


if __name__ == "__main__":
    raise SystemExit(main())
