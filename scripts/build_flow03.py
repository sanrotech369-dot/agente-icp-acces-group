# -*- coding: utf-8 -*-
# Genera 03-respuestas-handoff.json v2 (MS365 calendario+Teams, disponibilidad real, re-derivacion).
import json

SYS = "\n".join([
"<identidad>Agente de ACCES GROUP (Ricardo Varela) manejando la respuesta de un prospecto. Consultiva, espanol de NEGOCIO, sin jerga, sin presion, sin precio prematuro, sin inventar.</identidad>",
"<mision>Unico objetivo: conseguir la ENTRADA y AGENDAR una reunion de 20 min con estructura (contexto->como se resuelve->siguiente paso). Vende el siguiente paso pequeno, no el proyecto.</mision>",
"<frontera>Fabricamos y calificamos hasta el 1er contacto. Si responde con requerimiento real y hay decisor -> LEAD, nuevo_estado=lead_handoff. Reunion aceptada != trato ganado.</frontera>",
"<candado>Ninguna cuenta a lead_handoff sin Economic Buyer mapeado. Si revelan quien decide -> decisor_revelado=true + datos. Si el que responde no decide y no da al decisor -> correo de orientacion.</candado>",
"<intenciones>interesado_agenda | da_horario_especifico | requerimiento | persona_equivocada | pregunta | objecion | no_interesado | fuera_de_oficina | rebote | otro_canal | reagenda | cortes_sin_compromiso | solicita_propuesta | spam</intenciones>",
"<agenda>Para interesado_agenda/da_horario_especifico/reagenda: decision_agenda=true. NO inventes horarios: usa las franjas de {DISPONIBILIDAD}. Propon 2-3 de ESAS franjas y ofrece SIEMPRE auto-agenda {BOOKING_URL}. Solo si el cliente da/confirma UNA hora concreta pon crear_evento implicito devolviendo esa hora en opciones_iso[0] e intencion=da_horario_especifico. Si {DISPONIBILIDAD} vacia -> usar_booking_link=true.</agenda>",
"<re_derivacion>Si te mandan con otra persona y dan correo/nombre: persona_equivocada=true, decisor={nombre,correo,cargo}, quien_refirio=nombre del que respondio. cuerpo_html = intro calida al referido (menciona quien lo refirio + que resolvemos + respeto + CTA 20 min). correo_agradecimiento = 1-2 lineas al que refirio.</re_derivacion>",
"<reglas>Max ~120 palabras, 1 CTA, sin firma. objecion: escuchar-reconocer-diagnostico, sin descuento/presion (reactivacion si es precio). no_interesado: agradece y cierra (nurturing +90d). fuera_de_oficina/rebote/spam: no_redactar=true (rebote -> enriquecer=true). solicita_propuesta: NO cotices, ofrece llamada de alcance 20 min.</reglas>",
"<prohibido>NO % sin universo. NO miedo regulatorio ni cumplimiento garantizado. NO nombrar entidades afectadas. NO precio prematuro. NO inventar correos, horarios ni IDs.</prohibido>",
'<salida>SOLO este JSON sin backticks : {"intencion":"","no_redactar":false,"decisor_revelado":false,"decisor":{"nombre":"","correo":"","cargo":""},"persona_equivocada":false,"quien_refirio":"","nuevo_score":0,"nuevo_estado":"respondio|agendado|lead_handoff|nurturing|descartado","nueva_etapa":"Primer contacto|Handoff comercial","decision_agenda":false,"ventana":"","crear_evento":false,"propuesta_reunion":{"titulo":"","duracion_min":20,"estructura":["","",""],"opciones_iso":[]},"usar_booking_link":false,"enriquecer":false,"canal_sugerido":"correo","asunto_respuesta":"","cuerpo_html":"","correo_agradecimiento":"","fecha_siguiente_paso":"YYYY-MM-DD","razon":""}</salida>',
])

