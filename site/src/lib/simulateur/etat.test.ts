import { describe, expect, it } from 'vitest';
import { DEFAUTS, ecrireEtat, lireEtat } from './etat';

const ANNEES = [2015, 2022, 2025];

describe('état du simulateur dans l’adresse', () => {
  it('sans paramètre : les défauts, et une adresse nue', () => {
    expect(lireEtat('', ANNEES)).toEqual({ etat: DEFAUTS, ecarts: [] });
    expect(ecrireEtat(DEFAUTS)).toBe('');
  });

  it('aller-retour', () => {
    const etat = { annee: 2022, xGw: 2.5, effacement: 120, froidC: 0, plancherGw: 1 };
    const q = ecrireEtat(etat);
    expect(q).toBe('?annee=2022&x=2.5&effacement=120');
    expect(lireEtat(q, ANNEES)).toEqual({ etat, ecarts: [] });
    const etat2 = { ...etat, froidC: 4.5, plancherGw: 0 };
    const q2 = ecrireEtat(etat2);
    expect(q2).toBe('?annee=2022&x=2.5&effacement=120&froid=4.5&plancher=0');
    expect(lireEtat(q2, ANNEES)).toEqual({ etat: etat2, ecarts: [] });
    expect(lireEtat(q, ANNEES)).toEqual({ etat, ecarts: [] });
  });

  it('ramène les valeurs hors plage ou illisibles, et le dit', () => {
    const { etat, ecarts } = lireEtat('?annee=2030&x=25&effacement=-3', ANNEES);
    expect(etat).toEqual({ ...DEFAUTS, annee: 2025, xGw: 20, effacement: 0 });
    expect(ecarts).toHaveLength(3);
    expect(lireEtat('?x=abc&effacement=', ANNEES).etat).toEqual(DEFAUTS);
    expect(lireEtat('?x=1.04&effacement=10.6', ANNEES).etat).toEqual({
      ...DEFAUTS,
      annee: 2025,
      xGw: 1,
      effacement: 11
    });
    const r = lireEtat('?froid=15&plancher=-1', ANNEES);
    expect(r.etat).toEqual({ ...DEFAUTS, froidC: 12, plancherGw: 0 });
    expect(r.ecarts).toHaveLength(2);
    expect(lireEtat('?froid=2.3&plancher=1.04', ANNEES).etat).toEqual({
      ...DEFAUTS,
      froidC: 2.5,
      plancherGw: 1
    });
    expect(lireEtat('?froid=abc&plancher=', ANNEES).etat).toEqual(DEFAUTS);
  });

  it('une ancienne adresse (sans froid ni plancher) redonne le même scénario, défauts compris', () => {
    expect(lireEtat('?annee=2022&x=5&effacement=100', ANNEES)).toEqual({
      etat: { ...DEFAUTS, annee: 2022, xGw: 5, effacement: 100 },
      ecarts: []
    });
  });

  it('arrondit le pas de 0,1 GW sans bruit flottant', () => {
    expect(ecrireEtat({ ...DEFAUTS, xGw: 0.1 + 0.2 })).toBe('?x=0.3');
  });
});
