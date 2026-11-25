import { sourcesDe } from '$lib/chiffres';
import { chargerChiffres } from '$lib/server/chiffres';

export const prerender = true;

export function load() {
  const chiffres = chargerChiffres();
  const usages = new Map<string, number>();
  for (const c of Object.values(chiffres))
    usages.set(c.source.cle, (usages.get(c.source.cle) ?? 0) + 1);
  const sources = [...sourcesDe(chiffres).values()]
    .map((s) => ({ ...s, chiffres: usages.get(s.cle) ?? 0 }))
    .sort(
      (a, b) =>
        a.editeur.localeCompare(b.editeur, 'fr') ||
        b.date_publication.localeCompare(a.date_publication)
    );
  return { sources, nombreChiffres: Object.keys(chiffres).length };
}
