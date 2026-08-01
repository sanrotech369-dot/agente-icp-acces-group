# Flujo 03 · Respuestas → Reunión (agente autónomo de conversión)

> Objetivo único del agente: **conseguir una entrada**, generando rapport consultivo, y
> **agendar una reunión de 20 min con estructura identificada**. Semi-manual: todo se
> redacta como borrador para revisión humana hasta que se autorice el envío automático.
> Fiel a `contexto-icp.md`: candado de decisor, frontera de handoff, cadencia 3×3×30,
> regla 70/30, sin inventar correos, sin precio prematuro.

## 0. Realidad MS365
El cliente usa **Microsoft 365**. Por tanto:
- Lectura de disponibilidad y creación de citas = **Microsoft Graph / Outlook Calendar**
  (mismas credenciales OAuth2 que el correo), NO Google Calendar.
- Link de auto-agenda = `BOOKING_URL` en `Config` (Microsoft Bookings o Calendly).

---

## 1. Mapa COMPLETO de casos (qué contesta el prospecto → qué hace el agente)

| # | Intención detectada | Señales típicas | Acción del agente | Estado CRM |
|---|---|---|---|---|
| 1 | **interesado_agenda** | "sí me interesa", "cuándo", "esta/próxima semana", "mándame invitación" | Detectar ventana (semana en curso / próxima) → **leer disponibilidad MS365** → proponer **2–3 franjas reales** + ofrecer `BOOKING_URL` → crear cita tentativa | `agendado` |
| 2 | **da_horario_especifico** | "el martes 5pm", "jueves después de las 4" | Parsear fecha/hora → **validar contra calendario MS365** → si libre: confirmar + crear evento; si ocupado: proponer la más cercana | `agendado` |
| 3 | **requerimiento** | describe un dolor/necesidad real, pide propuesta/alcance | Respuesta consultiva (NO sobre-proponer): reconoce el requerimiento, 1 pregunta de diagnóstico, propone **llamada de 20 min de alcance**. Si hay decisor → `lead_handoff` | `respondio`→`lead_handoff` |
| 4 | **persona_equivocada / dio_decisor** | "no soy yo", "contacta a X", da correo/nombre del correcto | **Generar NUEVO correo** al referido: menciona **quién lo refirió**, contexto, qué resolvemos, gancho del sector; **crear nuevo lead** ligado; agradecer al que refirió | nuevo lead `no_contactado`; original `descartado(referido)` |
| 5 | **pregunta** | duda concreta (qué hacen, precios, tiempos, casos) | Responder con **valor** (70/30), sin precio cerrado; reconducir a la llamada de 20 min | `respondio` |
| 6 | **objecion** | "ya tenemos proveedor", "sin presupuesto", "no es prioridad", "caro" | Escuchar→reconocer→**pregunta de diagnóstico**. Precio → reactivación ("el contexto cambió, ¿ahora sí hacen los números?"). NO descuento, NO presión | `respondio`/`nurturing` |
| 7 | **no_interesado** | "no gracias", "quítame" | Agradecer, cerrar con clase, **nurturing** con fecha de reactivación (+90d). Respetar opt-out | `nurturing`/`descartado` |
| 8 | **fuera_de_oficina** | auto-reply OOO, "vacaciones hasta…" | NO redactar respuesta; **reprogramar** el toque a la fecha de regreso; no cuenta como respuesta | sin cambio |
| 9 | **rebote / correo_invalido** | bounce, "dirección no existe" | Disparar **enriquecimiento**: buscar correo/canal nuevo → actualizar CRM → re-encolar primer contacto | `pendiente`+`[ENRIQUECER]` |
| 10 | **otro_canal** | "márcame", "por WhatsApp", da teléfono | Registrar canal; preparar guion de llamada/WhatsApp; agendar toque por ese canal | `respondio` |
| 11 | **reagenda / cancela** | "movamos la cita", "no podré" | Leer evento (Event_Id) → proponer nueva franja / cancelar en MS365 → confirmar | `agendado` |
| 12 | **cortés_sin_compromiso** | "gracias, lo reviso", vago | Pregunta calificadora suave + valor; mantener cadencia | `respondio` |
| 13 | **solicita_propuesta_formal** | "mándame cotización/propuesta" | NO cotizar en frío: ofrecer **llamada de alcance de 20 min** para dimensionar; si insiste y hay decisor → `lead_handoff` a comercial | `lead_handoff` |
| 14 | **spam / irrelevante** | newsletters, no-reply | Ignorar, marcar leído, no registrar actividad | sin cambio |

**Candado de decisor (transversal):** ninguna cuenta pasa a `lead_handoff` sin Economic
Buyer mapeado. Si responde alguien sin poder y NO da al decisor → seguir con correo de
**orientación** ("¿con quién debería dirigir este tema?").

---

