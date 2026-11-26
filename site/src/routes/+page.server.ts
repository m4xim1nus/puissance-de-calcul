import { sourcesDe } from '$lib/chiffres';
import { typographier } from '$lib/markdown';
import { noteChiffre } from '$lib/notes';
import { chargerChiffres } from '$lib/server/chiffres';
import { chargerEnquete, lireFrontMatter, rendreCorps } from '$lib/server/enquetes';
import { lireFichier } from '$lib/server/makingof';
import { anneePrix, anneesPrix } from '$lib/server/prix';

export const prerender = true;

/** Année affichée par défaut : la dernière année complète. */
const ANNEE_DEFAUT = 2025;

export function load() {
  const chiffres = chargerChiffres();
  const sources = sourcesDe(chiffres);
  // Heures négatives publiées par RTE (référentiel), avec leur note ; les autres années sont un
  // calcul du site sur les données affichées.
  const references: Record<number, { valeur: number; note: string }> = {};
  for (const a of anneesPrix()) {
    const c = chiffres[`heures_negatives_${a}`];
    if (c && typeof c.valeur === 'number')
      references[a] = { valeur: c.valeur, note: typographier(noteChiffre(null, c, sources)) };
  }
  // Titre et question de l'enquête « Quand ? », tirés de son front matter (docs/enquetes/quand.md).
  const quand = chargerEnquete('quand', chiffres).meta;
  // Idem pour « Quel carbone ? » (docs/enquetes/carbone.md).
  const carbone = chargerEnquete('carbone', chiffres).meta;
  return {
    annees: anneesPrix(),
    initiale: anneePrix(ANNEE_DEFAUT),
    references,
    quand,
    carbone,
    message: chargerMessage(chiffres)
  };
}

/** Message principal (docs/MESSAGE.md) : chiffres du référentiel et notes, comme une enquête. */
function chargerMessage(chiffres: ReturnType<typeof chargerChiffres>) {
  const { meta, corps } = lireFrontMatter(lireFichier('docs/MESSAGE.md'));
  for (const champ of ['titre', 'mise_a_jour', 'repose_sur'])
    if (!meta[champ]) throw new Error(`docs/MESSAGE.md : champ « ${champ} » absent`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(meta.mise_a_jour))
    throw new Error("docs/MESSAGE.md : mise_a_jour n'est pas une date AAAA-MM-JJ");
  const blocs = rendreCorps(corps, chiffres).map((b) => {
    if (b.type !== 'html') throw new Error('docs/MESSAGE.md : pas de graphique dans le message');
    return b.html;
  });
  return {
    titre: typographier(meta.titre),
    miseAJour: meta.mise_a_jour,
    reposeSur: typographier(meta.repose_sur),
    blocs
  };
}
