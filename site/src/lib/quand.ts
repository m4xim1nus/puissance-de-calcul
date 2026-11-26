// Données et calculs d'affichage des graphiques de l'enquête « Quand ? ». Les valeurs viennent de
// data/export/quand.json (calculé par `pc build`) ; ce module ne fait que les mettre en forme :
// MW → GW à une décimale, classes de couleur, statistiques mensuelles des matrices.
import { FINE, formaterDate, formaterNombre } from '$lib/format';

/** Une année de quand.json, réduite à ce qu'affichent les graphiques. */
export interface AnneeQuand {
  annee: number;
  heures: number;
  heuresValides: number;
  /** [rang, MW] ; rang 1 = heure de charge résiduelle la plus élevée. */
  monotone: [number, number][];
  maxMw: number;
  /** Début de l'heure du maximum, heure légale de Paris (ISO avec décalage). */
  maxDebutParis: string;
  minMw: number;
  minDebutParis: string;
  quantilesMw: Record<
    'p01' | 'p05' | 'p10' | 'p25' | 'p50' | 'p75' | 'p90' | 'p95' | 'p99',
    number
  >;
  /** Heures où la charge résiduelle est négative. */
  heuresNegatives: number;
  chargesPlates: {
    xMw: number;
    /** Part entre 0 et 1, borne haute. */
    partDansJ: number;
    heuresAuDessusDuMax: number;
  }[];
}

/** Matrice jour × heure de Paris de la charge résiduelle (MW) ; `null` = heure absente. */
export interface MatriceRn {
  annee: number;
  jours: string[];
  valeurs: (number | null)[][];
}

export interface DonneesQuand {
  annees: AnneeQuand[];
  matrices: MatriceRn[];
  /** Sources des séries, telles que décrites par quand.json. */
  sources: string;
  /** Dates d'extraction (ISO) des séries sources. */
  extractions: Record<string, string>;
  /** Années absentes et pourquoi. */
  exclues: Record<string, string>;
}

/** Années comparées dans les graphiques (de la plus ancienne à la plus récente). */
export const ANNEES_COMPAREES = [2022, 2023, 2024, 2025] as const;

/** MW → « 12,3 GW » : une décimale, toujours (« 8,0 GW »), signe moins typographique. */
export function gw(mw: number, unite = true): string {
  const n = formaterNombre(mw / 1000, 1);
  const fixe = /,\d$/.test(n) ? n : `${n},0`;
  return unite ? `${fixe}${FINE}GW` : fixe;
}

/** Une part entre 0 et 1 → « 52 % ». */
export const pourcent = (p: number): string => `${formaterNombre(Math.round(p * 100), 0)}${FINE}%`;

/* ---------- Échelle de couleur de la charge résiduelle ---------- */

/** Bornes des classes, en MW : 4 classes sous zéro, 4 au-dessus (jetons --rn-n0 … --rn-p3). */
export const SEUILS_RN = [-20000, -10000, -5000, 0, 5000, 10000, 20000] as const;

export const JETONS_RN = [
  '--rn-n0',
  '--rn-n1',
  '--rn-n2',
  '--rn-n3',
  '--rn-p0',
  '--rn-p1',
  '--rn-p2',
  '--rn-p3'
] as const;

/** Classe (0 à 7) d'une valeur en MW ; zéro tombe du côté positif (rien à couvrir = 0, pas un surplus). */
export function classeRn(mw: number): number {
  let k = 0;
  while (k < SEUILS_RN.length && mw >= SEUILS_RN[k]) k++;
  return k;
}

/** Libellé d'une classe : « −20 à −10 GW », « 20 GW et plus »… */
export function libelleClasseRn(k: number): string {
  const g = (mw: number) => formaterNombre(mw / 1000, 0);
  if (k === 0) return `moins de ${g(SEUILS_RN[0])}${FINE}GW`;
  if (k === SEUILS_RN.length) return `${g(SEUILS_RN.at(-1)!)}${FINE}GW et plus`;
  return `${g(SEUILS_RN[k - 1])} à ${g(SEUILS_RN[k])}${FINE}GW`;
}