## 2. Sub-flujo de AGENDA (casos 1, 2, 11) — el corazón

```
Claude clasifica → decision_agenda=true, ventana={semana_curso|proxima|fecha_dada}
   │
   ├─ [Graph: getSchedule] leer libre/ocupado en ventana de reuniones
   │      (mar–jue 10:00–13:00 y 16:00–18:00 MX, configurable; evita 13–14h)
   │
   ├─ [Code] calcular 2–3 franjas realmente libres (>=48h de anticipación)
   │
   ├─ ¿hay franjas claras?
   │     SÍ → Claude arma respuesta con las 2–3 opciones reales + "o si prefieres,
   │          agenda tú mismo aquí: {BOOKING_URL}"  →  crear evento TENTATIVO
   │     NO / agenda saturada → responder SOLO con {BOOKING_URL} (auto-agenda)
   │
   └─ [Graph: create event] título "ACCES × {Empresa} — 20 min", invitado = correo,
          cuerpo con contexto; guarda Event_Id real (nunca inventado) en CRM
```
- **Estructura identificada de la reunión** (para que no sea "una llamada más"): el evento
  y el correo llevan una mini-agenda de 3 puntos: (1) contexto del sector/dolor, (2) cómo
  otros resuelven la evidencia/continuidad, (3) siguiente paso. Así la reunión nace con
  estructura y objetivo, no abierta.
- **Anticipación y no-solapamiento:** solo franjas con ≥48h y sin choque; respeta la
  agenda real del director.

---

## 3. Sub-flujo de RE-DERIVACIÓN (caso 4) — "contacta a otra persona"

Cuando `persona_equivocada=true` y `decisor_revelado` con correo:
1. **Crear nuevo lead** (misma empresa, nuevo contacto, `Fuente`=referido por {quien}).
2. **Redactar correo cálido de intro** con estos elementos obligatorios:
   - Quién lo refirió ("{Nombre} me sugirió escribirle directamente").
   - Qué hacemos y **qué problema resolvemos** para su sector (gancho).
   - Respeto: "no quiero saltarme pasos, me pasaron su contacto como la persona correcta".
   - CTA suave a 20 min.
3. **Agradecer** al que refirió (correo breve de cortesía) y marcar su lead `descartado(referido)`.
4. Candado: el nuevo contacto arranca con `Decisor_Mapeado` según lo que dijo el referidor.

---

## 4. Arquitectura de nodos (v2 — reemplaza Google Calendar por MS365)

```
Cada 10 min (schedule)
 → Outlook: correos no leídos (bandeja)
 → ¿es OOO/bounce/spam? (Code pre-filtro)  ──► ramas 8/9/14
 → Buscar lead en CRM (Google Sheets, por correo/thread)
 → Prep clasificación (Code: arma contexto + historial)
 → Claude: Clasificar + Redactar (prompt 03 v2)  → JSON estricto
 → Parsear
 → switch(intencion):
      agenda      → Graph getSchedule → Code franjas → Graph create event → Capturar Event_Id
      referido    → Crear lead nuevo (Sheets) → Claude intro → borrador Outlook al referido
      handoff     → marcar lead_handoff + notificar comercial
      objecion/pregunta/otro → (respuesta directa)
      OOO/bounce/spam → reprogramar / enriquecer / ignorar
 → Outlook: borrador de respuesta (semi-manual)
 → Actualizar lead (Sheets: estado, etapa, score, Event_Id, bitácora, Fecha_Siguiente_Paso)
 → Registrar en Actividad (Sheets)
 → Outlook: marcar leído
```
**Config nuevos (`Config`):** `booking_url`, `calendario_id` (o `me`), `ventana_reunion`
(`mar-jue 10-13,16-18`), `min_horas_anticipacion=48`, `dias_reactivacion=90`,
`correo_comercial_handoff`.

---

## 5. "Piensa antes de ejecutar" (preparado para decidir)
Como Outlook aún no está conectado, **todo queda en borrador** (gate humano). Cuando se
autorice, el mismo flujo **ejecuta**: crea la cita real, manda el correo, mueve el estado.
El agente nunca inventa Event_Id/Thread_Id: si Graph falla, cae a `BOOKING_URL` y avisa.

## 6. Robustecimiento (técnicas ICP modernas a incorporar por fases)
- **Trigger-event monitoring**: vacante de CISO, multa CNBV, deadline regulatorio <6 meses,
  cambio de CIO → sube prioridad y personaliza gancho (ya hay señales en INTELIGENCIA_SECTORES).
- **Multi-threading**: correo a dirección + LinkedIn al champion técnico en paralelo.
- **Allbound / intent**: cruzar bases con señales públicas (dorks) antes de tocar.
- **Personalización "show me you know my world"**: 1 dato real del sector/empresa por correo.
- **Bandit de asuntos**: A/B de líneas de asunto, el agente aprende cuál abre más.
