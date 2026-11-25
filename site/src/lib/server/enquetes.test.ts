import { describe, expect, it } from 'vitest';
import type { Chiffre, Chiffres } from '$lib/chiffres';
import { chargerChiffres } from './chiffres';
import {
  chargerEnquete,
  lireFrontMatter,
  metaEnquete,
  rendreCorps,
  slugsEnquetes
} from './enquetes';

const source = {
  cle: 'src',
  editeur: 'RTE',
  titre: 'Titre',
  date_publication: '2025-12-23',
  url: 'https://exemple.fr'
};
const base: Chiffre = {
  libelle: 'Conso',
  valeur: [4, 5],
  unite: 'TWh',
  grandeur: 'energie',
  periode: '2024',
  perimetre: 'sites dédiés',
  source,
  page: 'p. 27',
  citation: '« de l’ordre de 4 à 5 TWh »',
  confiance: 'B'
};
const chiffres: Chiffres = { conso: base };

describe('front matter', () => {
  it('sépare les métadonnées du corps', () => {
    const { meta, corps } = lireFrontMatter(
      '---\ntitre: Combien ?\nmise_a_jour: "2026-11-26"\n---\n\nTexte'
    );
    expect(meta).toEqual({ titre: 'Combien ?', mise_a_jour: '2026-11-26' });
    expect(corps.trim()).toBe('Texte');
  });
  it('accepte un fichier sans front matter', () => {
    expect(lireFrontMatter('Texte').meta).toEqual({});
  });
  it('refuse un front matter non fermé ou illisible', () => {
    expect(() => lireFrontMatter('---\ntitre: x\nTexte')).toThrow(/non fermé/);
    expect(() => lireFrontMatter('---\npas de deux-points\n---\n')).toThrow(/illisible/);
  });
  it('exige les champs d’une enquête', () => {
    expect(() => metaEnquete({ titre: 'x', question: 'y' }, 'z')).toThrow(/mise_a_jour/);
  });
});

describe('rendu du corps', () => {
  it('remplace {{id}} par la valeur formatée et un appel de note, avec la note en marge', () => {
    const [b] = rendreCorps('Ils ont consommé {{conso}}.', chiffres);
    expect(b.type).toBe('html');
    const html = (b as { html: string }).html;
    expect(html).toContain('<span class="chiffre">4 à 5 TWh</span>');
    expect(html).toContain('href="#note-1"');
    expect(html).toContain('<details class="notes"><summary>Note 1</summary>');
    expect(html).toContain('id="note-1"');
  });
  it('fait échouer le rendu sur un {{id}} inconnu', () => {
    expect(() => rendreCorps('Voir {{inconnu}}.', chiffres)).toThrow(/Chiffre inconnu.*inconnu/);
  });
  it('rend {{source:cle|page}} en appel de note vers la source seule', () => {
    const [b] = rendreCorps('Selon RTE {{source:src|p. 6}}.', chiffres);
    const html = (b as { html: string }).html;
    expect(html).toContain('id="note-1"');
    expect(html).toContain('p. 6');
    expect(() => rendreCorps('{{source:absente|p. 1}}', chiffres)).toThrow(/Source inconnue/);
  });
  it('accepte un jeton coupé par un retour à la ligne', () => {
    const [b] = rendreCorps('Voir {{source:src|page\nweb}}.', chiffres);
    expect((b as { html: string }).html).toContain('page web');
  });
  it('renvoie à la première note quand un chiffre revient', () => {
    const [b] = rendreCorps('{{conso}} puis {{conso}}', chiffres);
    expect((b as { html: string }).html).toContain('voir la <a href="#note-1">note 1</a>');
  });
  it('accroche les notes aux items de liste', () => {
    const [b] = rendreCorps('1. **Réservée.** {{conso}}\n2. Sans chiffre', chiffres);
    const html = (b as { html: string }).html;
    expect(html).toMatch(/^<ol><li><div class="avec-notes"><details class="notes">/);
    expect(html).toContain('<li>Sans chiffre</li>');
  });
  it('transforme ::: graphique nom ::: en bloc, et refuse un nom inconnu', () => {
    const blocs = rendreCorps('a\n\n::: graphique pyramide :::\n\nb', chiffres);
    expect(blocs.map((b) => b.type)).toEqual(['html', 'graphique', 'html']);
    expect(blocs[1]).toEqual({ type: 'graphique', nom: 'pyramide' });
    expect(() => rendreCorps('::: graphique camembert :::', chiffres)).toThrow(/Graphique inconnu/);
    expect(() => rendreCorps('::: encadre x :::', chiffres)).toThrow(/Directive inconnue/);
  });
  it('applique les espaces insécables de la ponctuation française', () => {
    const [b] = rendreCorps("Il dit : « oui » ; vraiment ? aujourd'hui", chiffres);
    expect((b as { html: string }).html).toBe(
      '<p>Il dit\u00a0: «\u00a0oui\u00a0»\u202f; vraiment\u202f? aujourd’hui</p>'
    );
  });
  it('ne rend pas le commentaire HTML de tête', () => {
    const blocs = rendreCorps('<!--\nSyntaxe : {{id}}\n-->\n\nTexte', chiffres);
    expect(blocs).toEqual([{ type: 'html', html: '<p>Texte</p>' }]);
  });
});

describe('enquêtes du dépôt', () => {
  it('rend toutes les enquêtes de docs/enquetes avec le référentiel réel', () => {
    const reel = chargerChiffres();
    const slugs = slugsEnquetes();
    expect(slugs).toContain('combien');
    for (const slug of slugs) {
      const e = chargerEnquete(slug, reel);
      const html = e.blocs.map((b) => (b.type === 'html' ? b.html : '')).join('');
      expect(html).not.toMatch(/\{\{|\}\}|<!--|:::/);
    }
  });
});
