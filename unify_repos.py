"""Unify 500+ GitHub repos into logical families.

The Belentani GitHub account holds ~511 repositories that are really
pieces of a much smaller set of logical projects. This script:

1. Normalizes repo names (case, separators, noise words).
2. Detects evolution markers: v1/v2/v3, -backup, -final, -old,
   -copy, (1), -audited, -fix, .tar leftovers, etc.
3. Groups repos into FAMILIES by shared semantic root
   (prefix, acronym, brand, or strong token overlap).
4. Marks near-duplicates inside each family (difflib ratio).
5. Emits three artifacts: JSON map, Markdown map, ASCII tree.

Stdlib only. Idempotent. Read-only (never touches the repos).

Usage:
    python unify_repos.py [repos.json] [out_dir]
"""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_IN = HERE / "repos.json"
DEFAULT_OUT = HERE / "unified"

# ----------------------------------------------------------------------
# 1. Name normalization
# ----------------------------------------------------------------------

_EVOLUTION_RE = re.compile(
    r"[ _\-.]*(v\d+(\.\d+)*|backup|back|-back|final|finale|definitivo|"
    r"old|viejo|new|nuevo|copy|copia|audited|auditado|fixed|fix|test|tmp|temp|"
    r"pro|premium|ultra|plus|full|pack|lite|mini|latest|wip|draft|archived|"
    r"deprecated|obsoleto|legacy|experimental|omega|alpha|beta|rc\d*|"
    r"\(\d+\)|\d{4}[\-_]\d{2}[\-_]\d{2}|[\-_]\d+)$",
    re.IGNORECASE,
)

_BRAND_RE = re.compile(
    r"^(belentani|duck|judas|aion|nexus|noiacore|noia|lingua|secure|"
    r"omega|manos|arte|oculus|marinho|forge|claude|qwen|comfy|"
    r"voice|libro|mistral|codex|hermes|open|terra|zion|aether)",
    re.IGNORECASE,
)


