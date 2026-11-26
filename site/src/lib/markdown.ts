// Markdown minimal, sans dépendance : titres, paragraphes, citations `>`, listes (imbriquées),
// tableaux, blocs de code, règles horizontales, puis **gras**, *italique*, `code` et liens
// [texte](url). Le texte est échappé avant toute balise : le résultat se rend avec {@html}.
//
// Extensions propres au site (actives seulement si l'appelant les demande) :
// - `{{expression}}` dans le texte, remplacé par le HTML que renvoie `options.jeton` ;
// - une ligne `::: nom argument :::`, renvoyée comme bloc « directive » par `markdownBlocs` ;
// - `options.envelopper`, qui reçoit le HTML d'un paragraphe ou d'un item de liste (pour y
//   accrocher des notes marginales).
// Les commentaires HTML `<!-- … -->` en début de ligne ne sont jamais rendus.

const ECHAPPE: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' };
export const echapper = (t: string) => t.replace(/[&<>"]/g, (c) => ECHAPPE[c]);

export interface OptionsMarkdown {
  /** Niveau HTML du titre Markdown de niveau 1 (défaut 1) ; les suivants suivent, plafonnés à 6. */
  niveauTitre?: number;
  /** HTML d'un jeton `{{expression}}` (l'expression est passée sans les accolades, espaces normalisés). */
  jeton?: (expression: string) => string;
  /**
   * HTML final d'un paragraphe (`p`, contenu en ligne déjà rendu, balise à fournir) ou du contenu
   * d'un item de liste (`li`, sans la balise `<li>`).
   */
  envelopper?: (html: string, contexte: 'p' | 'li') => string;
  /**
   * Typographie française : fine avant ; ! ?, insécable avant : et dans « », apostrophe courbe.
   * `'espaces'` : les espaces seulement, sans toucher aux caractères du texte (textes publiés
   * tels quels : citations, brief).
   */
  typographie?: boolean | 'espaces';
}

/**
 * Remplace les espaces ordinaires autour de la ponctuation haute par des espaces insécables et,
 * sauf `espacesSeules`, l'apostrophe droite par l'apostrophe courbe.
 */
export function typographier(t: string, espacesSeules = false): string {
  return (espacesSeules ? t : t.replace(/(\p{L})'(?=\p{L})/gu, '$1’'))
    .replace(/ ([;!?])/g, '\u202f$1')
    .replace(/ :/g, '\u00a0:')
    .replace(/« /g, '«\u00a0')
    .replace(/ »/g, '\u00a0»');
}

export type Bloc =
  | { type: 'html'; html: string }
  | { type: 'directive'; nom: string; argument: string; brut: string };

const RE_JETON = /\{\{\s*([^{}]+?)\s*\}\}/g;

/** Une ligne de texte en HTML (sans paragraphe). */
export function enLigne(texte: string, options: OptionsMarkdown = {}): string {
  // Code inline et jetons sont extraits d'abord : leur contenu ne reçoit aucune autre mise en forme.
  const reserves: string[] = [];
  const reserver = (html: string) => {
    reserves.push(html);
    return `\u0000${reserves.length - 1}\u0000`;
  };
  let t = texte.replace(/`([^`]+)`/g, (_, c: string) => reserver(`<code>${echapper(c)}</code>`));
  if (options.jeton) {
    const jeton = options.jeton;
    t = t.replace(RE_JETON, (_, e: string) => reserver(jeton(e.replace(/\s+/g, ' '))));
  }
  const echappe = echapper(t);
  return (options.typographie ? typographier(echappe, options.typographie === 'espaces') : echappe)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*]+?)\*/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t: string, url: string) =>
      /^(https?:|\/|#)/.test(url)
        ? `<a href="${url}"${url.startsWith('http') ? ' rel="external"' : ''}>${t}</a>`
        : t
    )
    .replace(/\u0000(\d+)\u0000/g, (_, i: string) => reserves[Number(i)]);
}

/** Des paragraphes (séparés par une ligne vide) en HTML. */
export function paragraphes(texte: string): string {
  return texte
    .trim()
    .split(/\n\s*\n/)
    .map((p) => `<p>${enLigne(p.replace(/[ \t]*\n[ \t]*/g, ' '))}</p>`)
    .join('');
}

/** Retire les blancs ASCII en bord de ligne, jamais les espaces insécables (U+00A0, U+202F). */
const rogner = (t: string) => t.replace(/^[ \t]+|[ \t]+$/g, '');

const RE_PUCE = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/;
const RE_TABLE_SEP = /^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$/;
const RE_DIRECTIVE = /^\s{0,3}:::\s*([\w-]+)(?:\s+(.*?))?\s*:::\s*$/;
const RE_COMMENTAIRE = /^\s{0,3}<!--/;

/** Cellules d'une ligne de tableau `| a | b |`, rognées ; un pipe échappé `\|` reste dans sa cellule. */
export const cellules = (ligne: string): string[] =>
  ligne
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split(/(?<!\\)\|/)
    .map((c) => c.trim().replace(/\\\|/g, '|'));

function tableau(lignes: string[], options: OptionsMarkdown): string {
  const aligne = cellules(lignes[1]).map((c) =>
    c.startsWith(':') && c.endsWith(':') ? 'center' : c.endsWith(':') ? 'right' : ''
  );
  const cell = (balise: string, c: string, i: number) =>
    `<${balise}${aligne[i] ? ` style="text-align:${aligne[i]}"` : ''}>${enLigne(c, options)}</${balise}>`;
  const tete = cellules(lignes[0]).map((c, i) => cell('th', c, i));
  const corps = lignes.slice(2).map(
    (l) =>
      `<tr>${cellules(l)
        .map((c, i) => cell('td', c, i))
        .join('')}</tr>`
  );
  return `<table><thead><tr>${tete.join('')}</tr></thead><tbody>${corps.join('')}</tbody></table>`;
}

/** Liste à partir de lignes[i] ; renvoie le HTML et l'indice de la première ligne non consommée. */
function liste(lignes: string[], debut: number, options: OptionsMarkdown): [string, number] {
  const indent = (l: string) => l.match(/^\s*/)![0].replace(/\t/g, '    ').length;
  const base = indent(lignes[debut]);
  const ordonnee = /\d/.test(lignes[debut].match(RE_PUCE)![2]);
  const items: string[] = [];
  let i = debut;
  while (i < lignes.length) {
    const m = lignes[i].match(RE_PUCE);
    if (!m || indent(lignes[i]) !== base) break;
    let texte = m[3];
    i++;
    let sous = '';
    while (i < lignes.length && lignes[i].trim() !== '') {
      const mm = lignes[i].match(RE_PUCE);
      if (mm && indent(lignes[i]) > base) {
        const [html, suite] = liste(lignes, i, options);
        sous += html;
        i = suite;
      } else if (mm) {
        break;
      } else {
        texte += ' ' + rogner(lignes[i]); // ligne de continuation
        i++;
      }
    }
    const contenu = enLigne(texte, options);
    items.push(
      `<li>${options.envelopper ? options.envelopper(contenu, 'li') : contenu}${sous}</li>`
    );
  }
  const balise = ordonnee ? 'ol' : 'ul';
  return [`<${balise}>${items.join('')}</${balise}>`, i];
}

/** Un document Markdown en blocs de premier niveau : HTML ou directive `::: nom argument :::`. */
export function markdownBlocs(texte: string, options: OptionsMarkdown = {}): Bloc[] {
  const decalage = (options.niveauTitre ?? 1) - 1;
  const lignes = texte.replace(/\r\n?/g, '\n').split('\n');
  const blocs: Bloc[] = [];
  const html = (h: string) => blocs.push({ type: 'html', html: h });
  let i = 0;
  while (i < lignes.length) {
    const l = lignes[i];
    if (l.trim() === '') {
      i++;
    } else if (RE_COMMENTAIRE.test(l)) {
      // Commentaire HTML : sauté jusqu'à sa fermeture (incluse), jamais rendu.
      while (i < lignes.length && !lignes[i].includes('-->')) i++;
      i++;
    } else if (RE_DIRECTIVE.test(l)) {
      const m = l.match(RE_DIRECTIVE)!;
      blocs.push({ type: 'directive', nom: m[1], argument: (m[2] ?? '').trim(), brut: l.trim() });
      i++;
    } else if (/^\s*(```|~~~)/.test(l)) {
      const cloture = l.trim().slice(0, 3);
      const lang = l.trim().slice(3).trim();
      const code: string[] = [];
      i++;
      while (i < lignes.length && !lignes[i].trim().startsWith(cloture)) code.push(lignes[i++]);
      i++;
      const classe = /^[\w-]+$/.test(lang) ? ` class="langage-${lang}"` : '';
      html(`<pre><code${classe}>${echapper(code.join('\n'))}</code></pre>`);
    } else if (/^\s{0,3}#{1,6}\s/.test(l)) {
      const m = l.trim().match(/^(#{1,6})\s+(.*?)\s*#*$/)!;
      const n = Math.min(6, m[1].length + decalage);
      html(`<h${n}>${enLigne(m[2], options)}</h${n}>`);
      i++;
    } else if (/^\s{0,3}([-*_])(\s*\1){2,}\s*$/.test(l)) {
      html('<hr />');
      i++;
    } else if (/^\s{0,3}>/.test(l)) {
      const citation: string[] = [];
      while (i < lignes.length && /^\s{0,3}>/.test(lignes[i]))
        citation.push(lignes[i++].replace(/^\s{0,3}>\s?/, ''));
      html(`<blockquote>${markdown(citation.join('\n'), options)}</blockquote>`);
    } else if (l.includes('|') && i + 1 < lignes.length && RE_TABLE_SEP.test(lignes[i + 1])) {
      const bloc = [l, lignes[i + 1]];
      i += 2;
      while (i < lignes.length && lignes[i].trim() !== '' && lignes[i].includes('|'))
        bloc.push(lignes[i++]);
      html(tableau(bloc, options));
    } else if (RE_PUCE.test(l)) {
      const [h, suite] = liste(lignes, i, options);
      html(h);
      i = suite;
    } else {
      const para: string[] = [];
      while (
        i < lignes.length &&
        lignes[i].trim() !== '' &&
        !/^\s*(```|~~~)/.test(lignes[i]) &&
        !/^\s{0,3}(#{1,6}\s|>)/.test(lignes[i]) &&
        !RE_PUCE.test(lignes[i]) &&
        !RE_DIRECTIVE.test(lignes[i]) &&
        !RE_COMMENTAIRE.test(lignes[i])
      )
        para.push(rogner(lignes[i++]));
      const contenu = enLigne(para.join(' '), options);
      html(options.envelopper ? options.envelopper(contenu, 'p') : `<p>${contenu}</p>`);
    }
  }
  return blocs;
}

/** Un document Markdown en HTML ; une directive, sans rendu propre ici, reste du texte. */
export function markdown(texte: string, options: OptionsMarkdown = {}): string {
  return markdownBlocs(texte, options)
    .map((b) => (b.type === 'directive' ? `<p>${echapper(b.brut)}</p>` : b.html))
    .join('\n');
}
