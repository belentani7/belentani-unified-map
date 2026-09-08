"""Maximum-scope audit of the deployed ecosystem.

For every repo clone under the audit dir:
  1. detect deploy configs (vercel.json, netlify.toml, wrangler.toml, workflows)
  2. detect committed .env / secret files (danger signal)
  3. extract project names, domains, URLs
  4. run the keyrotor secret scanner on every text file

Outputs: audit-results.json + audit-report.md (no secret VALUES ever written).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\USER\keyrotor")
from keyrotor.redact import find_secrets  # noqa: E402

AUDIT_DIR = Path(r"C:\Users\USER\AppData\Local\Temp\opencode\audit-deploys")
OUT_DIR = Path(r"C:\Users\USER\belentani-unified\audit")

DEPLOY_CONFIGS = [
    "vercel.json", "netlify.toml", "wrangler.toml", "wrangler.jsonc",
    "cloudflare.toml", "_redirects", "_headers", "firebase.json",
    "fly.toml", "render.yaml", "railway.json",
]
SECRET_FILENAMES = {".env", ".env.local", ".env.production", ".env.development",
                    ".env.staging", ".env.example", "serviceAccount.json",
                    "credentials.json", "firebase-adminsdk.json", "secrets.json"}
TEXT_SUFFIXES = {".py", ".md", ".html", ".toml", ".yml", ".yaml", ".json",
                 ".txt", ".ini", ".cfg", ".js", ".jsx", ".ts", ".tsx",
                 ".env", ".mjs", ".cjs", ".css", ".sh", ".ps1"}
URL_RE = re.compile(r"https?://[a-zA-Z0-9.\-]+(?:\.vercel\.app|\.netlify\.app"
                    r"|\.pages\.dev|\.workers\.dev|\.web\.app|\.fly\.dev"
                    r"|\.onrender\.com|\.trycloudflare\.com|vercel\.com|"
                    r"netlify\.com|cloudflare\.com)[a-zA-Z0-9/.\-]*")
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "__pycache__",
             ".venv", "venv", ".turbo", "out", ".pytest_cache"}


def walk_text_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts[:-1]):
            continue
        yield p


def audit_repo(repo_dir: Path) -> dict:
    name = repo_dir.name
    res = {
        "repo": name,
        "deploy_configs": [],
        "workflows": [],
        "committed_env_files": [],
        "urls": [],
        "secret_files": {},
        "framework_hints": set(),
    }

    # package.json framework hints
    pkg = repo_dir / "package.json"
    if pkg.is_file():
        try:
            pj = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
            deps = {**(pj.get("dependencies") or {}), **(pj.get("devDependencies") or {})}
            for hint in ("next", "react", "turbo", "astro", "vite", "remix",
                         "nuxt", "svelte", "vue", "wrangler", "@vercel"):
                if hint in deps:
                    res["framework_hints"].add(hint)
        except Exception:
            pass

    for cfg in DEPLOY_CONFIGS:
        p = repo_dir / cfg
        if p.is_file():
            res["deploy_configs"].append(cfg)
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                for m in URL_RE.finditer(text):
                    res["urls"].append(m.group(0))
                if cfg == "wrangler.toml" or cfg == "cloudflare.toml":
                    m = re.search(r'name\s*=\s*"([^"]+)"', text)
                    if m:
                        res["urls"].append(f"cf-project:{m.group(1)}")
                if cfg == "netlify.toml":
                    for m in re.finditer(r'(?:site|name)\s*=\s*"([^"]+)"', text):
                        res["urls"].append(f"netlify-site:{m.group(1)}")
            except Exception:
                pass

    wf_dir = repo_dir / ".github" / "workflows"
    if wf_dir.is_dir():
        for wf in sorted(wf_dir.glob("*.yml")):
            res["workflows"].append(wf.name)
            try:
                text = wf.read_text(encoding="utf-8", errors="ignore")
                for m in URL_RE.finditer(text):
                    res["urls"].append(m.group(0))
                if "vercel" in text.lower():
                    res["deploy_configs"].append("ci:vercel-action")
                if "netlify" in text.lower():
                    res["deploy_configs"].append("ci:netlify-action")
                if "cloudflare" in text.lower() or "wrangler" in text.lower():
                    res["deploy_configs"].append("ci:cloudflare-action")
            except Exception:
                pass

    # committed env/secret files
    for p in repo_dir.rglob(".env*"):
        if p.is_file() and ".git" not in p.parts:
            res["committed_env_files"].append(str(p.relative_to(repo_dir)))
    for p in repo_dir.rglob("*"):
        if p.is_file() and p.name.lower() in SECRET_FILENAMES:
            rel = str(p.relative_to(repo_dir))
            if rel not in res["committed_env_files"]:
                res["committed_env_files"].append(rel)

    # secret scan
    for p in walk_text_files(repo_dir):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        found = find_secrets(text)
        if found:
            kinds: dict = {}
            for kind, _ in found:
                kinds[kind] = kinds.get(kind, 0) + 1
            res["secret_files"][str(p.relative_to(repo_dir))] = kinds

    # URLs in README
    for readme in (repo_dir / "README.md", repo_dir / "readme.md"):
        if readme.is_file():
            try:
                text = readme.read_text(encoding="utf-8", errors="ignore")
                for m in URL_RE.finditer(text):
                    res["urls"].append(m.group(0))
            except Exception:
                pass

    res["urls"] = sorted(set(res["urls"]))
    res["framework_hints"] = sorted(res["framework_hints"])
    return res


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for repo_dir in sorted(AUDIT_DIR.iterdir()):
        if repo_dir.is_dir() and (repo_dir / ".git").exists():
            results.append(audit_repo(repo_dir))

    (OUT_DIR / "audit-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# AUDITORIA MAXIMA — REPOS DESPLEGADOS (Vercel / Cloudflare / Netlify)",
        "",
        f"- Fecha: 2026-09-08",
        f"- Repos auditados: {len(results)}",
        f"- Regla: cero valores secretos reproducidos en este informe",
        "",
    ]
    for r in results:
        secret_total = sum(sum(v.values()) for v in r["secret_files"].values())
        status = "SECRETS!" if (secret_total or r["committed_env_files"]) else "clean"
        lines += [
            f"## {r['repo']} — {status}",
            "",
            f"- Deploy configs: {', '.join(r['deploy_configs']) or 'ninguno'}",
            f"- Workflows CI: {', '.join(r['workflows']) or 'ninguno'}",
            f"- Framework hints: {', '.join(r['framework_hints']) or 'n/a'}",
            f"- URLs detectadas: {', '.join(r['urls']) or 'ninguna'}",
            f"- .env commiteados: {len(r['committed_env_files'])}",
        ]
        for f in r["committed_env_files"]:
            lines.append(f"  - ALERTA env: `{f}`")
        if r["secret_files"]:
            lines.append(f"- Secret-like matches: {secret_total} en {len(r['secret_files'])} archivos")
            for f, kinds in sorted(r["secret_files"].items()):
                detail = ", ".join(f"{k}x{n}" for k, n in sorted(kinds.items()))
                lines.append(f"  - `{f}`: {detail}")
        lines.append("")

    (OUT_DIR / "audit-report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[+] {len(results)} repos auditados")
    print(f"[+] json: {OUT_DIR / 'audit-results.json'}")
    print(f"[+] md:   {OUT_DIR / 'audit-report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
