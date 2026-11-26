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
  productionPrevue: cite('350 à 370 TWh')
};
const OPTIONS = { maxReglable: 500, derniereAnnee: 2025 };
const reference = REFS.maxPluriannuel.valeur_mw;

function texte(etat: Etat) {
  const x = Math.round(etat.xGw * 1000);
  const sim = simuler(table, x, etat.effacement, undefined, undefined, undefined, reference);
  const plate = simuler(table, x, 0, undefined, undefined, undefined, reference);
  const ph = phrases(etat, sim, plate, REFS, OPTIONS);
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
  { ...DEFAUTS, xGw: 0, effacement: 50 }
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

  it('effacement : borne basse, énergie perdue, marge non calculable', () => {
    const { tout } = texte({ ...DEFAUTS, xGw: 5, effacement: 1 });
    expect(tout).toContain('borne basse');
    expect(tout).toMatch(/est perdue/);
    expect(tout).toContain('non calculable ici');
    expect(tout).toMatch(/sauf pendant l’heure de charge/);
    const { tout: suffisant } = texte({ ...DEFAUTS, xGw: 5, effacement: 100 });
    expect(suffisant).toContain('Par construction, les heures effacées sont celles que compte');
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
