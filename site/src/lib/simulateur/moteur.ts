// Moteur du simulateur : réimplémentation en TypeScript de pipeline/pc/quand.py (implémentation de
// référence). Fonctions pures, sans dépendance, exécutées dans le navigateur.
//
// Mêmes règles que la référence, à reproduire à l'identique (voir l'en-tête de quand.py) :
// - une heure est **valide** pour un indicateur si toutes ses entrées sont renseignées (null =
//   donnée absente, jamais imputée) ; sommes et moyennes sur les heures valides ;
// - énergie : Σ des MW moyens horaires × 1 h = MWh ; TWh = MWh / 10⁶ ;
// - classement des heures tendues : RN décroissant, puis `heure_utc` croissante (chaînes ISO de
//   même format : l'ordre lexicographique est l'ordre chronologique) ;
// - quantiles de type 7 (interpolation linéaire entre rangs) ;
// - comparaisons strictes là où la référence les écrit (RN + charge > RN max, prix < 0).
//
// Les sorties portent les **noms de la référence** (snake_case) : le test de parité
// (moteur.test.ts) les compare chemin par chemin aux cas partagés de pipeline/tests/cas_quand.json.

/** Table horaire d'une année : colonnes de même longueur, une ligne par heure UTC. */
export interface TableHoraire {
  /** Début de l'heure, ISO 8601 en UTC (« 2025-01-14T07:00Z »). */
  heure_utc: string[];
  consommation: (number | null)[];
  eolien: (number | null)[];
  solaire: (number | null)[];
  nucleaire: (number | null)[];
  nucleaire_disponible: (number | null)[];
  /** EUR/MWh, day-ahead France. */
  prix?: (number | null)[];
  /** Solde des échanges physiques, positif = import. */
  ech_physiques?: (number | null)[];
  /**
   * Nucléaire disponible déclaré en réintégrant les arrêts et baisses qu'EDF déclare indisponibles
   * pour modulation (COLONNE_REINTEGRE de la référence) ; facultatif.
   */
  nucleaire_disponible_reintegre?: (number | null)[];
}

export const N_MONOTONE_EXACT = 100;
/** Plancher retranché à J (MW) pour `part_dans_j_plancher` : hypothèse du site (PLANCHER_J_MW). */
export const PLANCHER_J_MW = 1000;
/** Seuil de prix « cher » (EUR/MWh), choisi par le site (SEUIL_PRIX_CHER_EUR_MWH). */
export const SEUIL_PRIX_CHER_EUR_MWH = 150;
export const PAS_MONOTONE = 20;
/** Durée de l'épisode de froid (heures consécutives), choix du site (DUREE_FROID_H). */
export const DUREE_FROID_H = 168;

/** Une monotone : [rang (1 = la plus élevée), valeur]. */
export type Monotone = [number, number][];

/** Un instant remarquable : valeur, heure UTC de début, même instant en heure légale de Paris. */
export interface Instant {
  valeur_mw: number;
  heure_utc: string;
  debut_paris: string;
}

/* ---------- Briques ---------- */

/** RN (MW) d'une heure : consommation − éolien − solaire − nucléaire disponible ; null si une entrée manque. */
export function chargeResiduelle(
  consommation: number | null,
  eolien: number | null,
  solaire: number | null,
  nucleaireDisponible: number | null
): number | null {
  if (consommation === null || eolien === null || solaire === null || nucleaireDisponible === null)
    return null;
  return consommation - eolien - solaire - nucleaireDisponible;
}

/** J (MW) d'une heure : nucléaire disponible déclaré non produit, borné à 0 ; null si une entrée manque. */
export function jeuNucleaire(
  nucleaireDisponible: number | null,
  nucleaire: number | null
): number | null {
  if (nucleaireDisponible === null || nucleaire === null) return null;
  return Math.max(0, nucleaireDisponible - nucleaire);
}

/** Quantile d'ordre q de valeurs **triées par ordre croissant** (type 7). */
export function quantile(tries: readonly number[], q: number): number {
  if (!tries.length) throw new Error('quantile d’une liste vide');
  const h = (tries.length - 1) * q;
  const i = Math.floor(h);
  if (i + 1 >= tries.length) return tries[tries.length - 1];
  return tries[i] + (h - i) * (tries[i + 1] - tries[i]);
}

