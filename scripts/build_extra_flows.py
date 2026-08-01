# -*- coding: utf-8 -*-
import json, os
BASE="/workspace/agente-icp-acces-group/sistema-n8n/n8n"

def sheets_doc(): return {"__rl":True,"value":"REEMPLAZA_SHEET_ID","mode":"id"}
def sheet_leads(): return {"__rl":True,"value":"Leads","mode":"name"}

# ---------------- 00 INGESTA ----------------
PARSE_CSV = r"""
// Parse CSV (con comillas) del MASTER_LEADS y carga solo el ARRANQUE (no_contactado).
function parseCSV(t){const rows=[];let row=[],cur='',q=false;
 for(let i=0;i<t.length;i++){const c=t[i];
  if(q){if(c=='"'){if(t[i+1]=='"'){cur+='"';i++;}else q=false;}else cur+=c;}
  else{if(c=='"')q=true;else if(c==','){row.push(cur);cur='';}else if(c=='\n'){row.push(cur);rows.push(row);row=[];cur='';}else if(c=='\r'){}else cur+=c;}}
 if(cur.length||row.length){row.push(cur);rows.push(row);}return rows;}
const txt = typeof $json==='string' ? $json : ($json.data || $json.body || '');
const rows = parseCSV(String(txt));
const head = rows.shift()||[];
const FILTRO = 'no_contactado'; // arranque; cambia a '' para cargar todo
const out=[];
for(const r of rows){ if(!r.length||!r[0]) continue; const o={}; head.forEach((h,i)=>o[h.trim()]=r[i]!==undefined?r[i]:'');
  if(FILTRO && o.Estado!==FILTRO) continue; out.push({json:o}); }
return out;
"""

