// Phrases des résultats et textes de la page : propriétés exigées par la relecture du simulateur
// (docs/relectures/2026-11-26-simulateur.md).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { lireCsvHoraire } from './csv';
import { DEFAUTS, type Etat } from './etat';
import { simuler } from './moteur';
import { phrases } from './phrases';
import type { ChiffreCite, References } from './references';

const RACINE = resolve(process.cwd(), '..');
const lire = (chemin: string) => readFileSync(resolve(RACINE, chemin), 'utf8');
const quand = JSON.parse(lire('data/export/quand.json'));
const table = lireCsvHoraire(lire('data/export/horaire/2025.csv'));

const cite = (texte: string): ChiffreCite => ({ id: 'x', texte, confiance: 'C', note: '<p></p>' });
const REFS: References = {
  maxPluriannuel: quand.rn_max_pluriannuel,
  marge: cite('8 à 10 GW'),
  productionPubliee: { 2025: cite('373 TWh') },
  productionPrevue: cite('350 à 370 TWh'),
  gradient: { ...cite('2 400 MW/°C'), mw_par_c: 2400 },
  record: { ...cite('102 GW'), valeur_mw: 102100 },
  recordHoraire: { ...cite('100,6 GW'), valeur_mw: 100600 },
  pointeFroids2010: { ...cite('100 GW'), valeur_mw: 100000 },
  froidPointe: { ...cite('5,5 °C'), annee: 2025 },
  jHeuresCheres: { ...cite('0,5 GW'), annee: 2025 },
  jHeuresCheresMax: { ...cite('2,0 GW'), annee: 2020, heures: 2 }
};
const OPTIONS = { maxReglable: 500, derniereAnnee: 2025 };
const reference = REFS.maxPluriannuel.valeur_mw;

function texte(etat: Etat) {
  const x = Math.round(etat.xGw * 1000);
  const p = Math.round(etat.plancherGw * 1000);
  const g = REFS.gradient.mw_par_c;
  const sim = simuler(
    table,
    x,
    etat.effacement,
    undefined,
    undefined,
    p,
    reference,
    etat.froidC,
    g
  );
  const plate = simuler(table, x, 0, undefined, undefined, p, reference, etat.froidC, g);
  const seul = etat.froidC
    ? simuler(table, 0, 0, undefined, undefined, p, reference, etat.froidC, g)
    : null;
  const ph = phrases(etat, sim, plate, REFS, OPTIONS, seul);
  return {
    ph,
    sim,
    tout: [
      ph.scenario,
      ...ph.tuiles.flatMap((t) => [t.titre, t.qualif ?? '', t.valeur, t.detail])
    ].join(' ')
  };
}

/** Causalité attribuée aux exportations (relecture, SF1) : ne doit revenir nulle part. */
const EXPORTS_CAUSAL =
  /(servie?s?|couverte?s?)[^.]{0,40}(par|de) moins d.exportations|d.abord servie/i;

const SCENARIOS: Etat[] = [
  DEFAUTS,
  { ...DEFAUTS, xGw: 5 },
  { ...DEFAUTS, xGw: 5, effacement: 1 },
  { ...DEFAUTS, xGw: 10, effacement: 100 },
  { ...DEFAUTS, xGw: 20, effacement: 500 },
  { ...DEFAUTS, xGw: 0 },
  { ...DEFAUTS, xGw: 0, effacement: 50 },
  { ...DEFAUTS, froidC: 3 },
  { ...DEFAUTS, xGw: 5, effacement: 100, froidC: 8 },
  { ...DEFAUTS, xGw: 0, froidC: 12 },
  { ...DEFAUTS, xGw: 5, plancherGw: 0 },
  { ...DEFAUTS, xGw: 5, plancherGw: 3 }
];