/**
 * Monotone décroissante sous-échantillonnée : rangs 1 à `nExact` exacts, puis `nExact + pas`,
 * `nExact + 2 pas`… et toujours le dernier rang.
 */
export function monotone(
  valeurs: readonly number[],
  nExact = N_MONOTONE_EXACT,
  pas = PAS_MONOTONE
): Monotone {
  const d = [...valeurs].sort((a, b) => b - a);
  const n = d.length;
  const rangs: number[] = [];
  for (let r = 1; r <= Math.min(nExact, n); r++) rangs.push(r);
  for (let r = nExact + pas; r <= n; r += pas) rangs.push(r);
  if (n && rangs[rangs.length - 1] !== n) rangs.push(n);
  return rangs.map((r) => [r, d[r - 1]]);
}

const moyenne = (xs: readonly number[]): number | null =>
  xs.length ? xs.reduce((s, x) => s + x, 0) / xs.length : null;

const deuxChiffres = (n: number) => String(n).padStart(2, '0');

let formatParis: Intl.DateTimeFormat | undefined;

/**
 * Même instant en heure légale de Paris, au format de la référence (`datetime.isoformat`,
 * minutes) : « 2025-01-14T07:00Z » → « 2025-01-14T08:00+01:00 ».
 */
export function debutParis(isoUtc: string): string {
  const t = Date.parse(isoUtc);
  if (Number.isNaN(t) || !/(Z|[+-]\d{2}:\d{2})$/.test(isoUtc))
    throw new Error(`heure sans fuseau ou illisible : ${isoUtc}`);
  formatParis ??= new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/Paris',
    hourCycle: 'h23',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
  const p = Object.fromEntries(
    formatParis.formatToParts(new Date(t)).map((x) => [x.type, Number(x.value)])
  ) as Record<string, number>;
  const local = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute);
  const decalage = Math.round((local - t) / 60_000);
  const signe = decalage < 0 ? '-' : '+';
  const a = Math.abs(decalage);
  return (
    `${p.year}-${deuxChiffres(p.month)}-${deuxChiffres(p.day)}T${deuxChiffres(p.hour)}:` +
    `${deuxChiffres(p.minute)}${signe}${deuxChiffres(Math.floor(a / 60))}:${deuxChiffres(a % 60)}`
  );
}

function instant(heuresUtc: readonly string[], i: number, v: number): Instant {
  return { valeur_mw: v, heure_utc: heuresUtc[i], debut_paris: debutParis(heuresUtc[i]) };
}

/** Comparaison de deux chaînes ISO de même format (ordre chronologique). */
const avant = (a: string, b: string): number => (a < b ? -1 : a > b ? 1 : 0);

/** RN et J de chaque heure d'une table, après contrôle des longueurs. */
export function series(table: TableHoraire): { rn: (number | null)[]; j: (number | null)[] } {
  const n = table.heure_utc.length;
  for (const [c, v] of Object.entries(table))
    if (v !== undefined && (v as unknown[]).length !== n)
      throw new Error(`colonne ${c} : ${(v as unknown[]).length} valeurs pour ${n} heures`);
  const rn = table.heure_utc.map((_, i) =>
    chargeResiduelle(
      table.consommation[i],
      table.eolien[i],
      table.solaire[i],
      table.nucleaire_disponible[i]
    )
  );
  const j = table.heure_utc.map((_, i) =>
    jeuNucleaire(table.nucleaire_disponible[i], table.nucleaire[i])
  );
  return { rn, j };
}

/** J_r de chaque heure (disponible réintégré non produit), ou null sans la colonne (`j_reintegre`). */
export function jReintegre(table: TableHoraire): (number | null)[] | null {
  const d = table.nucleaire_disponible_reintegre;
  if (!d) return null;
  return table.heure_utc.map((_, i) => jeuNucleaire(d[i], table.nucleaire[i]));
}

/** Grandeurs des charges plates recalculées avec J_r (CLES_CHARGE_REINTEGRE). */
export interface ChargePlateReintegree {
  x_mw: number;
  energie_dans_j_twh: number;
  part_dans_j: number | null;
  heures_j_superieur_ou_egal_x: number;
  energie_dans_j_plancher_twh: number;
  part_dans_j_plancher: number | null;
}

