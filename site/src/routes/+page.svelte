<script lang="ts">
  import { formaterDate } from '$lib/format';
  import HeroPrix from '$lib/graphiques/HeroPrix.svelte';
  import TexteAnnote from '$lib/simulateur/TexteAnnote.svelte';

  let { data } = $props();
  const m = $derived(data.message);
</script>

<svelte:head>
  <title>Puissance de calcul</title>
  <meta
    name="description"
    content="Le système électrique français peut-il accueillir la vague de data centers, et à quelles conditions ? Données sourcées et datées."
  />
</svelte:head>

<!-- Accueil refait en session 4 (retour de l'auteur, 26/11/2026) : la question, le message à
     retenir en quatre points, un chiffre fort par enquête avec son lien, puis le calendrier des
     prix ; le message complet, daté, est replié en bas. -->
<header class="ouverture">
  <h1>
    Le système électrique français peut-il accueillir la vague de data centers, et à quelles
    conditions&#8239;?
  </h1>
  <p class="chapeau">
    Ce site part d’une hypothèse&#8239;: en moyenne sur l’année, l’électricité française est
    abondante et décarbonée, mais cette moyenne ne tranche rien&#8239;; la question se joue à
    l’heure, au <a class="glossaire" href="/methode#g-poste-electrique">poste électrique</a> et au prix.
    Il vérifie, chiffre et date ce qu’en disent les données publiques, et dit où elles manquent.
  </p>
</header>

<section class="retenir" aria-labelledby="retenir-titre">
  <div class="retenir-tete">
    <h2 id="retenir-titre">À retenir</h2>
    <p class="meta">
      Au {formaterDate(m.miseAJour)}, version {m.version}, d’après {m.reposeSur}.
      <a href="#message">Le message en détail ↓</a>
    </p>
  </div>
  <TexteAnnote blocs={m.retenir} />
</section>

<section class="enquetes" aria-labelledby="enquetes-titre">
  <h2 id="enquetes-titre">Les enquêtes, en un chiffre</h2>
  <div class="grille">
    {#each data.accroches as a (a.slug)}
      <article class="carte-enquete">
        <h3><a href="/{a.slug}">{a.titre}</a></h3>
        <!-- eslint-disable svelte/no-at-html-tags -->
        <p class="fort" class:long={a.long}>{@html a.chiffre}</p>
        <p class="suite">{@html a.suite}</p>
        <details class="notes-carte">
          <summary>Sources</summary>
          <div class="notes-corps">{@html a.notes}</div>
        </details>
        <!-- eslint-enable svelte/no-at-html-tags -->
        <a class="lire" href="/{a.slug}">Lire l’enquête<span class="lecteur"> {a.titre}</span> →</a>
      </article>
    {/each}
    <article class="carte-enquete simulateur">
      <h3><a href="/simulateur">Simulateur</a></h3>
      <p class="fort">Et avec 5&#8239;GW de plus&#8239;?</p>
      <p class="suite">
        Ajoute une consommation plate à une année observée, heure par heure, avec ou sans
        <a class="glossaire" href="/methode#g-effacement">effacement</a> aux heures les plus
        tendues, et regarde ce qui change&#8239;: l’énergie, la part trouvée dans le nucléaire
        disponible non produit, les heures où la
        <a class="glossaire" href="/methode#g-charge-residuelle">charge résiduelle</a>
        dépasse son maximum observé, les prix. Les hypothèses sont affichées, et plusieurs se règlent.
      </p>
      <a class="lire" href="/simulateur?x=5">Ouvrir le simulateur avec 5&#8239;GW →</a>
    </article>
  </div>
</section>

<section class="pourquoi" aria-label="Pourquoi heure par heure">
  <p>
    Pourquoi regarder heure par heure&#8239;? Parce qu’une consommation qui tourne jour et nuit
    passe par toutes les heures de l’année, les plus chères comme celles à
    <a class="glossaire" href="/methode#g-prix-negatif">prix négatif</a>. Le calendrier ci-dessous
    en montre un signal&#8239;: le
    <a class="glossaire" href="/methode#g-prix-de-gros">prix de gros</a>
    <a class="glossaire" href="/methode#g-day-ahead">day-ahead</a> en France, fixé la veille pour le lendemain,
    une case par heure, une ligne par jour.
  </p>
  <p>
    En 2025, les heures à prix négatif (en vert) tombent surtout en milieu de journée, d’avril à
    septembre&#8239;; les plus chères, surtout en janvier et février, le matin et le soir. Le prix
    n’a pas encore son enquête&#8239;: ce calendrier en est la matière première.
  </p>
</section>

<HeroPrix annees={data.annees} initiale={data.initiale} references={data.references} />

<section id="message" class="message" aria-labelledby="message-titre">
  <details>
    <summary>
      <h2 id="message-titre">{m.titre}</h2>
      <span class="meta"
        >Le message complet, version {m.version} du {formaterDate(m.miseAJour)}, et ce qui a changé</span
      >
    </summary>
    <TexteAnnote blocs={m.detail} />
    <h3>Ce qui a changé</h3>
    <TexteAnnote blocs={m.changements} />
  </details>
</section>

<style>
  .ouverture h1 {
    margin: 0.9rem 0 0.7rem;
    max-width: 22em;
    font-size: clamp(1.75rem, 1.25rem + 1.9vw, 2.6rem);
    line-height: 1.12;
  }
  .chapeau {
    max-width: var(--mesure);
    margin: 0 0 1.4rem;
    font-size: 1.15rem;
    line-height: 1.55;
    color: var(--encre-2);
  }

  .retenir {
    margin: 0 0 2.2rem;
    border-top: 3px solid var(--signal);
  }
  .retenir-tete {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.2rem 1rem;
    margin: 0.7rem 0 0.4rem;
  }
  .retenir h2 {
    margin: 0;
    font-size: 1.3rem;
  }
  .meta {
    margin: 0;
    font-family: var(--sans);
    font-size: 0.95rem;
    color: var(--encre-2);
  }
  .retenir :global(li + li) {
    margin-top: 0.6rem;
  }

  .enquetes {
    margin-bottom: 2.4rem;
  }
  .enquetes h2 {
    margin-top: 0;
    font-size: 1.45rem;
  }
  .grille {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr));
    gap: 1rem;
  }
  .carte-enquete {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    padding: 0.9rem 1rem 1rem;
    border: 1px solid var(--encre);
    border-top-width: 4px;
    border-radius: 4px;
  }
  .carte-enquete h3 {
    margin: 0;
    font-family: var(--sans);
    font-size: 1.05rem;
    font-weight: 600;
  }
  .carte-enquete h3 a {
    text-decoration: none;
  }
  .fort {
    margin: 0.1rem 0 0;
    font-family: var(--sans);
    font-size: clamp(1.9rem, 1.4rem + 1.6vw, 2.5rem);
    font-weight: 600;
    line-height: 1.1;
  }
  .fort :global(.chiffre) {
    background: linear-gradient(
      transparent 62%,
      var(--signal) 62%,
      var(--signal) 92%,
      transparent 92%
    );
    color: var(--encre);
  }
  .fort.long {
    font-size: clamp(1.5rem, 1.2rem + 0.9vw, 1.85rem);
  }
  .fort :global(sup) {
    font-size: 0.4em;
  }
  .suite {
    margin: 0;
    font-size: 0.98rem;
    line-height: 1.5;
  }
  .carte-enquete.simulateur {
    grid-column: 1 / -1;
    border-top-color: var(--signal);
  }
  .notes-carte {
    font-family: var(--sans);
    font-size: 0.85rem;
    color: var(--encre-2);
  }
  .notes-carte summary {
    cursor: pointer;
  }
  .notes-carte :global(.note + .note) {
    margin-top: 0.4rem;
  }
  .lire {
    margin-top: auto;
    padding-top: 0.3rem;
    font-family: var(--sans);
    font-weight: 600;
  }
  .lecteur {
    position: absolute;
    left: -100vw;
  }

  .pourquoi p {
    max-width: var(--mesure);
    margin: 0 0 0.6rem;
    font-size: 1.05rem;
    line-height: 1.55;
  }

  .message {
    margin-top: 2.4rem;
    border-top: 1px solid var(--trait);
  }
  .message summary {
    cursor: pointer;
    padding: 0.8rem 0 0.4rem;
  }
  .message summary h2 {
    display: inline;
    margin: 0;
    font-size: 1.3rem;
  }
  .message summary .meta {
    display: block;
    margin-top: 0.2rem;
  }
  .message h3 {
    margin-top: 1.6rem;
    font-size: 1.15rem;
  }
</style>