PREP = r"""
// ---- Prep clasificacion v2: disponibilidad real MS365 + prompt v2 ----
const BOOKING_URL = 'REEMPLAZA_BOOKING_URL'; // Microsoft Bookings o Calendly
const leads = $('Buscar lead').all().map(i=>i.json).filter(l=>l && l.ID_Lead);
const msgs  = $('Outlook: no leídos').all().map(i=>i.json);
let events = [];
try { const r = $('Graph: disponibilidad').first().json; events = (r && r.value) ? r.value : []; } catch(e){ events = []; }
// franjas libres reales (MX -06:00, sin DST): mar-jue 10-13 y 16-18, >=48h, 20 min
function iso(d){ return d.toISOString(); }
const now = new Date();
const busy = events.filter(e=>e && e.start && e.end && (e.showAs!=='free'))
  .map(e=>({s:new Date(e.start.dateTime+'-06:00'), e:new Date(e.end.dateTime+'-06:00')}));
function libre(cand){ for(const b of busy){ if(cand>=b.s && cand<b.e) return false; } return true; }
const dias=['dom','lun','mar','mié','jue','vie','sáb'];
const meses=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
const horas=[10,10.5,11,12,16,16.5,17];
const slotsISO=[]; const slotsTxt=[];
for(let dd=2; dd<=16 && slotsISO.length<4; dd++){
  const base=new Date(now.getTime()+dd*86400000);
  const wd=base.getUTCDay(); // aprox
  const dow=new Date(base.toLocaleString('en-US',{timeZone:'America/Mexico_City'})).getDay();
  if(![2,3,4].includes(dow)) continue;
  const y=base.getFullYear(), mo=base.getMonth(), da=base.getDate();
  for(const h of horas){
    const hh=Math.floor(h), mm=(h%1)?30:0;
    const cand=new Date(`${y}-${String(mo+1).padStart(2,'0')}-${String(da).padStart(2,'0')}T${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}:00-06:00`);
    if((cand-now)<48*3600000) continue;
    if(!libre(cand)) continue;
    slotsISO.push(cand.toISOString());
    slotsTxt.push(`${dias[cand.getUTCDay()]} ${da} ${meses[mo]} ${String(hh).padStart(2,'0')}:${mm?'30':'00'}`);
    if(slotsISO.length>=4) break;
  }
}
const DISPONIBILIDAD = slotsTxt.length ? slotsTxt.join(' | ') : '(sin franjas: usar BOOKING_URL)';
const out=[];
for(const lead of leads){
  const msg = msgs.find(m=>m && m.from && m.from.emailAddress && m.from.emailAddress.address===lead.Correo) || {};
  const texto=(msg.body && msg.body.content)? msg.body.content : (msg.bodyPreview||'');
  const user = `Fecha hoy: ${$now.toFormat('yyyy-LL-dd')} · Zona: America/Mexico_City\n`
   +`Lead: ${lead.Empresa} | Micro-ICP ${lead.Micro_ICP} | Sector ${lead.Sector} | Contacto ${lead.Contacto} (${lead.Cargo})\n`
   +`Gancho: ${lead.Gancho} | Trigger: ${lead.Trigger_Regulatorio} | Estado: ${lead.Estado} | Decisor_Mapeado: ${lead.Decisor_Mapeado}\n`
   +`BOOKING_URL: ${BOOKING_URL}\nDISPONIBILIDAD (franjas libres reales MS365): ${DISPONIBILIDAD}\nopciones_iso disponibles: ${JSON.stringify(slotsISO)}\n`
   +`--- CORREO DEL PROSPECTO ---\nAsunto: ${msg.subject||''}\nCuerpo:\n[inicio]\n${texto}\n[fin]\n--- Clasifica y redacta. Devuelve solo el JSON. ---`;
  out.push({ json: { ...lead, msg_id: msg.id, conversationId: msg.conversationId, booking_url: BOOKING_URL, disponibilidad: DISPONIBILIDAD, slotsISO, system: $json.__sys, user } });
}
return out;
"""
# inyecta el system via variable para no escapar dos veces
PREP = PREP.replace("$json.__sys", "SYSTEM_PLACEHOLDER")