ingesta = {
 "name":"ICP · 00 Ingesta de bases → Sheet (arranque)",
 "nodes":[
  {"parameters":{"content":"## 00 · Ingesta al CRM\nManual: baja MASTER_LEADS.csv (salida del motor) y agrega al Sheet solo las cuentas de ARRANQUE (Estado=no_contactado). Para carga masiva de las 26k, importa el CSV directo a Google Sheets (Archivo→Importar). Reemplaza REEMPLAZA_SHEET_ID y la URL raw si cambia la rama.","height":220,"width":460},
   "id":"n0","name":"Guía","type":"n8n-nodes-base.stickyNote","typeVersion":1,"position":[-160,-40]},
  {"parameters":{},"id":"trig","name":"Ejecutar manual","type":"n8n-nodes-base.manualTrigger","typeVersion":1,"position":[320,200]},
  {"parameters":{"method":"GET","url":"https://raw.githubusercontent.com/sanrotech369-dot/agente-icp-acces-group/claude/autonomous-sales-agent-icp-g3h1kx/salidas/MASTER_LEADS.csv","options":{"response":{"response":{"responseFormat":"text"}}}},
   "id":"http","name":"Bajar MASTER_LEADS.csv","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[540,200]},
  {"parameters":{"jsCode":PARSE_CSV},"id":"parse","name":"Parsear + filtrar arranque","type":"n8n-nodes-base.code","typeVersion":2,"position":[760,200]},
  {"parameters":{"operation":"append","documentId":sheets_doc(),"sheetName":sheet_leads(),
    "columns":{"mappingMode":"autoMapInputData","matchingColumns":["ID_Lead"]},"options":{}},
   "id":"append","name":"Agregar al Sheet","type":"n8n-nodes-base.googleSheets","typeVersion":4.5,"position":[980,200]}
 ],
 "connections":{
  "Ejecutar manual":{"main":[[{"node":"Bajar MASTER_LEADS.csv","type":"main","index":0}]]},
  "Bajar MASTER_LEADS.csv":{"main":[[{"node":"Parsear + filtrar arranque","type":"main","index":0}]]},
  "Parsear + filtrar arranque":{"main":[[{"node":"Agregar al Sheet","type":"main","index":0}]]}
 },
 "settings":{"executionOrder":"v1"}
}

# ---------------- 06 DASHBOARD SEMANAL (lunes) ----------------
METRICS = r"""
const hoy=$now.toFormat('yyyy-LL-dd');
const hace7=$now.minus({days:7}).toFormat('yyyy-LL-dd');
const leads=$('Leer Leads').all().map(i=>i.json).filter(l=>l&&l.ID_Lead);
const ds=s=>String(s||'').slice(0,10);
const by=k=>leads.reduce((a,l)=>{const v=String(l[k]||'sin');a[v]=(a[v]||0)+1;return a;},{});
const sem=leads.filter(l=>ds(l.Ultimo_Contacto)>=hace7);
const semBy=k=>sem.reduce((a,l)=>{const v=String(l[k]||'sin');a[v]=(a[v]||0)+1;return a;},{});
const enr=leads.filter(l=>String(l.Enriquecer||'').toUpperCase()==='SÍ'||String(l.Enriquecer||'').toUpperCase()==='SI').length;
const prox=leads.filter(l=>ds(l.Fecha_Siguiente_Paso)>=hoy).map(l=>({e:l.Empresa,f:ds(l.Fecha_Siguiente_Paso),icp:l.Micro_ICP})).sort((a,b)=>a.f.localeCompare(b.f)).slice(0,15);
const m={semana_del:hace7,al:hoy,total:leads.length,
 por_estado:by('Estado'),por_micro_icp:by('Micro_ICP'),por_sector:by('Sector'),
 actividad_semana:{tocados:sem.length,por_estado:semBy('Estado'),agendados:sem.filter(l=>l.Estado==='agendado').length,handoff:sem.filter(l=>l.Estado==='lead_handoff').length,respondio:sem.filter(l=>l.Estado==='respondio').length},
 cola_enriquecimiento:enr,proximos:prox};
const system=[
'<identidad>Analista comercial senior de ACCES GROUP. Dashboard EJECUTIVO SEMANAL (lunes) claro y accionable, solo con datos provistos, sin inventar.</identidad>',
'<reglas>Espanol ejecutivo. HTML simple (h2,h3,table,ul). Incluye: (1) Resumen de la semana (tocados, respuestas, agendas, handoffs), (2) Embudo por Estado, (3) Distribucion por Micro-ICP y top sectores, (4) Cola de enriquecimiento, (5) Proximos seguimientos, (6) 3 recomendaciones de Siguiente Mejor Accion priorizadas por impacto (meta $2.5M/mes, cobertura 3.3x). Sin firma.</reglas>',
'<salida>Devuelve SOLO el HTML del dashboard, sin backticks ni texto fuera del HTML.</salida>'].join('\n');
const user='Semana '+hace7+' a '+hoy+'\nMarcador (JSON):\n'+JSON.stringify(m,null,2)+'\n\nGenera el dashboard semanal en HTML.';
return [{json:{hoy,system,user}}];
"""
PARSE_REP = r"""
let text='';try{const _b=$json.content||($json.body&&$json.body.content)||[];const _t=_b.find(x=>x&&x.type==='text');text=_t?_t.text:'';}catch(e){text='';}
text=text.replace(/^```html/i,'').replace(/^```/,'').replace(/```$/,'').trim();
return [{json:{hoy:$('Calcular dashboard semanal').item.json.hoy,reporte_html:text}}];
"""
dash = {
 "name":"ICP · 06 Dashboard semanal (lunes)",
 "nodes":[
  {"parameters":{"content":"## 06 · Dashboard SEMANAL (lunes 8:00)\nCada lunes lee el CRM y arma el dashboard de la semana (tocados, respuestas, agendas, handoffs, embudo por sector/ICP, cola de enriquecimiento, proximos) + 3 recomendaciones. Borrador a Ricardo.\nCredenciales: Google Sheets, Outlook, Header Auth. Reemplaza REEMPLAZA_SHEET_ID y REEMPLAZA_TU_CORREO.","height":240,"width":460},
   "id":"n0","name":"Guía","type":"n8n-nodes-base.stickyNote","typeVersion":1,"position":[-160,-40]},
  {"parameters":{"rule":{"interval":[{"field":"cronExpression","expression":"0 8 * * 1"}]}},"id":"trig","name":"Lunes 8:00","type":"n8n-nodes-base.scheduleTrigger","typeVersion":1.2,"position":[320,220]},
  {"parameters":{"documentId":sheets_doc(),"sheetName":sheet_leads(),"options":{}},"id":"read","name":"Leer Leads","type":"n8n-nodes-base.googleSheets","typeVersion":4.5,"position":[540,220]},
  {"parameters":{"jsCode":METRICS},"id":"metrics","name":"Calcular dashboard semanal","type":"n8n-nodes-base.code","typeVersion":2,"position":[760,220]},
  {"parameters":{"method":"POST","url":"https://api.anthropic.com/v1/messages","authentication":"genericCredentialType","genericAuthType":"httpHeaderAuth","sendHeaders":True,
    "headerParameters":{"parameters":[{"name":"anthropic-version","value":"2023-06-01"},{"name":"content-type","value":"application/json"}]},
    "sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify({ model:'claude-sonnet-5', max_tokens:2200, system:$json.system, messages:[{role:'user',content:$json.user}] }) }}","options":{}},
   "id":"claude","name":"Claude: Dashboard","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[980,220]},
  {"parameters":{"jsCode":PARSE_REP},"id":"parse","name":"Preparar HTML","type":"n8n-nodes-base.code","typeVersion":2,"position":[1200,220]},
  {"parameters":{"resource":"draft","operation":"create","subject":"={{ 'Dashboard ICP ACCES — semana al ' + $json.hoy }}","bodyContent":"={{ $json.reporte_html }}","additionalFields":{"bodyContentType":"html","toRecipients":"REEMPLAZA_TU_CORREO"}},
   "id":"draft","name":"Outlook: borrador dashboard","type":"n8n-nodes-base.microsoftOutlook","typeVersion":2,"position":[1420,220]}
 ],
 "connections":{
  "Lunes 8:00":{"main":[[{"node":"Leer Leads","type":"main","index":0}]]},
  "Leer Leads":{"main":[[{"node":"Calcular dashboard semanal","type":"main","index":0}]]},
  "Calcular dashboard semanal":{"main":[[{"node":"Claude: Dashboard","type":"main","index":0}]]},
  "Claude: Dashboard":{"main":[[{"node":"Preparar HTML","type":"main","index":0}]]},
  "Preparar HTML":{"main":[[{"node":"Outlook: borrador dashboard","type":"main","index":0}]]}
 },
 "settings":{"executionOrder":"v1"}
}

for fn,obj in [("00-ingesta-bases.json",ingesta),("06-dashboard-semanal.json",dash)]:
    open(os.path.join(BASE,fn),"w",encoding="utf-8").write(json.dumps(obj,ensure_ascii=False,indent=2))
    json.load(open(os.path.join(BASE,fn)))  # valida
    print("OK",fn,"nodos",len(obj["nodes"]))
