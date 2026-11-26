import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { lireCsvHoraire } from './csv';
import { DEFAUTS } from './etat';
import { simuler } from './moteur';
import { phrases } from './phrases';

const table = lireCsvHoraire(
  readFileSync(resolve(process.cwd(), '../data/export/horaire/2025.csv'), 'utf8')
);

describe('phrases des résultats', () => {
  it('disent « au plus », « observé », « pas une défaillance », sans espace manquante', () => {
    const etat = { ...DEFAUTS, xGw: 5, effacement: 2 };
    const sim = simuler(table, 5000, 2);
    const { scenario, tuiles } = phrases(etat, sim, simuler(table, 5000), 500);
    const tout = [scenario, ...tuiles.flatMap((t) => [t.qualif ?? '', t.valeur, t.detail])].join(
      ' '
    );
    expect(tuiles[1].qualif).toBe('au plus');
    expect(tout).toContain('sans effet en retour');
    expect(tout).toContain('Ce n’est pas une défaillance.');
    expect(tout).toMatch(/il faudrait effacer au moins/);
    // Aucune phrase collée à la suivante (« année.Aux »), aucune espace avant une virgule.
    expect(tout).not.toMatch(/[a-zé)][.;][A-ZÀ-Ý]/);
    expect(tout).not.toMatch(/ ,/);
  });

  it('X nul : pas de part, pas de prix pondéré, pas d’effacement annoncé', () => {
    const etat = { ...DEFAUTS, xGw: 0, effacement: 10 };
    const sim = simuler(table, 0, 10);
    const { scenario, tuiles } = phrases(etat, sim, simuler(table, 0), 500);
    expect(scenario).not.toContain('sauf');
    expect(tuiles[1].valeur).toBe('—');
    expect(tuiles[4].valeur).toBe('—');
    expect(tuiles[2].valeur).toBe('0\u00a0heure');
  });
});
