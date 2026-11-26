import { describe, expect, it } from 'vitest';
import { ANNEES_COMPAREES } from '$lib/quand';
import { chargerChiffres } from './chiffres';
import { chargerQuand, lireQuand } from './quand';

describe('données de « Quand ? » (data/export/quand.json du dépôt)', () => {
  const q = chargerQuand();
  it('contient les années comparées, leurs monotones et leurs charges plates', () => {
    for (const a of ANNEES_COMPAREES) {
      const d = q.annees.find((x) => x.annee === a);
      expect(d, String(a)).toBeDefined();
      expect(d!.monotone[0][0]).toBe(1);
      expect(d!.monotone[0][1]).toBe(d!.maxMw);
      expect(d!.monotone.at(-1)![0]).toBe(d!.heuresValides);
      // Monotone : décroissante.
      expect(d!.monotone.every((p, i, t) => i === 0 || p[1] <= t[i - 1][1])).toBe(true);
      expect(d!.chargesPlates.map((c) => c.xMw)).toEqual(
        q.annees[0].chargesPlates.map((c) => c.xMw)
      );
    }
  });
  it('a des matrices jour × 24 h pour 2022 et 2025', () => {
    expect(q.matrices.map((m) => m.annee)).toEqual([2022, 2025]);
    for (const m of q.matrices) expect(m.valeurs.length).toBe(m.jours.length);
  });
  it('donne les mêmes valeurs que le référentiel des chiffres', () => {
    // Le texte cite le référentiel, les graphiques lisent quand.json : ils doivent concorder.
    const ch = chargerChiffres();
    for (const a of ANNEES_COMPAREES) {
      const d = q.annees.find((x) => x.annee === a)!;
      expect(Math.abs(d.maxMw / 1000 - (ch[`quand_rn_max_${a}`].valeur as number))).toBeLessThan(
        0.05
      );
    }
    const d25 = q.annees.find((x) => x.annee === 2025)!;
    const part = (x: number) => d25.chargesPlates.find((c) => c.xMw === x)!.partDansJ;
    expect(Math.round(part(1000) * 100)).toBe(ch.quand_part_j_1gw_2025.valeur);
    expect(Math.round(part(5000) * 100)).toBe(ch.quand_part_j_5gw_2025.valeur);
    const h = (x: number) => d25.chargesPlates.find((c) => c.xMw === x)!.heuresAuDessusDuMax;
    expect(h(5000)).toBe(ch.quand_heures_rn_sup_max_5gw_2025.valeur);
    expect(h(10000)).toBe(ch.quand_heures_rn_sup_max_10gw_2025.valeur);
  });
  it('refuse un fichier incomplet', () => {
    expect(() => lireQuand({})).toThrow(/annees/);
    expect(() => lireQuand({ annees: { 2025: { heures: 8760, charge_residuelle: {} } } })).toThrow(
      /quantiles_mw/
    );
  });
});
