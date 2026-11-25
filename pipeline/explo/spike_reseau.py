"""Spike d'accès : sources réseau, géographie, météo.

Vérifie l'accès (pas un pipeline). Télécharge de petits échantillons dans
data/raw/spike/reseau/ (non versionné) et calcule quelques ordres de grandeur.

Usage (aucune installation globale) :
    uv run --with httpx,pyshp python pipeline/explo/spike_reseau.py [étape ...]

Étapes : odre, ddt45, contours, openmeteo, pvgis, ninja, calculs
Sans argument : tout sauf `ninja` (quota anonyme de 5 requêtes/jour, voir rapport).
Aucun secret, aucun compte : renewables.ninja est appelé SANS jeton.
"""
from __future__ import annotations

import json
import math
import sys
import time
import zipfile
from pathlib import Path

import csv
from collections import Counter

import httpx

RACINE = Path(__file__).resolve().parents[2]
RAW = RACINE / "data" / "raw" / "spike" / "reseau"
ODRE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"
# Fouju (Seine-et-Marne) ; Marseille en second point
POINTS = {"fouju": (48.58, 2.77), "marseille": (43.30, 5.37)}
ANNEE = 2023  # dernière année complète commune à PVGIS 5.3 (2005-2023)


def client() -> httpx.Client:
    return httpx.Client(timeout=120, follow_redirects=True,
                        headers={"User-Agent": "spike-acces-donnees/0.1"})


def telecharger(c: httpx.Client, url: str, dest: Path, **params) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  déjà là : {dest.name}")
        return dest
    for essai in range(4):  # PVGIS coupe parfois les connexions rapprochées
        try:
            r = c.get(url, params=params or None)
            r.raise_for_status()
            break
        except httpx.TransportError as e:
            print(f"  essai {essai + 1} échoué ({type(e).__name__}), pause")
            time.sleep(5 * (essai + 1))
    else:
        raise RuntimeError(f"échec : {url}")
    dest.write_bytes(r.content)
    print(f"  {r.status_code} {len(r.content):>10,d} o  {dest.name}")
    return dest


# --- 1/2/3 : ODRÉ (postes, lignes, contraintes) ---------------------------
def etape_odre(c: httpx.Client) -> None:
    print("ODRÉ")
    for ds in ["postes-electriques-rte", "lignes-aeriennes-rte-nv",
               "lignes-souterraines-rte-nv", "contraintes-region",
               "energies-et-puissances-regionales-liees-au-contraintes",
               "suivi-projet-raccordement-enr"]:
        telecharger(c, f"{ODRE}/{ds}/exports/csv", RAW / f"{ds}.csv",
                    delimiter=";", limit=-1)
    # Constat clé : la géométrie est NULLE (publication sans coordonnées depuis 2024)
    g = c.get(f"{ODRE}/postes-electriques-rte/exports/geojson", params={"limit": 3}).json()
    print("  géométrie postes :", [f["geometry"] for f in g["features"]])
    with open(RAW / "postes-electriques-rte.csv", encoding="utf-8-sig") as f:
        p = list(csv.DictReader(f, delimiter=";"))
    print("  postes :", len(p), Counter(x["tension"] for x in p).most_common())


# --- 1 : Caparéseau via data.gouv (extrait DDT Loiret, 2023) --------------
def etape_ddt45(c: httpx.Client) -> None:
    import shapefile  # pyshp
    print("Extrait Caparéseau (DDT 45)")
    url = ("https://atom.geo-ide.developpement-durable.gouv.fr/atomArchive/GetResource"
           "?id=55304b34-d48c-45a8-84c5-b5e3d7e805c3&dataType=dataset")
    z = telecharger(c, url, RAW / "ddt45" / "capacite.zip")
    with zipfile.ZipFile(z) as zf:
        zf.extractall(RAW / "ddt45")
    shp = next((RAW / "ddt45").rglob("*.shp"))
    r = shapefile.Reader(str(shp))
    print("  ", len(r), "postes", r.shapeTypeName, "champs", [f[0] for f in r.fields[1:]])


# --- 5 : contours -----------------------------------------------------------
def etape_contours(c: httpx.Client) -> None:
    print("Contours")
    base = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master"
    for f in ["regions", "departements", "regions-version-simplifiee",
              "departements-version-simplifiee"]:
        telecharger(c, f"{base}/{f}.geojson", RAW / "contours" / f"{f}.geojson")
    # API officielle (millésime courant) : un département, communes
    telecharger(c, "https://geo.api.gouv.fr/communes", RAW / "contours" / "geoapi_communes77.geojson",
                codeDepartement="77", fields="nom,code,contour", format="geojson", geometry="contour")
    # Admin Express : on ne télécharge pas (archives lourdes), on liste le flux Atom
    r = c.get("https://data.geopf.fr/telechargement/resource/ADMIN-EXPRESS")
    print("  Admin Express (flux Atom) HTTP", r.status_code, "—",
          "totalentries=" + r.text.split('totalentries="')[1].split('"')[0])


# --- 4a : Open-Meteo ---------------------------------------------------------
def etape_openmeteo(c: httpx.Client) -> None:
    print("Open-Meteo (ERA5, UTC)")
    for nom, (lat, lon) in POINTS.items():
        # model=era5 : grille 0,25° ; sans `models`, grille « best match » différente (voir rapport)
        telecharger(
            c, "https://archive-api.open-meteo.com/v1/archive",
            RAW / "meteo" / f"openmeteo_{nom}_{ANNEE}.json",
            latitude=lat, longitude=lon, start_date=f"{ANNEE}-01-01", end_date=f"{ANNEE}-12-31",
            hourly="temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_100m,"
                   "wind_speed_10m,global_tilted_irradiance",
            tilt=35, azimuth=0, wind_speed_unit="ms", timezone="UTC", models="era5")
    # même année que renewables.ninja (2019) pour comparer l'éolien
    telecharger(
        c, "https://archive-api.open-meteo.com/v1/archive",
        RAW / "meteo" / "openmeteo_fouju_2019.json",
        latitude=48.58, longitude=2.77, start_date="2019-01-01", end_date="2019-12-31",
        hourly="wind_speed_100m", wind_speed_unit="ms", timezone="UTC", models="era5")


