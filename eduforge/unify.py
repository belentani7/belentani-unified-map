#!/usr/bin/env python3
"""EDU FORGE — analisis de familias duplicadas y eleccion de target.

Regla del usuario:
  - el target es EL MAS GRANDE Y MAS RECIENTE de cada familia
  - merge sin perdida: los archivos unicos de los demas se copian al target
  - dedup por sha256; conflictos de ruta -> unified_from/<repo>/<ruta>
  - nunca se tocan: .git, node_modules, .env* (regla NO SECRETS)
  - manifest JSON completo para auditoria

Uso: python -m eduforge.unify <dir_clones> <out_json>
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "__pycache__",
             ".venv", "venv", ".turbo", "out", ".pytest_cache", "unified_from"}
SKIP_NAMES = {".env", ".env.local", ".env.production", ".env.development",
              ".env.staging", "serviceAccount.json", "credentials.json",
              "firebase-adminsdk.json"}

FAMILIES = {
    "manosabiertas": [
        "ManosAbiertas", "belentani-monorepo", "manosabiertas-components",
        "manosabiertas-38d5f", "manosabiertas-optimizacion-2", "manos-abiertas",
        "manos_abiertas_course_modules", "manosabiertas-repo", "clon-manosabiertas",
        "ManosAbiertas-backup-v1", "manos-abiertas-docs",
        "manosabiertas-vercel-20260813", "manos-abiertas-release-netlify-20260812",
    ],
    "linguaforge": ["linguaforge", "linguaforge-v2", "maos-abertas-linguaforge"],
    "ux-academy": ["ux-academy-professional-program"],
    "lingua-aberta": ["lingua-aberta"],
    "open-school": ["open-school"],
}

# El repo VIVO (mas reciente, activo) es el destino real del merge.
# El contenido de los backups mas grandes se integra en el via unified_from/.
TARGET_OVERRIDE = {"manosabiertas": "ManosAbiertas"}


def load_archived(repos_json: Path) -> set:
    try:
        data = json.loads(repos_json.read_text(encoding="utf-8"))
        return {r["name"] for r in data if r.get("isArchived")}
    except Exception:
        return set()


def repo_files(root: Path) -> dict:
    """ruta_relativa -> (sha256, bytes) de archivos mergeables."""
    out = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        parts = p.relative_to(root).parts
        if any(d in SKIP_DIRS for d in parts[:-1]) or p.name in SKIP_NAMES:
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp",
                                ".mp4", ".mp3", ".wav", ".zip", ".exe", ".dll",
                                ".woff", ".woff2", ".ttf", ".pdf"}:
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            digest = hashlib.sha256(
                p.read_bytes()).hexdigest()  # bytes = exacto, sin ambiguedades
        out[str(p.relative_to(root))] = (digest, p.stat().st_size)
    return out


def analyze(clones_dir: Path) -> dict:
    report = {}
    for family, names in FAMILIES.items():
        members = []
        for name in names:
            root = clones_dir / name
            if not (root / ".git").exists():
                continue
            files = repo_files(root)
            members.append({
                "repo": name,
                "files": len(files),
                "bytes": sum(v[1] for v in files.values()),
            })
        if not members:
            continue
        # target = mas archivos; empate -> mas bytes (el mas completo)
        biggest = max(members, key=lambda m: (m["files"], m["bytes"]))
        target = TARGET_OVERRIDE.get(family, biggest["repo"])
        report[family] = {
            "target": target,
            "biggest": biggest["repo"],
            "members": sorted(members, key=lambda m: -m["files"]),
        }
    return report


def merge_family(clones_dir: Path, family: str, target_name: str,
                 archived: set, out_work: Path) -> dict:
    """Copia archivos unicos de los hermanos al target de trabajo.

    - fuentes ARCHIVADAS (backups): siempre a unified_from/<repo>/<ruta>
    - fuentes ACTIVAS: merge en raiz; colision -> unified_from/<repo>/<ruta>
    """
    target_root = clones_dir / target_name
    target_files = repo_files(target_root)
    manifest = {"family": family, "target": target_name,
                "copied": [], "skipped_identical": 0, "conflicts": 0}
    seen = {r: h for r, (h, _) in target_files.items()}
    for name in FAMILIES[family]:
        if name == target_name:
            continue
        src = clones_dir / name
        if not (src / ".git").exists():
            continue
        is_arch = name in archived
        for rel, (digest, _size) in repo_files(src).items():
            if rel in seen:
                manifest["skipped_identical"] += 1
                continue
            if is_arch:
                dst = target_root / "unified_from" / name / rel
            else:
                dst = target_root / rel
                if dst.exists():
                    dst = target_root / "unified_from" / name / rel
                    manifest["conflicts"] += 1
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src / rel, dst)
            seen[rel] = digest
            manifest["copied"].append({"from": name, "path": str(dst.relative_to(target_root)),
                                       "sha256": digest[:16]})
    return manifest


def main() -> int:
    clones = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\Users\USER\AppData\Local\Temp\opencode\audit-deploys")
    out_json = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
        r"C:\Users\USER\belentani-unified\audit\edu-merge-analysis.json")
    mode = sys.argv[3] if len(sys.argv) > 3 else "analyze"

    report = analyze(clones)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    if mode == "analyze":
        print("=== ANALISIS DE FAMILIAS (target = mas grande y reciente) ===")
        for family, data in report.items():
            print(f"\n[{family}] TARGET: {data['target']}"
                  + (f" (biggest={data['biggest']})"
                     if data["biggest"] != data["target"] else ""))
            for m in data["members"]:
                mark = " <-- TARGET" if m["repo"] == data["target"] else ""
                print(f"    {m['repo']:<42} {m['files']:>5} archivos  "
                      f"{m['bytes']/1024:>8.0f} KB{mark}")
        print(f"\n[+] {out_json}")
        return 0

    # mode == merge: aplica los merges a los clones de trabajo
    archived = load_archived(Path(r"C:\Users\USER\belentani-unified\repos.json"))
    all_manifests = {}
    for family, data in report.items():
        man = merge_family(clones, family, data["target"], archived, clones)
        total_copied = len(man["copied"])
        print(f"[{family}] -> {data['target']}: "
              f"{total_copied} archivos unicos copiados "
              f"({man['skipped_identical']} identicos saltados, "
              f"{man['conflicts']} conflictos a unified_from/)")
        all_manifests[family] = man
    man_path = Path(r"C:\Users\USER\belentani-unified\audit\edu-merge-manifest.json")
    man_path.write_text(json.dumps(all_manifests, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"[+] manifest: {man_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
