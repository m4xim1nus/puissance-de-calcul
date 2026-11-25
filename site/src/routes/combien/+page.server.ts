import { chargerChiffres } from '$lib/server/chiffres';
import { chargerEnquete } from '$lib/server/enquetes';

export const prerender = true;

export function load() {
  const chiffres = chargerChiffres();
  return { enquete: chargerEnquete('combien', chiffres), chiffres };
}
