// Grille « jours × heures de Paris » d'une année de prix horaires, et échelle de couleurs.
// Partagé entre le prérendu et le navigateur ; aucune dépendance au fuseau de la machine.

/** Données compactes d'une année : une valeur par heure UTC depuis `debut` (null = absente). */
export interface AnneePrix {
  annee: number;
  /** Début de la première heure, ISO UTC (minuit, heure de Paris, le 1er janvier). */
  debut: string;
  /** €/MWh, arrondis à l'euro (au centime entre −1 et 1, pour garder le signe). */
  prix: (number | null)[];
  /** Année en cours : données provisoires, incomplètes. */
  provisoire: boolean;
  /** Date d'extraction des prix (ISO). */
  extrait_le: string;
}

const H = 3_600_000;

/** Dernier dimanche d'un mois (0 = janvier), à 01:00 UTC : bascule de l'heure légale en Europe. */
function dernierDimanche01Utc(annee: number, mois: number): number {
  const fin = new Date(Date.UTC(annee, mois + 1, 0, 1)); // dernier jour du mois, 01:00 UTC
  return fin.getTime() - fin.getUTCDay() * 24 * H;
}

/** Décalage de l'heure de Paris sur UTC (heures) : 2 en heure d'été, 1 sinon (règle de l'UE). */
export function decalageParis(utcMs: number): 1 | 2 {
  const a = new Date(utcMs).getUTCFullYear();
  return utcMs >= dernierDimanche01Utc(a, 2) && utcMs < dernierDimanche01Utc(a, 9) ? 2 : 1;
}

export type Case =
  | { type: 'prix'; v: number | null }
  /** Jour de 25 heures : l'heure 2 h existe deux fois (été, puis hiver). */
  | { type: 'double'; v: [number | null, number | null] }
  /** Jour de 23 heures : l'heure 2 h n'existe pas. */
  | { type: 'inexistante' }
  /** Pas encore publiée (année en cours). */
  | { type: 'hors-donnees' };

export interface Jour {
  /** AAAA-MM-JJ, heure de Paris. */
  date: string;
  cases: Case[];
}

const iso = (ms: number) => new Date(ms).toISOString().slice(0, 10);

/** Les jours de l'année (heure de Paris), 24 cases chacun, à partir des valeurs horaires UTC. */
export function grille(a: Pick<AnneePrix, 'annee' | 'debut' | 'prix'>): Jour[] {
  const jours = new Map<string, Case[]>();
  // Tous les jours civils de l'année, d'abord « hors données ».
  for (let t = Date.UTC(a.annee, 0, 1); t < Date.UTC(a.annee + 1, 0, 1); t += 24 * H)
    jours.set(
      iso(t),
      Array.from({ length: 24 }, (): Case => ({ type: 'hors-donnees' }))
    );
  // Jour de passage à l'heure d'été : 2 h n'existe pas.
  const ete = dernierDimanche01Utc(a.annee, 2);
  jours.get(iso(ete))![2] = { type: 'inexistante' };

  const t0 = Date.parse(a.debut);
  a.prix.forEach((v, i) => {
    const t = t0 + i * H;
    const local = t + decalageParis(t) * H;
    const cases = jours.get(iso(local));
    if (!cases) return;
    const h = new Date(local).getUTCHours();
    const c = cases[h];
    if (c.type === 'prix') cases[h] = { type: 'double', v: [c.v, v] };
    else cases[h] = { type: 'prix', v };
  });
  return [...jours].map(([date, cases]) => ({ date, cases }));
}

/** Seuils de l'échelle (€/MWh) : bornes basses des classes, de la plus négative à la plus haute. */
export const SEUILS = [-20, -5, 0, 25, 50, 100, 200] as const;
/** Prix au-delà duquel la couleur est écrêtée (la valeur exacte reste dans l'infobulle). */
export const ECRETAGE = 200;

/**
 * Classe d'un prix : 0 à 2 pour les prix strictement négatifs (du plus au moins négatif),
 * 3 à 7 pour les prix positifs ou nuls (de 0 à ≥ 200 €/MWh).
 */
export function classe(v: number): number {
  if (v < -20) return 0;
  if (v < -5) return 1;
  if (estNegatif(v)) return 2;
  if (v < 25) return 3;
  if (v < 50) return 4;
  if (v < 100) return 5;
  if (v < 200) return 6;
  return 7;
}

/** Libellés des classes, pour la légende et le tableau. */
export const LIBELLES_CLASSES = [
  'moins de −20',
  '−20 à −5',
  '−5 à 0 (exclu)',
  '0 à 25',
  '25 à 50',
  '50 à 100',
  '100 à 200',
  '200 et plus'
];

/** Nombre d'heures à prix strictement négatif, au total et par mois (heure de Paris). */
export function heuresNegatives(a: Pick<AnneePrix, 'annee' | 'debut' | 'prix'>): {
  total: number;
  parMois: number[];
} {
  const parMois = Array(12).fill(0) as number[];
  const t0 = Date.parse(a.debut);
  a.prix.forEach((v, i) => {
    if (v === null || !estNegatif(v)) return;
    const t = t0 + i * H;
    const local = new Date(t + decalageParis(t) * H);
    if (local.getUTCFullYear() === a.annee) parMois[local.getUTCMonth()]++;
  });
  return { total: parMois.reduce((s, n) => s + n, 0), parMois };
}

/**
 * Valeur stockée pour un prix strictement négatif mais arrondi à « -0.0 » dans le CSV (moyenne de
 * quarts d'heure entre −0,005 et 0 €/MWh) : le signe est connu, pas la valeur. JSON ne sait pas
 * écrire −0 ; ce marqueur, hors de la précision publiée, le remplace.
 */
export const NEGATIF_ARRONDI = -0.001;

/** Prix strictement négatif, y compris un −0 (négatif arrondi à zéro dans la source). */
export const estNegatif = (v: number) => v < 0 || Object.is(v, -0);

/** Arrondi de stockage : à l'euro, sauf entre −1 et 1 € (au centime) pour garder le signe. */
export function arrondiStockage(v: number): number {
  if (Object.is(v, -0)) return NEGATIF_ARRONDI;
  const r = Math.abs(v) < 1 ? Math.round(v * 100) / 100 : Math.round(v);
  return r === 0 && v < 0 ? NEGATIF_ARRONDI : r;
}
