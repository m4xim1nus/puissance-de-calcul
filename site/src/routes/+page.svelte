<script lang="ts">
  import EnChantier from '$lib/EnChantier.svelte';
  import HeroPrix from '$lib/graphiques/HeroPrix.svelte';

  let { data } = $props();
</script>

<svelte:head>
  <title>Puissance de calcul</title>
  <meta
    name="description"
    content="Le système électrique français peut-il accueillir la vague de data centers, et à quelles conditions ? Données sourcées et datées."
  />
</svelte:head>

<h1 class="lecteur">Puissance de calcul : le système électrique français face aux data centers</h1>

<HeroPrix annees={data.annees} initiale={data.initiale} references={data.references} />

<section class="enquetes" aria-labelledby="enquetes-titre">
  <h2 id="enquetes-titre">Les enquêtes</h2>
  <div class="grille">
    <a class="enquete" href="/combien">
      <span class="etat">Enquête</span>
      <span class="titre">Combien ?</span>
      <span class="question"
        >Combien pèsent les data centers dans le système électrique français, aujourd’hui et dans
        dix ans&#8239;?</span
      >
      <span class="lire">Lire l’enquête →</span>
    </a>
    <EnChantier
      titre="Quand ?"
      manque="L’enquête n’est pas encore écrite."
      pourquoi="Les séries horaires de consommation, de production et de prix sont prêtes et contrôlées ; leur analyse heure par heure est en cours."
      viendra="À quelles heures une consommation supplémentaire et continue tombe sur un système tendu, et à quelles heures sur un système en excédent."
    />
    <EnChantier
      titre="Simulateur"
      manque="Le module de simulation n’est pas encore publié."
      pourquoi="Son modèle est en cours de spécification ; il sera décrit et testé avant d’être mis en ligne."
      viendra="Un outil où l’on règle la puissance et le profil d’un parc de data centers pour voir, heure par heure, ce qu’il ajoute au système."
    />
  </div>
</section>

<style>
  .enquetes h2 {
    margin-top: 0;
    font-size: 1.45rem;
  }
  .grille {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
    gap: 1rem;
    align-items: start;
  }
  .enquete {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    padding: 0.9rem 1rem;
    border: 1px solid var(--encre);
    border-radius: 4px;
    text-decoration: none;
    font-family: var(--sans);
  }
  .enquete:hover {
    background: var(--papier-2);
  }
  .etat {
    color: var(--encre-2);
    font-weight: 500;
  }
  .titre {
    font-size: 1.25rem;
    font-weight: 600;
  }
  .question {
    font-family: var(--serif);
    font-size: 0.95rem;
    line-height: 1.5;
  }
  .lire {
    font-weight: 600;
    margin-top: 0.3rem;
  }
</style>
