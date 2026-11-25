import { describe, expect, it } from 'vitest';
import { sectionsMakingOf } from './makingof';

describe('making-of', () => {
  const sections = sectionsMakingOf();
  it('trouve et rend les quatre fichiers', () => {
    expect(sections.map((s) => s.id)).toEqual(['journal', 'decisions', 'erreurs', 'brief']);
    for (const s of sections) expect(s.html.length, s.fichier).toBeGreaterThan(200);
  });
  it('rend les tableaux des décisions', () => {
    const d = sections.find((s) => s.id === 'decisions')!;
    expect(d.html).toContain('<table>');
    expect(d.html).not.toContain('|---|');
  });
});
