import { describe, expect, it } from 'vitest';
import { chargerChiffres } from './chiffres';
import { chargerCarbone, lireCarbone } from './carbone';

describe('données de « Quel carbone ? » (data/export/carbone.json du dépôt)', () => {
  const d = chargerCarbone();
  it('couvre 2015-2025 pour la production, 2021-2025 pour la consommation', () => {
    expect(d.annees.map((a) => a.annee)).toEqual(Array.from({ length: 11 }, (_, i) => 2015 + i));
    expect(d.annees.filter((a) => a.consommation).map((a) => a.annee)).toEqual([
      2021, 2022, 2023, 2024, 2025
    ]);
  });
  it('a des matrices mois × heure 12 × 24 pour 2022 et 2025', () => {
    expect(d.matrices.map((m) => m.annee)).toEqual([2022, 2025]);
    for (const m of d.matrices) {
      expect(m.valeurs.length).toBe(12);
      expect(m.valeurs.every((l) => l.length === 24 && l.every((v) => v !== null))).toBe(true);
    }
  });
  it('concorde avec les chiffres cités par le texte', () => {
    // Le texte cite le référentiel, le graphique lit carbone.json : ils doivent concorder.
    const ch = chargerChiffres();
    for (const a of [2022, 2024, 2025]) {
      const x = d.annees.find((y) => y.annee === a)!;
      expect(
        Math.abs(x.production.moyenne - (ch[`carbone_prod_moyenne_${a}`].valeur as number))
      ).toBeLessThan(0.05);
      expect(
        Math.abs(x.consommation!.moyenne - (ch[`carbone_conso_moyenne_${a}`].valeur as number))
      ).toBeLessThan(0.05);
    }
    const m25 = d.matrices.find((m) => m.annee === 2025)!.valeurs.flat() as number[];
    expect(Math.max(...m25)).toBeCloseTo(ch.carbone_prod_mh_max_2025.valeur as number, 1);
    expect(Math.min(...m25)).toBeCloseTo(ch.carbone_prod_mh_min_2025.valeur as number, 1);
  });
  it('refuse un fichier incomplet', () => {
    expect(() => lireCarbone({})).toThrow(/annees/);
    expect(() =>
      lireCarbone({
        annees: {
          '2025': {
            production: {
              moyenne_ponderee: 1,
              profil_mensuel: [1],
              max: { valeur: 1 },
              min: { valeur: 1 }
            }
          }
        },
        matrices_mois_heure: { production: {} },
        donnees: { sources: 's', extractions: {} }
      })
    ).toThrow(/12 mois/);
  });
});
