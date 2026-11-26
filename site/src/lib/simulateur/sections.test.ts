import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { sectionsParTitre } from './sections';

describe('sections du texte de lecture', () => {
  it('coupe à chaque titre de niveau 2, sans rien perdre ni ajouter', () => {
    const html = '<h2>Un</h2><p>a</p>\n<h2 id="x">Deux&nbsp;: b</h2><ul><li>c</li></ul>';
    const s = sectionsParTitre([html]);
    expect(s).toEqual([
      { titre: 'Un', html: '<p>a</p>' },
      { titre: 'Deux&nbsp;: b', html: '<ul><li>c</li></ul>' }
    ]);
    // Le texte reconstitué contient tout le texte d'origine.
    const texte = (h: string) => h.replace(/<[^>]+>/g, '').replace(/\s+/g, '');
    expect(texte(s.map((x) => x.titre + x.html).join(''))).toBe(texte(html));
  });

  it('refuse un texte placé avant le premier titre', () => {
    expect(() => sectionsParTitre(['<p>perdu</p><h2>Un</h2>'])).toThrow();
    expect(() => sectionsParTitre(['<p>sans titre</p>'])).toThrow();
  });

  it('lecture.md commence par un titre de niveau 2', () => {
    const md = readFileSync('src/lib/simulateur/lecture.md', 'utf8').replace(/<!--[\s\S]*?-->/, '');
    expect(md.trim().startsWith('## ')).toBe(true);
  });
});
