// Recherche d'un rang dans une monotone échantillonnée (rangs croissants), partagée par le tracé
// (MonotoneAvantApres.svelte) et par son tableau de données (TableauMonotone.svelte, dans la notice).
import type { Monotone } from './moteur';

/** Indice de l'échantillon de rang le plus proche (rangs croissants). */
export function proche(m: Monotone, rang: number): number {
  let bas = 0;
  let haut = m.length - 1;
  while (haut - bas > 1) {
    const k = (bas + haut) >> 1;
    if (m[k][0] <= rang) bas = k;
    else haut = k;
  }
  return rang - m[bas][0] <= m[haut][0] - rang ? bas : haut;
}