/** Part d'une charge dans J_r, après le supplément (`_dans_j` de la référence). */
export interface DansJ {
  energie_dans_j_twh: number;
  part_dans_j: number | null;
  energie_dans_j_plancher_twh: number;
  part_dans_j_plancher: number | null;
  heures_j_couvre_charge: number;
}

function dansJ(
  js: readonly (number | null)[],
  charge: readonly number[],
  plancherMw: number
): DansJ {
  let base = 0;
  let tenu = 0;
  let tenuPlancher = 0;
  let couvre = 0;
  for (let i = 0; i < js.length; i++) {
    const v = js[i];
    if (v === null) continue;
    base += charge[i];
    tenu += Math.min(charge[i], v);
    tenuPlancher += Math.min(charge[i], Math.max(0, v - plancherMw));
    if (charge[i] > 0 && v >= charge[i]) couvre++;
  }
  return {
    energie_dans_j_twh: tenu / 1e6,
    part_dans_j: base > 0 ? tenu / base : null,
    energie_dans_j_plancher_twh: tenuPlancher / 1e6,
    part_dans_j_plancher: base > 0 ? tenuPlancher / base : null,
    heures_j_couvre_charge: couvre
  };
}

/** Indices des heures où RN est renseignée, de la plus tendue à la moins tendue. */
export function classementTendues(
  heuresUtc: readonly string[],
  rn: readonly (number | null)[]
): number[] {
  const idx: number[] = [];
  for (let i = 0; i < rn.length; i++) if (rn[i] !== null) idx.push(i);
  return idx.sort(
    (a, b) => (rn[b] as number) - (rn[a] as number) || avant(heuresUtc[a], heuresUtc[b])
  );
}

/* ---------- Charge plate (comme indicateurs_annee) ---------- */

export interface ChargePlate {
  x_mw: number;
  energie_ajoutee_twh: number;
  energie_dans_j_twh: number;
  part_dans_j: number | null;
  heures_j_superieur_ou_egal_x: number;
  rn_max_plus_x_mw: number | null;
  heures_rn_plus_x_au_dessus_du_max: number | null;
  solde_echanges_moyen_heures_j_ge_x_mw: number | null;
  plancher_mw: number;
  energie_dans_j_plancher_twh: number;
  part_dans_j_plancher: number | null;
  heures_rn_plus_x_au_dessus_du_max_reference: number | null;
}

/** Charge constante de `xMw` MW (comme `charge_plate` de la référence). */
export function chargePlate(
  rn: readonly (number | null)[],
  j: readonly (number | null)[],
  xMw: number,
  heures: number = rn.length,
  solde?: readonly (number | null)[],
  plancherMw: number = PLANCHER_J_MW,
  rnMaxReferenceMw: number | null = null
): ChargePlate {
  if (!(xMw > 0)) throw new Error('charge plate nulle ou négative');
  const jv = j.filter((v): v is number => v !== null);
  const rnv = rn.filter((v): v is number => v !== null);
  const tenu = jv.reduce((s, v) => s + Math.min(xMw, v), 0);
  const tenuPlancher = jv.reduce((s, v) => s + Math.min(xMw, Math.max(0, v - plancherMw)), 0);
  const rnMax = rnv.length ? Math.max(...rnv) : null;
  const soldes: number[] = [];
  if (solde)
    j.forEach((v, i) => {
      const e = solde[i];
      if (v !== null && e !== null && v >= xMw) soldes.push(e);
    });
  return {
    x_mw: xMw,
    energie_ajoutee_twh: (xMw * heures) / 1e6,
    energie_dans_j_twh: tenu / 1e6,
    part_dans_j: jv.length ? tenu / (xMw * jv.length) : null,
    heures_j_superieur_ou_egal_x: jv.filter((v) => v >= xMw).length,
    rn_max_plus_x_mw: rnMax === null ? null : rnMax + xMw,
    heures_rn_plus_x_au_dessus_du_max:
      rnMax === null ? null : rnv.filter((v) => v + xMw > rnMax).length,
    solde_echanges_moyen_heures_j_ge_x_mw: moyenne(soldes),
    plancher_mw: plancherMw,
    energie_dans_j_plancher_twh: tenuPlancher / 1e6,
    part_dans_j_plancher: jv.length ? tenuPlancher / (xMw * jv.length) : null,
    heures_rn_plus_x_au_dessus_du_max_reference:
      rnMaxReferenceMw === null ? null : rnv.filter((v) => v + xMw > rnMaxReferenceMw).length
  };
}

