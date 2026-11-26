import { describe, expect, it } from 'vitest';
import { chargerChiffres } from '$lib/server/chiffres';
import { anneePrix, anneesPrix, prixExacts } from '$lib/server/prix';
import {
  arrondiStockage,
  classe,
  comparaisonReference,
  decalageParis,
  grille,
  heuresNegatives,
  statistiques
} from './heatmap';

describe('heure de Paris', () => {
  it('applique la règle européenne des changements d’heure', () => {
    expect(decalageParis(Date.parse('2025-03-30T00:59Z'))).toBe(1);
    expect(decalageParis(Date.parse('2025-03-30T01:00Z'))).toBe(2);
    expect(decalageParis(Date.parse('2025-10-26T00:59Z'))).toBe(2);
    expect(decalageParis(Date.parse('2025-10-26T01:00Z'))).toBe(1);
    expect(decalageParis(Date.parse('2016-03-27T01:00Z'))).toBe(2);
  });
});

describe('grille jours × heures', () => {
  const a = anneePrix(2025);
  const g = grille(a);
  it('compte 365 jours de 24 cases, du 1er janvier au 31 décembre', () => {
    expect(g).toHaveLength(365);
    expect(g[0].date).toBe('2025-01-01');
    expect(g.at(-1)!.date).toBe('2025-12-31');
    expect(g.every((j) => j.cases.length === 24)).toBe(true);
  });
  it('laisse vide la case 2 h du jour de 23 heures', () => {
    const j = g.find((j) => j.date === '2025-03-30')!;
    expect(j.cases[2]).toEqual({ type: 'inexistante' });
    expect(j.cases.filter((c) => c.type === 'prix')).toHaveLength(23);
  });
  it('garde les deux valeurs de 2 h le jour de 25 heures, dans l’ordre', () => {
    const j = g.find((j) => j.date === '2025-10-26')!;
    expect(j.cases[2]).toEqual({ type: 'double', v: [16, 8] });
  });
  it('n’a aucune case hors données pour une année complète', () => {
    expect(g.flatMap((j) => j.cases).some((c) => c.type === 'hors-donnees')).toBe(false);
  });
  it('marque l’année en cours comme provisoire', () => {
    const derniere = anneesPrix().at(-1)!;
    expect(anneePrix(derniere).provisoire).toBe(derniere >= 2026);
    expect(a.provisoire).toBe(false);
  });
});

describe('prix négatifs et arrondis', () => {
  it('garde le signe à l’arrondi de stockage', () => {
    expect(arrondiStockage(-0.01)).toBe(-0.01);
    expect(arrondiStockage(-1.5)).toBeLessThan(0);
    expect(arrondiStockage(87.46)).toBe(87);
    expect(arrondiStockage(-0)).toBeLessThan(0);
    expect(arrondiStockage(-0.004)).toBeLessThan(0);
    expect(arrondiStockage(0)).toBe(0);
  });
  it('sépare strictement négatif et nul', () => {
    expect(classe(-0.01)).toBe(2);
    expect(classe(0)).toBe(3);
    expect(classe(-0)).toBe(2);
    expect(classe(650)).toBe(7);
  });
  it('retrouve les heures négatives du référentiel (RTE) pour 2023, 2024 et 2025', () => {
    const chiffres = chargerChiffres();
    for (const annee of [2023, 2024, 2025]) {
      const ref = chiffres[`heures_negatives_${annee}`].valeur;
      const exact = heuresNegatives({ annee, ...prixExacts(annee) }).total;
      const compact = heuresNegatives(anneePrix(annee)).total;
      expect(exact, `${annee}`).toBe(ref);
      expect(compact, `${annee} (données compactes)`).toBe(ref);
    }
  });
  it('tranche le signe des moyennes arrondies à zéro par la somme exacte des quarts d’heure', () => {
    // 2026-02-23 14 h UTC : quarts −0,04, −0,01, −0,01, +0,06 → somme nulle, pas négative.
    const { debut, prix } = prixExacts(2026);
    const i = (Date.parse('2026-02-23T14:00Z') - Date.parse(debut)) / 3_600_000;
    expect(Object.is(prix[i], 0)).toBe(true);
    // 2025-10-05 1 h UTC : quarts 0, 0, −0,01, −0,01 → moyenne −0,005, négative. Depuis le
    // 26/11/2026, le pipeline exporte cette moyenne exacte (4 décimales) au lieu de « -0.0 ».
    const a = prixExacts(2025);
    const j = (Date.parse('2025-10-05T01:00Z') - Date.parse(a.debut)) / 3_600_000;
    expect(a.prix[j]).toBeLessThan(0);
  });
  it('compte heures sans prix, prix planchers et heures écrêtées', () => {
    const st = statistiques(grille(anneePrix(2025)));
    expect(st.negatives).toBe(513);
    expect(st.planchers).toBeGreaterThan(0);
    expect(st.planchers).toBeLessThan(st.negatives);
    expect(st.sansPrix).toBe(0);
    expect(statistiques(grille(anneePrix(2015))).sansPrix).toBeGreaterThan(0);
    expect(statistiques(grille(anneePrix(2022))).ecretees).toBeGreaterThan(8760 * 0.1);
  });
  it('n’affirme l’égalité avec RTE que si elle est vérifiée', () => {
    expect(comparaisonReference(513, 513)).toEqual({
      egal: true,
      texte: 'égal au chiffre publié par RTE'
    });
    const c = comparaisonReference(506, 513);
    expect(c.egal).toBe(false);
    expect(c.texte).toBe('RTE publie 513\u00a0h\u202f; écart de −7\u00a0h');
  });
  it('produit un fichier compact d’environ 35 Ko par an', () => {
    const taille = JSON.stringify(anneePrix(2022)).length;
    expect(taille).toBeLessThan(45_000);
  });
});
