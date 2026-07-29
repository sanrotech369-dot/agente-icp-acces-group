# SETUP — Piloto de n8n en tu PC (Windows)

Objetivo: correr los 5 flujos en tu computadora para **validar tono y calidad** con tus
cuentas reales, generando **borradores** en Outlook que tú revisas. (Para operación
automática 24/7 después migramos a un servidor; en local n8n solo trabaja cuando tu PC está
encendida con n8n abierto.)

---

## Paso 1 — Instalar Node.js
1. Ve a https://nodejs.org → descarga **LTS** (Windows Installer .msi) → instálalo (Siguiente,
   Siguiente, Finalizar).

## Paso 2 — Arrancar n8n
1. Abre **PowerShell** (menú inicio → escribe "PowerShell").
2. Pega y Enter (fija la zona horaria y arranca n8n):
   ```powershell
   $env:GENERIC_TIMEZONE="America/Mexico_City"; $env:TZ="America/Mexico_City"; npx n8n
   ```
3. La primera vez descarga n8n (unos minutos). Cuando diga *Editor is now accessible*, abre
   el navegador en **http://localhost:5678**.
4. Crea tu cuenta local (owner) — es solo para tu n8n en tu PC.
> Para volver a usarlo otro día: repite el comando del punto 2. n8n solo corre mientras esa
> ventana de PowerShell esté abierta.

## Paso 3 — Crear el CRM en Google Sheets
1. Crea un Google Sheet llamado `ICP_CRM_ACCES` con 3 pestañas: `Leads`, `Actividad`, `Config`.
2. En `Leads`: **Archivo → Importar → Subir** el archivo `sistema-n8n/crm/leads-seed.csv`
   (está en tu carpeta clonada del repo) → *Reemplazar hoja actual*. Ya quedan tus 42 cuentas.
3. Llena `Config` según `crm/estructura-crm.md`.
4. Copia el **ID del Sheet** (en la URL, entre `/d/` y `/edit`).

## Paso 4 — API key de Claude
- Entra a https://console.anthropic.com → API Keys → crea una (`sk-ant-...`). Guárdala.

## Paso 5 — Credenciales en n8n (Credentials → New)
1. **Google Sheets (OAuth2)** y **Google Calendar (OAuth2)** — sigue el asistente; en Google
   Cloud pon la Redirect URI que te da n8n (pantalla de consentimiento Externa + tu correo
   como usuario de prueba; habilita APIs Sheets y Calendar).
2. **Microsoft Outlook (OAuth2)** — registra una app en Azure Portal, pon el Redirect URI de
   n8n, permisos `Mail.ReadWrite` (+ `Calendars.ReadWrite` opcional), crea client secret.
3. **Header Auth** (para Claude): Name = `x-api-key`, Value = tu `sk-ant-...`.

## Paso 6 — Importar los 5 flujos
En n8n → **Workflows → Import from File** e importa desde tu carpeta clonada
`sistema-n8n/n8n/`:
`01-prescore-bases.json`, `02-primer-contacto.json`, `03-respuestas-handoff.json`,
`04-seguimiento-cadencia.json`, `05-reporte-marcador.json`.

En cada flujo:
- Nodos **Google Sheets**: reemplaza `REEMPLAZA_SHEET_ID` por tu ID y asigna la credencial.
- Nodos **Outlook**: asigna credencial; confirma recurso **Draft → Create**.
- Nodos **Claude** (HTTP): asigna la credencial **Header Auth**.
- Nodo **Calendar** (flujo 03): asigna credencial y `primary`.
- Flujo 05: pon tu correo en `REEMPLAZA_TU_CORREO`.
- Firma: ya viene la de Ricardo Varela; edita el teléfono en el nodo *Parsear + firma*.

## Paso 7 — Prueba del piloto (manual, sin esperar horario)
1. Abre `01-prescore-bases` → **Execute Workflow**. Verás en `Leads` los `Pre_Score`,
   `Micro_ICP` y `Estado` (pendiente/segunda_ola/nurturing) de las cuentas `sin_prescore`.
   *(Las 42 del seed ya traen estado; para probar el pre-score, pon algunas en
   `Estado=sin_prescore`.)*
2. Abre `02-primer-contacto` → **Execute Workflow** (ignora el horario en modo manual).
   Revisa el **borrador** creado en Outlook: tono, gancho, personalización, firma.
3. Ajusta el prompt (nodo *Elegir lead + tope* / archivos en `prompts/`) hasta que el tono
   te convenza.
4. Para simular una respuesta: contéstate un borrador desde otra cuenta y ejecuta
   `03-respuestas-handoff` a mano → verás la clasificación, la cita y el borrador de respuesta.

## Paso 8 — Activar (opcional en piloto)
Cuando el tono te convenza, pon los flujos en **Active**. Recuerda: en tu PC solo corren
mientras n8n está abierto. Para automático real → migramos a servidor 24/7.

## Modelo de Claude
Los nodos usan `claude-sonnet-5`. Si tu cuenta da error de modelo, cambia el ID en el campo
`jsonBody` del nodo HTTP por el que aparezca en tu consola de Anthropic.
