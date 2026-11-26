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
  it('arrondit l’affichage à 3 chiffres significatifs, la note gardant la valeur exacte', () => {
    const exact: Chiffres = { x: { ...base, valeur: 36.73 } };
    const [b] = rendreCorps('{{x}}', exact);
    const html = (b as { html: string }).html;
    expect(html).toContain('<span class="chiffre">36,7\u202fTWh</span>');
    expect(html).toContain('36,73\u202fTWh');
  });
  it('garde les espaces fines insécables tapées dans le texte, y compris en bord de ligne', () => {
    const [b] = rendreCorps('les 8\u202f760 heures et 1\u202f%\u202f\nde plus', chiffres);
    expect((b as { html: string }).html).toBe(
      '<p>les 8\u202f760 heures et 1\u202f%\u202f de plus</p>'
    );
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
  it('refuse une ligne qui commence par une année suivie d’un point (liste involontaire)', () => {
    expect(() => rendreCorps('atteint 21 TWh en\n2035. En décarbonation rapide', chiffres)).toThrow(
      /Ligne 2.*2035/
    );
    expect(() => rendreCorps('1. une liste voulue\n2. suite', chiffres)).not.toThrow();
    expect(() => rendreCorps('en\n2035\\. suite', chiffres)).not.toThrow();
    expect(() => rendreCorps('```\n2035. dans du code\n```', chiffres)).not.toThrow();
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
      // Une seule liste numérotée voulue au plus par enquête (la pyramide), jamais une liste
      // ouverte par une année.
      expect(html).not.toMatch(/<ol><li>[^<]*(En|en) décarbonation/);
    }
  });
});

describe('fragments partagés (::: inclure nom :::)', () => {
  it('remplace la ligne par le fragment, et refuse un fragment inconnu', async () => {
    const { mkdtempSync, writeFileSync } = await import('node:fs');
    const { tmpdir } = await import('node:os');
    const { join } = await import('node:path');
    const { inclureFragments } = await import('./enquetes');
    const d = mkdtempSync(join(tmpdir(), 'fragments-'));
    writeFileSync(join(d, 'essai.md'), '- **Essai.** {{conso}}\n  suite\n');
    expect(inclureFragments('- a\n- ::: inclure essai :::\n- b', d)).toBe(
      '- a\n- **Essai.** {{conso}}\n  suite\n- b'
    );
    expect(inclureFragments('::: inclure essai :::', d)).toBe('- **Essai.** {{conso}}\n  suite');
    expect(() => inclureFragments('::: inclure absent :::', d)).toThrow();
    writeFileSync(join(d, 'boucle.md'), '::: inclure essai :::');
    expect(() => inclureFragments('::: inclure boucle :::', d)).toThrow(/n’en inclut pas/);
  });

  it('« Quand ? » et le simulateur partagent les limites froid et écrêtement, sans recopie', async () => {
    const { readFileSync } = await import('node:fs');
    const { resolve } = await import('node:path');
    const racine = resolve(process.cwd(), '..');
    for (const f of ['docs/enquetes/quand.md', 'site/src/lib/simulateur/lecture.md']) {
      const t = readFileSync(resolve(racine, f), 'utf8');
      expect(t, f).toMatch(/^- ::: inclure limite-froid :::$/m);
      expect(t, f).toMatch(/^- ::: inclure limite-ecretement :::$/m);
      expect(t, f).not.toMatch(/\*\*Le froid extrême\.\*\*|\*\*L'écrêtement\.\*\*/);
    }
    const q = chargerEnquete('quand', chargerChiffres());
    const html = q.blocs.map((b) => (b.type === 'html' ? b.html : '')).join('');
    expect(html).toContain('Le froid extrême.');
    expect(html).toContain('L’écrêtement.');
    expect(html).not.toContain('inclure');
  });

  it('le texte de lecture du simulateur rend les deux limites partagées, sans directive restante', async () => {
    const { textesSimulateur } = await import('./simulateur');
    const { lecture } = textesSimulateur(chargerChiffres());
    const html = lecture.join('');
    expect(html).toContain('Le froid extrême.');
    expect(html).toContain('L’écrêtement.');
    expect(html).not.toContain('inclure');
    // Les deux restent dans la même liste que les autres limites.
    const liste = html.slice(html.indexOf('Ce que ce calcul ne dit pas'));
    expect(liste.match(/<ul>/g)?.length).toBe(1);
  });
});
