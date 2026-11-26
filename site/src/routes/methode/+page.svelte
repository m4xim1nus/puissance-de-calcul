<script lang="ts">
  import { COTES, type Confiance, type Source } from '$lib/chiffres';
  import { formaterDate } from '$lib/format';
  import { dateSource } from '$lib/notes';
  import { page } from '$app/state';
  import { tick } from 'svelte';

  let { data } = $props();

  // Glossaire replié par défaut (lisible sans JavaScript) ; arrivée par une ancre #g-… : on le
  // déplie, puis on fait défiler jusqu'au terme (le navigateur n'a pas pu viser un repli fermé).
  let glossaireOuvert = $state(false);
  $effect(() => {
    const ancre = page.url.hash.slice(1);
    if (!ancre.startsWith('g-')) return;
    glossaireOuvert = true;
    tick().then(() => document.getElementById(decodeURIComponent(ancre))?.scrollIntoView());
  });

  const cotes = Object.entries(COTES) as [Confiance, string][];
  const publie = (s: Source) => {
    const d = dateSource(s);
    return /^\d/.test(d) ? `le ${d}` : `en ${d}`;
  };
</script>

<svelte:head>
  <title>Méthode · Puissance de calcul</title>
</svelte:head>

<div class="methode">
  <h1>Méthode</h1>
  <p class="chapeau">
    D’où viennent les chiffres du site, comment leur fiabilité est cotée, et ce que veulent dire les
    mots du métier. Page provisoire : les hypothèses de calcul et les contrôles de cohérence y
    seront détaillés au fil des enquêtes.
  </p>

  <h2 id="confiance">La cote de confiance</h2>
  <p>
    Chaque chiffre affiché vient d’une entrée unique du référentiel des chiffres, qui porte sa
    source, sa date, sa page, la citation exacte, sa période et son périmètre. Le chiffre et sa note
    sont générés depuis cette même entrée : aucun chiffre n’est tapé à la main dans une page. Chaque
    entrée reçoit une cote :
  </p>
  <dl class="cotes">
    {#each cotes as [lettre, sens] (lettre)}
      <div>
        <dt><span class="cote" aria-hidden="true">{lettre}</span> Confiance {lettre}</dt>
        <dd>{sens.charAt(0).toUpperCase() + sens.slice(1)}.</dd>
      </div>
    {/each}
  </dl>
  <p>
    Un chiffre sans recoupement est marqué « non recoupé » dans sa note. Un recoupement est dit
    indépendant quand il repose sur d’autres données que la source principale ; deux éditeurs qui
    exploitent les mêmes comptages ne se recoupent pas de façon indépendante. Quand le site dérive
    un chiffre d’une valeur publiée (une puissance moyenne tirée d’une énergie annuelle, une somme
    de capacités par site), la note l’indique par la mention « calcul du site » et donne le calcul.
  </p>

  <h2 id="sources">Sources</h2>
  <p>
    {data.sources.length} publications&#8239;: celles des {data.nombreChiffres} chiffres du référentiel,
    et celles que les pages citent sans en tirer de chiffre. Les dates de publication approchées au mois
    sont données au mois.
  </p>
  <ul class="sources">
    {#each data.sources as s (s.cle)}
      <li>
        <span class="editeur">{s.editeur}</span>,
        <a href={s.url} rel="external">{s.titre}</a>, publié {publie(s)}.
        <span class="secondaire">
          {#if s.consulte_le}Consulté le {formaterDate(s.consulte_le)}.{/if}
          {#if s.note}{s.note.charAt(0).toUpperCase() + s.note.slice(1)}.{/if}
          {#if s.chiffres}{s.chiffres}
            {s.chiffres > 1 ? 'chiffres' : 'chiffre'}.{:else}Citée sans chiffre.{/if}
        </span>
      </li>
    {/each}
  </ul>

  <h2 id="donnees">Données</h2>
  <p>
    Les séries horaires (calendrier de l’accueil, « Quand ? », « Quel carbone ? », simulateur)
    viennent de trois producteurs, sous licence ouverte. Elles sont téléchargées par le pipeline du
    site, contrôlées, puis figées dans le dépôt : le site publié ne télécharge rien. Le site sert
    les fichiers horaires par année close (<code>/donnees/horaire/AAAA.csv</code>)&#8239;; les
    métadonnées (<code>meta.json</code>) et la table complète (<code>systeme_horaire.parquet</code>)
    sont dans le dossier <code>data/export/</code> du
    <a href="https://github.com/m4xim1nus/puissance-de-calcul" rel="external">dépôt public</a>.
  </p>
  <ul class="sources">
    <li>
      <span class="editeur">Prix day-ahead France</span> : Bundesnetzagentur / SMARD.de via
      energy-charts.info (Fraunhofer ISE),
      <a href="https://creativecommons.org/licenses/by/4.0/" rel="external">CC BY 4.0</a>.
      <span class="secondaire">
        {#if data.donnees.extractionPrix}Extraction le {formaterDate(
            data.donnees.extractionPrix.derniere
          )} (heure de Paris).{/if}
        Au pas horaire jusqu’au 30 septembre 2025, au quart d’heure ensuite ; le prix d’une heure est
        alors la moyenne simple de ses quatre quarts d’heure (convention de RTE).
      </span>
    </li>
    <li>
      <span class="editeur">Consommation, production, échanges</span> : RTE, éCO2mix, via ODRÉ (Open
      Data Réseaux Énergies),
      <a href="https://www.etalab.gouv.fr/licence-ouverte-open-licence/" rel="external"
        >Licence Ouverte 2.0</a
      >.
      <span class="secondaire">
        {#if data.donnees.extractionEco2mix}Extraction le {formaterDate(
            data.donnees.extractionEco2mix.derniere
          )} (heure de Paris).{/if}
        Données définitives, consolidées puis temps réel selon l’ancienneté ; les cellules absentes ne
        sont jamais imputées.
      </span>
    </li>
    <li>
      <span class="editeur">Disponibilité nucléaire déclarée</span> : EDF, indisponibilités des
      moyens de production (REMIT), opendata.edf.fr,
      <a href="https://www.etalab.gouv.fr/licence-ouverte-open-licence/" rel="external"
        >Licence Ouverte 2.0</a
      >.
      <span class="secondaire">
        {#if data.donnees.extractionRemit}Extraction le {formaterDate(
            data.donnees.extractionRemit.derniere
          )} (heure de Paris).{/if}
        Historique depuis 2015 et liste courante ; puissance déclarée disponible, reconstruite heure par
        heure par le site (colonne <code>nucleaire_disponible</code>).
      </span>
    </li>
  </ul>
  <details class="lisezmoi">
    <summary
      >Format des séries horaires (copie de data/export/horaire/LISEZMOI.md du dépôt&#8239;; ses
      chemins relatifs renvoient au dossier data/export/)</summary
    >
    <div class="texte-lisezmoi">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html data.donnees.lisezmoi}
    </div>
  </details>

  <h2 id="glossaire">Glossaire</h2>
  <p>
    Le sens retenu par ce site pour les termes du métier, en {data.glossaire.length} entrées. Les pages
    y renvoient par un lien discret, à la première occurrence du terme.
  </p>
  <details class="glossaire" bind:open={glossaireOuvert}>
    <summary>Afficher le glossaire</summary>
    <dl>
      {#each data.glossaire as e (e.id)}
        <div class="terme" id="g-{e.id}">
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          <dt>{@html e.terme}</dt>
          <dd>
            <!-- eslint-disable-next-line svelte/no-at-html-tags -->
            {@html e.definition}
            {#if e.source}
              <!-- eslint-disable-next-line svelte/no-at-html-tags -->
              <span class="source-terme">Source&nbsp;: {@html e.source}</span>
            {/if}
          </dd>
        </div>
      {/each}
    </dl>
  </details>
</div>

<style>
  .methode {
    max-width: var(--mesure);
  }
  .cotes {
    margin: 0 0 1.2em;
  }
  .cotes div {
    display: grid;
    grid-template-columns: 9rem 1fr;
    gap: 0 1rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid var(--trait);
  }
  .cotes dt {
    font-family: var(--sans);
    font-weight: 600;
  }
  .cotes dd {
    margin: 0;
  }
  .cote {
    display: inline-block;
    min-width: 1.35em;
    text-align: center;
    border: 1.5px solid var(--encre);
    border-radius: 3px;
    line-height: 1.25;
    margin-right: 0.2rem;
  }
  .sources {
    padding-left: 0;
    list-style: none;
  }
  .sources li {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--trait);
    margin: 0;
  }
  .editeur {
    font-family: var(--sans);
    font-weight: 600;
  }
  .secondaire {
    display: block;
    color: var(--encre-2);
    font-size: 0.9rem;
  }
  .lisezmoi {
    margin-bottom: 1.5rem;
  }
  .texte-lisezmoi {
    font-size: 0.95rem;
  }
  .texte-lisezmoi :global(table) {
    font-size: 0.85rem;
  }
  .glossaire dl {
    margin-top: 0.75rem;
  }
  .terme {
    padding: 0.55rem 0 0.65rem;
    border-bottom: 1px solid var(--trait);
    scroll-margin-top: 1rem;
  }
  .terme:target {
    box-shadow: inset 3px 0 0 var(--signal);
    padding-left: 0.8rem;
  }
  .glossaire dt {
    font-family: var(--sans);
    font-weight: 600;
  }
  .glossaire dd {
    margin: 0.15rem 0 0;
  }
  .source-terme {
    display: block;
    margin-top: 0.25rem;
    color: var(--encre-2);
    font-size: 0.9rem;
  }
  @media (max-width: 30rem) {
    .cotes div {
      grid-template-columns: 1fr;
    }
  }
</style>
