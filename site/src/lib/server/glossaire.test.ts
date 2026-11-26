import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import { enLigne } from '$lib/markdown';
import { inclureFragments, lireFrontMatter, rendreCorps } from './enquetes';
import {
  chargerGlossaire,
  lireGlossaire,
  phrases,
  rendreGlossaire,
  resolveurGlossaire,
  RE_RENVOI
} from './glossaire';
import { RACINE } from './makingof';

const lire = (chemin: string) => readFileSync(resolve(RACINE, chemin), 'utf8');
const md = (dossier: string) =>
  readdirSync(resolve(RACINE, dossier))
    .filter((f) => f.endsWith('.md'))
    .map((f) => `${dossier}/${f}`);

const entree = (terme: string, id: string, definition: string, source = '') =>
  `## ${terme} {#${id}}\n\n${definition}\n${source ? `\n${source}\n` : ''}`;
const fichier = (...entrees: string[]) =>
  `---\ntitre: Glossaire\nmise_a_jour: 2026-11-26\n---\n\n<!-- format -->\n\n${entrees.join('\n')}`;
const DEUX = 'Une phrase. Une autre phrase.';

describe('format du glossaire', () => {
  it('lit terme, identifiant, définition et source', () => {
    const [e] = lireGlossaire(
      fichier(entree('Terme', 'terme', DEUX, 'Source : [Texte](https://exemple.fr), p. 2.'))
    );
    expect(e).toEqual({
      id: 'terme',
      terme: 'Terme',
      definition: DEUX,
      source: '[Texte](https://exemple.fr), p. 2.'
    });
  });
  it('compte les phrases sans couper « p. 30 » ni un lien', () => {
    expect(phrases('Voir p. 30 du rapport. Puis [le texte](https://x.fr/A.Pdf).')).toBe(2);
    expect(phrases('Une seule (UE) 2024/1106.')).toBe(1);
  });
  it('refuse les entorses au format', () => {
    const refus = (texte: string, motif: RegExp) =>
      expect(() => lireGlossaire(texte)).toThrow(motif);
    refus(fichier('## Terme sans identifiant\n\n' + DEUX), /titre illisible/);
    refus(fichier(entree('A', 'a', DEUX), entree('B', 'a', DEUX)), /en double/);
    refus(fichier(entree('A', 'a', 'Une seule phrase.')), /1 phrase/);
    refus(fichier(entree('A', 'a', 'Un. Deux. Trois. Quatre. Cinq. Six.')), /6 phrase/);
    refus(fichier(entree('B', 'b', DEUX), entree('A', 'a', DEUX)), /ordre alphabétique/);
    refus(fichier(entree('A', 'a', 'Voir [B](glossaire:b). Fin.')), /renvoi vers « b »/);
    refus(fichier(entree('A', 'a', DEUX, 'Source : RTE, p. 2.')), /lien https/);
    refus(fichier(entree('A', 'a', 'Vaut {{x}}. Fin.')), /référentiel/);
    refus(fichier(entree('A', 'a', DEUX + '\n\nSecond paragraphe. Fin.')), /un seul paragraphe/);
    refus('pas de front matter', /front matter/);
  });
});

describe('glossaire du dépôt (docs/GLOSSAIRE.md)', () => {
  const entrees = chargerGlossaire();
  const ids = new Set(entrees.map((e) => e.id));

  it('compte de 20 à 40 entrées, dont les termes demandés', () => {
    expect(entrees.length).toBeGreaterThanOrEqual(20);
    expect(entrees.length).toBeLessThanOrEqual(40);
    for (const id of [
      'merit-order',
      'capture-price',
      'ppa',
      'turpe',
      'cfe-24-7',
      'prix-de-gros',
      'day-ahead',
      'prix-negatif',
      'poste-electrique',
      'remit',
      'services-systeme',
      'mecanisme-capacite',
      'plages-pp',
      'solde-echanges',
      'mw-mwh',
      'facteur-moyen-marginal'
    ])
      expect(ids, id).toContain(id);
  });

  it('se rend en HTML, avec une ancre par terme et des renvois internes à la page', () => {
    const rendu = rendreGlossaire();
    expect(rendu).toHaveLength(entrees.length);
    const pp = rendu.find((e) => e.id === 'mecanisme-capacite')!;
    expect(pp.definition).toContain('<a class="glossaire" href="#g-plages-pp">');
    expect(rendu.every((e) => !e.definition.includes('glossaire:'))).toBe(true);
  });
});