/* ---------- Résumé d'une année : sous-ensemble d'indicateurs_annee ---------- */

/**
 * Les indicateurs d'`indicateurs_annee` dont le simulateur a besoin (charge résiduelle, heures
 * tendues classées, nucléaire disponible non produit, heures à prix bas, charges plates), sous les
 * mêmes noms. Ce qui n'y est pas (répartition des heures tendues par mois et par heure, couverture,
 * J par mois, RN et J moyens aux prix bas) n'est calculé que par la référence.
 */
export function resumeAnnee(
  table: TableHoraire,
  options: {
    charges_mw?: readonly number[];
    n_tendues?: number;
    n_exact?: number;
    pas_monotone?: number;
    plancher_j_mw?: number;
    seuil_prix_cher_eur_mwh?: number;
    rn_max_reference_mw?: number | null;
  } = {}
) {
  const {
    charges_mw = [],
    n_tendues = 100,
    n_exact = N_MONOTONE_EXACT,
    pas_monotone = PAS_MONOTONE,
    plancher_j_mw = PLANCHER_J_MW,
    seuil_prix_cher_eur_mwh = SEUIL_PRIX_CHER_EUR_MWH,
    rn_max_reference_mw = null
  } = options;
  const hu = table.heure_utc;
  const n = hu.length;
  const { rn, j } = series(table);
  const classe = classementTendues(hu, rn);
  const rnv = rn.filter((v): v is number => v !== null);
  const iMin = [...classe].sort(
    (a, b) => (rn[a] as number) - (rn[b] as number) || avant(hu[a], hu[b])
  )[0];
  const tries = [...rnv].sort((a, b) => a - b);
  const top = classe.slice(0, n_tendues);
  const jv = j.filter((v): v is number => v !== null);
  const prix = table.prix ?? new Array<number | null>(n).fill(null);
  const pv = prix.filter((v): v is number => v !== null);
  const cheres: number[] = [];
  prix.forEach((p, i) => {
    const v = j[i];
    if (p !== null && v !== null && p > seuil_prix_cher_eur_mwh) cheres.push(v);
  });
  const Q = {
    p01: 0.01,
    p05: 0.05,
    p10: 0.1,
    p25: 0.25,
    p50: 0.5,
    p75: 0.75,
    p90: 0.9,
    p95: 0.95,
    p99: 0.99
  };
  const jr = jReintegre(table);
  let jeuReintegre;
  if (jr && table.nucleaire_disponible_reintegre) {
    const jrv = jr.filter((v): v is number => v !== null);
    const dr = table.nucleaire_disponible_reintegre;
    let arrets = 0;
    dr.forEach((a, i) => {
      const b = table.nucleaire_disponible[i];
      if (a !== null && b !== null) arrets += a - b;
    });
    jeuReintegre = {
      heures_valides: jrv.length,
      somme_twh: jrv.reduce((s, v) => s + v, 0) / 1e6,
      heures_positif: jrv.filter((v) => v > 0).length,
      moyenne_mw: moyenne(jrv),
      arrets_modulation_courts_twh: arrets / 1e6,
      charges_plates: charges_mw.map((x): ChargePlateReintegree => {
        const c = chargePlate(rn, jr, x, n, undefined, plancher_j_mw);
        return {
          x_mw: c.x_mw,
          energie_dans_j_twh: c.energie_dans_j_twh,
          part_dans_j: c.part_dans_j,
          heures_j_superieur_ou_egal_x: c.heures_j_superieur_ou_egal_x,
          energie_dans_j_plancher_twh: c.energie_dans_j_plancher_twh,
          part_dans_j_plancher: c.part_dans_j_plancher
        };
      })
    };
  }
  return {
    heures: n,
    charge_residuelle: {
      heures_valides: rnv.length,
      ...(rnv.length
        ? {
            max: instant(hu, classe[0], rn[classe[0]] as number),
            min: instant(hu, iMin, rn[iMin] as number),
            moyenne_mw: moyenne(rnv),
            quantiles_mw: Object.fromEntries(
              Object.entries(Q).map(([k, q]) => [k, quantile(tries, q)])
            ) as Record<keyof typeof Q, number>,
            heures_negatives: rnv.filter((v) => v < 0).length,
            monotone: monotone(rnv, n_exact, pas_monotone)
          }
        : {})
    },
    heures_tendues: {
      n: top.length,
      rn_moyenne_mw: moyenne(top.map((i) => rn[i] as number)),
      rn_min_mw: top.length ? Math.min(...top.map((i) => rn[i] as number)) : null,
      heures: top.map((i) => [hu[i], rn[i]] as [string, number])
    },
    jeu_nucleaire: {
      heures_valides: jv.length,
      somme_twh: jv.reduce((s, v) => s + v, 0) / 1e6,
      heures_positif: jv.filter((v) => v > 0).length,
      moyenne_mw: moyenne(jv),
      prix_chers: {
        seuil_eur_mwh: seuil_prix_cher_eur_mwh,
        heures: cheres.length,
        j_moyenne_mw: moyenne(cheres)
      }
    },
    charges_plates: charges_mw.map((x) =>
      chargePlate(rn, j, x, n, table.ech_physiques, plancher_j_mw, rn_max_reference_mw)
    ),
    prix: {
      heures_valides: pv.length,
      heures_negatif: pv.filter((p) => p < 0).length,
      heures_nul_ou_negatif: pv.filter((p) => p <= 0).length
    },
    ...(jeuReintegre ? { jeu_nucleaire_reintegre: jeuReintegre } : {})
  };
}

