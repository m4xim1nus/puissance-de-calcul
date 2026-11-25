#!/usr/bin/env python3
"""Spike « data centers » — exploration OSM + géocodage des communes.

Usage :
    python3 pipeline/explo/spike_datacenters.py overpass   # télécharge et résume OSM
    python3 pipeline/explo/spike_datacenters.py communes   # géocode les communes du CSV amorce
    python3 pipeline/explo/spike_datacenters.py odre       # soutirages RPT section J (ODRÉ)
    python3 pipeline/explo/spike_datacenters.py sdes       # données SDES 2024 (xlsx)

Sorties (data/raw/spike/datacenters/) :
    overpass_fr_datacenters_raw.json   réponse Overpass brute (ODbL, © contributeurs OSM)
    osm_datacenters_fr_metro.csv       un objet OSM par ligne, France métropolitaine
    osm_quality.json                   taux de remplissage des attributs
    communes_geocodees.json            centres de communes (geo.api.gouv.fr)
    odre_soutirages_rpt_sectionJ.csv   soutirages RPT, section NAF J, pas 30 min (Licence Ouverte)
    sdes_datacenters_2024_donnees.xlsx SDES, consommation des data centers > 1 GWh (2018-2024)

Script d'exploration : pas de dépendance hors bibliothèque standard.
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "spike" / "datacenters"
UA = "puissance-de-calcul-spike/0.1"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Toute la France (area ISO3166-1=FR inclut l'outre-mer) ; on filtre ensuite
# sur une emprise métropolitaine + Corse.
OVERPASS_QUERY = """
[out:json][timeout:180];
area["ISO3166-1"="FR"][admin_level=2]->.fr;
(
  nwr["telecom"="data_center"](area.fr);
  nwr["building"="data_center"](area.fr);
  nwr["building"="datacenter"](area.fr);
);
out center tags;
"""
METRO_BBOX = (41.2, -5.6, 51.2, 9.8)  # lat_min, lon_min, lat_max, lon_max

KEYS_OF_INTEREST = [
    "name", "operator", "operator:wikidata", "addr:city", "addr:postcode",
    "data_center:power", "start_date", "ref", "website", "ref:FR:SIRET",
    "building", "telecom",
]


def http_get(url: str, data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=240) as r:
        return r.read()


def fetch_overpass(force: bool = False) -> dict:
    out = RAW / "overpass_fr_datacenters_raw.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    body = urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode()
    raw = http_get(OVERPASS_URL, body)
    out.write_bytes(raw)
    return json.loads(raw)


def coords(el: dict) -> tuple[float | None, float | None]:
    if el["type"] == "node":
        return el.get("lat"), el.get("lon")
    c = el.get("center") or {}
    return c.get("lat"), c.get("lon")


def in_metro(lat, lon) -> bool:
    if lat is None or lon is None:
        return False
    a, b, c, d = METRO_BBOX
    return a <= lat <= c and b <= lon <= d


def overpass_summary() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    data = fetch_overpass()
    els = data["elements"]
    rows = []
    for el in els:
        lat, lon = coords(el)
        t = el.get("tags", {})
        rows.append({
            "osm_id": f'{el["type"]}/{el["id"]}',
            "lat": lat, "lon": lon, "metro": in_metro(lat, lon),
            **{k: t.get(k, "") for k in KEYS_OF_INTEREST},
        })
    metro = [r for r in rows if r["metro"]]
    # Doublons probables : un bâtiment building=data_center sans telecom=* à
    # l'intérieur d'un site telecom=data_center. Indicateur grossier : même
    # nom + même opérateur.
    dup_key = Counter((r["name"], r["operator"]) for r in metro if r["name"])
    n = len(metro)
    fill = {k: round(sum(1 for r in metro if r[k]) / n, 3) for k in KEYS_OF_INTEREST}
    ops = Counter(r["operator"] for r in metro if r["operator"])
    quality = {
        "osm_timestamp": data.get("osm3s", {}).get("timestamp_osm_base"),
        "n_total_france_entiere": len(rows),
        "n_metropole": n,
        "n_hors_metropole": len(rows) - n,
        "par_type_objet": Counter(r["osm_id"].split("/")[0] for r in metro),
        "telecom_data_center": sum(1 for r in metro if r["telecom"] == "data_center"),
        "building_data_center_sans_telecom": sum(
            1 for r in metro if r["telecom"] != "data_center"),
        "taux_remplissage": fill,
        "noms_en_double_nom_operateur": {f"{k[0]} | {k[1]}": v for k, v in dup_key.items() if v > 1},
        "top_operateurs": ops.most_common(25),
        "avec_data_center_power": [
            {"osm_id": r["osm_id"], "name": r["name"], "power": r["data_center:power"]}
            for r in metro if r["data_center:power"]
        ],
    }
    (RAW / "osm_quality.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2))
    with open(RAW / "osm_datacenters_fr_metro.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(metro[0].keys()))
        w.writeheader()
        w.writerows(metro)
    print(json.dumps({k: quality[k] for k in (
        "osm_timestamp", "n_total_france_entiere", "n_metropole", "telecom_data_center",
        "building_data_center_sans_telecom", "taux_remplissage")}, ensure_ascii=False, indent=2))
    print("top opérateurs :", quality["top_operateurs"][:15])


# Communes du CSV amorce dont les coordonnées viennent du centre communal
# (geo.api.gouv.fr, champ « centre »). Code INSEE pour lever les homonymies.
COMMUNES = {
    "Fouju": "77195", "Vernou-la-Celle-sur-Seine": "77494", "Escaudain": "59205",
    "Bosquel": "80114", "Bourbourg": "59094", "Loon-Plage": "59359",
    "Bouchain": "59092", "Cambrai": "59122", "Mougins": "06085",
    "Bruyères-le-Châtel": "91115", "Bessé-sur-Braye": "72035",
    "Alixan": "26004", "Dugny": "93030", "Rungis": "94065",
    "Nozay": "91458", "Meudon": "92048", "Argenteuil": "95018",
    "Aulnay-sous-Bois": "93005", "Le Bourget": "93013",
    "Corbeil-Essonnes": "91174", "Villeneuve-Saint-Georges": "94078",
    "Bonneuil-sur-Marne": "94011", "Saint-Ouen-l'Aumône": "95572",
    "Bouc-Bel-Air": "13015", "Wissous": "91689", "Cabriès": "13019",
    "Petit-Landau": "68254", "Gravelines": "59273", "Roubaix": "59512",
    "La Courneuve": "93027", "Marseille": "13055", "Villefontaine": "38553",
    "La Maxe": "57452", "Richemont": "57582", "Le Coudray-Montceaux": "91179",
    "Sucy-en-Brie": "94071", "Marcoussis": "91363",
}


def geocode_communes() -> None:
    out = {}
    for nom, insee in COMMUNES.items():
        url = f"https://geo.api.gouv.fr/communes/{insee}?fields=nom,code,codeDepartement,centre"
        try:
            d = json.loads(http_get(url))
        except Exception as e:  # noqa: BLE001 — exploration
            out[nom] = {"erreur": str(e)}
            continue
        if d.get("nom", "").lower() != nom.lower():
            d["alerte"] = f"nom attendu {nom}, reçu {d.get('nom')}"
        out[nom] = d
        time.sleep(0.1)
    (RAW / "communes_geocodees.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    for k, v in out.items():
        print(k, v.get("code"), v.get("codeDepartement"), (v.get("centre") or {}).get("coordinates"), v.get("alerte", ""))


ODRE_SOUTIRAGES = (
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "soutirages-quotidiens-consolides-rpt-par-section/exports/csv"
)
SDES_XLSX = "https://www.statistiques.developpement-durable.gouv.fr/media/9471/download?inline"


def odre_section_j() -> None:
    """Soutirages RPT de la section NAF J (Information et communication).

    ATTENTION : la section J n'est PAS le périmètre « data centers » de RTE
    (environ 0,26 TWh en 2025 contre ~1 TWh pour les data centers raccordés
    au RPT selon le Bilan électrique 2025). Proxy partiel seulement.
    """
    q = urllib.parse.urlencode({
        "where": 'secteur_activite_economique like "J-%"', "delimiter": ";"})
    out = RAW / "odre_soutirages_rpt_sectionJ.csv"
    out.write_bytes(http_get(f"{ODRE_SOUTIRAGES}?{q}"))
    rows = list(csv.DictReader(open(out, encoding="utf-8-sig"), delimiter=";"))
    hh_cols = [c for c in rows[0] if c[:2].isdigit() and "h" in c]
    by_year: dict[str, float] = {}
    hh: dict[tuple[str, str], float] = {}
    for r in rows:
        y = r["date_de_la_courbe"][:4]
        by_year[y] = by_year.get(y, 0.0) + float(r["energie_journaliere"] or 0)
        for c in hh_cols:
            if r[c]:
                hh[(r["date_de_la_courbe"], c)] = hh.get((r["date_de_la_courbe"], c), 0.0) + float(r[c])
    for y in sorted(by_year):
        v = [x for (d, _), x in hh.items() if d.startswith(y)]
        print(f"{y}: {by_year[y] / 1e3:.1f} GWh ; P moy {sum(v) / len(v):.1f} MW ; P max {max(v):.1f} MW")


def sdes_xlsx() -> None:
    (RAW / "sdes_datacenters_2024_donnees.xlsx").write_bytes(http_get(SDES_XLSX))
    print("ok :", RAW / "sdes_datacenters_2024_donnees.xlsx")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "overpass"
    {"overpass": overpass_summary, "communes": geocode_communes,
     "odre": odre_section_j, "sdes": sdes_xlsx}[cmd]()
