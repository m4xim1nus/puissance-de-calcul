// Phrases des résultats du simulateur, réunies ici pour être relues d'un bloc (et testées) :
// chaque chiffre avec son unité et le mot juste (« au plus », « prix observés, sans effet en
// retour », « pas une défaillance »). Texte brut, sans HTML ; les notes des chiffres du référentiel
// (HTML, préparées au prérendu) sont rendues à part (`notes`).
//
// Corrections de la relecture du 26/11/2026 (docs/relectures/2026-11-26-simulateur.md) : aucune
// causalité attribuée aux exportations (SF1), fourchette avec et sans plancher de J et énergie mise
// en regard de la production (SF2), deux maxima de référence et cas trivial de l'heure du maximum
// (SF3), effacement présenté comme borne basse et circulaire, énergie effacée perdue (SF4), pas de
// prix moyen pondéré (SF5), rapprochement avec les marges de RTE (SF6).
//
// Limites traitées le 26/11/2026 (docs/SIMULATEUR.md) : froid supplémentaire sur un épisode (pas un
// écart aux normales, double compte dit), plancher de J réglable. Puis (ERREURS.md, « un plafond qui
// dépend de ce qu'EDF déclare indisponible ») : le « au plus » du nucléaire disponible non produit
// vaut avec la disponibilité déclarée par EDF ; la tuile donne aussi la valeur en réintégrant les
// arrêts courts qu'EDF déclare indisponibles pour modulation (seconde valeur, `complement` ; arrêts
// de moins de 7 jours seulement, relecture du 26/11/2026, F2). Repère du froid en consommation, pas
// en degrés sous les normales (même relecture, F1). Avec du froid, les phrases
// « effacer N* heures suffit » ne valent que si le froid seul ne dépasse pas le maximum (`seul`).
import { typographier } from '$lib/markdown';
import { gw, heureParis } from '$lib/quand';
import type { Etat } from './etat';
import { FINE, INSECABLE, dateParis, formaterDate, formaterNombre } from '$lib/format';
import { heures, part, puissanceReglee, twh } from './format';
import type { Simulation } from './moteur';
import type { References } from './references';

export interface Tuile {
  titre: string;
  /** Qualificatif avant la valeur (« au plus »), le cas échéant. */
  qualif?: string;
  valeur: string;
  /** Seconde valeur, plus petite, sous la valeur (variante), le cas échéant. */
  complement?: string;
  detail: string;
  /** Notes HTML des chiffres du référentiel cités dans le détail. */
  notes?: string[];
}

/** « l'heure » ou « les 12 heures » (évite « les 1 heure »). */
const lesHeures = (n: number) => (n === 1 ? 'l’heure' : `les ${heures(n)}`);
/** « 1 heure effacée », « 3 heures effacées ». */
const effacees = (n: number) => `${heures(n)} effacée${n >= 2 ? 's' : ''}`;

export interface OptionsPhrases {
  /** Nombre d'heures d'effacement maximal du réglage. */
  maxReglable: number;
  /** Année la plus récente proposée : la prévision de l'exploitant n'est rapprochée que d'elle. */
  derniereAnnee: number;
}

/** « 39 à 52 % », ou « 52 % » si les deux bornes s'écrivent pareil. */
const fourchette = (bas: number, haut: number) => {
  const b = part(bas);
  const h = part(haut);
  return b === h ? h : `${b.replace(/\s%$/, '')} à ${h}`;
};

/** « 1,5 °C » (pas de 0,5). */
const degres = (c: number) => `${formaterNombre(c, 1)}${FINE}°C`;

/** Période d'heures UTC (début de la première, début de la dernière) en dates de Paris :
 * « du 13 au 20 janv. 2025 », « du 28 févr. au 7 mars 2025 », « du 28 déc. 2024 au 4 janv. 2025 ». */
