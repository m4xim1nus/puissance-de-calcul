// Mise en forme des résultats du simulateur : unités explicites, espaces fines, pas de « 0 % »
// trompeur pour une part petite mais non nulle.
import { FINE, INSECABLE, formaterNombre } from '$lib/format';

/** Énergie en TWh : deux décimales sous 10 TWh, une au-delà (8,76 TWh ; 175,2 TWh). */
export function twh(v: number): string {
  return `${formaterNombre(v, Math.abs(v) < 10 ? 2 : 1)}${FINE}TWh`;
}

/** Part entre 0 et 1 en pour cent entier ; « moins de 1 % » et « plus de 99 % » aux bords. */
export function part(p: number): string {
  if (p > 0 && p < 0.005) return `moins de 1${FINE}%`;
  if (p < 1 && p > 0.995) return `plus de 99${FINE}%`;
  return `${formaterNombre(Math.round(p * 100), 0)}${FINE}%`;
}

/** Prix en €/MWh, une décimale. */
export const prix = (v: number): string => `${formaterNombre(v, 1)}${FINE}€/MWh`;

/** Nombre d'heures : « 0 heure », « 1 heure », « 1 234 heures ». */
export const heures = (n: number): string =>
  `${formaterNombre(n)}${INSECABLE}heure${n >= 2 ? 's' : ''}`;

/** Puissance réglée : « 1 GW », « 2,5 GW » (sans décimale inutile). */
export const puissanceReglee = (xGw: number): string => `${formaterNombre(xGw, 1)}${FINE}GW`;
