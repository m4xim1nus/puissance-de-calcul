// Données du graphique de « Quel carbone ? », lues au prérendu dans data/export/carbone.json
// (calculé par `pc build`, contrôlé par `pc check`). Lecture stricte : un champ manquant fait
// échouer le build.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import type { AnneeCarbone, DonneesCarbone, MatriceCarbone, SerieAnnee } from '$lib/carbone';
import { RACINE } from '$lib/server/makingof';

/* eslint-disable @typescript-eslint/no-explicit-any -- lecture d'un JSON externe, validée champ par champ */

function exiger<T>(valeur: T | undefined | null, chemin: string): T {
  if (valeur === undefined || valeur === null)
    throw new Error(`carbone.json : champ « ${chemin} » absent`);
  return valeur;
}

const nombre = (v: unknown, chemin: string): number => {
  if (typeof v !== 'number' || !Number.isFinite(v))
    throw new Error(`carbone.json : « ${chemin} » n'est pas un nombre`);
  return v;
};

const nombreOuNul = (v: unknown, chemin: string): number | null =>
  v === null ? null : nombre(v, chemin);

function serie(s: any, c: string): SerieAnnee {
  const profil = exiger(s.profil_mensuel, `${c}.profil_mensuel`) as unknown[];
  if (profil.length !== 12) throw new Error(`carbone.json : ${c}.profil_mensuel n'a pas 12 mois`);
  return {
    moyenne: nombre(s.moyenne_ponderee, `${c}.moyenne_ponderee`),
    profilMensuel: profil.map((v, i) => nombreOuNul(v, `${c}.profil_mensuel[${i}]`)),
    max: nombre(s.max?.valeur, `${c}.max.valeur`),
    min: nombre(s.min?.valeur, `${c}.min.valeur`)
  };
}

export function lireCarbone(brut: any): DonneesCarbone {
  const annees: AnneeCarbone[] = Object.entries(
    exiger(brut.annees, 'annees') as Record<string, any>
  )
    .map(([a, d]) => ({
      annee: Number(a),
      production: serie(exiger(d.production, `annees.${a}.production`), `annees.${a}.production`),
      ...(d.consommation ? { consommation: serie(d.consommation, `annees.${a}.consommation`) } : {})
    }))
    .sort((x, y) => x.annee - y.annee);

  const matrices: MatriceCarbone[] = Object.entries(
    exiger(brut.matrices_mois_heure?.production, 'matrices_mois_heure.production') as Record<
      string,
      any
    >
  )
    .map(([a, m]) => {
      const valeurs = exiger(
        m.valeurs,
        `matrices_mois_heure.production.${a}.valeurs`
      ) as unknown[][];
      if (valeurs.length !== 12 || valeurs.some((l) => l.length !== 24))
        throw new Error(`carbone.json : matrice ${a} n'est pas 12 × 24`);
      return {
        annee: Number(a),
        valeurs: valeurs.map((l, i) =>
          l.map((v, h) => nombreOuNul(v, `matrices_mois_heure.production.${a}[${i}][${h}]`))
        )
      };
    })
    .sort((x, y) => x.annee - y.annee);

  return {
    annees,
    matrices,
    sources: exiger(brut.donnees?.sources, 'donnees.sources'),
    extractions: exiger(brut.donnees?.extractions, 'donnees.extractions')
  };
}

let cache: DonneesCarbone | undefined;

export function chargerCarbone(): DonneesCarbone {
  return (cache ??= lireCarbone(
    JSON.parse(readFileSync(resolve(RACINE, 'data/export/carbone.json'), 'utf8'))
  ));
}