function periodeParis(debutUtc: string, derniereUtc: string): string {
  const fin = new Date(Date.parse(derniereUtc) + 3_600_000).toISOString().slice(0, 16) + 'Z';
  const [a, b] = [debutUtc, fin].map((h) => formaterDate(dateParis(h), true).split(INSECABLE));
  const debut =
    a[2] !== b[2] ? a.join(INSECABLE) : a[1] !== b[1] ? `${a[0]}${INSECABLE}${a[1]}` : a[0];
  return `du ${debut} au ${b.join(INSECABLE)}`;
}

/** Durée d'un épisode : « 7 jours » si elle tombe juste, sinon en heures. */
const duree = (h: number) => (h % 24 === 0 ? `${h / 24}${INSECABLE}jours` : heures(h));

/**
 * @param sim simulation avec les hypothèses choisies (seuil de référence = maximum pluriannuel)
 * @param plate même puissance sans effacement (= `sim` si l'effacement est nul)
 * @param seul froid seul : X nul, sans effacement, même froid (null sans froid)
 */
export function phrases(
  etat: Etat,
  sim: Simulation,
  plate: Simulation,
  refs: References,
  options: OptionsPhrases,
  seul: Simulation | null = null
): { scenario: string; tuiles: Tuile[] } {
  const x = puissanceReglee(etat.xGw);
  const aucune = sim.x_mw === 0;
  const froid = sim.froid_heures > 0 && sim.froid_ajout_mw > 0;
  const nEff = aucune ? 0 : sim.heures_effacees.length;
  const pluri = refs.maxPluriannuel;
  const datePluri = heureParis(pluri.debut_paris);
  // Heures au-delà des maxima dues au froid seul : aucun effacement de la charge ne les supprime.
  const seulAu = froid && seul ? (seul.heures_au_dessus_du_max ?? 0) : 0;
  const seulRef = froid && seul ? (seul.heures_au_dessus_du_max_reference ?? 0) : 0;

  const partFroid = froid
    ? ` Froid supplémentaire de ${degres(sim.froid_c)} pendant les ${duree(sim.froid_heures)} les ` +
      `plus tendus, ${periodeParis(sim.froid_debut_utc as string, sim.froid_fin_utc as string)} : ` +
      `${gw(sim.froid_ajout_mw)} de consommation en plus à chaque heure.`
    : '';
  const scenario =
    (aucune
      ? `${etat.annee} : aucune consommation ajoutée (X = 0)` +
        (etat.effacement ? ' ; l’effacement est sans objet.' : '.')
      : `${etat.annee} : consommation ajoutée de ${x} à toutes les heures` +
        (nEff
          ? ` sauf pendant ${lesHeures(nEff)} de charge résiduelle ${froid ? 'la plus élevée, froid compris' : 'observée la plus élevée'} ` +
            `(au moins ${gw(sim.rn_seuil_effacement_mw as number)})`
          : '') +
        '.') + partFroid;

  /* ---------- 1. Énergie ---------- */
  const energie: Tuile = {
    titre: 'Énergie ajoutée',
    valeur: twh(sim.energie_ajoutee_twh),
    detail: aucune
      ? 'Aucune consommation ajoutée.'
      : `${x} × ${heures(sim.heures - nEff)}` +
        (nEff
          ? ` (${heures(sim.heures)} de l’année, moins ${effacees(nEff)}). ` +
            `L’énergie effacée, ${twh(sim.energie_effacee_twh)}, est perdue : le simulateur ne la ` +
            'reporte ni sur d’autres heures ni sur un autre site.'
          : ', toute l’année.')
  };

  /* ---------- 2. Marge (rapprochement, consommation plate) ---------- */
  const marge: Tuile = aucune
    ? {
        titre: 'Marge de sécurité d’approvisionnement',
        valeur: '—',
        detail: 'Aucune consommation ajoutée.'
      }
    : nEff
      ? {
          titre: 'Marge de sécurité d’approvisionnement',
          valeur: 'non calculable ici',
          detail:
            `Sans effacement, une consommation plate de ${x} retirerait à peu près ${x} de marge ` +
            `(rapprochement du site, à comparer aux ${refs.marge.texte} évalués par RTE pour ` +
            'l’hiver 2026-2027). Combien de marge l’effacement rend, le simulateur ne sait pas le ' +
            'dire : seul un calcul probabiliste, comme celui de RTE, le peut.',
          notes: [refs.marge.note]
        }
      : {
          titre: 'Marge de sécurité d’approvisionnement',
          qualif: 'à peu près',
          valeur: `${x} en moins`,
          detail:
            `Dans un calcul d’adéquation, consommer ${x} en permanence revient à retirer à peu ` +
            `près ${x} de capacité toujours disponible : rapprochement du site, pour une ` +
            `consommation plate. RTE évaluait les marges de l’hiver 2026-2027 à ${refs.marge.texte} ` +
            '(Bilan prévisionnel 2025), avant la baisse de disponibilité nucléaire prévue pour cet hiver.',
          notes: [refs.marge.note]
        };

  /* ---------- 3. Maximum de l'année ---------- */
  const nEtoile = plate.heures_au_dessus_du_max ?? 0;
  const au = sim.heures_au_dessus_du_max ?? 0;
  const m: string[] = [];
  if (aucune && !froid)
    m.push(`Aucune consommation ajoutée : le maximum reste ${gw(sim.rn_max_mw ?? 0)}.`);
  else if (sim.max_apres && sim.rn_max_mw !== null) {
    m.push(`Maximum observé de ${etat.annee} : ${gw(sim.rn_max_mw)}.`);
    if (!nEff && !aucune)
      m.push(
        'Ce compte vaut au moins 1 dès que X est positif : l’heure du maximum se dépasse ' +
          'elle-même' +
          (au === 1 ? ', et c’est la seule ici.' : '.')
      );
    // L'heure du maximum est-elle dans l'épisode ? Alors le moindre froid la fait se dépasser elle-même.
    const maxDansEpisode =
      froid &&
      sim.rn_max_heure_utc !== null &&
      sim.froid_debut_utc !== null &&
      sim.froid_fin_utc !== null &&
      sim.rn_max_heure_utc >= sim.froid_debut_utc &&
      sim.rn_max_heure_utc <= sim.froid_fin_utc;
    if (froid)
      m.push(
        seulAu > 0
          ? `Le froid supplémentaire, à lui seul, porte la charge résiduelle au-delà de ce maximum ` +
              `pendant ${heures(seulAu)}` +
              (maxDansEpisode
                ? ' (l’heure du maximum, dans l’épisode, se dépasse elle-même dès le moindre froid)'
                : '') +
              ` : aucun effacement de la consommation ajoutée ne ${seulAu > 1 ? 'les' : 'la'} supprime.`
          : 'Le froid supplémentaire, à lui seul, ne dépasse pas ce maximum.'
      );
    if (sim.max_apres.valeur_mw > sim.rn_max_mw)
      m.push(
        `Nouveau maximum : ${gw(sim.max_apres.valeur_mw)} (${heureParis(sim.max_apres.debut_paris)}).`
      );
    if (nEff && nEtoile > 0) m.push(`Sans effacement : ${heures(nEtoile)}.`);
    if (aucune) {
      // Froid seul : pas de consommation ajoutée à effacer.
    } else if (nEtoile > nEff && seulAu > 0)
      m.push(
        `En effaçant les ${heures(nEtoile)} les plus tendues, en les connaissant à l’avance, il ` +
          `resterait ${seulAu > 1 ? `les ${heures(seulAu)} dues` : 'l’heure due'} au froid seul.`
      );
    else if (nEtoile > nEff)
      m.push(
        `Pour ne jamais dépasser ce maximum, il faudrait effacer au moins ${heures(nEtoile)}, en ` +
          (nEtoile > 1 ? 'les' : 'la') +
          ' connaissant à l’avance : c’est une borne basse' +
          (nEtoile > options.maxReglable
            ? ` (plus que les ${options.maxReglable} heures que propose le réglage).`
            : '.')
      );
    else if (nEff && nEtoile > 0 && seulAu === 0)
      m.push(
        'Par construction, les heures effacées sont celles que compte cet indicateur : avec ' +
          `${heures(nEtoile)} ou plus, il tombe à zéro. Cela ne dit rien d’un effacement réel, ` +
          'qui ne connaît pas ces heures à l’avance.'
      );
    if (au > 0) m.push('Dépasser un maximum observé n’est pas une défaillance.');
  }
  const maxAnnee: Tuile = {
    titre: `Heures au-delà du maximum de ${etat.annee}`,
    valeur: heures(au),
    detail: m.join(' ')
  };

  /* ---------- 4. Maximum 2015-2025 ---------- */
  const auRef = sim.heures_au_dessus_du_max_reference ?? 0;
  const nEtoileRef = plate.heures_au_dessus_du_max_reference ?? 0;
  const r: string[] = [
    `${gw(pluri.valeur_mw)}, le ${datePluri} : le plus haut de ${pluri.annees}.`
  ];
  // Constat de docs/enquetes/quand.md sur cette heure-là : écrit seulement si c'est bien elle.
  if (pluri.debut_paris.startsWith('2018-02-27T19:'))
    r.push(
      'Le système l’a couvert avec d’autres moyens : du charbon et du fioul, et des importations importantes.'
    );
  if ((!aucune || froid) && sim.max_apres && sim.max_apres.valeur_mw > pluri.valeur_mw)
    r.push(`Le nouveau maximum le dépasse de ${gw(sim.max_apres.valeur_mw - pluri.valeur_mw)}.`);
  if (froid && seulRef > 0)
    r.push(
      `Le froid supplémentaire, à lui seul, le dépasse pendant ${heures(seulRef)} : aucun ` +
        `effacement de la consommation ajoutée ne ${seulRef > 1 ? 'les' : 'la'} supprime.`
    );
  else if (!aucune && nEtoileRef > nEff)
    r.push(
      `Pour ne jamais le dépasser, il faudrait effacer au moins ${heures(nEtoileRef)}, en ` +
        (nEtoileRef > 1 ? 'les' : 'la') +
        ' connaissant à l’avance : borne basse.'
    );
  if (auRef > 0)
    r.push(
      'Ce n’est pas une défaillance, mais c’est au-delà de tout ce que le système a couvert de 2015 à 2025.'
    );
  const maxPluri: Tuile = {
    titre: `Heures au-delà du maximum ${pluri.annees}`,
    valeur: heures(auRef),
    detail: r.join(' ')
  };

  /* ---------- 5. Nucléaire disponible non produit ---------- */
  const notesJ: string[] = [];
  let nucleaire: Tuile;
  if (sim.part_dans_j === null || sim.part_dans_j_plancher === null) {
    nucleaire = {
      titre: 'Dans le nucléaire disponible non produit',
      valeur: '—',
      detail: 'Aucune consommation ajoutée.'
    };
  } else {
    const haut = part(sim.part_dans_j);
    const bas = part(sim.part_dans_j_plancher);
    const r = sim.reintegre;
    const avecR = r !== null && r.part_dans_j !== null && r.part_dans_j_plancher !== null;
    const valR = avecR ? fourchette(r.part_dans_j_plancher as number, r.part_dans_j as number) : '';
    const valD = fourchette(sim.part_dans_j_plancher, sim.part_dans_j);
    const memes = avecR && valR === valD;
    const prodAnnee = sim.production_nucleaire_twh;
    const publiee = refs.productionPubliee[etat.annee];
    let comparaison =
      `Ce serait au plus ${twh(sim.energie_dans_j_twh)} de production nucléaire en plus sur ` +
      `l’année (${twh(sim.energie_dans_j_plancher_twh)} avec le plancher), pour une production ` +
      `observée de ${twh(prodAnnee)} en ${etat.annee}`;
    if (publiee) {
      comparaison += ` (RTE publie ${publiee.texte})`;
      notesJ.push(publiee.note);
    }
    if (etat.annee === options.derniereAnnee) {
      comparaison += ` ; l’exploitant prévoit ${refs.productionPrevue.texte} par an pour 2026-2027 (confiance ${refs.productionPrevue.confiance})`;
      notesJ.push(refs.productionPrevue.note);
    }
    comparaison += '.';
    const declare =
      'Ces parts valent avec la disponibilité déclarée par EDF. EDF déclare indisponibles, comme ' +
      'des arrêts planifiés, des arrêts et baisses « pour modulation ». Ceux de moins de 7 jours, ' +
      'décidés au jour le jour, sont économiques : le plus souvent, la tranche sera redémarrée « si ' +
      'les conditions économiques le justifient ». Les plus longs peuvent relever de la gestion du ' +
      'combustible et restent retranchés. ' +
      (!avecR
        ? ''
        : memes
          ? `En ${etat.annee}, réintégrer les arrêts courts ne change pas ces parts. `
          : `En réintégrant les arrêts courts, ce serait ${valR}, et au plus ` +
            `${twh((r as NonNullable<typeof r>).energie_dans_j_twh)} de production nucléaire en plus. `);
    nucleaire = {
      titre: 'Dans le nucléaire disponible non produit',
      qualif: 'au plus',
      valeur: valD,
      complement: avecR
        ? memes
          ? 'disponibilité déclarée par EDF ; même valeur en réintégrant ses arrêts courts pour modulation'
          : `disponibilité déclarée par EDF ; ${valR} en réintégrant ses arrêts courts pour modulation`
        : 'avec la disponibilité déclarée par EDF',
      detail:
        (sim.plancher_mw > 0
          ? `de l’énergie ajoutée : ${haut} sans plancher, ${bas} en retranchant ` +
            `${gw(sim.plancher_mw)} de ce nucléaire à toute heure (plancher réglable, hypothèse du ` +
            'site : une part n’est pas mobilisable). '
          : `de l’énergie ajoutée, sans plancher (réglé à 0) : borne haute seule, qui compte ` +
            'comme mobilisable tout le nucléaire disponible non produit. ') +
        (froid
          ? 'Pendant l’épisode de froid, la consommation due au froid passe d’abord : la ' +
            'consommation ajoutée ne trouve que ce qu’elle laisse. La production nucléaire en plus ' +
            'affichée ne compte que la consommation ajoutée : celle que le froid prend d’abord s’y ' +
            'ajouterait. '
          : '') +
        `${comparaison} ${declare}La puissance restée inemployée heure par heure ne dit pas ` +
        'que le combustible et le calendrier des arrêts suivraient : en énergie, la limite est ' +
        'plus nette.',
      notes: notesJ
    };
  }

  /* ---------- 6. Heures où ce nucléaire suffirait : un constat sur les échanges ---------- */
  const s = sim.solde_echanges_moyen_heures_j_couvre_mw;
  const echanges: Tuile =
    aucune || s === null
      ? {
          titre: 'Heures où ce nucléaire suffirait',
          valeur: aucune ? '—' : heures(sim.heures_j_couvre_charge),
          detail: aucune
            ? 'Aucune consommation ajoutée.'
            : 'Heures où le nucléaire disponible non produit aurait suffi à couvrir toute la consommation ajoutée.'
        }
      : {
          titre: 'Heures où ce nucléaire suffirait',
          valeur: heures(sim.heures_j_couvre_charge),
          detail:
            'où le nucléaire disponible non produit aurait suffi à couvrir toute la consommation ' +
            `ajoutée. La France y ${s < 0 ? 'exportait' : 'importait'} en moyenne ${gw(Math.abs(s))} : ` +
            'c’est un constat. Qui servirait la consommation ajoutée (plus de nucléaire, moins ' +
            'd’éolien et de solaire arrêtés, moins d’exportations) dépend de la saturation des ' +
            'interconnexions et des prix voisins ; ce site ne sait pas encore le dire.'
        };

  /* ---------- 7. Prix nuls ou négatifs ---------- */
  const nb = sim.heures_prix_nul_ou_negatif_charge;
  const prixBas: Tuile =
    sim.part_prix_nul_ou_negatif === null || sim.part_prix_negatif === null
      ? {
          titre: 'Énergie ajoutée consommée à prix nul ou négatif',
          valeur: '—',
          detail: 'Aucune consommation ajoutée aux heures où le prix est connu.'
        }
      : {
          titre: 'Énergie ajoutée consommée à prix nul ou négatif',
          valeur: part(sim.part_prix_nul_ou_negatif),
          detail:
            `dont ${part(sim.part_prix_negatif)} à prix strictement négatif. Prix day-ahead ` +
            'observés, sans effet en retour : ce n’est pas une facture. Pour une consommation ' +
            'plate, c’est la part des heures de l’année à prix nul ou négatif, quelle que soit la ' +
            'puissance.' +
            (nb
              ? ` Le nucléaire disponible non produit aurait couvert la consommation ajoutée à ` +
                `${part(sim.heures_prix_nul_ou_negatif_j_couvre / nb)} de ces ${heures(nb)}. Avec ` +
                'elle, une partie de ces heures n’aurait plus été à prix nul ou négatif ; le ' +
                'simulateur ne dit pas lesquelles.'
              : '')
        };

  /* ---------- 8. Consommation maximale (avec un froid supplémentaire seulement) ---------- */
  // Les prix avant le nucléaire : la tuile du nucléaire, avec sa seconde valeur, partage ainsi sa
  // rangée avec celle des prix, dont le titre tient sur deux lignes (l'outil tient sur un écran).
  const tuiles = [energie, marge, maxAnnee, maxPluri, prixBas, nucleaire, echanges];
  const cMax = sim.consommation_max_apres;
  const cObs = sim.consommation_max_observee;
  if (froid && cMax && cObs) {
    // Même pas de temps que le scénario : la moyenne horaire de 2012, pas la demi-heure.
    const record = refs.recordHoraire.valeur_mw;
    tuiles.push({
      titre: 'Consommation horaire maximale',
      valeur: gw(cMax.valeur_mw),
      detail:
        `${heureParis(cMax.debut_paris)}, moyenne horaire hors Corse, froid supplémentaire ` +
        `${aucune ? '' : 'et consommation ajoutée '}compris ; ${gw(cObs.valeur_mw)} observés en ` +
        `${etat.annee}. Pointe de février 2012 : ${refs.recordHoraire.texte} en moyenne horaire ` +
        `(${refs.record.texte} à la demi-heure). ` +
        (cMax.valeur_mw > record ? 'Le scénario la dépasse. ' : '') +
        'Ce n’est pas le froid de février 2012 : les degrés réglés s’ajoutent à ceux de jours ' +
        'déjà froids, et RTE estime qu’avec des froids comparables à ceux du début des années ' +
        `2010, les pointes de l’hiver 2026-2027 resteraient « sensiblement inférieures à ` +
        `${refs.pointeFroids2010.texte} » (sauf cas très exceptionnels). Au-delà de quelques ` +
        'degrés, le gradient moyen est en outre prolongé hors de ce que RTE publie.',
      notes: [
        refs.recordHoraire.note,
        refs.record.note,
        refs.pointeFroids2010.note,
        refs.gradient.note
      ]
    });
  }
  return {
    scenario: typographier(scenario),
    tuiles: tuiles.map((u) => ({
      ...u,
      detail: typographier(u.detail),
      ...(u.complement ? { complement: typographier(u.complement) } : {})
    }))
  };
}
