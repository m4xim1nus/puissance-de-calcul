<script lang="ts">
  // Tableau des données de la monotone du simulateur (équivalent accessible du graphique), rangé
  // dans la notice de la page avec la lecture et les sources du graphique.
  import { formaterNombre } from '$lib/format';
  import { gw } from '$lib/quand';
  import type { Monotone } from './moteur';
  import { proche } from './rangs';

  interface Props {
    annee: number;
    libelle: string;
    avant: Monotone;
    apres: Monotone;
  }
  let { annee, libelle, avant, apres }: Props = $props();

  const RANGS_TABLEAU = [1, 2, 5, 10, 50, 100, 200, 500, 1000, 2000, 4000, 6000, 8000];
  const n = $derived(avant[avant.length - 1][0]);
  const lignesTableau = $derived(
    [...RANGS_TABLEAU.filter((r) => r < n), n].map((r) => {
      const i = proche(avant, r);
      return { rang: avant[i][0], avant: avant[i][1], apres: apres[i][1] };
    })
  );
</script>

<div class="defile">
  <table>
    <caption class="lecteur"
      >Charge résiduelle de {annee} à quelques rangs, en GW, observée et avec {libelle}</caption
    >
    <thead>
      <tr>
        <th scope="col" class="num">Rang de l’heure</th>
        <th scope="col" class="num">Observée</th>
        <th scope="col" class="num">Avec {libelle}</th>
        <th scope="col" class="num">Écart</th>
      </tr>
    </thead>
    <tbody>
      {#each lignesTableau as l (l.rang)}
        <tr>
          <th scope="row" class="num">{formaterNombre(l.rang)}</th>
          <td class="num">{gw(l.avant, false)}</td>
          <td class="num">{gw(l.apres, false)}</td>
          <td class="num">{gw(l.apres - l.avant, false)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
<p class="note-tableau">
  GW, moyenne horaire ; heures où la charge résiduelle est renseignée. Rang 1 = heure la plus tendue
  de la courbe considérée.
</p>

<style>
  .defile {
    overflow-x: auto;
    margin-top: 0.5rem;
  }
  table {
    display: table;
    font-size: 0.875rem;
  }
  th[scope='row'] {
    font-weight: 500;
    border-bottom-color: var(--trait);
  }
  .num {
    white-space: nowrap;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }
  .note-tableau {
    font-family: var(--sans);
    font-size: 0.85rem;
    color: var(--encre-2);
    max-width: 46rem;
  }
</style>
