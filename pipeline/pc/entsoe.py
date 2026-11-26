"""ENTSO-E Transparency Platform : téléchargement (`pc download entsoe_*`) et lecture des XML.

Rapport : docs/spike/entsoe-pipeline.md (spike d'accès : docs/spike/entsoe-acces.md).

**Jeton** : lu au moment du téléchargement dans `$ENTSOE_TOKEN`, sinon dans
`source/entsoe_token` (racine du dépôt, dossier privé non versionné). Il n'est ajouté
qu'à la requête HTTP envoyée : jamais écrit dans un fichier, un journal, un message
d'erreur ni dans l'URL notée au manifeste (`securityToken=***`). Sans jeton, les clés
ENTSO-E échouent avec un message clair ; le reste du pipeline (build, check, CI) n'en
dépend pas.

**Découpage** : une requête par (clé, série, année civile en heure de Paris), la
fenêtre maximale de l'API étant d'un an. Brut gardé tel quel, compressé :
`data/raw/entsoe/<clé>/<série>/<AAAA>.xml.gz` ; entrée au manifeste
`<clé>/<série>/<AAAA>`. Une réponse « No matching data found » (HTTP 200,
`Acknowledgement_MarketDocument`) est gardée aussi : c'est une absence publiée, pas une
erreur (champ `vide` au manifeste).

**Lecture** (`lire_document`) : chaque `Period` porte sa résolution (mélange PT60M /
PT15M / PT30M dans une même réponse) ; `curveType` A03 : une position omise répète la
valeur précédente, jusqu'à la fin de la `Period` ; le nombre de positions se calcule
depuis `start`, `end` et la résolution (jours de 23 h et 25 h). Horodatage : début de
période, UTC. Règles particulières : voir `REGLES_LECTURE`.
"""

from __future__ import annotations

import gzip
import hashlib
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

API = "https://web-api.tp.entsoe.eu/api"
RACINE_DEPOT = Path(__file__).resolve().parents[2]
FICHIER_JETON = RACINE_DEPOT / "source" / "entsoe_token"
VARIABLE_JETON = "ENTSOE_TOKEN"

#: Parallélisme des requêtes. Le spike a passé 12 à 15 requêtes simultanées sans HTTP 429 ;
#: la limite officielle (400 requêtes/min ?) n'a pas été lue. On reste prudent.
PARALLELISME = 5
#: Attentes entre relances (s) sur délai dépassé, erreur réseau, HTTP 429 sans Retry-After, 5xx
#: (dont 599 « Unable to access service within time limit », constaté par le spike).
ATTENTES_RELANCE_S = (15, 30, 60, 120, 240)
#: HTTP 400 qui sont en fait des pannes du serveur (constatées le 2026-11-26 sur A75 IT 2025 et 2026 :
#: « An unexpected error occurred: I/O error on POST request… failed to respond », « Error while
#: extracting response… ») : relancées comme un 5xx. Un 400 sur un paramètre refusé ne l'est pas.
PANNES_SERVEUR = ("An unexpected error occurred",)
DELAI_REQUETE_S = 300  # latence constatée : 3 à 40 s par requête, quelle que soit la taille

#: Une année close n'est figée que si elle a été extraite après le 1er février de l'année
#: suivante : les données de fin décembre (production réalisée, flux) sont publiées ou
#: corrigées avec retard. Avant, l'année est retéléchargée comme l'année en cours.
MOIS_MARGE_CLOTURE = 2

ANNEE_DEBUT = 2015  # = sources.ANNEE_DEBUT (ENTSO-E FR commence le 01/01/2015 ; 2014 vide)

# --------------------------------------------------------------------------
# Domaines (codes EIC) et catalogue des requêtes
# --------------------------------------------------------------------------

