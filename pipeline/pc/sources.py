"""Sources open data et téléchargement (spécification : docs/spike/systeme.md).

`pc download` écrit dans `data/raw/<clé>/` et note dans `data/raw/manifeste.json`,
pour chaque fichier : URL complète (paramètres compris), date d'extraction,
nature des données, sha256, taille et nombre de lignes. Ce manifeste date
l'instantané ; `pc build` en recopie l'essentiel dans `data/export/meta.json`.

Deux familles de sources :

- **annuelles** (éCO2mix cons-def, prix day-ahead, nucléaire horaire) : un
  fichier par année civile (heure de Paris). C'est là que joue
  l'incrémental : une année **close** déjà téléchargée n'est pas refaite,
  sauf `--force`. Pour éCO2mix, une année n'est close que si toutes ses
  lignes étaient « définitives » au téléchargement : une année encore
  « consolidée » sera revue par RTE (spécification éCO2mix § 1.1) et on la
  retélécharge tant qu'elle ne l'est pas ;
- **instantanés** (éCO2mix temps réel, références annuelles ODRÉ) : un seul
  fichier, retéléchargé à chaque exécution, car ces jeux changent (fenêtre
  glissante, révisions) ;
- **indisponibilités EDF (REMIT)** (`edf_remit`, opendata.edf.fr, data-fair) :
  deux fichiers CSV gardés tels quels, l'historique depuis 2015 (export ponctuel
  d'EDF, 112 Mo) et la liste courante (mise à jour toutes les heures). La liste
  courante est retéléchargée à chaque exécution ; l'historique aussi, **sauf**
  si le fichier local a déjà le md5 que data-fair publie pour le fichier en
  ligne (même contenu octet pour octet : le retélécharger ne changerait rien).
  Les métadonnées data-fair (date de mise à jour des données, nom du fichier
  d'origine, md5) sont notées dans le manifeste ;
- **ENTSO-E Transparency Platform** (`entsoe_*`, `pc/entsoe.py`) : une requête par
  série (zone ou frontière dans un sens) et par année civile, XML brut compressé dans
  `data/raw/entsoe/`, en parallèle ; jeton requis (`$ENTSOE_TOKEN` ou
  `source/entsoe_token`), jamais écrit nulle part. Sans jeton, ces clés échouent avec
  un message clair, les autres sont téléchargées normalement.

Les exports ODRÉ passent par `/exports/parquet` (l'endpoint `/records` est
plafonné à 10 000 lignes) : sans jeton, mais lents (1 à 5 min par an et par
jeu). energy-charts limite `/price` à 2 requêtes par minute (HTTP 429 avec
`Retry-After` au-delà) : on espace les requêtes de 31 s.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
import polars as pl

from . import entsoe

ODRE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"
EC = "https://api.energy-charts.info"
EDF = "https://opendata.edf.fr/data-fair/api/v1/datasets"

ANNEE_DEBUT = 2015
MANIFESTE = "manifeste.json"
PAUSE_ENERGY_CHARTS_S = 31  # 2 requêtes/min sur /price (openapi energy-charts, 2026-07-20)

# Licences et attributions à afficher (vérifiées pendant le spike du 2026-11-25).
LICENCE_ODRE = {
    "licence": "Licence Ouverte v2.0 (Etalab)",
    "attribution": "RTE — éCO2mix, via ODRÉ (Open Data Réseaux Énergies)",
    "url_licence": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
}
LICENCE_PRIX = {
    "licence": "CC BY 4.0",
    # Champ `license_info` de la réponse energy-charts pour bzn=FR, mot pour mot :
    "license_info": "CC BY 4.0 (creativecommons.org/licenses/by/4.0) from Bundesnetzagentur | SMARD.de",
    "attribution": "Bundesnetzagentur | SMARD.de, via energy-charts.info (Fraunhofer ISE)",
    "url_licence": "https://creativecommons.org/licenses/by/4.0/",
}
# Licence lue dans les métadonnées data-fair des deux jeux (champ `license`, 2026-11-26) et sur
# data.gouv.fr (spike « Quand ? », docs/spike/quand.md § 2.1).
LICENCE_EDF = {
    "licence": "Licence Ouverte v2.0 (Etalab)",
    "attribution": "EDF — indisponibilités des moyens de production d'EDF SA (REMIT), via opendata.edf.fr",
    "url_licence": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
}


def _where_annee(champ: str, annee: int) -> str:
    """Filtre ODSQL sur l'année civile en heure de Paris (1er janvier = heure d'hiver, +01:00)."""
    return (f"{champ} >= '{annee}-01-01T00:00:00+01:00' and "
            f"{champ} < '{annee + 1}-01-01T00:00:00+01:00'")


SOURCES: dict[str, dict] = {
    "eco2mix_cons_def": {
        "type": "odre_annuel", "jeu": "eco2mix-national-cons-def", "champ_date": "date_heure",
        "nature": "éCO2mix national, consolidé et définitif (MW moyens au pas de 30 min)",
        **LICENCE_ODRE,
    },
    "eco2mix_tr": {
        "type": "odre_instantane", "jeu": "eco2mix-national-tr",
        "nature": "éCO2mix national, temps réel (MW instantanés au pas de 15 min, fenêtre glissante)",
        **LICENCE_ODRE,
    },
    "prix_fr": {
        "type": "energy_charts_annuel", "bzn": "FR",
        "nature": "prix day-ahead (SDAC) zone FR, EUR/MWh, horodatage = début de période ; "
                  "pas de 60 min puis 15 min à partir de la livraison du 2025-10-01",
        **LICENCE_PRIX,
    },
    "odre_nucleaire": {
        "type": "odre_annuel", "jeu": "production-nette-nucleaire", "champ_date": "horodate",
        "nature": "production nucléaire nette nationale horaire (GWh par heure, « convention débutante »)",
        **LICENCE_ODRE,
    },
    "odre_ges_conso": {
        "type": "odre_instantane", "jeu": "part-enr-intensite-ges-conso-tr",
        "nature": "intensité GES de la consommation (imports compris) et part EnR, horaire, gCO2eq/kWh",
        **LICENCE_ODRE,
    },
    "odre_conso_annuelle": {
        "type": "odre_instantane", "jeu": "consommation-annuelle-brute",
        "nature": "consommation brute annuelle France (Corse comprise), GWh",
        **LICENCE_ODRE,
    },
    "odre_conso_annuelle_regionale": {
        "type": "odre_instantane", "jeu": "consommation-annuelle-brute-regionale",
        "nature": "consommation brute annuelle par région, GWh",
        **LICENCE_ODRE,
    },
    "edf_remit": {
        "type": "edf_datafair",
        "jeux": {
            "historique": "historique-des-indisponibilites-des-moyens-de-production-de-edf-sa-depuis-2015",
            "courante": "indisponibilites-des-moyens-de-production-edf-sa",
        },
        "nature": "indisponibilités des moyens de production d'EDF SA déclarées au titre de REMIT, une ligne "
                  "par version d'événement (CSV latin-1, « ; ») : historique depuis 2015 (export ponctuel) "
                  "et liste courante (événements terminés depuis moins de trois mois, mise à jour horaire)",
        **LICENCE_EDF,
    },
    # ENTSO-E : catalogue des séries et licences dans pc/entsoe.py (licence propre à chaque donnée).
    **{cle: {"type": "entsoe", "nature": entsoe.NATURES[cle], **entsoe.LICENCES[cle]} for cle in entsoe.CLES},
}


# --------------------------------------------------------------------------
# Manifeste
# --------------------------------------------------------------------------


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def lire_manifeste(raw: Path) -> dict:
    p = raw / MANIFESTE
    return json.loads(p.read_text()) if p.exists() else {}


def maj_manifeste(raw: Path, cle: str, entree: dict) -> None:
    """Relit le manifeste, met à jour une entrée et réécrit (atomique) : deux `pc download`
    parallèles sur des sources différentes ne s'écrasent pas."""
    manifeste = lire_manifeste(raw)
    manifeste[cle] = entree
    tmp = raw / f"{MANIFESTE}.{os.getpid()}.part"
    tmp.write_text(json.dumps(manifeste, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(raw / MANIFESTE)


def fichier(raw: Path, cle: str, annee: int | None = None) -> Path:
    """Chemin du fichier brut d'une source (une année, ou l'instantané)."""
    ext = "json" if SOURCES[cle]["type"].startswith("energy_charts") else "parquet"
    return raw / cle / (f"{annee}.{ext}" if annee is not None else f"{cle}.{ext}")


def fichier_edf(raw: Path, partie: str) -> Path:
    """Fichier brut REMIT d'EDF : `partie` = « historique » ou « courante »."""
    return raw / "edf_remit" / f"{partie}.csv"


def md5_fichier(chemin: Path) -> str:
    h = hashlib.md5()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def fichiers_annuels(raw: Path, cle: str) -> list[Path]:
    return sorted((raw / cle).glob("[0-9][0-9][0-9][0-9].*"))


# --------------------------------------------------------------------------
# Téléchargement
# --------------------------------------------------------------------------


def _telecharger(client: httpx.Client, url: str, params: dict | None, dest: Path) -> str:
    """Télécharge `url` dans `dest` (écriture atomique). Renvoie l'URL complète effectivement appelée.

    Respecte `Retry-After` sur HTTP 429 (energy-charts). Lève `httpx.HTTPStatusError` sinon.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    for _ in range(8):
        t0 = time.time()
        with client.stream("GET", url, params=params) as r:
            if r.status_code == 429:
                attente = int(r.headers.get("Retry-After", "60"))
                print(f"  HTTP 429, attente {attente} s", file=sys.stderr)
                time.sleep(attente + 1)
                continue
            r.raise_for_status()
            with part.open("wb") as f:
                for bloc in r.iter_bytes(1 << 20):
                    f.write(bloc)
            url_complete = str(r.url)
        part.replace(dest)
        print(f"  {dest.relative_to(dest.parents[1])} : {dest.stat().st_size / 1e6:.2f} Mo en "
              f"{time.time() - t0:.0f} s", file=sys.stderr)
        return url_complete
    raise RuntimeError(f"HTTP 429 persistant sur {url}")


def _natures_parquet(chemin: Path) -> tuple[int, dict | None]:
    """Nombre de lignes et, si la colonne existe, décompte des valeurs de `nature` (lignes renseignées)."""
    df = pl.read_parquet(chemin)
    if "nature" not in df.columns:
        return df.height, None
    v = df.filter(pl.col("consommation").is_not_null()) if "consommation" in df.columns else df
    natures = {str(k): int(n) for k, n in v.group_by("nature").len().iter_rows()}
    return df.height, natures


def _lignes_csv(chemin: Path) -> int:
    """Nombre d'enregistrements d'un CSV « ; » (en-tête exclu ; un champ entre guillemets peut contenir
    un saut de ligne, d'où une vraie lecture plutôt qu'un comptage de lignes)."""
    return pl.read_csv(chemin, separator=";", encoding="utf8-lossy", infer_schema_length=0, columns=[0]).height


def _entree(cle: str, url: str, dest: Path, annee: int | None) -> dict:
    src = SOURCES[cle]
    if dest.suffix == ".parquet":
        lignes, natures = _natures_parquet(dest)
    elif dest.suffix == ".csv":
        lignes, natures = _lignes_csv(dest), None
    else:
        d = json.loads(dest.read_text())
        lignes, natures = len(d.get("unix_seconds") or []), None
    e = {
        "url": url,
        "extrait_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nature": src["nature"],
        "sha256": sha256_fichier(dest),
        "taille": dest.stat().st_size,
        "lignes": lignes,
        "licence": src["licence"],
        "attribution": src["attribution"],
    }
    if annee is not None:
        e["annee"] = annee
    if natures is not None:
        e["natures"] = natures
    return e


def _annee_close(cle: str, annee: int, entree: dict | None, aujourd_hui: date) -> bool:
    """Une année déjà téléchargée est-elle figée (inutile de la refaire) ?"""
    if entree is None or annee >= aujourd_hui.year:
        return False
    if cle == "eco2mix_cons_def":
        # Close seulement si tout était définitif : le consolidé sera remplacé.
        natures = entree.get("natures") or {}
        return bool(natures) and all("finitive" in n for n in natures)
    return True


def _download_edf(client: httpx.Client, raw: Path, cle: str, manifeste: dict, force: bool) -> None:
    """Jeux data-fair d'EDF : métadonnées (petites) puis fichier brut (`/raw`) si nécessaire."""
    for partie, slug in SOURCES[cle]["jeux"].items():
        cle_m = f"{cle}/{partie}"
        dest = fichier_edf(raw, partie)
        r = client.get(f"{EDF}/{slug}")
        r.raise_for_status()
        meta = r.json()
        original = meta.get("originalFile") or meta.get("file") or {}
        md5_distant = original.get("md5")
        source = {
            "mis_a_jour_source": meta.get("dataUpdatedAt"),
            "fichier_source": original.get("name"),
            "md5_source": md5_distant,
        }
        if (partie == "historique" and not force and dest.exists() and md5_distant
                and cle_m in manifeste and md5_fichier(dest) == md5_distant):
            print(f"  {partie} : inchangé en ligne (md5 {md5_distant}), pas retéléchargé", file=sys.stderr)
            entree = {**manifeste[cle_m], **source, "verifie_le": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            maj_manifeste(raw, cle_m, entree)
            continue
        url = _telecharger(client, f"{EDF}/{slug}/raw", None, dest)
        if md5_distant and md5_fichier(dest) != md5_distant:
            # la liste courante change toutes les heures : les métadonnées lues juste avant peuvent
            # déjà être périmées. On le note, sans échouer.
            print(f"  {partie} : md5 local ≠ md5 annoncé ({md5_distant}), mise à jour entre-temps ?", file=sys.stderr)
        maj_manifeste(raw, cle_m, {**_entree(cle, url, dest, None), **source})


def download(raw: Path, cles: list[str] | None = None, force: bool = False,
             aujourd_hui: date | None = None) -> None:
    aujourd_hui = aujourd_hui or date.today()
    inconnues = set(cles or []) - set(SOURCES)
    if inconnues:
        raise SystemExit(f"clés inconnues : {sorted(inconnues)} (connues : {sorted(SOURCES)})")
    raw.mkdir(parents=True, exist_ok=True)
    manifeste = lire_manifeste(raw)
    demandees = list(cles or SOURCES)
    cles_entsoe = [c for c in demandees if SOURCES[c]["type"] == "entsoe"]
    sans_jeton = bool(cles_entsoe) and not entsoe.lire_jeton()
    if sans_jeton and cles:  # clés ENTSO-E demandées explicitement : échec immédiat, rien téléchargé
        raise SystemExit(f"{', '.join(cles_entsoe)} : {entsoe.MESSAGE_SANS_JETON}")
    if sans_jeton:
        print(f"AVERTISSEMENT : {entsoe.MESSAGE_SANS_JETON} Clés ENTSO-E sautées.", file=sys.stderr)
    derniere_ec = 0.0
    # Les exports ODRÉ sont lents (jusqu'à 5 min) : délai large.
    with httpx.Client(timeout=httpx.Timeout(900, connect=60), follow_redirects=True,
                      headers={"User-Agent": "pc-pipeline (open data)"}) as client:
        for cle in demandees:
            src = SOURCES[cle]
            if src["type"] == "entsoe":
                continue  # après les autres, en parallèle (ci-dessous)
            print(f"{cle} ({src['type']})", file=sys.stderr)
            if src["type"] == "edf_datafair":
                _download_edf(client, raw, cle, manifeste, force)
                continue
            if src["type"] == "odre_instantane":
                dest = fichier(raw, cle)
                url = _telecharger(client, f"{ODRE}/{src['jeu']}/exports/parquet", None, dest)
                maj_manifeste(raw, cle, _entree(cle, url, dest, None))
                continue
            for annee in range(ANNEE_DEBUT, aujourd_hui.year + 1):
                cle_m = f"{cle}/{annee}"
                dest = fichier(raw, cle, annee)
                if not force and dest.exists() and _annee_close(cle, annee, manifeste.get(cle_m), aujourd_hui):
                    continue
                if src["type"] == "odre_annuel":
                    url = _telecharger(client, f"{ODRE}/{src['jeu']}/exports/parquet",
                                       {"where": _where_annee(src["champ_date"], annee)}, dest)
                else:  # energy-charts : dates interprétées en heure locale de la zone
                    fin = date(annee, 12, 31) if annee < aujourd_hui.year else aujourd_hui + timedelta(days=1)
                    attente = PAUSE_ENERGY_CHARTS_S - (time.time() - derniere_ec)
                    if attente > 0:
                        time.sleep(attente)
                    try:
                        url = _telecharger(client, f"{EC}/price",
                                           {"bzn": src["bzn"], "start": f"{annee}-01-01", "end": fin.isoformat()}, dest)
                    except httpx.HTTPStatusError as err:
                        print(f"  {annee} : HTTP {err.response.status_code} {err.response.text[:120]}", file=sys.stderr)
                        derniere_ec = time.time()
                        continue
                    derniere_ec = time.time()
                maj_manifeste(raw, cle_m, _entree(cle, url, dest, annee))
    if cles_entsoe and not sans_jeton:
        echecs = entsoe.download(raw, cles_entsoe, manifeste, force, aujourd_hui, maj_manifeste)
        if echecs:
            raise SystemExit(f"ENTSO-E : {len(echecs)} échec(s) :\n" + "\n".join(echecs))
    if sans_jeton:
        raise SystemExit(f"{', '.join(cles_entsoe)} non téléchargées : {entsoe.MESSAGE_SANS_JETON}")
