<script lang="ts">
  // Page /simulateur : l'outil, en pleine fenêtre sur ordinateur (retours de l'auteur du
  // 2026-11-26 : « pas possible de le repenser pour se régler en pleine page non scrollable sur
  // desktop ? »). Le texte d'en-tête et le texte de lecture, inchangés, sont dans la notice de
  // l'outil (panneau latéral avec JavaScript, texte dans le flux sans) : voir Simulateur.svelte.
  import Simulateur from '$lib/simulateur/Simulateur.svelte';

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
  <Simulateur
    annees={data.annees}
    sources={data.sources}
    extractions={data.extractions}
    references={data.references}
    enTete={data.enTete}
    lecture={data.lecture}
  >
    {#snippet tete()}
      <header class="titre">
        <p class="rubrique">Simulateur</p>
        <h1>Une consommation de plus, heure par heure</h1>
      </header>
    {/snippet}
  </Simulateur>
</article>

<style>
  /* L'outil prend plus large que la colonne de lecture du site : réglages, quatre tuiles de
     résultats par ligne et deux panneaux de graphique côte à côte. */
  .page-simulateur {
    --page: min(100rem, calc(100vw - 2 * var(--bord) - 1rem));
    width: var(--page);
    margin-left: calc((100% - var(--page)) / 2);
  }
  @media (max-width: 62rem) {
    .page-simulateur {
      --page: 100%;
    }
  }
  /* Pleine fenêtre sur ordinateur : la page occupe exactement la hauteur de la fenêtre (bandeau du
     site compris) et l'outil prend ce qui reste sous le bandeau. Sans JavaScript, la notice suit
     l'outil dans le flux et la page défile ; avec, le pied de page est masqué (il ferait défiler
     la page pour une ligne). */
  @media (min-width: 62rem) and (min-height: 36rem) {
    :global(body:has(.page-simulateur)) {
      display: flex;
      flex-direction: column;
      min-height: 100dvh;
    }
    :global(main:has(.page-simulateur)) {
      flex: 1 0 auto;
      display: flex;
      flex-direction: column;
      min-height: 0;
      padding-top: 0.6rem;
      padding-bottom: 0.75rem;
    }
    :global(main:has(.page-simulateur .outil.js)) {
      flex: 1 1 0;
    }
    :global(main:has(.page-simulateur .outil.js) + .pied) {
      display: none;
    }
    .page-simulateur {
      flex: 1 1 auto;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }
  }
  .titre {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0 0.75rem;
  }
  .rubrique {
    margin: 0;
    font-family: var(--sans);
    font-weight: 500;
    color: var(--encre-2);
  }
  h1 {
    margin: 0;
    font-size: clamp(1.5rem, 1.3rem + 0.6vw, 1.75rem);
    line-height: 1.15;
  }
</style>
