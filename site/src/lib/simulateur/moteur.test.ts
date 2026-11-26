// Parité du moteur TypeScript avec la référence Python (pipeline/pc/quand.py) :
// 1. tous les cas partagés de pipeline/tests/cas_quand.json (valeurs calculées à la main) sont
//    rejoués ; pour `indicateurs_annee`, seuls les chemins que le moteur calcule sont comparés, et
//    les autres doivent figurer dans NON_CALCULES (un nouveau chemin non classé fait échouer) ;
// 2. sur les années réelles 2022 et 2025, lues dans data/export/horaire/AAAA.csv (les fichiers que
//    sert le site), le moteur redonne les valeurs de data/export/quand.json (charges plates, RN max
//    et sa date, Σ J, heures à prix bas), aux arrondis de l'export près.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { lireCsvHoraire } from './csv';
import { debutParis, quantile, resumeAnnee, simuler, type TableHoraire } from './moteur';

const RACINE = resolve(process.cwd(), '..');
const lireJson = (chemin: string) => JSON.parse(readFileSync(resolve(RACINE, chemin), 'utf8'));

interface Cas {
  nom: string;
  fonction: string;
  parametres?: Record<string, unknown>;
  entree: Record<string, unknown>;
  attendu: Record<string, unknown>;
}
const CAS = lireJson('pipeline/tests/cas_quand.json') as { tolerance: number; cas: Cas[] };

/** Chemins d'`indicateurs_annee` que seul Python calcule (préfixes). */
const NON_CALCULES = [
  'heures_tendues.par_mois',
  'heures_tendues.par_heure_paris',
  'heures_tendues.part_',
  'heures_tendues.heures_couverture',
  'heures_tendues.couverture_moyenne_mw',
  'jeu_nucleaire.par_mois_twh',
  'prix.rn_moyenne_',
  'prix.j_moyenne_'
];

/** Fonctions de la référence que le moteur ne réimplémente pas (la heatmap lit quand.json). */
const FONCTIONS_NON_IMPLEMENTEES = new Set(['matrice_jour_heure']);

function lire(obj: unknown, chemin: string): unknown {
  let o = obj;
  for (const m of chemin ? chemin.split('.') : []) {
    if (o === undefined || o === null) return undefined;
    o = Array.isArray(o) ? o[Number(m)] : (o as Record<string, unknown>)[m];
  }
  return o;
}

function egal(a: unknown, b: unknown, tol: number): boolean {
  if (Array.isArray(b))
    return Array.isArray(a) && a.length === b.length && b.every((y, i) => egal(a[i], y, tol));
  if (b === null || typeof b === 'string') return a === b;
  if (typeof a !== 'number' || typeof b !== 'number') return false;
  return Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));
}

function executer(cas: Cas): unknown {
  const e = cas.entree;
  const p = cas.parametres ?? {};
  switch (cas.fonction) {
    case 'indicateurs_annee':
      return resumeAnnee(e as unknown as TableHoraire, p);
    case 'simuler':
      return simuler(
        e as unknown as TableHoraire,
        p.x_mw as number,
        (p.heures_effacement as number | undefined) ?? 0,
        p.n_exact as number | undefined,
        p.pas_monotone as number | undefined
      );
    case 'quantile':
      return quantile(e.tries as number[], e.q as number);
    default:
      throw new Error(`fonction ${cas.fonction} : ni implémentée ni déclarée non implémentée`);
  }
}

describe('parité avec pipeline/tests/cas_quand.json', () => {
  const rejoues = CAS.cas.filter((c) => !FONCTIONS_NON_IMPLEMENTEES.has(c.fonction));

  it('rejoue tous les cas des fonctions implémentées, et au moins ceux du simulateur', () => {
    expect(rejoues.filter((c) => c.fonction === 'simuler').length).toBeGreaterThanOrEqual(5);
    expect(CAS.cas.length - rejoues.length).toBe(
      CAS.cas.filter((c) => c.fonction === 'matrice_jour_heure').length
    );
  });

  it.each(rejoues.map((c) => [c.nom, c] as const))('%s', (_, cas) => {
    const sortie = executer(cas);
    const fautes: string[] = [];
    let compares = 0;
    for (const [chemin, v] of Object.entries(cas.attendu)) {
      if (cas.fonction === 'indicateurs_annee' && NON_CALCULES.some((p) => chemin.startsWith(p)))
        continue;
      const obtenu = lire(sortie, chemin);
      compares++;
      if (!egal(obtenu, v, CAS.tolerance))
        fautes.push(`${chemin} : obtenu ${JSON.stringify(obtenu)}, attendu ${JSON.stringify(v)}`);
    }
    expect(fautes).toEqual([]);
    expect(compares).toBeGreaterThan(0);
  });
});

describe('heure de Paris', () => {
  it('suit les changements d’heure comme zoneinfo', () => {
    expect(debutParis('2024-12-31T23:00Z')).toBe('2025-01-01T00:00+01:00');
    expect(debutParis('2025-03-30T00:00Z')).toBe('2025-03-30T01:00+01:00');
    expect(debutParis('2025-03-30T01:00Z')).toBe('2025-03-30T03:00+02:00');
    expect(debutParis('2025-10-26T00:00Z')).toBe('2025-10-26T02:00+02:00');
    expect(debutParis('2025-10-26T01:00Z')).toBe('2025-10-26T02:00+01:00');
  });
  it('refuse une heure sans fuseau', () => {
    expect(() => debutParis('2025-01-01T00:00')).toThrow();
  });
});

