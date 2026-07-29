# Sistema n8n — Agente ICP ACCES GROUP (afinado a tu operación real)

Construido a partir de **tu** `contexto-icp.md` + índice maestro. No es genérico: usa tu
ICP Real v1, tu pre-score, tus micro-ICP, tus ganchos, tu cadencia 3×3×30, tu firma y tus
candados. Motor: **n8n gratuito + Claude + Outlook + Google Sheets**.

---

## Lo que ya está construido en esta carpeta

```
sistema-n8n/
├── crm/
│   ├── estructura-crm.md      ← esquema del Google Sheet (Leads/Actividad/Config)
│   └── leads-seed.csv         ← TUS 42 empresas ya trabajadas, con su estado real
├── prompts/
│   ├── 01-prescore.md         ← pre-score ICP Real v1 (0–100)
│   └── 02-primer-contacto.md  ← redacción 1er contacto + ganchos por sector
├── n8n/
│   ├── 01-prescore-bases.json ← pre-califica bases → ABORDAR/SEGUNDA_OLA/NURTURING
│   └── 02-primer-contacto.json← mar–jue 8:30–10:30, ≤15/día, borrador Outlook
└── firma/
    └── firma-ricardo-varela.html
```

## Cómo refleja tu metodología (validada con 24 tratos ganados)

| Tu regla real | Dónde vive en el sistema |
|---|---|
| Pre-score 0–100 (Sector30+Reg30+Tam20+Geo10+Señal10) | prompt + workflow 01 |
| ≥70 abordar · 50–69 segunda ola · <50 nurturing | workflow 01 → columna `Estado` |
| Micro-ICP 1/2/3 + ganchos (Anexo 21 / CNBV / auditoría cliente) | prompt 02 |
| Ventana correos **mar–jue 8:30–10:30**, **≤15/día**, semi-manual | workflow 02 (cron + gate + tope) |
| Cadencia 3×3×30, máx 9 toques/30 días | `Cadencia_Paso` + `Num_Toques` |
| Candado de decisor (sin Economic Buyer → nurturing) | columna `Decisor_Mapeado` + regla en prompts |
| Correos VETADOS (2003/adivinados) | pre-score `correo_valido=false` → descartado |
| Firma Ricardo Varela | firma/ + nodos Parsear |
| Frontera: fabricar+calificar hasta 1er contacto → handoff | `Estado` → `lead_handoff` (workflow 03, pendiente) |

## Semilla real incluida (`leads-seed.csv`)
42 cuentas que ya trabajaste, con su **estado preservado** para que el agente **no
recontacte** a quien ya escribiste:
- **CIAJ** (GANADO, webinar oct-2026 · WhatsApp)
- **7 gasolineras** ICP-1 (Petrosun, Tres Emes, Laja Bajío, Grupo IDEA, Delfines, Octano…)
- **17 financieras** ICP-2 (TOKA, Caja SMG, Compartamos, BanBajío, CrediClub, Fincomún…)
- **17 confitería/manufactura** ICP-3 (Alpezzi, Van Dyck, Dulces de la Rosa, La Providencia…)

Los `no_contactado` (tarjetas listas) entran a la cadencia; los `contactado` esperan
respuesta; `descartado` (ya clientes / anti-ICP) quedan fuera.

---

## ⚠️ Decisión pendiente tuya: cadencia
Construí con **tu metodología validada** (mar–jue 8:30–10:30, ≤15/día). Al inicio pediste
*9:00–10:30 diario, ~60/día*. Es un **parámetro**: en `02-primer-contacto.json` cambias el
cron a `* 9-10 * * 1-5`, el gate y el tope. Dime cuál prefieres y lo dejo fijo.

---

## Pendiente de construir (siguiente iteración)
- **03 Respuestas + handoff + agenda:** al responder → clasifica, aplica candado de decisor,
  agenda reunión (Calendar) y marca `lead_handoff` (sale a comercial).
- **04 Seguimiento cadencia 3×3×30:** avanza los toques de correo; marca tareas manuales de
  LinkedIn/video.
- **05 Reporte / marcador:** contactadas, ganados, sin respuesta, tarjetas listas, pipeline.
- **Ingesta de las 147 bases crudas** (ya clasificadas en `Bases_Crudas` del índice maestro)
  → extрае empresas/correos → pre-score → Leads.

## Setup
Mismo procedimiento que la guía de instalación (n8n gratis, credenciales Google/Outlook/
Anthropic Header Auth, importar los JSON, reemplazar `REEMPLAZA_SHEET_ID`). Para el piloto,
importa `leads-seed.csv` al Sheet `Leads` y ejecuta `01` (pre-score) y luego `02`.
