<script lang="ts">
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
  <TexteAnnote blocs={data.textes.enTete} />
  <Simulateur annees={data.annees} sources={data.sources} extractions={data.extractions} />
  <TexteAnnote blocs={data.textes.lecture} />
</article>

<style>
  .page-simulateur {
    max-width: var(--large);
  }
  .rubrique {
    margin: 1.5rem 0 0;
    font-family: var(--sans);
    font-weight: 500;
    color: var(--encre-2);
  }
  .tete h1 {
    margin-top: 0.1em;
  }
</style>