FIRMA = r"""
// ---- Parsear v2: parse JSON, arma cuerpo con firma, agenda/re-derivacion ----
const L='https://raw.githubusercontent.com/sanrotech369-dot/acces-assets/main/';
let text=''; try { const _b=$json.content||($json.body&&$json.body.content)||[]; const _t=_b.find(x=>x&&x.type==='text'); text=_t?_t.text:'{}'; } catch(e){ text='{}'; }
text=text.replace(/^```json/i,'').replace(/```$/,'').trim();
let d; try{ d=JSON.parse(text);}catch(e){ d={intencion:'otro',no_redactar:true,razon:'parse_error'}; }
const l=$('Prep clasificación').item.json;
const dest = d.persona_equivocada ? ((d.decisor&&d.decisor.correo)||l.Correo) : l.Correo;
const nombre = d.persona_equivocada ? ((d.decisor&&d.decisor.nombre)||'estimado(a)') : ((l.Contacto&&String(l.Contacto).trim())?l.Contacto:'estimado(a)');
const CUERPO = d.cuerpo_html||'';
const html='<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222;max-width:680px;">'
+'<p style="margin:0 0 12px 0;"><strong>CLASIFICACI&Oacute;N:</strong> <strong style="color:#c00;">CONFIDENCIAL</strong></p>'
+'<p style="margin:0 0 16px 0;"><img src="'+L+'logo.png" alt="ACCES GROUP" style="max-width:220px;height:auto;"></p>'
+'<p style="margin:0 0 4px 0;">Muy buen d&iacute;a <strong>'+nombre+'</strong>,</p>'
+'<p style="margin:0 0 16px 0;">Es un placer y un gusto saludarte.</p>'+CUERPO
+'<p style="margin:16px 0 4px 0;">Quedo atento a tus comentarios.</p>'
+'<p style="margin:0 0 20px 0;">Saludos y excelente d&iacute;a.</p>'
+'<p style="margin:0 0 8px 0;"><img src="'+L+'firma.png" alt="Ricardo Varela Leyva" style="max-width:430px;height:auto;"></p>'
+'<p style="margin:16px 0 0 0;font-size:10px;color:#999;">Aviso de privacidad: <a href="https://www.accesgroup.com.mx/aviso-privacidad/" style="color:#0a3d62;">accesgroup.com.mx/aviso-privacidad</a></p></div>';
d.cuerpo_final=html; d.destinatario=dest;
const pr=d.propuesta_reunion||{}; const opt=(pr.opciones_iso&&pr.opciones_iso[0])?pr.opciones_iso[0]:null; const dur=pr.duracion_min||20;
d.reunion_titulo=pr.titulo||('ACCES GROUP <> '+(l.Empresa||'')+' — 20 min');
d.reunion_estructura=(pr.estructura||[]).filter(Boolean).map((s,i)=>(i+1)+'. '+s).join('<br>');
d.crear_evento = (d.crear_evento===true) || (d.intencion==='da_horario_especifico');
if(d.crear_evento && opt){ d.reunion_inicio=opt; d.reunion_fin=new Date(new Date(opt).getTime()+dur*60000).toISOString(); } else { d.crear_evento=false; }
if(d.decisor_revelado) d.Decisor_Mapeado='si';
return [{ json: { ...l, ...d } }];
"""

def code(js): return {"jsCode": js}
def pos(x,y): return [x,y]

nodes = []
def add(nid,name,ntype,tv,params,x,y):
    nodes.append({"parameters":params,"id":nid,"name":name,"type":ntype,"typeVersion":tv,"position":[x,y]})

add("note1","Guía","n8n-nodes-base.stickyNote",1,{"content":"## 03 v2 · Respuestas → Reunión (MS365)\nCada 10 min: lee respuestas, consulta DISPONIBILIDAD real (Graph calendarView), clasifica 14 casos, agenda en MS365 con enlace de Teams automático, re-deriva al decisor, deja borradores (semi-manual). Registro en Google Sheets.\nCredenciales: Microsoft Outlook (correo+calendario, Graph), Google Sheets, Header Auth (Anthropic). Reemplaza REEMPLAZA_SHEET_ID y REEMPLAZA_BOOKING_URL.","height":300,"width":460},-180,-80)
add("trigger","Cada 10 min","n8n-nodes-base.scheduleTrigger",1.2,{"rule":{"interval":[{"field":"cronExpression","expression":"*/10 8-19 * * 1-5"}]}},300,240)
add("getmsgs","Outlook: no leídos","n8n-nodes-base.microsoftOutlook",2,{"resource":"message","operation":"getAll","limit":15,"filtersUI":{"values":{"readStatus":"unread"}},"options":{}},520,240)
add("find","Buscar lead","n8n-nodes-base.googleSheets",4.5,{"documentId":{"__rl":True,"value":"REEMPLAZA_SHEET_ID","mode":"id"},"sheetName":{"__rl":True,"value":"Leads","mode":"name"},"filtersUI":{"values":[{"lookupColumn":"Correo","lookupValue":"={{ $json.from.emailAddress.address }}"}]},"options":{}},740,240)
# Graph disponibilidad (calendarView proximos 16 dias)
add("avail","Graph: disponibilidad","n8n-nodes-base.httpRequest",4.2,{
 "method":"GET","url":"https://graph.microsoft.com/v1.0/me/calendarView",
 "authentication":"predefinedCredentialType","nodeCredentialType":"microsoftOutlookOAuth2Api",
 "sendQuery":True,"queryParameters":{"parameters":[
   {"name":"startDateTime","value":"={{ $now.toISO() }}"},
   {"name":"endDateTime","value":"={{ $now.plus({days:16}).toISO() }}"},
   {"name":"$select","value":"start,end,showAs,subject"},
   {"name":"$top","value":"100"}]},
 "sendHeaders":True,"headerParameters":{"parameters":[{"name":"Prefer","value":"outlook.timezone=\"America/Mexico_City\""}]},
 "options":{}},960,240)
