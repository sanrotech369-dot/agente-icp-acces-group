#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor ICP · ACCES GROUP — ingesta masiva + pre-score → esquema CRM (Google Sheet Leads).
Modos:
  python motor_icp.py <archivo.md> [--hint X]      # 1 base (debug)
  python motor_icp.py --masivo <dir_bases> <seed.csv>  # todas las *_extraccion_forense.md
Emite MASTER_LEADS.csv (esquema CRM) + MASTER_RESUMEN.json. No inventa correos.
Fiel a contexto-icp.md (ICP Real v1).
"""
import sys, re, csv, unicodedata, os, glob, json
from collections import defaultdict, OrderedDict

OUT="/tmp/claude-0/-home-user-opendataloader-pdf/49cbf8ae-2e2e-5727-819e-0405ee376fff/scratchpad"

def na(x):
    x=(x or "").strip()
    return "" if x.lower() in ("no encontrado","n/a","-","") else x
def deacc(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c)!="Mn").lower()

# Palabras del GIRO real (por empresa) — señal fuerte, específica
KW=OrderedDict([
 ("ICP-1",["gasolin","estacion de servicio","estación de servicio","gasolineria","carburante","servicentro","combustibles"]),
 ("ICP-2",["banco","banca ","financ","sofom","sofipo","socap","caja popular","cooperativa de ahorro","fintech","ifpe","aseguradora","seguros","afore","casa de bolsa","medios de pago","credito","arrendadora"]),
 ("ICP-3",["confit","dulce","choc","caramelo","gomita","malvavisco","grenetina","aliment","carne","lacteo","bebida","cerveza","panific","botana","harina","manufactur","quimic","plastico","farmac","cosmetic","empaque","envase","maquila","metalmecan","siderur","autopart","fundicion","textil"]),
 ("OBS-LOG",["transporte","logist","mensajer","paqueter","autotransporte","fletes","transportista"]),
 ("OBS-AUTO",["automotive","automotriz","autopartes agencia","concesionar","agencia de autos","movilidad"]),
 ("OBS-TUR",["hotel","turism","hospedaje","restaurant"]),
 ("NEW-CONSTRUCCION",["construc","obra civil","edificac","inmobili","ferreter","muebl"]),
 ("NEW-MINERIA",["miner"]),
 ("NEW-ENERGIA",["electric","energia","subestacion","fotovolt","petroleo","hidrocarbur","exploracion y produccion"]),
])
# Sector conocido por BASE (fallback SOLO cuando el giro no dice nada). Curado por nombre de archivo.
BASE_SECTOR=[
 ("gasolineras",     "ICP-1"), ("gas-stations","ICP-1"),
 ("confiteria",      "ICP-3"), ("confiterias","ICP-3"), ("carnes-y-lacteos","ICP-3"),
 ("alimentria",      "ICP-3"), ("foodi","ICP-3"), ("farmaceutica","ICP-3"),
 ("quimicos","ICP-3"),("poliplast","ICP-3"),("expocerveza","ICP-3"),("femsa","ICP-3"),
 ("maquiladoras","ICP-3"),("parque-industrial","ICP-3"),("industrial","ICP-3"),
 ("copayment",       "ICP-2"),
 ("automotive","OBS-AUTO"),("movilidad","OBS-AUTO"),("amap","OBS-AUTO"),
 ("transportistas","OBS-LOG"),("logistics","OBS-LOG"),
 ("hoteles","OBS-TUR"),("estancias","OBS-TUR"),
 ("construccion","NEW-CONSTRUCCION"),("construshow","NEW-CONSTRUCCION"),
 ("ferreshow","NEW-CONSTRUCCION"),("muebler","NEW-CONSTRUCCION"),
 ("minero","NEW-MINERIA"),("mem2020","NEW-MINERIA"),
 ("electrica","NEW-ENERGIA"),("petroleo","NEW-ENERGIA"),("exploracion","NEW-ENERGIA"),
]
def base_sector(hint):
    h=deacc(hint or "")
    for kw,code in BASE_SECTOR:
        if kw in h: return code
    return "OTRO"
def detect_sector(giro,hint):
    g=deacc(giro or "")
    # 1) el GIRO manda (verdad por empresa)
    for code,kws in KW.items():
        for kw in kws:
            if deacc(kw) in g: return code
    # 2) si el giro no dice nada, usa el sector conocido de la base
    return base_sector(hint)

MICRO={
 "ICP-1":(30,30,"ICP-1","Gasolineras / Energía retail","Anexo 21 SAT",
   "El SAT ya no pide papeles, pide evidencia técnica. ¿Su estación pasaría hoy la prueba de seguridad anual del Anexo 21?"),
 "ICP-2":(27,27,"ICP-2","Financiero regulado","CNBV",
   "La CNBV pide evidencia, no políticas. ¿Ya tiene agendados sus 2 pentest del año con reporte auditable?"),
 "ICP-3":(24,15,"ICP-3","Manufactura / Alimentos / Confitería","Auditoría de cliente",
   "Sus clientes globales ya auditan a sus proveedores. ¿Puede demostrar sus controles cuando se los pidan?"),
 "OBS-LOG":(15,0,"OBSERVACION","Logística / Transporte","",""),
 "OBS-AUTO":(15,0,"OBSERVACION","Automotriz / Movilidad","",""),
 "OBS-TUR":(15,0,"OBSERVACION","Turismo / Hotelería","",""),
 "NEW-CONSTRUCCION":(5,0,"NUEVO","Construcción [por robustecer]","",""),
 "NEW-MINERIA":(5,0,"NUEVO","Minería [por robustecer]","",""),
 "NEW-ENERGIA":(5,0,"NUEVO","Energía / Hidrocarburos [por robustecer]","",""),
 "OTRO":(5,0,"OTRO","Multisector [segmentar]","",""),
}
OBSERVACION={"OBS-LOG","OBS-AUTO","OBS-TUR"}
OCCIDENTE={"jalisco"}
FREE=("hotmail","gmail","yahoo","outlook","live.com","prodigy","aol","infosel","att.net","starmedia","webtelmex","podernet","icloud","msn","mail.udg")
DECISOR=("director","directora","gerente","dueñ","duen","propietari","socio","presidente","ceo","cfo","cio","ciso","fundador","administrador","titular","jefe")
TECH=("sistemas","tecnolog","seguridad","informatic"," ti "," t.i")

ANTIICP=("bbva","bancomer","banorte","santander","banamex","citibanam","hsbc","scotiabank",
 "gnp","axa","metlife","mapfre","qualitas","pwc","pricewaterhouse","deloitte","kpmg","ernst",
 "mancera","accenture","ibm","oracle","microsoft","femsa","bimbo","coca","pepsi","nestle",
 "unilever","procter","bosch","siemens","general electric","3m","cemex","grupo financiero",
 "bursatil","casa de bolsa","afore")
def is_antiicp(name):
    n=deacc(name)
    return any(w in n for w in ANTIICP)
def norm_company(name):
    n=deacc(name)
    n=re.sub(r"\b(s\.?a\.?b?\.?|de|c\.?v\.?|s\.? de r\.?l\.?|sc|sa|cv|the)\b"," ",n)
    n=re.sub(r"[^a-z0-9 ]"," ",n); return re.sub(r"\s+"," ",n).strip()
def email_estado(mail,vet):
    if not mail: return "faltante"
    if vet: return "vetado_2003"
    dom=mail.split("@")[-1].lower()
    return "generico" if any(f in dom for f in FREE) else "ok"

def parse_rows(path):
    rows=[]
    with open(path,encoding="utf-8",errors="replace") as fh:
        for line in fh:
            if not line.startswith("| "): continue
            if "Empresa / razón social" in line or re.match(r"^\|\s*---",line): continue
            safe=line.rstrip("\n").replace("\\|"," ")
            parts=[p.strip() for p in safe.split("|")]
            if len(parts)<19: continue
            rows.append(parts[1:19])
    return rows

def calificar_archivo(path,hint=""):
    vet = "gasolineras-en-mexico" in deacc(path) or "gas-stations" in deacc(path)
    comp=OrderedDict()
    for c in parse_rows(path):
        v=[na(x) for x in c[:18]]
        empresa,com,giro,contacto,cargo,area,correo,telf,cel,web,dirn,ciudad,estado,pais,fuente,pag,evid,obs=v
        if not empresa: continue
        k=norm_company(empresa)
        if not k or len(k)<3: continue
        d=comp.setdefault(k,dict(empresa=empresa,giro=giro,contactos=[],correos=set(),tels=set(),
              web=web,ciudad=ciudad,estado=estado,pais=pais or "México",fuente=os.path.basename(path),obs=set()))
        for fld,key in ((giro,"giro"),(web,"web"),(estado,"estado"),(ciudad,"ciudad")):
            if fld and not d[key]: d[key]=fld
        if correo: d["correos"].add(correo)
        if telf: d["tels"].add(telf)
        if cel: d["tels"].add(cel)
        if obs: d["obs"].add(obs)
        if contacto or cargo: d["contactos"].append((contacto,cargo,correo))
    res=[]
    for k,d in comp.items():
        sec=detect_sector(d["giro"],hint)
        sw,rw,micro,secname,trig,gancho=MICRO[sec]
        big=any(w in deacc(d["empresa"]) for w in ("grupo","industrias","corporativ","s.a.b"))
        tam=10 if big else 5
        est=deacc(d["estado"])
        geo=10 if est in OCCIDENTE else (7 if ("mexic" in deacc(d["pais"]) and est) else (3 if d["pais"] and "mexic" not in deacc(d["pais"]) else 5))
        allc=deacc(" ".join(f"{c} {p}" for c,p,_ in d["contactos"])); obt=deacc(" ".join(d["obs"]))
        senal=6 if (any(t in allc for t in TECH) or any(t in allc for t in DECISOR) or "posible decisor" in obt) else 2
        score=sw+rw+tam+geo+senal
        if sec in OBSERVACION or sec=="OTRO" or sec.startswith("NEW"): score=min(score,65)
        corp=[m for m in d["correos"] if email_estado(m,vet)=="ok"]
        mail=corp[0] if corp else (sorted(d["correos"])[0] if d["correos"] else "")
        est_mail=email_estado(mail,vet)
        bc=("","")
        for c,p,m in d["contactos"]:
            if any(t in deacc(p) for t in DECISOR): bc=(c,p); break
        if bc==("","") and d["contactos"]: bc=d["contactos"][0][:2]
        enr = est_mail in ("faltante","vetado_2003") or (est_mail=="generico" and not corp)
        res.append(dict(key=k,empresa=d["empresa"],antiicp=is_antiicp(d["empresa"]),sector_code=sec,micro=micro,sector=secname,
            trigger=trig,gancho=gancho,pre_score=score,contacto=bc[0],cargo=bc[1],correo=mail,
            correo_estado=est_mail,enriquecer=enr,tel=(sorted(d["tels"])[0] if d["tels"] else ""),
            web=d["web"],ciudad=d["ciudad"],estado_region=d["estado"],pais=d["pais"],
            fuente=d["fuente"],n_contactos=len(d["contactos"])))
    return res

CRM_COLS=["ID_Lead","Empresa","Micro_ICP","Sector","Pais","Contacto","Cargo","Correo",
 "Decisor_Mapeado","Pre_Score","Score_ICP","Estado","Etapa","Trigger_Regulatorio","Gancho",
 "Cadencia_Paso","Ultimo_Contacto","Fecha_Siguiente_Paso","Num_Toques","Canal","Fuente",
 "Thread_Id","Event_Id","Asunto","Notas","Correo_Estado","Enriquecer","Telefono","Ciudad","Estado_Region"]

def to_crm(r,idn):
    score=r["pre_score"]
    if score>=70: estado,etapa,canal="no_contactado","Primer contacto","correo"
    elif score>=50: estado,etapa,canal="pendiente","Fabricación","correo"
    else: estado,etapa,canal="nurturing","Fabricación","correo"
    if r["enriquecer"]:
        canal="investigación";
        if estado=="no_contactado": estado="pendiente"; etapa="Fabricación"
    notas=[]
    if r.get("antiicp"): estado,etapa="descartado","Anti-ICP"; notas.append("[ANTI-ICP: corporativo global → nurturing/Tier1]")
    if r["enriquecer"]: notas.append(f"[ENRIQUECER: correo {r['correo_estado']}]")
    if r["sector_code"].startswith("NEW"): notas.append("[SECTOR NUEVO: robustecer con EXPLORA MERCADOS]")
    if r["n_contactos"]>1: notas.append(f"{r['n_contactos']} contactos en base (multithreading)")
    return {"ID_Lead":idn,"Empresa":r["empresa"],"Micro_ICP":r["micro"],"Sector":r["sector"],
      "Pais":r["pais"],"Contacto":r["contacto"],"Cargo":r["cargo"],"Correo":r["correo"],
      "Decisor_Mapeado":"no","Pre_Score":score,"Score_ICP":"","Estado":estado,"Etapa":etapa,
      "Trigger_Regulatorio":r["trigger"],"Gancho":r["gancho"],"Cadencia_Paso":0,
      "Ultimo_Contacto":"","Fecha_Siguiente_Paso":"","Num_Toques":0,"Canal":canal,
      "Fuente":r["fuente"],"Thread_Id":"","Event_Id":"","Asunto":"","Notas":" · ".join(notas),
      "Correo_Estado":r["correo_estado"],"Enriquecer":"SÍ" if r["enriquecer"] else "no",
      "Telefono":r["tel"],"Ciudad":r["ciudad"],"Estado_Region":r["estado_region"]}

def masivo(bases_dir,seed_csv):
    seed=set()
    if os.path.exists(seed_csv):
        with open(seed_csv,encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                seed.add(norm_company(row.get("Empresa","")))
    files=sorted(glob.glob(os.path.join(bases_dir,"*_extraccion_forense*.md")))
    merged=OrderedDict(); ya_seed=0; procesados=0
    for path in files:
        hint=re.sub(r"^[0-9]+-","",os.path.basename(path)).replace("_extraccion_forense","").replace(".md","")
        try: rows=calificar_archivo(path,hint)
        except Exception as e: print("  ! error",os.path.basename(path),e); continue
        procesados+=1
        for r in rows:
            if r["key"] in seed: ya_seed+=1; continue
            if r["key"] in merged:
                m=merged[r["key"]]
                if r["pre_score"]>m["pre_score"]: r["fuente"]=m["fuente"]+"; "+r["fuente"]; merged[r["key"]]=r
                else: m["fuente"]=m["fuente"]+"; "+r["fuente"]
            else: merged[r["key"]]=r
    allleads=sorted(merged.values(),key=lambda x:-x["pre_score"])
    activos=[r for r in allleads if r["sector_code"]!="OTRO"]
    reserva=[r for r in allleads if r["sector_code"]=="OTRO"]
    rows_crm=[to_crm(r,f"L-{1001+i}") for i,r in enumerate(activos)]
    csvp=os.path.join(OUT,"MASTER_LEADS.csv")
    with open(csvp,"w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=CRM_COLS); w.writeheader()
        for r in rows_crm: w.writerow(r)
    # reserva (multisector genérico) → solo para segmentar después
    with open(os.path.join(OUT,"MASTER_RESERVA.csv"),"w",newline="",encoding="utf-8") as fh:
        w=csv.writer(fh); w.writerow(["Empresa","Correo","Ciudad","Estado","Fuente"])
        for r in reserva: w.writerow([r["empresa"],r["correo"],r["ciudad"],r["estado_region"],r["fuente"]])
    print(f"\n[Reserva multisector genérica (a segmentar): {len(reserva)} empresas → MASTER_RESERVA.csv]")
    # resumen
    by_micro=defaultdict(int); by_sec=defaultdict(int); by_est=defaultdict(int); enr=0; abordar=0; anti=0; arranque=0
    for r in rows_crm:
        by_micro[r["Micro_ICP"]]+=1; by_sec[r["Sector"]]+=1; by_est[r["Estado"]]+=1
        if r["Enriquecer"]=="SÍ": enr+=1
        if r["Estado"]=="descartado": anti+=1
        if r["Estado"]=="no_contactado": abordar+=1
        if r["Estado"]=="no_contactado" and r["Correo_Estado"]=="ok" and r["Contacto"]: arranque+=1
    print(f"\n>>> LISTA DE ARRANQUE (listos YA: ≥70 + correo corporativo + contacto): {arranque}")
    print(f">>> Anti-ICP descartados (corporativo global): {anti}")
    print(f"\n===== INGESTA MASIVA =====")
    print(f"Bases forenses procesadas: {procesados}/{len(files)}")
    print(f"Empresas únicas calificadas: {len(rows_crm)}")
    print(f"Ya en tu bitácora (excluidas para no re-contactar): {ya_seed}")
    print(f"Requieren ENRIQUECIMIENTO de correo: {enr}  ({100*enr//max(1,len(rows_crm))}%)")
    print(f"ABORDAR YA (pre-score ≥70): {abordar}")
    print("\nPor micro-ICP:")
    for k,v in sorted(by_micro.items(),key=lambda x:-x[1]): print(f"  {v:6d}  {k}")
    print("\nPor estado inicial:")
    for k,v in sorted(by_est.items(),key=lambda x:-x[1]): print(f"  {v:6d}  {k}")
    print("\nTop 12 sectores (por # empresas):")
    for k,v in sorted(by_sec.items(),key=lambda x:-x[1])[:12]: print(f"  {v:6d}  {k}")
    print(f"\nTOP 15 leads listos (correo OK, mayor pre-score):")
    shown=0
    for r in rows_crm:
        if r["Estado"]!="descartado" and r["Correo_Estado"]=="ok" and r["Contacto"]:
            print(f"  {r['Pre_Score']:3d} [{r['Micro_ICP']:<11}] {r['Empresa'][:34]:<34} | {r['Cargo'][:16]:<16} | {r['Correo'][:30]}")
            shown+=1
            if shown>=15: break
    stats=dict(bases=procesados,empresas=len(rows_crm),ya_seed=ya_seed,enriquecer=enr,
        abordar=abordar,por_micro=dict(by_micro),por_estado=dict(by_est),por_sector=dict(by_sec),csv=csvp)
    json.dump(stats,open(os.path.join(OUT,"MASTER_RESUMEN.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print(f"\nCSV maestro -> {csvp}")

if __name__=="__main__":
    if "--masivo" in sys.argv:
        i=sys.argv.index("--masivo"); masivo(sys.argv[i+1],sys.argv[i+2])
    else:
        path=sys.argv[1]; hint=sys.argv[sys.argv.index("--hint")+1] if "--hint" in sys.argv else ""
        for r in calificar_archivo(path,hint)[:20]: print(r["pre_score"],r["micro"],r["empresa"])