#: Codes EIC des domaines utilisés. Allemagne : la zone de prix est DE-AT-LU jusqu'au
#: 30/09/2018, DE-LU ensuite (A44 DE-LU vide en 2016, DE-AT-LU présent : constaté le
#: 2026-11-26) ; production et flux sont demandés sur la zone de contrôle « DE »
#: (`10Y1001A1001A83F`), qui répond de 2015 à 2026 (mêmes valeurs que DE-LU en 2024 :
#: constaté), d'où une série continue. Italie : prix sur la zone IT-Nord (frontalière de la
#: France), production et flux sur l'Italie entière (zone de contrôle).
DOMAINES = {
    "FR": "10YFR-RTE------C",
    "BE": "10YBE----------2",
    "DE": "10Y1001A1001A83F",
    "DE-LU": "10Y1001A1001A82H",
    "DE-AT-LU": "10Y1001A1001A63L",
    "ES": "10YES-REE------0",
    "IT": "10YIT-GRTN-----B",
    "IT-Nord": "10Y1001A1001A73I",
    "CH": "10YCH-SWISSGRIDZ",
    "GB": "10YGB----------A",
}
VOISINS_FLUX = ("BE", "DE", "CH", "IT", "ES", "GB")
#: Capacités d'échange prévues jour-1 (NTC, A61 / A01) : publiées pour ces frontières seulement.
#: FR↔BE et FR↔DE sont en couplage flow-based (CWE puis Core) : pas de NTC (A61 vide en 2016 et
#: 2021, constaté le 2026-11-26 ; le spike : 2019 et 2026).
VOISINS_NTC = ("CH", "IT-Nord", "ES", "GB")


@dataclass(frozen=True)
class Serie:
    """Une série ENTSO-E à télécharger année par année."""
    cle: str  # clé `pc download`
    nom: str  # identifiant de la série (dossier) : zone « FR », frontière « FR-BE » (sens FR → BE)
    params: tuple  # paramètres de la requête, hors période et jeton (tuple de paires, ordre gardé)
    annees: tuple[int, int | None] = (ANNEE_DEBUT, None)  # première et dernière année (None : en cours)

    def parametres(self) -> dict:
        return dict(self.params)


def _prix(zone: str, annees=(ANNEE_DEBUT, None)) -> Serie:
    d = DOMAINES[zone]
    return Serie("entsoe_prix", zone, (("documentType", "A44"), ("in_Domain", d), ("out_Domain", d)), annees)


def _production(zone: str, annees=(ANNEE_DEBUT, None)) -> Serie:
    return Serie("entsoe_production", zone,
                 (("documentType", "A75"), ("processType", "A16"), ("in_Domain", DOMAINES[zone])), annees)


def _flux(de: str, vers: str) -> Serie:
    # A11 : in_Domain = zone qui importe, out_Domain = zone qui exporte (spike § 2).
    return Serie("entsoe_flux", f"{de}-{vers}",
                 (("documentType", "A11"), ("in_Domain", DOMAINES[vers]), ("out_Domain", DOMAINES[de])))


def _ntc(de: str, vers: str) -> Serie:
    return Serie("entsoe_capacites", f"{de}-{vers}",
                 (("documentType", "A61"), ("contract_MarketAgreement.Type", "A01"),
                  ("in_Domain", DOMAINES[vers]), ("out_Domain", DOMAINES[de])))


CATALOGUE: dict[str, list[Serie]] = {
    # Prix day-ahead (A44). GB : plus de prix EUR après 2020 (sortie du couplage), en GBP avant.
    "entsoe_prix": [_prix("FR"), _prix("BE"), _prix("DE-AT-LU", (ANNEE_DEBUT, 2018)), _prix("DE-LU", (2018, None)),
                    _prix("ES"), _prix("IT-Nord"), _prix("CH"), _prix("GB", (ANNEE_DEBUT, 2020))],
    # Production réalisée par filière (A75, processType A16). GB : vide à partir de 2022 (constaté).
    "entsoe_production": [_production(z) for z in ("FR", "BE", "DE", "ES", "IT", "CH")]
                         + [_production("GB", (ANNEE_DEBUT, 2021))],
    # Flux physiques (A11), chaque frontière dans les deux sens.
    "entsoe_flux": [s for v in VOISINS_FLUX for s in (_flux("FR", v), _flux(v, "FR"))],
    # Capacités d'échange prévues jour-1 (A61, contrat A01).
    "entsoe_capacites": [s for v in VOISINS_NTC for s in (_ntc("FR", v), _ntc(v, "FR"))],
    # Charge totale réalisée (A65, processType A16).
    "entsoe_charge": [Serie("entsoe_charge", "FR", (("documentType", "A65"), ("processType", "A16"),
                                                    ("outBiddingZone_Domain", DOMAINES["FR"])))],
}