describe('simulateur : propriétés', () => {
  const table = lireCsvHoraire(
    readFileSync(resolve(RACINE, 'data/export/horaire/2025.csv'), 'utf8')
  );

  it('effacer les N* heures au-dessus du maximum suffit, N* − 1 ne suffit pas', () => {
    const x = 5000;
    const nEtoile = simuler(table, x).heures_au_dessus_du_max as number;
    expect(nEtoile).toBeGreaterThan(1);
    expect(simuler(table, x, nEtoile).heures_au_dessus_du_max).toBe(0);
    expect(simuler(table, x, nEtoile - 1).heures_au_dessus_du_max).toBe(1);
  });

  it('refuse une puissance négative ou un effacement non entier', () => {
    expect(() => simuler(table, -1)).toThrow();
    expect(() => simuler(table, 1000, 1.5)).toThrow();
  });
});

describe('parité avec data/export/quand.json sur les années réelles', () => {
  const quand = lireJson('data/export/quand.json');
  /** quand.json arrondit les TWh et les parts à 4 décimales, les MW à l'unité. */
  const proche4 = (a: number | null, b: number) => Math.abs((a as number) - b) <= 0.5e-4 + 1e-12;

  it.each([2022, 2025])('%i', (annee) => {
    const ref = quand.annees[String(annee)];
    const table = lireCsvHoraire(
      readFileSync(resolve(RACINE, `data/export/horaire/${annee}.csv`), 'utf8')
    );
    const xs = quand.parametres.charges_plates_mw as number[];
    const r = resumeAnnee(table, { charges_mw: xs });

    expect(r.heures).toBe(ref.heures);
    expect(r.charge_residuelle.heures_valides).toBe(ref.charge_residuelle.heures_valides);
    expect(r.charge_residuelle.max).toEqual(ref.charge_residuelle.max);
    expect(r.charge_residuelle.min).toEqual(ref.charge_residuelle.min);
    expect(r.charge_residuelle.monotone).toEqual(ref.charge_residuelle.monotone);
    expect(r.charge_residuelle.heures_negatives).toBe(ref.charge_residuelle.heures_negatives);
    for (const [k, v] of Object.entries(ref.charge_residuelle.quantiles_mw))
      expect(
        Math.abs(r.charge_residuelle.quantiles_mw![k as 'p50'] - (v as number))
      ).toBeLessThanOrEqual(0.5);
    expect(r.heures_tendues.heures).toEqual(ref.heures_tendues.heures);

    expect(r.jeu_nucleaire.heures_valides).toBe(ref.jeu_nucleaire.heures_valides);
    expect(proche4(r.jeu_nucleaire.somme_twh, ref.jeu_nucleaire.somme_twh)).toBe(true);
    expect(r.jeu_nucleaire.heures_positif).toBe(ref.jeu_nucleaire.heures_positif);

    expect(r.prix).toEqual({
      heures_valides: ref.prix.heures_valides,
      heures_negatif: ref.prix.heures_negatif,
      heures_nul_ou_negatif: ref.prix.heures_nul_ou_negatif
    });

    expect(r.charges_plates.length).toBe(ref.charges_plates.length);
    r.charges_plates.forEach((c, i) => {
      const e = ref.charges_plates[i];
      expect(c.x_mw).toBe(e.x_mw);
      expect(proche4(c.energie_ajoutee_twh, e.energie_ajoutee_twh)).toBe(true);
      expect(proche4(c.energie_dans_j_twh, e.energie_dans_j_twh)).toBe(true);
      expect(proche4(c.part_dans_j, e.part_dans_j)).toBe(true);
      expect(c.heures_j_superieur_ou_egal_x).toBe(e.heures_j_superieur_ou_egal_x);
      expect(c.rn_max_plus_x_mw).toBe(e.rn_max_plus_x_mw);
      expect(c.heures_rn_plus_x_au_dessus_du_max).toBe(e.heures_rn_plus_x_au_dessus_du_max);
      expect(
        Math.abs(
          (c.solde_echanges_moyen_heures_j_ge_x_mw as number) -
            e.solde_echanges_moyen_heures_j_ge_x_mw
        )
      ).toBeLessThanOrEqual(0.5);

      // Le simulateur sans effacement redonne la charge plate publiée.
      const s = simuler(table, e.x_mw);
      expect(proche4(s.part_dans_j, e.part_dans_j)).toBe(true);
      expect(proche4(s.energie_ajoutee_twh, e.energie_ajoutee_twh)).toBe(true);
      expect(s.heures_au_dessus_du_max).toBe(e.heures_rn_plus_x_au_dessus_du_max);
      expect(s.max_apres?.valeur_mw).toBe(e.rn_max_plus_x_mw);
      expect(s.heures_j_couvre_charge).toBe(e.heures_j_superieur_ou_egal_x);
    });
  });
});
