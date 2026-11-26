<script lang="ts">
  // Consommation plate de X GW ajoutée aux années observées 2022 à 2025.
  // (a) Part de son énergie qui tiendrait, au plus, dans le nucléaire disponible non produit :
  //     fourchette entre « sans plancher » (borne haute) et « avec un plancher non mobilisable »
  //     (hypothèse du site), une barre par année, décalées à chaque valeur de X.
  // (b) Heures où la charge résiduelle + X dépasserait le maximum observé : de l'année (au moins 1,
  //     l'heure du maximum elle-même), et de 2015-2025 (peut valoir 0). Même axe pour les deux
  //     panneaux, en échelle log(1 + heures), qui garde le zéro.
  // Deux grandeurs, panneaux séparés, chacun son axe. SVG rendu au prérendu, lisible sans JS.
  import { scaleLinear, scaleLog, scaleSymlog } from 'd3-scale';
  import { formaterNombre } from '$lib/format';
  import {
    ANNEES_COMPAREES,
    TRAITS_ANNEES,
    ecarter,
    gw,
    heureParis,
    pourcent,
    sourcesRn,
    type AnneeQuand
  } from '$lib/quand';
  import Figure from './Figure.svelte';
  import Infobulle, { type LigneInfobulle } from './Infobulle.svelte';
  import { donneesQuand, type PropsGraphique } from './registre';

  let { donnees }: PropsGraphique = $props();
  const q = $derived(donneesQuand(donnees));
  const annees = $derived(
    ANNEES_COMPAREES.map((a) => {
      const d = q.annees.find((x) => x.annee === a);
      if (!d) throw new Error(`quand.json : année ${a} absente`);
      return d;
    })
  );
  const reference = $derived(q.rnMaxPluriannuel);
  const xs = $derived(annees[0].chargesPlates.map((c) => c.xMw));
  const couleur = (i: number) => `var(--annee-${i + 1})`;
  const trait = (i: number) => TRAITS_ANNEES[i] || undefined;
  /** « 5 GW », « 0,5 GW » : X est un paramètre rond, sans décimale inutile. */
  const xGw = (mw: number) => gw(mw).replace(/,0(?= GW)/, '');

  const charge = (a: AnneeQuand, xMw: number) => {
    const c = a.chargesPlates.find((c) => c.xMw === xMw);
    if (!c) throw new Error(`quand.json : charge plate ${xMw} MW absente en ${a.annee}`);
    return c;
  };
  const plancher = $derived.by(() => {
    const p = new Set(annees.flatMap((a) => a.chargesPlates.map((c) => c.plancherMw)));
    if (p.size !== 1) throw new Error('quand.json : plancher différent selon les années');
    return [...p][0];
  });

  type Serie = 'annee' | 'reference';
  const heures = (s: Serie, a: AnneeQuand, xMw: number) =>
    s === 'annee'
      ? charge(a, xMw).heuresAuDessusDuMax
      : charge(a, xMw).heuresAuDessusDuMaxReference;
  const plafondHeures = $derived(
    Math.max(
      ...annees.flatMap((a) =>
        a.chargesPlates.flatMap((c) => [c.heuresAuDessusDuMax, c.heuresAuDessusDuMaxReference])
      )
    )
  );

  type Panneau = 'part' | Serie;
  let actif = $state<{ p: Panneau; x: number } | null>(null);
  const h = (n: number) => `${formaterNombre(n)} h`;
  const lignes = (p: Panneau, xMw: number): LigneInfobulle[] =>
    [...annees].reverse().map((a) => {
      if (p === 'part') {
        const c = charge(a, xMw);
        return {
          valeur: `${pourcent(c.partDansJ)} au plus`,
          libelle: `${a.annee} ; ${pourcent(c.partDansJPlancher)} avec plancher`
        };
      }
      return { valeur: h(heures(p, a, xMw)), libelle: String(a.annee) };
    });

  const TITRES: Record<Panneau, string> = $derived({
    part: 'Part de l’énergie ajoutée qui tiendrait, au plus, dans le nucléaire disponible non produit',
    annee: 'Heures au-delà du maximum de l’année',
    reference: `Heures au-delà du maximum ${reference.annees}`
  });
