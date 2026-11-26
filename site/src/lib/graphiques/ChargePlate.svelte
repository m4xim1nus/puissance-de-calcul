<script lang="ts">
  // Consommation plate de X GW ajoutée aux années observées 2022 à 2025 : (a) part de son énergie
  // qui tiendrait, au plus, dans le nucléaire disponible non produit ; (b) heures où la charge
  // résiduelle + X dépasserait le maximum observé de l'année. Deux grandeurs, deux panneaux, chacun
  // son axe. SVG rendu au prérendu, lisible sans JS.
  import { scaleLinear, scaleLog } from 'd3-scale';
  import { formaterNombre } from '$lib/format';
  import { ANNEES_COMPAREES, ecarter, gw, pourcent, sourcesRn } from '$lib/quand';
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
  const xs = $derived(annees[0].chargesPlates.map((c) => c.xMw));
  /** Haut de l'axe logarithmique du panneau b : le plus grand nombre d'heures, avec une marge. */
  const plafondHeures = $derived(
    1.3 * Math.max(...annees.flatMap((a) => a.chargesPlates.map((c) => c.heuresAuDessusDuMax)))
  );
  const couleur = (i: number) => `var(--annee-${i + 1})`;
  const xGw = (mw: number) => gw(mw).replace(/,0(?= GW)/, '');

  type Panneau = 'part' | 'heures';
  const valeur = (p: Panneau, a: (typeof annees)[number], xMw: number) => {
    const c = a.chargesPlates.find((c) => c.xMw === xMw);
    if (!c) throw new Error(`quand.json : charge plate ${xMw} MW absente en ${a.annee}`);
    return p === 'part' ? c.partDansJ : c.heuresAuDessusDuMax;
  };
  const texte = (p: Panneau, v: number) => (p === 'part' ? pourcent(v) : `${formaterNombre(v)} h`);

  let actif = $state<{ p: Panneau; x: number } | null>(null);
  const lignes = (p: Panneau, xMw: number): LigneInfobulle[] =>
    [...annees]
      .reverse()
      .map((a) => ({ valeur: texte(p, valeur(p, a, xMw)), libelle: String(a.annee) }));
  const TITRES: Record<Panneau, string> = {
    part: 'Part de l’énergie ajoutée qui tiendrait au plus dans le nucléaire disponible non produit',
    heures: 'Heures où la charge résiduelle + X dépasse son maximum observé de l’année'
  };
</script>

<Figure
  id="charge-plate"
  titre="Une consommation plate de X GW ajoutée aux années 2022 à 2025"
  sousTitre="X GW consommés à toutes les heures de l’année, ajoutés aux données observées de chaque année. Deux grandeurs différentes, deux panneaux, chacun son axe ; X en échelle logarithmique."
  remarques="« Au plus » : une partie du nucléaire disponible est réservée aux services système ; une baisse de production pour économiser le combustible déplace de l’énergie dans le temps ; et la France exporte à ces heures, si bien qu’une consommation ajoutée serait d’abord servie, en partie, par moins d’exportations. Dépasser le maximum observé n’est pas une défaillance : c’est sortir de ce que le système a connu dans l’année. Une charge plate n’est pas le profil d’un data center réel."
  sources={sourcesRn(q)}
  titreTableau="Tableau des données : consommation plate de X GW, 2022 à 2025"
