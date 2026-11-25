// Composant de chaque graphique appelable depuis une enquête. Le type impose un composant par nom
// déclaré dans noms.ts.
import type { Component } from 'svelte';
import type { Chiffres } from '$lib/chiffres';
import Estimations2024 from './Estimations2024.svelte';
import Pyramide from './Pyramide.svelte';
import Trajectoires from './Trajectoires.svelte';
import type { NomGraphique } from './noms';

export const GRAPHIQUES: Record<NomGraphique, Component<{ chiffres: Chiffres }>> = {
  'estimations-2024': Estimations2024,
  pyramide: Pyramide,
  trajectoires: Trajectoires
};
