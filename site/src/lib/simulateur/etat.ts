// Hypothèses réglables du simulateur (docs/SIMULATEUR.md, « Hypothèses réglables ») : défauts,
// plages, justifications, et leur passage dans l'adresse de la page (partage d'un scénario par lien).

export interface Etat {
  /** Année civile observée (heure de Paris). */
  annee: number;
  /** Puissance appelée ajoutée, en GW (pas de 0,1 GW). */
  xGw: number;
  /** Heures d'effacement par an (entier). */
  effacement: number;
  /** Froid supplémentaire sur l'épisode, en °C (pas de 0,5). */
  froidC: number;
  /** Plancher de nucléaire non mobilisable retranché à J, en GW (pas de 0,1). */
  plancherGw: number;
}

/** Défauts : froid nul et plancher de 1 GW redonnent exactement les résultats d'avant ces réglages. */
export const DEFAUTS: Etat = { annee: 2025, xGw: 1, effacement: 0, froidC: 0, plancherGw: 1 };

export const BORNES = {
  xGw: { min: 0, max: 20, pas: 0.1 },
  effacement: { min: 0, max: 500, pas: 1 },
  froidC: { min: 0, max: 12, pas: 0.5 },
  plancherGw: { min: 0, max: 3, pas: 0.1 }
} as const;

/**
 * Paramètres de l'adresse : `?annee=2022&x=5&effacement=100&froid=4.5&plancher=0.5` (x et plancher
 * en GW, froid en °C, point décimal). Une ancienne adresse, sans `froid` ni `plancher`, garde
 * leurs défauts : elle redonne le même scénario.
 */
export const PARAMETRES = {
  annee: 'annee',
  xGw: 'x',
  effacement: 'effacement',
  froidC: 'froid',
  plancherGw: 'plancher'
} as const;

const borner = (v: number, min: number, max: number) => Math.min(max, Math.max(min, v));
/** Arrondi au pas de 0,1 GW sans bruit flottant (0,30000000000000004 → 0,3). */
export const arrondirGw = (v: number) => Math.round(v * 10) / 10;
/** Arrondi au pas de 0,5 °C. */
export const arrondirFroid = (v: number) => Math.round(v * 2) / 2;

const virgule = (v: number) => String(v).replace('.', ',');

/**
 * État lu dans une chaîne de requête. Une valeur absente prend son défaut ; une valeur illisible
 * ou hors plage est ramenée au défaut ou à la borne, et l'écart est rendu pour être affiché.
 */
export function lireEtat(
  recherche: string,
  annees: readonly number[]
): { etat: Etat; ecarts: string[] } {
  const p = new URLSearchParams(recherche);
  const ecarts: string[] = [];
  const etat = { ...DEFAUTS };

  const a = p.get(PARAMETRES.annee);
  if (a !== null) {
    if (/^\d{4}$/.test(a) && annees.includes(Number(a))) etat.annee = Number(a);
    else ecarts.push(`année « ${a} » non disponible : ${DEFAUTS.annee} retenue`);
  }

  const x = p.get(PARAMETRES.xGw);
  if (x !== null) {
    const v = Number(x);
    if (x.trim() === '' || !Number.isFinite(v))
      ecarts.push(`puissance « ${x} » illisible : ${DEFAUTS.xGw} GW retenu`);
    else {
      const b = arrondirGw(borner(v, BORNES.xGw.min, BORNES.xGw.max));
      if (b !== v) ecarts.push(`puissance ramenée à ${String(b).replace('.', ',')} GW`);
      etat.xGw = b;
    }
  }

  const e = p.get(PARAMETRES.effacement);
  if (e !== null) {
    const v = Number(e);
    if (e.trim() === '' || !Number.isFinite(v))
      ecarts.push(`effacement « ${e} » illisible : ${DEFAUTS.effacement} h retenu`);
    else {
      const b = Math.round(borner(v, BORNES.effacement.min, BORNES.effacement.max));
      if (b !== v) ecarts.push(`effacement ramené à ${b} h`);
      etat.effacement = b;
    }
  }
  const f = p.get(PARAMETRES.froidC);
  if (f !== null) {
    const v = Number(f);
    if (f.trim() === '' || !Number.isFinite(v))
      ecarts.push(`froid « ${f} » illisible : ${DEFAUTS.froidC} °C retenu`);
    else {
      const b = arrondirFroid(borner(v, BORNES.froidC.min, BORNES.froidC.max));
      if (b !== v) ecarts.push(`froid ramené à ${virgule(b)} °C`);
      etat.froidC = b;
    }
  }

  const pl = p.get(PARAMETRES.plancherGw);
  if (pl !== null) {
    const v = Number(pl);
    if (pl.trim() === '' || !Number.isFinite(v))
      ecarts.push(`plancher « ${pl} » illisible : ${virgule(DEFAUTS.plancherGw)} GW retenu`);
    else {
      const b = arrondirGw(borner(v, BORNES.plancherGw.min, BORNES.plancherGw.max));
      if (b !== v) ecarts.push(`plancher ramené à ${virgule(b)} GW`);
      etat.plancherGw = b;
    }
  }
  return { etat, ecarts };
}

/** Chaîne de requête d'un état ; les valeurs par défaut sont omises (« » si tout est par défaut). */
export function ecrireEtat(etat: Etat): string {
  const p = new URLSearchParams();
  if (etat.annee !== DEFAUTS.annee) p.set(PARAMETRES.annee, String(etat.annee));
  if (etat.xGw !== DEFAUTS.xGw) p.set(PARAMETRES.xGw, String(arrondirGw(etat.xGw)));
  if (etat.effacement !== DEFAUTS.effacement) p.set(PARAMETRES.effacement, String(etat.effacement));
  if (etat.froidC !== DEFAUTS.froidC) p.set(PARAMETRES.froidC, String(arrondirFroid(etat.froidC)));
  if (etat.plancherGw !== DEFAUTS.plancherGw)
    p.set(PARAMETRES.plancherGw, String(arrondirGw(etat.plancherGw)));
  const s = p.toString();
  return s ? `?${s}` : '';
}