>
  {#snippet legende()}
    {#each annees as a, i (a.annee)}
      <span class="cle"
        ><svg width="24" height="12" aria-hidden="true"
          ><line
            x1="1"
            x2="23"
            y1="6"
            y2="6"
            stroke={couleur(i)}
            stroke-width={i === annees.length - 1 ? 3 : 2}
          /><circle cx="12" cy="6" r="3.5" fill={couleur(i)} /></svg
        >{a.annee}</span
      >
    {/each}
  {/snippet}

  {#snippet trace(largeur: number)}
    {@const W = Math.max(300, largeur)}
    {@const empile = W < 640}
    {@const Lp = empile ? W : (W - 32) / 2}
    <div class="panneaux" class:empile>
      {#each ['part', 'heures'] as const as p (p)}
        {@const M = { haut: 16, bas: 38, gauche: 44, droite: 44 }}
        {@const H = 250}
        {@const x = scaleLog()
          .domain([xs[0] * 0.8, xs[xs.length - 1] * 1.15])
          .range([M.gauche, Lp - M.droite])}
        {@const y =
          p === 'part'
            ? scaleLinear()
                .domain([0, 1])
                .range([H - M.bas, M.haut])
            : scaleLog()
                .domain([1, plafondHeures])
                .range([H - M.bas, M.haut])}
        {@const graduations =
          p === 'part' ? [0, 0.25, 0.5, 0.75, 1] : y.ticks().filter((t) => Math.log10(t) % 1 === 0)}
        {@const fins = ecarter(
          annees.map((a, i) => ({ i, annee: a.annee, y: y(valeur(p, a, xs[xs.length - 1])) })),
          14,
          M.haut,
          H - M.bas
        )}
        <div class="panneau">
          <p class="titre-panneau" id="charge-plate-{p}">
            {#if p === 'part'}
              Part de l’énergie ajoutée qui tiendrait, <strong>au plus</strong>, dans le nucléaire
              disponible non produit
            {:else}
              Heures où la charge résiduelle + X dépasse son maximum observé de l’année
              <span class="precision">(échelle logarithmique)</span>
            {/if}
          </p>
          <div class="trace-panneau">
            <svg
              width={Lp}
              height={H}
              viewBox="0 0 {Lp} {H}"
              role="group"
              aria-labelledby="charge-plate-{p}"
            >
              {#each graduations as v (v)}
                <line class="grille" x1={M.gauche} x2={Lp - M.droite} y1={y(v)} y2={y(v)} />
                <text class="graduation" x={M.gauche - 6} y={y(v) + 4} text-anchor="end"
                  >{p === 'part' ? pourcent(v) : formaterNombre(v)}</text
                >
              {/each}
              <line class="base" x1={M.gauche} x2={Lp - M.droite} y1={H - M.bas} y2={H - M.bas} />
              {#each xs as xm (xm)}
                <text class="graduation" x={x(xm)} y={H - M.bas + 16} text-anchor="middle"
                  >{formaterNombre(xm / 1000, 1)}</text
                >
              {/each}
              <text class="graduation" x={Lp - M.droite} y={H - 4} text-anchor="end">X, en GW</text>
              {#if actif?.p === p}
                <line class="repere" x1={x(actif.x)} x2={x(actif.x)} y1={M.haut} y2={H - M.bas} />
              {/if}
              {#each annees as a, i (a.annee)}
                <path
                  class="ligne"
                  class:forte={i === annees.length - 1}
                  stroke={couleur(i)}
                  d={xs
                    .map(
                      (xm, k) =>
                        `${k ? 'L' : 'M'}${x(xm).toFixed(1)},${y(valeur(p, a, xm)).toFixed(1)}`
                    )
                    .join('')}
                />
                {#each xs as xm (xm)}
                  <circle
                    class="point"
                    cx={x(xm)}
                    cy={y(valeur(p, a, xm))}
                    r="4"
                    fill={couleur(i)}
                  />
                {/each}
              {/each}
              {#each fins as f (f.annee)}
                <text class="etiquette" x={Lp - M.droite + 8} y={f.y + 4}>{f.annee}</text>
              {/each}
              <!-- Couche de survol : une colonne par valeur de X, au pointeur comme au clavier. -->
              {#each xs as xm, k (xm)}
                {@const g = k === 0 ? M.gauche : (x(xs[k - 1]) + x(xm)) / 2}
                {@const d = k === xs.length - 1 ? Lp - M.droite : (x(xm) + x(xs[k + 1])) / 2}
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
            </svg>
            {#if actif?.p === p}
              <Infobulle
                x={x(actif.x)}
                y={M.haut + 6}
                largeur={Lp}
                titre="X = {xGw(actif.x)}"
                lignes={lignes(p, actif.x)}
              />
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/snippet}

  {#snippet tableau()}
    <table>
      <caption class="lecteur"
        >Consommation plate de X GW : part au plus dans le nucléaire disponible non produit, et
        heures au-dessus du maximum observé</caption
      >
      <thead>
        <tr>
          <th scope="col" rowspan="2">X</th>
          {#each annees as a (a.annee)}
            <th scope="colgroup" colspan="2" class="groupe">{a.annee}</th>
          {/each}
        </tr>
        <tr>
          {#each annees as a (a.annee)}
            <th scope="col" class="num">Part, au plus</th>
            <th scope="col" class="num">Heures au-dessus du max.</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each xs as xm (xm)}
          <tr>
            <th scope="row" class="num">{xGw(xm)}</th>
            {#each annees as a (a.annee)}
              <td class="num">{pourcent(valeur('part', a, xm))}</td>
              <td class="num">{formaterNombre(valeur('heures', a, xm))}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
    <p class="note-tableau">
      {TITRES.part} : Σ min(X, J) / (X × heures où J est renseigné), J = nucléaire disponible déclaré
      − nucléaire produit, borné à zéro. {TITRES.heures} : heures où charge résiduelle + X &gt; maximum
      de l’année (strictement).
    </p>
  {/snippet}
</Figure>

<style>
  .cle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-variant-numeric: tabular-nums;
  }
  .panneaux {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 2rem;
  }
  .panneaux.empile {
    grid-template-columns: minmax(0, 1fr);
    gap: 1.25rem;
  }
  .titre-panneau {
    margin: 0 0 0.4rem;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.3;
    min-height: 2.6em;
  }
  .titre-panneau strong {
    font-weight: 700;
  }
  .precision {
    color: var(--encre-2);
    font-weight: 400;
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
    stroke-width: 1.75;
    stroke-linejoin: round;
  }
  .ligne.forte {
    stroke-width: 2.75;
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