#: Licences (vérifiées le 2026-11-26 sur les documents d'ENTSO-E, citées sans interprétation :
#: docs/spike/entsoe-pipeline.md § Licence).
#: - Conditions générales d'utilisation (« General Terms and Conditions for the use of the ENTSO-E
#:   Transparency Platform », approuvées le 29/03/2023, applicables au 01/11/2023), § 3.1 ;
#: - « List of data available for free re-use » (dernière modification 18/10/2023) : données sous
#:   CC BY 4.0. Y figurent « Forecasted cross-zonal capacity » (art. 11.1.a, NTC) et « Physical
#:   flows » (art. 12.1.g). N'y figurent PAS : charge réalisée (6.1.a), prix day-ahead (12.1.d),
#:   production réalisée par filière (16.1.b&c). Exception expresse : « data provided by
#:   interconnectors Interconnexion France-Angleterre » (IFA).
URL_CGU = "https://transparencyplatform.zendesk.com/hc/article_attachments/40921869376401"
URL_LISTE_OUVERTE = "https://transparencyplatform.zendesk.com/hc/article_attachments/40921869379729"
ATTRIBUTION = "ENTSO-E Transparency Platform"
LICENCE_ENTSOE_OUVERTE = {
    "licence": "CC BY 4.0 (ENTSO-E, « List of data available for free re-use », version du 18/10/2023)",
    "attribution": ATTRIBUTION,
    "url_licence": URL_LISTE_OUVERTE,
    "conditions": "« Data Users may freely copy, redistribute, and adapt the listed data for any purpose, by "
                  "giving appropriate credit (attribution) to its source and indicating if they have made any "
                  "changes » ; exception : « data provided by interconnectors Interconnexion France-Angleterre »",
}
LICENCE_ENTSOE_CGU = {
    "licence": "Conditions générales d'utilisation de la Transparency Platform (29/03/2023) ; donnée absente de "
               "la liste des données librement réutilisables (CC BY 4.0)",
    "attribution": ATTRIBUTION,
    "url_licence": URL_CGU,
    "conditions": "« mention the ENTSO-E Transparency Platform as the source of publication of the data » ; "
                  "« not cause prejudice to the copyright or related right on a Transparency Platform Data, which "
                  "may be owned by the concerned Primary Owner of Data. In case of a risk to cause prejudice to "
                  "said right, the Data User shall seek the prior agreement of the holder of the copyright or "
                  "related right »",
}
LICENCES = {
    "entsoe_prix": LICENCE_ENTSOE_CGU,
    "entsoe_production": LICENCE_ENTSOE_CGU,
    "entsoe_charge": LICENCE_ENTSOE_CGU,
    "entsoe_flux": LICENCE_ENTSOE_OUVERTE,
    "entsoe_capacites": LICENCE_ENTSOE_OUVERTE,
}
NATURES = {
    "entsoe_prix": "ENTSO-E A44, prix day-ahead (EUR/MWh ; GB en GBP/MWh), FR et voisins ; XML brut gzip",
    "entsoe_production": "ENTSO-E A75 (A16), production réalisée par filière (MW), FR et voisins ; XML brut gzip",
    "entsoe_flux": "ENTSO-E A11, flux physiques par frontière et par sens (MW), FR ↔ voisins ; XML brut gzip",
    "entsoe_capacites": "ENTSO-E A61 (contrat A01), capacités d'échange prévues jour-1 (NTC, MW) ; XML brut gzip",
    "entsoe_charge": "ENTSO-E A65 (A16), charge totale réalisée FR (MW) ; XML brut gzip",
}
CLES = tuple(CATALOGUE)


# --------------------------------------------------------------------------
# Jeton
# --------------------------------------------------------------------------


class JetonAbsent(RuntimeError):
    pass


def lire_jeton() -> str | None:
    """Jeton ENTSO-E (`$ENTSOE_TOKEN`, sinon `source/entsoe_token`), ou None."""
    j = os.environ.get(VARIABLE_JETON, "").strip()
    if j:
        return j
    if FICHIER_JETON.is_file():
        j = FICHIER_JETON.read_text(encoding="utf-8").strip()
        return j or None
    return None


MESSAGE_SANS_JETON = (
    "jeton ENTSO-E absent : définir la variable d'environnement ENTSOE_TOKEN ou écrire le jeton dans "
    "source/entsoe_token (dossier privé, non versionné). Les autres sources et `pc build` / `pc check` "
    "fonctionnent sans lui.")


