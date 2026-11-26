// Glossaire : lit au prérendu docs/GLOSSAIRE.md (format décrit en tête du fichier), le valide et le
// rend pour /methode. Fournit aussi le résolveur des renvois [texte](glossaire:id) des pages : un
// identifiant absent du glossaire lève une erreur, et le build échoue plutôt que d'afficher un
// lien mort.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { enLigne } from '$lib/markdown';
import { RACINE } from '$lib/server/makingof';

export const FICHIER_GLOSSAIRE = 'docs/GLOSSAIRE.md';

export interface EntreeGlossaire {
  id: string;
  /** Terme, texte brut (Markdown en ligne autorisé, rendu par `rendreGlossaire`). */
  terme: string;
  /** Définition, un paragraphe Markdown en ligne (lignes jointes). */
  definition: string;
  /** Ligne « Source : … » sans son préfixe, ou null. */
  source: string | null;
}

export interface EntreeGlossaireRendue {
  id: string;
  terme: string;
  definition: string;
  source: string | null;
}

const RE_TITRE = /^## +(.+?) +\{#([a-z0-9]+(?:-[a-z0-9]+)*)\}\s*$/;
export const RE_RENVOI = /\]\(glossaire:([^)\s]*)\)/g;

/** Nombre de phrases : une fin de phrase est un point (ou ! ?) suivi d'une majuscule ou de la fin. */
export function phrases(texte: string): number {
  const t = texte.replace(/\[([^\]]*)\]\([^)\s]*\)/g, '$1').trim();
  return t.split(/[.!?](?=\s+[«(A-ZÀ-ÖØ-Þ]|\s*$)/u).filter((p) => p.trim() !== '').length;
}

/** Lit et valide le glossaire ; toute entorse au format lève une erreur qui dit où. */
export function lireGlossaire(source: string): EntreeGlossaire[] {
  // Front matter lu ici sans passer par enquetes.ts (qui importe ce module).
  const fm = source.replace(/\r\n?/g, '\n').match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!fm || !/^titre: .+$/m.test(fm[1]) || !/^mise_a_jour: \d{4}-\d{2}-\d{2}$/m.test(fm[1]))
    throw new Error(`${FICHIER_GLOSSAIRE} : front matter « titre » et « mise_a_jour » attendus`);
  const corps = fm[2];
  const texte = corps.replace(/<!--[\s\S]*?-->/g, '');
  const [avant, ...blocs] = texte.split(/^(?=## )/m);
  if (avant.trim() !== '')
    throw new Error(`${FICHIER_GLOSSAIRE} : texte hors entrée avant le premier terme`);
  const entrees: EntreeGlossaire[] = [];
  const vus = new Set<string>();
  for (const bloc of blocs) {
    const [titre, ...reste] = bloc.trimEnd().split('\n');
    const m = titre.match(RE_TITRE);
    if (!m) throw new Error(`${FICHIER_GLOSSAIRE} : titre illisible « ${titre} »`);
    const [, terme, id] = m;
    const ou = `${FICHIER_GLOSSAIRE}, « ${id} »`;
    if (vus.has(id)) throw new Error(`${ou} : identifiant en double`);
    vus.add(id);
    const paragraphes = reste
      .join('\n')
      .trim()
      .split(/\n\s*\n/)
      .map((p) => p.replace(/\s*\n\s*/g, ' ').trim());
    let source: string | null = null;
    if (paragraphes.length === 2 && paragraphes[1].startsWith('Source : ')) {
      source = paragraphes.pop()!.slice('Source : '.length);
      if (!/\]\(https:\/\/[^)\s]+\)/.test(source))
        throw new Error(`${ou} : la source doit contenir un lien https`);
    }
    if (paragraphes.length !== 1 || !paragraphes[0])
      throw new Error(`${ou} : une définition d'un seul paragraphe, puis « Source : » facultative`);
    const definition = paragraphes[0];
    if (/\{\{|:::/.test(definition))
      throw new Error(`${ou} : ni chiffre du référentiel ni directive dans une définition`);
    const n = phrases(definition);
    if (n < 2 || n > 5) throw new Error(`${ou} : ${n} phrase(s), 2 à 5 attendues`);
    entrees.push({ id, terme, definition, source });
  }
  for (let k = 1; k < entrees.length; k++)
    if (entrees[k - 1].terme.localeCompare(entrees[k].terme, 'fr') > 0)
      throw new Error(
        `${FICHIER_GLOSSAIRE} : « ${entrees[k].terme} » doit précéder « ${entrees[k - 1].terme} » (ordre alphabétique)`
      );
  // Renvois internes au glossaire : vers une entrée existante.
  for (const e of entrees)
    for (const [, cible] of e.definition.matchAll(RE_RENVOI))
      if (!vus.has(cible))
        throw new Error(`${FICHIER_GLOSSAIRE}, « ${e.id} » : renvoi vers « ${cible} », absent`);
  return entrees;
}

let cache: EntreeGlossaire[] | null = null;

/** Le glossaire du dépôt (lu une fois par processus). */
export function chargerGlossaire(): EntreeGlossaire[] {
  cache ??= lireGlossaire(readFileSync(resolve(RACINE, FICHIER_GLOSSAIRE), 'utf8'));
  return cache;
}

/** Ancre d'un terme sur /methode. */
export const ancreGlossaire = (id: string) => `g-${id}`;

/**
 * Résolveur des renvois [texte](glossaire:id) pour le rendu Markdown : l'URL de l'entrée, ou une
 * erreur si l'identifiant n'est pas dans le glossaire. `prefixe` vaut '' sur /methode elle-même.
 */
export function resolveurGlossaire(
  entrees: EntreeGlossaire[] = chargerGlossaire(),
  prefixe = '/methode'
): (id: string) => string {
  const ids = new Set(entrees.map((e) => e.id));
  return (id) => {
    if (!ids.has(id))
      throw new Error(`Renvoi au glossaire inconnu : « glossaire:${id} » (${FICHIER_GLOSSAIRE})`);
    return `${prefixe}#${ancreGlossaire(id)}`;
  };
}

/** Le glossaire rendu pour /methode : HTML en ligne, typographié ; renvois internes à la page. */
export function rendreGlossaire(
  entrees: EntreeGlossaire[] = chargerGlossaire()
): EntreeGlossaireRendue[] {
  const options = { typographie: true, glossaire: resolveurGlossaire(entrees, '') } as const;
  return entrees.map((e) => ({
    id: e.id,
    terme: enLigne(e.terme, options),
    definition: enLigne(e.definition, options),
    source: e.source === null ? null : enLigne(e.source, options)
  }));
}
