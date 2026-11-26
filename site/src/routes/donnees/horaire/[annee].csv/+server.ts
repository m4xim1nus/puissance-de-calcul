// Séries horaires d'une année pleine, servies telles quelles au simulateur : le prérendu copie
// data/export/horaire/AAAA.csv dans le site (aucune copie versionnée dans site/, aucun appel externe).
import { anneesSimulateur, csvHoraire } from '$lib/server/simulateur';

export const prerender = true;

export function entries() {
  return anneesSimulateur().map((a) => ({ annee: String(a) }));
}

export function GET({ params }: { params: { annee: string } }) {
  return new Response(csvHoraire(Number(params.annee)), {
    headers: { 'content-type': 'text/csv; charset=utf-8' }
  });
}
