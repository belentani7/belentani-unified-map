# AUDITORIA MAXIMA — ECOSISTEMA DESPLEGADO (Vercel / Cloudflare / Netlify / Pages)

- Fecha: 2026-09-08
- Repos auditados: **10**
- Metodo: clon superficial + escaner de secretos keyrotor + verificacion HTTP real
- Regla: cero valores secretos reproducidos en este informe

---

## 1. RESUMEN EJECUTIVO

| Veredicto | Cantidad |
|---|---|
| Secretos reales commiteados | **0** (en los 10 repos) |
| .env commiteados | 2 (ambos `.env.example` con placeholders vacios) |
| Deployments VIVOS | 4 (+ 4 subpaths de GitHub Pages) |
| Deployments MUERTOS (404) | 7 |
| Tokens en CI hardcodeados | 0 (usa GitHub Secrets correctamente) |

---

## 2. DEPLOYMENTS VIVOS (verificado HTTP 200 hoy)

| URL | Proyecto | Plataforma |
|---|---|---|
| `https://belentani-judas.vercel.app` | BELENTANI Judas Experience OS | Vercel |
| `https://ux-academy-professional-program.vercel.app` | UX Academy — Diseno, growth y practica profesional | Vercel |
| `https://manosabiertas-seven.vercel.app` | ManosAbiertas (homepage oficial) | Vercel |
| `https://belentani7.github.io` (root) | BELENTANI // OMEGA CORE — JUDAS_OS v12.0 | GitHub Pages |

> Nota: `manosabiertas-seven.vercel.app` responde 200 pero muestra
> "Login - Vercel": la Deployment Protection de Vercel esta ACTIVADA
> (site vivo, gated por login).

### GitHub Pages habilitadas

| Subpath | Estado |
|---|---|
| `/ManosAbiertas/` | Pages habilitada |
| `/linguaforge/` | Pages habilitada |
| `/ux-academy-professional-program/` | Pages habilitada |
| `/Netlify/` | Pages habilitada |

---

## 3. DEPLOYMENTS MUERTOS (404) — candidatos a limpieza

- `linguaforge-belentani.netlify.app`
- `linguaforge-belentani.surge.sh`
- `linguaforge-belentani.vercel.app`
- `manos-abiertas-belentani.netlify.app`
- `manos-abiertas-belentani.surge.sh`
- `manos-abiertas-belentani.vercel.app`
- `manosabiertas-vercel.vercel.app`

> Accion sugerida: eliminar proyectos muertos en Vercel/Netlify/Surge y
> quitar esas URLs de READMEs para que el mapa de deploys sea fiel.

---

## 4. POSTURA DE SEGURIDAD POR REPO

| Repo | Deploy config | CI | Secret-like values | Veredicto |
|---|---|---|---|---|
| belentani-monorepo | ninguno (TurboRepo) | ninguna | 0 | CLEAN |
| lingua-aberta | ninguna | ninguna | 0 (solo `.env.example` vacio) | CLEAN |
| linguaforge | ninguna | ninguna | 0 | CLEAN |
| linguaforge-v2 | ninguna | ninguna | 0 | CLEAN |
| manos-abiertas-release-netlify-20260812 | netlify.toml | ninguna | 0 | CLEAN |
| ManosAbiertas | ci:vercel-action + ci:netlify-action | deploy.yml | 0 (solo `.env.example` vacio) | CLEAN |
| manosabiertas-vercel-20260813 | netlify.toml | ninguna | 0 | CLEAN |
| maos-abertas-linguaforge | ninguna | ci.yml | 0 | CLEAN |
| Netlify | netlify.toml | ci.yml + deploy-pages.yml | 0 | CLEAN |
| ux-academy-professional-program | vercel.json + netlify.toml | ninguna | 0 | CLEAN |

### Buenas practicas confirmadas

- `ManosAbiertas/.github/workflows/deploy.yml` usa `secrets.NETLIFY_AUTH_TOKEN`
  y `secrets.NETLIFY_SITE_ID` — sin tokens hardcodeados.
- Ningun `serviceAccount.json` ni `credentials.json` commiteado.
- Los `.env.example` encontrados contienen variables con valores vacios.

---

## 5. INVENTARIO DE FRAMEWORKS

- Next.js/React: ManosAbiertas, Netlify, manos-abiertas-*-2026081x
- React + Vite: lingua-aberta, linguaforge, linguaforge-v2, maos-abertas-linguaforge, ux-academy-professional-program
- TurboRepo: belentani-monorepo

---

## 6. ACCIONES RECOMENDADAS (por prioridad)

1. **Consolidar deploys**: ManosAbiertas tiene 3 plataformas tocadas (Vercel, Netlify, Pages) + 7 URLs muertas. Elegir 1 canonica por proyecto.
2. **Auditar Deployment Protection**: `manosabiertas-seven.vercel.app` gated — confirmar que es intencional.
3. **Limpieza de URLs muertas** en READMEs (seccion 3).
4. **Backups archivados**: 5+ repos `-backup-2026-08-2x` archivados correctamente — no requieren accion.
5. **Rotar** cualquier token usado en despliegues antiguos de Netlify/Vercel si fueron generados antes de 2026-08.

---

## 7. ARTEFACTOS

- `audit/audit-results.json` — datos crudos por repo (sin valores)
- `audit/audit-live.json` — verificacion HTTP de URLs
- `audit/audit-report.md` — este informe
- `audit_deploys.py` — motor de auditoria (re-ejecutable)

*Generado 2026-09-08 por la auditoria de ampliacion maxima.*
