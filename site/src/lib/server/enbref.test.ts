// Relevé « En bref » (making-of/en-bref.json, produit par `pc bilan`) : forme attendue par la page,
// et aucune trace de la machine de l'auteur (chemin, identifiant de session).
import { describe, expect, it } from 'vitest';
import { FICHIER_EN_BREF, lireFichier, makingOf } from './makingof';

describe('en-bref.json', () => {
  const brut = lireFichier(FICHIER_EN_BREF);
  const { enBref, journal, decisions } = makingOf();

  it('a une session par entrée du journal relevée, numérotées comme le journal', () => {
    const numeros = new Set(journal.entrees.map((s) => s.numero));
    expect(enBref.sessions.length).toBeGreaterThan(0);
    for (const s of enBref.sessions) expect(numeros.has(s.numero)).toBe(true);
  });

  it('a des totaux numériques cohérents avec les sessions', () => {
    const somme = (k: 'actif_min' | 'signes_auteur' | 'messages_auteur') =>
      enBref.sessions.reduce((t, s) => t + s[k], 0);
    expect(enBref.total.actif_min).toBe(somme('actif_min'));
    expect(enBref.total.signes_auteur).toBe(somme('signes_auteur'));
    expect(enBref.total.messages_auteur).toBe(somme('messages_auteur'));
    for (const v of Object.values(enBref.depot)) expect(Number.isFinite(v)).toBe(true);
  });

  it('ne contient ni chemin ni identifiant de transcription', () => {
    expect(brut).not.toMatch(/\/home\/|\.jsonl|\.claude|[0-9a-f]{8}-[0-9a-f]{4}-/);
  });

  it('ne publie pas d’horaires de session, seulement des dates', () => {
    for (const s of enBref.sessions) {
      expect(s.date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(Object.keys(s)).not.toContain('debut');
      expect(Object.keys(s)).not.toContain('fin');
    }
  });

  it('décisions : auteur seul + Claude seul + partagées = total (aucun double compte)', () => {
    const e = decisions.entrees;
    const seul = (q: string) => e.filter((d) => d.qui.every((t) => t.qui === q)).length;
    const partagees = e.filter((d) => new Set(d.qui.map((t) => t.qui)).size > 1).length;
    expect(seul("l'auteur") + seul('Claude') + partagees).toBe(e.length);
  });
});
