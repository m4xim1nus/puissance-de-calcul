import { chargerChiffres } from '$lib/server/chiffres';
import { chargerQuand } from '$lib/server/quand';
import { anneesSimulateur, referencesSimulateur, textesSimulateur } from '$lib/server/simulateur';

export const prerender = true;

export function load() {
  const q = chargerQuand();
  const chiffres = chargerChiffres();
  return {
    annees: anneesSimulateur(),
    textes: textesSimulateur(chiffres),
    references: referencesSimulateur(chiffres),
    sources: q.sources,
    extractions: q.extractions
  };
}