def masquer(texte: str, jeton: str | None) -> str:
    """Retire le jeton d'un texte (message d'erreur, URL)."""
    t = str(texte)
    if jeton:
        t = t.replace(jeton, "***")
    return re.sub(r"(securityToken=)[^&\s'\"]+", r"\1***", t)


def url_publique(params: dict) -> str:
    """URL notée au manifeste : paramètres de la requête, jeton masqué."""
    return f"{API}?{urlencode(params)}&securityToken=***"


# --------------------------------------------------------------------------
# Téléchargement
# --------------------------------------------------------------------------


def debut_annee_utc(annee: int) -> datetime:
    """1er janvier 00:00 heure de Paris (toujours CET, UTC+1) en UTC."""
    return datetime(annee - 1, 12, 31, 23, tzinfo=timezone.utc)


def fenetre(annee: int, aujourd_hui: date) -> tuple[str, str]:
    """Fenêtre de requête (yyyyMMddHHmm, UTC) : l'année civile de Paris, tronquée à J+2 pour l'année en cours."""
    debut, fin = debut_annee_utc(annee), debut_annee_utc(annee + 1)
    if annee >= aujourd_hui.year:
        fin = min(fin, datetime(aujourd_hui.year, aujourd_hui.month, aujourd_hui.day, tzinfo=timezone.utc)
                  + timedelta(days=2))
    return debut.strftime("%Y%m%d%H%M"), fin.strftime("%Y%m%d%H%M")


def fichier_entsoe(raw: Path, serie: Serie, annee: int) -> Path:
    return raw / "entsoe" / serie.cle / serie.nom / f"{annee}.xml.gz"


def cle_manifeste(serie: Serie, annee: int) -> str:
    return f"{serie.cle}/{serie.nom}/{annee}"


def annees_serie(serie: Serie, aujourd_hui: date) -> range:
    premiere, derniere = serie.annees
    return range(premiere, min(derniere or aujourd_hui.year, aujourd_hui.year) + 1)


def annee_close(entree: dict | None, annee: int, aujourd_hui: date) -> bool:
    """Année déjà téléchargée et figée : close, et extraite après le 1er février de l'année suivante."""
    if entree is None or annee >= aujourd_hui.year:
        return False
    extrait = datetime.fromisoformat(entree["extrait_le"]).date()
    return extrait >= date(annee + 1, MOIS_MARGE_CLOTURE, 1)


def motif_acquittement(contenu: bytes) -> str | None:
    """Texte du motif si la réponse est un `Acknowledgement_MarketDocument`, sinon None."""
    tete = contenu[:400]
    if b"Acknowledgement_MarketDocument" not in tete:
        return None
    m = re.search(rb"<text>([^<]*)</text>", contenu)
    return m.group(1).decode("utf-8", "replace") if m else "(motif absent)"


AUCUNE_DONNEE = "No matching data found"


class ErreurEntsoe(RuntimeError):
    pass


def _requete(client, params: dict, jeton: str, journal) -> bytes:
    """GET avec relances ; renvoie le corps (XML). Lève `ErreurEntsoe` (message sans jeton)."""
    derniere = ""
    for essai in range(len(ATTENTES_RELANCE_S) + 1):
        attente = ATTENTES_RELANCE_S[min(essai, len(ATTENTES_RELANCE_S) - 1)]
        try:
            r = client.get(API, params={**params, "securityToken": jeton})
        except Exception as err:  # délai dépassé, réseau : relance (message masqué)
            derniere = masquer(f"{type(err).__name__}: {err}", jeton)
        else:
            if r.status_code == 200:
                return r.content
            corps = r.text[:2000]
            motif = (re.findall(r"<text>([^<]*)</text>", corps) or [corps[:200]])[0]
            derniere = masquer(f"HTTP {r.status_code} : {motif}", jeton)
            if r.status_code == 429:
                attente = int(r.headers.get("Retry-After", attente))
            elif r.status_code < 500 and not any(m in motif for m in PANNES_SERVEUR):
                raise ErreurEntsoe(derniere)  # 400 : paramètre refusé, inutile de relancer
        if essai < len(ATTENTES_RELANCE_S):
            journal(f"relance dans {attente} s ({derniere})")
            time.sleep(attente)
    raise ErreurEntsoe(f"échec après {len(ATTENTES_RELANCE_S) + 1} essais : {derniere}")


