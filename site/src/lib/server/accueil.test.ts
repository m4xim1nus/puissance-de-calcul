import { describe, expect, it } from 'vitest';
import { load } from '../../routes/+page.server';

describe('accueil', () => {
  const data = load();
  it('une accroche par enquête, qui commence par un chiffre du référentiel avec sa note', () => {
    expect(data.accroches.map((a) => a.slug)).toEqual(['combien', 'quand', 'carbone', 'ou']);
    for (const a of data.accroches) {
      expect(a.chiffre, a.slug).toMatch(/<span class="chiffre">[^<]+<\/span><sup class="appel">/);
      expect(a.suite.trim().length, a.slug).toBeGreaterThan(20);
      expect(a.notes, a.slug).toContain('class="note');
    }
  });
  it('le message en trois sections, daté et versionné', () => {
    const m = data.message;
    expect(m.miseAJour).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(m.version).toMatch(/^\d+$/);
    expect(m.retenir.join('')).toContain('<strong>');
    expect(m.detail.length).toBeGreaterThan(3);
    expect(m.changements.join('')).toContain(`Version ${m.version}`);
  });
  it('des notes numérotées sans doublon sur toute la page, dans l’ordre de lecture', () => {
    const html = [
      ...data.message.retenir,
      ...data.accroches.map((a) => a.chiffre + a.suite),
      ...data.message.detail,
      ...data.message.changements
    ].join('');
    const appels = [...html.matchAll(/id="appel-(\d+)"/g)].map((m) => Number(m[1]));
    expect(appels).toEqual(appels.map((_, i) => i + 1));
  });
});
