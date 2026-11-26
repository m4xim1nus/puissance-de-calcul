// Prix day-ahead France, lus au prérendu dans data/export/horaire/AAAA.csv et réduits à un
// fichier statique compact par année (une valeur par heure UTC).
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { arrondiStockage, type AnneePrix } from '$lib/heatmap';
import { RACINE } from '$lib/server/makingof';

interface Meta {
  annees: Record<string, { heures: number; premiere_heure_utc: string }>;
  sources: Record<string, { extrait_le: string }>;
}

let meta: Meta | undefined;
const lireMeta = (): Meta =>
  (meta ??= JSON.parse(readFileSync(resolve(RACINE, 'data/export/meta.json'), 'utf8')));

/** Années disponibles, de la plus ancienne à la plus récente. */
export function anneesPrix(): number[] {
  return Object.keys(lireMeta().annees)
    .map(Number)
    .sort((a, b) => a - b);
}

let sommesQuarts: Map<number, number> | undefined;

/**
 * Somme exacte, en centimes, des quarts d'heure de chaque heure (depuis le passage au pas de
 * 15 min). Sert à trancher le signe des heures que le CSV horaire arrondit à « -0.0 » : une
 * moyenne de −0,0025 €/MWh est négative, une somme nulle ne l'est pas (erreur d'arrondi flottant).
 */
function centimesParHeure(): Map<number, number> {
  if (sommesQuarts) return sommesQuarts;
  sommesQuarts = new Map();
  const lignes = readFileSync(resolve(RACINE, 'data/export/prix_quart_horaire.csv'), 'utf8')
    .trim()
    .split('\n');
  const entete = lignes[0].split(',');
  const iT = entete.indexOf('debut_utc');
  const iP = entete.indexOf('prix_eur_mwh');
  for (const l of lignes.slice(1)) {
    const c = l.split(',');
    if (c[iP] === '') continue;
    const heure = Math.floor(Date.parse(c[iT]) / 3_600_000) * 3_600_000;
    sommesQuarts.set(heure, (sommesQuarts.get(heure) ?? 0) + Math.round(Number(c[iP]) * 100));
  }
  return sommesQuarts;
}

const heuresDansAnnee = (a: number) => (Date.UTC(a + 1, 0, 1) - Date.UTC(a, 0, 1)) / 3_600_000;

/** Prix exacts d'une année (€/MWh, null si absent), dans l'ordre des heures UTC. */
export function prixExacts(annee: number): { debut: string; prix: (number | null)[] } {
  const lignes = readFileSync(resolve(RACINE, `data/export/horaire/${annee}.csv`), 'utf8')
    .trim()
    .split('\n');
  const entete = lignes[0].split(',');
  const iH = entete.indexOf('heure_utc');
  const iP = entete.indexOf('prix');
  if (iH < 0 || iP < 0)
    throw new Error(`horaire/${annee}.csv : colonnes heure_utc ou prix absentes`);
  const debut = lignes[1].split(',')[iH];
  const t0 = Date.parse(debut);
  const prix = lignes.slice(1).map((l, i) => {
    const c = l.split(',');
    if (Date.parse(c[iH]) !== t0 + i * 3_600_000)
      throw new Error(`horaire/${annee}.csv : heure manquante ou en double à la ligne ${i + 2}`);
    if (c[iP] === '') return null;
    const v = Number(c[iP]);
    // Moyenne arrondie à zéro : le signe vient de la somme exacte des quarts d'heure.
    if (v === 0) {
      const centimes = centimesParHeure().get(t0 + i * 3_600_000);
      if (centimes !== undefined) return centimes < 0 ? -0 : 0;
    }
    return v;
  });
  return { debut, prix };
}

export function anneePrix(annee: number): AnneePrix {
  const m = lireMeta();
  const infos = m.annees[String(annee)];
  const source = m.sources[`prix_fr/${annee}`];
  if (!infos || !source) throw new Error(`Prix ${annee} absents de meta.json`);
  const { debut, prix } = prixExacts(annee);
  return {
    annee,
    debut,
    prix: prix.map((v) => (v === null ? null : arrondiStockage(v))),
    provisoire: infos.heures < heuresDansAnnee(annee),
    extrait_le: source.extrait_le
  };
}
