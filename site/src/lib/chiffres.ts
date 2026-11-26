// Types du référentiel des chiffres (data/export/chiffres.json) et accès strict par identifiant.
import type { Valeur } from '$lib/format';

export interface Source {
  cle: string;
  editeur: string;
  titre: string;
  date_publication: string;
  url: string;
  consulte_le?: string;
  note?: string;
}

export interface Recoupement {
  source: string;
  valeur: string;
  note?: string;
  independant: boolean;
}

export type Confiance = 'A' | 'B' | 'C';

export interface Chiffre {
  libelle: string;
  valeur: Valeur;
  unite: string;
  grandeur: string;
  periode: string;
  perimetre: string;
  source: Source;
  page: string;
  citation: string;
  confiance: Confiance;
  calcul?: string;
  recoupements?: Recoupement[];
  verification?: string;
  note?: string;
  /** Chiffre calculé par le site : étape du pipeline qui le produit (« pc build »). */
  produit_par?: string;
  /** Valeur calculée avant l'arrondi d'affichage. */
  valeur_calculee?: number;
  /** Pas d'arrondi de `valeur` (0,1 → une décimale). */
  precision?: number;
}

export type Chiffres = Record<string, Chiffre>;

/** Légende de la cote de confiance (docs/CONCEPTION.md, « Principes »). */
export const COTES: Record<Confiance, string> = {
  A: 'source primaire et recoupement indépendant (autre éditeur, autre méthode)',
  B: 'source primaire, sans recoupement indépendant',
  C: 'source secondaire, ou grandeur mal définie par la source'
};

/** Le chiffre `id`, ou une erreur explicite : un identifiant inconnu doit faire échouer le build. */
export function chiffre(chiffres: Chiffres, id: string): Chiffre {
  const c = Object.hasOwn(chiffres, id) ? chiffres[id] : undefined;
  if (!c) throw new Error(`Chiffre inconnu dans le référentiel : « ${id} »`);
  return c;
}

/** Les sources citées par le référentiel, dédoublonnées par clé. */
export function sourcesDe(chiffres: Chiffres): Map<string, Source> {
  const sources = new Map<string, Source>();
  for (const c of Object.values(chiffres)) sources.set(c.source.cle, c.source);
  return sources;
}

/** La valeur exprimée en MW (pour les puissances publiées en MW ou en GW). */
export function enMW(c: Chiffre): number {
  if (Array.isArray(c.valeur))
    throw new Error(`Intervalle inattendu pour une puissance : ${c.libelle}`);
  if (c.unite === 'MW') return c.valeur;
  if (c.unite === 'GW') return c.valeur * 1000;
  throw new Error(`Unité de puissance inattendue : « ${c.unite} » (${c.libelle})`);
}
