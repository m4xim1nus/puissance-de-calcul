// Enquêtes : lit au prérendu docs/enquetes/<slug>.md (front matter + corps Markdown) et rend la
// syntaxe propre au site. Toute référence inconnue (chiffre, source, graphique) lève une erreur :
// le build échoue plutôt que d'afficher un trou.
import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { chiffre, sourcesDe, type Chiffres } from '$lib/chiffres';
import { formaterValeur } from '$lib/format';
import type { BlocEnquete, Enquete, MetaEnquete } from '$lib/enquete';
import { estNomGraphique } from '$lib/graphiques/noms';
import { echapper, markdownBlocs, typographier } from '$lib/markdown';
import { appel, noteChiffre, noteRenvoi, noteSource } from '$lib/notes';
import { RACINE } from '$lib/server/makingof';

const CHAMPS_REQUIS = ['titre', 'question', 'mise_a_jour'] as const;

/** Front matter `---` en tête : paires `cle: valeur` sur une ligne (guillemets facultatifs). */
export function lireFrontMatter(source: string): { meta: Record<string, string>; corps: string } {
  const lignes = source.replace(/\r\n?/g, '\n').split('\n');
  if (lignes[0].trim() !== '---') return { meta: {}, corps: source };
  const fin = lignes.indexOf('---', 1);
  if (fin < 0) throw new Error('Front matter non fermé (ligne « --- » manquante)');
  const meta: Record<string, string> = {};
  for (const [k, ligne] of lignes.slice(1, fin).entries()) {
    if (ligne.trim() === '' || ligne.trim().startsWith('#')) continue;
    const m = ligne.match(/^([A-Za-z_][\w-]*):\s*(.*)$/);
    if (!m) throw new Error(`Front matter, ligne ${k + 2} illisible : « ${ligne} »`);
    if (m[1] in meta) throw new Error(`Front matter : clé « ${m[1]} » en double`);
    meta[m[1]] = m[2].trim().replace(/^(["'])(.*)\1$/, '$2');
  }
  return { meta, corps: lignes.slice(fin + 1).join('\n') };
}

function resume(numeros: number[]): string {
  if (numeros.length === 1) return `Note ${numeros[0]}`;
  return `Notes ${numeros.slice(0, -1).join(', ')} et ${numeros.at(-1)}`;
}

/** Rend le corps d'une enquête en blocs HTML (avec notes marginales) et emplacements de graphiques. */
export function rendreCorps(corps: string, chiffres: Chiffres): BlocEnquete[] {
  const sources = sourcesDe(chiffres);
  const notes = new Map<number, string>();
  const premiereNote = new Map<string, number>();
  let numero = 0;

  const jeton = (expression: string): string => {
    const n = ++numero;
    if (expression.startsWith('source:')) {
      const [cle, ...reste] = expression.slice('source:'.length).split('|');
      const s = sources.get(cle.trim());
      if (!s) throw new Error(`Source inconnue dans le référentiel : « ${cle.trim()} »`);
      notes.set(n, typographier(noteSource(n, s, reste.join('|').trim() || undefined)));
      return appel(n);
    }
    if (!/^[\w-]+$/.test(expression)) throw new Error(`Jeton illisible : « {{${expression}}} »`);
    const c = chiffre(chiffres, expression);
    const deja = premiereNote.get(expression);
    if (deja === undefined) {
      premiereNote.set(expression, n);
      notes.set(n, typographier(noteChiffre(n, c, sources)));
    } else {
      notes.set(n, typographier(noteRenvoi(n, c, deja)));
    }
    return `<span class="chiffre">${echapper(formaterValeur(c.valeur, c.unite))}</span>${appel(n)}`;
  };

  const envelopper = (html: string, contexte: 'p' | 'li'): string => {
    const numeros = [...html.matchAll(/data-note="(\d+)"/g)].map((m) => Number(m[1]));
    const texte = contexte === 'p' ? `<p>${html}</p>` : `<div class="contenu">${html}</div>`;
    if (!numeros.length) return contexte === 'p' ? texte : html;
    const corpsNotes = numeros.map((k) => notes.get(k)!).join('');
    // Les notes précèdent le texte dans le DOM : sur grand écran elles flottent dans la marge à
    // hauteur du paragraphe ; sur téléphone, la mise en page les replace dessous, repliées.
    const aside =
      `<details class="notes"><summary>${resume(numeros)}</summary>` +
      `<div class="notes-corps">${corpsNotes}</div></details>`;
    return `<div class="avec-notes">${aside}${texte}</div>`;
  };

  return markdownBlocs(corps, { niveauTitre: 1, jeton, envelopper, typographie: true }).map((b) => {
    if (b.type === 'html') return b;
    if (b.nom !== 'graphique') throw new Error(`Directive inconnue : « ${b.brut} »`);
    if (!estNomGraphique(b.argument)) throw new Error(`Graphique inconnu : « ${b.argument} »`);
    return { type: 'graphique', nom: b.argument };
  });
}

/** Valide le front matter d'une enquête. */
export function metaEnquete(meta: Record<string, string>, slug: string): MetaEnquete {
  for (const champ of CHAMPS_REQUIS)
    if (!meta[champ])
      throw new Error(`Enquête « ${slug} » : champ « ${champ} » absent du front matter`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(meta.mise_a_jour))
    throw new Error(`Enquête « ${slug} » : mise_a_jour n'est pas une date AAAA-MM-JJ`);
  return { titre: meta.titre, question: meta.question, mise_a_jour: meta.mise_a_jour };
}

const DOSSIER = resolve(RACINE, 'docs/enquetes');

export function slugsEnquetes(): string[] {
  return readdirSync(DOSSIER)
    .filter((f) => f.endsWith('.md'))
    .map((f) => f.slice(0, -3))
    .sort();
}

export function chargerEnquete(slug: string, chiffres: Chiffres): Enquete {
  if (!/^[a-z0-9-]+$/.test(slug)) throw new Error(`Slug d'enquête invalide : « ${slug} »`);
  const { meta, corps } = lireFrontMatter(readFileSync(resolve(DOSSIER, `${slug}.md`), 'utf8'));
  return { slug, meta: metaEnquete(meta, slug), blocs: rendreCorps(corps, chiffres) };
}
