// Hypothèses réglables du simulateur (docs/SIMULATEUR.md, « Hypothèses réglables ») : défauts,
// plages, justifications, et leur passage dans l'adresse de la page (partage d'un scénario par lien).

export interface Etat {
  /** Année civile observée (heure de Paris). */
  annee: number;
  /** Puissance appelée ajoutée, en GW (pas de 0,1 GW). */
  xGw: number;
  /** Heures d'effacement par an (entier). */
  effacement: number;
}

export const DEFAUTS: Etat = { annee: 2025, xGw: 1, effacement: 0 };

export const BORNES = {
  xGw: { min: 0, max: 20, pas: 0.1 },
  effacement: { min: 0, max: 500, pas: 1 }
} as const;

/** Paramètres de l'adresse : `?annee=2022&x=5&effacement=100` (x en GW, point décimal). */
export const PARAMETRES = { annee: 'annee', xGw: 'x', effacement: 'effacement' } as const;

const borner = (v: number, min: number, max: number) => Math.min(max, Math.max(min, v));
/** Arrondi au pas de 0,1 GW sans bruit flottant (0,30000000000000004 → 0,3). */
export const arrondirGw = (v: number) => Math.round(v * 10) / 10;

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
  return { etat, ecarts };
}

/** Chaîne de requête d'un état ; les valeurs par défaut sont omises (« » si tout est par défaut). */
export function ecrireEtat(etat: Etat): string {
  const p = new URLSearchParams();
  if (etat.annee !== DEFAUTS.annee) p.set(PARAMETRES.annee, String(etat.annee));
  if (etat.xGw !== DEFAUTS.xGw) p.set(PARAMETRES.xGw, String(arrondirGw(etat.xGw)));
  if (etat.effacement !== DEFAUTS.effacement) p.set(PARAMETRES.effacement, String(etat.effacement));
  const s = p.toString();
  return s ? `?${s}` : '';
}
