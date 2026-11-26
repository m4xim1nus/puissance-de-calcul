import { describe, expect, it } from 'vitest';
import { decimalesDe, FINE, formaterFixe, formaterValeur } from './format';
import {
  classeRn,
  ecarter,
  gw,
  heureParis,
  libelleClasseRn,
  pourcent,
  SEUILS_RN,
  JETONS_RN,
  sourcesRn,
  statsMensuelles,
  type DonneesQuand
} from './quand';

describe('formats de « Quand ? »', () => {
  it('affiche les GW à une décimale, toujours', () => {
    expect(gw(8000)).toBe(`8,0${FINE}GW`);
    expect(gw(-3184)).toBe(`−3,2${FINE}GW`);
    expect(gw(31433, false)).toBe('31,4');
    expect(pourcent(0.5217)).toBe(`52${FINE}%`);
  });
  it('déduit les décimales d’un pas d’arrondi et les impose', () => {
    expect([decimalesDe(0.1), decimalesDe(1), decimalesDe(0.01)]).toEqual([1, 0, 2]);
    expect(formaterFixe(8, 1)).toBe('8,0');
    expect(formaterFixe(1400, 0)).toBe(`1${FINE}400`);
    expect(formaterValeur(8, 'GW', true, 0.1)).toBe(`8,0${FINE}GW`);
    expect(formaterValeur(-3.2, 'GW', true, 0.1)).toBe(`−3,2${FINE}GW`);
    // Sans précision, l'arrondi générique est inchangé.
    expect(formaterValeur(8, 'GW', true)).toBe(`8${FINE}GW`);
  });
  it('dit l’heure de Paris de début', () => {
    expect(heureParis('2025-01-14T08:00+01:00')).toBe('14 janv. 2025, 8 h');
    expect(heureParis('2025-09-01T07:00+02:00')).toBe('1er sept. 2025, 7 h');
  });
});

describe('échelle de la charge résiduelle', () => {
  it('a 4 classes de chaque côté de zéro, chaque borne basse incluse dans sa classe', () => {
    expect(JETONS_RN).toHaveLength(SEUILS_RN.length + 1);
    expect(
      [-25000, -20000, -10001, -5000, -1, 0, 4999, 5000, 19999, 20000, 38000].map(classeRn)
    ).toEqual([0, 1, 1, 3, 3, 4, 4, 5, 6, 7, 7]);
    expect(libelleClasseRn(0)).toBe(`moins de −20${FINE}GW`);
    expect(libelleClasseRn(4)).toBe(`0 à 5${FINE}GW`);
    expect(libelleClasseRn(7)).toBe(`20${FINE}GW et plus`);
  });
});

describe('statistiques mensuelles', () => {
  it('ignore les heures absentes et compte les heures positives', () => {
    const s = statsMensuelles({
      annee: 2025,
      jours: ['2025-01-01', '2025-01-02', '2025-02-01'],
      valeurs: [
        [1000, -1000, null, ...Array(21).fill(0)],
        [3000, ...Array(23).fill(0)],
        [500, ...Array(23).fill(null)]
      ]
    });
    expect(s[0]).toEqual({
      mois: 0,
      moyenneMw: 3000 / 47,
      maxMw: 3000,
      minMw: -1000,
      heuresPositives: 2,
      heures: 47
    });
    expect(s[1].heures).toBe(1);
    expect(s[2].heures).toBe(0);
    expect(Number.isNaN(s[2].moyenneMw)).toBe(true);
  });
});

describe('mise en page', () => {
  it('écarte les étiquettes sans sortir du cadre', () => {
    const r = ecarter(
      [
        { k: 'a', y: 100 },
        { k: 'b', y: 102 },
        { k: 'c', y: 195 }
      ],
      14,
      0,
      200
    );
    expect(r.map((e) => [e.k, e.y])).toEqual([
      ['a', 100],
      ['b', 114],
      ['c', 195]
    ]);
    const bas = ecarter([{ y: 199 }, { y: 200 }], 14, 0, 200);
    expect(bas.map((e) => e.y)).toEqual([186, 200]);
  });
  it('cite les séries de la charge résiduelle, sans les prix', () => {
    const q = {
      sources: 'éCO2mix national (RTE) ; REMIT (EDF) ; prix day-ahead France (energy-charts)',
      extractions: { eco2mix: '2026-11-25T23:21:04+00:00', prix: '2026-11-25T23:21:07+00:00' }
    } as unknown as DonneesQuand;
    const s = sourcesRn(q);
    expect(s).toContain('éCO2mix national (RTE) ; REMIT (EDF)');
    expect(s).not.toMatch(/prix|energy-charts/);
    // 23:21 UTC le 25 novembre = 00:21 à Paris le 26 : la date affichée est celle de Paris.
    expect(s).toContain('éCO2mix le 26\u00a0novembre\u00a02026');
  });
});
