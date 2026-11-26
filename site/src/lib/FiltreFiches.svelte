<script lang="ts" generics="V extends string">
  // Filtre d'une liste de fiches : un bouton par valeur, « Toutes » en tête. Amélioration
  // progressive : sans JavaScript, le filtre n'est pas affiché et toutes les fiches restent
  // visibles (la page est prérendue avec la sélection « tout »).
  import { onMount } from 'svelte';

  interface Props {
    /** Intitulé visible du groupe de boutons (« Tranchée par »). */
    intitule: string;
    /** Identifiant unique, pour relier l'intitulé au groupe. */
    id: string;
    options: { valeur: V; libelle: string; nombre: number }[];
    total: number;
    /** Valeur choisie ; `null` = toutes les fiches. */
    selection: V | null;
    /** « décision » / « décisions », pour le décompte annoncé. */
    unites: [string, string];
    /** Nombre de fiches affichées avec la sélection courante. */
    affichees: number;
  }
  let {
    intitule,
    id,
    options,
    total,
    selection = $bindable(),
    unites,
    affichees
  }: Props = $props();

  let pret = $state(false);
  onMount(() => (pret = true));

  const unite = (n: number) => (n > 1 ? unites[1] : unites[0]);
</script>

{#if pret}
  <div class="filtre">
    <span class="intitule" id="{id}-intitule">{intitule}</span>
    <div class="boutons" role="group" aria-labelledby="{id}-intitule">
      <button type="button" aria-pressed={selection === null} onclick={() => (selection = null)}
        >Toutes <span class="n">{total}</span></button
      >
      {#each options as o (o.valeur)}
        <button
          type="button"
          aria-pressed={selection === o.valeur}
          onclick={() => (selection = selection === o.valeur ? null : o.valeur)}
          >{o.libelle} <span class="n">{o.nombre}</span></button
        >
      {/each}
    </div>
    <p class="compte" aria-live="polite">
      {#if selection === null}
        {total}&nbsp;{unite(total)}
      {:else}
        {affichees}&nbsp;{unite(affichees)} sur {total}
      {/if}
    </p>
  </div>
{/if}

<style>
  .filtre {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.4rem 1rem;
    margin: 0 0 1rem;
    font-family: var(--sans);
  }
  .intitule {
    font-weight: 600;
  }
  .boutons {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
  }
  button {
    font: inherit;
    font-size: 0.95rem;
    padding: 0.2rem 0.6rem;
    min-height: 2rem;
    border: 1px solid var(--trait);
    border-radius: 3px;
    background: transparent;
    color: var(--encre);
    cursor: pointer;
  }
  button:hover {
    border-color: var(--encre-2);
  }
  button[aria-pressed='true'] {
    background: var(--encre);
    border-color: var(--encre);
    color: var(--papier);
    font-weight: 600;
  }
  .n {
    font-variant-numeric: tabular-nums;
    opacity: 0.8;
  }
  .compte {
    margin: 0;
    font-size: 0.95rem;
    color: var(--encre-2);
  }
</style>
