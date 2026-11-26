// Découpe d'un texte rendu au prérendu (HTML de rendreCorps) en sections, une par titre de niveau 2 :
// la page /simulateur range chaque section dans un repli dont l'intitulé est le titre, tel quel.

export interface Section {
  /** HTML du titre (texte typographié du fichier Markdown, sans balise <h2>). */
  titre: string;
  /** HTML de la section, titre exclu. */
  html: string;
}

const TITRE = /<h2(?:\s[^>]*)?>([\s\S]*?)<\/h2>/;

/** Sections du texte ; rien ne doit précéder le premier titre (sinon ce texte serait perdu). */
export function sectionsParTitre(blocs: string[]): Section[] {
  const parties = blocs.join('\n').split(new RegExp(TITRE.source, 'g'));
  const avant = parties.shift() ?? '';
  if (avant.trim()) throw new Error('Texte avant le premier titre de section : il serait perdu');
  const sections: Section[] = [];
  for (let k = 0; k < parties.length; k += 2)
    sections.push({ titre: parties[k].trim(), html: (parties[k + 1] ?? '').trim() });
  if (!sections.length) throw new Error('Aucun titre de section');
  return sections;
}
