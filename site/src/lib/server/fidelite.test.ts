// Fidélité de la page /making-of à ses sources Markdown, sur les vrais fichiers du dépôt.
//
// La page est rendue côté serveur (comme au prérendu), puis comparée mot pour mot, unité par
// unité, aux fichiers : intro et sessions du journal, brief, chaque ligne de DECISIONS.md, chaque
// entrée d'ERREURS.md (hors bloc « Format »). Les numéros des listes ordonnées rendues sont
// réinsérés (« N. ») pour attraper une ligne prise à tort pour une liste (cas « 2035. »).
// Portage de la vérification de la relecture du 2026-11-26 (docs/relectures/), pour qu'elle
// tourne en CI.
import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
import Page from '../../routes/making-of/+page.svelte';
import { FICHIERS, lireFichier, makingOf } from './makingof';

/* ---------- Un arbre HTML minimal (la sortie de Svelte est bien formée) ---------- */

interface Noeud {
  nom: string;
  attrs: Record<string, string>;
  enfants: (Noeud | string)[];
  parent: Noeud | null;
}

const VIDES = new Set(['br', 'hr', 'img', 'input', 'meta', 'link', 'wbr', 'source']);

function arbre(html: string): Noeud {
  const racine: Noeud = { nom: '#racine', attrs: {}, enfants: [], parent: null };
  let courant = racine;
  const re =
    /<!--[\s\S]*?-->|<\/([a-zA-Z0-9]+)\s*>|<([a-zA-Z0-9]+)((?:\s+[^\s=>]+(?:="[^"]*")?)*)\s*\/?>|([^<]+)/g;
  for (const m of html.matchAll(re)) {
    if (m[0].startsWith('<!--')) continue;
    if (m[1]) {
      const nom = m[1].toLowerCase();
      let n: Noeud | null = courant;
      while (n && n.nom !== nom) n = n.parent;
      if (!n?.parent) throw new Error(`balise fermante orpheline </${nom}>`);
      courant = n.parent;
    } else if (m[2]) {
      const attrs: Record<string, string> = {};
      for (const a of (m[3] ?? '').matchAll(/([^\s=]+)(?:="([^"]*)")?/g)) attrs[a[1]] = a[2] ?? '';
      const n: Noeud = { nom: m[2].toLowerCase(), attrs, enfants: [], parent: courant };
      courant.enfants.push(n);
      if (!VIDES.has(n.nom) && !m[0].endsWith('/>')) courant = n;
    } else if (m[4]) courant.enfants.push(m[4]);
  }
  return racine;
}

const classes = (n: Noeud) => (n.attrs.class ?? '').split(/\s+/);
const a = (n: Noeud, c: string) => classes(n).includes(c);

function tous(n: Noeud, test: (n: Noeud) => boolean, acc: Noeud[] = []): Noeud[] {
  for (const e of n.enfants)
    if (typeof e !== 'string') {
      if (test(e)) acc.push(e);
      tous(e, test, acc);
    }
  return acc;
}
const un = (n: Noeud, test: (n: Noeud) => boolean) => {
  const r = tous(n, test);
  expect(r, 'élément attendu une fois').toHaveLength(1);
  return r[0];
};

const ENTITES: Record<string, string> = { amp: '&', lt: '<', gt: '>', quot: '"', nbsp: ' ' };
const decoder = (t: string) =>
  t.replace(/&(#\d+|#x[0-9a-f]+|\w+);/gi, (x, e: string) =>
    e[0] === '#'
      ? String.fromCodePoint(e[1] === 'x' ? parseInt(e.slice(2), 16) : Number(e.slice(1)))
      : (ENTITES[e] ?? x)
  );

/** Texte d'un nœud : espace autour des blocs, rien autour du balisage en ligne. */
const EN_LIGNE = new Set(['strong', 'em', 'code', 'a', 'b', 'i']);
function texte(n: Noeud): string {
  let rang = 0;
  return n.enfants
    .map((e) => {
      if (typeof e === 'string') return decoder(e);
      const numero = n.nom === 'ol' && e.nom === 'li' ? `${++rang}. ` : '';
      const t = texte(e);
      return EN_LIGNE.has(e.nom) ? t : ` ${numero}${t} `;
    })
    .join('');
}

const mots = (t: string) => t.split(/[\s  ]+/).filter(Boolean);

/* ---------- Le Markdown source, débarrassé de sa syntaxe ---------- */

function texteMd(md: string): string {
  const sortie: string[] = [];
  let code = false;
  for (let l of md.split('\n')) {
    if (/^\s*(```|~~~)/.test(l)) {
      code = !code;
      continue;
    }
    if (code) {
      sortie.push(l);
      continue;
    }
    if (/^\s*---\s*$/.test(l) || /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$/.test(l)) continue;
    l = l
      .replace(/^\s{0,3}(>\s?)+/, '')
      .replace(/^\s*#{1,6}\s+/, '')
      .replace(/^(\s*)[-*+]\s+/, '$1');
    if (l.trim().startsWith('|'))
      l = l
        .trim()
        .replace(/^\||\|$/g, '')
        .replace(/\|/g, ' ');
    sortie.push(l);
  }
  return sortie
    .join('\n')
    .replace(/\[([^\]]+)\]\([^)\s]+\)/g, '$1')
    .replace(/\*\*/g, '')
    .replace(/`/g, '')
    .replace(/(^|[^*])\*([^*]+?)\*/g, '$1$2');
}

/** Compare deux suites de mots ; en cas d'écart, montre le premier mot qui diffère. */
function memesMots(nom: string, source: string, rendu: string) {
  const s = mots(source);
  const r = mots(rendu);
  let k = 0;
  while (k < s.length && s[k] === r[k]) k++;
  const contexte = (m: string[]) => m.slice(Math.max(0, k - 6), k + 6).join(' ');
  expect(
    k === s.length && k === r.length
      ? 'identiques'
      : `source « ${contexte(s)} » / rendu « ${contexte(r)} »`,
    `${nom} : premier écart au mot ${k + 1}`
  ).toBe('identiques');
  expect(s.length, nom).toBeGreaterThan(0);
}

/* ---------- Comparaisons ---------- */

describe('fidélité de la page making-of à ses fichiers source', () => {
  const { body } = render(Page, { props: { data: makingOf() } as never });
  const page = arbre(body);
  const section = (id: string) => un(page, (n) => n.nom === 'section' && n.attrs.id === id);

  it('le brief, en entier et une seule fois', () => {
    const briefs = tous(page, (n) => n.nom === 'details' && a(n, 'brief'));
    expect(briefs).toHaveLength(1);
    memesMots(
      'brief',
      texteMd(lireFichier(FICHIERS.brief)),
      texte(un(briefs[0], (n) => a(n, 'contenu')))
    );
  });

  it('le journal : intro, puis chaque session (titre, demande et détail)', () => {
    const journal = lireFichier(FICHIERS.journal);
    const lignes = journal.split('\n');
    const fin = lignes.findIndex((l) => /^(---\s*$|## )/.test(l));
    const s = section('journal');
    memesMots(
      'journal, intro',
      texteMd(lignes.slice(1, fin).join('\n')),
      texte(un(s, (n) => a(n, 'intro')))
    );

    const blocs = journal.split(/\n(?=## )/).slice(1);
    const sessions = tous(s, (n) => n.nom === 'li' && a(n, 'session'));
    expect(sessions).toHaveLength(blocs.length);
    blocs.forEach((bloc, k) => {
      const [titre, ...corps] = bloc.split('\n');
      const m = titre.match(/^## Session (\d+) — (\d{4}-\d{2}-\d{2})(?:,\s*(.+?))?\s+·\s+(.+)$/)!;
      const li = sessions[k];
      memesMots(
        `session ${m[1]}, titre`,
        `Session ${m[1]} · ${texteMd(m[4])}`,
        texte(un(li, (n) => n.nom === 'h3'))
      );
      expect(un(li, (n) => n.nom === 'time').attrs.datetime).toBe(m[2]);
      const detail = tous(li, (n) => n.nom === 'details' && !a(n, 'brief'));
      const rendu =
        texte(un(li, (n) => a(n, 'demande'))) +
        ' ' +
        detail.map((d) => texte(un(d, (n) => a(n, 'contenu')))).join(' ');
      memesMots(`session ${m[1]}, demande et détail`, texteMd(corps.join('\n')), rendu);
    });
  });

  it('les décisions : intro, puis date, décision et raisons de chaque ligne', () => {
    const lignes = lireFichier(FICHIERS.decisions).split('\n');
    const iTable = lignes.findIndex((l) => l.trim().startsWith('|'));
    const s = section('decisions');
    memesMots(
      'décisions, intro',
      texteMd(lignes.slice(1, iTable).join('\n')),
      texte(un(s, (n) => a(n, 'intro')))
    );
    const rangs = lignes.filter((l) => l.trim().startsWith('|')).slice(2);
    const fiches = tous(s, (n) => n.nom === 'li' && a(n, 'fiche'));
    expect(fiches).toHaveLength(rangs.length);
    rangs.forEach((l, k) => {
      const [date, decision, raisons] = l
        .trim()
        .replace(/^\||\|$/g, '')
        .split(/(?<!\\)\|/)
        .map((c) => c.trim());
      const f = fiches[k];
      expect(un(f, (n) => n.nom === 'time').attrs.datetime, `décision ${k + 1}`).toBe(date);
      memesMots(
        `décision ${k + 1} (${date})`,
        texteMd(decision),
        texte(un(f, (n) => a(n, 'decision')))
      );
      memesMots(
        `décision ${k + 1} (${date}), raisons`,
        'Raisons ' + texteMd(raisons),
        texte(un(f, (n) => a(n, 'raisons')))
      );
    });
  });

  it('les erreurs : intro sans le bloc « Format », puis titre et champs de chaque entrée', () => {
    const source = lireFichier(FICHIERS.erreurs);
    const lignes = source.split('\n');
    const iFormat = lignes.findIndex((l) => /^Format\s*:/.test(l));
    const s = section('erreurs');
    memesMots(
      'erreurs, intro',
      texteMd(lignes.slice(1, iFormat).join('\n')),
      texte(un(s, (n) => a(n, 'intro')))
    );
    expect(texte(s)).not.toContain('AAAA-MM-JJ');

    // Entrées : après le bloc de code du format.
    const apresFormat = source.slice(source.indexOf('```', source.indexOf('```') + 3) + 3);
    const blocs = apresFormat.split(/\n(?=### )/).slice(1);
    const fiches = tous(s, (n) => n.nom === 'li' && a(n, 'fiche'));
    expect(fiches).toHaveLength(blocs.length);
    blocs.forEach((bloc, k) => {
      const [titre, ...reste] = bloc.split('\n');
      const m = titre.match(/^### (\S+) — (.+)$/)!;
      const f = fiches[k];
      expect(un(f, (n) => n.nom === 'time').attrs.datetime).toBe(m[1]);
      memesMots(`erreur ${k + 1}, titre`, texteMd(m[2]), texte(un(f, (n) => n.nom === 'h3')));
      // « - **Faux** : texte » s'affiche en rubrique : nom du champ, puis son texte.
      const corps = reste.join('\n').replace(/^- \*\*([^*]+)\*\*\s*:\s?/gm, '$1 ');
      const rendu = tous(f, (n) => a(n, 'preambule') || a(n, 'rubriques'))
        .map(texte)
        .join(' ');
      memesMots(`erreur ${k + 1} (${m[1]})`, texteMd(corps), rendu);
    });
  });
});
