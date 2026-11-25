// Types d'une enquête rendue (partagés entre le prérendu et les composants).
import type { NomGraphique } from '$lib/graphiques/noms';

export interface MetaEnquete {
  titre: string;
  question: string;
  mise_a_jour: string;
}

export type BlocEnquete = { type: 'html'; html: string } | { type: 'graphique'; nom: NomGraphique };

export interface Enquete {
  slug: string;
  meta: MetaEnquete;
  blocs: BlocEnquete[];
}
