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
  /** Gradient hivernal de la consommation publié par RTE (MW par °C), pour le réglage du froid. */
  gradient: ChiffreCite & { mw_par_c: number };
  /** Pointe historique de consommation (février 2012, demi-heure, hors Corse), en MW. */
  record: ChiffreCite & { valeur_mw: number };
  /** Consommation horaire maximale de 2012 (moyenne des deux demi-heures), en MW : même pas de temps
   * que le simulateur. */
  recordHoraire: ChiffreCite & { valeur_mw: number };
  /** Pointes de l'hiver 2026-2027 estimées par RTE avec des froids comparables à ceux du début des
   * années 2010 (« sensiblement inférieures » à cette valeur), en MW. */
  pointeFroids2010: ChiffreCite & { valeur_mw: number };
  /** Froid réglable à partir duquel la consommation horaire maximale de la dernière année dépasse
   * cette pointe (calcul du site). */
  froidPointe: ChiffreCite & { annee: number };
  /** Nucléaire disponible non produit moyen aux heures chères de la dernière année : repère du plancher. */
  jHeuresCheres: ChiffreCite & { annee: number };
  /** La plus haute de ces moyennes annuelles, son année et son nombre d'heures chères. */
  jHeuresCheresMax: ChiffreCite & { annee: number; heures: number };
}
