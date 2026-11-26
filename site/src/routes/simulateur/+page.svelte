<script lang="ts">
  // Page /simulateur : l'outil d'abord, tenu sur un écran d'ordinateur portable (retour de l'auteur
  // du 2026-11-26 : « le simulateur ne devrait pas être scrollable »). Le texte d'en-tête et le texte
  // de lecture sont inchangés, rangés en replis : l'en-tête juste au-dessus de l'outil (ce que le
  // simulateur ne modélise pas, à un clic), la lecture après les résultats, une section par repli.
  import Simulateur from '$lib/simulateur/Simulateur.svelte';
  import TexteAnnote from '$lib/simulateur/TexteAnnote.svelte';

  let { data } = $props();
</script>

<svelte:head>
  <title>Simulateur · Puissance de calcul</title>
  <meta
    name="description"
    content="Ajouter une consommation de X GW à une année observée du système électrique français, heure par heure : énergie, nucléaire disponible non produit, heures au-delà du maximum observé, prix observés."
  />
</svelte:head>

<article class="page-simulateur">
  <header class="tete">
    <p class="rubrique">Simulateur</p>
    <h1>Une consommation de plus, heure par heure</h1>
  </header>

  <details class="repli presentation" id="presentation">
    <summary
      ><span class="intitule">Ce que fait le simulateur, et ce qu’il ne modélise pas</span></summary
    >
    <div class="repli-corps">
      <TexteAnnote blocs={data.enTete} />
    </div>
  </details>

  <Simulateur
    annees={data.annees}
    sources={data.sources}
    extractions={data.extractions}
    references={data.references}
    lienLecture="#lecture-1"
  />

  <div class="lecture">
    {#each data.lecture as s, i (i)}
      <details class="repli" id="lecture-{i + 1}">
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
        <summary><h2 class="intitule">{@html s.titre}</h2></summary>
        <div class="repli-corps">
          <TexteAnnote blocs={[s.html]} />
        </div>
      </details>
    {/each}
  </div>
</article>

<style>
  /* L'outil prend plus large que la colonne de lecture du site : trois tuiles de résultats par
     ligne à côté des réglages. Le texte replié garde la colonne et sa marge de notes. */
  .page-simulateur {
    --page: min(76rem, calc(100vw - 2 * var(--bord) - 1rem));
    width: var(--page);
    margin-left: calc((100% - var(--page)) / 2);
  }
  @media (max-width: 62rem) {
    .page-simulateur {
      --page: 100%;
    }
  }
  .rubrique {
    margin: 0;
    font-family: var(--sans);
    font-weight: 500;
    color: var(--encre-2);
  }
  .tete h1 {
    margin: 0 0 0.6rem;
    font-size: clamp(1.75rem, 1.4rem + 1.2vw, 2.1rem);
  }
  .repli {
    max-width: var(--large);
    border-top: 1px solid var(--trait);
  }
  .repli:last-child {
    border-bottom: 1px solid var(--trait);
  }
  .repli > summary {
    padding: 0.45rem 0;
    color: var(--encre);
  }
  .intitule {
    display: inline;
    margin: 0;
    font-family: var(--sans);
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.3;
  }
  .repli-corps {
    padding: 0 0 1rem;
  }
  .repli-corps :global(.texte-annote > :first-child) {
    margin-top: 0.25rem;
  }
  .repli-corps :global(.texte-annote h2) {
    margin-top: 1.4em;
    font-size: 1.3rem;
  }
  .presentation {
    margin: 0 0 1rem;
    border-bottom: 1px solid var(--trait);
  }
  .lecture {
    margin-top: 1rem;
  }
</style>
