import { describe, expect, it } from 'vitest';
import type { Chiffre } from './chiffres';
import { FINE } from './format';
import { appel, dateSource, noteChiffre, noteSource } from './notes';

const source = {
  cle: 'rte-be2025',
  editeur: 'RTE',
  titre: 'Bilan électrique 2025',
  date_publication: '2026-03-01',
  url: 'https://exemple.fr/be2025.pdf',
  consulte_le: '2026-11-25',
  note: 'date de publication approchée au mois'
};
const c: Chiffre = {
  libelle: 'Puissance moyenne appelée',
  valeur: 114,
  unite: 'MW',
  grandeur: 'puissance_appelee_moyenne',
  periode: '2025',
  perimetre: 'réseau de transport',
  source,
  page: 'p. 18',
  citation: '« près de 1 TWh en 2025 »',
  confiance: 'B',
  calcul: '1 TWh ÷ 8 760 h'
};

describe('notes', () => {
  it('rend un appel numéroté qui pointe vers la note', () => {
    expect(appel(3)).toContain('href="#note-3"');
    expect(appel(3)).toContain('id="appel-3"');
    expect(appel(3)).toContain('aria-label="note 3"');
  });
  it('date une source au mois quand sa date est approchée', () => {
    expect(dateSource(source)).toBe('mars 2026');
    expect(dateSource({ ...source, note: undefined })).toBe('1er mars 2026');
  });
  it('rend une note complète : source, lien, date, page, citation, période, périmètre, calcul, cote', () => {
    const html = noteChiffre(7, c);
    expect(html).toContain('id="note-7"');
    expect(html).toContain(
      'RTE, <a href="https://exemple.fr/be2025.pdf" rel="external">Bilan électrique 2025</a>'
    );
    expect(html).toContain('mars 2026, p. 18.');
    expect(html).toContain('p. 18');
    expect(html).toContain('Citation : </span>« près de 1 TWh en 2025 »');
    expect(html).toContain('Période</span> 2025');
    expect(html).toContain('Périmètre</span> réseau de transport');
    expect(html).toContain('<strong>calcul du site</strong>');
    expect(html).toContain('Calcul du site</span> 1 TWh ÷ 8 760 h.');
    expect(html).toContain(`114${FINE}MW`);
    expect(html).toContain('Confiance B</a> : source primaire, recoupement partiel');
    expect(html).toContain('Non recoupé.');
  });
  it('omet la mention de calcul quand le chiffre est publié tel quel', () => {
    const html = noteChiffre(1, { ...c, calcul: undefined });
    expect(html).not.toContain('Calcul du site');
    expect(html).not.toContain('calcul du site');
  });
  it('échappe le contenu du référentiel', () => {
    expect(noteChiffre(1, { ...c, citation: '<b>x</b>' })).toContain('&lt;b&gt;x&lt;/b&gt;');
  });
  it('rend une note de source seule, avec sa page', () => {
    const html = noteSource(2, source, 'p. 6');
    expect(html).toContain('id="note-2"');
    expect(html).toContain('p. 6');
    expect(html).not.toContain('Confiance');
  });
});
