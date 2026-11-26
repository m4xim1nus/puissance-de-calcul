<script lang="ts">
  // Simulateur v1 (docs/SIMULATEUR.md) : hypothèses réglables, état dans l'adresse, calcul dans le
  // navigateur par le moteur (./moteur.ts, parité testée avec pipeline/pc/quand.py) sur le CSV de
  // l'année servi par le site. Le texte des hypothèses est rendu au prérendu ; les résultats
  // demandent JavaScript, et le disent.
  import { onMount } from 'svelte';
  import { typographier } from '$lib/markdown';
  import { afterNavigate, replaceState } from '$app/navigation';
  import { dateParis, formaterDate, formaterNombre } from '$lib/format';
  import { lireCsvHoraire } from './csv';
  import { BORNES, DEFAUTS, arrondirGw, ecrireEtat, lireEtat, type Etat } from './etat';
  import { heures, part, puissanceReglee, twh } from './format';
  import { phrases } from './phrases';
  import MonotoneAvantApres from './MonotoneAvantApres.svelte';
  import { simuler, type TableHoraire } from './moteur';

  interface Props {
    annees: number[];
    /** Séries sources (quand.json, `donnees.sources`). */
    sources: string;
    /** Dates d'extraction ISO (quand.json, `donnees.extractions`). */
    extractions: Record<string, string>;
  }
  let { annees, sources, extractions }: Props = $props();

  /** Rangs exacts de la monotone (zoom du graphique) ; au-delà, un rang sur PAS. */
  const ZOOM = 600;
  const PAS = 10;

  let etat = $state<Etat>({ ...DEFAUTS });
  let ecarts = $state<string[]>([]);
  let monte = $state(false);

  // Tables déjà chargées (une par année), et chargement en cours.
  const cache = new Map<number, TableHoraire>();
  let table = $state<TableHoraire | null>(null);
  let anneeTable = $state<number | null>(null);
  let erreur = $state<string | null>(null);

  async function charger(a: number) {
    erreur = null;
    const deja = cache.get(a);
    if (deja) {
      table = deja;
      anneeTable = a;
      return;
    }
    try {
      const r = await fetch(`/donnees/horaire/${a}.csv`);
      if (!r.ok) throw new Error(`réponse ${r.status}`);
      const t = lireCsvHoraire(await r.text());
      cache.set(a, t);
      // Une réponse arrivée après un autre choix d'année est gardée en cache, pas affichée.
      if (etat.annee === a) {
        table = t;
        anneeTable = a;
      }
    } catch (e) {
      if (etat.annee === a) erreur = e instanceof Error ? e.message : String(e);
    }
  }

  onMount(() => {
    const lu = lireEtat(location.search, annees);
    etat = lu.etat;
    ecarts = lu.ecarts;
    monte = true;
  });

  $effect(() => {
    if (monte) charger(etat.annee);
  });

  // replaceState n'est utilisable qu'une fois le routeur prêt (après la première navigation) :
  // appelé dès onMount, il lève une erreur et bloque les effets suivants.
  let routeurPret = $state(false);
  afterNavigate(() => (routeurPret = true));

  $effect(() => {
    if (!monte || !routeurPret) return;
    const q = ecrireEtat(etat);
    if (q !== location.search) replaceState(`${location.pathname}${q}`, {});
  });

  function regler(champ: 'xGw' | 'effacement', brut: number) {
    if (!Number.isFinite(brut)) return;
    const b = BORNES[champ];
    const v = Math.min(b.max, Math.max(b.min, brut));
    etat[champ] = champ === 'xGw' ? arrondirGw(v) : Math.round(v);
    ecarts = [];
  }

  const pret = $derived(table !== null && anneeTable === etat.annee);
  const xMw = $derived(Math.round(etat.xGw * 1000));
  const sim = $derived(pret && table ? simuler(table, xMw, etat.effacement, ZOOM, PAS) : null);
  /** Même puissance sans effacement : sert de comparaison (heures au-delà du maximum, prix). */
  const plate = $derived(
    !sim || !table ? null : etat.effacement === 0 ? sim : simuler(table, xMw, 0, 1, 1e9)
  );
  const libelle = $derived(
    `${puissanceReglee(etat.xGw)}${etat.effacement ? `, effacés ${heures(etat.effacement)}` : ''}`
  );

  const NOMS: Record<string, string> = {
    eco2mix: 'éCO2mix',
    edf_remit: 'REMIT (EDF)',
    prix: 'prix day-ahead'
  };
  const ligneSources = $derived(
    typographier(
      `Calcul du site, fait dans le navigateur sur les séries horaires publiées ` +
        `(data/export/horaire/${etat.annee}.csv) : ${sources}. Extraction : ` +
        Object.entries(extractions)
          .map(([k, iso]) => `${NOMS[k] ?? k} le ${formaterDate(dateParis(iso))}`)
          .join(', ') +
        '.'
    )
  );

  // Résumé pour les lecteurs d'écran, différé : un curseur qu'on fait glisser n'annonce pas
  // chaque pas.
  let annonce = $state('');
  $effect(() => {
    const s = sim;
    if (!s) return;
    const texte =
      `${etat.annee}, ${libelle} : ${twh(s.energie_ajoutee_twh)} ajoutés ; ` +
      (s.part_dans_j === null
        ? ''
        : `au plus ${part(s.part_dans_j)} dans le nucléaire disponible non produit ; `) +
      `${heures(s.heures_au_dessus_du_max ?? 0)} au-delà du maximum observé` +
      (s.part_prix_nul_ou_negatif === null
        ? '.'
        : ` ; ${part(s.part_prix_nul_ou_negatif)} de l’énergie à prix nul ou négatif.`);
    const t = setTimeout(() => (annonce = texte), 700);
    return () => clearTimeout(t);
  });