def telecharger_une(client, raw: Path, serie: Serie, annee: int, jeton: str, aujourd_hui: date) -> dict:
    """Télécharge une (série, année) ; écrit le XML compressé ; renvoie l'entrée de manifeste."""
    debut, fin = fenetre(annee, aujourd_hui)
    params = {**serie.parametres(), "periodStart": debut, "periodEnd": fin}
    nom = cle_manifeste(serie, annee)
    t0 = time.time()
    contenu = _requete(client, params, jeton, lambda m: print(f"  {nom} : {m}", file=sys.stderr))
    motif = motif_acquittement(contenu)
    if motif is not None and AUCUNE_DONNEE not in motif:
        raise ErreurEntsoe(masquer(f"acquittement inattendu : {motif}", jeton))
    dest = fichier_entsoe(raw, serie, annee)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    part.write_bytes(gzip.compress(contenu, compresslevel=6, mtime=0))
    part.replace(dest)
    points = contenu.count(b"<Point>")
    print(f"  {nom} : {len(contenu) / 1e6:.2f} Mo XML → {dest.stat().st_size / 1e6:.2f} Mo, {points} points"
          f"{' (vide : ' + motif + ')' if motif else ''}, {time.time() - t0:.0f} s", file=sys.stderr)
    entree = {
        "url": url_publique(params),
        "extrait_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nature": NATURES[serie.cle],
        "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
        "sha256_xml": hashlib.sha256(contenu).hexdigest(),
        "taille": dest.stat().st_size,
        "taille_xml": len(contenu),
        "lignes": points,
        "annee": annee,
        "licence": LICENCES[serie.cle]["licence"],
        "attribution": ATTRIBUTION,
    }
    if motif:
        entree["vide"] = motif
    return entree


def taches(raw: Path, cles: list[str], manifeste: dict, force: bool, aujourd_hui: date) -> list[tuple[Serie, int]]:
    """(série, année) à (re)télécharger, selon l'incrémental."""
    out = []
    for cle in cles:
        for serie in CATALOGUE[cle]:
            for annee in annees_serie(serie, aujourd_hui):
                dest = fichier_entsoe(raw, serie, annee)
                if not force and dest.exists() and annee_close(manifeste.get(cle_manifeste(serie, annee)), annee,
                                                                aujourd_hui):
                    continue
                out.append((serie, annee))
    return out


def download(raw: Path, cles: list[str], manifeste: dict, force: bool, aujourd_hui: date, maj_manifeste) -> list[str]:
    """Télécharge les clés ENTSO-E demandées, en parallèle. Renvoie la liste des échecs (messages
    sans jeton) ; lève `JetonAbsent` sans jeton."""
    import httpx

    jeton = lire_jeton()
    if not jeton:
        raise JetonAbsent(MESSAGE_SANS_JETON)
    a_faire = taches(raw, cles, manifeste, force, aujourd_hui)
    print(f"ENTSO-E : {len(a_faire)} requête(s) ({', '.join(cles)}), {PARALLELISME} en parallèle", file=sys.stderr)
    echecs: list[str] = []
    t0 = time.time()
    with httpx.Client(timeout=httpx.Timeout(DELAI_REQUETE_S, connect=60),
                      headers={"User-Agent": "pc-pipeline (open data)"}) as client, \
            ThreadPoolExecutor(PARALLELISME) as ex:
        futurs = {ex.submit(telecharger_une, client, raw, s, a, jeton, aujourd_hui): (s, a) for s, a in a_faire}
        for f in as_completed(futurs):
            serie, annee = futurs[f]
            nom = cle_manifeste(serie, annee)
            try:
                entree = f.result()
            except Exception as err:
                msg = masquer(f"{nom} : {type(err).__name__}: {err}", jeton)
                print(f"  ÉCHEC {msg}", file=sys.stderr)
                echecs.append(msg)
                continue
            maj_manifeste(raw, nom, entree)  # thread principal : pas d'écriture concurrente
    print(f"ENTSO-E : {len(a_faire) - len(echecs)} fichier(s) en {time.time() - t0:.0f} s, {len(echecs)} échec(s)",
          file=sys.stderr)
    return echecs


