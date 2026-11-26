import { describe, expect, it } from 'vitest';
import { DEFAUTS, ecrireEtat, lireEtat } from './etat';

const ANNEES = [2015, 2022, 2025];

describe('état du simulateur dans l’adresse', () => {
  it('sans paramètre : les défauts, et une adresse nue', () => {
    expect(lireEtat('', ANNEES)).toEqual({ etat: DEFAUTS, ecarts: [] });
    expect(ecrireEtat(DEFAUTS)).toBe('');
  });

  it('aller-retour', () => {
    const etat = { annee: 2022, xGw: 2.5, effacement: 120 };
    const q = ecrireEtat(etat);
    expect(q).toBe('?annee=2022&x=2.5&effacement=120');
    expect(lireEtat(q, ANNEES)).toEqual({ etat, ecarts: [] });
  });

  it('ramène les valeurs hors plage ou illisibles, et le dit', () => {
    const { etat, ecarts } = lireEtat('?annee=2030&x=25&effacement=-3', ANNEES);
    expect(etat).toEqual({ annee: 2025, xGw: 20, effacement: 0 });
    expect(ecarts).toHaveLength(3);
    expect(lireEtat('?x=abc&effacement=', ANNEES).etat).toEqual(DEFAUTS);
    expect(lireEtat('?x=1.04&effacement=10.6', ANNEES).etat).toEqual({
      annee: 2025,
      xGw: 1,
      effacement: 11
    });
  });

  it('arrondit le pas de 0,1 GW sans bruit flottant', () => {
    expect(ecrireEtat({ ...DEFAUTS, xGw: 0.1 + 0.2 })).toBe('?x=0.3');
  });
});
