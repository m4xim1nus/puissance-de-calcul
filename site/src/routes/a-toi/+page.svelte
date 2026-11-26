<script lang="ts">
  import { formaterDate } from '$lib/format';

  let { data } = $props();
</script>

<svelte:head>
  <title>{data.titre} · Puissance de calcul</title>
  <meta
    name="description"
    content="Cinq missions à faire toi-même avec Claude Code, de ta courbe Linky à la chasse aux erreurs de ce site."
  />
</svelte:head>

<h1>{data.titre}</h1>
<p class="maj">
  Mis à jour le <time datetime={data.miseAJour}>{formaterDate(data.miseAJour)}</time>
</p>

<div class="texte missions">
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html data.html}
</div>

<style>
  .maj {
    font-family: var(--sans);
    color: var(--encre-2);
    margin-top: -0.5rem;
  }
  .missions :global(h2) {
    margin-top: 2.2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--trait);
  }
  .missions :global(blockquote) {
    color: var(--encre);
    border-left-color: var(--encre-2);
  }
</style>
