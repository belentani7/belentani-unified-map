#!/usr/bin/env python3
"""EDU FORGE — orquestador: curriculum + frontend + voz + agente + push.

Por cada repo target (edu):
  1. campus/ con cursos (curriculum.py)
  2. campus frontend premium (frontend.py)
  3. agente tutor vivo en GitHub (agent.py + workflow)
  4. voces por idioma (voice.py, si hay red)
  5. commit + push con email proton

Uso: python -m eduforge.cli [dir_clones] [--skip-voice] [--skip-push]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eduforge import curriculum, frontend, voice  # noqa: E402
from eduforge.agent import main as agent_main  # noqa: E402

HERE = Path(__file__).resolve().parent
REPOS = ["ManosAbiertas", "lingua-aberta", "ux-academy-professional-program",
         "linguaforge", "open-school"]

WORKFLOW = """name: tutor-ia

on:
  schedule:
    - cron: "0 8 * * *"
  issues:
    types: [opened]
  workflow_dispatch:

permissions:
  contents: write
  issues: write

jobs:
  capsula:
    runs-on: ubuntu-latest
    if: github.event_name != 'issues'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Capsula didactica del dia
        run: python campus/agente/tutor.py capsula

  tutor:
    runs-on: ubuntu-latest
    if: github.event_name == 'issues' && github.event.action == 'opened'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Responder si tiene la etiqueta tutor
        env:
          ETIQUETAS: ${{ toJSON(github.event.issue.labels) }}
        run: |
          echo "$ETIQUETAS" | grep -qi "tutor" && python campus/agente/tutor.py issue || echo "sin etiqueta tutor"
"""


def install_agent(root: Path) -> None:
    ag = root / "campus" / "agente"
    ag.mkdir(parents=True, exist_ok=True)
    (ag / "tutor.py").write_text(
        (HERE / "agent.py").read_text(encoding="utf-8"), encoding="utf-8")
    wf = root / ".github" / "workflows" / "tutor-ia.yml"
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text(WORKFLOW, encoding="utf-8")


def push(root: Path, repo: str) -> tuple[str, bool]:
    r = subprocess.run(["git", "-C", str(root), "add", "-A"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return f"git add fallo: {r.stderr[:200]}", False
    r = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                       capture_output=True, text=True)
    if not r.stdout.strip():
        return "sin cambios", True
    subprocess.run(["git", "-C", str(root), "config", "user.name",
                    "Belentani"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email",
                    "belentani7studio@proton.me"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-m",
                    "edu-forge: unificacion + campus Harvard/Coursera + "
                    "voz IA + agente tutor GitHub"], check=True)
    subprocess.run(["git", "-C", str(root), "push"], check=True)
    r = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip()[:7], True


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    clones = Path(args[0]) if args else Path(
        r"C:\Users\USER\AppData\Local\Temp\opencode\audit-deploys")
    skip_voice = "--skip-voice" in sys.argv
    skip_push = "--skip-push" in sys.argv

    results = {}
    for repo in REPOS:
        root = clones / repo
        if not (root / ".git").exists():
            continue
        print(f"\n=== {repo} ===")
        curriculum.generate(root, repo)
        print("  curriculum OK")
        frontend.generate(root, repo)
        print("  frontend OK")
        install_agent(root)
        print("  agente tutor OK")
        if not skip_voice:
            try:
                voice.main()
            except Exception as e:
                print(f"  voz: fallo ({e})")
        if skip_push:
            results[repo] = {"push": "skipped"}
            continue
        head, ok = push(root, repo)
        results[repo] = {"push": head if ok else "FAIL", "ok": ok}
        print(f"  push: {head} {'OK' if ok else 'FALLO'}")
    out = Path(r"C:\Users\USER\belentani-unified\audit\edu-forge-run.json")
    import json
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n[+] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