# --- 4b : PVGIS --------------------------------------------------------------
def etape_pvgis(c: httpx.Client) -> None:
    print("PVGIS 5.3 seriescalc")
    for nom, (lat, lon) in POINTS.items():
        for db in ["PVGIS-SARAH3", "PVGIS-ERA5"]:
            telecharger(
                c, "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc",
                RAW / "meteo" / f"pvgis_{nom}_{db}_{ANNEE}.json",
                lat=lat, lon=lon, startyear=ANNEE, endyear=ANNEE, pvcalculation=1,
                peakpower=1, loss=14, angle=35, aspect=0, raddatabase=db, outputformat="json")


# --- 4c : renewables.ninja (anonyme, 5 req/jour d'après la doc) -------------
def etape_ninja(c: httpx.Client) -> None:
    print("renewables.ninja (anonyme)")
    telecharger(
        c, "https://www.renewables.ninja/api/data/wind",
        RAW / "meteo" / "ninja_wind_fouju_2019.json",
        lat=48.58, lon=2.77, date_from="2019-01-01", date_to="2019-12-31",
        capacity=1, height=100, turbine="Vestas V80 2000", format="json")


# --- calculs d'ordres de grandeur -------------------------------------------
def _meteo(nom: str, annee: int = ANNEE) -> dict[str, list]:
    return json.loads((RAW / "meteo" / f"openmeteo_{nom}_{annee}.json").read_text())["hourly"]


def t_humide_stull(t: float, rh: float) -> float:
    """Température de bulbe humide, formule de Stull (2011), valable RH 5-99 %, T -20..50 °C."""
    return (t * math.atan(0.151977 * math.sqrt(rh + 8.313659)) + math.atan(t + rh)
            - math.atan(rh - 1.676331) + 0.00391838 * rh**1.5 * math.atan(0.023101 * rh)
            - 4.686035)


def puissance_eolienne_generique(v: float) -> float:
    """Courbe générique 2 MW, FACTEUR DE CHARGE INDICATIF seulement (pas un modèle fiable) :
    entrée 3 m/s, nominal 12 m/s, coupure 25 m/s, cubique entre les deux."""
    if v < 3 or v >= 25:
        return 0.0
    if v >= 12:
        return 1.0
    return (v**3 - 27) / (12**3 - 27)


def etape_calculs(_c: httpx.Client | None = None) -> None:
    out: dict = {}
    for nom in POINTS:
        m = _meteo(nom)
        t, rh = m["temperature_2m"], m["relative_humidity_2m"]
        n = len(t)
        # Degrés-heures de refroidissement au-dessus de seuils (°C·h par an), air sec
        dh = {f"degres_heures_T>{s}C": round(sum(max(x - s, 0) for x in t)) for s in (20, 25, 30)}
        dh["heures_T>35C"] = sum(x > 35 for x in t)
        dh["heures_Tbulbe_humide>20C"] = sum(t_humide_stull(a, max(5, min(99, b))) > 20
                                             for a, b in zip(t, rh))
        # PV : GTI (inclinée 35°, plein sud) x (1 - 14 % pertes), sans effet température -> borne haute
        gti = [x or 0 for x in m["global_tilted_irradiance"]]
        cf_gti = sum(gti) / n / 1000 * 0.86
        cf_vent = sum(puissance_eolienne_generique(v) for v in m["wind_speed_100m"]) / n
        out[nom] = {
            "heures": n, "t_moy_C": round(sum(t) / n, 2),
            "GHI_kWh_m2": round(sum(m["shortwave_radiation"]) / 1000),
            "cf_pv_openmeteo_gti35_pr86": round(cf_gti, 4),
            "cf_eolien_generique_100m": round(cf_vent, 4),
            "refroidissement": dh,
        }
        for db in ["PVGIS-SARAH3", "PVGIS-ERA5"]:
            p = RAW / "meteo" / f"pvgis_{nom}_{db}_{ANNEE}.json"
            if p.exists():
                hh = json.loads(p.read_text())["outputs"]["hourly"]
                out[nom][f"cf_pv_{db}"] = round(sum(x["P"] for x in hh) / len(hh) / 1000, 4)
                out[nom][f"kWh_kWp_{db}"] = round(sum(x["P"] for x in hh) / 1000)
    nj = RAW / "meteo" / "ninja_wind_fouju_2019.json"
    if nj.exists():
        d = json.loads(nj.read_text())["data"]
        h19 = _meteo("fouju", 2019)["wind_speed_100m"]
        out["ninja_wind_fouju_2019"] = {
            "heures": len(d),
            "cf_ninja": round(sum(v["electricity"] for v in d.values()) / len(d), 4),
            "cf_generique_openmeteo_2019": round(
                sum(puissance_eolienne_generique(v) for v in h19) / len(h19), 4)}
    (RAW / "summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=2, ensure_ascii=False))


ETAPES = {"odre": etape_odre, "ddt45": etape_ddt45, "contours": etape_contours,
          "openmeteo": etape_openmeteo, "pvgis": etape_pvgis, "ninja": etape_ninja,
          "calculs": etape_calculs}

if __name__ == "__main__":
    choix = sys.argv[1:] or [e for e in ETAPES if e != "ninja"]
    with client() as cli:
        for e in choix:
            ETAPES[e](cli)
