// Référentiel des chiffres, lu au prérendu depuis data/export/chiffres.json (versionné, produit par
// le pipeline). Pas de copie dans site/ : le build lit directement l'export.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import type { Chiffres } from '$lib/chiffres';
import { RACINE } from '$lib/server/makingof';

const CONFIANCES = new Set(['A', 'B', 'C']);

let cache: Chiffres | undefined;

/** Vérifie les champs dont le site a besoin ; une entrée incomplète fait échouer le build. */
export function validerChiffres(brut: unknown): Chiffres {
  const chiffres = (brut as { chiffres?: unknown })?.chiffres;
  if (!chiffres || typeof chiffres !== 'object')
    throw new Error('chiffres.json : clé « chiffres » absente');
  for (const [id, c] of Object.entries(chiffres as Record<string, Record<string, unknown>>)) {
    for (const champ of ['libelle', 'unite', 'periode', 'perimetre', 'page', 'citation'])
      if (typeof c[champ] !== 'string') throw new Error(`chiffres.json : « ${id} » sans ${champ}`);
    const v = c.valeur;
    const ok =
      typeof v === 'number' ||
      (Array.isArray(v) && v.length === 2 && v.every((x) => typeof x === 'number'));
    if (!ok) throw new Error(`chiffres.json : « ${id} » a une valeur invalide`);
    if (!CONFIANCES.has(c.confiance as string))
      throw new Error(`chiffres.json : « ${id} » a une confiance invalide`);
    const s = c.source as Record<string, unknown> | undefined;
    for (const champ of ['cle', 'editeur', 'titre', 'date_publication', 'url'])
      if (typeof s?.[champ] !== 'string')
        throw new Error(`chiffres.json : « ${id} », source sans ${champ}`);
  }
  return chiffres as Chiffres;
}

export function chargerChiffres(): Chiffres {
  cache ??= validerChiffres(
    JSON.parse(readFileSync(resolve(RACINE, 'data/export/chiffres.json'), 'utf8'))
  );
  return cache;
}
