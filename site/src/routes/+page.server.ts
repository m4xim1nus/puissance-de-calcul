import { sourcesDe } from '$lib/chiffres';
import { typographier } from '$lib/markdown';
import { noteChiffre } from '$lib/notes';
import { chargerChiffres } from '$lib/server/chiffres';
import { anneePrix, anneesPrix } from '$lib/server/prix';

export const prerender = true;

/** Année affichée par défaut : la dernière année complète. */
const ANNEE_DEFAUT = 2025;

export function load() {
  const chiffres = chargerChiffres();
  const sources = sourcesDe(chiffres);
  // Heures négatives publiées par RTE (référentiel), avec leur note ; les autres années sont un
  // calcul du site sur les données affichées.
  const references: Record<number, { valeur: number; note: string }> = {};
  for (const a of anneesPrix()) {
    const c = chiffres[`heures_negatives_${a}`];
    if (c && typeof c.valeur === 'number')
      references[a] = { valeur: c.valeur, note: typographier(noteChiffre(null, c, sources)) };
  }
  return { annees: anneesPrix(), initiale: anneePrix(ANNEE_DEFAUT), references };
}