/* ---------- Statistiques mensuelles d'une matrice ---------- */

export interface StatMois {
  mois: number;
  moyenneMw: number;
  maxMw: number;
  minMw: number;
  /** Heures où la charge résiduelle est positive (le reste du système doit fournir). */
  heuresPositives: number;
  heures: number;
}

/** Par mois de Paris : moyenne, maximum, minimum, heures positives, sur les heures renseignées. */
export function statsMensuelles(m: MatriceRn): StatMois[] {
  const stats: StatMois[] = Array.from({ length: 12 }, (_, mois) => ({
    mois,
    moyenneMw: 0,
    maxMw: -Infinity,
    minMw: Infinity,
    heuresPositives: 0,
    heures: 0
  }));
  m.jours.forEach((jour, d) => {
    const s = stats[Number(jour.slice(5, 7)) - 1];
    for (const v of m.valeurs[d]) {
      if (v === null) continue;
      s.heures++;
      s.moyenneMw += v;
      if (v > s.maxMw) s.maxMw = v;
      if (v < s.minMw) s.minMw = v;
      if (v > 0) s.heuresPositives++;
    }
  });
  for (const s of stats) s.moyenneMw = s.heures ? s.moyenneMw / s.heures : NaN;
  return stats;
}

/* ---------- Mise en page ---------- */

/** Écarte verticalement des étiquettes (au moins `pas` pixels), sans sortir de [haut, bas]. */
export function ecarter<T extends { y: number }>(
  items: T[],
  pas: number,
  haut: number,
  bas: number
): T[] {
  const tri = [...items].sort((a, b) => a.y - b.y).map((t) => ({ ...t }));
  for (let i = 0; i < tri.length; i++)
    tri[i].y = Math.max(tri[i].y, i === 0 ? haut : tri[i - 1].y + pas);
  // Si la dernière dépasse le bas, on remonte la pile.
  for (let i = tri.length - 1; i >= 0; i--)
    tri[i].y = Math.min(tri[i].y, i === tri.length - 1 ? bas : tri[i + 1].y - pas);
  return tri;
}

/** « 2025-01-14T08:00+01:00 » → « 14 janv. 2025, 8 h » (heure de Paris de début). */
export function heureParis(iso: string): string {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):/);
  if (!m) throw new Error(`Horodatage illisible : ${iso}`);
  const MOIS = [
    'janv.',
    'févr.',
    'mars',
    'avr.',
    'mai',
    'juin',
    'juil.',
    'août',
    'sept.',
    'oct.',
    'nov.',
    'déc.'
  ];
  const jour = Number(m[3]) === 1 ? '1er' : String(Number(m[3]));
  return `${jour} ${MOIS[Number(m[2]) - 1]} ${m[1]}, ${Number(m[4])} h`;
}

/* ---------- Sources ---------- */

const NOMS_EXTRACTIONS: Record<string, string> = {
  eco2mix: 'éCO2mix',
  edf_remit: 'REMIT (EDF)',
  prix: 'prix day-ahead'
};

/**
 * Ligne « Sources » des graphiques de charge résiduelle : calcul du site, séries utilisées (les
 * prix n'entrent pas dans la charge résiduelle ni dans le nucléaire non produit) et extractions.
 */
export function sourcesRn(q: DonneesQuand): string {
  const series = q.sources
    .split(/\s*;\s*/)
    .filter((s) => !/prix/i.test(s))
    .join(' ; ');
  const extraits = Object.entries(q.extractions)
    .filter(([k]) => k !== 'prix')
    .map(([k, iso]) => `${NOMS_EXTRACTIONS[k] ?? k} le ${formaterDate(iso.slice(0, 10))}`)
    .join(', ');
  return `Calcul du site (data/export/quand.json, pc build) sur ${series}. Extraction : ${extraits}.`;
}
