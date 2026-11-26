// Simulateur : années servies, CSV horaires (copiés tels quels par le prérendu) et textes de la page,
// rendus par la même chaîne que les enquêtes (chiffres du référentiel et notes).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { chiffre, sourcesDe, type Chiffres } from '$lib/chiffres';
import type { BlocEnquete } from '$lib/enquete';
import { formaterValeur } from '$lib/format';
import { typographier } from '$lib/markdown';
import { noteChiffre } from '$lib/notes';
import type { ChiffreCite, References } from '$lib/simulateur/references';
import { RACINE } from '$lib/server/makingof';
import { rendreCorps } from '$lib/server/enquetes';
import { chargerQuand } from '$lib/server/quand';

/** Années pleines (celles de quand.json), de la plus ancienne à la plus récente. */
export function anneesSimulateur(): number[] {
  return chargerQuand().annees.map((a) => a.annee);
}

/** Contenu exact de data/export/horaire/AAAA.csv d'une année pleine. */
export function csvHoraire(annee: number): string {
  if (!anneesSimulateur().includes(annee))
    throw new Error(`Simulateur : ${annee} n'est pas une année pleine de quand.json`);
  return readFileSync(resolve(RACINE, `data/export/horaire/${annee}.csv`), 'utf8');
}

const lireTexte = (nom: string) =>
  readFileSync(resolve(RACINE, 'site/src/lib/simulateur', nom), 'utf8');

/** Blocs HTML d'un texte du simulateur ; un graphique y est refusé (la page place le sien). */
function rendre(nom: string, chiffres: Chiffres): string[] {
  return rendreCorps(lireTexte(nom), chiffres).map((b: BlocEnquete) => {
    if (b.type !== 'html') throw new Error(`${nom} : directive de graphique non prévue`);
    return b.html;
  });
}

export function textesSimulateur(chiffres: Chiffres): { enTete: string[]; lecture: string[] } {
  const enTete = rendre('en-tete.md', chiffres);
  // Les notes sont numérotées par texte : une seule partie de la page peut en porter.
  if (enTete.some((h) => h.includes('data-note=')))
    throw new Error(
      'en-tete.md : pas de chiffre ni de source annotés dans l’en-tête du simulateur'
    );
  return { enTete, lecture: rendre('lecture.md', chiffres) };
}

/* eslint-disable @typescript-eslint/no-explicit-any -- lecture d'un JSON externe, validée champ par champ */

/** Repères des résultats : maximum pluriannuel (quand.json) et chiffres cités du référentiel. */
export function referencesSimulateur(chiffres: Chiffres): References {
  const q: any = JSON.parse(readFileSync(resolve(RACINE, 'data/export/quand.json'), 'utf8'));
  const m = q.rn_max_pluriannuel;
  if (
    typeof m?.valeur_mw !== 'number' ||
    typeof m?.debut_paris !== 'string' ||
    typeof m?.annees !== 'string'
  )
    throw new Error('quand.json : rn_max_pluriannuel absent ou incomplet');
  const sources = sourcesDe(chiffres);
  const cite = (id: string): ChiffreCite => {
    const c = chiffre(chiffres, id);
    return {
      id,
      texte: typographier(formaterValeur(c.valeur, c.unite, true, c.precision)),
      confiance: c.confiance,
      note: typographier(noteChiffre(null, c, sources))
    };
  };
  const productionPubliee: Record<number, ChiffreCite> = {};
  for (const a of anneesSimulateur())
    if (Object.hasOwn(chiffres, `prod_nucleaire_${a}`))
      productionPubliee[a] = cite(`prod_nucleaire_${a}`);
  const enMw = (id: string, attendue: string, facteur: number): number => {
    const c = chiffre(chiffres, id);
    if (c.unite !== attendue || typeof c.valeur !== 'number')
      throw new Error(
        `« ${id} » : ${c.unite} ${JSON.stringify(c.valeur)}, attendu un nombre en ${attendue}`
      );
    return Math.round(c.valeur * facteur * 1e6) / 1e6; // 102,1 × 1 000 sans bruit flottant
  };
  const annees = anneesSimulateur();
  const derniere = annees[annees.length - 1];
  // Repères du plancher : J moyen aux heures chères, dernière année et année où il est le plus haut.
  const avecJCher = annees.filter((a) => Object.hasOwn(chiffres, `quand_j_heures_cheres_${a}`));
  if (!avecJCher.includes(derniere))
    throw new Error(`quand_j_heures_cheres_${derniere} absent du référentiel`);
  const jCher = (a: number) => chiffre(chiffres, `quand_j_heures_cheres_${a}`).valeur as number;
  const anneeMax = avecJCher.reduce((m, a) => (jCher(a) > jCher(m) ? a : m), avecJCher[0]);
  const heuresCheres = chiffre(chiffres, `quand_heures_prix_chers_${anneeMax}`).valeur as number;
  return {
    maxPluriannuel: { valeur_mw: m.valeur_mw, debut_paris: m.debut_paris, annees: m.annees },
    marge: cite('marge_rte_hiver_2026_2027'),
    productionPubliee,
    productionPrevue: cite('prod_nucleaire_prevision_2026_2027'),
    gradient: {
      ...cite('thermosensibilite_hiver_rte'),
      mw_par_c: enMw('thermosensibilite_hiver_rte', 'MW/°C', 1)
    },
    record: {
      ...cite('pointe_conso_record_2012'),
      valeur_mw: enMw('pointe_conso_record_2012', 'GW', 1000)
    },
    recordHoraire: {
      ...cite('pointe_conso_record_2012_horaire'),
      valeur_mw: enMw('pointe_conso_record_2012_horaire', 'GW', 1000)
    },
    pointeFroids2010: {
      ...cite('pointe_froids_2010_hiver_2026_2027'),
      valeur_mw: enMw('pointe_froids_2010_hiver_2026_2027', 'GW', 1000)
    },
    froidPointe: { ...cite(`quand_froid_100gw_${derniere}`), annee: derniere },
    jHeuresCheres: { ...cite(`quand_j_heures_cheres_${derniere}`), annee: derniere },
    jHeuresCheresMax: {
      ...cite(`quand_j_heures_cheres_${anneeMax}`),
      annee: anneeMax,
      heures: heuresCheres
    }
  };
}
