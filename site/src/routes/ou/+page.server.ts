import { chargerChiffres } from '$lib/server/chiffres';
import { chargerEnquete } from '$lib/server/enquetes';

export const prerender = true;

export function load() {
  const chiffres = chargerChiffres();
  return {
    // Le texte est rendu ici, notes comprises. « Où ? » n'a pas de graphique : on n'embarque pas
    // le référentiel dans la page (un graphique qui en aurait besoin ferait échouer le prérendu
    // sur « Chiffre inconnu »).
    enquete: chargerEnquete('ou', chiffres),
    chiffres: {}
  };
}