/** Maximum de plusieurs maxima annuels : valeur la plus élevée, puis heure UTC la plus ancienne
 * (comme `max_pluriannuel` de la référence) ; l'année d'origine est ajoutée. */
export function maxPluriannuel(
  maxima: Record<string, Instant | null>
): (Instant & { annee: string }) | null {
  let meilleur: (Instant & { annee: string }) | null = null;
  for (const [annee, m] of Object.entries(maxima)) {
    if (!m) continue;
    if (
      !meilleur ||
      m.valeur_mw > meilleur.valeur_mw ||
      (m.valeur_mw === meilleur.valeur_mw && avant(m.heure_utc, meilleur.heure_utc) < 0)
    )
      meilleur = { ...m, annee };
  }
  return meilleur;
}

/* ---------- Simulateur ---------- */

/**
 * Charge ajoutée heure par heure : X partout, 0 pendant les `heuresEffacement` heures **valides**
 * (RN renseignée) où RN observée est la plus élevée. Prévision parfaite : borne optimiste. Une heure
 * où RN manque n'est pas classée et garde X.
 */
export function profilEffacement(
  heuresUtc: readonly string[],
  rn: readonly (number | null)[],
  xMw: number,
  heuresEffacement = 0
): number[] {
  if (!(xMw >= 0)) throw new Error('puissance ajoutée négative');
  if (!(heuresEffacement >= 0) || !Number.isInteger(heuresEffacement))
    throw new Error('nombre d’heures d’effacement négatif ou non entier');
  const charge = new Array<number>(rn.length).fill(xMw);
  for (const i of classementTendues(heuresUtc, rn).slice(0, heuresEffacement)) charge[i] = 0;
  return charge;
}

export interface EffetCharge {
  heures: number;
  energie_ajoutee_twh: number;
  heures_charge_nulle: number;
  heures_j_valides: number;
  energie_dans_j_twh: number;
  part_dans_j: number | null;
  plancher_mw: number;
  energie_dans_j_plancher_twh: number;
  part_dans_j_plancher: number | null;
  heures_j_couvre_charge: number;
  solde_echanges_moyen_heures_j_couvre_mw: number | null;
  heures_rn_valides: number;
  rn_max_mw: number | null;
  /** Heure du maximum observé (même départage que les heures tendues). */
  rn_max_heure_utc: string | null;
  max_apres: Instant | null;
  heures_au_dessus_du_max: number | null;
  rn_max_reference_mw: number | null;
  heures_au_dessus_du_max_reference: number | null;
  heures_prix_valides: number;
  energie_prix_valide_twh: number;
  part_prix_negatif: number | null;
  part_prix_nul_ou_negatif: number | null;
  prix_moyen_pondere_eur_mwh: number | null;
  prix_moyen_eur_mwh: number | null;
  heures_prix_nul_ou_negatif_charge: number;
  heures_prix_nul_ou_negatif_j_couvre: number;
  monotone_avant: Monotone;
  monotone_apres: Monotone;
  /** Point 2 recalculé avec J_r (arrêts pour modulation réintégrés) ; null sans J_r. */
  reintegre: DansJ | null;
}

