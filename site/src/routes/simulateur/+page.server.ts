import { chargerChiffres } from '$lib/server/chiffres';
import { chargerQuand } from '$lib/server/quand';
import { anneesSimulateur, referencesSimulateur, textesSimulateur } from '$lib/server/simulateur';
import { sectionsParTitre } from '$lib/simulateur/sections';

export const prerender = true;

export function load() {
  const q = chargerQuand();
  const chiffres = chargerChiffres();
  const textes = textesSimulateur(chiffres);
  return {
    annees: anneesSimulateur(),
    enTete: textes.enTete,
    // Le texte de lecture est rangé en replis, un par section (titre de niveau 2).
    lecture: sectionsParTitre(textes.lecture),
    references: referencesSimulateur(chiffres),
    sources: q.sources,
    extractions: q.extractions
  };
}
