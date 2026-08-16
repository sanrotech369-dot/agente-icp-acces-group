# -*- coding: utf-8 -*-
import json, os
BASE="/workspace/agente-icp-acces-group/sistema-n8n/n8n"
def doc(): return {"__rl":True,"value":"REEMPLAZA_SHEET_ID","mode":"id"}
def tab(n): return {"__rl":True,"value":n,"mode":"name"}
def claude_node(nid,name,x,y,maxtok=1200):
    return {"parameters":{"method":"POST","url":"https://api.anthropic.com/v1/messages","authentication":"genericCredentialType","genericAuthType":"httpHeaderAuth","sendHeaders":True,
      "headerParameters":{"parameters":[{"name":"anthropic-version","value":"2023-06-01"},{"name":"content-type","value":"application/json"}]},
      "sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify({ model:'claude-sonnet-5', max_tokens:"+str(maxtok)+", system:$json.system, messages:[{role:'user',content:$json.user}] }) }}","options":{}},
      "id":nid,"name":name,"type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[x,y]}
def serper_node(nid,name,x,y):
    return {"parameters":{"method":"POST","url":"https://google.serper.dev/search","sendHeaders":True,
      "headerParameters":{"parameters":[{"name":"X-API-KEY","value":"REEMPLAZA_SERPER_KEY"},{"name":"Content-Type","value":"application/json"}]},
      "sendBody":True,"specifyBody":"json","jsonBody":"={{ JSON.stringify({ q: $json.query, gl:'mx', hl:'es', num:10 }) }}","options":{}},
      "id":nid,"name":name,"type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[x,y]}

# ================= 07 ENRIQUECIMIENTO =================
PREP07 = r"""
const l=$json;
const query = `${l.Empresa} ${l.Ciudad||''} ${l.Estado_Region||''} contacto correo director gerente`;
return [{json:{...l, query}}];
"""
EXTRACT07 = r"""
const res = $json; const org = (res.organic||[]).slice(0,8).map(o=>({t:o.title,l:o.link,s:o.snippet}));
const l = $('Prep búsqueda').item.json;
const system=[
'<identidad>Investigador OSINT B2B de ACCES GROUP. Extrae SOLO datos de contacto verificables de los resultados. NO inventes correos ni adivines patrones.</identidad>',
'<reglas>Prefiere dominio corporativo propio. Si solo hay dominio (sin correo), sugiere canal (sitio/telefono/LinkedIn) pero marca correo="" y encontrado=false para correo. Da confianza 0-100 y la URL fuente.</reglas>',
'<salida>SOLO JSON: {"correo":"","telefono":"","web":"","linkedin":"","fuente_url":"","confianza":0,"encontrado":false,"nota":""}</salida>'].join('\n');
const user = `Empresa: ${l.Empresa} | Ciudad: ${l.Ciudad||''} ${l.Estado_Region||''}\nResultados de busqueda:\n${JSON.stringify(org,null,1)}\n\nExtrae el mejor canal de contacto verificable. Devuelve solo el JSON.`;
return [{json:{...l, system, user}}];
"""
UPD07 = r"""
let d={};try{const _b=$json.content||[];const _t=_b.find(x=>x&&x.type==='text');d=JSON.parse((_t?_t.text:'{}').replace(/^```json/i,'').replace(/```$/,'').trim());}catch(e){d={encontrado:false};}
const l=$('Extraer contacto').item.json;
const found=!!(d.correo&&d.correo.includes('@'));
return [{json:{ID_Lead:l.ID_Lead,
 Correo: found? d.correo : (l.Correo||''),
 Telefono: d.telefono||l.Telefono||'',
 Web: d.web||l.Web||'',
 Correo_Estado: found?'ok':(l.Correo_Estado||'faltante'),
 Enriquecer: found?'no':'SÍ',
 Estado: found?'no_contactado':(l.Estado||'pendiente'),
 Notas: (l.Notas||'')+` | enriquecido ${found?('OK '+d.confianza+'% '+(d.fuente_url||'')):('sin correo; '+(d.nota||'')+' '+(d.linkedin||''))}`
}}];
"""
enr={"name":"ICP · 07 Enriquecimiento de contactos (autónomo)","nodes":[
 {"parameters":{"content":"## 07 · Enriquecimiento (autónomo)\nDiario: toma leads con Enriquecer=SÍ, busca en web (Serper) el canal real, Claude extrae SOLO lo verificable (no inventa), actualiza el CRM y RE-ENCOLA (Estado=no_contactado) al encontrar correo.\nCredenciales: Google Sheets, Header Auth (Anthropic), Serper (X-API-KEY). Reemplaza REEMPLAZA_SHEET_ID y REEMPLAZA_SERPER_KEY.","height":240,"width":470},"id":"n0","name":"Guía","type":"n8n-nodes-base.stickyNote","typeVersion":1,"position":[-160,-60]},
 {"parameters":{"rule":{"interval":[{"field":"cronExpression","expression":"0 7 * * 1-5"}]}},"id":"t","name":"Cada día 7:00","type":"n8n-nodes-base.scheduleTrigger","typeVersion":1.2,"position":[300,200]},
 {"parameters":{"documentId":doc(),"sheetName":tab("Leads"),"filtersUI":{"values":[{"lookupColumn":"Enriquecer","lookupValue":"SÍ"}]},"options":{}},"id":"read","name":"Leads a enriquecer","type":"n8n-nodes-base.googleSheets","typeVersion":4.5,"position":[520,200]},
 {"parameters":{"maxItems":20},"id":"limit","name":"Máx 20/día","type":"n8n-nodes-base.limit","typeVersion":1,"position":[740,200]},
 {"parameters":{"jsCode":PREP07},"id":"prep","name":"Prep búsqueda","type":"n8n-nodes-base.code","typeVersion":2,"position":[940,200]},
 serper_node("serp","Buscar en web (Serper)",1140,200),
 {"parameters":{"jsCode":EXTRACT07},"id":"ext","name":"Extraer contacto","type":"n8n-nodes-base.code","typeVersion":2,"position":[1340,200]},
 claude_node("cl","Claude: Extraer",1540,200,900),
 {"parameters":{"jsCode":UPD07},"id":"map","name":"Mapear update","type":"n8n-nodes-base.code","typeVersion":2,"position":[1740,200]},
 {"parameters":{"operation":"update","documentId":doc(),"sheetName":tab("Leads"),"columns":{"mappingMode":"defineBelow","matchingColumns":["ID_Lead"],"value":{
   "ID_Lead":"={{ $json.ID_Lead }}","Correo":"={{ $json.Correo }}","Telefono":"={{ $json.Telefono }}","Web":"={{ $json.Web }}","Correo_Estado":"={{ $json.Correo_Estado }}","Enriquecer":"={{ $json.Enriquecer }}","Estado":"={{ $json.Estado }}","Notas":"={{ $json.Notas }}"}},"options":{}},"id":"upd","name":"Actualizar CRM","type":"n8n-nodes-base.googleSheets","typeVersion":4.5,"position":[1940,200]}
],"connections":{
 "Cada día 7:00":{"main":[[{"node":"Leads a enriquecer","type":"main","index":0}]]},
 "Leads a enriquecer":{"main":[[{"node":"Máx 20/día","type":"main","index":0}]]},
 "Máx 20/día":{"main":[[{"node":"Prep búsqueda","type":"main","index":0}]]},
 "Prep búsqueda":{"main":[[{"node":"Buscar en web (Serper)","type":"main","index":0}]]},
 "Buscar en web (Serper)":{"main":[[{"node":"Extraer contacto","type":"main","index":0}]]},
 "Extraer contacto":{"main":[[{"node":"Claude: Extraer","type":"main","index":0}]]},
 "Claude: Extraer":{"main":[[{"node":"Mapear update","type":"main","index":0}]]},
 "Mapear update":{"main":[[{"node":"Actualizar CRM","type":"main","index":0}]]}
},"settings":{"executionOrder":"v1"}}

# ================= 08 EXPLORA MERCADOS =================
PREP08 = r"""
const s=$json;
const query = `${s.Sector} Mexico ciberseguridad incidentes regulacion 2025 2026 madurez continuidad`;
return [{json:{...s, query}}];
"""
FICHA08 = r"""
const res=$json; const org=(res.organic||[]).slice(0,8).map(o=>({t:o.title,l:o.link,s:o.snippet}));
const s=$('Prep sector').item.json;
const system=[
'<identidad>Analista de inteligencia sectorial de ACCES GROUP (ciberseguridad/GRC/continuidad). Construyes fichas de sector para calificar cuentas, con el estilo de INTELIGENCIA_SECTORES.md: por que es prioritario, subsectores/urgencia, drivers regulatorios con fecha, dolores->solucion ACCES->gancho, interlocutores, tickets, triggers de compra. Solo con lo provisto + conocimiento del portafolio ACCES. Sin inventar cifras sin fuente.</identidad>',
'<portafolio>Auditoria, Pentesting, SOC/NOC as a Service, CISO as a Service, gestion de terceros, BIA/BCP/DRP, seguridad cloud/APIs, DevSecOps, respuesta a incidentes, concientizacion, administrados 24x7, gobierno IT/OT, ISO 27001.</portafolio>',
'<reglas>Gancho consultivo = impacto al NEGOCIO (multa, paro, auditoria, licencia), no miedo tecnico. Da un PESO sugerido 0-30 para el pre-score del sector y su justificacion. Marca fechas regulatorias vivas.</reglas>',
'<salida>SOLO JSON: {"sector":"","peso_sugerido":0,"por_que_prioritario":"","subsectores":"","drivers_regulatorios":"","dolores_solucion_gancho":"","interlocutores":"","triggers_compra":"","ficha_md":"","fuentes":[]}</salida>'].join('\n');
const user=`Sector a robustecer: ${s.Sector}\nResultados de busqueda:\n${JSON.stringify(org,null,1)}\n\nEscribe la ficha de inteligencia del sector (ficha_md en Markdown lista para pegar en INTELIGENCIA_SECTORES.md). Devuelve solo el JSON.`;
return [{json:{...s, system, user}}];
"""
MAP08 = r"""
let d={};try{const _b=$json.content||[];const _t=_b.find(x=>x&&x.type==='text');d=JSON.parse((_t?_t.text:'{}').replace(/^```json/i,'').replace(/```$/,'').trim());}catch(e){d={};}
const s=$('Ficha sector').item.json;
return [{json:{Sector:s.Sector,Peso:d.peso_sugerido||5,Estado:'robustecido',
 Resumen:(d.por_que_prioritario||'').slice(0,400),
 Ficha_md:d.ficha_md||'',
 Fuentes:(d.fuentes||[]).join(' | '),
 asunto:'Ficha de sector — '+s.Sector,
 cuerpo:'<h2>Ficha: '+s.Sector+'</h2><pre style="white-space:pre-wrap;font-family:inherit">'+(d.ficha_md||'').replace(/</g,'&lt;')+'</pre>'}}];
"""
exp={"name":"ICP · 08 EXPLORA MERCADOS (investiga sectores nuevos)","nodes":[
 {"parameters":{"content":"## 08 · EXPLORA MERCADOS\nToma sectores con Estado=por_robustecer (tab 'Sectores'), investiga en web (Serper), Claude escribe la FICHA estilo INTELIGENCIA_SECTORES.md con peso sugerido, y guarda ficha+peso en el Sheet + borrador a Ricardo para revisar y pegar en el .md.\nCredenciales: Google Sheets, Header Auth, Serper. Crea la pestaña 'Sectores' con columnas: Sector, Estado, Peso, Resumen, Ficha_md, Fuentes. Semilla: Construccion, Mineria, Energia, Automotriz, Turismo, Logistica.","height":260,"width":480},"id":"n0","name":"Guía","type":"n8n-nodes-base.stickyNote","typeVersion":1,"position":[-160,-60]},
 {"parameters":{},"id":"t","name":"Ejecutar manual","type":"n8n-nodes-base.manualTrigger","typeVersion":1,"position":[300,200]},
 {"parameters":{"documentId":doc(),"sheetName":tab("Sectores"),"filtersUI":{"values":[{"lookupColumn":"Estado","lookupValue":"por_robustecer"}]},"options":{}},"id":"read","name":"Sectores por robustecer","type":"n8n-nodes-base.googleSheets","typeVersion":4.5,"position":[520,200]},
 {"parameters":{"jsCode":PREP08},"id":"prep","name":"Prep sector","type":"n8n-nodes-base.code","typeVersion":2,"position":[740,200]},
 serper_node("serp","Buscar en web (Serper)",940,200),
 {"parameters":{"jsCode":FICHA08},"id":"fi","name":"Ficha sector","type":"n8n-nodes-base.code","typeVersion":2,"position":[1140,200]},
 claude_node("cl","Claude: Ficha de sector",1340,200,2200),
 {"parameters":{"jsCode":MAP08},"id":"map","name":"Mapear ficha","type":"n8n-nodes-base.code","typeVersion":2,"position":[1540,200]},
 {"parameters":{"operation":"update","documentId":doc(),"sheetName":tab("Sectores"),"columns":{"mappingMode":"defineBelow","matchingColumns":["Sector"],"value":{
   "Sector":"={{ $json.Sector }}","Estado":"robustecido","Peso":"={{ $json.Peso }}","Resumen":"={{ $json.Resumen }}","Ficha_md":"={{ $json.Ficha_md }}","Fuentes":"={{ $json.Fuentes }}"}},"options":{}},"id":"upd","name":"Guardar ficha","type":"n8n-nodes-base.googleSheets","typeVersion":4.5,"position":[1740,120]},
 {"parameters":{"resource":"draft","operation":"create","subject":"={{ $json.asunto }}","bodyContent":"={{ $json.cuerpo }}","additionalFields":{"bodyContentType":"html","toRecipients":"REEMPLAZA_TU_CORREO"}},"id":"draft","name":"Outlook: borrador ficha","type":"n8n-nodes-base.microsoftOutlook","typeVersion":2,"position":[1740,300]}
],"connections":{
 "Ejecutar manual":{"main":[[{"node":"Sectores por robustecer","type":"main","index":0}]]},
 "Sectores por robustecer":{"main":[[{"node":"Prep sector","type":"main","index":0}]]},
 "Prep sector":{"main":[[{"node":"Buscar en web (Serper)","type":"main","index":0}]]},
 "Buscar en web (Serper)":{"main":[[{"node":"Ficha sector","type":"main","index":0}]]},
 "Ficha sector":{"main":[[{"node":"Claude: Ficha de sector","type":"main","index":0}]]},
 "Claude: Ficha de sector":{"main":[[{"node":"Mapear ficha","type":"main","index":0}]]},
 "Mapear ficha":{"main":[[{"node":"Guardar ficha","type":"main","index":0},{"node":"Outlook: borrador ficha","type":"main","index":0}]]}
},"settings":{"executionOrder":"v1"}}

for fn,obj in [("07-enriquecimiento.json",enr),("08-explora-mercados.json",exp)]:
    open(os.path.join(BASE,fn),"w",encoding="utf-8").write(json.dumps(obj,ensure_ascii=False,indent=2))
    d=json.load(open(os.path.join(BASE,fn)))
    names={n["name"] for n in d["nodes"]}
    for a,c in d["connections"].items():
        assert a in names
        for g in c["main"]:
            for e in g: assert e["node"] in names, e["node"]
    print("OK",fn,"nodos",len(obj["nodes"]))