add("prep","Prep clasificación","n8n-nodes-base.code",2,code(PREP.replace("SYSTEM_PLACEHOLDER", json.dumps(SYS))),1180,240)
add("claude","Claude: Clasificar","n8n-nodes-base.httpRequest",4.2,{
 "method":"POST","url":"https://api.anthropic.com/v1/messages","authentication":"genericCredentialType","genericAuthType":"httpHeaderAuth",
 "sendHeaders":True,"headerParameters":{"parameters":[{"name":"anthropic-version","value":"2023-06-01"},{"name":"content-type","value":"application/json"}]},
 "sendBody":True,"specifyBody":"json",
 "jsonBody":"={{ JSON.stringify({ model:'claude-sonnet-5', max_tokens:1600, system: $json.system, messages:[{role:'user',content:$json.user}] }) }}","options":{}},1400,240)
add("parse","Parsear","n8n-nodes-base.code",2,code(FIRMA),1620,240)
add("ifAgenda","¿Crear evento?","n8n-nodes-base.if",2.2,{"conditions":{"options":{"caseSensitive":True,"typeValidation":"loose","version":2},"combinator":"and","conditions":[{"leftValue":"={{ $json.crear_evento }}","rightValue":"={{ true }}","operator":{"type":"boolean","operation":"true","singleValue":True}}]}},1840,240)
# Graph crear evento MS365 con Teams
EVENT_BODY = "={{ JSON.stringify({ subject: $json.reunion_titulo, body:{ contentType:'HTML', content:'<b>Agenda (20 min):</b><br>'+($json.reunion_estructura||'') }, start:{ dateTime: $json.reunion_inicio, timeZone:'America/Mexico_City' }, end:{ dateTime: $json.reunion_fin, timeZone:'America/Mexico_City' }, attendees:[{ emailAddress:{ address: $json.Correo, name: $json.Contacto }, type:'required' }], isOnlineMeeting:true, onlineMeetingProvider:'teamsForBusiness' }) }}"
add("mevent","Graph: crear evento (Teams)","n8n-nodes-base.httpRequest",4.2,{
 "method":"POST","url":"https://graph.microsoft.com/v1.0/me/events",
 "authentication":"predefinedCredentialType","nodeCredentialType":"microsoftOutlookOAuth2Api",
 "sendHeaders":True,"headerParameters":{"parameters":[{"name":"Content-Type","value":"application/json"}]},
 "sendBody":True,"specifyBody":"json","jsonBody":EVENT_BODY,"options":{}},2060,140)
add("capId","Capturar Event_Id","n8n-nodes-base.code",2,code("const d=$('Parsear').item.json; d.Event_Id=$json.id||''; d.teams_link=($json.onlineMeeting&&$json.onlineMeeting.joinUrl)||''; return [{json:d}];"),2280,140)
add("noId","Sin evento","n8n-nodes-base.code",2,code("const d=$json; if(!d.Event_Id)d.Event_Id=''; return [{json:d}];"),2060,340)
# Borrador principal (respuesta o intro al referido)
add("draft","Outlook: borrador principal","n8n-nodes-base.microsoftOutlook",2,{"resource":"draft","operation":"create","subject":"={{ $json.asunto_respuesta }}","bodyContent":"={{ $json.cuerpo_final }}","additionalFields":{"bodyContentType":"html","toRecipients":"={{ $json.destinatario }}"}},2500,240)
# Persona equivocada -> nuevo lead + agradecer
add("ifRef","¿Persona equivocada?","n8n-nodes-base.if",2.2,{"conditions":{"options":{"caseSensitive":True,"typeValidation":"loose","version":2},"combinator":"and","conditions":[{"leftValue":"={{ $json.persona_equivocada }}","rightValue":"={{ true }}","operator":{"type":"boolean","operation":"true","singleValue":True}}]}},2720,240)
add("newlead","Crear lead referido","n8n-nodes-base.googleSheets",4.5,{"operation":"append","documentId":{"__rl":True,"value":"REEMPLAZA_SHEET_ID","mode":"id"},"sheetName":{"__rl":True,"value":"Leads","mode":"name"},"columns":{"mappingMode":"defineBelow","value":{
 "ID_Lead":"={{ 'L-REF-' + ($json.conversationId||$json.msg_id||'').toString().slice(-8) }}","Empresa":"={{ $json.Empresa }}","Micro_ICP":"={{ $json.Micro_ICP }}","Sector":"={{ $json.Sector }}","Pais":"={{ $json.Pais }}",
 "Contacto":"={{ $json.decisor.nombre }}","Cargo":"={{ $json.decisor.cargo }}","Correo":"={{ $json.decisor.correo }}","Decisor_Mapeado":"si","Estado":"no_contactado","Etapa":"Primer contacto",
 "Trigger_Regulatorio":"={{ $json.Trigger_Regulatorio }}","Gancho":"={{ $json.Gancho }}","Num_Toques":0,"Canal":"correo","Fuente":"={{ 'Referido por ' + ($json.quien_refirio||$json.Contacto) + ' (' + $json.Empresa + ')' }}","Notas":"referido desde lead " + "={{ $json.ID_Lead }}"}},"options":{}},2940,140)
