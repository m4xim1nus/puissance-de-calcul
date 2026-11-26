// « À toi » : missions à faire soi-même avec Claude Code (exigence du brief). Le texte vient de
// docs/A-TOI.md, source unique, rendu au prérendu avec le Markdown maison.
import { markdown } from '$lib/markdown';
import { lireFichier } from '$lib/server/makingof';

export const FICHIER_A_TOI = 'docs/A-TOI.md';

/** Titre et date du front matter, texte en HTML (titres `##` rendus en h2). */
export function aToi(source = lireFichier(FICHIER_A_TOI)) {
  const m = source.match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) throw new Error(`${FICHIER_A_TOI} : front matter absent`);
  const champ = (cle: string) => m[1].match(new RegExp(`^${cle}:\\s*(.+)$`, 'm'))?.[1].trim();
  const titre = champ('titre');
  const miseAJour = champ('mise_a_jour');
  if (!titre || !miseAJour) throw new Error(`${FICHIER_A_TOI} : titre ou mise_a_jour absent`);
  const html = markdown(source.slice(m[0].length), { typographie: true });
  return { titre, miseAJour, html };
}
