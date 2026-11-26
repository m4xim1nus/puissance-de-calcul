import { sourcesDe } from '$lib/chiffres';
import { typographier } from '$lib/markdown';
import { noteChiffre } from '$lib/notes';
import { accroche, lireMessage, rendreSection } from '$lib/server/accueil';
import { chargerChiffres } from '$lib/server/chiffres';
import { anneePrix, anneesPrix } from '$lib/server/prix';

export const prerender = true;

/** Année affichée par défaut : la dernière année complète. */
const ANNEE_DEFAUT = 2025;
/** Enquêtes de l'accueil, dans l'ordre de lecture proposé. */
const ENQUETES = ['combien', 'quand', 'carbone', 'ou'] as const;

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
  // Notes numérotées dans l'ordre de la page : « À retenir », accroches, message en détail.
  const msg = lireMessage();
  const retenir = rendreSection(msg.retenir, chiffres, 0);
  let n = retenir.derniere;
  const accroches = ENQUETES.map((slug) => {
    const a = accroche(slug, chiffres, n);
    n = Math.max(n, ...[...a.notes.matchAll(/id="note-(\d+)"/g)].map((m) => Number(m[1])));
    return a;
  });
  const detail = rendreSection(msg.detail, chiffres, n);
  const changements = rendreSection(msg.changements, chiffres, detail.derniere);
  return {
    annees: anneesPrix(),
    initiale: anneePrix(ANNEE_DEFAUT),
    references,
    accroches,
    message: {
      titre: msg.titre,
      miseAJour: msg.miseAJour,
      version: msg.version,
      reposeSur: msg.reposeSur,
      retenir: retenir.blocs,
      detail: detail.blocs,
      changements: changements.blocs
    }
  };
}
