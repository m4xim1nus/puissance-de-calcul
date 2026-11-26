// Formatage à la française : virgule décimale, espace fine insécable (U+202F) pour grouper les
// milliers et avant un symbole d'unité, espace insécable (U+00A0) avant une unité en toutes lettres.

/** Espace fine insécable (U+202F). */
export const FINE = ' ';
/** Espace insécable (U+00A0). */
export const INSECABLE = ' ';

const formats = new Map<number, Intl.NumberFormat>();

/** 4.34 → « 4,34 » ; 1400 → « 1 400 » (espace fine insécable). `decimales` : au plus (défaut 2). */
export function formaterNombre(n: number, decimales = 2): string {
  if (!Number.isFinite(n)) throw new Error(`Nombre invalide : ${n}`);
  let f = formats.get(decimales);
  if (!f) {
    f = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: decimales, useGrouping: true });
    formats.set(decimales, f);
  }
  // Intl peut grouper avec une espace insécable ordinaire selon la version d'ICU : on normalise.
  return f.format(n).replace(/[   ]/g, FINE).replace('-', '−');
}

/** Nombre de décimales qu'implique un pas d'arrondi : 0,1 → 1 ; 1 → 0 ; 0,25 → 2. */
export function decimalesDe(precision: number): number {
  if (!(precision > 0)) throw new Error(`Précision invalide : ${precision}`);
  return Math.max(0, Math.ceil(-Math.log10(precision) - 1e-9));
}

/** Comme formaterNombre, mais avec exactement `decimales` décimales (8 → « 8,0 » pour 1). */
export function formaterFixe(n: number, decimales: number): string {
  const t = formaterNombre(n, decimales);
  if (decimales === 0) return t;
  const [ent, dec = ''] = t.split(',');
  return `${ent},${dec.padEnd(decimales, '0')}`;
}

/** Une unité en toutes lettres (« sites ») prend une espace insécable ; un symbole, une fine. */
export function separateurUnite(unite: string): string {
  return /^[a-zà-ÿ]{3,}/.test(unite) ? INSECABLE : FINE;
}

export type Valeur = number | [number, number];

/** Arrondi d'affichage à 3 chiffres significatifs au plus (36,73 → 36,7 ; 442,2 → 442). */
export function arrondir(n: number, chiffres = 3): number {
  return n === 0 ? 0 : Number(n.toPrecision(chiffres));
}

/**
 * 442.2, 'TWh' → « 442,2 TWh » ; [4, 5], 'TWh' → « 4 à 5 TWh » (insécable de bout en bout).
 * Avec `arrondi`, au plus 3 chiffres significatifs (affichage dans le texte et les graphiques ;
 * la valeur exacte reste dans la note et le tableau de données).
 */
export function formaterValeur(
  valeur: Valeur,
  unite: string,
  arrondi = false,
  precision?: number
): string {
  // Un chiffre calculé porte sa précision d'affichage : elle prime sur l'arrondi générique.
  const f = (n: number) =>
    precision !== undefined
      ? formaterFixe(n, decimalesDe(precision))
      : formaterNombre(arrondi ? arrondir(n) : n);
  const nombre = Array.isArray(valeur)
    ? `${f(valeur[0])}${INSECABLE}à${INSECABLE}${f(valeur[1])}`
    : f(valeur);
  return unite ? `${nombre}${separateurUnite(unite)}${unite}` : nombre;
}

const MOIS = [
  'janvier',
  'février',
  'mars',
  'avril',
  'mai',
  'juin',
  'juillet',
  'août',
  'septembre',
  'octobre',
  'novembre',
  'décembre'
];
const MOIS_COURTS = [
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

/** « 2026-01-30 » → « 30 janvier 2026 » (ou « 30 janv. 2026 ») ; « 2026-05 » → « mai 2026 ». */
export function formaterDate(iso: string, court = false): string {
  const m = iso.match(/^(\d{4})-(\d{2})(?:-(\d{2}))?$/);
  if (!m) throw new Error(`Date ISO invalide : ${iso}`);
  const mois = (court ? MOIS_COURTS : MOIS)[Number(m[2]) - 1];
  if (!mois) throw new Error(`Mois invalide : ${iso}`);
  if (!m[3]) return `${mois}${INSECABLE}${m[1]}`;
  const jour = Number(m[3]) === 1 ? '1er' : String(Number(m[3]));
  return `${jour}${INSECABLE}${mois}${INSECABLE}${m[1]}`;
}

/** Une période du référentiel (« 2025-11-01 », « fin 2024 », « 2022 → 2025-11-15 ») en clair. */
export function formaterPeriode(periode: string, court = false): string {
  return periode.replace(/\b\d{4}-\d{2}(?:-\d{2})?\b/g, (d) => formaterDate(d, court));
}

/** Date civile en heure de Paris (AAAA-MM-JJ) d'un instant ISO 8601 : une extraction faite à
 * 23 h 12 UTC le 25 novembre a eu lieu le 26 novembre à Paris. */
export function dateParis(iso: string): string {
  const instant = new Date(iso);
  if (Number.isNaN(instant.getTime())) throw new Error(`Instant ISO invalide : ${iso}`);
  return new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Europe/Paris',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(instant);
}
