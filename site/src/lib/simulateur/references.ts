// Repères extérieurs à l'année simulée, préparés au prérendu (src/lib/server/simulateur.ts) :
// maximum pluriannuel de la charge résiduelle (quand.json) et chiffres du référentiel cités dans
// les résultats, avec leur note (source, page, confiance). Aucun nombre de source tapé à la main.

/** Un chiffre du référentiel, déjà mis en forme, et sa note HTML (rendue avec {@html}). */
export interface ChiffreCite {
  id: string;
  /** Valeur avec son unité, typographiée (« 8 à 10 GW »). */
  texte: string;
  confiance: 'A' | 'B' | 'C';
  note: string;
}

export interface References {
  /** Maximum horaire de la charge résiduelle sur les années pleines (quand.json). */
  maxPluriannuel: { valeur_mw: number; debut_paris: string; annees: string };
  /** Marges de sécurité d'approvisionnement évaluées par RTE pour l'hiver 2026-2027 (BP2025). */
  marge: ChiffreCite;
  /** Production nucléaire publiée par RTE, par année (seulement celles du référentiel). */
  productionPubliee: Record<number, ChiffreCite>;
  /** Production nucléaire projetée par l'exploitant pour 2026-2027. */
  productionPrevue: ChiffreCite;
}
