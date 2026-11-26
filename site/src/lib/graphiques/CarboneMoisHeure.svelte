<script lang="ts">
  // Intensité carbone MOYENNE de la production, mois × heure de Paris, 2022 et dernière année
  // pleine côte à côte, même échelle séquentielle. SVG en viewBox : lisible sans JavaScript, à
  // toute largeur. Ce n'est pas un facteur marginal : le sous-titre et les remarques le disent.
  import { INSECABLE } from '$lib/format';
  import {
    JETONS_CO2,
    classeCo2,
    grammes,
    libelleClasseCo2,
    sourcesCarbone,
    type AnneeCarbone
  } from '$lib/carbone';
  import Figure from './Figure.svelte';
  import { donneesCarbone, type PropsGraphique } from './registre';

  let { donnees }: PropsGraphique = $props();
  const d = $derived(donneesCarbone(donnees));
  const annees = $derived(d.matrices.map((m) => m.annee).join(' et '));
  const parAnnee = $derived(
    new Map<number, AnneeCarbone>(d.annees.map((a) => [a.annee, a] as const))
  );

  const MOIS_COURTS = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];
  const MOIS = [
    'janvier',
    'février',
    'mars',
    'avril',
    'mai',
    'juin',
    'juillet',
    'août',
    'septembre',
    'octobre',
    'novembre',
    'décembre'
  ];
  const NOMS_MOIS = MOIS.map((m) => m[0].toUpperCase() + m.slice(1));

  // Géométrie du viewBox (unités SVG ; le dessin se met à l'échelle de sa colonne).
  const GAUCHE = 16;
  const HAUT = 14;
  const CASE = 15;
  const LARGEUR = GAUCHE + 24 * CASE;
  const HAUTEUR = HAUT + 12 * CASE;

  const plage = (h: number) => `${h}${INSECABLE}h – ${(h + 1) % 24}${INSECABLE}h`;
  const valeur = (v: number | null) => (v === null ? '—' : grammes(v, false));
</script>

<Figure
  id="carbone-mois-heure"
  titre="Intensité carbone moyenne de la production, par mois et par heure, {annees}"
  sousTitre="En gCO2eq par kWh produit, émissions directes. Une ligne par mois, de janvier (en haut) à décembre ; une colonne par heure de début, en heure de Paris. Chaque case est la moyenne de l’intensité horaire d’éCO2mix sur les jours du mois, pondérée par la production. C’est une moyenne : elle ne dit pas ce qu’une consommation ajoutée ferait émettre."
  remarques="Même échelle pour les deux années ; au-delà de 60 g, la couleur sature. France continentale hors Corse : le Bilan électrique de RTE, Corse comprise et avec d’autres facteurs d’émission, donne des moyennes annuelles un peu plus hautes. Valeur exacte de chaque case au survol et, mois par mois, dans le tableau des données."
  sources={sourcesCarbone(d)}
  titreTableau="Tableau des données : intensité moyenne par mois, {annees}"
