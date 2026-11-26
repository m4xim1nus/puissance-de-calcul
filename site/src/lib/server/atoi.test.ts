import { describe, expect, it } from 'vitest';
import { aToi } from './atoi';

describe('« À toi »', () => {
  const { titre, miseAJour, html } = aToi();
  it('lit le front matter de docs/A-TOI.md', () => {
    expect(titre).toBe('À toi');
    expect(miseAJour).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
  it('rend des missions numérotées, chacune avec ce qu’il faut vérifier', () => {
    const missions = html.match(/<h2>\d\. /g) ?? [];
    expect(missions.length).toBeGreaterThanOrEqual(3);
    expect((html.match(/Vérifie toi-même/g) ?? []).length).toBe(missions.length);
  });
  it('ne garde aucun commentaire ni lien interne cassé', () => {
    expect(html).not.toContain('<!--');
    const internes = [...html.matchAll(/href="(\/[^"#]*)/g)].map((m) => m[1]);
    for (const l of internes)
      expect([
        '/',
        '/making-of',
        '/simulateur',
        '/quand',
        '/combien',
        '/carbone',
        '/methode'
      ]).toContain(l);
  });
});