</script>

<Figure
  id="charge-plate"
  titre="Une consommation plate de X GW ajoutée aux années 2022 à 2025"
  sousTitre="X GW consommés à toutes les heures de l’année, ajoutés aux données observées de chaque année. Deux grandeurs différentes, panneaux séparés, chacun son axe ; X en échelle logarithmique."
  remarques="« Au plus » : une partie du nucléaire disponible est réservée aux services système, et une baisse de production pour économiser le combustible déplace de l’énergie dans le temps ; le plancher, hypothèse du site, retranche une part qui ne serait mobilisable à aucune heure. Qui servirait réellement la charge ajoutée (nucléaire inemployé, moins d’exportations, autres moyens) dépend de la saturation des interconnexions, que ces données ne disent pas. Dépasser un maximum observé n’est pas une défaillance : au-delà du maximum de l’année, c’est plus que cette année-là ; au-delà du maximum 2015-2025, plus que toutes les années observées. Une charge plate n’est pas le profil d’un data center réel."
  sources={sourcesRn(q)}
  titreTableau="Tableau des données : consommation plate de X GW, 2022 à 2025"
>
  {#snippet legende()}
    {#each annees as a, i (a.annee)}
      <span class="cle"
        ><svg width="30" height="12" aria-hidden="true"
          ><line
            x1="1"
            x2="29"
            y1="6"
            y2="6"
            stroke={couleur(i)}
            stroke-dasharray={trait(i)}
            stroke-linecap="round"
            stroke-width={i === annees.length - 1 ? 3 : 2.25}
          /></svg
        >{a.annee}</span
      >
    {/each}
  {/snippet}

  {#snippet trace(largeur: number)}
    {@const W = Math.max(300, largeur)}
    {@const cote = W >= 640}
    {@const Lb = cote ? (W - 32) / 2 : W}
    <div class="ligne-a">{@render part(Math.min(W, 760))}</div>
    <div class="panneaux" class:juxtaposes={cote}>
      {@render depassements('annee', Lb)}
      {@render depassements('reference', Lb)}
    </div>
  {/snippet}

  {#snippet tableau()}
    <table>
      <caption class="lecteur"
        >Consommation plate de X GW, par année : part au plus dans le nucléaire disponible non
        produit, avec et sans plancher, et heures au-delà des maximums observés</caption
      >
      <thead>
        <tr>
          <th scope="col">Année</th>
          <th scope="col" class="num">X</th>
          <th scope="col" class="num">Part, au plus (sans plancher)</th>
          <th scope="col" class="num">Part avec plancher de {xGw(plancher)}</th>
          <th scope="col" class="num">Heures au-delà du max. de l’année</th>
          <th scope="col" class="num">Heures au-delà du max. {reference.annees}</th>
        </tr>
      </thead>
      {#each annees as a (a.annee)}
        <tbody>
          {#each xs as xm, k (xm)}
            {@const c = charge(a, xm)}
            <tr>
              {#if k === 0}<th scope="rowgroup" rowspan={xs.length}>{a.annee}</th>{/if}
              <td class="num">{xGw(xm)}</td>
              <td class="num">{pourcent(c.partDansJ)}</td>
              <td class="num">{pourcent(c.partDansJPlancher)}</td>
              <td class="num">{formaterNombre(c.heuresAuDessusDuMax)}</td>
              <td class="num">{formaterNombre(c.heuresAuDessusDuMaxReference)}</td>
            </tr>
          {/each}
        </tbody>
      {/each}
    </table>
    <p class="note-tableau">
      Part : Σ min(X, J) / (X × heures où J est renseigné), J = nucléaire disponible déclaré −
      nucléaire produit, borné à zéro ; avec plancher, J est d’abord diminué de {xGw(plancher)}
      (hypothèse du site). Heures : heures où charge résiduelle + X dépasse strictement le maximum de
      l’année, ou le maximum {reference.annees} ({gw(reference.valeurMw)}, {heureParis(
        reference.debutParis
      )}).
    </p>
  {/snippet}
</Figure>

<!-- (a) Fourchette de la part de l'énergie : une barre par année, décalées à chaque X. -->
{#snippet part(L: number)}
  {@const M = { haut: 14, bas: 38, gauche: 44, droite: 16 }}
  {@const H = 250}
  {@const x = scaleLog()
    .domain([xs[0] * 0.75, xs[xs.length - 1] * 1.2])
    .range([M.gauche, L - M.droite])}
  {@const y = scaleLinear()
    .domain([0, 1])
    .range([H - M.bas, M.haut])}
  {@const ecart = Math.min(8, (x(xs[xs.length - 1]) - x(xs[xs.length - 2])) / 5)}
  {@const dx = (i: number) => (i - (annees.length - 1) / 2) * ecart}
  <div class="panneau">
    <p class="titre-panneau" id="charge-plate-part">
      (a) Part de l’énergie ajoutée qui tiendrait, <strong>au plus</strong>, dans le nucléaire
      disponible non produit
    </p>
    <p class="aide">
      <svg width="14" height="26" aria-hidden="true"
        ><line x1="7" x2="7" y1="6" y2="22" stroke="var(--encre-2)" stroke-width="3" /><circle
          cx="7"
          cy="6"
          r="4"
          fill="var(--encre-2)"
        /><line x1="2" x2="12" y1="22" y2="22" stroke="var(--encre-2)" stroke-width="2" /></svg
      >
      Point : sans plancher, <strong>au plus</strong>. Trait du bas : avec un plancher de
      {xGw(plancher)} non mobilisable (hypothèse du site). À chaque X, de gauche à droite : {annees
        .map((a) => a.annee)
        .join(', ')}.
    </p>
    <div class="trace-panneau">
      <svg
        width={L}
        height={H}
        viewBox="0 0 {L} {H}"
        role="group"
        aria-labelledby="charge-plate-part"
      >
        {#each [0, 0.25, 0.5, 0.75, 1] as v (v)}
          <line class="grille" x1={M.gauche} x2={L - M.droite} y1={y(v)} y2={y(v)} />
          <text class="graduation" x={M.gauche - 6} y={y(v) + 4} text-anchor="end"
            >{pourcent(v)}</text
          >
        {/each}
        <line class="base" x1={M.gauche} x2={L - M.droite} y1={y(0)} y2={y(0)} />
        {#each xs as xm (xm)}
          <text class="graduation" x={x(xm)} y={H - M.bas + 16} text-anchor="middle"
            >{formaterNombre(xm / 1000, 1)}</text
          >
        {/each}
        <text class="graduation" x={L - M.droite} y={H - 4} text-anchor="end">X, en GW</text>
        {#if actif?.p === 'part'}
          <line class="repere" x1={x(actif.x)} x2={x(actif.x)} y1={M.haut} y2={H - M.bas} />
        {/if}
        {#each xs as xm (xm)}
          {#each annees as a, i (a.annee)}
            {@const c = charge(a, xm)}
            {@const cx = x(xm) + dx(i)}
            <line
              class="fourchette"
              x1={cx}
              x2={cx}
              y1={y(c.partDansJPlancher)}
              y2={y(c.partDansJ)}
              stroke={couleur(i)}
            />
            <line
              class="plancher"
              x1={cx - 3}
              x2={cx + 3}
              y1={y(c.partDansJPlancher)}
              y2={y(c.partDansJPlancher)}
              stroke={couleur(i)}
            />
            <circle class="point" {cx} cy={y(c.partDansJ)} r="4" fill={couleur(i)} />
          {/each}
        {/each}
        {@render colonnes('part', x, L, M, H)}
      </svg>
      {#if actif?.p === 'part'}
        <Infobulle
          x={x(actif.x)}
          y={M.haut + 6}
          largeur={L}
          titre="X = {xGw(actif.x)}"
          lignes={lignes('part', actif.x)}
        />
      {/if}
    </div>
  </div>
{/snippet}

<!-- (b) Heures au-delà d'un maximum observé, échelle log(1 + heures) commune aux deux panneaux. -->
{#snippet depassements(s: Serie, L: number)}
  {@const M = { haut: 14, bas: 38, gauche: 44, droite: 42 }}
  {@const H = 240}
  {@const x = scaleLog()
    .domain([xs[0] * 0.75, xs[xs.length - 1] * 1.2])
    .range([M.gauche, L - M.droite])}
  {@const y = scaleSymlog()
    .constant(1)
    .domain([0, plafondHeures * 1.3])
    .range([H - M.bas, M.haut])}
  {@const graduations = [0, 1, 10, 100, 1000, 10000].filter((t) => t <= plafondHeures * 1.3)}
  {@const fins = ecarter(
    annees.map((a, i) => ({ i, annee: a.annee, y: y(heures(s, a, xs[xs.length - 1])) + 4 })),
    14,
    M.haut + 4,
    H - M.bas + 4
  )}
  <div class="panneau">
    <p class="titre-panneau" id="charge-plate-{s}">
      ({s === 'annee' ? 'b' : 'c'}) {TITRES[s]}
      {#if s === 'annee'}
        <span class="precision">(au moins 1 : l’heure du maximum elle-même)</span>
      {:else}
        <span class="precision"
          >({gw(reference.valeurMw)}, {heureParis(reference.debutParis)} ; peut valoir 0)</span
        >
      {/if}
    </p>
    <div class="trace-panneau">
      <svg
        width={L}
        height={H}
        viewBox="0 0 {L} {H}"
        role="group"
        aria-labelledby="charge-plate-{s}"
      >
        {#each graduations as v (v)}
          <line
            class={v === 0 ? 'base' : 'grille'}
            x1={M.gauche}
            x2={L - M.droite}
            y1={y(v)}
            y2={y(v)}
          />
          <text class="graduation" x={M.gauche - 6} y={y(v) + 4} text-anchor="end"
            >{formaterNombre(v)}</text
          >
        {/each}
        {#each xs as xm (xm)}
          <text class="graduation" x={x(xm)} y={H - M.bas + 16} text-anchor="middle"
            >{formaterNombre(xm / 1000, 1)}</text
          >
        {/each}
        <text class="graduation" x={L - M.droite} y={H - 4} text-anchor="end">X, en GW</text>
        {#if actif?.p === s}
          <line class="repere" x1={x(actif.x)} x2={x(actif.x)} y1={M.haut} y2={H - M.bas} />
        {/if}
        {#each annees as a, i (a.annee)}
          <path
            class="ligne"
            class:forte={i === annees.length - 1}
            stroke={couleur(i)}
            stroke-dasharray={trait(i)}
            d={xs
              .map(
                (xm, k) => `${k ? 'L' : 'M'}${x(xm).toFixed(1)},${y(heures(s, a, xm)).toFixed(1)}`
              )
              .join('')}
          />
          {#each xs as xm (xm)}
            <circle class="point" cx={x(xm)} cy={y(heures(s, a, xm))} r="3.5" fill={couleur(i)} />
          {/each}
        {/each}
        {#each fins as f (f.annee)}
          <text class="etiquette" x={L - M.droite + 7} y={f.y}>{f.annee}</text>
        {/each}
        {@render colonnes(s, x, L, M, H)}
      </svg>
      {#if actif?.p === s}
        <Infobulle
          x={x(actif.x)}
          y={M.haut + 6}
          largeur={L}
          titre="X = {xGw(actif.x)}"
          lignes={lignes(s, actif.x)}
        />
      {/if}
    </div>
    <p class="aide">Échelle log(1 + heures) : le zéro reste au bas de l’axe.</p>
  </div>
{/snippet}

<!-- Couche de survol : une colonne par valeur de X, au pointeur comme au clavier. -->
{#snippet colonnes(
  p: Panneau,
  x: (v: number) => number,
  L: number,
  M: { haut: number; bas: number; gauche: number; droite: number },
  H: number
)}
  {#each xs as xm, k (xm)}
    {@const g = k === 0 ? M.gauche : (x(xs[k - 1]) + x(xm)) / 2}
    {@const d = k === xs.length - 1 ? L - M.droite : (x(xm) + x(xs[k + 1])) / 2}
    <!-- svelte-ignore a11y_no_noninteractive_tabindex (marque focalisable : l'infobulle s'affiche au clavier comme au survol) -->
    <rect
      class="colonne"
      x={g}
      y={M.haut}
      width={d - g}
      height={H - M.haut - M.bas}
      tabindex="0"
      role="img"
      aria-label="X = {xGw(xm)} : {lignes(p, xm)
        .map((l) => `${l.libelle}, ${l.valeur}`)
        .join(' ; ')}"
      onpointerenter={() => (actif = { p, x: xm })}
      onpointerleave={() => (actif = null)}
      onfocus={() => (actif = { p, x: xm })}
      onblur={() => (actif = null)}
    />
  {/each}
{/snippet}

<style>
  .cle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-variant-numeric: tabular-nums;
  }
  .ligne-a {
    margin-bottom: 1.5rem;
  }
  .panneaux {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 1.25rem;
  }
  .panneaux.juxtaposes {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 2rem;
  }
  .titre-panneau {
    margin: 0 0 0.3rem;
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.3;
  }
  .titre-panneau strong {
    font-weight: 800;
  }
  .precision {
    color: var(--encre-2);
    font-weight: 400;
  }
  .aide {
    margin: 0 0 0.4rem;
    font-size: 0.875rem;
    line-height: 1.35;
    color: var(--encre-2);
    max-width: 44rem;
  }
  .aide strong {
    color: var(--encre);
  }
  .aide svg {
    display: inline-block;
    vertical-align: middle;
    margin-right: 0.3rem;
    overflow: visible;
  }
  .trace-panneau {
    position: relative;
  }
  svg {
    display: block;
    max-width: 100%;
    height: auto;
    overflow: visible;
    font-family: var(--sans);
  }
  .grille {
    stroke: var(--trait);
  }
  .base {
    stroke: var(--encre-2);
  }
  .graduation {
    fill: var(--encre-2);
    font-size: 12px;
    font-variant-numeric: tabular-nums;
  }
  .ligne {
    fill: none;
    stroke-width: 2;
    stroke-linejoin: round;
    stroke-linecap: round;
  }
  .ligne.forte {
    stroke-width: 3;
  }
  .fourchette {
    stroke-width: 3;
    stroke-linecap: round;
  }
  .plancher {
    stroke-width: 2;
  }
  .point {
    stroke: var(--papier);
    stroke-width: 1.5;
  }
  .etiquette {
    paint-order: stroke;
    stroke: var(--papier);
    stroke-width: 3px;
    stroke-linejoin: round;
    fill: var(--encre);
    font-size: 12px;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
  }
  .repere {
    stroke: var(--encre-2);
    stroke-dasharray: 3 3;
  }
  .colonne {
    fill: transparent;
  }
  .colonne:focus-visible {
    outline: 2px solid var(--encre);
    outline-offset: -2px;
  }
  .note-tableau {
    font-size: 0.85rem;
    color: var(--encre-2);
    max-width: 46rem;
  }
</style>