# --------------------------------------------------------------------------
# Lecture des XML
# --------------------------------------------------------------------------

#: Règles de lecture appliquées par `lire_document` et `normaliser` (reprises dans le rapport).
REGLES_LECTURE = {
    "resolution": "lue par Period (PT15M, PT30M, PT60M) : une réponse annuelle mêle les résolutions",
    "a03": "curveType A03 : une position omise répète la valeur précédente jusqu'à la fin de la Period ; "
           "une Period sans position 1 laisse vides les positions qui précèdent son premier point",
    "positions": "nombre de positions = (end − start) / résolution (jours de 23 h et de 25 h)",
    "horodatage": "début de période, UTC (timeInterval/start + (position − 1) × résolution)",
    "sequences_a44": "A44 : à chaque instant, la série sans `classificationSequence_AttributeInstanceComponent."
                     "position` si elle existe, sinon la séquence 1 ; les autres séquences (enchères hors SDAC) sont "
                     "écartées. ES (depuis le 05/09/2025) : série sans séquence = energy-charts, séquences 1-3 "
                     "différentes ; DE-LU : séquence 1 = energy-charts, séquence 2 différente (constaté le 2026-11-26, "
                     "voir entsoe_derive.selection_sdac)",
    "quarts_repetes": "A44 avant la livraison du 01/10/2025 (SDAC quart-horaire) : une heure publiée en PT15M dont "
                      "les quatre quarts sont égaux est ramenée à un point horaire (cas du 30/09/2025) ; des quarts "
                      "différents sont gardés et signalés",
    "production": "A75 : série de production si `inBiddingZone_Domain`, de consommation (pompage, stockage) "
                  "si `outBiddingZone_Domain` ; jamais additionnées",
    "doublons": "un même (série, filière, sens, instant) lu deux fois (recouvrement de deux années) : la valeur "
                "du fichier le plus récent est gardée ; un conflit de valeurs est compté et signalé",
}