/* ---------- Renvois depuis les pages ---------- */

/** Sources Markdown de chaque page qui en a, fragments partagés inclus. */
function pagesMarkdown(): Record<string, string> {
  const pages: Record<string, string> = { '/': lire('docs/MESSAGE.md') };
  for (const f of md('docs/enquetes')) {
    const slug = f.split('/').pop()!.slice(0, -3);
    // L'accroche du front matter est rendue sur l'accueil, pas sur la page de l'enquête.
    const { meta, corps } = lireFrontMatter(lire(f));
    pages[`/${slug}`] = inclureFragments(corps);
    if (meta.accroche) pages['/'] += `\n${meta.accroche}`;
  }
  pages['/simulateur'] =
    inclureFragments(lire('site/src/lib/simulateur/en-tete.md')) +
    '\n' +
    inclureFragments(lire('site/src/lib/simulateur/lecture.md'));
  return pages;
}

/** Liens écrits en dur dans les composants : href="/methode#g-id". */
function liensSvelte(): { fichier: string; id: string }[] {
  const liens: { fichier: string; id: string }[] = [];
  const parcourir = (dossier: string) => {
    for (const d of readdirSync(resolve(RACINE, dossier), { withFileTypes: true })) {
      const chemin = `${dossier}/${d.name}`;
      if (d.isDirectory()) parcourir(chemin);
      else if (d.name.endsWith('.svelte'))
        for (const [, id] of lire(chemin).matchAll(/\/methode#g-([^"'\s)]*)/g))
          liens.push({ fichier: chemin, id });
    }
  };
  parcourir('site/src');
  return liens;
}

const renvois = (texte: string) => [...texte.matchAll(RE_RENVOI)].map((m) => m[1]);

describe('renvois au glossaire depuis les pages', () => {
  const ids = new Set(chargerGlossaire().map((e) => e.id));

  it('chaque renvoi [texte](glossaire:id) des textes du site vise une entrée existante', () => {
    const fichiers = [
      'docs/MESSAGE.md',
      ...md('docs/enquetes'),
      ...md('docs/enquetes/partage'),
      ...md('site/src/lib/simulateur')
    ];
    for (const f of fichiers)
      for (const id of renvois(lire(f))) expect(ids, `${f} : glossaire:${id}`).toContain(id);
  });

  it('chaque lien /methode#g-id écrit dans un composant vise une entrée existante', () => {
    const liens = liensSvelte();
    expect(liens.length).toBeGreaterThan(0);
    for (const { fichier, id } of liens) expect(ids, `${fichier} : #g-${id}`).toContain(id);
  });

  it('un terme n’est lié qu’une fois par page (première occurrence)', () => {
    const pages = pagesMarkdown();
    for (const { fichier, id } of liensSvelte())
      if (fichier === 'site/src/routes/+page.svelte') pages['/'] += `](glossaire:${id})`;
    for (const [page, texte] of Object.entries(pages)) {
      const vus = renvois(texte);
      const doubles = vus.filter((id, k) => vus.indexOf(id) !== k);
      expect(doubles, `${page} : liés plusieurs fois`).toEqual([]);
    }
  });

  it('les fragments partagés ne portent pas de renvoi (ils vivent dans deux pages)', () => {
    for (const f of md('docs/enquetes/partage')) expect(renvois(lire(f)), f).toEqual([]);
  });

  it('un identifiant inconnu fait échouer le rendu', () => {
    expect(() => rendreCorps('Voir le [merit order](glossaire:inconnu).', {})).toThrow(
      /glossaire:inconnu/
    );
    const [b] = rendreCorps('Voir le [prix](glossaire:day-ahead).', {});
    expect((b as { html: string }).html).toContain(
      '<a class="glossaire" href="/methode#g-day-ahead">prix</a>'
    );
  });

  it('le résolveur refuse un identifiant absent, et le Markdown sans résolveur garde le texte', () => {
    expect(() => resolveurGlossaire()('nimporte-quoi')).toThrow(/inconnu/);
    expect(enLigne('[prix](glossaire:day-ahead)')).toBe('prix');
  });
});
