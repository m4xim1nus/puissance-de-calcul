import { describe, expect, it } from 'vitest';
import {
  FICHIERS,
  analyserDecisions,
  analyserErreurs,
  analyserJournal,
  analyserQui,
  classerReperage,
  lireFichier,
  makingOf,
  premierePhrase
} from './makingof';

/**
 * Écarts au contrat présents dans les fichiers du dépôt au moment où le contrat a été posé
 * (2026-11-26), signalés à l'owner et laissés en l'état (ces fichiers ne se corrigent pas
 * ici). Le test échoue sur tout nouvel écart, et aussi quand un écart listé disparaît : la
 * liste ne peut que se vider.
 */
const ECARTS_CONNUS: Record<keyof typeof FICHIERS, string[]> = {
  journal: [],
  decisions: [],
  erreurs: [],
  brief: []
};

function verifierContrat(fichier: keyof typeof FICHIERS, ecarts: string[]) {
  const connus = ECARTS_CONNUS[fichier];
  expect(
    ecarts.filter((e) => !connus.includes(e)),
    `${FICHIERS[fichier]} ne respecte pas son format`
  ).toEqual([]);
  expect(
    connus.filter((e) => !ecarts.includes(e)),
    `écart corrigé dans ${FICHIERS[fichier]} : le retirer de ECARTS_CONNUS`
  ).toEqual([]);
}

