// Simulateur : années servies, CSV horaires (copiés tels quels par le prérendu) et textes de la page,
// rendus par la même chaîne que les enquêtes (chiffres du référentiel et notes).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import type { Chiffres } from '$lib/chiffres';
import type { BlocEnquete } from '$lib/enquete';
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