/** Ce qu'une charge ajoutée (MW par heure) rencontre dans une année observée (`effet_charge`). */
export function effetCharge(
  heuresUtc: readonly string[],
  rn: readonly (number | null)[],
  j: readonly (number | null)[],
  prix: readonly (number | null)[],
  charge: readonly number[],
  solde?: readonly (number | null)[],
  nExact = N_MONOTONE_EXACT,
  pas = PAS_MONOTONE,
  plancherMw = PLANCHER_J_MW,
  rnMaxReferenceMw: number | null = null,
  supplement?: readonly number[],
  jReint?: readonly (number | null)[] | null
): EffetCharge {
  const n = heuresUtc.length;
  for (const [nom, v] of [
    ['rn', rn],
    ['j', j],
    ['prix', prix],
    ['charge', charge]
  ] as const)
    if (v.length !== n) throw new Error(`${nom} : ${v.length} valeurs pour ${n} heures`);
  if (charge.some((c) => c === null || !(c >= 0)))
    throw new Error('charge ajoutée absente ou négative');
  const supp = supplement ?? new Array<number>(n).fill(0);
  if (supp.length !== n || supp.some((v) => v === null || !(v >= 0)))
    throw new Error('supplément absent, négatif ou de mauvaise longueur');
  // J laissé à la charge après le supplément (identique à J sans supplément).
  const js = j.map((v, i) => (v === null ? null : supp[i] === 0 ? v : Math.max(0, v - supp[i])));
  if (jReint && jReint.length !== n)
    throw new Error(`j_reintegre : ${jReint.length} valeurs pour ${n} heures`);
  const reintegre = jReint
    ? dansJ(
        jReint.map((v, i) => (v === null ? null : supp[i] === 0 ? v : Math.max(0, v - supp[i]))),
        charge,
        plancherMw
      )
    : null;

  // 2. Nucléaire disponible non produit
  let baseJ = 0;
  let tenu = 0;
  let tenuPlancher = 0;
  let heuresJ = 0;
  const soldes: number[] = [];
  let couvre = 0;
  for (let i = 0; i < n; i++) {
    const v = js[i];
    if (v === null) continue;
    heuresJ++;
    baseJ += charge[i];
    tenu += Math.min(charge[i], v);
    tenuPlancher += Math.min(charge[i], Math.max(0, v - plancherMw));
    if (charge[i] > 0 && v >= charge[i]) {
      couvre++;
      const e = solde?.[i] ?? null;
      if (e !== null) soldes.push(e);
    }
  }

  // 3. Charge résiduelle
  const avantVal: number[] = [];
  const apresVal: number[] = [];
  let rnMax: number | null = null;
  let iRnMax = -1;
  let iMax = -1;
  for (let i = 0; i < n; i++) {
    const v = rn[i];
    if (v === null) continue;
    const a = v + supp[i] + charge[i];
    avantVal.push(v);
    apresVal.push(a);
    if (rnMax === null || v > rnMax) {
      rnMax = v;
      iRnMax = i;
    }
    const m = iMax < 0 ? null : (rn[iMax] as number) + supp[iMax] + charge[iMax];
    if (m === null || a > m || (a === m && heuresUtc[i] < heuresUtc[iMax])) iMax = i;
  }
  const auDessus = rnMax === null ? null : apresVal.filter((a) => a > (rnMax as number)).length;

  // 4. Prix
  let baseP = 0;
  let neg = 0;
  let nulNeg = 0;
  let pondere = 0;
  let heuresBas = 0;
  let heuresBasCouvertes = 0;
  const prixValides: number[] = [];
  for (let i = 0; i < n; i++) {
    const p = prix[i];
    if (p === null) continue;
    prixValides.push(p);
    baseP += charge[i];
    pondere += charge[i] * p;
    if (p < 0) neg += charge[i];
    if (p <= 0) nulNeg += charge[i];
    if (p <= 0 && charge[i] > 0) {
      heuresBas++;
      const v = js[i];
      if (v !== null && v >= charge[i]) heuresBasCouvertes++;
    }
  }

  return {
    heures: n,
    energie_ajoutee_twh: charge.reduce((s, c) => s + c, 0) / 1e6,
    heures_charge_nulle: charge.filter((c) => c === 0).length,
    heures_j_valides: heuresJ,
    energie_dans_j_twh: tenu / 1e6,
    part_dans_j: baseJ > 0 ? tenu / baseJ : null,
    plancher_mw: plancherMw,
    energie_dans_j_plancher_twh: tenuPlancher / 1e6,
    part_dans_j_plancher: baseJ > 0 ? tenuPlancher / baseJ : null,
    heures_j_couvre_charge: couvre,
    solde_echanges_moyen_heures_j_couvre_mw: moyenne(soldes),
    heures_rn_valides: avantVal.length,
    rn_max_mw: rnMax,
    rn_max_heure_utc: iRnMax < 0 ? null : heuresUtc[iRnMax],
    max_apres:
      iMax < 0 ? null : instant(heuresUtc, iMax, (rn[iMax] as number) + supp[iMax] + charge[iMax]),
    heures_au_dessus_du_max: auDessus,
    rn_max_reference_mw: rnMaxReferenceMw,
    heures_au_dessus_du_max_reference:
      rnMaxReferenceMw === null ? null : apresVal.filter((a) => a > rnMaxReferenceMw).length,
    heures_prix_valides: prixValides.length,
    energie_prix_valide_twh: baseP / 1e6,
    part_prix_negatif: baseP > 0 ? neg / baseP : null,
    part_prix_nul_ou_negatif: baseP > 0 ? nulNeg / baseP : null,
    prix_moyen_pondere_eur_mwh: baseP > 0 ? pondere / baseP : null,
    prix_moyen_eur_mwh: moyenne(prixValides),
    heures_prix_nul_ou_negatif_charge: heuresBas,
    heures_prix_nul_ou_negatif_j_couvre: heuresBasCouvertes,
    monotone_avant: monotone(avantVal, nExact, pas),
    monotone_apres: monotone(apresVal, nExact, pas),
    reintegre
  };
}