describe('phrases des résultats', () => {
  it.each(SCENARIOS.map((e) => [JSON.stringify(e), e] as const))('%s : forme', (_, etat) => {
    const { tout } = texte(etat);
    expect(tout).not.toMatch(EXPORTS_CAUSAL);
    expect(tout).not.toMatch(/prix moyen pondéré|€\/MWh/);
    expect(tout).not.toMatch(/les 1\s/);
    expect(tout).not.toMatch(/1\s(heure|heures) effacées/);
    // Aucune phrase collée à la suivante, aucune espace avant une virgule.
    expect(tout).not.toMatch(/[a-zé)][.;][A-ZÀ-Ý]/);
    expect(tout).not.toMatch(/ ,/);
  });

  it('X > 0 : « au plus », fourchette avec plancher ≤ sans plancher, deux maxima, marge', () => {
    const { ph, sim, tout } = texte({ ...DEFAUTS, xGw: 5 });
    expect(sim.part_dans_j_plancher as number).toBeLessThanOrEqual(sim.part_dans_j as number);
    const j = ph.tuiles.find((t) => t.titre.startsWith('Dans le nucléaire'))!;
    expect(j.qualif).toBe('au plus');
    expect(j.valeur).toMatch(/^\d+ à \d+\s%$/);
    expect(tout).toContain('sans effet en retour');
    expect(tout).toContain('n’est pas une défaillance');
    expect(tout).toContain('au moins 1 dès que X est positif');
    expect(ph.tuiles.map((t) => t.titre)).toEqual(
      expect.arrayContaining([
        'Heures au-delà du maximum de 2025',
        `Heures au-delà du maximum ${REFS.maxPluriannuel.annees}`,
        'Marge de sécurité d’approvisionnement'
      ])
    );
    expect(tout).toContain('à peu près 5 GW');
    expect(tout).toContain('350 à 370 TWh');
  });

  it('nucléaire non produit : « au plus » avec la disponibilité déclarée, seconde valeur réintégrée', () => {
    const { ph, sim, tout } = texte({ ...DEFAUTS, xGw: 5 });
    const j = ph.tuiles.find((t) => t.titre.startsWith('Dans le nucléaire'))!;
    const r = sim.reintegre!;
    expect(r.part_dans_j as number).toBeGreaterThan(sim.part_dans_j as number);
    expect(r.part_dans_j_plancher as number).toBeGreaterThan(sim.part_dans_j_plancher as number);
    expect(j.complement).toMatch(
      /^disponibilité déclarée par EDF\s; \d+ à \d+\s% en réintégrant ses arrêts courts pour modulation$/
    );
    expect(j.detail).toContain('avec la disponibilité déclarée par EDF');
    expect(j.detail).toMatch(/«\spour modulation\s»/);
    expect(j.detail).toMatch(/En réintégrant les arrêts courts, ce serait \d+ à \d+\s%/);
    expect(j.detail).toContain('Les plus longs peuvent relever de la gestion du combustible');
    expect(j.detail).toContain('en énergie, la limite est plus nette');
    expect(tout).not.toMatch(/plafond physique|capacité physique disponible/);
    // la tuile du nucléaire suit celle des prix et précède « Heures où ce nucléaire suffirait »
    const titres = ph.tuiles.map((t) => t.titre);
    expect(titres.indexOf('Heures où ce nucléaire suffirait')).toBe(titres.indexOf(j.titre) + 1);
  });

  it('nucléaire non produit : année sans arrêt pour modulation déclaré, et CSV sans la colonne', () => {
    const t2017 = lireCsvHoraire(lire('data/export/horaire/2017.csv'));
    const etat = { ...DEFAUTS, annee: 2017, xGw: 5 };
    const s2017 = simuler(t2017, 5000, 0, undefined, undefined, 1000, reference);
    const j2017 = phrases(etat, s2017, s2017, REFS, OPTIONS).tuiles.find((t) =>
      t.titre.startsWith('Dans le nucléaire')
    )!;
    expect(j2017.complement).toMatch(
      /^disponibilité déclarée par EDF\s; même valeur en réintégrant ses arrêts courts pour modulation$/
    );
    expect(j2017.detail).toContain(
      'En 2017, réintégrer les arrêts courts ne change pas ces parts.'
    );
    const sansColonne = { ...table };
    delete sansColonne.nucleaire_disponible_reintegre;
    const s = simuler(sansColonne, 5000, 0, undefined, undefined, 1000, reference);
    expect(s.reintegre).toBeNull();
    const j = phrases({ ...DEFAUTS, xGw: 5 }, s, s, REFS, OPTIONS).tuiles.find((t) =>
      t.titre.startsWith('Dans le nucléaire')
    )!;
    expect(j.complement).toBe('avec la disponibilité déclarée par EDF');
    expect(j.valeur).toBe(
      phrases(
        { ...DEFAUTS, xGw: 5 },
        simuler(table, 5000),
        simuler(table, 5000),
        REFS,
        OPTIONS
      ).tuiles.find((t) => t.titre.startsWith('Dans le nucléaire'))!.valeur
    );
  });

  it('effacement : borne basse, énergie perdue, marge non calculable', () => {
    const { tout } = texte({ ...DEFAUTS, xGw: 5, effacement: 1 });
    expect(tout).toContain('borne basse');
    expect(tout).toMatch(/est perdue/);
    expect(tout).toContain('non calculable ici');
    expect(tout).toMatch(/sauf pendant l’heure de charge/);
    const { tout: suffisant } = texte({ ...DEFAUTS, xGw: 5, effacement: 100 });
    expect(suffisant).toContain('Par construction, les heures effacées sont celles que compte');
  });

  it('par défaut : sept tuiles, pas de froid, plancher de 1 GW', () => {
    const { ph, sim, tout } = texte(DEFAUTS);
    expect(ph.tuiles).toHaveLength(7);
    expect(sim.froid_heures).toBe(0);
    expect(sim.plancher_mw).toBe(1000);
    expect(tout).not.toContain('Froid');
  });

  it('froid : épisode daté, pas un écart aux normales, record, heures dues au froid seul', () => {
    const { ph, sim, tout } = texte({ ...DEFAUTS, xGw: 5, effacement: 100, froidC: 8 });
    expect(sim.froid_ajout_mw).toBe(19200);
    expect(ph.scenario).toMatch(
      /Froid supplémentaire de 8\s°C pendant les 7\sjours les plus tendus, du 13 au 20\sjanv\.\s2025\s:/
    );
    expect(ph.scenario).toMatch(/19,2\sGW/);
    expect(ph.scenario).toContain('froid compris');
    const c = ph.tuiles.find((t) => t.titre === 'Consommation horaire maximale')!;
    // Repère en consommation (RTE, hiver 2026-2027), pas en degrés sous les normales (relecture, F1).
    expect(c.detail).not.toMatch(/sous les normales/);
    expect(c.detail).toContain('Ce n’est pas le froid de février 2012');
    expect(c.detail).toMatch(/«\ssensiblement inférieures à 100 GW\s»/);
    expect(c.detail).toContain('Le scénario la dépasse.');
    expect(c.detail).toContain(`${REFS.recordHoraire.texte} en moyenne horaire`);
    expect(c.notes).toHaveLength(4);
    // L'heure du maximum de 2025 est dans l'épisode : elle se dépasse elle-même (relecture, f2).
    expect(tout).toContain('l’heure du maximum, dans l’épisode, se dépasse elle-même');
    // La part du froid dans J n'est pas comptée dans la production en plus affichée (relecture, f5).
    expect(ph.tuiles.find((t) => t.titre.startsWith('Dans le nucléaire'))!.detail).toContain(
      'celle que le froid prend d’abord s’y ajouterait'
    );
    // 2025 : 8 °C × 2,4 GW sur la semaine la plus tendue dépasse le maximum observé à elle seule.
    expect(tout).toContain('à lui seul');
    expect(tout).not.toMatch(/il faudrait effacer au moins/);
    const faible = texte({ ...DEFAUTS, xGw: 5, froidC: 0.5 });
    expect(
      faible.ph.tuiles.find((t) => t.titre === 'Consommation horaire maximale')!.detail
    ).not.toContain('Le scénario la dépasse.');
    const seul = texte({ ...DEFAUTS, xGw: 0, froidC: 12 });
    expect(seul.tout).not.toContain('borne basse');
    expect(
      seul.ph.tuiles.find((t) => t.titre.startsWith('Heures au-delà du maximum de'))!.valeur
    ).not.toBe('0 heure');
  });

  it('plancher réglable : nul → une seule valeur, plus haut → part plus basse', () => {
    const nul = texte({ ...DEFAUTS, xGw: 5, plancherGw: 0 });
    const j0 = nul.ph.tuiles.find((t) => t.titre.startsWith('Dans le nucléaire'))!;
    expect(j0.valeur).toMatch(/^\d+\s%$/);
    expect(j0.detail).toContain('réglé à 0');
    const haut = texte({ ...DEFAUTS, xGw: 5, plancherGw: 3 });
    expect(haut.sim.part_dans_j_plancher as number).toBeLessThan(
      texte({ ...DEFAUTS, xGw: 5 }).sim.part_dans_j_plancher as number
    );
    expect(haut.ph.tuiles.find((t) => t.titre.startsWith('Dans le nucléaire'))!.detail).toMatch(
      /3,0\sGW/
    );
  });

  it('X nul : ni part, ni défaillance, ni effacement annoncé', () => {
    for (const effacement of [0, 50]) {
      const { ph, tout } = texte({ ...DEFAUTS, xGw: 0, effacement });
      expect(tout).not.toContain('défaillance');
      expect(tout).not.toContain('borne basse');
      expect(ph.scenario).not.toContain('sauf');
      for (const t of ph.tuiles.filter((t) => !t.titre.startsWith('Heures au-delà')))
        expect(['—', '0,00 TWh']).toContain(t.valeur);
      if (effacement) expect(ph.scenario).toContain('sans objet');
    }
  });
});

describe('textes de la page', () => {
  it('aucune causalité attribuée aux exportations', () => {
    for (const f of ['en-tete.md', 'lecture.md']) {
      const t = lire(`site/src/lib/simulateur/${f}`).replace(/\s+/g, ' ');
      expect(t, f).not.toMatch(EXPORTS_CAUSAL);
    }
  });
});
