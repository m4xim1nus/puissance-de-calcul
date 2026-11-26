// Types d'une enquête rendue (partagés entre le prérendu et les composants).
import type { NomGraphique } from '$lib/graphiques/noms';

export interface MetaEnquete {
  titre: string;
  question: string;
  mise_a_jour: string;
}

/** Encart « en préparation » (EnChantier.svelte) : texte simple, typographié. */
export interface Chantier {
  titre: string;
  manque: string;
  pourquoi: string;
  viendra: string;
}

export type BlocEnquete =
  | { type: 'html'; html: string }
  | { type: 'graphique'; nom: NomGraphique }
  | ({ type: 'chantier' } & Chantier);

export interface Enquete {
  slug: string;
  meta: MetaEnquete;
  blocs: BlocEnquete[];
}
