// Un fichier statique compact par année de prix (≈ 35 Ko), chargé à la demande par le hero.
import { json } from '@sveltejs/kit';
import { anneePrix, anneesPrix } from '$lib/server/prix';

export const prerender = true;

export function entries() {
  return anneesPrix().map((a) => ({ annee: String(a) }));
}

export function GET({ params }: { params: { annee: string } }) {
  return json(anneePrix(Number(params.annee)));
}
