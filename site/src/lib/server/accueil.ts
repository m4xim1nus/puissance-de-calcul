// Accueil : accroches chiffrées des enquêtes (champ `accroche` de leur front matter) et message
// principal (docs/MESSAGE.md) en trois sections. Tout est rendu au prérendu par rendreCorps, avec
// une numérotation de notes continue sur la page (ancres `note-N` uniques).
import type { Chiffres } from '$lib/chiffres';
import { typographier } from '$lib/markdown';
import { derniereNote, lireFrontMatter, metaEnquete, rendreCorps } from '$lib/server/enquetes';
import { lireFichier } from '$lib/server/makingof';

export interface Accroche {
  slug: string;
  titre: string;
  question: string;
  /** Le chiffre fort, et ce qui le précède (« Environ 50 postes »), avec son appel de note. */
  chiffre: string;
  /** Chiffre fort long (unité composée) : affiché plus petit pour tenir dans la carte. */
  long: boolean;
  /** La suite de la phrase, puis les autres phrases (HTML en ligne). */
  suite: string;
  /** Notes de l'accroche (HTML du corps des notes). */
  notes: string;
}

const RE_ENVELOPPE =
  /^<div class="avec-notes"><details class="notes"><summary>[^<]*<\/summary><div class="notes-corps">([\s\S]*)<\/div><\/details><p>([\s\S]*)<\/p><\/div>$/;

/** Un paragraphe rendu par rendreCorps : corps des notes et contenu du `<p>`. */
function paragrapheAnnote(texte: string, chiffres: Chiffres, depart: number, slug: string) {
  const blocs = rendreCorps(texte, chiffres, depart);
  const html = blocs.length === 1 && blocs[0].type === 'html' ? blocs[0].html : '';
  const m = html.match(RE_ENVELOPPE);
  if (m) return { notes: m[1], contenu: m[2], derniere: derniereNote([html]) };
  // Paragraphe sans chiffre ni source : pas d'enveloppe de notes.
  const simple = html.match(/^<p>([\s\S]*)<\/p>$/);
  if (!simple || html.includes('data-note'))
    throw new Error(`Enquête « ${slug} » : l'accroche doit tenir en un paragraphe annoté`);
  return { notes: '', contenu: simple[1], derniere: depart };
}

/**
 * Accroche d'une enquête : un seul paragraphe qui contient au moins un chiffre du référentiel.
 * Le chiffre fort de la carte est soit ce qui précède `||` (qui doit contenir un chiffre), soit,
 * sans `||`, le premier chiffre et le texte qui le précède (20 signes au plus).
 */
export function accroche(slug: string, chiffres: Chiffres, depart: number): Accroche {
  const { meta } = lireFrontMatter(lireFichier(`docs/enquetes/${slug}.md`));
  const { titre, question } = metaEnquete(meta, slug);
  const texte = meta.accroche ?? '';
  const [avant, apres] = texte.includes('||') ? texte.split('||').map((t) => t.trim()) : [];
  if (avant !== undefined) {
    if (!/\{\{[\w-]+\}\}/.test(avant) || !apres)
      throw new Error(`Enquête « ${slug} » : accroche « chiffre || suite » mal formée`);
    const fort = paragrapheAnnote(avant, chiffres, depart, slug);
    const suite = paragrapheAnnote(apres, chiffres, Math.max(depart, fort.derniere), slug);
    return {
      slug,
      titre,
      question,
      long: visible(fort.contenu).length > 12,
      chiffre: fort.contenu,
      suite: ' ' + suite.contenu,
      notes: fort.notes + suite.notes
    };
  }
  if (!/^[^{]{0,20}\{\{[\w-]+\}\}/.test(texte))
    throw new Error(
      `Enquête « ${slug} » : champ « accroche » absent, ou qui ne commence pas par un chiffre {{id}} (20 signes au plus avant)`
    );
  const { notes, contenu } = paragrapheAnnote(texte, chiffres, depart, slug);
  const fin = contenu.indexOf('</sup>') + '</sup>'.length;
  const chiffre = contenu.slice(0, fin);
  return {
    slug,
    titre,
    question,
    long: visible(chiffre).length > 12,
    chiffre,
    suite: contenu.slice(fin),
    notes
  };
}

const visible = (html: string) => html.replace(/<sup[\s\S]*?<\/sup>|<[^>]+>/g, '');

export const SECTIONS_MESSAGE = ['À retenir', 'Le message en détail', 'Ce qui a changé'] as const;

/** Une section du message en blocs HTML annotés, notes numérotées après `depart`. */
export function rendreSection(corps: string, chiffres: Chiffres, depart: number) {
  const blocs = rendreCorps(corps, chiffres, depart).map((b) => {
    if (b.type !== 'html') throw new Error('docs/MESSAGE.md : pas de graphique dans le message');
    return b.html;
  });
  return { blocs, derniere: Math.max(depart, derniereNote(blocs)) };
}

/** Message principal : front matter contrôlé, et ses trois sections, dans l'ordre, en Markdown. */
export function lireMessage() {
  const { meta, corps } = lireFrontMatter(lireFichier('docs/MESSAGE.md'));
  for (const champ of ['titre', 'mise_a_jour', 'version', 'repose_sur'])
    if (!meta[champ]) throw new Error(`docs/MESSAGE.md : champ « ${champ} » absent`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(meta.mise_a_jour))
    throw new Error("docs/MESSAGE.md : mise_a_jour n'est pas une date AAAA-MM-JJ");
  const morceaux = corps.split(/^## (.+)$/m);
  const titres = morceaux.filter((_, i) => i % 2 === 1).map((t) => t.trim());
  if (JSON.stringify(titres) !== JSON.stringify(SECTIONS_MESSAGE))
    throw new Error(
      `docs/MESSAGE.md : sections ${JSON.stringify(titres)}, attendu ${JSON.stringify(SECTIONS_MESSAGE)}`
    );
  const [retenir, detail, changements] = SECTIONS_MESSAGE.map((_, i) => morceaux[2 * i + 2]);
  return {
    titre: typographier(meta.titre),
    miseAJour: meta.mise_a_jour,
    version: meta.version,
    reposeSur: typographier(meta.repose_sur),
    retenir,
    detail,
    changements
  };
}