describe('contrat des fichiers du making-of (vrais fichiers du dépôt)', () => {
  const m = makingOf();

  it('DECISIONS.md : chaque ligne a 4 colonnes, une date AAAA-MM-JJ et un « Qui » reconnu', () => {
    verifierContrat('decisions', m.decisions.ecarts);
    expect(m.decisions.entrees.length).toBeGreaterThan(10);
    for (const d of m.decisions.entrees) expect(d.qui.length, d.quiTexte).toBeGreaterThan(0);
  });

  it('ERREURS.md : chaque entrée a ses 4 champs et dit qui a repéré l’erreur', () => {
    verifierContrat('erreurs', m.erreurs.ecarts);
    expect(m.erreurs.entrees.length).toBeGreaterThan(5);
  });

  it('JOURNAL.md : chaque session a un en-tête au format et une demande citée', () => {
    verifierContrat('journal', m.journal.ecarts);
    expect(m.journal.entrees.length).toBeGreaterThan(0);
    for (const s of m.journal.entrees) expect(s.demande, s.id).toContain('<blockquote>');
  });

  it('le brief est rattaché à la session 1, en entier et sans retouche', () => {
    const s1 = m.journal.entrees.find((s) => s.numero === 1)!;
    expect(s1.brief).not.toBeNull();
    expect(m.journal.entrees.filter((s) => s.brief !== null)).toHaveLength(1);
    // Chaque ligne de texte du brief se retrouve dans le rendu (au balisage près).
    const texte = (h: string) =>
      h
        .replace(/<[^>]+>/g, '')
        .replace(/&amp;/g, '&')
        .replace(/&quot;/g, '"')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/\s+/g, ' ');
    const rendu = texte(s1.brief!);
    const mots = lireFichier(FICHIERS.brief)
      .replace(/[*`#>|]|^\s*[-\d.]+\s/gm, ' ')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .split(/\s+/)
      .filter((w) => /\p{L}{4,}/u.test(w) && !/[*_[\]()]/.test(w));
    expect(mots.length).toBeGreaterThan(500);
    const absents = mots.filter((w) => !rendu.includes(w));
    expect(absents).toEqual([]);
  });

  it('n’affiche ni le gabarit « Format » d’ERREURS.md ni de syntaxe Markdown brute', () => {
    expect(m.erreurs.intro).toContain('lecteur critique');
    expect(m.erreurs.intro).not.toContain('AAAA-MM-JJ');
    const tout = JSON.stringify(m);
    expect(tout).not.toContain('|---|');
    expect(tout).not.toMatch(/\*\*[^*]+\*\*/);
    expect(tout).not.toContain('### ');
  });

  it('garde visible la note de caviardage du journal', () => {
    expect(m.journal.intro).toContain('<blockquote>');
    expect(m.journal.intro).toContain('Caviardage');
  });
});

describe('analyse des formats (cas synthétiques)', () => {
  it('lit les arbitres simples et composés', () => {
    expect(analyserQui('Claude')).toEqual([{ qui: 'Claude', role: null }]);
    expect(analyserQui('l’auteur')).toEqual([{ qui: "l'auteur", role: null }]);
    expect(analyserQui("l'auteur (demande), Claude (forme)")).toEqual([
      { qui: "l'auteur", role: 'demande' },
      { qui: 'Claude', role: 'forme' }
    ]);
    expect(analyserQui('Claude (forme, couleurs)')).toEqual([
      { qui: 'Claude', role: 'forme, couleurs' }
    ]);
    expect(analyserQui('RTE')).toBeNull();
    expect(analyserQui('')).toBeNull();
  });

  const TETE = '# D\n\n| Date | Décision | Raisons | Qui |\n|---|---|---|---|\n';
  it('refuse une décision à 3 colonnes, une date mal formée, un « Qui » inconnu', () => {
    const a = analyserDecisions(
      TETE +
        '| 2026-11-26 | a | b | Claude |\n' +
        '| 2026-11-26 | a | Claude |\n' +
        '| 26/11/2026 | a | b | Claude |\n' +
        '| 2026-02-30 | a | b | Claude |\n' +
        '| 2026-11-26 | a | b | le comité |\n'
    );
    expect(a.entrees).toHaveLength(5);
    expect(a.ecarts).toEqual([
      'ligne 6 : 4 colonnes attendues, 3 trouvées',
      expect.stringContaining('ligne 6 : « Qui »'),
      'ligne 7 : date « 26/11/2026 » au lieu de AAAA-MM-JJ',
      'ligne 8 : date « 2026-02-30 » au lieu de AAAA-MM-JJ',
      expect.stringContaining('ligne 9 : « Qui » vaut « le comité »')
    ]);
    expect(a.entrees.map((d) => d.id).slice(0, 2)).toEqual([
      'decision-2026-11-26-1',
      'decision-2026-11-26-2'
    ]);
  });

  const ERREUR = (champs: string) =>
    '# E\n\nIntro.\n\nFormat :\n\n```\n### AAAA-MM-JJ — t\n- **Faux** : …\n```\n\n---\n\n### 2026-11-26 — Titre\n' +
    champs;
  it('lit une erreur complète, y compris une liste sous un champ', () => {
    const a = analyserErreurs(
      ERREUR(
        '- **Faux** :\n  1. un ;\n  2. deux.\n- **Repéré par** : Claude lui-même.\n- **Correction** : x.\n- **Garde-fou ajouté** : aucun.\n'
      )
    );
    expect(a.ecarts).toEqual([]);
    expect(a.entrees).toHaveLength(1);
    expect(a.entrees[0].reperage).toBe('Claude lui-même');
    expect(a.entrees[0].champs[0].html).toBe('<ol><li>un\u202f;</li><li>deux.</li></ol>');
    expect(a.intro).toBe('<p>Intro.</p>');
  });
  it('refuse une erreur à qui il manque un champ', () => {
    const a = analyserErreurs(
      ERREUR('- **Faux** : a\n- **Repéré par** : un test\n- **Correction** : c\n')
    );
    expect(a.ecarts).toEqual(['ligne 14 : champ « Garde-fou ajouté » absent']);
  });
  it('classe qui a repéré l’erreur', () => {
    expect(classerReperage('Claude lui-même, en relisant')).toBe('Claude lui-même');
    expect(classerReperage('`pc check`, lancé par l’agent du pipeline')).toBe('un test');
    expect(classerReperage('le test `test_x`')).toBe('un test');
    expect(classerReperage('la contre-vérification adverse.')).toBe('un agent');
    expect(classerReperage('l’agent du site')).toBe('un agent');
    expect(classerReperage("L'auteur, en relisant le site")).toBe("l'auteur");
    expect(classerReperage('un lecteur')).toBeNull();
  });

  const SESSION = '# J\n\nIntro.\n\n---\n\n## Session 3 — 2026-12-01, à partir de 9 h · objet\n\n';
  it('refuse une session sans demande citée', () => {
    expect(analyserJournal(SESSION + '**Fait** :\n\n- x\n').ecarts).toEqual([
      "ligne 7 : pas de paragraphe « **Demande de l'auteur** »"
    ]);
    expect(
      analyserJournal(SESSION + "**Demande de l'auteur** : fais x.\n\n**Fait** : x.\n").ecarts
    ).toEqual(["ligne 7 : la demande de l'auteur n'est pas citée (bloc « > » attendu)"]);
  });
  it('lit en-tête, demande, résumé et parties d’une session', () => {
    const a = analyserJournal(
      SESSION +
        "**Demande de l'auteur** (citée telle quelle) :\n\n> fais x\n\n**Fait** :\n\n- x\n\n" +
        '**Durée** : de 9 h à 10 h. Pause comprise.\n\n**Coût** : non relevé.\n'
    );
    expect(a.ecarts).toEqual([]);
    const s = a.entrees[0];
    expect([s.id, s.numero, s.date, s.horaire, s.objet]).toEqual([
      'session-3',
      3,
      '2026-12-01',
      'à partir de 9 h',
      'objet'
    ]);
    expect(s.demande).toContain('<blockquote><p>fais x</p></blockquote>');
    expect(s.resume).toEqual([
      { cle: 'Durée', html: 'de 9 h à 10 h' },
      { cle: 'Coût', html: 'non relevé' }
    ]);
    expect(s.parties).toEqual(['Fait', 'Durée', 'Coût']);
    expect(s.enCours).toBe(false);
    const ouverte = analyserJournal(SESSION + "**Demande de l'auteur** :\n\n> fais x\n");
    expect(ouverte.entrees[0].enCours).toBe(true);
    expect(s.detail).not.toContain('fais x');
    expect(s.brief).toBeNull();
  });
  it('coupe à la première phrase', () => {
    expect(premierePhrase('10 (8 Opus, 2 Sonnet). L’agent du site…')).toBe('10 (8 Opus, 2 Sonnet)');
    expect(premierePhrase('sans point')).toBe('sans point');
  });
});
