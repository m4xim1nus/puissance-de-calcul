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

<!-- La question d'abord, visible sans défiler ; puis ce que fait le site et ce que montre le
     calendrier. Aucune thèse : la page pose la question (décision de l'auteur, 2026-11-26). -->
<header class="ouverture">
  <h1>
    Le système électrique français peut-il accueillir la vague de data centers, et à quelles
    conditions&#8239;?
  </h1>
  <p>
    Ce site vérifie, chiffre et date ce qu’on peut en savoir avec les données publiques&nbsp;:
    combien les data centers consomment et consommeront, à quelles heures, où, et à quel prix. Il
    dit aussi où les données manquent ou se contredisent.
  </p>
  <p>
    Le calendrier ci-dessous montre l’un des signaux de l’état du système électrique&nbsp;: le prix
    de gros day-ahead en France, fixé la veille pour le lendemain, une case par heure, une ligne par
    jour. Une consommation qui tourne jour et nuit passe par toutes ces heures, les plus chères
    comme celles à prix négatif.
  </p>
</header>

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
    <a class="enquete" href="/quand">
      <span class="etat">Enquête</span>
      <span class="titre">{data.quand.titre}</span>
      <span class="question">{data.quand.question}</span>
      <span class="lire">Lire l’enquête →</span>
    </a>
    <EnChantier
      titre="Simulateur"
      manque="Le module de simulation n’est pas encore publié."
      pourquoi="Son modèle est en cours de spécification, à partir des séries horaires de l’enquête « Quand ? » ; il sera décrit et testé avant d’être mis en ligne."
      viendra="Un outil où l’on règle la puissance et le profil d’un parc de data centers pour voir, heure par heure, ce qu’il ajoute au système."
    />
  </div>
</section>

<style>
  .ouverture h1 {
    margin: 0.9rem 0 0.8rem;
    max-width: 22em;
    font-size: clamp(1.75rem, 1.25rem + 1.9vw, 2.5rem);
    line-height: 1.12;
  }
  .ouverture p {
    max-width: var(--mesure);
    margin: 0 0 0.6rem;
    font-size: 1.125rem;
    line-height: 1.55;
  }
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
