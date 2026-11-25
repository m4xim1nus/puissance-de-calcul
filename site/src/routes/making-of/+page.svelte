<script lang="ts">
  let { data } = $props();
</script>

<svelte:head>
  <title>Making-of · Puissance de calcul</title>
</svelte:head>

<h1>Making-of</h1>
<p class="colonne">
  Ce site est construit par Claude Code, sous la direction de l'auteur. Voici la matière brute, publiée
  telle quelle : le journal de bord, les décisions et leurs raisons, les erreurs de Claude
  consignées sans les embellir, et le brief de départ.
</p>
<nav class="sommaire" aria-label="Sections du making-of">
  {#each data.sections as s (s.id)}
    <a href="#{s.id}">{s.titre}</a>
  {/each}
</nav>

{#each data.sections as s (s.id)}
  <section id={s.id}>
    <h2>{s.titre}</h2>
    <div class="texte">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html s.html}
    </div>
  </section>
{/each}

<style>
  .sommaire {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
  }
  section {
    border-top: 1px solid var(--filet);
    margin-top: 2em;
  }
  /* Le tableau des décisions est plus large que la colonne de lecture. */
  .texte {
    max-width: none;
  }
  .texte :global(> p),
  .texte :global(> ul),
  .texte :global(> ol),
  .texte :global(> blockquote) {
    max-width: var(--colonne);
  }
</style>
