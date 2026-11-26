import { describe, expect, it } from 'vitest';
import { enLigne, markdown, paragraphes } from './markdown';

describe('markdown de base', () => {
  it('échappe le HTML avant de mettre en forme', () => {
    expect(enLigne('<script>**gras**')).toBe('&lt;script&gt;<strong>gras</strong>');
  });
  it('rend les liens internes et externes, ignore les autres schémas', () => {
    expect(enLigne('[loi](/lois/2023-270)')).toBe('<a href="/lois/2023-270">loi</a>');
    expect(enLigne('[AN](https://x.fr)')).toBe('<a href="https://x.fr" rel="external">AN</a>');
    expect(enLigne('[x](javascript:alert)')).toBe('x');
  });
  it('découpe en paragraphes', () => {
    expect(paragraphes('a\nb\n\n*c*')).toBe('<p>a b</p><p><em>c</em></p>');
  });
});
describe('typographie', () => {
  it('pose les insécables, et ne courbe l’apostrophe qu’en typographie complète', () => {
    expect(enLigne("l'heure : « oui » ?", { typographie: true })).toBe(
      'l’heure\u00a0: «\u00a0oui\u00a0»\u202f?'
    );
    expect(enLigne("l'heure : « oui » ?", { typographie: 'espaces' })).toBe(
      "l'heure\u00a0: «\u00a0oui\u00a0»\u202f?"
    );
  });
});
describe('markdown complet', () => {
  it('protège le code inline de toute autre mise en forme', () => {
    expect(enLigne('`a *b* <c>` et *d*')).toBe('<code>a *b* &lt;c&gt;</code> et <em>d</em>');
  });
  it('rend titres décalés, gras, italique et liens', () => {
    expect(
      markdown('# T\n\nun **gras**, un *it* et [lien](https://x.fr)', { niveauTitre: 3 })
    ).toBe(
      '<h3>T</h3>\n<p>un <strong>gras</strong>, un <em>it</em> et <a href="https://x.fr" rel="external">lien</a></p>'
    );
  });
  it('rend les citations, y compris multilignes et avec markdown dedans', () => {
    expect(markdown('> a\n> **b**\n\nfin')).toBe(
      '<blockquote><p>a <strong>b</strong></p></blockquote>\n<p>fin</p>'
    );
  });
  it('rend les listes imbriquées et ordonnées', () => {
    expect(markdown('- a\n  - a1\n  - a2\n- b\n\n1. x\n2. y')).toBe(
      '<ul><li>a<ul><li>a1</li><li>a2</li></ul></li><li>b</li></ul>\n<ol><li>x</li><li>y</li></ol>'
    );
  });
  it('rend les tableaux avec alignements et pipes échappés', () => {
    const t = '| Date | Valeur |\n|---|--:|\n| `a\\|b` | **1** |\n| c | 2 |';
    expect(markdown(t)).toBe(
      '<table><thead><tr><th>Date</th><th style="text-align:right">Valeur</th></tr></thead>' +
        '<tbody><tr><td><code>a|b</code></td><td style="text-align:right"><strong>1</strong></td></tr>' +
        '<tr><td>c</td><td style="text-align:right">2</td></tr></tbody></table>'
    );
  });
  it('rend les blocs de code sans interpréter leur contenu', () => {
    expect(markdown('```python\nx = "<a>" # *y*\n```')).toBe(
      '<pre><code class="langage-python">x = &quot;&lt;a&gt;&quot; # *y*</code></pre>'
    );
  });
  it('échappe le HTML brut', () => {
    expect(markdown('<script>alert(1)</script>')).toBe(
      '<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>'
    );
  });
});
