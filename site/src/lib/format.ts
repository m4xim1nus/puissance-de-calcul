// Formatage à la française : virgule décimale, espace fine insécable (U+202F) pour grouper les
// milliers et avant un symbole d'unité, espace insécable (U+00A0) avant une unité en toutes lettres.

/** Espace fine insécable (U+202F). */
export const FINE = ' ';
/** Espace insécable (U+00A0). */
export const INSECABLE = ' ';

const NOMBRE = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2, useGrouping: true });

/** 4.34 → « 4,34 » ; 1400 → « 1 400 » (espace fine insécable). */
export function formaterNombre(n: number): string {
  if (!Number.isFinite(n)) throw new Error(`Nombre invalide : ${n}`);
  // Intl peut grouper avec une espace insécable ordinaire selon la version d'ICU : on normalise.
  return NOMBRE.format(n).replace(/[   ]/g, FINE).replace('-', '−');
}

/** Une unité en toutes lettres (« sites ») prend une espace insécable ; un symbole, une fine. */
export function separateurUnite(unite: string): string {
  return /^[a-zà-ÿ]{3,}/.test(unite) ? INSECABLE : FINE;
}

export type Valeur = number | [number, number];

/** 442.2, 'TWh' → « 442,2 TWh » ; [4, 5], 'TWh' → « 4 à 5 TWh » (insécable de bout en bout). */
export function formaterValeur(valeur: Valeur, unite: string): string {
  const nombre = Array.isArray(valeur)
    ? `${formaterNombre(valeur[0])}${INSECABLE}à${INSECABLE}${formaterNombre(valeur[1])}`
    : formaterNombre(valeur);
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