export interface Simulation extends EffetCharge {
  x_mw: number;
  heures_effacement: number;
  /** Heures UTC effacées, de la plus tendue à la moins tendue (froid compris). */
  heures_effacees: string[];
  /** RN (froid compris) de la moins tendue des heures effacées ; null sans effacement. */
  rn_seuil_effacement_mw: number | null;
  /** X × heures effacées : énergie perdue, reportée ni dans le temps ni sur un autre site. */
  energie_effacee_twh: number;
  /** Production nucléaire observée de la table (heures renseignées). */
  production_nucleaire_twh: number;
  /** Froid supplémentaire (°C) et gradient (MW/°C) ; ajout = froid × gradient sur l'épisode. */
  froid_c: number;
  gradient_mw_par_c: number | null;
  froid_ajout_mw: number;
  froid_heures: number;
  froid_debut_utc: string | null;
  /** Début de la dernière heure de l'épisode. */
  froid_fin_utc: string | null;
  energie_froid_twh: number;
  /** Consommation maximale observée, et avec froid et charge ajoutés. */
  consommation_max_observee: Instant | null;
  consommation_max_apres: Instant | null;
}

/**
 * Épisode de froid : les `dureeH` lignes consécutives de RN observée moyenne la plus élevée
 * (`episode_froid` de la référence : moyenne des RN renseignées, sommées dans l'ordre ; fenêtre
 * sans RN écartée ; égalité → la plus ancienne ; table plus courte → toute la table).
 */
