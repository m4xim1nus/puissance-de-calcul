// Placement d'étiquettes autour d'une ligne de points : chaque étiquette part de son point (ou s'y
// termine), sous la ligne (voie 0) ou au-dessus (voie −1), puis sur des voies plus éloignées reliées
// au point par un trait de renvoi. Ni chevauchement d'étiquettes, ni renvoi qui traverse une
// étiquette.

export interface EtiquettePlacee {
  /** Abscisse d'ancrage du texte. */
  x: number;
  ancre: 'start' | 'end';
  /** 0, 1, 2… sous la ligne ; −1, −2… au-dessus. */
  voie: number;
}

/** Largeur approximative d'un texte en Barlow Semi Condensed (≈ 0,5 em par caractère). */
export const largeurTexte = (texte: string, taille: number) => texte.length * taille * 0.5;

const VOIES = [0, -1, 1, -2, 2, -3, 3, -4, 4];
/** Essais dans l'ordre : par paire de voies (dessous, dessus), l'étiquette qui part du point avant
 *  celle qui s'y termine (une étiquette alignée à droite se lit mal quand d'autres points sont à
 *  sa gauche). */
const ESSAIS = [0, 2, 4, 6].flatMap((k) =>
  (['start', 'end'] as const).flatMap((ancre) =>
    [VOIES[k], VOIES[k + 1]].map((voie) => ({ voie, ancre }))
  )
);

/** Voies traversées par le renvoi d'une étiquette posée sur `voie`. */
const traversees = (voie: number): number[] =>
  voie > 0
    ? Array.from({ length: voie }, (_, k) => k)
    : Array.from({ length: -voie - 1 }, (_, k) => -k - 1);

export function placerEtiquettes(
  items: { x: number; largeur: number }[],
  largeurTotale: number,
  ecart = 10
): EtiquettePlacee[] {
  const occupe = new Map<number, [number, number][]>();
  const libre = (voie: number, a: number, b: number, marge = ecart) =>
    !(occupe.get(voie) ?? []).some(([c, d]) => a < d + marge && b + marge > c);
  const prendre = (voie: number, a: number, b: number) =>
    occupe.set(voie, [...(occupe.get(voie) ?? []), [a, b]]);

  const ordre = items.map((_, i) => i).sort((a, b) => items[a].x - items[b].x);
  const res: EtiquettePlacee[] = new Array(items.length);
  for (const i of ordre) {
    const { x, largeur } = items[i];
    const debuts = { start: x - 4, end: x + 4 - largeur };
    const tient = (a: 'start' | 'end') => debuts[a] >= 0 && debuts[a] + largeur <= largeurTotale;
    // Si aucun ancrage ne tient dans la largeur, on garde le moins débordant.
    const repli: 'start' | 'end' = x < largeurTotale / 2 ? 'start' : 'end';
    let choix: EtiquettePlacee | undefined;
    // Premier passage : renvoi libre exigé ; second passage (écran étroit, points serrés) : le
    // renvoi peut passer derrière une étiquette, masqué par le halo du texte.
    for (const exigerRenvoi of [true, false]) {
      for (const { voie, ancre } of ESSAIS) {
        if (!tient(ancre) && (tient('start') || tient('end') || ancre !== repli)) continue;
        const renvoiLibre =
          !exigerRenvoi || traversees(voie).every((v) => libre(v, x - 1, x + 1, 2));
        const debut = debuts[ancre];
        if (renvoiLibre && libre(voie, debut, debut + largeur)) {
          prendre(voie, debut, debut + largeur);
          for (const v of traversees(voie)) prendre(v, x - 1, x + 1);
          choix = { x: ancre === 'start' ? x - 4 : x + 4, ancre, voie };
          break;
        }
      }
      if (choix) break;
    }
    // Faute de place, une voie de plus sous la ligne.
    res[i] = choix ?? { x: x - 4, ancre: 'start', voie: VOIES.length };
  }
  return res;
}