BASCULE_SDAC_15MIN = datetime(2025, 9, 30, 22, tzinfo=timezone.utc)  # = build.BASCULE_PRIX_15MIN
RESOLUTIONS = {"PT15M": 15, "PT30M": 30, "PT60M": 60}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _instant(texte: str) -> datetime:
    return datetime.strptime(texte.strip(), "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)


def lire_document(source) -> dict:
    """Lit un document ENTSO-E (chemin .xml / .xml.gz, ou octets). Renvoie :

    `{"type": "A44"…, "vide": motif | None, "series": [{"meta": {...}, "points": [(debut, pas_min, valeur,
    publie)]}]}` où `publie` est faux pour une valeur répétée par la règle A03. Lecture incrémentale
    (iterparse, une TimeSeries à la fois) : les A75 des voisins dépassent 70 Mo de XML par an.
    """
    if isinstance(source, (bytes, bytearray)):
        import io
        flux = io.BytesIO(gzip.decompress(source) if source[:2] == b"\x1f\x8b" else bytes(source))
    else:
        p = Path(source)
        flux = gzip.open(p, "rb") if p.suffix == ".gz" else p.open("rb")
    doc = {"type": None, "vide": None, "series": []}
    profondeur = 0
    with flux:
        for evt, el in ET.iterparse(flux, events=("start", "end")):
            if evt == "start":
                profondeur += 1
                continue
            profondeur -= 1
            nom = _local(el.tag)
            if profondeur == 1 and nom == "type":
                doc["type"] = (el.text or "").strip()
            elif nom == "Reason":
                doc["vide"] = next(((x.text or "").strip() for x in el if _local(x.tag) == "text"), "")
            elif nom == "TimeSeries":
                doc["series"].append(_lire_serie(el))
                el.clear()
    return doc


#: Champs gardés d'une TimeSeries (enfants directs, et `MktPSRType/psrType`).
CHAMPS_SERIE = ("in_Domain.mRID", "out_Domain.mRID", "inBiddingZone_Domain.mRID", "outBiddingZone_Domain.mRID",
                "curveType", "currency_Unit.name", "price_Measure_Unit.name", "quantity_Measure_Unit.name",
                "businessType", "auction.type", "classificationSequence_AttributeInstanceComponent.position")


def _lire_serie(ts) -> dict:
    """Une TimeSeries : métadonnées et Periods brutes (positions et valeurs publiées, sans dépliage)."""
    ns = ts.tag[: ts.tag.index("}") + 1] if "}" in ts.tag else ""
    meta = {}
    for x in ts:
        n = _local(x.tag)
        if n in CHAMPS_SERIE:
            meta[n] = (x.text or "").strip()
        elif n == "MktPSRType":
            meta["psrType"] = (x.findtext(f"{ns}psrType") or "").strip()
    periodes = []
    for p in ts.findall(f"{ns}Period"):
        res = (p.findtext(f"{ns}resolution") or "").strip()
        if res not in RESOLUTIONS:
            raise ValueError(f"résolution inconnue : {res!r}")
        debut, fin, pas = _instant(p.findtext(f"{ns}timeInterval/{ns}start")), \
            _instant(p.findtext(f"{ns}timeInterval/{ns}end")), RESOLUTIONS[res]
        n = int((fin - debut).total_seconds() // 60 // pas)  # jours de 23 h / 25 h compris
        pos, val = [], []
        for pt in p.findall(f"{ns}Point"):
            v = pt.findtext(f"{ns}price.amount")
            if v is None:
                v = pt.findtext(f"{ns}quantity")
            pos.append(int(pt.findtext(f"{ns}position")))
            val.append(float(v))
        if pos and (max(pos) > n or min(pos) < 1):
            raise ValueError(f"position hors de [1, {n}] dans une Period de {debut} à {fin}")
        if len(set(pos)) != len(pos):
            raise ValueError(f"position répétée dans une Period de {debut} à {fin}")
        periodes.append({"start": debut, "pas": pas, "n": n, "pos": pos, "val": val})
    return {"meta": meta, "periodes": periodes}


def deplier(series: list[dict]):
    """Points de plusieurs TimeSeries (polars) : `ts` (indice de la série), `debut_utc`, `pas_min`, `valeur`,
    `publie`. Toutes les positions 1…n de chaque Period ; règle A03 (`curveType` A03 : une position omise
    répète la valeur précédente, jusqu'à la fin de la Period ; avant le premier point publié : rien) ;
    autre courbe : seulement les points publiés. Début = start + (position − 1) × pas."""
    import polars as pl
    per, p_per, p_pos, p_val = [], [], [], []
    k = 0
    for i, ts in enumerate(series):
        a03 = ts["meta"].get("curveType", "A01") == "A03"
        for p in ts["periodes"]:
            per.append((i, k, p["start"], p["pas"], p["n"], a03))
            p_per.extend([k] * len(p["pos"]))
            p_pos.extend(p["pos"])
            p_val.extend(p["val"])
            k += 1
    utc = pl.Datetime("us", "UTC")
    P = pl.DataFrame(per, schema={"ts": pl.Int32, "per": pl.Int32, "start": utc, "pas": pl.Int16, "n": pl.Int32,
                                  "a03": pl.Boolean}, orient="row")
    V = pl.DataFrame({"per": p_per, "pos": p_pos, "valeur": p_val},
                     schema={"per": pl.Int32, "pos": pl.Int32, "valeur": pl.Float64})
    g = (P.with_columns(pl.int_ranges(1, pl.col("n") + 1, dtype=pl.Int32).alias("pos")).explode("pos")
          .drop_nulls("pos")
          .join(V, on=["per", "pos"], how="left").sort(["per", "pos"])
          .with_columns(pl.col("valeur").is_not_null().alias("publie"))
          .with_columns(pl.when(pl.col("a03")).then(pl.col("valeur").forward_fill().over("per"))
                          .otherwise(pl.col("valeur")).alias("valeur"))
          .filter(pl.col("valeur").is_not_null()))
    return g.select("ts", (pl.col("start") + pl.duration(minutes=(pl.col("pos") - 1) * pl.col("pas")))
                    .alias("debut_utc"), pl.col("pas").alias("pas_min"), "valeur", "publie")


def points(ts: dict) -> list[tuple]:
    """Points d'une TimeSeries : [(début UTC, pas en min, valeur, publiée ?)] (via `deplier`)."""
    return [tuple(r) for r in deplier([ts]).select("debut_utc", "pas_min", "valeur", "publie").iter_rows()]
