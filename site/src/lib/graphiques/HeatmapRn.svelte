<script lang="ts">
  // Charge résiduelle jour × heure de Paris, 2022 et 2025 côte à côte, même échelle. Même
  // grammaire que le calendrier des prix de l'accueil, en plus petit et sans sélecteur : ce n'est
  // pas une seconde « audace ». Sans JavaScript, le tableau mensuel reste lisible.
  import { onMount } from 'svelte';
  import { FINE, formaterNombre } from '$lib/format';
  import {
    JETONS_RN,
    SEUILS_RN,
    gw,
    libelleClasseRn,
    sourcesRn,
    statsMensuelles
  } from '$lib/quand';
  import CalendrierRn from './CalendrierRn.svelte';
  import Figure from './Figure.svelte';
  import { donneesQuand, type PropsGraphique } from './registre';

  let { donnees }: PropsGraphique = $props();
  const q = $derived(donneesQuand(donnees));
  const matrices = $derived(q.matrices);
  const stats = $derived(matrices.map((m) => ({ annee: m.annee, mois: statsMensuelles(m) })));
  const NOMS_MOIS = [
    'Janvier',
    'Février',
    'Mars',
    'Avril',
    'Mai',
    'Juin',
    'Juillet',
    'Août',
    'Septembre',
    'Octobre',
    'Novembre',
    'Décembre'
  ];
  const annees = $derived(matrices.map((m) => m.annee).join(' et '));
  // Les calendriers sont des canvas : sans JavaScript, ils resteraient vides. On ne les rend
  // qu'après le chargement ; sinon, le message et le tableau mensuel suffisent.
  let pret = $state(false);
  onMount(() => (pret = true));
</script>

<Figure
  id="heatmap-rn"
  titre="Charge résiduelle heure par heure, {annees}"
  sousTitre="En GW, moyenne de chaque heure. Une ligne par jour, du 1er janvier (en haut) au 31 décembre ; une colonne par heure de début, en heure de Paris. Brun : à fournir par le reste du système (hydraulique, thermique, bioénergies, échanges, stockage, effacements) ; bleu-vert : surplus avant exports et pompage."
  remarques="Même échelle pour les deux années. Gris : heure absente (passage à l’heure d’été) ou donnée manquante ; l’heure répétée du passage à l’heure d’hiver est la moyenne de ses deux occurrences. Valeur exacte dans l’infobulle."
  sources={sourcesRn(q)}
  titreTableau="Tableau des données : charge résiduelle par mois, {annees}"
>
  {#snippet legende()}
    <div class="echelle-bloc">
      <div class="echelle" aria-hidden="true">
        {#each JETONS_RN as j, i (j)}
          <span class="classe" class:zero={i === 4} style:background="var({j})"></span>
        {/each}
      </div>
      <div class="graduations" aria-hidden="true">
        {#each SEUILS_RN as s, i (s)}
          <span style:left="{((i + 1) / JETONS_RN.length) * 100}%" class:zero={s === 0}
            >{formaterNombre(s / 1000, 0)}</span
          >
        {/each}
      </div>
      <p class="lecteur">
        Classes de couleur : {JETONS_RN.map((_, i) => libelleClasseRn(i)).join(' ; ')}.
      </p>
      <p class="legende-texte">
        GW. <span class="fort">Sous zéro</span> à gauche (surplus), au-dessus à droite (à fournir).
        Au-delà de {formaterNombre(SEUILS_RN.at(-1)! / 1000, 0)}{FINE}GW ou en deçà de
        {formaterNombre(SEUILS_RN[0] / 1000, 0)}{FINE}GW, la couleur sature.
      </p>
    </div>
  {/snippet}

  {#snippet trace(_largeur: number)}
    {#if pret}
      <div class="paire">
        {#each matrices as m (m.annee)}
          <div class="panneau">
            <p class="annee">{m.annee}</p>
            <CalendrierRn matrice={m} />
          </div>
        {/each}
      </div>
    {/if}
    <noscript
      ><p class="sans-js">
        Les calendriers demandent JavaScript ; les statistiques mensuelles sont dans le tableau
        ci-dessous.
      </p></noscript
    >
  {/snippet}

  {#snippet tableau()}
    <table>
      <caption class="lecteur">Charge résiduelle par mois, en GW</caption>
      <thead>
        <tr>
          <th scope="col" rowspan="2">Mois</th>
          {#each stats as s (s.annee)}
            <th scope="colgroup" colspan="4" class="groupe">{s.annee}</th>
          {/each}
        </tr>
        <tr>
          {#each stats as s (s.annee)}
            <th scope="col" class="num">Moyenne</th>
            <th scope="col" class="num">Maximum</th>
            <th scope="col" class="num">Minimum</th>
            <th scope="col" class="num">Heures au-dessus de 0</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each NOMS_MOIS as nom, k (nom)}
          <tr>
            <th scope="row">{nom}</th>
            {#each stats as s (s.annee)}
              {@const m = s.mois[k]}
              <td class="num">{gw(m.moyenneMw, false)}</td>
              <td class="num">{gw(m.maxMw, false)}</td>
              <td class="num">{gw(m.minMw, false)}</td>
              <td class="num">{formaterNombre(m.heuresPositives)} / {formaterNombre(m.heures)}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
    <p class="note-tableau">
      GW, moyenne horaire ; calcul du site sur les matrices publiées dans quand.json (heures
      renseignées seulement).
    </p>
  {/snippet}
</Figure>

<style>
  .echelle-bloc {
    max-width: 30rem;
    width: 100%;
  }
  .echelle {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 2px;
    height: 12px;
  }
  .classe {
    border-radius: 2px;
  }
  .classe.zero {
    margin-left: 4px;
  }
  .graduations {
    position: relative;
    height: 1.2rem;
    font-size: 0.8rem;
    color: var(--encre-2);
    font-variant-numeric: tabular-nums;
  }
  .graduations span {
    position: absolute;
    top: 0.1rem;
    transform: translateX(-50%);
  }
  .graduations span.zero {
    color: var(--encre);
    font-weight: 600;
  }
  .legende-texte {
    margin: 0.2rem 0 0;
    font-size: 0.875rem;
    color: var(--encre-2);
  }
  .fort {
    color: var(--encre);
    font-weight: 600;
  }
  .paire {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.5rem;
    max-width: 52rem;
  }
  .annee {
    margin: 0 0 0.2rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
  .sans-js {
    font-size: 0.9rem;
    color: var(--encre-2);
  }
  .groupe {
    text-align: center;
    border-bottom-color: var(--trait);
  }
  .note-tableau {
    font-size: 0.85rem;
    color: var(--encre-2);
    max-width: 46rem;
  }
</style>
