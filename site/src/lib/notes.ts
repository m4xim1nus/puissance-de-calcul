// Notes marginales : un appel numéroté dans le texte, une note générée depuis l'entrée du
// référentiel (jamais de chiffre ni de source tapés à la main). Sorties en HTML, rendues avec {@html}.
import { COTES, type Chiffre, type Source } from '$lib/chiffres';
import { formaterDate, formaterPeriode, formaterValeur } from '$lib/format';
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

function lienSource(s: Source): string {
  return `<a href="${echapper(s.url)}" rel="external">${echapper(s.titre)}</a>`;
}

/** « RTE, Titre (lien), 23 déc. 2025, p. 18. » */
function referenceSource(s: Source, page: string | undefined): string {
  const morceaux = [echapper(s.editeur), lienSource(s), dateSource(s, true)];
  if (page) morceaux.push(echapper(page));
  return `<span class="note-source">${morceaux.join(', ')}.</span>`;
}

/** Consultation et remarque sur la source. */
function apropos(s: Source): string {
  let html = '';
  if (s.consulte_le) html += `Consulté le ${formaterDate(s.consulte_le)}.`;
  if (s.note) html += ` Sur la source : ${echapper(s.note)}.`;
  return html ? `<p class="note-secondaire">${html.trim()}</p>` : '';
}

const majuscule = (t: string) => t.charAt(0).toUpperCase() + t.slice(1);

/** Mention lisible de la cote de confiance, avec sa légende en clair (pas seulement une lettre). */
export function cote(c: Chiffre['confiance']): string {
  return (
    `<span class="cote" aria-hidden="true">${c}</span> ` +
    `<a href="/methode#confiance">Confiance ${c}</a> : ${COTES[c]}.`
  );
}

/**
 * Note d'un chiffre du référentiel. Visible : source (éditeur, titre et lien, date, page),
 * citation, période, mention du calcul, cote. Dans un repli : périmètre, calcul détaillé,
 * remarque, recoupements, consultation (une note complète dans la marge serait plus longue que
 * le paragraphe qu'elle annote).
 */
export function noteChiffre(
  numero: number,
  c: Chiffre,
  sources: ReadonlyMap<string, Source> = new Map()
): string {
  const exacte = c.citation.trim().startsWith('«');
  const visible = [
    `<p class="note-tete"><span class="note-num">${numero}</span> ${referenceSource(c.source, c.page)}</p>`,
    `<p class="note-citation"><span class="lecteur">${exacte ? 'Citation' : 'Dans la source'} : </span>${echapper(c.citation)}</p>`,
    `<p class="note-cote"><span class="note-cle">Période</span> ${echapper(formaterPeriode(c.periode))}` +
      (c.calcul ? ` · <strong>calcul du site</strong>` : '') +
      ` · ${cote(c.confiance)}</p>`
  ];
  const detail = [
    `<p><span class="note-cle">Périmètre</span> ${echapper(c.perimetre)}.</p>`,
    `<p><span class="note-cle">Valeur</span> ${echapper(formaterValeur(c.valeur, c.unite))} (${echapper(c.libelle.charAt(0).toLowerCase() + c.libelle.slice(1))}).</p>`
  ];
  if (c.calcul)
    detail.push(`<p><span class="note-cle">Calcul du site</span> ${echapper(c.calcul)}.</p>`);
  if (c.note) detail.push(`<p>${echapper(majuscule(c.note))}.</p>`);
  if (c.recoupements?.length) {
    for (const r of c.recoupements) {
      const s = sources.get(r.source);
      const qui = s ? ` (${echapper(s.editeur)}, ${echapper(s.titre)})` : '';
      const nature = r.independant ? 'Recoupement indépendant' : 'Recoupement non indépendant';
      const note = r.note ? ` ; ${echapper(r.note)}` : '';
      detail.push(`<p>${nature}${qui} : ${echapper(r.valeur)}${note}.</p>`);
    }
  } else {
    detail.push(`<p>Non recoupé.</p>`);
  }
  detail.push(apropos(c.source));
  const plus = c.calcul ? 'Périmètre, calcul, recoupement' : 'Périmètre, recoupement';
  return (
    `<div class="note" id="note-${numero}">${visible.join('')}` +
    `<details class="note-plus"><summary>${plus}</summary>${detail.join('')}</details></div>`
  );
}

/** Note d'un renvoi à une source, sans chiffre. */
export function noteSource(numero: number, s: Source, page?: string): string {
  return (
    `<div class="note" id="note-${numero}"><p class="note-tete"><span class="note-num">${numero}</span> ` +
    `${referenceSource(s, page)}</p>${apropos(s)}</div>`
  );
}

/** Note brève pour un chiffre déjà annoté plus haut dans la page. */
export function noteRenvoi(numero: number, c: Chiffre, premiere: number): string {
  return (
    `<div class="note note-renvoi" id="note-${numero}"><p class="note-tete">` +
    `<span class="note-num">${numero}</span> <span class="note-libelle">${echapper(c.libelle)}</span> : ` +
    `<span class="note-valeur">${echapper(formaterValeur(c.valeur, c.unite))}</span>, voir la ` +
    `<a href="#note-${premiere}">note ${premiere}</a>.</p></div>`
  );
}
