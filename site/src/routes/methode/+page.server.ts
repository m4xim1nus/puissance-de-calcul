import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { sourcesDe } from '$lib/chiffres';
import { dateParis } from '$lib/format';
import { markdown } from '$lib/markdown';
import { chargerChiffres } from '$lib/server/chiffres';
import { RACINE } from '$lib/server/makingof';

interface Meta {
  attributions: { donnees: string; licence: string; attribution: string; url_licence: string }[];
  sources: Record<string, { extrait_le: string }>;
}

/** Séries horaires : attributions, licences, dates d'extraction (heure de Paris), format. */
function donnees() {
  const meta: Meta = JSON.parse(readFileSync(resolve(RACINE, 'data/export/meta.json'), 'utf8'));
  const extraction = (prefixe: string) => {
    const dates = Object.entries(meta.sources)
      .filter(([k]) => k.startsWith(prefixe))
      .map(([, v]) => dateParis(v.extrait_le))
      .sort();
    return dates.length ? { premiere: dates[0], derniere: dates.at(-1)! } : null;
  };
  const lisezmoi = readFileSync(resolve(RACINE, 'data/export/horaire/LISEZMOI.md'), 'utf8');
  return {
    attributions: meta.attributions,
    extractionPrix: extraction('prix_fr/'),
    extractionEco2mix: extraction('eco2mix'),
    extractionOdre: extraction('odre_'),
    // Copie du LISEZMOI des séries horaires ; son titre devient un h3 sous le h2 « Données ».
    lisezmoi: markdown(lisezmoi, { niveauTitre: 3 })
  };
}

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
  return { sources, nombreChiffres: Object.keys(chiffres).length, donnees: donnees() };
}
