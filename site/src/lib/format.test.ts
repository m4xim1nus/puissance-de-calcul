import { describe, expect, it } from 'vitest';
import {
  FINE,
  INSECABLE,
  formaterDate,
  formaterNombre,
  formaterPeriode,
  formaterValeur
} from './format';

describe('formatage des nombres', () => {
  it('met une virgule décimale', () => {
    expect(formaterNombre(4.34)).toBe('4,34');
    expect(formaterNombre(442.2)).toBe('442,2');
    expect(formaterNombre(36.73)).toBe('36,73');
  });
  it('groupe les milliers avec une espace fine insécable', () => {
    expect(formaterNombre(1400)).toBe(`1${FINE}400`);
    expect(formaterNombre(4339)).toBe(`4${FINE}339`);
  });
  it('sépare un symbole d’unité par une espace fine insécable', () => {
    expect(formaterValeur(442.2, 'TWh')).toBe(`442,2${FINE}TWh`);
    expect(formaterValeur(22, '%')).toBe(`22${FINE}%`);
    expect(formaterValeur(1400, 'MW')).toBe(`1${FINE}400${FINE}MW`);
  });
  it('sépare une unité en toutes lettres par une espace insécable', () => {
    expect(formaterValeur(63, 'sites')).toBe(`63${INSECABLE}sites`);
  });
  it('écrit un intervalle « 4 à 5 TWh », insécable de bout en bout', () => {
    const v = formaterValeur([4, 5], 'TWh');
    expect(v).toBe(`4${INSECABLE}à${INSECABLE}5${FINE}TWh`);
    expect(v).not.toMatch(/ /);
  });
  it('refuse une valeur non finie', () => {
    expect(() => formaterNombre(Number.NaN)).toThrow();
  });
});

describe('formatage des dates et périodes', () => {
  it('écrit les dates en toutes lettres, avec « 1er »', () => {
    expect(formaterDate('2026-01-30')).toBe(`30${INSECABLE}janvier${INSECABLE}2026`);
    expect(formaterDate('2025-11-01')).toBe(`1er${INSECABLE}novembre${INSECABLE}2025`);
    expect(formaterDate('2026-05')).toBe(`mai${INSECABLE}2026`);
    expect(formaterDate('2025-12-19', true)).toBe(`19${INSECABLE}déc.${INSECABLE}2025`);
  });
  it('laisse les périodes en clair et convertit les dates qu’elles contiennent', () => {
    expect(formaterPeriode('fin 2024')).toBe('fin 2024');
    expect(formaterPeriode('2024')).toBe('2024');
    expect(formaterPeriode('2022 → 2025-11-15')).toBe(
      `2022 → 15${INSECABLE}novembre${INSECABLE}2025`
    );
  });
});
