# CRM del Agente ICP — Google Sheets (cerebro único, gratis)

Google Sheet `ICP_CRM_ACCES` con 3 pestañas. Refleja tu metodología real (pre-score,
micro-ICP, candado de decisor, frontera de primer contacto).

## Pestaña `Leads`
Cabeceras exactas (fila 1). El seed real está en `leads-seed.csv` (impórtalo aquí):

| Columna | Significado | Escribe |
|---|---|---|
| `ID_Lead` | ID único (L-0001) | tú/ingesta |
| `Empresa` | razón comercial | tú |
| `Micro_ICP` | ICP-1 / ICP-2 / ICP-3 / OBSERVACION / ALIANZA | agente |
| `Sector` | sector fino | tú/agente |
| `Pais` | país | tú |
| `Contacto` · `Cargo` · `Correo` | contacto | tú |
| `Decisor_Mapeado` | si/no — **CANDADO**: si=no → nurturing aunque score alto | agente |
| `Pre_Score` | 0–100 (desde base, a quién abordar) | agente |
| `Score_ICP` | 0–100 (al 1er contacto, si entra a pipeline) | agente |
| `Estado` | `sin_prescore` · `pendiente` · `contactado` · `respondio` · `agendado` · `lead_handoff` · `nurturing` · `descartado` · `no_contactado` | agente |
| `Etapa` | Fabricación · Primer contacto · Handoff comercial | agente |
| `Trigger_Regulatorio` | Anexo 21 / CNBV / Auditoría cliente / … | agente |
| `Gancho` | gancho de mensaje del sector | agente |
| `Cadencia_Paso` | paso 3×3×30 (1..9) | agente |
| `Ultimo_Contacto` · `Fecha_Siguiente_Paso` | fechas YYYY-MM-DD | agente |
| `Num_Toques` | toques (máx 9 / 30 días) | agente |
| `Canal` | correo / LinkedIn / WhatsApp / llamada | agente |
| `Fuente` | base de origen | tú |
| `Thread_Id` · `Event_Id` | IDs reales Outlook/Calendar (nunca inventar) | agente |
| `Asunto` · `Notas` | último asunto / bitácora | agente |

## Pestaña `Actividad`
`Timestamp` · `ID_Lead` · `Accion` · `Canal` · `Detalle` · `Score`

## Pestaña `Config`
| Clave | Valor ejemplo |
|---|---|
| remitente_nombre | Ricardo Varela |
| remitente_correo | rvarela@accesgroup.com.mx |
| tope_diario_correos | 15 |
| ventana_dias | 2,3,4  (mar-jue) |
| ventana_horas | 8:30-10:30 |
| zona_horaria | America/Mexico_City |
| max_toques | 9 |
| dias_candado_decisor | 15 |

> **Regla:** el pre-score prioriza (a quién), el score completo califica (si entra). No se
> mezclan. Ninguna cuenta pasa a handoff sin Economic Buyer mapeado.
