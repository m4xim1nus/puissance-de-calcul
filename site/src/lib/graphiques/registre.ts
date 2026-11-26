// Composant de chaque graphique appelable depuis une enquête. Le type impose un composant par nom
// déclaré dans noms.ts. Chaque graphique reçoit le référentiel des chiffres et, s'il en a besoin,
// les données propres à son enquête (`donnees`, chargées au prérendu par la route).
import type { Component } from 'svelte';
import type { Chiffres } from '$lib/chiffres';
import type { DonneesCarbone } from '$lib/carbone';
import type { DonneesQuand } from '$lib/quand';
import CarboneMoisHeure from './CarboneMoisHeure.svelte';
import ChargePlate from './ChargePlate.svelte';
import Estimations2024 from './Estimations2024.svelte';
import HeatmapRn from './HeatmapRn.svelte';
import MonotoneRn from './MonotoneRn.svelte';
import Pyramide from './Pyramide.svelte';
import Trajectoires from './Trajectoires.svelte';
import type { NomGraphique } from './noms';

/** Données propres à une enquête, en plus du référentiel. */
export interface DonneesEnquete {
  quand?: DonneesQuand;
  carbone?: DonneesCarbone;
}

export type PropsGraphique = { chiffres: Chiffres; donnees?: DonneesEnquete };

export const GRAPHIQUES: Record<NomGraphique, Component<PropsGraphique>> = {
  'estimations-2024': Estimations2024,
  pyramide: Pyramide,
  trajectoires: Trajectoires,
  'monotone-rn': MonotoneRn,
  'heatmap-rn': HeatmapRn,
  'charge-plate': ChargePlate,
  'carbone-mois-heure': CarboneMoisHeure
};

/** Les données de « Quand ? », ou une erreur explicite si la route ne les a pas chargées. */
export function donneesQuand(d: DonneesEnquete | undefined): DonneesQuand {
  if (!d?.quand)
    throw new Error('Graphique de « Quand ? » sans ses données (data/export/quand.json)');
  return d.quand;
}

/** Les données de « Quel carbone ? », ou une erreur explicite si la route ne les a pas chargées. */
export function donneesCarbone(d: DonneesEnquete | undefined): DonneesCarbone {
  if (!d?.carbone)
    throw new Error('Graphique de « Quel carbone ? » sans ses données (data/export/carbone.json)');
  return d.carbone;
}
