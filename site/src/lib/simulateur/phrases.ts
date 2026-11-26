// Phrases des résultats du simulateur, réunies ici pour être relues d'un bloc (et testées) :
// chaque chiffre avec son unité et le mot juste (« au plus », « prix observé, sans effet en
// retour », « ce n'est pas une défaillance »). Texte brut, sans HTML.
import { typographier } from '$lib/markdown';
import { gw, heureParis } from '$lib/quand';
import type { Etat } from './etat';
import { heures, part, prix, puissanceReglee, twh } from './format';
import type { Simulation } from './moteur';

export interface Tuile {
  titre: string;
  /** Qualificatif avant la valeur (« au plus »), le cas échéant. */
  qualif?: string;
  valeur: string;
  detail: string;
}

/**
 * @param sim simulation avec les hypothèses choisies
 * @param plate même puissance sans effacement (= `sim` si l'effacement est nul)
 * @param maxReglable nombre d'heures d'effacement maximal du réglage
 */
export function phrases(
  etat: Etat,
  sim: Simulation,
  plate: Simulation,
  maxReglable: number
): { scenario: string; tuiles: Tuile[] } {
  const x = puissanceReglee(etat.xGw);
  const effacees = sim.x_mw > 0 ? sim.heures_effacees.length : 0;
  const aucune = sim.x_mw === 0;

  const scenario =
    `${etat.annee} : consommation ajoutée de ${x} à toutes les heures` +
    (effacees
      ? ` sauf pendant les ${heures(effacees)} de charge résiduelle observée la plus élevée ` +
        `(au moins ${gw(sim.rn_seuil_effacement_mw as number)})`
      : '') +
    '.';

  const energie: Tuile = {
    titre: 'Énergie ajoutée',
    valeur: twh(sim.energie_ajoutee_twh),
    detail: aucune
      ? 'Aucune consommation ajoutée.'
      : `${x} × ${heures(sim.heures - sim.heures_charge_nulle)}` +
        (sim.heures_charge_nulle
          ? ` (${heures(sim.heures)} de l’année, moins ${heures(sim.heures_charge_nulle)} effacées).`
          : ', toute l’année.')
  };

  const s = sim.solde_echanges_moyen_heures_j_couvre_mw;
  const nucleaire: Tuile =
    sim.part_dans_j === null
      ? {
          titre: 'Dans le nucléaire disponible non produit',
          valeur: '—',
          detail: 'Aucune consommation ajoutée.'
        }
      : {
          titre: 'Dans le nucléaire disponible non produit',
          qualif: 'au plus',
          valeur: part(sim.part_dans_j),
          detail:
            `de l’énergie ajoutée, soit au plus ${twh(sim.energie_dans_j_twh)} de production ` +
            `nucléaire en plus sur l’année.` +
            (s === null
              ? ''
              : ` Quand ce nucléaire couvrirait toute la consommation ajoutée ` +
                `(${heures(sim.heures_j_couvre_charge)}), la France ${s < 0 ? 'exportait' : 'importait'} ` +
                `en moyenne ${gw(Math.abs(s))} : une partie serait d’abord servie par ` +
                `${s < 0 ? 'moins d’exportations' : 'plus d’importations'}.`)
        };

  const nEtoile = plate.heures_au_dessus_du_max ?? 0;
  const morceaux: string[] = [];
  if (sim.max_apres && sim.rn_max_mw !== null) {
    morceaux.push(
      sim.max_apres.valeur_mw > sim.rn_max_mw
        ? `Nouveau maximum de la charge résiduelle : ${gw(sim.max_apres.valeur_mw)} ` +
            `(${heureParis(sim.max_apres.debut_paris)}), contre ${gw(sim.rn_max_mw)} observés.`
        : `Le maximum reste celui observé, ${gw(sim.rn_max_mw)}.`
    );
    morceaux.push('Ce n’est pas une défaillance.');
  }
  if (effacees && nEtoile > 0) morceaux.push(`Sans effacement : ${heures(nEtoile)}.`);
  if (nEtoile > effacees)
    morceaux.push(
      `Pour ne jamais le dépasser, il faudrait effacer au moins ${heures(nEtoile)}, ` +
        `en les connaissant à l’avance` +
        (nEtoile > maxReglable ? ` (plus que les ${maxReglable} que propose le réglage).` : '.')
    );
  else if (effacees && nEtoile > 0)
    morceaux.push('Avec une prévision parfaite, l’effacement suffit à ne jamais le dépasser.');
  const maximum: Tuile = {
    titre: 'Heures au-delà du maximum observé',
    valeur: heures(sim.heures_au_dessus_du_max ?? 0),
    detail: morceaux.join(' ')
  };

  const sansPrix = 'Aucune consommation ajoutée aux heures où le prix est connu.';
  const prixBas: Tuile =
    sim.part_prix_nul_ou_negatif === null || sim.part_prix_negatif === null
      ? { titre: 'Énergie consommée à prix nul ou négatif', valeur: '—', detail: sansPrix }
      : {
          titre: 'Énergie consommée à prix nul ou négatif',
          valeur: part(sim.part_prix_nul_ou_negatif),
          detail:
            `dont ${part(sim.part_prix_negatif)} à prix strictement négatif. Prix observés, sans ` +
            `effet en retour : avec cette consommation, certains auraient été plus élevés.`
        };

  const prixMoyen: Tuile =
    sim.prix_moyen_pondere_eur_mwh === null
      ? { titre: 'Prix moyen pondéré par la consommation ajoutée', valeur: '—', detail: sansPrix }
      : {
          titre: 'Prix moyen pondéré par la consommation ajoutée',
          valeur: prix(sim.prix_moyen_pondere_eur_mwh),
          detail:
            'Prix day-ahead observé, sans effet en retour de la consommation ajoutée.' +
            (effacees && plate.prix_moyen_eur_mwh !== null
              ? ` Sans effacement : ${prix(plate.prix_moyen_eur_mwh)}.`
              : '')
        };

  return {
    scenario: typographier(scenario),
    tuiles: [energie, nucleaire, maximum, prixBas, prixMoyen].map((u) => ({
      ...u,
      detail: typographier(u.detail)
    }))
  };
}
