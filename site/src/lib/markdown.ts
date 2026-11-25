// Markdown minimal, sans dépendance : titres, paragraphes, citations `>`, listes (imbriquées),
// tableaux, blocs de code, règles horizontales, puis **gras**, *italique*, `code` et liens
// [texte](url). Le texte est échappé avant toute balise : le résultat se rend avec {@html}.

const ECHAPPE: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' };
const echapper = (t: string) => t.replace(/[&<>"]/g, (c) => ECHAPPE[c]);

/** Une ligne de texte en HTML (sans paragraphe). */
export function enLigne(texte: string): string {
  // Le code inline est extrait d'abord : son contenu ne reçoit aucune autre mise en forme.
  const codes: string[] = [];
  const sansCode = texte.replace(/`([^`]+)`/g, (_, c: string) => {
    codes.push(`<code>${echapper(c)}</code>`);
    return `\u0000${codes.length - 1}\u0000`;
  });
  return echapper(sansCode)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*]+?)\*/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t: string, url: string) =>
      /^(https?:|\/|#)/.test(url)
        ? `<a href="${url}"${url.startsWith('http') ? ' rel="external"' : ''}>${t}</a>`
        : t
    )
    .replace(/\u0000(\d+)\u0000/g, (_, i: string) => codes[Number(i)]);
}

/** Des paragraphes (séparés par une ligne vide) en HTML. */
export function paragraphes(texte: string): string {
  return texte
    .trim()
    .split(/\n\s*\n/)
    .map((p) => `<p>${enLigne(p.replace(/\s*\n\s*/g, ' '))}</p>`)
    .join('');
}

export interface OptionsMarkdown {
  /** Niveau HTML du titre Markdown de niveau 1 (défaut 1) ; les suivants suivent, plafonnés à 6. */
  niveauTitre?: number;
}

const RE_PUCE = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/;
const RE_TABLE_SEP = /^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$/;

const cellules = (ligne: string): string[] =>
  ligne
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split(/(?<!\\)\|/)
    .map((c) => c.trim().replace(/\\\|/g, '|'));

function tableau(lignes: string[]): string {
  const aligne = cellules(lignes[1]).map((c) =>
    c.startsWith(':') && c.endsWith(':') ? 'center' : c.endsWith(':') ? 'right' : ''
  );
  const cell = (balise: string, c: string, i: number) =>
    `<${balise}${aligne[i] ? ` style="text-align:${aligne[i]}"` : ''}>${enLigne(c)}</${balise}>`;
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
function liste(lignes: string[], debut: number): [string, number] {
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
        const [html, suite] = liste(lignes, i);
        sous += html;
        i = suite;
      } else if (mm) {
        break;
      } else {
        texte += ' ' + lignes[i].trim(); // ligne de continuation
        i++;
      }
    }
    items.push(`<li>${enLigne(texte)}${sous}</li>`);
  }
  const balise = ordonnee ? 'ol' : 'ul';
  return [`<${balise}>${items.join('')}</${balise}>`, i];
}

/** Un document Markdown en HTML. */
export function markdown(texte: string, options: OptionsMarkdown = {}): string {
  const decalage = (options.niveauTitre ?? 1) - 1;
  const lignes = texte.replace(/\r\n?/g, '\n').split('\n');
  const html: string[] = [];
  let i = 0;
  while (i < lignes.length) {
    const l = lignes[i];
    if (l.trim() === '') {
      i++;
    } else if (/^\s*(```|~~~)/.test(l)) {
      const cloture = l.trim().slice(0, 3);
      const lang = l.trim().slice(3).trim();
      const code: string[] = [];
      i++;
      while (i < lignes.length && !lignes[i].trim().startsWith(cloture)) code.push(lignes[i++]);
      i++;
      const classe = /^[\w-]+$/.test(lang) ? ` class="langage-${lang}"` : '';
      html.push(`<pre><code${classe}>${echapper(code.join('\n'))}</code></pre>`);
    } else if (/^\s{0,3}#{1,6}\s/.test(l)) {
      const m = l.trim().match(/^(#{1,6})\s+(.*?)\s*#*$/)!;
      const n = Math.min(6, m[1].length + decalage);
      html.push(`<h${n}>${enLigne(m[2])}</h${n}>`);
      i++;
    } else if (/^\s{0,3}([-*_])(\s*\1){2,}\s*$/.test(l)) {
      html.push('<hr />');
      i++;
    } else if (/^\s{0,3}>/.test(l)) {
      const citation: string[] = [];
      while (i < lignes.length && /^\s{0,3}>/.test(lignes[i]))
        citation.push(lignes[i++].replace(/^\s{0,3}>\s?/, ''));
      html.push(`<blockquote>${markdown(citation.join('\n'), options)}</blockquote>`);
    } else if (l.includes('|') && i + 1 < lignes.length && RE_TABLE_SEP.test(lignes[i + 1])) {
      const bloc = [l, lignes[i + 1]];
      i += 2;
      while (i < lignes.length && lignes[i].trim() !== '' && lignes[i].includes('|'))
        bloc.push(lignes[i++]);
      html.push(tableau(bloc));
    } else if (RE_PUCE.test(l)) {
      const [h, suite] = liste(lignes, i);
      html.push(h);
      i = suite;
    } else {
      const para: string[] = [];
      while (
        i < lignes.length &&
        lignes[i].trim() !== '' &&
        !/^\s*(```|~~~)/.test(lignes[i]) &&
        !/^\s{0,3}(#{1,6}\s|>)/.test(lignes[i]) &&
        !RE_PUCE.test(lignes[i])
      )
        para.push(lignes[i++].trim());
      html.push(`<p>${enLigne(para.join(' '))}</p>`);
    }
  }
  return html.join('\n');
}
