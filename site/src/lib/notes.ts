// Notes marginales : un appel numéroté dans le texte, une note générée depuis l'entrée du
// référentiel (jamais de chiffre ni de source tapés à la main). Sorties en HTML, rendues avec {@html}.
import { COTES, type Chiffre, type Source } from '$lib/chiffres';
import {
  formaterDate,
  formaterNombre,
  formaterPeriode,
  formaterValeur,
  separateurUnite
} from '$lib/format';
import { echapper } from '$lib/markdown';

/** Appel de note dans le texte. */
export function appel(numero: number): string {
  return (
    `<sup class="appel"><a href="#note-${numero}" id="appel-${numero}" data-note="${numero}"` +
    ` aria-label="note ${numero}">${numero}</a></sup>`
  );
}

/** Date de publication d'une source ; au mois seulement quand la source dit qu'elle est approchée. */
export function dateSource(s: Source, court = false): string {
  const auMois = /approch[ée]e au mois/.test(s.note ?? '');
  return formaterDate(auMois ? s.date_publication.slice(0, 7) : s.date_publication, court);
}

/** Titre court d'une source : avant « — » ou « ( », puis coupé à environ 40 caractères. */
export function titreCourt(titre: string, max = 40): string {
  let t = titre.split(/ — | \(/)[0].trim();
  if (t.length > max) {
    const coupe = t.slice(0, max + 1);
    t = coupe.slice(0, coupe.lastIndexOf(' ')).replace(/[\s,;:]+$/, '') + '…';
  }
  return t;
}

function lienSource(s: Source, court = false): string {
  const titre = court ? titreCourt(s.titre) : s.titre;
  const complet = court && titre !== s.titre ? ` title="${echapper(s.titre)}"` : '';
  return `<a href="${echapper(s.url)}" rel="external"${complet}>${echapper(titre)}</a>`;
}

/** « RTE, Titre court (lien), mars 2026, p. 18 » */
function referenceSource(s: Source, page: string | undefined, court = true): string {
  const morceaux = [echapper(s.editeur), lienSource(s, court), dateSource(s, true)];
  if (page) morceaux.push(echapper(page));
  return `<span class="note-source">${morceaux.join(', ')}</span>`;
}

/** Consultation et remarque sur la source. */
function apropos(s: Source): string {
  let html = '';
  if (s.consulte_le) html += `Consulté le ${formaterDate(s.consulte_le)}.`;
  if (s.note) html += ` Sur la source : ${echapper(s.note)}.`;
  return html ? `<p class="note-secondaire">${html.trim()}</p>` : '';
}

const majuscule = (t: string) => t.charAt(0).toUpperCase() + t.slice(1);

/** Pastille de confiance : une lettre, avec sa légende pour les lecteurs d'écran et au survol. */
export function pastille(c: Chiffre['confiance']): string {
  const legende = `Confiance ${c} : ${COTES[c]}`;
  return (
    `<a class="cote" href="/methode#confiance" title="${legende}">` +
    `<span aria-hidden="true">${c}</span><span class="lecteur">${legende}</span></a>`
  );
}

/** Mention de la cote de confiance avec sa légende en clair. */
export function cote(c: Chiffre['confiance']): string {
  return `<a href="/methode#confiance">Confiance ${c}</a> : ${COTES[c]}.`;
}

/** Recoupements d'un chiffre, ou « Non recoupé ». */
function recoupements(c: Chiffre, sources: ReadonlyMap<string, Source>): string[] {
  if (!c.recoupements?.length) return [`<p>Non recoupé.</p>`];
  return c.recoupements.map((r) => {
    const s = sources.get(r.source);
    const qui = s ? ` (${echapper(s.editeur)}, ${echapper(s.titre)})` : '';
    const nature = r.independant ? 'Recoupement indépendant' : 'Recoupement non indépendant';
    const note = r.note ? ` ; ${echapper(r.note)}` : '';
    return `<p>${nature}${qui} : ${echapper(r.valeur)}${note}.</p>`;
  });
}

/**
 * Note d'un chiffre du référentiel. Visible, en une ou deux lignes : numéro, éditeur, titre court
 * (lien), date, page, pastille de confiance, et « calcul du site » s'il y a lieu. Dans le repli :
 * titre complet, citation exacte, période, périmètre, valeur exacte, calcul, remarque,
 * recoupements, cote en clair, consultation. Rien n'est perdu, tout est à un clic.
 */
export function noteChiffre(
  numero: number | null,
  c: Chiffre,
  sources: ReadonlyMap<string, Source> = new Map()
): string {
  if (c.produit_par) return noteCalcul(numero, c, sources);
  const exacte = c.citation.trim().startsWith('«');
  const tete =
    `<span class="note-tete">${numero === null ? '' : `<span class="note-num">${numero}</span> `}` +
    `${referenceSource(c.source, c.page)} ${pastille(c.confiance)}` +
    (c.calcul ? ` · <strong class="note-calcul">calcul du site</strong>` : '') +
    `</span>`;
  const detail = [
    `<p><span class="note-cle">Source</span> ${echapper(c.source.editeur)}, ${lienSource(c.source)}.</p>`,
    `<p class="note-citation"><span class="note-cle">${exacte ? 'Citation' : 'Dans la source'}</span> ${echapper(c.citation)}</p>`,
    `<p><span class="note-cle">Période</span> ${echapper(formaterPeriode(c.periode))}.</p>`,
    `<p><span class="note-cle">Périmètre</span> ${echapper(c.perimetre)}.</p>`,
    `<p><span class="note-cle">Valeur exacte</span> ${echapper(formaterValeur(c.valeur, c.unite))} (${echapper(c.libelle.charAt(0).toLowerCase() + c.libelle.slice(1))}).</p>`
  ];
  if (c.calcul)
    detail.push(`<p><span class="note-cle">Calcul du site</span> ${echapper(c.calcul)}.</p>`);
  if (c.note) detail.push(`<p>${echapper(majuscule(c.note))}.</p>`);
  detail.push(...recoupements(c, sources));
  detail.push(`<p>${cote(c.confiance)}</p>`);
  detail.push(apropos(c.source));
  return (
    `<div class="note"${numero === null ? '' : ` id="note-${numero}"`}>${tete} ` +
    `<details class="note-plus"><summary>détails</summary>` +
    `<div class="note-detail">${detail.join('')}</div></details></div>`
  );
}

/** Note d'un renvoi à une source, sans chiffre. */
export function noteSource(numero: number, s: Source, page?: string): string {
  const detail = `<p>${echapper(s.editeur)}, ${lienSource(s)}.</p>${apropos(s)}`;
  return (
    `<div class="note" id="note-${numero}"><span class="note-tete"><span class="note-num">${numero}</span> ` +
    `${referenceSource(s, page)}</span> <details class="note-plus"><summary>détails</summary>` +
    `<div class="note-detail">${detail}</div></details></div>`
  );
}

/** Note brève pour un chiffre déjà annoté plus haut dans la page. */
export function noteRenvoi(numero: number, premiere: number): string {
  return (
    `<div class="note note-renvoi" id="note-${numero}"><span class="note-tete">` +
    `<span class="note-num">${numero}</span> Même chiffre : voir la ` +
    `<a href="#note-${premiere}">note ${premiere}</a>.</span></div>`
  );
}

/**
 * Note d'un chiffre calculé par le site (`produit_par`) : pas de page de source à citer, mais la
 * méthode et les données. Visible : numéro, « calcul du site », période, pastille. Dans le repli :
 * méthode, données (avec lien), champ lu, période, périmètre, valeur avant arrondi, remarque,
 * contrôle, cote, date du calcul.
 */
export function noteCalcul(
  numero: number | null,
  c: Chiffre,
  sources: ReadonlyMap<string, Source> = new Map()
): string {
  if (!c.calcul) throw new Error(`Chiffre calculé sans méthode (« calcul ») : ${c.libelle}`);
  const tete =
    `<span class="note-tete">${numero === null ? '' : `<span class="note-num">${numero}</span> `}` +
    `<strong class="note-calcul">Calcul du site</strong>, ${echapper(formaterPeriode(c.periode, true))} ` +
    `${pastille(c.confiance)}</span>`;
  const exacte =
    c.valeur_calculee !== undefined
      ? `${formaterNombre(c.valeur_calculee, 6)}${separateurUnite(c.unite)}${c.unite}, affiché arrondi${c.precision !== undefined ? ` au pas de ${formaterValeur(c.precision, c.unite)}` : ''}`
      : formaterValeur(c.valeur, c.unite);
  const detail = [
    `<p><span class="note-cle">Méthode</span> ${echapper(c.calcul)}.</p>`,
    `<p><span class="note-cle">Données</span> ${lienSource(c.source)}.</p>`,
    `<p><span class="note-cle">Champ</span> ${echapper(c.citation)}.</p>`,
    `<p><span class="note-cle">Période</span> ${echapper(formaterPeriode(c.periode))}.</p>`,
    `<p><span class="note-cle">Périmètre</span> ${echapper(c.perimetre)}.</p>`,
    `<p><span class="note-cle">Valeur exacte</span> ${echapper(exacte)} (${echapper(c.libelle.charAt(0).toLowerCase() + c.libelle.slice(1))}).</p>`
  ];
  if (c.note) detail.push(`<p>${echapper(majuscule(c.note))}.</p>`);
  detail.push(
    `<p>Produit par <code>${echapper(c.produit_par ?? '')}</code>` +
      (c.verification ? `, contrôlé par <code>${echapper(c.verification)}</code>` : '') +
      `.</p>`
  );
  detail.push(...recoupements(c, sources));
  detail.push(`<p>${cote(c.confiance)}</p>`);
  detail.push(apropos(c.source));
  return (
    `<div class="note note-calculee"${numero === null ? '' : ` id="note-${numero}"`}>${tete} ` +
    `<details class="note-plus"><summary>méthode et données</summary>` +
    `<div class="note-detail">${detail.join('')}</div></details></div>`
  );
}
