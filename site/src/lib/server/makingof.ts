// Making-of : lit au prérendu les trois fichiers de making-of/ et le brief figé (docs/BRIEF.md),
// versionnés à la racine du dépôt, et les rend en HTML. Rien n'est lu à l'exécution côté client.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { markdown } from '$lib/markdown';

// Les scripts npm tournent dans site/ : la racine du dépôt est son parent.
export const RACINE = resolve(process.cwd(), '..');

export interface SectionMakingOf {
  id: string;
  titre: string;
  fichier: string;
  html: string;
}

const SECTIONS = [
  { id: 'journal', titre: 'Journal', fichier: 'making-of/JOURNAL.md' },
  { id: 'decisions', titre: 'Décisions', fichier: 'making-of/DECISIONS.md' },
  { id: 'erreurs', titre: 'Erreurs de Claude', fichier: 'making-of/ERREURS.md' },
  { id: 'brief', titre: 'Brief', fichier: 'docs/BRIEF.md' }
] as const;

export function sectionsMakingOf(): SectionMakingOf[] {
  return SECTIONS.map((s) => ({
    ...s,
    // Les titres des fichiers deviennent des h3 : le h2 est celui de la section.
    html: markdown(readFileSync(resolve(RACINE, s.fichier), 'utf8'), { niveauTitre: 3 })
  }));
}
