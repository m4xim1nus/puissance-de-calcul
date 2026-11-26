// Making-of : lit au prérendu les trois registres de making-of/ et le brief figé (docs/BRIEF.md),
// les analyse selon leurs formats imposés et rend leur contenu en HTML avec le Markdown maison.
// Les fichiers restent la source unique : rien n'y est réécrit, rien n'est lu côté client.
//
// Les formats sont un contrat, vérifié par makingof.test.ts sur les vrais fichiers du dépôt :
// chaque analyseur renvoie ses entrées et la liste de ses écarts au format (`ecarts`). L'affichage
// reste tolérant (une entrée hors format est montrée telle quelle) ; c'est le test qui échoue.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { cellules, enLigne as enLigneBrut, markdown as markdownBrut } from '$lib/markdown';

// Les scripts npm tournent dans site/ : la racine du dépôt est son parent.
export const RACINE = resolve(process.cwd(), '..');

export const FICHIERS = {
  journal: 'making-of/JOURNAL.md',
  decisions: 'making-of/DECISIONS.md',
  erreurs: 'making-of/ERREURS.md',
  brief: 'docs/BRIEF.md'
} as const;

export const lireFichier = (chemin: string) =>
  readFileSync(resolve(RACINE, chemin), 'utf8').replace(/\r\n?/g, '\n');

// Seules les espaces sont typographiées (insécables avant : ; ? ! et dans « ») : aucun caractère
// du texte ne change, ce qui garde intacts les citations et le brief « publié tel quel ».
const TYPO = { typographie: 'espaces' } as const;
const enLigne = (t: string) => enLigneBrut(t, TYPO);
const markdown = (t: string, niveauTitre = 1) => markdownBrut(t, { ...TYPO, niveauTitre });

const RE_DATE = /^\d{4}-\d{2}-\d{2}$/;
/** Une date AAAA-MM-JJ qui existe au calendrier. */
export function dateValide(d: string): boolean {
  if (!RE_DATE.test(d)) return false;
  const t = new Date(`${d}T00:00:00Z`);
  return !Number.isNaN(t.getTime()) && t.toISOString().slice(0, 10) === d;
}

const apostrophe = (t: string) => t.replace(/’/g, "'");

