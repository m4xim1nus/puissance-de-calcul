// Données des graphiques de l'enquête « Combien ? ». Aucune valeur ici : seulement des identifiants
// du référentiel (data/export/chiffres.json) et des libellés courts. Un identifiant absent, une
// unité ou une période inattendue lèvent une erreur au prérendu.
import { chiffre, enMW, type Chiffre, type Chiffres, type Source } from '$lib/chiffres';
import { formaterPeriode, formaterValeur } from '$lib/format';

/** Une ligne du tableau de données repliable d'un graphique. */
export interface LigneDonnees {
  id: string;
  libelle: string;
  valeur: string;
  periode: string;
  perimetre: string;
  source: Source;
  page: string;
  confiance: Chiffre['confiance'];
  calcul: boolean;
}

export function ligneDonnees(chiffres: Chiffres, id: string, libelle?: string): LigneDonnees {
  const c = chiffre(chiffres, id);
  return {
    id,
    libelle: libelle ?? c.libelle,
    valeur: formaterValeur(c.valeur, c.unite),
    periode: formaterPeriode(c.periode),
    perimetre: c.perimetre,
    source: c.source,
    page: c.page,
    confiance: c.confiance,
    calcul: Boolean(c.calcul)
  };
}

/** Les sources d'un graphique, une fois chacune, avec leurs pages : « RTE, Titre (p. 18, p. 27) ». */
export function sourcesGraphique(chiffres: Chiffres, ids: string[]): string {
  const parCle = new Map<string, { s: Source; pages: string[] }>();
  for (const id of ids) {
    const c = chiffre(chiffres, id);
    const e = parCle.get(c.source.cle) ?? { s: c.source, pages: [] };
    // « communiqué », « page web » : déjà dit par le titre, on ne le répète pas.
    const redondante = c.source.titre.toLowerCase().includes(c.page.toLowerCase());
    if (!redondante && !e.pages.includes(c.page)) e.pages.push(c.page);
    parCle.set(c.source.cle, e);
  }
  return [...parCle.values()]
    .map(
      ({ s, pages }) => `${s.editeur}, ${s.titre}${pages.length ? ` (${pages.join(' ; ')})` : ''}`
    )
    .join(' · ');
}

function exiger(c: Chiffre, unite: string, id: string): Chiffre {
  if (c.unite !== unite) throw new Error(`« ${id} » : unité ${c.unite}, ${unite} attendu`);
  return c;
}

const bornes = (v: Chiffre['valeur']): [number, number] => (Array.isArray(v) ? v : [v, v]);

/* ---------- Estimations 2024 ---------- */

export const ESTIMATIONS_2024 = [
  { id: 'dc_conso_rpt_2024', libelle: 'Sites dédiés raccordés au réseau de transport (RTE)' },
  { id: 'dc_conso_rpd_2024', libelle: 'Sites dédiés raccordés au réseau d’Enedis' },
  { id: 'dc_conso_sdes_2024', libelle: 'Points de livraison de plus de 1 GWh par an (SDES)' },
  { id: 'dc_conso_sites_dedies_2024', libelle: 'Ensemble des sites dédiés (RTE)' },
  { id: 'dc_conso_avec_internes_2024', libelle: 'Sites dédiés et centres internes (RTE)' }
] as const;

export interface Estimation {
  id: string;
  libelle: string;
  min: number;
  max: number;
  intervalle: boolean;
  texte: string;
}

export function estimations2024(chiffres: Chiffres): Estimation[] {
  return ESTIMATIONS_2024.map(({ id, libelle }) => {
    const c = exiger(chiffre(chiffres, id), 'TWh', id);
    if (c.periode !== '2024') throw new Error(`« ${id} » : période ${c.periode}, 2024 attendu`);
    const [min, max] = bornes(c.valeur);
    return {
      id,
      libelle,
      min,
      max,
      intervalle: min !== max,
      texte: formaterValeur(c.valeur, c.unite, true)
    };
  });
}

/* ---------- Pyramide des puissances ---------- */

interface PointSpec {
  id: string;
  /** Précision courte affichée avec la valeur (réseau, palier…). */
  precision?: string;
}

