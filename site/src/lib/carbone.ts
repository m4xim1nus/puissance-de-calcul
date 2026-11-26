// Données et mise en forme du graphique de l'enquête « Quel carbone ? ». Les valeurs viennent de
// data/export/carbone.json (calculé par `pc build`, contrôlé par `pc check`) : des intensités
// MOYENNES, jamais des facteurs marginaux. Ce module ne fait que les classer et les formater.
import { FINE, dateParis, formaterDate, formaterNombre } from '$lib/format';

/** Statistiques d'une série (production ou consommation) sur une année. */
export interface SerieAnnee {
  /** Moyenne annuelle pondérée (gCO2eq/kWh). */
  moyenne: number;
  /** Moyennes mensuelles pondérées, janvier en premier ; null = mois sans donnée. */
  profilMensuel: (number | null)[];
  max: number;
  min: number;
}

export interface AnneeCarbone {
  annee: number;
  production: SerieAnnee;
  /** Absente avant 2021 (série de RTE publiée depuis 2021). */
  consommation?: SerieAnnee;
}

/** Matrice mois (lignes, janvier = 0) × heure de Paris de début (24 colonnes), gCO2eq/kWh. */
export interface MatriceCarbone {
  annee: number;
  valeurs: (number | null)[][];
}

export interface DonneesCarbone {
  annees: AnneeCarbone[];
  /** Matrices de la production (2022 et dernière année pleine). */
  matrices: MatriceCarbone[];
  sources: string;
  extractions: Record<string, string>;
}

/** Bornes basses des classes (gCO2eq/kWh), de la plus claire à la plus foncée. */
export const SEUILS_CO2 = [10, 20, 40, 60] as const;

/** Jetons de couleur des classes (app.css), séquentiels. */
export const JETONS_CO2 = ['--co2-0', '--co2-1', '--co2-2', '--co2-3', '--co2-4'] as const;

/** Classe (0 à 4) d'une intensité. */
export function classeCo2(g: number): number {
  let k = 0;
  while (k < SEUILS_CO2.length && g >= SEUILS_CO2[k]) k++;
  return k;
}

/** Libellé d'une classe : « moins de 10 », « 10 à 20 », « 50 et plus » (gCO2eq/kWh). */
export function libelleClasseCo2(k: number): string {
  const s = (g: number) => formaterNombre(g, 0);
  if (k === 0) return `moins de ${s(SEUILS_CO2[0])}`;
  if (k === SEUILS_CO2.length) return `${s(SEUILS_CO2.at(-1)!)} et plus`;
  return `${s(SEUILS_CO2[k - 1])} à ${s(SEUILS_CO2[k])}`;
}

/** 18.359 → « 18,4 g » (une décimale, toujours) ; sans unité si `unite` est faux. */
export function grammes(g: number, unite = true): string {
  const n = formaterNombre(g, 1);
  const fixe = /,\d$/.test(n) ? n : `${n},0`;
  return unite ? `${fixe}${FINE}g` : fixe;
}

const NOMS_EXTRACTIONS: Record<string, string> = {
  eco2mix: 'éCO2mix',
  odre_ges_conso: 'intensité de la consommation (ODRÉ)'
};

/** Ligne « Sources » du graphique : calcul du site, séries, extractions. */
export function sourcesCarbone(d: DonneesCarbone): string {
  const extraits = Object.entries(d.extractions)
    .filter(([, iso]) => iso)
    .map(([k, iso]) => `${NOMS_EXTRACTIONS[k] ?? k} le ${formaterDate(dateParis(iso))}`)
    .join(', ');
  return `Calcul du site (data/export/carbone.json, pc build) sur ${d.sources}. Extraction : ${extraits}.`;
}