</script>

<section class="hypotheses" aria-labelledby="hypotheses-titre">
  <h2 id="hypotheses-titre">Hypothèses</h2>
  <p class="consigne">
    Trois réglages, chacun avec sa valeur par défaut et sa raison. L’adresse de la page porte le
    scénario : on la copie pour le partager.
  </p>

  <div class="hypothese">
    <label class="nom" for="sim-annee">Année observée</label>
    <div class="controle">
      <select
        id="sim-annee"
        value={etat.annee}
        disabled={!monte}
        onchange={(e) => {
          etat.annee = Number((e.currentTarget as HTMLSelectElement).value);
          ecarts = [];
        }}
      >
        {#each annees as a (a)}
          <option value={a}>{a}</option>
        {/each}
      </select>
    </div>
    <p class="defaut">
      Défaut : {DEFAUTS.annee}, dernière année close. Choix : {annees[0]} à {annees.at(-1)}.
    </p>
    <p class="raison">
      Une année observée, avec sa météo, sa disponibilité nucléaire et ses prix : 2022, année de
      faible disponibilité du parc nucléaire et de prix de crise, ne ressemble pas à 2025. L’année
      en cours n’est pas proposée tant qu’elle n’est pas close.
    </p>
  </div>

  <div class="hypothese">
    <label class="nom" for="sim-x">Puissance appelée ajoutée</label>
    <div class="controle">
      <input
        id="sim-x-curseur"
        type="range"
        min={BORNES.xGw.min}
        max={BORNES.xGw.max}
        step={BORNES.xGw.pas}
        value={etat.xGw}
        disabled={!monte}
        aria-label="Puissance appelée ajoutée, en GW (curseur)"
        aria-valuetext={puissanceReglee(etat.xGw)}
        oninput={(e) => regler('xGw', Number((e.currentTarget as HTMLInputElement).value))}
      />
      <span class="saisie"
        ><input
          id="sim-x"
          type="number"
          inputmode="decimal"
          min={BORNES.xGw.min}
          max={BORNES.xGw.max}
          step={BORNES.xGw.pas}
          value={etat.xGw}
          disabled={!monte}
          onchange={(e) => regler('xGw', Number((e.currentTarget as HTMLInputElement).value))}
        /> GW</span
      >
    </div>
    <p class="defaut">
      Défaut : {formaterNombre(DEFAUTS.xGw)} GW. Plage : {BORNES.xGw.min} à {BORNES.xGw.max} GW, par pas
      de 0,1 GW.
    </p>
    <p class="raison">
      Puissance <strong>consommée</strong> en moyenne sur chaque heure, pas puissance réservée ni
      raccordée : un data center raccordé n’utilise qu’une partie de sa puissance de raccordement
      (voir <a href="/combien">« Combien ? »</a>).
    </p>
  </div>

  <div class="hypothese">
    <label class="nom" for="sim-effacement">Profil : plat, avec effacement</label>
    <div class="controle">
      <input
        id="sim-effacement-curseur"
        type="range"
        min={BORNES.effacement.min}
        max={BORNES.effacement.max}
        step={BORNES.effacement.pas}
        value={etat.effacement}
        disabled={!monte}
        aria-label="Heures d’effacement par an (curseur)"
        aria-valuetext={heures(etat.effacement)}
        oninput={(e) => regler('effacement', Number((e.currentTarget as HTMLInputElement).value))}
      />
      <span class="saisie"
        ><input
          id="sim-effacement"
          type="number"
          inputmode="numeric"
          min={BORNES.effacement.min}
          max={BORNES.effacement.max}
          step={BORNES.effacement.pas}
          value={etat.effacement}
          disabled={!monte}
          onchange={(e) =>
            regler('effacement', Number((e.currentTarget as HTMLInputElement).value))}
        /> h/an</span
      >
    </div>
    <p class="defaut">
      Défaut : 0 heure (consommation plate toute l’année). Plage : 0 à {BORNES.effacement.max} heures
      par an.
    </p>
    <p class="raison">
      Aucune courbe de charge de data center n’est publiée : la consommation est supposée constante.
      L’effacement la met à zéro pendant les heures où la charge résiduelle
      <strong>observée</strong> est la plus élevée, comme si on les connaissait à l’avance : c’est une
      borne optimiste.
    </p>
  </div>

  {#if ecarts.length}
    <p class="ecarts" role="status">Adresse corrigée : {ecarts.join(' ; ')}.</p>
  {/if}
  {#if monte && JSON.stringify(etat) !== JSON.stringify(DEFAUTS)}
    <button
      type="button"
      class="retour"
      onclick={() => {
        etat = { ...DEFAUTS };
        ecarts = [];
      }}>Revenir aux valeurs par défaut</button
    >
  {/if}
</section>

<section class="resultats" aria-labelledby="resultats-titre">
  <h2 id="resultats-titre">Résultats</h2>
  <noscript>
    <p class="sans-js">
      Les résultats sont calculés dans le navigateur, à partir des séries horaires de l’année : ils
      demandent JavaScript. Le reste de la page se lit sans. Les séries sont téléchargeables :
      {#each annees as a, i (a)}<a href="/donnees/horaire/{a}.csv" download>{a}</a>{i <
        annees.length - 1
          ? ', '
          : '.'}{/each}
    </p>
  </noscript>

  {#if monte}
    {#if erreur}
      <p class="etat-calcul erreur" role="alert">
        Les séries de {etat.annee} n’ont pas pu être chargées ({erreur}). Rechargez la page.
      </p>
    {:else if !sim || !plate}
      <p class="etat-calcul" role="status">Chargement des séries horaires de {etat.annee}…</p>
    {:else}
      {@const ph = phrases(etat, sim, plate, BORNES.effacement.max)}
      <p class="scenario">{ph.scenario}</p>

      <dl class="tuiles">
        {#each ph.tuiles as tu (tu.titre)}
          <div class="tuile">
            <dt>{tu.titre}</dt>
            <dd class="valeur">
              {#if tu.qualif}<span class="qualif">{tu.qualif}</span>{/if}
              {tu.valeur}
            </dd>
            <dd class="detail">{tu.detail}</dd>
          </div>
        {/each}
      </dl>

      <p class="couverture">
        Heures de {etat.annee} (année civile, heure de Paris) : {formaterNombre(sim.heures)}. Charge
        résiduelle renseignée : {formaterNombre(sim.heures_rn_valides)} ; nucléaire disponible et
        produit : {formaterNombre(sim.heures_j_valides)} ; prix : {formaterNombre(
          sim.heures_prix_valides
        )}. Chaque résultat porte sur les heures où ses données sont renseignées.
        <a href="/donnees/horaire/{etat.annee}.csv" download
          >Télécharger les séries de {etat.annee}</a
        > (CSV).
      </p>

      {#if sim.rn_max_mw !== null}
        <MonotoneAvantApres
          annee={etat.annee}
          {libelle}
          avant={sim.monotone_avant}
          apres={sim.monotone_apres}
          rnMaxMw={sim.rn_max_mw}
          zoom={ZOOM}
          sources={ligneSources}
        />
      {/if}
    {/if}
  {/if}
  <p class="lecteur" aria-live="polite">{annonce}</p>
</section>

<style>
  .hypotheses,
  .resultats {
    max-width: var(--large);
  }
  .consigne {
    max-width: var(--mesure);
  }
  .hypothese {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 0.25rem;
    max-width: var(--mesure);
    padding: 0.9rem 0 1rem;
    border-top: 1px solid var(--trait);
  }
  .nom {
    font-family: var(--sans);
    font-weight: 600;
    font-size: 1.15rem;
  }
  .controle {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    flex-wrap: wrap;
    font-family: var(--sans);
  }
  .controle input[type='range'] {
    flex: 1 1 14rem;
    min-width: 0;
    accent-color: var(--encre);
  }
  .saisie {
    white-space: nowrap;
  }
  input[type='number'],
  select {
    font: inherit;
    font-size: 1.05rem;
    font-variant-numeric: tabular-nums;
    color: var(--encre);
    background: var(--papier);
    border: 1px solid var(--encre-2);
    border-radius: 3px;
    padding: 0.2rem 0.4rem;
  }
  input[type='number'] {
    width: 5.5rem;
  }
  :disabled {
    opacity: 0.6;
  }
  .defaut {
    margin: 0;
    font-family: var(--sans);
    font-size: 0.95rem;
    color: var(--encre-2);
  }
  .raison {
    margin: 0;
    font-size: 1rem;
    line-height: 1.5;
  }
  .ecarts {
    font-family: var(--sans);
    font-size: 0.95rem;
    border-left: 3px solid var(--signal);
    padding-left: 0.6rem;
    max-width: var(--mesure);
  }
  .retour {
    font: inherit;
    font-family: var(--sans);
    font-size: 0.95rem;
    color: var(--encre);
    background: none;
    border: 1px solid var(--encre-2);
    border-radius: 3px;
    padding: 0.2rem 0.6rem;
    cursor: pointer;
  }
  .retour:hover {
    background: var(--papier-2);
  }
  .sans-js,
  .etat-calcul {
    font-family: var(--sans);
    color: var(--encre-2);
    max-width: var(--mesure);
  }
  .erreur {
    color: var(--encre);
    border-left: 3px solid var(--sur-zero);
    padding-left: 0.6rem;
  }
  .scenario {
    font-family: var(--sans);
    font-size: 1.1rem;
    max-width: 46rem;
  }
  .tuiles {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(14.5rem, 1fr));
    gap: 1rem 1.5rem;
    margin: 0 0 1rem;
  }
  .tuile {
    border-top: 2px solid var(--encre);
    padding-top: 0.5rem;
  }
  .tuile dt {
    font-family: var(--sans);
    font-weight: 500;
    font-size: 0.95rem;
    line-height: 1.25;
    color: var(--encre-2);
  }
  .tuile dd {
    margin: 0;
  }
  .tuile dd.valeur {
    font-family: var(--sans);
    font-weight: 600;
    font-size: 1.75rem;
    line-height: 1.2;
    margin: 0.15rem 0 0.25rem;
    font-variant-numeric: tabular-nums;
  }
  .qualif {
    font-size: 1.05rem;
    font-weight: 500;
  }
  .detail {
    font-size: 0.92rem;
    line-height: 1.45;
  }
  .couverture {
    font-family: var(--sans);
    font-size: 0.9rem;
    color: var(--encre-2);
    max-width: 46rem;
  }
</style>