/** Texte d'en-tête d'un fichier : entre le titre `#` et la première ligne qui vérifie `fin`. */
function entete(lignes: string[], fin: (l: string) => boolean): string {
  const debut = lignes.findIndex((l) => /^#\s/.test(l)) + 1;
  const garde: string[] = [];
  for (let i = debut; i < lignes.length && !fin(lignes[i]); i++) garde.push(lignes[i]);
  return garde.join('\n').trim();
}

/* ------------------------------------------------------------------ Décisions */

export type Arbitre = "l'auteur" | 'Claude';
export const ARBITRES: Arbitre[] = ["l'auteur", 'Claude'];

/** Un arbitre de la colonne « Qui », avec son rôle s'il est précisé : « l'auteur (demande) ». */
export interface Tranche {
  qui: Arbitre;
  role: string | null;
}

export interface Decision {
  id: string;
  date: string;
  /** HTML en ligne. */
  decision: string;
  /** HTML en ligne. */
  raisons: string;
  qui: Tranche[];
  /** Texte brut de la colonne « Qui », pour un affichage de secours. */
  quiTexte: string;
}

export interface Analyse<T> {
  /** HTML du texte d'introduction du fichier. */
  intro: string;
  entrees: T[];
  /** Écarts au format imposé, avec la ligne du fichier ; vide si le fichier respecte le contrat. */
  ecarts: string[];
}

/**
 * « l'auteur », « Claude », « l'auteur (demande), Claude (forme) » → arbitres et rôles ;
 * `null` si un nom n'est pas reconnu. Les virgules entre parenthèses ne séparent pas.
 */
export function analyserQui(texte: string): Tranche[] | null {
  const parts = apostrophe(texte)
    .replace(/\*/g, '')
    .split(/,(?![^(]*\))/)
    .map((p) => p.trim())
    .filter(Boolean);
  if (!parts.length) return null;
  const tranches: Tranche[] = [];
  for (const p of parts) {
    const m = p.match(/^([^()]+?)\s*(?:\(([^()]+)\))?$/);
    if (!m) return null;
    const qui = ARBITRES.find((a) => a.toLowerCase() === m[1].trim().toLowerCase());
    if (!qui) return null;
    tranches.push({ qui, role: m[2]?.trim() || null });
  }
  return tranches;
}

const ENTETE_DECISIONS = ['Date', 'Décision', 'Raisons', 'Qui'];

export function analyserDecisions(texte: string): Analyse<Decision> {
  const lignes = texte.split('\n');
  const ecarts: string[] = [];
  const iTete = lignes.findIndex((l) => /^\s*\|/.test(l));
  if (iTete < 0) return { intro: '', entrees: [], ecarts: ['aucun tableau trouvé'] };
  const tete = cellules(lignes[iTete]);
  if (tete.join('|') !== ENTETE_DECISIONS.join('|'))
    ecarts.push(
      `ligne ${iTete + 1} : en-tête attendu « ${ENTETE_DECISIONS.join(' | ')} », trouvé « ${tete.join(' | ')} »`
    );
  const entrees: Decision[] = [];
  const parDate = new Map<string, number>();
  for (let i = iTete + 2; i < lignes.length && /^\s*\|/.test(lignes[i]); i++) {
    const n = i + 1;
    const c = cellules(lignes[i]);
    if (c.length !== 4) ecarts.push(`ligne ${n} : 4 colonnes attendues, ${c.length} trouvées`);
    const [date = '', decision = '', raisons = '', quiTexte = ''] = c;
    if (!dateValide(date)) ecarts.push(`ligne ${n} : date « ${date} » au lieu de AAAA-MM-JJ`);
    if (!decision) ecarts.push(`ligne ${n} : décision vide`);
    if (!raisons) ecarts.push(`ligne ${n} : raisons vides`);
    const qui = analyserQui(quiTexte);
    if (!qui)
      ecarts.push(
        `ligne ${n} : « Qui » vaut « ${quiTexte} » ; attendu « l'auteur », « Claude », ou une liste « l'auteur (rôle), Claude (rôle) »`
      );
    const rang = (parDate.get(date) ?? 0) + 1;
    parDate.set(date, rang);
    entrees.push({
      id: `decision-${date}-${rang}`,
      date,
      decision: enLigne(decision),
      raisons: enLigne(raisons),
      qui: qui ?? [],
      quiTexte
    });
  }
  if (!entrees.length) ecarts.push('aucune décision dans le tableau');
  return { intro: markdown(entete(lignes, (l) => /^\s*\|/.test(l))), entrees, ecarts };
}

/* ------------------------------------------------------------------ Erreurs */

export const CHAMPS = ['Faux', 'Repéré par', 'Correction', 'Garde-fou ajouté'] as const;
export type Champ = (typeof CHAMPS)[number];

/** Qui a repéré l'erreur, en catégories (celles du bloc « Format » d'ERREURS.md). */
export type Reperage = 'Claude lui-même' | 'un agent' | 'un test' | "l'auteur";
export const REPERAGES: Reperage[] = ['Claude lui-même', 'un agent', 'un test', "l'auteur"];

export interface Erreur {
  id: string;
  date: string;
  /** HTML en ligne. */
  titre: string;
  /** HTML du texte libre placé avant les champs (vide en général). */
  preambule: string;
  champs: { nom: Champ; html: string }[];
  reperage: Reperage | null;
}

/**
 * Catégorie du champ « Repéré par ». L'ordre compte : « `pc check`, lancé par l'agent du
 * pipeline » est un test ; « Claude lui-même » prime sur tout le reste.
 */
export function classerReperage(texte: string): Reperage | null {
  const t = apostrophe(texte);
  if (/Claude lui-même/i.test(t)) return 'Claude lui-même';
  if (/\btest\b|\bpc check\b/i.test(t)) return 'un test';
  if (/\bl'auteur\b/i.test(t)) return "l'auteur";
  if (/\bagents?\b|contre-vérification|relecture/i.test(t)) return 'un agent';
  return null;
}

const RE_CHAMP = /^- \*\*([^*]+)\*\*\s*:\s?(.*)$/;
const RE_TITRE_ERREUR = /^### (\S+) — (.+)$/;

/** Retire l'indentation commune des lignes non vides. */
function desindenter(lignes: string[]): string {
  const marges = lignes.filter((l) => l.trim()).map((l) => l.match(/^ */)![0].length);
  const m = marges.length ? Math.min(...marges) : 0;
  return lignes.map((l) => l.slice(Math.min(m, l.match(/^ */)![0].length))).join('\n');
}

export function analyserErreurs(texte: string): Analyse<Erreur> {
  const lignes = texte.split('\n');
  const ecarts: string[] = [];
  // Introduction : jusqu'au bloc « Format : » (gabarit pour les rédacteurs, pas pour le lecteur).
  const intro = markdown(entete(lignes, (l) => /^Format\s*:/.test(l) || /^(---|### )/.test(l)));

  // Entrées : chaque `### ` hors bloc de code (le gabarit du format en contient un).
  const blocs: { n: number; titre: string; corps: string[] }[] = [];
  let code = false;
  lignes.forEach((l, i) => {
    if (/^\s*(```|~~~)/.test(l)) code = !code;
    if (!code && l.startsWith('### ')) blocs.push({ n: i + 1, titre: l, corps: [] });
    else if (blocs.length && !/^---\s*$/.test(l)) blocs.at(-1)!.corps.push(l);
  });

  const entrees: Erreur[] = blocs.map(({ n, titre, corps }, k) => {
    const m = titre.match(RE_TITRE_ERREUR);
    if (!m)
      ecarts.push(`ligne ${n} : titre attendu « ### AAAA-MM-JJ — titre », trouvé « ${titre} »`);
    const date = m?.[1] ?? '';
    if (m && !dateValide(date)) ecarts.push(`ligne ${n} : date « ${date} » au lieu de AAAA-MM-JJ`);

    const preambule: string[] = [];
    const champs: { nom: Champ; lignes: string[] }[] = [];
    for (const l of corps) {
      const c = l.match(RE_CHAMP);
      const nom = c && CHAMPS.find((x) => x === c[1].trim());
      if (nom) champs.push({ nom, lignes: [c![2]] });
      else if (champs.length) champs.at(-1)!.lignes.push(l);
      else preambule.push(l);
    }
    for (const nom of CHAMPS) {
      const k2 = champs.filter((c) => c.nom === nom).length;
      if (k2 === 0) ecarts.push(`ligne ${n} : champ « ${nom} » absent`);
      if (k2 > 1) ecarts.push(`ligne ${n} : champ « ${nom} » répété`);
    }
    const textes = champs.map((c) => ({ nom: c.nom, texte: desindenter(c.lignes).trim() }));
    for (const c of textes) if (!c.texte) ecarts.push(`ligne ${n} : champ « ${c.nom} » vide`);
    const repere = textes.find((c) => c.nom === 'Repéré par');
    const reperage = repere ? classerReperage(repere.texte) : null;
    if (repere && !reperage)
      ecarts.push(
        `ligne ${n} : « Repéré par » ne dit pas qui (attendu : l'auteur, un test, un agent ou Claude lui-même)`
      );
    return {
      id: `erreur-${date || 'sans-date'}-${k + 1}`,
      date,
      titre: enLigne(m?.[2] ?? titre.replace(/^###\s*/, '')),
      preambule: markdown(preambule.join('\n')),
      champs: textes.map((c) => ({ nom: c.nom, html: markdown(c.texte) })),
      reperage
    };
  });
  if (!entrees.length) ecarts.push('aucune entrée « ### AAAA-MM-JJ — titre »');
  return { intro, entrees, ecarts };
}

/* ------------------------------------------------------------------ Journal */

/** Paragraphes du journal résumés dans l'en-tête de session. */
export const RESUMES = ['Durée', 'Agents', 'Coût'] as const;

export interface Session {
  id: string;
  numero: number;
  date: string;
  /** « à partir de 23 h 03 », si l'en-tête le donne. */
  horaire: string | null;
  /** HTML en ligne. */
  objet: string;
  /** HTML : le paragraphe « Demande de l'auteur » et la citation qui suit. */
  demande: string;
  /** Première phrase des paragraphes Durée, Agents, Coût présents (HTML en ligne). */
  resume: { cle: (typeof RESUMES)[number]; html: string }[];
  /** Intitulés des parties repliées, dans l'ordre (« Ce qu'elle recouvrait », « Fait »…). */
  parties: string[];
  /** HTML de tout le reste de la session, replié à l'affichage. */
  detail: string;
  /** HTML du brief, rattaché à la session 1 (décision de l'auteur, 2026-11-26). */
  brief: string | null;
}

const RE_TITRE_SESSION = /^## Session (\d+) — (\d{4}-\d{2}-\d{2})(?:,\s*(.+?))?\s+·\s+(.+)$/;
const RE_PARTIE = /^\*\*([^*]+)\*\*/;
const DEMANDE = /^Demande de l'auteur/;

/** Première phrase d'un paragraphe, sans son point final. */
export function premierePhrase(texte: string): string {
  const t = texte.replace(/\s+/g, ' ').trim();
  const m = t.match(/^(.+?[^.\s])\.(?=\s|$)/);
  return m ? m[1] : t;
}

export function analyserJournal(texte: string, brief: string | null = null): Analyse<Session> {
  const lignes = texte.split('\n');
  const ecarts: string[] = [];
  const intro = markdown(entete(lignes, (l) => /^(---\s*$|## )/.test(l)));

  const blocs: { n: number; titre: string; corps: string[] }[] = [];
  lignes.forEach((l, i) => {
    if (l.startsWith('## ')) blocs.push({ n: i + 1, titre: l, corps: [] });
    else if (blocs.length && !/^---\s*$/.test(l)) blocs.at(-1)!.corps.push(l);
  });

  const entrees: Session[] = blocs.map(({ n, titre, corps }) => {
    const m = titre.match(RE_TITRE_SESSION);
    if (!m)
      ecarts.push(
        `ligne ${n} : titre attendu « ## Session N — AAAA-MM-JJ[, horaire] · objet », trouvé « ${titre} »`
      );
    else if (!dateValide(m[2])) ecarts.push(`ligne ${n} : date « ${m[2]} » invalide`);
    const numero = m ? Number(m[1]) : 0;

    // Parties : un paragraphe qui commence par **Intitulé**, jusqu'à la partie suivante.
    const parties: { titre: string | null; lignes: string[] }[] = [{ titre: null, lignes: [] }];
    corps.forEach((l, i) => {
      const p = l.match(RE_PARTIE);
      if (p && (i === 0 || !corps[i - 1].trim()))
        parties.push({ titre: apostrophe(p[1]).trim(), lignes: [l] });
      else parties.at(-1)!.lignes.push(l);
    });
    const demande = parties.find((p) => p.titre && DEMANDE.test(p.titre));
    if (!demande) ecarts.push(`ligne ${n} : pas de paragraphe « **Demande de l'auteur** »`);
    else if (!demande.lignes.some((l) => /^\s{0,3}>/.test(l)))
      ecarts.push(`ligne ${n} : la demande de l'auteur n'est pas citée (bloc « > » attendu)`);

    const resume = RESUMES.flatMap((cle) => {
      const p = parties.find((x) => x.titre === cle);
      if (!p) return [];
      const texte = p.lignes
        .join(' ')
        .replace(RE_PARTIE, '')
        .replace(/^\s*:\s*/, '');
      return [{ cle, html: enLigne(premierePhrase(texte)) }];
    });
    const reste = parties.filter((p) => p !== demande && p.lignes.some((l) => l.trim()));
    return {
      id: `session-${numero || n}`,
      numero,
      date: m?.[2] ?? '',
      horaire: m?.[3] ?? null,
      objet: enLigne(m?.[4] ?? titre.replace(/^##\s*/, '')),
      demande: demande ? markdown(demande.lignes.join('\n')) : '',
      resume,
      parties: reste.map((p) => p.titre ?? 'Notes'),
      detail: markdown(reste.map((p) => p.lignes.join('\n')).join('\n\n')),
      brief: numero === 1 ? brief : null
    };
  });
  if (!entrees.length) ecarts.push('aucune session « ## Session N — … »');
  if (brief !== null && !entrees.some((s) => s.numero === 1))
    ecarts.push('pas de session 1 où rattacher le brief');
  return { intro, entrees, ecarts };
}

/* ------------------------------------------------------------------ Page */

export function makingOf() {
  // Le brief est rendu en entier, sans retouche : ses titres descendent sous celui de la session.
  const brief = markdown(lireFichier(FICHIERS.brief), 4);
  return {
    journal: analyserJournal(lireFichier(FICHIERS.journal), brief),
    decisions: analyserDecisions(lireFichier(FICHIERS.decisions)),
    erreurs: analyserErreurs(lireFichier(FICHIERS.erreurs))
  };
}
