import { describe, expect, it } from 'vitest';
import type { Chiffre } from './chiffres';
import { FINE } from './format';
import { appel, dateSource, noteChiffre, noteSource, titreCourt } from './notes';

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
  it('rend une note compacte : n°, éditeur, titre court, date, page, pastille, calcul du site', () => {
    const html = noteChiffre(7, c);
    const tete = html.slice(0, html.indexOf('<details'));
    expect(tete).toContain('id="note-7"');
    expect(tete).toContain(
      'RTE, <a href="https://exemple.fr/be2025.pdf" rel="external">Bilan électrique 2025</a>'
    );
    expect(tete).toContain('mars\u00a02026, p. 18');
    expect(tete).toContain('class="cote"');
    expect(tete).toContain('Confiance B : source primaire, sans recoupement indépendant');
    expect(tete).toContain('calcul du site');
    // La citation, la période, le périmètre et le calcul détaillé sont dans le repli.
    expect(tete).not.toContain('près de 1 TWh');
    const repli = html.slice(html.indexOf('<details'));
    expect(repli).toContain('« près de 1 TWh en 2025 »');
    expect(repli).toContain('Période</span> 2025');
    expect(repli).toContain('Périmètre</span> réseau de transport');
    expect(repli).toContain('Calcul du site</span> 1 TWh ÷ 8 760 h.');
    expect(repli).toContain(`114${FINE}MW`);
    expect(repli).toContain('Non recoupé.');
  });
  it('raccourcit les titres longs, le titre complet restant au survol et dans le repli', () => {
    expect(titreCourt('Bilan électrique 2025 — rapport complet')).toBe('Bilan électrique 2025');
    expect(titreCourt('Les data centers en chiffres clés (page web)')).toBe(
      'Les data centers en chiffres clés'
    );
    const long = titreCourt(
      "Prospective d'évolution des consommations des centres de données en France de 2024 à 2060"
    );
    expect(long.length).toBeLessThanOrEqual(41);
    expect(long.endsWith('…')).toBe(true);
  });
  it('omet la mention de calcul quand le chiffre est publié tel quel', () => {
    const html = noteChiffre(1, { ...c, calcul: undefined });
    expect(html).not.toContain('alcul du site');
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

describe('note d’un chiffre calculé par le site', () => {
  const calcule: Chiffre = {
    ...c,
    source: { ...source, cle: 'pdc-quand', editeur: 'Puissance de calcul (calcul du site)' },
    page: 'data/export/quand.json',
    libelle: 'Charge résiduelle, maximum horaire',
    valeur: 31.4,
    valeur_calculee: 31.433,
    precision: 0.1,
    unite: 'GW',
    periode: '2025-01-14, 8 h-9 h (heure de Paris)',
    citation: 'annees.2025.charge_residuelle.max',
    calcul: 'consommation − éolien − solaire − nucléaire disponible',
    produit_par: 'pc build',
    verification: 'pc check'
  };
  it('dit « calcul du site », la méthode et les données, sans page de source', () => {
    const html = noteChiffre(4, calcule);
    const tete = html.slice(0, html.indexOf('<details'));
    expect(tete).toContain('Calcul du site');
    expect(tete).toContain('14 janv. 2025');
    expect(tete).not.toContain('data/export/quand.json');
    expect(html).toContain('<span class="note-cle">Méthode</span> consommation − éolien');
    expect(html).toContain('<span class="note-cle">Données</span>');
    expect(html).toContain(`31,433${FINE}GW, affiché arrondi au pas de 0,1${FINE}GW`);
    expect(html).toContain('contrôlé par <code>pc check</code>');
    expect(html).toContain('Non recoupé.');
    expect(html).toContain('id="note-4"');
  });
  it('refuse un chiffre calculé sans méthode', () => {
    expect(() => noteChiffre(1, { ...calcule, calcul: undefined })).toThrow(/sans méthode/);
  });
});
