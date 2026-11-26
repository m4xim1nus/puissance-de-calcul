"""Indisponibilités nucléaires déclarées par EDF au titre de REMIT → puissance disponible horaire.

Source : opendata.edf.fr (data-fair, Licence Ouverte 2.0), deux fichiers (`pc download edf_remit`) :

- l'**historique** depuis 2015 (export ponctuel, le dernier du 07/09/2026) ;
- la **liste courante** (indisponibilités non terminées il y a moins de trois mois, mise à jour
  toutes les heures).

Une ligne par **version** d'un événement : statut (`Active`, `Inactive` = version remplacée,
`Annulée`, `Supprimée`), identifiant, numéro de version, tranche, filière, début, fin, type,
cause, information complémentaire, puissance maximale (MW), puissance disponible (MW), date de
publication. Spécification et pièges : docs/spike/quand.md § 2.1.

Méthode (`evenements_nucleaires`, `segments_tranches`, `disponible_horaire`) :

1. union des deux fichiers ; pour un même couple (identifiant, version), la liste courante
   l'emporte (instantané plus récent) ;
2. **dernière version** de chaque événement ; l'événement est retenu si cette version est
   `Active` (une dernière version `Annulée` ou `Supprimée` l'écarte ; une exception documentée,
   `SUPPRESSIONS_ECARTEES`) ;
3. filière nucléaire, types `Planifiée` et `Fortuite` seulement : les « chroniques » (PMIN,
   aFRR) ne sont pas des indisponibilités (puissances à 0, texte libre) ;
4. par tranche et à chaque instant : **minimum** des puissances disponibles des événements qui
   le couvrent (règle d'EDF, description du jeu : « En cas de superposition d'indisponibilités,
   fortuites ou programmées, la pratique est de retenir la puissance disponible minimale »),
   borné à [0, puissance maximale] ; hors événement, la **puissance maximale** de la tranche ;
5. moyenne exacte sur chaque heure UTC (fonction en escalier intégrée, pas d'échantillonnage) ;
6. somme nationale des tranches **en exploitation** (`PERIODES_EXPLOITATION`).

Les dates sont lues en heure de Paris (`FUSEAU_REMIT`), hypothèse testée par `pc check`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

DATETIME_UTC = pl.Datetime("us", "UTC")

#: Fuseau des dates REMIT d'EDF. Non écrit dans la fiche du jeu ; établi par les tests de
#: `pc check` (`controle_fuseau_remit`) : voir le commentaire de ce contrôle.
FUSEAU_REMIT = "Europe/Paris"

#: En-têtes attendus, dans l'ordre (identiques dans les deux fichiers, aux guillemets près).
ENTETES = ["Status", "Identifiant", "Numéro de version", "Nom", "Filière", "Date de début",
           "Date de fin", "Type", "Cause", "Information complémentaire", "Puissance maximale (MW)",
           "Puissance disponible (MW)", "Date de publication"]
COLONNES = ["statut", "id", "version", "tranche", "filiere", "debut", "fin", "type", "cause", "info",
            "pmax", "pdispo", "publication"]
FORMATS_DATE = {"historique": "%d/%m/%Y %H:%M", "courante": "%Y-%m-%d %H:%M:%S"}
TYPES_INDISPONIBILITE = ["Planifiée", "Fortuite"]

#: Périmètre : le jeu couvre « EDF SA + Luminus » (contre-vérification du 26/11/2026,
#: docs/spike/quand-contre-verification.md § 1) : 1 311 lignes de l'historique viennent d'unités
#: belges de Luminus (Seraing, Ringvaart, Nobelwind ; identifiants `10000_LUM_…`, gaz et éolien en
#: mer, aucune nucléaire). On ne garde que les identifiants d'EDF SA, la filière nucléaire et les
#: tranches françaises ci-dessous ; une tranche nucléaire inconnue fait échouer la lecture (format
#: ou parc changé : à examiner, pas à absorber en silence).
PREFIXE_EDF_SA = "05470_EDF_"
TRANCHES_NUCLEAIRES = {
    *(f"BELLEVILLE {i}" for i in (1, 2)), *(f"BLAYAIS {i}" for i in (1, 2, 3, 4)),
    *(f"BUGEY {i}" for i in (2, 3, 4, 5)), *(f"CATTENOM {i}" for i in (1, 2, 3, 4)),
    *(f"CHINON {i}" for i in (1, 2, 3, 4)), *(f"CHOOZ {i}" for i in (1, 2)), *(f"CIVAUX {i}" for i in (1, 2)),
    *(f"CRUAS {i}" for i in (1, 2, 3, 4)), *(f"DAMPIERRE {i}" for i in (1, 2, 3, 4)),
    *(f"FESSENHEIM {i}" for i in (1, 2)), *(f"FLAMANVILLE {i}" for i in (1, 2, 3)),
    *(f"GOLFECH {i}" for i in (1, 2)), *(f"GRAVELINES {i}" for i in (1, 2, 3, 4, 5, 6)),
    *(f"NOGENT {i}" for i in (1, 2)), *(f"PALUEL {i}" for i in (1, 2, 3, 4)), *(f"PENLY {i}" for i in (1, 2)),
    *(f"ST ALBAN {i}" for i in (1, 2)), *(f"ST LAURENT {i}" for i in (1, 2)),
    *(f"TRICASTIN {i}" for i in (1, 2, 3, 4)),
}

#: Tranches dont l'exploitation commence ou s'arrête pendant la période couverte (heure de
#: Paris, bornes [début, fin) ; None = sans borne). Hors de ces périodes, la tranche ne compte ni
#: dans la puissance disponible ni dans la puissance maximale du parc. Toute autre tranche est
#: réputée en exploitation sur toute la période.
#:
#: - Fessenheim 1 et 2 : arrêt définitif le 22/02/2020 et dans la nuit du 29 au 30/06/2020.
#:   Instant retenu = fin du dernier événement REMIT de la tranche (baisse de charge avant
#:   l'arrêt : 21/02/2020 22:30 → 22/02/2020 02:00, puissance disponible 12 MW ; 29/06/2020
#:   18:30 → 23:30, 50 MW). Aucun événement ne la déclare indisponible ensuite : sans cette
#:   borne, elle compterait à pleine puissance jusqu'à aujourd'hui. RTE l'inclut « jusqu'à juin
#:   2020 » (Bilan électrique 2025, fig. 2.9).
#: - Flamanville 3 (EPR) : comptée à partir de son **premier événement REMIT** (18/12/2024
#:   13:50, avant le premier couplage au réseau du 21/12/2024). Avant, elle n'est pas déclarée :
#:   la compter à pleine puissance serait faux. RTE l'exclut de ses taux de disponibilité
#:   (« Le calcul exclut l'EPR de Flamanville qui est encore en phase d'essais », BE2025,
#:   fig. 2.5) : `pc check` compare donc le taux hors Flamanville 3 (`HORS_TAUX_RTE`).
PERIODES_EXPLOITATION: dict[str, tuple[datetime | None, datetime | None]] = {
    "FESSENHEIM 1": (None, datetime(2020, 2, 22, 2, 0)),
    "FESSENHEIM 2": (None, datetime(2020, 6, 29, 23, 30)),
    "FLAMANVILLE 3": (datetime(2024, 12, 18, 13, 50), None),
}
#: Tranches exclues du taux de disponibilité comparé à RTE (BE2025, fig. 2.5, hors EPR).
HORS_TAUX_RTE = {"FLAMANVILLE 3"}

#: Événements dont la **suppression** par EDF est écartée : on garde la dernière version avant
#: la suppression, comme si elle était active. Un seul cas, vérifié à la main :
#:
#: - `05470_EDF_T_00023936`, Golfech 1, arrêt programmé du 15/08/2020 02:00 au 12/12/2020 17:00
#:   (heure de Paris), puissance disponible 0 MW. Annoncé dès 2017 (version 1), mis à jour
#:   vingt fois, dont la version 20 publiée le 11/12/2020 21:52 qui fixe la fin au 12/12/2020
#:   17:00 ; version 21 « Supprimée » onze minutes plus tard, sans événement de remplacement.
#:   L'arrêt a pourtant eu lieu : l'événement suivant de la tranche (`05470_EDF_T_00051620`) est
#:   une « remontée par paliers » jusqu'au 15/12/2020, et RTE donne à la centrale de Golfech un
#:   taux de 78 % en 2020 (Bilan électrique 2025, fig. 2.9, p. 28), contre 94 % si l'on applique
#:   la suppression. Sans cette correction, le taux national 2020 s'écarte de RTE de +0,79 pt.
#:
#: Les autres suppressions ne sont pas touchées : appliquer cette règle à toutes dégrade
#: l'accord avec RTE sur les autres années (2021 : −0,8 pt ; 2025 : −1,9 pt), ce qui indique
#: que RTE les applique. Recherche systématique (2026-11-26) : parmi les événements supprimés
#: alors qu'ils étaient en cours et non couverts par un autre événement, c'est le seul de plus
#: de 150 heures (2 872 h ; les 87 autres durent de quelques heures à 141 h).
SUPPRESSIONS_ECARTEES: dict[str, str] = {
    "05470_EDF_T_00023936": "Golfech 1, arrêt du 15/08 au 12/12/2020 supprimé après coup, sans remplacement",
}


# --------------------------------------------------------------------------
# Lecture
# --------------------------------------------------------------------------


def local_vers_utc(e: pl.Expr, fuseau: str = FUSEAU_REMIT) -> pl.Expr:
    """Heure locale naïve → instant UTC.

    Heure inexistante (passage à l'heure d'été, 02:xx) : lue avec le décalage d'avant le
    changement (02:30 → 01:30 UTC, comme 03:30 en heure d'été). Heure ambiguë (passage à
    l'heure d'hiver, 02:xx deux fois) : la première occurrence (heure d'été), faute de mieux.
    """
    def conv(x: pl.Expr) -> pl.Expr:
        return x.dt.replace_time_zone(fuseau, ambiguous="earliest", non_existent="null").dt.convert_time_zone("UTC")
    # 02:30 en heure d'hiver (UTC+1) = 01:30 UTC = 03:30 en heure d'été : on convertit e + 1 h, sans rien retrancher.
    return pl.coalesce(conv(e), conv(e + pl.duration(hours=1))).cast(DATETIME_UTC)


def lire_csv(chemin: Path, fichier: str) -> pl.DataFrame:
    """Un fichier REMIT brut (latin-1, « ; », virgule décimale) → colonnes typées.

    `fichier` : « historique » ou « courante » (formats de date différents). Les dates restent
    en heure locale naïve (`debut_local`…) et sont converties en UTC (`debut`, `fin`,
    `publication`). Un en-tête inattendu lève une erreur : le format a changé.
    """
    df = pl.read_csv(chemin, separator=";", encoding="latin1", infer_schema_length=0, quote_char='"')
    if df.columns != ENTETES:
        raise ValueError(f"{chemin.name} : en-têtes inattendus {df.columns}")
    df.columns = COLONNES
    fmt = FORMATS_DATE[fichier]

    def nombre(c: str) -> pl.Expr:
        return pl.col(c).str.strip_chars().str.replace(",", ".").cast(pl.Float64, strict=True)

    def date(c: str) -> pl.Expr:
        return pl.col(c).str.strip_chars().str.strptime(pl.Datetime("us"), fmt, strict=True)

    return df.with_columns(
        pl.col("version").cast(pl.Int32, strict=True),
        nombre("pmax"), nombre("pdispo"),
        *[date(c).alias(f"{c}_local") for c in ("debut", "fin", "publication")],
        pl.lit(fichier).alias("fichier"),
    ).with_columns(
        *[local_vers_utc(pl.col(f"{c}_local")).alias(c) for c in ("debut", "fin", "publication")],
    )


def fusionner(hist: pl.DataFrame, cour: pl.DataFrame | None) -> pl.DataFrame:
    """Union des deux fichiers lus ; pour un même (identifiant, version), la liste courante l'emporte.

    Doublons exacts (même identifiant, même version) dans un même fichier : l'historique en
    contient (126 lignes en 2026, dont 39 nucléaires Planifiée/Fortuite), parfois avec des statuts
    différents (`Active` et `Inactive`) pour des dates et puissances identiques. On garde la ligne
    `Active` si elle existe : sans effet sur la reconstruction, qui ne lit que la dernière version.
    """
    df = pl.concat([hist] + ([cour] if cour is not None else []), how="vertical")
    rang = (pl.when(pl.col("fichier") == "courante").then(0).otherwise(1) * 2
            + pl.when(pl.col("statut") == "Active").then(0).otherwise(1))
    return (df.with_columns(rang.alias("_rang")).sort("id", "version", "_rang")
              .unique(subset=["id", "version"], keep="first", maintain_order=True).drop("_rang"))


# --------------------------------------------------------------------------
# Événements et reconstruction
# --------------------------------------------------------------------------


def evenements_nucleaires(brut: pl.DataFrame) -> pl.DataFrame:
    """Dernière version de chaque événement nucléaire Planifié/Fortuit, si elle est `Active`.

    Colonnes : `id`, `version`, `tranche`, `type`, `debut`, `fin` (UTC), `pmax`, `pdispo`
    (bornée à [0, pmax]), `publication`, `info`. Les événements de durée nulle ou négative sont
    écartés (aucun parmi les dernières versions actives en 2026).
    """
    nuc = brut.filter((pl.col("filiere") == "Nucléaire") & pl.col("id").str.starts_with(PREFIXE_EDF_SA))
    inconnues = set(nuc["tranche"].unique().to_list()) - TRANCHES_NUCLEAIRES
    if inconnues:
        raise ValueError(f"tranches nucléaires inconnues dans REMIT : {sorted(inconnues)}")
    # Les « chroniques » (PMIN, aFRR : Pmax = Pdispo = 0, 224 739 lignes en 2026) ne sont jamais
    # des arrêts : seuls les types Planifiée et Fortuite sont lus.
    n = nuc.filter(pl.col("type").is_in(TYPES_INDISPONIBILITE))
    # Suppressions écartées (`SUPPRESSIONS_ECARTEES`) : on retire la version « Supprimée » et on
    # garde la précédente, rendue active.
    ecartees = sorted(SUPPRESSIONS_ECARTEES)
    n = n.filter(~(pl.col("id").is_in(ecartees) & (pl.col("statut") == "Supprimée")))
    dernieres = n.sort("id", "version").group_by("id", maintain_order=True).last()
    dernieres = dernieres.with_columns(
        pl.when(pl.col("id").is_in(ecartees)).then(pl.lit("Active")).otherwise(pl.col("statut")).alias("statut"))
    return (dernieres.filter((pl.col("statut") == "Active") & (pl.col("fin") > pl.col("debut")))
                     .with_columns(pl.col("pdispo").clip(0, pl.col("pmax")))
                     .select("id", "version", "tranche", "type", "debut", "fin", "pmax", "pdispo",
                             "publication", "info")
                     .sort("tranche", "debut"))


def _utc(t: datetime | None) -> datetime | None:
    if t is None:
        return None
    return pl.select(local_vers_utc(pl.lit(t))).item().replace(tzinfo=timezone.utc)


def periodes_exploitation_utc(periodes: dict | None = None) -> dict[str, tuple[datetime | None, datetime | None]]:
    return {k: (_utc(a), _utc(b)) for k, (a, b) in (PERIODES_EXPLOITATION if periodes is None else periodes).items()}


def puissance_max_tranches(ev: pl.DataFrame) -> pl.DataFrame:
    """Puissance maximale de chaque tranche dans le temps : celle déclarée par l'événement le plus
    récent **par date de début**, prolongée jusqu'au suivant (et en arrière avant le premier).

    Une seule tranche a changé de puissance maximale déclarée : Flamanville 3 (1 620 MW jusqu'en
    septembre 2026, 1 600 MW ensuite). Colonnes : `tranche`, `depuis` (UTC), `pmax`.
    """
    p = (ev.sort("tranche", "debut").select("tranche", pl.col("debut").alias("depuis"), "pmax")
           .filter(pl.col("pmax") != pl.col("pmax").shift(1).over("tranche").fill_null(-1)))
    # la première valeur vaut aussi avant le premier événement
    return p.with_columns(pl.when(pl.col("depuis") == pl.col("depuis").min().over("tranche"))
                            .then(pl.lit(datetime(1900, 1, 1, tzinfo=timezone.utc)).cast(DATETIME_UTC))
                            .otherwise(pl.col("depuis")).alias("depuis"))


def segments_tranches(ev: pl.DataFrame, debut: datetime, fin: datetime,
                      periodes: dict | None = None) -> pl.DataFrame:
    """Puissance disponible de chaque tranche en escalier sur [debut, fin) (UTC).

    Une ligne par segment élémentaire où la puissance est constante : `tranche`, `t0`, `t1`,
    `dispo` (MW), `pmax` (MW). Les segments hors exploitation sont absents.
    """
    per = periodes_exploitation_utc(periodes)
    debut, fin = debut.astimezone(timezone.utc), fin.astimezone(timezone.utc)
    tranches = ev["tranche"].unique().sort().to_list()
    bornes = []
    for t in tranches:
        a, b = per.get(t, (None, None))
        a, b = max(a or debut, debut), min(b or fin, fin)
        if a < b:
            bornes.append((t, a, b))
    vie = pl.DataFrame(bornes, schema={"tranche": pl.Utf8, "vie0": DATETIME_UTC, "vie1": DATETIME_UTC}, orient="row")
    # points de rupture : bornes de vie, débuts et fins d'événements, changements de pmax
    pm = puissance_max_tranches(ev)
    points = pl.concat([
        vie.select("tranche", pl.col("vie0").alias("t")),
        vie.select("tranche", pl.col("vie1").alias("t")),
        ev.select("tranche", pl.col("debut").alias("t")),
        ev.select("tranche", pl.col("fin").alias("t")),
        pm.select("tranche", pl.col("depuis").alias("t")),
    ]).join(vie, on="tranche").filter((pl.col("t") >= pl.col("vie0")) & (pl.col("t") <= pl.col("vie1")))
    seg = (points.select("tranche", "t").unique().sort("tranche", "t")
                 .with_columns(pl.col("t").shift(-1).over("tranche").alias("t1"))
                 .drop_nulls("t1").rename({"t": "t0"}))
    # minimum des puissances disponibles des événements couvrant le segment
    couv = (seg.join(ev.select("tranche", "debut", "fin", "pdispo"), on="tranche")
               .filter((pl.col("debut") <= pl.col("t0")) & (pl.col("fin") >= pl.col("t1")))
               .group_by("tranche", "t0").agg(pl.col("pdispo").min()))
    seg = (seg.join(couv, on=["tranche", "t0"], how="left").sort("tranche", "t0")
              .join_asof(pm.sort("tranche", "depuis"), left_on="t0", right_on="depuis", by="tranche",
                         strategy="backward", check_sortedness=False)
              .with_columns(pl.min_horizontal(pl.coalesce("pdispo", "pmax"), pl.col("pmax")).alias("dispo")))
    return seg.select("tranche", "t0", "t1", "dispo", "pmax")


def horaire_depuis_segments(seg: pl.DataFrame, debut: datetime, fin: datetime) -> pl.DataFrame:
    """Moyennes horaires exactes (UTC) par tranche à partir des segments en escalier.

    Colonnes : `tranche`, `heure_utc`, `dispo` (MW moyen sur l'heure), `pmax` (MW moyen sur
    l'heure : une tranche en exploitation une demi-heure compte pour moitié), `minutes` (durée
    couverte). Les heures entièrement hors exploitation sont absentes.
    """
    s = seg.with_columns(
        pl.datetime_ranges(pl.col("t0").dt.truncate("1h"), pl.col("t1") - pl.duration(microseconds=1), "1h")
          .alias("heure_utc")).explode("heure_utc")
    fin_h = pl.col("heure_utc") + pl.duration(hours=1)
    duree = ((pl.min_horizontal(pl.col("t1"), fin_h) - pl.max_horizontal(pl.col("t0"), pl.col("heure_utc")))
             .dt.total_microseconds() / 3.6e9)
    s = s.with_columns(duree.alias("w"))
    h = (s.group_by("tranche", "heure_utc")
          .agg((pl.col("dispo") * pl.col("w")).sum().alias("dispo"), (pl.col("pmax") * pl.col("w")).sum().alias("pmax"),
               (pl.col("w").sum() * 60).round(6).alias("minutes")))
    return h.filter((pl.col("heure_utc") >= debut) & (pl.col("heure_utc") < fin)).sort("tranche", "heure_utc")


def disponible_horaire(ev: pl.DataFrame, debut: datetime, fin: datetime,
                       periodes: dict | None = None) -> pl.DataFrame:
    """Puissance disponible déclarée par tranche et par heure UTC sur [debut, fin)."""
    return horaire_depuis_segments(segments_tranches(ev, debut, fin, periodes), debut, fin)


def national(par_tranche: pl.DataFrame, exclure: set[str] | None = None) -> pl.DataFrame:
    """Somme nationale par heure : `nucleaire_disponible` et `nucleaire_pmax` (MW moyens)."""
    d = par_tranche.filter(~pl.col("tranche").is_in(sorted(exclure or set())))
    return (d.group_by("heure_utc").agg(pl.col("dispo").sum().alias("nucleaire_disponible"),
                                        pl.col("pmax").sum().alias("nucleaire_pmax"),
                                        pl.len().alias("tranches"))
             .sort("heure_utc"))


def taux_annuels(par_tranche: pl.DataFrame, exclure: set[str] | None = None) -> pl.DataFrame:
    """Taux de disponibilité annuel = Σ énergie disponible / Σ énergie maximale (année civile,
    heure de Paris), hors tranches `exclure`. Colonnes : `an`, `taux` (0-1), `heures`."""
    d = par_tranche.filter(~pl.col("tranche").is_in(sorted(exclure or set())))
    return (d.group_by(pl.col("heure_utc").dt.convert_time_zone("Europe/Paris").dt.year().alias("an"))
             .agg((pl.col("dispo").sum() / pl.col("pmax").sum()).alias("taux"),
                  pl.col("heure_utc").n_unique().alias("heures"))
             .sort("an"))


def bornes_fiables(h: pl.DataFrame, c: pl.DataFrame | None, extrait_courante: datetime | None) -> dict:
    """Ce que couvrent les deux fichiers, pour dater la série et détecter un trou entre eux.

    - `fin_historique` : dernière date de publication de l'historique (date de son export) ;
    - `debut_courante` : plus petite date de fin de la liste courante (elle ne garde que les
      événements terminés depuis moins de trois mois) ;
    - `trou` : vrai si la liste courante ne remonte plus jusqu'à l'export de l'historique. Les
      événements terminés entre les deux et publiés après l'export manqueraient alors.
    - `horizon` : dernière heure UTC pleine avant l'extraction de la liste courante ; au-delà,
      les déclarations sont des prévisions et la série est laissée vide.
    """
    fin_hist = h["publication"].max()
    deb_cour = c["fin"].min() if c is not None and c.height else None
    ref = extrait_courante or (c["publication"].max() if deb_cour is not None else fin_hist)
    horizon = ref.replace(minute=0, second=0, microsecond=0)
    return {
        "fin_historique": fin_hist,
        "fin_historique_local": h["publication_local"].max(),
        "debut_courante": deb_cour,
        "trou": deb_cour is None or deb_cour > fin_hist,
        "horizon": horizon,
    }


def depuis_raw(raw: Path) -> tuple[pl.DataFrame, pl.DataFrame, dict]:
    """Lecture des fichiers de `pc download edf_remit` : (brut, événements, bornes)."""
    from .sources import lire_manifeste, fichier_edf
    hist, cour = fichier_edf(raw, "historique"), fichier_edf(raw, "courante")
    if not hist.exists():
        raise FileNotFoundError(f"{hist} absent : lancer `pc download edf_remit`")
    h = lire_csv(hist, "historique")
    c = lire_csv(cour, "courante") if cour.exists() else None
    m = lire_manifeste(raw).get("edf_remit/courante") or {}
    extrait = datetime.fromisoformat(m["extrait_le"]).astimezone(timezone.utc) if m.get("extrait_le") else None
    brut = fusionner(h, c)
    return brut, evenements_nucleaires(brut), bornes_fiables(h, c, extrait)


def serie_nationale(raw: Path, debut: datetime, fin: datetime | None = None) -> tuple[pl.DataFrame, dict]:
    """Série nationale horaire (UTC) sur [debut, horizon) : `heure_utc`, `nucleaire_disponible`,
    `nucleaire_pmax`, `tranches`. Renvoie aussi les bornes (voir `bornes_fiables`)."""
    _, ev, bornes = depuis_raw(raw)
    fin = min(fin or bornes["horizon"], bornes["horizon"])
    par_tranche = disponible_horaire(ev, debut, fin)
    return national(par_tranche), bornes

