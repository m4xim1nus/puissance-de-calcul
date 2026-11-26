// Noms des graphiques qu'une enquête peut appeler par `::: graphique nom :::`.
// Le registre des composants (registre.ts) est typé sur cette liste : un nom sans composant ne
// compile pas, un nom inconnu dans une enquête fait échouer le build (server/enquetes.ts).
export const NOMS_GRAPHIQUES = [
  'estimations-2024',
  'pyramide',
  'trajectoires',
  'monotone-rn',
  'heatmap-rn',
  'charge-plate',
  'carbone-mois-heure'
] as const;
export type NomGraphique = (typeof NOMS_GRAPHIQUES)[number];

export const estNomGraphique = (nom: string): nom is NomGraphique =>
  (NOMS_GRAPHIQUES as readonly string[]).includes(nom);