export function episodeFroid(rn: readonly (number | null)[], dureeH = DUREE_FROID_H): number[] {
  if (!(dureeH > 0) || !Number.isInteger(dureeH))
    throw new Error('durée de l’épisode de froid nulle, négative ou non entière');
  const n = rn.length;
  const longueur = Math.min(dureeH, n);
  let meilleur = -1;
  let mMeilleur = 0;
  for (let debut = 0; debut + longueur <= n; debut++) {
    let somme = 0;
    let k = 0;
    for (let i = debut; i < debut + longueur; i++) {
      const v = rn[i];
      if (v === null) continue;
      somme += v;
      k++;
    }
    if (!k) continue;
    const m = somme / k;
    if (meilleur < 0 || m > mMeilleur) {
      meilleur = debut;
      mMeilleur = m;
    }
  }
  return meilleur < 0 ? [] : Array.from({ length: longueur }, (_, k) => meilleur + k);
}

/**
 * Simulateur (docs/SIMULATEUR.md) : X MW ajoutés à toutes les heures, sauf pendant les
 * `heuresEffacement` heures valides de RN la plus élevée, froid compris ; en option, un froid
 * supplémentaire de `froidC` °C × `gradientMwParC` sur l'épisode (`simuler` de la référence).
 */
export function simuler(
  table: TableHoraire,
  xMw: number,
  heuresEffacement = 0,
  nExact = N_MONOTONE_EXACT,
  pasMonotone = PAS_MONOTONE,
  plancherMw = PLANCHER_J_MW,
  rnMaxReferenceMw: number | null = null,
  froidC = 0,
  gradientMwParC: number | null = null,
  dureeFroidH = DUREE_FROID_H
): Simulation {
  const hu = table.heure_utc;
  const n = hu.length;
  if (!(froidC >= 0)) throw new Error('froid supplémentaire négatif');
  if (froidC > 0 && (gradientMwParC === null || !(gradientMwParC > 0)))
    throw new Error('froid supplémentaire sans gradient positif');
  const { rn, j } = series(table);
  const episode = froidC > 0 ? episodeFroid(rn, dureeFroidH) : [];
  const ajout = froidC > 0 ? froidC * (gradientMwParC as number) : 0;
  const supplement = new Array<number>(n).fill(0);
  for (const i of episode) supplement[i] = ajout;
  // Classement des heures tendues du scénario : RN + froid.
  const rnS = rn.map((v, i) => (v === null ? null : v + supplement[i]));
  const charge = profilEffacement(hu, rnS, xMw, heuresEffacement);
  const effacees = classementTendues(hu, rnS).slice(0, heuresEffacement);
  const r = effetCharge(
    hu,
    rn,
    j,
    table.prix ?? new Array<number | null>(n).fill(null),
    charge,
    table.ech_physiques,
    nExact,
    pasMonotone,
    plancherMw,
    rnMaxReferenceMw,
    supplement,
    jReintegre(table)
  );
  // Consommation maximale, observée et avec froid et charge (même départage que les heures tendues).
  let iObs = -1;
  let iApres = -1;
  const conso = table.consommation;
  const apres = (i: number) => (conso[i] as number) + supplement[i] + charge[i];
  for (let i = 0; i < n; i++) {
    const c = conso[i];
    if (c === null) continue;
    if (iObs < 0 || c > (conso[iObs] as number) || (c === conso[iObs] && hu[i] < hu[iObs]))
      iObs = i;
    const a = apres(i);
    if (iApres < 0 || a > apres(iApres) || (a === apres(iApres) && hu[i] < hu[iApres])) iApres = i;
  }
  return {
    x_mw: xMw,
    heures_effacement: heuresEffacement,
    heures_effacees: effacees.map((i) => hu[i]),
    rn_seuil_effacement_mw: effacees.length ? (rnS[effacees[effacees.length - 1]] as number) : null,
    energie_effacee_twh: (xMw * effacees.length) / 1e6,
    production_nucleaire_twh:
      table.nucleaire.reduce<number>((s, v) => (v === null ? s : s + v), 0) / 1e6,
    froid_c: froidC,
    gradient_mw_par_c: gradientMwParC,
    froid_ajout_mw: ajout,
    froid_heures: episode.length,
    froid_debut_utc: episode.length ? hu[episode[0]] : null,
    froid_fin_utc: episode.length ? hu[episode[episode.length - 1]] : null,
    energie_froid_twh: (ajout * episode.length) / 1e6,
    consommation_max_observee: iObs < 0 ? null : instant(hu, iObs, conso[iObs] as number),
    consommation_max_apres: iApres < 0 ? null : instant(hu, iApres, apres(iApres)),
    ...r
  };
}
