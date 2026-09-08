#!/usr/bin/env python3
"""Escaneo rapido de secretos sobre los targets edu (usa keyrotor.redact)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\USER\keyrotor")
from keyrotor.redact import find_secrets  # noqa: E402

SKIP = {".git", "node_modules", ".next", "dist", "build", "__pycache__",
        ".venv", "venv", ".turbo", "unified_from"}
TEXT = {".py", ".md", ".html", ".toml", ".yml", ".yaml", ".json", ".txt",
        ".js", ".jsx", ".ts", ".tsx", ".css", ".env", ".mjs", ".sh"}


def scan(root: Path) -> dict:
    out = {}
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT:
            continue
        if any(d in SKIP for d in p.relative_to(root).parts[:-1]):
            continue
        if p.name in {".env.example"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        found = find_secrets(text)
        if found:
            kinds = {}
            for kind, _ in found:
                kinds[kind] = kinds.get(kind, 0) + 1
            out[str(p.relative_to(root))] = kinds
    return out


def main() -> int:
    roots = [Path(a) for a in sys.argv[1:]]
    bad = 0
    for root in roots:
        r = scan(root)
        total = sum(sum(v.values()) for v in r.values())
        if total:
            bad += 1
            print(f"[{root.name}] SECRETS: {total} en {len(r)} archivos")
            for f, k in sorted(r.items()):
                print(f"   {f}: {k}")
        else:
            print(f"[{root.name}] CLEAN")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
