import { ANNEES_COMPAREES } from '$lib/quand';
import { chargerChiffres } from '$lib/server/chiffres';
import { chargerEnquete } from '$lib/server/enquetes';
import { chargerQuand } from '$lib/server/quand';

export const prerender = true;

export function load() {
  const chiffres = chargerChiffres();
  const quand = chargerQuand();
  return {
    // Le texte est rendu ici, notes comprises : les graphiques de « Quand ? » ne lisent pas le
    // référentiel, on ne l'embarque pas dans la page (un graphique qui en aurait besoin ferait
    // échouer le prérendu sur « Chiffre inconnu »).
    enquete: chargerEnquete('quand', chiffres),
    chiffres: {},
    donnees: {
      quand: {
        ...quand,
        // Monotones tracées : années comparées seulement (le tableau garde les quantiles de toutes).
        annees: quand.annees.map((a) =>
          (ANNEES_COMPAREES as readonly number[]).includes(a.annee) ? a : { ...a, monotone: [] }
        )
      }
    }
  };
}
