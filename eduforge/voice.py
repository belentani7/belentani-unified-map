#!/usr/bin/env python3
"""EDU FORGE — voz humana por idioma (ES/CA/PT/EN) sin coste.

Pipeline 1 (recomendado): edge-tts (Microsoft, gratis, sin API key,
voces neuronales humanas por idioma).
Pipeline 2 (alternativa): Kokoro TTS via Hugging Face Inference API
(opcional HF_API_KEY, nunca se commitea).
Pipeline 3 (fallback): manifiesto + nota (los audio se generan al hacer
deploy o en local con: python -m eduforge.voice).

Voces:
  es -> es-ES-ElviraNeural   ca -> ca-ES-JoanaNeural
  pt -> pt-BR-FranciscaNeural  en -> en-US-AriaNeural
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eduforge.curriculum import VOICE_SCRIPTS  # noqa: E402


async def _edge_speak(voz: str, texto: str, out: Path) -> bool:
    try:
        import edge_tts
    except ImportError:
        return False
    try:
        com = edge_tts.Communicate(texto, voz)
        await com.save(str(out))
        return out.exists() and out.stat().st_size > 1000
    except Exception:
        return False


async def _kokoro_speak(voz: str, texto: str, out: Path,
                        api_key: str | None) -> bool:
    if not api_key:
        return False
    import urllib.request
    payload = json.dumps({"inputs": texto,
                          "options": {"use_cache": False}}).encode()
    req = urllib.request.Request(
        f"https://router.huggingface.co/hf-inference/models/hexgrad/Kokoro-82M?voice={voz}",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out.write_bytes(r.read())
        return out.stat().st_size > 1000
    except Exception:
        return False


def kokoro_voices() -> dict:
    """Voces Kokoro (Hugging Face) por idioma."""
    return {"es": "ef_dora", "ca": "ef_dora",  # kokoro no tiene CA nativa
            "pt": "pf_dora", "en": "af_heart"}


def main() -> int:
    clones = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"C:\Users\USER\AppData\Local\Temp\opencode\audit-deploys")
    repos = ["ManosAbiertas", "lingua-aberta", "ux-academy-professional-program",
             "linguaforge", "open-school"]
    hf_key = None
    hf_file = Path(r"C:\Users\USER\keyrotor\.hf_key")
    if hf_file.exists():
        hf_key = hf_file.read_text(encoding="utf-8").strip() or None

    report = {}
    for repo in repos:
        voces = clones / repo / "campus" / "voces"
        if not voces.is_dir():
            continue
        done = []
        for lang, (voz_edge, guion) in VOICE_SCRIPTS.items():
            out = voces / f"bienvenida-{lang}.mp3"
            ok = asyncio.run(_edge_speak(voz_edge, guion, out))
            metodo = "edge-tts"
            if not ok:
                ok = asyncio.run(
                    _kokoro_speak(kokoro_voices()[lang], guion, out, hf_key))
                metodo = "kokoro-hf"
            if not ok:
                out.write_text("", encoding="utf-8")
            done.append({"idioma": lang, "archivo": out.name,
                         "ok": ok, "metodo": metodo})
        report[repo] = done
        ok_n = sum(1 for d in done if d["ok"])
        print(f"[{repo}] voces: {ok_n}/{len(done)} generadas")
    out = Path(r"C:\Users\USER\belentani-unified\audit\edu-voice.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"[+] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