>
  {#snippet legende()}
    <div class="echelle-bloc">
      <ul class="classes" aria-label="Classes de couleur, en gCO2eq/kWh">
        {#each JETONS_CO2 as j, k (j)}
          <li>
            <span class="pastille" style:background="var({j})" aria-hidden="true"></span>
            {libelleClasseCo2(k)}
          </li>
        {/each}
      </ul>
      <p class="legende-texte">gCO2eq/kWh, intensité moyenne de la production.</p>
    </div>
  {/snippet}

  {#snippet trace(_largeur: number)}
    <div class="paire">
      {#each d.matrices as m (m.annee)}
        <div class="panneau">
          <p class="annee">
            {m.annee}
            <span class="moyenne"
              >moyenne de l’année {grammes(parAnnee.get(m.annee)!.production.moyenne)}</span
            >
          </p>
          <svg
            viewBox="0 0 {LARGEUR} {HAUTEUR}"
            role="img"
            aria-label="Intensité moyenne de la production en {m.annee}, par mois et par heure ; valeurs mensuelles dans le tableau des données."
          >
            {#each [0, 6, 12, 18] as h (h)}
              <text class="axe" x={GAUCHE + h * CASE + 1} y="10">{h}{INSECABLE}h</text>
            {/each}
            {#each m.valeurs as ligne, i (i)}
              <text class="axe" x="0" y={HAUT + i * CASE + CASE * 0.72}>{MOIS_COURTS[i]}</text>
              {#each ligne as v, h (h)}
                <rect
                  x={GAUCHE + h * CASE}
                  y={HAUT + i * CASE}
                  width={CASE - 1}
                  height={CASE - 1}
                  style:fill={v === null
                    ? 'var(--prix-absent)'
                    : `var(${JETONS_CO2[classeCo2(v)]})`}
                  ><title
                    >{MOIS[i]}
                    {m.annee}, {plage(h)} : {v === null ? 'pas de donnée' : grammes(v)}</title
                  ></rect
                >
              {/each}
            {/each}
          </svg>
        </div>
      {/each}
    </div>
  {/snippet}

  {#snippet tableau()}
    <table>
      <caption class="lecteur">Intensité carbone moyenne par mois, en gCO2eq/kWh</caption>
      <thead>
        <tr>
          <th scope="col" rowspan="2">Mois</th>
          {#each d.matrices as m (m.annee)}
            <th scope="colgroup" colspan="2" class="groupe">{m.annee}</th>
          {/each}
        </tr>
        <tr>
          {#each d.matrices as m (m.annee)}
            <th scope="col" class="num">Production</th>
            <th scope="col" class="num">Consommation</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each NOMS_MOIS as nom, k (nom)}
          <tr>
            <th scope="row">{nom}</th>
            {#each d.matrices as m (m.annee)}
              {@const a = parAnnee.get(m.annee)!}
              <td class="num">{valeur(a.production.profilMensuel[k])}</td>
              <td class="num">{a.consommation ? valeur(a.consommation.profilMensuel[k]) : '—'}</td>
            {/each}
          </tr>
        {/each}
        <tr class="total">
          <th scope="row">Année</th>
          {#each d.matrices as m (m.annee)}
            {@const a = parAnnee.get(m.annee)!}
            <td class="num">{grammes(a.production.moyenne, false)}</td>
            <td class="num">{a.consommation ? grammes(a.consommation.moyenne, false) : '—'}</td>
          {/each}
        </tr>
      </tbody>
    </table>
    <p class="note-tableau">
      gCO2eq/kWh, émissions directes, moyennes pondérées (production : par la production ;
      consommation : par la consommation). Production : éCO2mix ; consommation : série de RTE,
      échanges compris. Toutes deux sont des moyennes, pas des facteurs marginaux. Calcul du site
      (data/export/carbone.json).
    </p>
  {/snippet}
</Figure>

<style>
  .echelle-bloc {
    width: 100%;
  }
  .classes {
    display: flex;
    flex-wrap: wrap;
    gap: 0.2rem 1rem;
    margin: 0;
    padding: 0;
    list-style: none;
    font-variant-numeric: tabular-nums;
  }
  .classes li {
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .pastille {
    display: inline-block;
    width: 0.9rem;
    height: 0.9rem;
    border-radius: 2px;
    box-shadow: inset 0 0 0 1px var(--trait);
  }
  .legende-texte {
    margin: 0.2rem 0 0;
    font-size: 0.875rem;
    color: var(--encre-2);
  }
  .paire {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr));
    gap: 1.25rem 2rem;
    max-width: 52rem;
  }
  .annee {
    margin: 0 0 0.3rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
  .moyenne {
    margin-left: 0.4rem;
    font-weight: 400;
    color: var(--encre-2);
  }
  svg {
    display: block;
    width: 100%;
    height: auto;
  }
  .axe {
    font-family: var(--sans);
    font-size: 9px;
    fill: var(--encre-2);
  }
  rect:hover {
    stroke: var(--encre);
    stroke-width: 1.5;
  }
  .groupe {
    text-align: center;
    border-bottom-color: var(--trait);
  }
  .total th,
  .total td {
    font-weight: 600;
  }
  .note-tableau {
    font-size: 0.85rem;
    color: var(--encre-2);
    max-width: 46rem;
  }
</style>
