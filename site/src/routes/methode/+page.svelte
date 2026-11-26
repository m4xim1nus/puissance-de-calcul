<script lang="ts">
  import { COTES, type Confiance, type Source } from '$lib/chiffres';
  import { formaterDate } from '$lib/format';
  import { dateSource } from '$lib/notes';

  let { data } = $props();

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
    {data.sources.length} publications, citées par les {data.nombreChiffres} chiffres du référentiel.
    Les dates de publication approchées au mois sont données au mois.
  </p>
  <ul class="sources">
    {#each data.sources as s (s.cle)}
      <li>
        <span class="editeur">{s.editeur}</span>,
        <a href={s.url} rel="external">{s.titre}</a>, publié {publie(s)}.
        <span class="secondaire">
          {#if s.consulte_le}Consulté le {formaterDate(s.consulte_le)}.{/if}
          {#if s.note}{s.note.charAt(0).toUpperCase() + s.note.slice(1)}.{/if}
          {s.chiffres}
          {s.chiffres > 1 ? 'chiffres' : 'chiffre'}.
        </span>
      </li>
    {/each}
  </ul>

  <h2 id="donnees">Données</h2>
  <p>
    Les séries horaires (hero de l’accueil, enquêtes à venir) viennent de deux producteurs, sous
    licence ouverte. Elles sont téléchargées par le pipeline du site, contrôlées, puis figées dans
    le dépôt : le site publié ne télécharge rien.
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
  </ul>
  <details class="lisezmoi">
    <summary>Format des séries horaires (copie de data/export/horaire/LISEZMOI.md)</summary>
    <div class="texte-lisezmoi">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html data.donnees.lisezmoi}
    </div>
  </details>

  <h2 id="glossaire">Glossaire</h2>
  <details class="glossaire">
    <summary>Afficher le glossaire</summary>
    <dl>
      <dt>Puissance recherchée</dt>
      <dd>
        Puissance électrique que des porteurs de projets déclarent rechercher, telle que l’État
        l’annonce pour les projets qu’il accompagne. Aucune définition publiée ; ce n’est ni un
        droit d’accès au réseau ni un engagement.
      </dd>
      <dt>Puissance réservée</dt>
      <dd>
        Capacité d’accès au réseau réservée par le gestionnaire pour un projet, une fois sa
        proposition technique et financière (PTF) signée. C’est un droit d’accès, avec une place
        dans la file d’attente ; il n’engage pas à consommer et peut être abandonné.
      </dd>
      <dt>Puissance pré-réservée (fast-track)</dt>
      <dd>
        Capacité que RTE réserve, à la demande de l’État, sur un site identifié, avant qu’un porteur
        de projet ne s’y engage. Elle est temporaire.
      </dd>
      <dt>Puissance signée</dt>
      <dd>
        Puissance de raccordement inscrite dans le contrat de raccordement, avec un calendrier de
        mise à disposition, souvent par paliers. Ce n’est pas une date de mise en service de
        l’installation.
      </dd>
      <dt>Puissance raccordée</dt>
      <dd>
        Puissance de raccordement des installations effectivement raccordées : la puissance maximale
        qu’elles peuvent soutirer au réseau selon leur contrat. Une capacité, pas une consommation.
      </dd>
      <dt>Puissance appelée</dt>
      <dd>
        Puissance effectivement soutirée au réseau, à un instant donné ou en moyenne sur une période
        (l’énergie consommée divisée par la durée ; sur un an, 8 760 heures, 8 784 en année
        bissextile).
      </dd>
      <dt>PTF</dt>
      <dd>
        Proposition technique et financière : offre du gestionnaire de réseau qui décrit la solution
        de raccordement, son coût et son délai. Son acceptation, avec le versement du premier
        acompte, fait entrer le projet dans la file d’attente et réserve la capacité.
      </dd>
      <dt>RPT</dt>
      <dd>
        Réseau public de transport d’électricité : haute et très haute tension (HTB, au-delà de 50
        kV), exploité par RTE.
      </dd>
      <dt>RPD</dt>
      <dd>
        Réseau public de distribution : moyenne et basse tension (HTA et BT, jusqu’à 50 kV),
        exploité par Enedis sur l’essentiel du territoire métropolitain et par des entreprises
        locales de distribution ailleurs.
      </dd>
      <dt>Fast-track</dt>
      <dd>
        Procédure de raccordement accéléré encadrée par la CRE (<a
          href="https://www.cre.fr/fileadmin/Documents/Deliberations/2025/250507_2025-120_Procedure_raccordement_Fast_track.pdf"
          rel="external">délibération n° 2025-120 du 7 mai 2025</a
        >), destinée à des consommateurs de très forte puissance raccordés en 400 kV sur des sites
        préalablement identifiés par l’État.
      </dd>
      <dt>MW et MWh</dt>
      <dd>
        Le MW mesure une puissance, un débit d’énergie à un instant ; le MWh mesure une énergie, une
        puissance maintenue pendant une durée (1 MW pendant une heure donne 1 MWh ; 1 TWh vaut un
        million de MWh). Une série au pas de 30 minutes exprimée en MW se somme en MWh avec un
        facteur 0,5.
      </dd>
      <dt>Facteur d’émission moyen et marginal</dt>
      <dd>
        Moyen : émissions de l’ensemble de la production (ou de la consommation, échanges compris)
        rapportées à l’énergie, sur une période donnée. Marginal : variation des émissions provoquée
        par une variation de la consommation, c’est-à-dire les émissions des moyens qui s’ajustent à
        la marge ; il dépend de l’heure et de l’horizon retenu (exploitation à court terme, ou
        évolution du parc à long terme). L’un ne remplace pas l’autre : chaque chiffre carbone du
        site dit lequel il est.
      </dd>
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
  .glossaire dt {
    font-family: var(--sans);
    font-weight: 600;
    margin-top: 0.9rem;
  }
  .glossaire dd {
    margin: 0.15rem 0 0;
  }
  @media (max-width: 30rem) {
    .cotes div {
      grid-template-columns: 1fr;
    }
  }
</style>
