import { chargerChiffres } from '$lib/server/chiffres';
import { chargerQuand } from '$lib/server/quand';
import { anneesSimulateur, textesSimulateur } from '$lib/server/simulateur';

export const prerender = true;

export function load() {
  const q = chargerQuand();
  return {
    annees: anneesSimulateur(),
    textes: textesSimulateur(chargerChiffres()),
    sources: q.sources,
    extractions: q.extractions
  };
}