def normalize(name: str) -> str:
    """belentani-Omega-v2-FINAL -> belentani-omega"""
    s = name.lower()
    s = s.replace(".tar", "").replace(".zip", "")
    s = re.sub(r"[\s\.]+", "-", s)
    s = _EVOLUTION_RE.sub("", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or name.lower()


def brand_of(normalized: str) -> str:
    m = _BRAND_RE.match(normalized)
    return m.group(1) if m else ""


# ----------------------------------------------------------------------
# 2. Family extraction
# ----------------------------------------------------------------------

# Strong family signals: brand + optional discriminator token
_DISCRIMINATORS = [
    "omega", "experience", "studio", "core", "web", "cv", "profile",
    "mono", "monograph", "fullstack", "unified", "agency", "os",
    "toolkit", "skills", "skill", "pack", "agent", "agents", "compliance",
    "workforce", "enterprise", "ecosystem", "inspect", "lab", "labs",
    "store", "landing", "mobile", "escape", "campaign", "university",
    "forge", "avatar", "dashboard", "api", "generator", "optimizer",
    "bench", "validator", "detector", "compass", "atlas", "voice",
    "bot", "saas", "research", "investigacion", "libro", "book",
    "inventory", "register", "registro", "map", "maps", "doc", "docs",
]

_SKIP_TOKENS = {"the", "de", "del", "la", "el", "y", "and", "or", "in", "of"}


def family_of(name: str, normalized: str) -> tuple[str, str]:
    """Return (family, kind) from a repo name."""
    brand = brand_of(normalized)
    tokens = [t for t in normalized.split("-") if t and t not in _SKIP_TOKENS]

    if brand:
        rest = [t for t in tokens if t != brand]
        disc = next((t for t in rest if t in _DISCRIMINATORS), "")
        if disc:
            return f"{brand}-{disc}", "branded"
        # second token acts as discriminator if short
        if rest and len(rest[0]) <= 12:
            return f"{brand}-{rest[0]}", "branded"
        return brand, "branded"

    # no known brand: use first meaningful token (or full normalized)
    if tokens:
        return tokens[0], "token"
    return normalized or "unnamed", "token"


# ----------------------------------------------------------------------
# 3. Top-level domains (the REAL logical projects)
# ----------------------------------------------------------------------

_DOMAIN_RULES: list[tuple[str, re.Pattern]] = [
    ("DUCK-ECOSYSTEM", re.compile(r"^(duck|heyduck|zion|aether)", re.I)),
    ("JUDAS-ERA", re.compile(r"^(judas|monos)", re.I)),
    ("SKILLS-INFRA", re.compile(
        r"^(claude-?skills|meta-?skill|mimocode|mimo|dev-toolkit|safe-exec|"
        r"forja|proofmesh|caveman|skill|manus-ai-skill|superpowers)", re.I)),
    ("AION-WORKFORCE", re.compile(
        r"^(aion|nexus|workforce|agent|agentmail|omniagent|local-agent|"
        r"open-manus|belentani-centro-manus|ai-agent)", re.I)),
    ("VOICE-AI", re.compile(r"^(voice|tts|speech|beep)", re.I)),
    ("AI-COMPUTE", re.compile(
        r"^(qwen|comfyui|gpu|latent|pbr|temporal|oss-compass|"
        r"decision-atlas|failure|llm|vfx|deepseek|codex|hermes|"
        r"mistral|openclaw|opencode|kilo|kling|wan|flux|omniroute|music)", re.I)),
    ("BOOKS-DOCS", re.compile(
        r"^(libro|research|investigacion|doc|docs|registro|inventario|"
        r"ecosystem|map)", re.I)),
    ("FORGE-OPS", re.compile(r"^(forge|toolkit|reports|studio-os)", re.I)),
    ("PRODUCTS", re.compile(
        r"^(manos|lingua|secure|oculus|arte|cruzando|natalia|carquidec|"
        r"open-school|aion-|firefly|dance|judas-|pedro|rh-|pvc|ctg|guia|"
        r"tender|steven|aurea|bellacore|lios|universal|music-os)", re.I)),
    ("BELENTANI-CORE", re.compile(r"^(belentani|omega|noiacore|noia)", re.I)),
]


def domain_of(name: str, family: str) -> str:
    for domain, pattern in _DOMAIN_RULES:
        if pattern.match(name):
            return domain
    return "EXPERIMENTS"


# ----------------------------------------------------------------------
# 4. Clustering + duplicate detection
# ----------------------------------------------------------------------


def build_map(repos: list[dict]) -> dict:
    families: "OrderedDict[str, dict]" = OrderedDict()
    orphans: list[dict] = []

    for repo in repos:
        name = repo.get("name", "")
        norm = normalize(name)
        fam, kind = family_of(name, norm)
        if kind == "token" and not fam or fam == "unnamed":
            orphans.append({**repo, "_normalized": norm})
            continue
        entry = families.setdefault(
            fam,
            {
                "family": fam,
                "domain": domain_of(name, fam),
                "members": [],
                "archived": 0,
                "private": 0,
                "total_pushes": 0,
                "languages": set(),
            },
        )
        entry["members"].append(
            {
                "name": name,
                "normalized": norm,
                "visibility": repo.get("visibility", "?"),
                "archived": bool(repo.get("isArchived", False)),
                "pushedAt": repo.get("pushedAt", ""),
                "language": (
                    repo["primaryLanguage"].get("name", "")
                    if isinstance(repo.get("primaryLanguage"), dict)
                    else ""
                ),
                "description": (repo.get("description") or "")[:140],
                "duplicate_of": None,
            }
        )
        if repo.get("isArchived"):
            entry["archived"] += 1
        if repo.get("visibility", "").upper() == "PRIVATE":
            entry["private"] += 1
        lang = (
            repo["primaryLanguage"].get("name")
            if isinstance(repo.get("primaryLanguage"), dict)
            else ""
        )
        if lang:
            entry["languages"].add(lang)

    # near-duplicate detection inside each family:
    # compare every pair, then resolve each marked member to the cluster
    # representative (lowest-index unmarked member)
    for fam in families.values():
        members = fam["members"]
        pairs = [
            (i, j, SequenceMatcher(None, members[i]["normalized"],
                                   members[j]["normalized"]).ratio())
            for i in range(len(members))
            for j in range(i + 1, len(members))
        ]
        marked: set = set()
        for i, j, ratio in pairs:
            if ratio >= 0.85:
                # prefer marking the later member; always point to the
                # lowest-index member that is not itself marked
                anchor = i if i not in marked else next(
                    (k for k in range(i + 1) if k not in marked), i
                )
                marked.add(j)
                members[j]["duplicate_of"] = members[anchor]["name"]

    return {
        "families": {k: v for k, v in families.items()},
        "orphans": orphans,
    }


# ----------------------------------------------------------------------
# 4. Reporting
# ----------------------------------------------------------------------


def _serialize(entry: dict) -> dict:
    out = dict(entry)
    out["languages"] = sorted(entry["languages"])
    return out


def write_outputs(data: dict, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    families = data["families"]
    orphans = data["orphans"]

    # group families by domain
    domains: "OrderedDict[str, list[tuple[str, dict]]]" = OrderedDict()
    for fam, entry in families.items():
        domains.setdefault(entry["domain"], []).append((fam, entry))
    for fam, entries in domains.items():
        entries.sort(key=lambda kv: (-len(kv[1]["members"]), kv[0]))
    if orphans:
        domains.setdefault("EXPERIMENTS", [])

    total = sum(len(f["members"]) for f in families.values())

    # ---- JSON ----
    json_path = out_dir / "REPO_UNIFICATION_MAP.json"
    json_path.write_text(
        json.dumps(
            {
                "generated": "2026-09-08",
                "tool": "unify_repos.py",
                "total_repos": total + len(orphans),
                "total_families": len(families),
                "total_domains": len(domains),
                "domains": [
                    {
                        "domain": dom,
                        "families": [
                            {"family": k, **_serialize(v)} for k, v in entries
                        ],
                    }
                    for dom, entries in domains.items()
                ],
                "orphans": orphans,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # ---- Markdown ----
    md_lines = [
        "# REPO UNIFICATION MAP — 500 piezas, N proyectos",
        "",
        f"Generado: 2026-09-08 · Repos analizados: **{total + len(orphans)}** · "
        f"Dominios lógicos: **{len(domains)}** · Familias: **{len(families)}** · "
        f"Huérfanos: {len(orphans)}",
        "",
        "| # | Dominio | Repos | Familias | Privados |",
        "|---|---------|-------|----------|----------|",
    ]
    for i, (dom, entries) in enumerate(domains.items(), 1):
        n = sum(len(e["members"]) for _, e in entries) + (
            len(orphans) if dom == "EXPERIMENTS" and orphans else 0
        )
        priv = sum(e["private"] for _, e in entries)
        md_lines.append(
            f"| {i} | **{dom}** | {n} | {len(entries)} | {priv} |"
        )
    md_lines += ["", "---", ""]

    for dom, entries in domains.items():
        md_lines.append(f"## {dom}")
        md_lines.append("")
        for fam, entry in entries:
            md_lines.append(f"### `{fam}` ({len(entry['members'])} repos)")
            for m in entry["members"]:
                dup = f" → **DUP de** `{m['duplicate_of']}`" if m["duplicate_of"] else ""
                arc = " 📦" if m["archived"] else ""
                vis = "PRIV" if m["visibility"].upper() == "PRIVATE" else "pub"
                md_lines.append(f"- `{m['name']}` [{vis}{arc}]{dup}")
            md_lines.append("")
        if dom == "EXPERIMENTS" and orphans:
            md_lines.append("### Huérfanos")
            for o in orphans:
                md_lines.append(f"- `{o['name']}`")
            md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    md_path = out_dir / "REPO_UNIFICATION_MAP.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # ---- ASCII tree ----
    tree = [
        "BELENTANI GITHUB — UNIFIED VIEW (por logica, no por nombre)",
        f"{total + len(orphans)} repos -> {len(domains)} dominios -> {len(families)} familias",
        "",
    ]
    dom_names = list(domains.keys())
    for di, dom in enumerate(dom_names):
        entries = domains[dom]
        n_dom = sum(len(e["members"]) for _, e in entries) + (
            len(orphans) if dom == "EXPERIMENTS" and orphans else 0
        )
        last = di == len(dom_names) - 1
        tree.append(f"{'└──' if last else '├──'} {dom} ({n_dom})")
        pad = "    " if last else "│   "
        shown = 0
        for fam, entry in entries:
            if shown >= 6:
                tree.append(f"{pad}└── … +{len(entries) - shown} familias")
                break
            tree.append(f"{pad}├── {fam} ({len(entry['members'])})")
            dups = [m["name"] for m in entry["members"] if m["duplicate_of"]]
            if dups:
                tree.append(f"{pad}│   └── DUPS: {', '.join(dups[:3])}")
            shown += 1
        if dom == "EXPERIMENTS" and orphans:
            tree.append(f"{pad}└── huerfanos ({len(orphans)})")
    tree_path = out_dir / "REPO_TREE.txt"
    tree_path.write_text("\n".join(tree), encoding="utf-8")

    return {"json": json_path, "md": md_path, "tree": tree_path}


def main(argv: list[str]) -> int:
    in_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_IN
    out_dir = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUT
    repos = json.loads(in_path.read_text(encoding="utf-8"))
    data = build_map(repos)
    paths = write_outputs(data, out_dir)
    n_fam = len(data["families"])
    n_orph = len(data["orphans"])
    n_dom = len({f["domain"] for f in data["families"].values()})
    print(f"[+] {len(repos)} repos -> {n_dom} dominios / {n_fam} familias / {n_orph} huerfanos")
    for k, v in paths.items():
        print(f"    {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
