# belentani-unified

511 repos de GitHub = piezas de ~11 proyectos lógicos. Este repo unifica
el ecosistema por lógica, no por nombre, y contiene el prompt definitivo.

## Contenido

| Archivo | Qué es |
|---|---|
| `DEFINITIVE_PROMPT.md` | EL prompt definitivo: repos + skills + dibujo del sistema + reglas |
| `unify_repos.py` | Unificador estructural (Python stdlib): normaliza, agrupa por familia, detecta duplicados, emite JSON/MD/ASCII |
| `unified/REPO_UNIFICATION_MAP.json` | Mapa completo máquina-legible (dominios, familias, dups) |
| `unified/REPO_UNIFICATION_MAP.md` | Mapa legible por humanos |
| `unified/REPO_TREE.txt` | Árbol ASCII del ecosistema |

## Regenerar

```bash
gh repo list --limit 1000 --json name,visibility,isArchived,pushedAt,isFork,primaryLanguage,description > repos.json
python unify_repos.py repos.json unified
```

`repos.json` nunca se sube a git (es regenerable y contiene metadata de
cuenta). Cero secretos en este repo.

## Estado

- Generado: 2026-09-08
- 511 repos → 11 dominios → 358 familias
- Duplicados detectados por similitud >= 0.85 dentro de cada familia