add("thanks","Outlook: agradecer referidor","n8n-nodes-base.microsoftOutlook",2,{"resource":"draft","operation":"create","subject":"={{ 'Gracias por el contacto — ' + $json.Empresa }}","bodyContent":"={{ $json.correo_agradecimiento || 'Gracias por dirigirme con la persona correcta, le escribo con gusto. Saludos.' }}","additionalFields":{"bodyContentType":"text","toRecipients":"={{ $json.Correo }}"}},3160,140)
add("upd","Actualizar lead","n8n-nodes-base.googleSheets",4.5,{"operation":"update","documentId":{"__rl":True,"value":"REEMPLAZA_SHEET_ID","mode":"id"},"sheetName":{"__rl":True,"value":"Leads","mode":"name"},"columns":{"mappingMode":"defineBelow","matchingColumns":["ID_Lead"],"value":{
 "ID_Lead":"={{ $json.ID_Lead }}","Estado":"={{ $json.nuevo_estado }}","Etapa":"={{ $json.nueva_etapa }}","Score_ICP":"={{ $json.nuevo_score }}","Decisor_Mapeado":"={{ $json.Decisor_Mapeado }}","Event_Id":"={{ $json.Event_Id }}","Thread_Id":"={{ $json.conversationId }}","Ultimo_Contacto":"={{ $now.toFormat('yyyy-LL-dd') }}","Fecha_Siguiente_Paso":"={{ $json.fecha_siguiente_paso }}","Canal":"={{ $json.canal_sugerido || 'correo' }}","Notas":"={{ $json.intencion + ' | ' + $json.razon + ($json.teams_link? ' | Teams: '+$json.teams_link:'') }}"}},"options":{}},3380,240)
add("markread","Outlook: marcar leído","n8n-nodes-base.microsoftOutlook",2,{"resource":"message","operation":"update","messageId":"={{ $json.msg_id }}","updateFields":{"isRead":True}},3600,240)

def conn(a,b,idx=0,out=0):
    c=flow["connections"].setdefault(a,{"main":[]})
    while len(c["main"])<=out: c["main"].append([])
    c["main"][out].append({"node":b,"type":"main","index":idx})

flow={"name":"ICP · 03 Respuestas + Agenda MS365 + Handoff (v2)","nodes":nodes,"connections":{},"settings":{"executionOrder":"v1"}}
conn("Cada 10 min","Outlook: no leídos")
conn("Outlook: no leídos","Buscar lead")
conn("Buscar lead","Graph: disponibilidad")
conn("Graph: disponibilidad","Prep clasificación")
conn("Prep clasificación","Claude: Clasificar")
conn("Claude: Clasificar","Parsear")
conn("Parsear","¿Crear evento?")
conn("¿Crear evento?","Graph: crear evento (Teams)",out=0)
conn("¿Crear evento?","Sin evento",out=1)
conn("Graph: crear evento (Teams)","Capturar Event_Id")
conn("Capturar Event_Id","Outlook: borrador principal")
conn("Sin evento","Outlook: borrador principal")
conn("Outlook: borrador principal","¿Persona equivocada?")
conn("¿Persona equivocada?","Crear lead referido",out=0)
conn("¿Persona equivocada?","Actualizar lead",out=1)
conn("Crear lead referido","Outlook: agradecer referidor")
conn("Outlook: agradecer referidor","Actualizar lead")
conn("Actualizar lead","Outlook: marcar leído")

open("/workspace/agente-icp-acces-group/sistema-n8n/n8n/03-respuestas-handoff.json","w",encoding="utf-8").write(json.dumps(flow,ensure_ascii=False,indent=2))
print("OK nodos:",len(nodes),"conexiones:",len(flow["connections"]))
