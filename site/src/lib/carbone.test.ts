import { describe, expect, it } from 'vitest';
import { FINE } from './format';
import {
  JETONS_CO2,
  SEUILS_CO2,
  classeCo2,
  grammes,
  libelleClasseCo2,
  sourcesCarbone,
  type DonneesCarbone
} from './carbone';

describe('formats et classes de « Quel carbone ? »', () => {
  it('affiche les grammes à une décimale, toujours', () => {
    expect(grammes(18.359)).toBe(`18,4${FINE}g`);
    expect(grammes(20, false)).toBe('20,0');
  });
  it('classe les intensités, bornes basses incluses', () => {
    expect(JETONS_CO2.length).toBe(SEUILS_CO2.length + 1);
    expect([0, 9.99, 10, 19.9, 20, 40, 59.9, 60, 154].map(classeCo2)).toEqual([
      0, 0, 1, 1, 2, 3, 3, 4, 4
    ]);
    expect(libelleClasseCo2(0)).toBe('moins de 10');
    expect(libelleClasseCo2(2)).toBe('20 à 40');
    expect(libelleClasseCo2(4)).toBe('60 et plus');
  });
  it('date les extractions dans la ligne des sources', () => {
    const d: DonneesCarbone = {
      annees: [],
      matrices: [],
      sources: 'éCO2mix national (RTE)',
      extractions: {
        eco2mix: '2026-11-25T23:21:04+00:00',
        odre_ges_conso: '2026-11-25T23:21:13+00:00'
      }
    };
    const s = sourcesCarbone(d);
    expect(s).toContain('data/export/carbone.json');
    expect(s).toContain('éCO2mix le 26 novembre 2026');
    expect(s).toContain('intensité de la consommation (ODRÉ) le 26');
  });
});
