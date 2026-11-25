<script lang="ts">
  // Consommation 2024 des data centers selon le périmètre : un point pour une valeur publiée,
  // une barre pour un intervalle publié. Une ligne par périmètre, un seul axe en TWh.
  import { scaleLinear } from 'd3-scale';
  import type { Chiffres } from '$lib/chiffres';
  import { formaterNombre } from '$lib/format';
  import Figure from './Figure.svelte';
  import Infobulle from './Infobulle.svelte';
  import {
    ESTIMATIONS_2024,
    estimations2024,
    ligneDonnees,
    sourcesGraphique,
    type Estimation
  } from './donnees';

  let { chiffres }: { chiffres: Chiffres } = $props();

  const lignes = $derived(estimations2024(chiffres));
  const ids = ESTIMATIONS_2024.map((e) => e.id);
  const tableau = $derived(ESTIMATIONS_2024.map((e) => ligneDonnees(chiffres, e.id, e.libelle)));
  const sources = $derived(sourcesGraphique(chiffres, ids));

  const HAUT_LIGNE = 50;
  const HAUT_AXE = 30;
  const DROITE = 88;

  let actif = $state<{ e: Estimation; x: number; y: number } | null>(null);
</script>

<Figure
  id="estimations-2024"
  titre="Consommation d’électricité des data centers en France en 2024, selon le périmètre retenu"
  sousTitre="En TWh sur l’année. Cinq estimations qui ne s’additionnent pas : les deux premières lignes sont des parties des sites dédiés, les autres des périmètres plus ou moins larges."
  {sources}
  lignes={tableau}
>
  {#snippet legende()}
    <span class="cle"
      ><svg width="14" height="14" aria-hidden="true"
        ><circle cx="7" cy="7" r="5" fill="var(--donnee)" /></svg
      > valeur publiée</span
    >
    <span class="cle"
      ><svg width="28" height="14" aria-hidden="true"
        ><rect x="1" y="3" width="26" height="8" rx="4" fill="var(--donnee)" /></svg
      > intervalle publié, de la borne basse à la borne haute</span
    >
  {/snippet}
  {#snippet trace(largeur: number)}
    {@const W = Math.max(280, largeur)}
    {@const max = Math.max(...lignes.map((l) => l.max))}
    {@const x = scaleLinear()
      .domain([0, max])
      .nice()
      .range([4, W - DROITE])}
    {@const H = lignes.length * HAUT_LIGNE + HAUT_AXE}
    <svg
      width={W}
      height={H}
      viewBox="0 0 {W} {H}"
      role="group"
      aria-label="Estimations de la consommation 2024, une ligne par périmètre"
    >
      {#each x.ticks(W < 480 ? 5 : 10) as t (t)}
        <line class="grille" x1={x(t)} x2={x(t)} y1="0" y2={H - HAUT_AXE + 4} />
        <text class="graduation" x={x(t)} y={H - 8} text-anchor="middle">{formaterNombre(t)}</text>
      {/each}
      <text class="graduation unite" x={W - DROITE + 8} y={H - 8}>TWh</text>
      {#each lignes as e, i (e.id)}
        {@const y = i * HAUT_LIGNE + 34}
        <!-- svelte-ignore a11y_no_noninteractive_tabindex (marque focalisable : l'infobulle s'affiche au clavier comme au survol) -->
        <g
          class="marque"
          class:actif={actif?.e.id === e.id}
          tabindex="0"
          role="img"
          aria-label="{e.libelle} : {e.texte}"
          onpointerenter={() => (actif = { e, x: x(e.max), y: y - 8 })}
          onpointerleave={() => (actif = null)}
          onfocus={() => (actif = { e, x: x(e.max), y: y - 8 })}
          onblur={() => (actif = null)}
        >
          <rect class="cible" x="0" y={y - 30} width={W} height={HAUT_LIGNE} />
          <text class="etiquette" x="4" y={y - 14}>{e.libelle}</text>
          {#if e.intervalle}
            <rect
              x={x(e.min)}
              y={y - 4}
              width={Math.max(8, x(e.max) - x(e.min))}
              height="8"
              rx="4"
              fill="var(--donnee)"
            />
          {:else}
            <circle cx={x(e.min)} cy={y} r="5.5" fill="var(--donnee)" class="anneau" />
          {/if}
          <text class="valeur" x={x(e.max) + 10} y={y + 5}>{e.texte}</text>
        </g>
      {/each}
    </svg>
    {#if actif}
      <Infobulle
        x={actif.x}
        y={actif.y}
        largeur={W}
        titre={actif.e.libelle}
        lignes={[{ valeur: actif.e.texte, libelle: 'en 2024' }]}
      />
    {/if}
  {/snippet}
</Figure>

<style>
  svg {
    display: block;
    max-width: 100%;
    height: auto;
    overflow: visible;
    font-family: var(--sans);
  }
  .cle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }
  .grille {
    stroke: var(--trait);
    stroke-width: 1;
  }
  .graduation {
    fill: var(--encre-2);
    font-size: 13px;
    font-variant-numeric: tabular-nums;
  }
  .unite {
    font-weight: 600;
  }
  .etiquette {
    fill: var(--encre);
    font-size: 15px;
  }
  .valeur {
    fill: var(--encre);
    font-size: 15px;
    font-weight: 600;
  }
  .anneau {
    stroke: var(--papier);
    stroke-width: 2;
  }
  .cible {
    fill: transparent;
  }
  .marque {
    outline: none;
  }
  .marque.actif .cible,
  .marque:focus-visible .cible {
    fill: color-mix(in srgb, var(--encre) 6%, transparent);
  }
  .marque:focus-visible .cible {
    stroke: var(--encre);
    stroke-width: 1.5;
  }
</style>
