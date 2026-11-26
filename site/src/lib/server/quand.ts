// Données des graphiques de « Quand ? », lues au prérendu dans data/export/quand.json (calculé par
// `pc build`, contrôlé par `pc check`). Lecture stricte : un champ manquant fait échouer le build.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import type { AnneeQuand, DonneesQuand, MatriceRn } from '$lib/quand';
import { RACINE } from '$lib/server/makingof';

/* eslint-disable @typescript-eslint/no-explicit-any -- lecture d'un JSON externe, validée champ par champ */

function exiger<T>(valeur: T | undefined | null, chemin: string): T {
  if (valeur === undefined || valeur === null)
    throw new Error(`quand.json : champ « ${chemin} » absent`);
  return valeur;
}

const nombre = (v: unknown, chemin: string): number => {
  if (typeof v !== 'number' || !Number.isFinite(v))
    throw new Error(`quand.json : « ${chemin} » n'est pas un nombre`);
  return v;
};

export function lireQuand(brut: any): DonneesQuand {
  const annees: AnneeQuand[] = Object.entries(exiger(brut.annees, 'annees') as Record<string, any>)
    .map(([a, d]) => {
      const c = `annees.${a}`;
      const rn = exiger(d.charge_residuelle, `${c}.charge_residuelle`);
      const q = exiger(rn.quantiles_mw, `${c}.charge_residuelle.quantiles_mw`);
      return {
        annee: Number(a),
        heures: nombre(d.heures, `${c}.heures`),
        heuresValides: nombre(rn.heures_valides, `${c}.charge_residuelle.heures_valides`),
        monotone: (exiger(rn.monotone, `${c}.charge_residuelle.monotone`) as unknown[]).map(
          (p, i) => {
            const [r, v] = p as [unknown, unknown];
            return [nombre(r, `${c}.monotone[${i}]`), nombre(v, `${c}.monotone[${i}]`)];
          }
        ) as [number, number][],
        maxMw: nombre(rn.max?.valeur_mw, `${c}.charge_residuelle.max.valeur_mw`),
        maxDebutParis: exiger(rn.max?.debut_paris, `${c}.charge_residuelle.max.debut_paris`),
        minMw: nombre(rn.min?.valeur_mw, `${c}.charge_residuelle.min.valeur_mw`),
        minDebutParis: exiger(rn.min?.debut_paris, `${c}.charge_residuelle.min.debut_paris`),
        quantilesMw: Object.fromEntries(
          ['p01', 'p05', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99'].map((k) => [
            k,
            nombre(q[k], `${c}.charge_residuelle.quantiles_mw.${k}`)
          ])
        ) as AnneeQuand['quantilesMw'],
        heuresNegatives: nombre(rn.heures_negatives, `${c}.charge_residuelle.heures_negatives`),
        chargesPlates: (exiger(d.charges_plates, `${c}.charges_plates`) as any[]).map((p, i) => ({
          xMw: nombre(p.x_mw, `${c}.charges_plates[${i}].x_mw`),
          partDansJ: nombre(p.part_dans_j, `${c}.charges_plates[${i}].part_dans_j`),
          partDansJPlancher: nombre(
            p.part_dans_j_plancher,
            `${c}.charges_plates[${i}].part_dans_j_plancher`
          ),
          plancherMw: nombre(p.plancher_mw, `${c}.charges_plates[${i}].plancher_mw`),
          heuresAuDessusDuMax: nombre(
            p.heures_rn_plus_x_au_dessus_du_max,
            `${c}.charges_plates[${i}].heures_rn_plus_x_au_dessus_du_max`
          ),
          heuresAuDessusDuMaxReference: nombre(
            p.heures_rn_plus_x_au_dessus_du_max_reference,
            `${c}.charges_plates[${i}].heures_rn_plus_x_au_dessus_du_max_reference`
          )
        }))
      };
    })
    .sort((a, b) => a.annee - b.annee);

  const matrices: MatriceRn[] = Object.entries(
    exiger(brut.matrices_rn, 'matrices_rn') as Record<string, any>
  )
    .filter(([a]) => /^\d{4}$/.test(a))
    .map(([a, m]) => {
      const jours = exiger(m.jours, `matrices_rn.${a}.jours`) as string[];
      const valeurs = exiger(m.valeurs, `matrices_rn.${a}.valeurs`) as (number | null)[][];
      if (valeurs.length !== jours.length || valeurs.some((l) => l.length !== 24))
        throw new Error(`quand.json : matrices_rn.${a} n'est pas une matrice jours × 24`);
      return { annee: Number(a), jours, valeurs };
    })
    .sort((a, b) => a.annee - b.annee);

  return {
    annees,
    matrices,
    sources: exiger(brut.donnees?.sources, 'donnees.sources'),
    extractions: exiger(brut.donnees?.extractions, 'donnees.extractions'),
    exclues: brut.annees_exclues ?? {},
    rnMaxPluriannuel: {
      valeurMw: nombre(brut.rn_max_pluriannuel?.valeur_mw, 'rn_max_pluriannuel.valeur_mw'),
      debutParis: exiger(brut.rn_max_pluriannuel?.debut_paris, 'rn_max_pluriannuel.debut_paris'),
      annee: Number(exiger(brut.rn_max_pluriannuel?.annee, 'rn_max_pluriannuel.annee')),
      annees: exiger(brut.rn_max_pluriannuel?.annees, 'rn_max_pluriannuel.annees')
    }
  };
}

let cache: DonneesQuand | undefined;

export function chargerQuand(): DonneesQuand {
  return (cache ??= lireQuand(
    JSON.parse(readFileSync(resolve(RACINE, 'data/export/quand.json'), 'utf8'))
  ));
}
