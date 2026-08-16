# Guía de importación y activación — Agente ICP ACCES (sistema completo)

El ciclo completo, de la base cruda a la reunión agendada, en **9 flujos importables**.
Todo semi-manual (borradores) hasta que autorices el envío. **Registro en Google Sheets;
correo + calendario/Teams en Microsoft 365.**

## Los 9 flujos (orden lógico)
| # | Flujo | Qué hace | Dispara |
|---|---|---|---|
| 00 | `00-ingesta-bases` | Carga al Sheet las cuentas de **arranque** (Estado=no_contactado) desde `MASTER_LEADS.csv` | Manual |
| 01 | `01-prescore-bases` | Pre-score 0–100 → ABORDAR/2A OLA/NURTURING | Manual/base nueva |
| 02 | `02-primer-contacto` | Redacta 1er correo con gancho + firma → **borrador Outlook** (mar-jue 8:30-10:30, ≤15/día) | Cron |
| 03 | `03-respuestas-handoff` **v2** | Clasifica 14 casos, **agenda en MS365 + Teams**, booking link, **re-derivación** al decisor, handoff | Cada 10 min |
| 04 | `04-seguimiento-cadencia` | Loop nurturing 3×3×30 (máx 9 toques/30 días) con bitácora | Cron diario |
| 05 | `05-reporte-marcador` | Marcador diario a Ricardo | 18:00 L-V |
| 06 | `06-dashboard-semanal` | **Dashboard de los lunes**: embudo por sector/ICP, agendas, handoffs, cola de enriquecimiento | Lunes 8:00 |
| 07 | `07-enriquecimiento` | Busca correo/canal nuevo (web) → actualiza CRM → **re-encola** | Diario 7:00 |
| 08 | `08-explora-mercados` | Investiga **sectores nuevos** → ficha estilo INTELIGENCIA_SECTORES + peso | Manual |

## Credenciales n8n (2 cuentas web)
1. **Microsoft Outlook OAuth2** (tu correo institucional) → correo + calendario + Teams.
   *(pendiente: consentimiento de administrador de Azure — el director).*
2. **Google Sheets OAuth2** → registro/CRM `ICP_CRM_ACCES`.
3. **Header Auth (Anthropic)** → header `x-api-key` con tu API key de Claude.
4. **Serper** (búsqueda web, para 07 y 08) → API key en `X-API-KEY`. *(serper.dev, plan gratis alcanza para arrancar).*

## Placeholders a reemplazar (buscar y reemplazar en cada JSON)
- `REEMPLAZA_SHEET_ID` → ID de tu Google Sheet.
- `REEMPLAZA_TU_CORREO` → rvarela@accesgroup.com.mx (destinatario de reportes).
- `REEMPLAZA_BOOKING_URL` → tu liga de Microsoft Bookings/Calendly (flujo 03).
- `REEMPLAZA_SERPER_KEY` → API key de Serper (flujos 07, 08).

## Pestañas del Google Sheet
- **Leads** (cabeceras de `estructura-crm.md` + `Correo_Estado`, `Enriquecer`, `Telefono`, `Ciudad`, `Estado_Region`).
- **Actividad** (`Timestamp, ID_Lead, Accion, Canal, Detalle, Score`).
- **Config** (claves de operación) + **Sectores** (`Sector, Estado, Peso, Resumen, Ficha_md, Fuentes`;
  semilla: Construcción, Minería, Energía, Automotriz, Turismo, Logística = `por_robustecer`).

## Carga inicial de datos
- **Arranque (rápido):** ejecuta el flujo **00** → agrega las ~97–120 cuentas listas.
- **Masivo (26,285):** importa `salidas/MASTER_LEADS.csv` directo al Sheet (Archivo → Importar)
  para no saturar la API. La **reserva** (137k multisector) queda en `MASTER_RESERVA.csv` para segmentar después.

## Lo único que hace un humano
1. Importar los 9 JSON a n8n.
2. Conectar las credenciales (Microsoft, Google, Anthropic, Serper) y reemplazar placeholders.
3. **Esperar el consentimiento de Azure del director** → conectar Outlook.
4. Revisar y aprobar los borradores (semi-manual) hasta que decidas automatizar el envío.

> A partir de ahí, el agente tiene **un solo objetivo: conseguir la reunión** — califica,
> contacta, responde, agenda en Teams, re-deriva al decisor, enriquece a los que no tienen
> correo, nutre a los que no contestan, investiga sectores nuevos y te reporta cada lunes.
