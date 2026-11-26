"""Spike ENTSO-E (jetable). Jeton lu dans source/entsoe_token ou $ENTSOE_TOKEN, jamais écrit.
Usage : python spike_entsoe.py  -> cache XML dans le dossier donné par $ENTSOE_CACHE."""
import os, re, sys, time, hashlib, urllib.request, urllib.error, xml.etree.ElementTree as ET
from pathlib import Path
RACINE = Path(__file__).resolve().parents[2]
TOKEN = os.environ.get("ENTSOE_TOKEN") or (RACINE / "source/entsoe_token").read_text().strip()
CACHE = Path(os.environ.get("ENTSOE_CACHE", "/tmp/entsoe_cache")); CACHE.mkdir(parents=True, exist_ok=True)
B = "https://web-api.tp.entsoe.eu/api"
ZONES = {"FR": "10YFR-RTE------C", "BE": "10YBE----------2", "DE-LU": "10Y1001A1001A82H", "ES": "10YES-REE------0",
         "IT-Nord": "10Y1001A1001A73I", "CH": "10YCH-SWISSGRIDZ", "GB": "10YGB----------A", "DE": "10Y1001A1001A83F",
         "NL": "10YNL----------L", "IT": "10YIT-GRTN-----B"}

def get(params, tag=None):
    """Retourne (code, texte, secondes). Le jeton est ajouté ici et jamais journalisé."""
    cle = hashlib.md5(repr(sorted(params.items())).encode()).hexdigest()
    f = CACHE / (cle + ".xml")
    if f.exists():
        return 200, f.read_text(), 0.0
    url = B + "?" + "&".join(f"{k}={v}" for k, v in params.items()) + f"&securityToken={TOKEN}"
    t = time.time()
    try:
        r = urllib.request.urlopen(url, timeout=120); code = r.status; txt = r.read().decode()
    except urllib.error.HTTPError as e:
        code = e.code; txt = e.read().decode()
    dt = time.time() - t
    if code == 200: f.write_text(txt)
    return code, txt, dt

def resume(txt):
    """Résumé par TimeSeries : résolutions, nb de points, positions manquantes, bornes."""
    txt = re.sub(r' xmlns="[^"]+"', "", txt, count=1)
    rac = ET.fromstring(txt)
    if rac.tag == "Acknowledgement_MarketDocument":
        return {"ack": rac.findtext("Reason/text"), "code": rac.findtext("Reason/code")}
    out = []
    for ts in rac.findall("TimeSeries"):
        d = {"psr": ts.findtext("MktPSRType/psrType"), "in": ts.findtext("in_Domain.mRID"), "out": ts.findtext("out_Domain.mRID"),
             "curve": ts.findtext("curveType"), "unit": ts.findtext("quantity_Measure_Unit.name") or ts.findtext("price_Measure_Unit.name"),
             "cur": ts.findtext("currency_Unit.name"), "conso": ts.find("outBiddingZone_Domain.mRID") is not None,
             "res": set(), "n": 0, "manque": 0, "debut": None, "fin": None}
        for p in ts.findall("Period"):
            res = p.findtext("resolution"); d["res"].add(res)
            pts = [int(x.findtext("position")) for x in p.findall("Point")]
            if pts:
                d["n"] += len(pts); d["manque"] += max(pts) - len(pts)
            d["debut"] = d["debut"] or p.findtext("timeInterval/start"); d["fin"] = p.findtext("timeInterval/end")
        out.append(d)
    return out

def agrege(r):
    """Résumé compact d'un résultat de resume()."""
    if isinstance(r, dict): return f"ACK {r}"
    if not r: return "vide"
    res = sorted({x for d in r for x in d["res"]}); psr = sorted({d["psr"] for d in r if d["psr"]})
    cur = sorted({str(d["cur"]) for d in r}); un = sorted({str(d["unit"]) for d in r})
    deb = min(d["debut"] for d in r); fin = max(d["fin"] for d in r)
    return f"{len(r)} TS, res={res}, n={sum(d['n'] for d in r)}, omis(A03)={sum(d['manque'] for d in r)}, unit={un}, cur={cur}, {deb}->{fin}" + (f", psr={psr}" if psr else "")

def show(nom, p):
    c, t, dt = get(p)
    print(f"{nom}: HTTP {c}, {len(t)} o, {dt:.1f}s ->", agrege(resume(t)) if c == 200 else (re.findall(r'<text>([^<]*)', t) or [re.sub(r'\s+', ' ', t)[:300]])[0][:300], flush=True)

def serie(txt, psr=None, conso=False):
    """Dépile un document en {debut_periode_utc(datetime): valeur}. A03 : un point omis répète le précédent.
    Retourne aussi le pas. Prix : price.amount ; sinon quantity."""
    from datetime import datetime, timedelta, timezone
    txt = re.sub(r' xmlns="[^"]+"', "", txt, count=1)
    out = {}
    for ts in ET.fromstring(txt).findall("TimeSeries"):
        if psr and ts.findtext("MktPSRType/psrType") != psr: continue
        if (ts.find("outBiddingZone_Domain.mRID") is not None) != conso and psr: continue
        for p in ts.findall("Period"):
            res = p.findtext("resolution"); pas = {"PT15M": 15, "PT30M": 30, "PT60M": 60}[res]
            t0 = datetime.strptime(p.findtext("timeInterval/start"), "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
            t1 = datetime.strptime(p.findtext("timeInterval/end"), "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
            n = int((t1 - t0).total_seconds() // 60 // pas)
            pts = {int(x.findtext("position")): float(x.findtext("price.amount") or x.findtext("quantity")) for x in p.findall("Point")}
            last = None
            for i in range(1, n + 1):
                if i in pts: last = pts[i]
                if last is not None: out[t0 + timedelta(minutes=pas * (i - 1))] = (last, pas, i in pts)
    return out