export const ETAGES_PYRAMIDE: { cle: string; nom: string; nature: string; points: PointSpec[] }[] =
  [
    {
      cle: 'recherchee',
      nom: 'Recherchée',
      nature:
        'annoncée par l’État pour les porteurs de projets qu’il accompagne ; définition non publiée',
      points: [{ id: 'dc_recherche_2026_01' }]
    },
    {
      cle: 'reservee',
      nom: 'Réservée',
      nature: 'droit d’accès au réseau de transport (PTF signée) ; n’engage pas à consommer',
      points: [
        { id: 'dc_reserve_rte_2024_12' },
        { id: 'dc_reserve_rte_2025_11' },
        { id: 'dc_reserve_rte_2026_05' }
      ]
    },
    {
      cle: 'prereservee',
      nom: 'Pré-réservée (fast-track)',
      nature: 'capacité pré-réservée par RTE à la demande de l’État, sur cinq sites',
      points: [{ id: 'dc_fasttrack_prereserve_2025_12' }]
    },
    {
      cle: 'signee',
      nom: 'Signée',
      nature:
        'contrat de raccordement du Campus IA à Fouju : paliers de puissance mise à disposition',
      points: [
        { id: 'dc_signe_fouju_2027', precision: 'premier palier' },
        { id: 'dc_signe_fouju_terme' }
      ]
    },
    {
      cle: 'raccordee',
      nom: 'Raccordée',
      nature:
        'puissance de raccordement des data centers en service (côté Enedis, nature de la puissance non précisée)',
      points: [
        { id: 'dc_raccorde_rpt_2025_12', precision: 'transport' },
        { id: 'dc_raccorde_rpd_2025', precision: 'Enedis' }
      ]
    },
    {
      cle: 'appelee',
      nom: 'Appelée',
      nature: 'puissance moyenne réellement soutirée sur l’année (énergie ÷ heures)',
      points: [{ id: 'dc_appele_moyen_rpt_2025', precision: 'transport' }]
    }
  ];

const GRANDEURS_PUISSANCE = new Set([
  'puissance_recherchee',
  'puissance_reservee',
  'puissance_signee',
  'puissance_raccordee',
  'puissance_appelee_moyenne'
]);

export interface PointPyramide {
  id: string;
  mw: number;
  valeur: string;
  date: string;
  precision?: string;
  calcul: boolean;
  libelle: string;
}

export interface EtagePyramide {
  cle: string;
  nom: string;
  nature: string;
  points: PointPyramide[];
}

export function pyramide(chiffres: Chiffres): EtagePyramide[] {
  return ETAGES_PYRAMIDE.map((e) => ({
    cle: e.cle,
    nom: e.nom,
    nature: e.nature,
    points: e.points.map(({ id, precision }) => {
      const c = chiffre(chiffres, id);
      if (!GRANDEURS_PUISSANCE.has(c.grandeur))
        throw new Error(`« ${id} » : grandeur ${c.grandeur}, pas une puissance de la pyramide`);
      return {
        id,
        mw: enMW(c),
        valeur: formaterValeur(c.valeur, c.unite, true),
        date: formaterPeriode(c.periode, true),
        precision,
        calcul: Boolean(c.calcul),
        libelle: c.libelle
      };
    })
  }));
}

export const idsPyramide = () => ETAGES_PYRAMIDE.flatMap((e) => e.points.map((p) => p.id));

/* ---------- Trajectoires ---------- */

export const TRAJECTOIRES = {
  depart: 'dc_conso_sites_dedies_2024',
  lente: ['traj_bp2025_lente_2030', 'traj_bp2025_lente_2035'],
  rapide: ['traj_bp2025_rapide_2030', 'traj_bp2025_rapide_2035'],
  bp2023: ['traj_bp2023_2030', 'traj_bp2023_2035'],
  ademe: ['traj_ademe_tendanciel_2035']
} as const;

export interface PointTrajectoire {
  id: string;
  annee: number;
  min: number;
  max: number;
  texte: string;
}

function pointTrajectoire(chiffres: Chiffres, id: string): PointTrajectoire {
  const c = exiger(chiffre(chiffres, id), 'TWh', id);
  if (!/^\d{4}$/.test(c.periode))
    throw new Error(`« ${id} » : période ${c.periode}, année attendue`);
  const [min, max] = bornes(c.valeur);
  return { id, annee: Number(c.periode), min, max, texte: formaterValeur(c.valeur, c.unite, true) };
}

export function trajectoires(chiffres: Chiffres) {
  const p = (ids: readonly string[]) => ids.map((id) => pointTrajectoire(chiffres, id));
  return {
    depart: pointTrajectoire(chiffres, TRAJECTOIRES.depart),
    lente: p(TRAJECTOIRES.lente),
    rapide: p(TRAJECTOIRES.rapide),
    bp2023: p(TRAJECTOIRES.bp2023),
    ademe: p(TRAJECTOIRES.ademe)
  };
}

export const idsTrajectoires = (): string[] => [
  TRAJECTOIRES.depart,
  ...TRAJECTOIRES.lente,
  ...TRAJECTOIRES.rapide,
  ...TRAJECTOIRES.bp2023,
  ...TRAJECTOIRES.ademe
];
