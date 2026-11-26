// Lecture d'un fichier data/export/horaire/AAAA.csv (format décrit dans son LISEZMOI.md) en table
// horaire du moteur. Lecture stricte : une colonne manquante ou une heure manquante, en double ou
// hors d'ordre lève une erreur plutôt que de fausser un résultat. Cellule vide = donnée absente.
import type { TableHoraire } from './moteur';

/** Colonnes lues : nom dans le CSV → nom dans la table du moteur (celui de la référence Python). */
const COLONNES = {
  heure_utc: 'heure_utc',
  consommation: 'consommation',
  eolien: 'eolien',
  solaire: 'solaire',
  nucleaire: 'nucleaire',
  nucleaire_disponible: 'nucleaire_disponible',
  prix: 'prix',
  solde_echanges: 'ech_physiques'
} as const;

/** Colonnes facultatives : lues si l'en-tête les porte (CSV antérieurs : absentes). */
const FACULTATIVES = {
  nucleaire_disponible_reintegre: 'nucleaire_disponible_reintegre'
} as const;

const HEURE = 3_600_000;

function nombre(cellule: string, ligne: number, colonne: string): number | null {
  if (cellule === '') return null;
  const v = Number(cellule);
  if (!Number.isFinite(v))
    throw new Error(
      `CSV horaire, ligne ${ligne} : « ${cellule} » n'est pas un nombre (${colonne})`
    );
  return v;
}

export function lireCsvHoraire(texte: string): TableHoraire {
  const lignes = texte.replace(/\r\n?/g, '\n').trim().split('\n');
  const entete = lignes[0].split(',');
  const indices = Object.fromEntries(
    Object.keys(COLONNES).map((c) => {
      const i = entete.indexOf(c);
      if (i < 0) throw new Error(`CSV horaire : colonne « ${c} » absente`);
      return [c, i];
    })
  ) as Record<keyof typeof COLONNES, number>;
  const facultatives = Object.entries(FACULTATIVES)
    .map(([csv, nom]) => [csv, nom, entete.indexOf(csv)] as const)
    .filter(([, , i]) => i >= 0);

  const table: TableHoraire = {
    heure_utc: [],
    consommation: [],
    eolien: [],
    solaire: [],
    nucleaire: [],
    nucleaire_disponible: [],
    prix: [],
    ech_physiques: []
  };
  for (const [, nom] of facultatives) table[nom] = [];
  let precedente = NaN;
  for (let k = 1; k < lignes.length; k++) {
    const c = lignes[k].split(',');
    const h = c[indices.heure_utc];
    const t = Date.parse(h);
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$/.test(h) || Number.isNaN(t))
      throw new Error(`CSV horaire, ligne ${k + 1} : heure illisible « ${h} »`);
    if (k > 1 && t !== precedente + HEURE)
      throw new Error(`CSV horaire, ligne ${k + 1} : heure manquante, en double ou hors d'ordre`);
    precedente = t;
    table.heure_utc.push(h);
    for (const [csv, nom] of Object.entries(COLONNES)) {
      if (nom === 'heure_utc') continue;
      (table[nom] as (number | null)[]).push(
        nombre(c[indices[csv as keyof typeof COLONNES]] ?? '', k + 1, csv)
      );
    }
    for (const [csv, nom, i] of facultatives)
      (table[nom] as (number | null)[]).push(nombre(c[i] ?? '', k + 1, csv));
  }
  return table;
}
