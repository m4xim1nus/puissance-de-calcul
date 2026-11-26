<script lang="ts">
  // Cadre commun des graphiques : titre qui dit ce qui est montré, unités, légende, tracé à la
  // largeur mesurée, remarques, sources, et tableau de données repliable (équivalent accessible).
  import type { Snippet } from 'svelte';
  import type { LigneDonnees } from './donnees';

  interface Props {
    id: string;
    titre: string;
    sousTitre: string;
    legende?: Snippet;
    trace: Snippet<[number]>;
    remarques?: string;
    sources: string;
    /** Chiffres du référentiel montrés par le graphique (tableau standard). */
    lignes?: LigneDonnees[];
    /** Tableau de données propre au graphique, à la place du tableau standard. */
    tableau?: Snippet;
    /** Intitulé du repli du tableau. */
    titreTableau?: string;
    /** Contrôles au-dessus du tracé (choix d'année…), affichés seulement avec JavaScript. */
    controles?: Snippet;
  }
  let {
    id,
    titre,
    sousTitre,
    legende,
    trace,
    remarques,
    sources,
    lignes = [],
    tableau,
    titreTableau = 'Tableau des données',
    controles
  }: Props = $props();

  // Largeur mesurée après hydratation ; au prérendu, une largeur de bureau (le SVG se réduit).
  let largeur = $state(0);
</script>

<figure class="graphique" aria-labelledby="{id}-titre">
  <figcaption>
    <h3 id="{id}-titre">{titre}</h3>
    <p class="sous-titre">{sousTitre}</p>
  </figcaption>
  {#if legende}
    <div class="legende">{@render legende()}</div>
  {/if}
  {#if controles}{@render controles()}{/if}
  <div class="trace" bind:clientWidth={largeur}>
    {@render trace(largeur || 840)}
  </div>
  {#if remarques}
    <p class="remarques">{remarques}</p>
  {/if}
  <p class="sources"><span class="cle">Sources</span> {sources}</p>
  <details class="donnees">
    <summary>{titreTableau}</summary>
    {#if tableau}
      <div class="defile">{@render tableau()}</div>
    {:else}
      <div class="defile">
        <table>
          <thead>
            <tr>
              <th scope="col">Donnée</th>
              <th scope="col">Valeur</th>
              <th scope="col">Période</th>
              <th scope="col">Périmètre</th>
              <th scope="col">Source</th>
              <th scope="col">Confiance</th>
            </tr>
          </thead>
          <tbody>
            {#each lignes as l (l.id)}
              <tr>
                <th scope="row">{l.libelle}</th>
                <td class="nombre"
                  >{l.valeur}{#if l.calcul}<br /><span class="calc">calcul du site</span>{/if}</td
                >
                <td>{l.periode}</td>
                <td>{l.perimetre}</td>
                <td
                  >{l.source.editeur}, <a href={l.source.url} rel="external">{l.source.titre}</a>, {l.page}</td
                >
                <td>{l.confiance}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </details>
</figure>

<style>
  .graphique {
    clear: both;
    margin: 2.5rem 0 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--encre);
    font-family: var(--sans);
  }
  figcaption h3 {
    margin: 0 0 0.2rem;
    font-size: 1.3rem;
    line-height: 1.2;
    max-width: 46rem;
  }
  .sous-titre {
    margin: 0 0 0.75rem;
    color: var(--encre-2);
    font-size: 1rem;
    line-height: 1.35;
    max-width: 46rem;
  }
  .legende {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem 1.25rem;
    margin: 0 0 0.75rem;
    font-size: 0.95rem;
    line-height: 1.3;
    color: var(--encre);
  }
  .trace {
    position: relative;
    width: 100%;
  }
  .remarques,
  .sources {
    margin: 0.75rem 0 0;
    font-size: 0.9rem;
    line-height: 1.4;
    color: var(--encre-2);
    max-width: 46rem;
  }
  .sources .cle {
    font-weight: 600;
    color: var(--encre);
  }
  .donnees {
    margin-top: 0.75rem;
  }
  .donnees summary {
    font-size: 0.95rem;
  }
  .defile {
    overflow-x: auto;
    margin-top: 0.5rem;
  }
  .defile :global(table) {
    display: table;
    min-width: 40rem;
    font-size: 0.875rem;
  }
  .defile :global(th[scope='row']) {
    font-weight: 500;
    border-bottom-color: var(--trait);
    min-width: 10rem;
  }
  .defile :global(.num) {
    white-space: nowrap;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }
  .nombre {
    white-space: nowrap;
  }
  .calc {
    color: var(--encre-2);
    font-size: 0.85em;
  }
</style>
