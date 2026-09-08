"""Extract sanitized insights from a ChatGPT chat-export JSON.

Reads the chat-export JSON (default: chat-export-1788747098977.json in
Downloads) and emits ONLY aggregate statistics (titles, chat types,
timestamps, counts). Message bodies are never copied. Everything passes
through the redactor before being written, so JWT-shaped tokens or keys
can never leak into the output.

Usage: python from_chat_export.py [export.json] [out_dir]
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_IN = Path(r"C:\Users\USER\Downloads\chat-export-1788747098977.json")
DEFAULT_OUT = HERE / "docs"

_SECRET_RE = re.compile(
    r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
    r"|\bsk-[A-Za-z0-9]{12,}|\bnvapi-[A-Za-z0-9]{20,}"
    r"|\bAIza[A-Za-z0-9_\-]{20,}|AQ\.[A-Za-z0-9_\-]{16,}"
    r"|github_pat_[A-Za-z0-9_]{10,}|\bhf_[A-Za-z0-9]{20,}"
)


def clean(text: str) -> str:
    return _SECRET_RE.sub("[REDACTED]", text)


def main(argv: list[str]) -> int:
    in_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_IN
    out_dir = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = json.loads(in_path.read_text(encoding="utf-8"))
    data = raw.get("data") or {}

    chats = data.get("messages") or []
    titles = [clean(str(t)) for t in (data.get("title") or "").split("\n") if str(t).strip()]
    types = [clean(str(t)) for t in (data.get("chat_type") or "").split() if str(t).strip()]

    stats = {
        "source": in_path.name,
        "generated": "2026-09-08",
        "total_conversations": len(chats),
        "titles": titles,
        "chat_types": Counter(types),
        "models_seen": sorted(
            {clean(str(m)) for m in (data.get("models") or []) if str(m).strip()}
        ),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "note": "stats only - message bodies were never extracted (privacy + secrets)",
    }
    (out_dir / "chat-export-stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Chat Export — Insights (sanitized)",
        "",
        f"- Conversaciones: **{stats['total_conversations']}**",
        f"- Creado: {stats['created_at']} · Actualizado: {stats['updated_at']}",
        "",
        "## Tipos de chat",
        "",
    ]
    for kind, count in stats["chat_types"].most_common():
        md.append(f"- {kind}: {count}")
    md += ["", "## Títulos", ""]
    for t in titles:
        md.append(f"- {t}")
    md += [
        "",
        "## Modelos vistos",
        "",
    ]
    for m in stats["models_seen"]:
        md.append(f"- `{m}`")
    md += [
        "",
        "> Solo estadísticas. Los cuerpos de mensajes no se extrajeron.",
    ]
    (out_dir / "chat-export-insights.md").write_text(
        "\n".join(md), encoding="utf-8"
    )
    print(f"[+] stats -> {out_dir / 'chat-export-stats.json'}")
    print(f"[+] md    -> {out_dir / 'chat-export-insights.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
