import { describe, expect, it } from 'vitest';
import { chargerChiffres } from '$lib/server/chiffres';
import { estimations2024, idsPyramide, pyramide, trajectoires } from './donnees';
import { placerEtiquettes } from './etiquettes';

const chiffres = chargerChiffres();

describe('données des graphiques', () => {
  it('construit les estimations 2024 depuis le référentiel, intervalles compris', () => {
    const e = estimations2024(chiffres);
    expect(e).toHaveLength(5);
    expect(e.filter((x) => x.intervalle).map((x) => x.id)).toEqual([
      'dc_conso_sites_dedies_2024',
      'dc_conso_avec_internes_2024'
    ]);
  });
  it('n’inclut dans la pyramide ni la pointe de cohorte ni la puissance mise à disposition', () => {
    const ids = idsPyramide();
    expect(ids).not.toContain('dc_pointe_cohorte_2022_2024');
    expect(ids).not.toContain('dc_mis_a_disposition_2022_2025');
    const etages = pyramide(chiffres);
    expect(etages.map((e) => e.cle)).toEqual([
      'recherchee',
      'reservee',
      'prereservee',
      'signee',
      'raccordee',
      'appelee'
    ]);
    expect(etages[1].points).toHaveLength(3);
    for (const e of etages) for (const p of e.points) expect(p.date).not.toBe('');
  });
  it('convertit les GW en MW pour l’échelle commune', () => {
    const p = pyramide(chiffres).flatMap((e) => e.points);
    expect(p.find((x) => x.id === 'dc_recherche_2026_01')!.mw).toBeCloseTo(28600);
    expect(p.find((x) => x.id === 'dc_raccorde_rpt_2025_12')!.mw).toBe(770);
  });
  it('lit les trajectoires par année', () => {
    const t = trajectoires(chiffres);
    expect(t.depart.annee).toBe(2024);
    expect(t.rapide.map((p) => p.annee)).toEqual([2030, 2035]);
    expect(t.bp2023.every((p) => p.max > p.min)).toBe(true);
  });
  it('échoue sur un identifiant absent', () => {
    const { dc_conso_rpt_2024: _, ...amputes } = chiffres;
    expect(() => estimations2024(amputes)).toThrow(/dc_conso_rpt_2024/);
  });
});

describe('placement des étiquettes', () => {
  it('passe au-dessus, puis à une voie plus éloignée, plutôt que de chevaucher', () => {
    const p = placerEtiquettes(
      [
        { x: 10, largeur: 100 },
        { x: 50, largeur: 100 },
        { x: 300, largeur: 50 }
      ],
      400
    );
    expect(p.map((e) => e.voie)).toEqual([0, -1, 0]);
  });
  it('place les étiquettes réelles de la pyramide sans renvoi, sous ou au-dessus des points', () => {
    for (const e of pyramide(chiffres)) {
      const p = placerEtiquettes(
        e.points.map((pt) => ({ x: (Math.log10(pt.mw) - 1.8) * 300, largeur: 150 })),
        900
      );
      for (const pl of p) expect([0, -1]).toContain(pl.voie);
    }
  });
  it('aligne à droite une étiquette qui déborderait', () => {
    const [e] = placerEtiquettes([{ x: 390, largeur: 100 }], 400);
    expect(e.ancre).toBe('end');
  });
});
