import { chargerCarbone } from '$lib/server/carbone';
import { chargerChiffres } from '$lib/server/chiffres';
import { chargerEnquete } from '$lib/server/enquetes';

export const prerender = true;

export function load() {
  const chiffres = chargerChiffres();
  return {
    // Le texte est rendu ici, notes comprises ; le graphique lit carbone.json, pas le référentiel :
    // on ne l'embarque pas dans la page (comme « Quand ? »).
    enquete: chargerEnquete('carbone', chiffres),
    chiffres: {},
    donnees: { carbone: chargerCarbone() }
  };
}
