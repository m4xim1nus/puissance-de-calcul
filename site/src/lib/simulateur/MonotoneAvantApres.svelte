<script lang="ts">
  // Monotone de la charge résiduelle de l'année choisie, observée et avec la consommation ajoutée
  // (chacune triée pour elle-même), et maximum observé en repère. Deux panneaux, même grandeur :
  // toute l'année, puis un zoom sur les heures les plus tendues, où l'effacement agit. Chaque
  // panneau a son axe vertical (le zoom n'est pas à la même échelle).
  //
  // Revu le 26/11/2026 (l'outil tient dans la fenêtre, docs/relectures/2026-11-26-simulateur-ux-agent.md) :
  // en-tête d'une hauteur fixe (titre, légende, lien), tracé à la hauteur qui reste quand `plein` ;
  // sous-titre, remarques, sources et tableau de données sont dans la notice de la page (lien
  // `notes`), à un clic. Le libellé du scénario, qui change de longueur avec les réglages, n'est
  // plus dans le titre visible ni dans la légende (il ferait varier leur hauteur) : il reste dans
  // le titre lu par les lecteurs d'écran, dans l'infobulle et dans la notice.
  import { scaleLinear } from 'd3-scale';
  import Infobulle, { type LigneInfobulle } from '$lib/graphiques/Infobulle.svelte';
  import { formaterNombre } from '$lib/format';
  import { gw } from '$lib/quand';
  import type { Monotone } from './moteur';
  import { proche } from './rangs';

  interface Props {
    annee: number;
    /** Libellé de la consommation ajoutée (« 1 GW », « 5 GW effacés 200 h »). */
    libelle: string;
    avant: Monotone;
    apres: Monotone;
    rnMaxMw: number;
    /** Maximum pluriannuel (repère extérieur à l'année) et ses années. */
    rnMaxPluriMw: number;
    anneesPluri: string;
    /** Dernier rang tracé une à une dans le zoom (le moteur doit rendre ces rangs exacts). */
    zoom: number;
    /** Le tracé prend la hauteur de son conteneur (outil en pleine fenêtre). */
    plein: boolean;
    /** Lien vers la lecture, les sources et les données du graphique (notice de la page). */
    notes: { href: string; ouvrir: (ev: MouseEvent) => void };
  }
  let {
    annee,
    libelle,
    avant,
    apres,
    rnMaxMw,
    rnMaxPluriMw,
    anneesPluri,
    zoom,
    plein,
    notes
  }: Props = $props();

  const couleurAvant = 'var(--donnee-faible)';
  const couleurApres = 'var(--donnee)';
  const n = $derived(avant[avant.length - 1][0]);

  type Panneau = 'annee' | 'zoom';
  const points = (m: Monotone, p: Panneau) => (p === 'annee' ? m : m.filter(([r]) => r <= zoom));

  let actif = $state<{ p: Panneau; i: number } | null>(null);
  let largeur = $state(0);
  let hauteur = $state(0);

  function lignes(i: number): LigneInfobulle[] {
    const [, a] = avant[i];
    const [, b] = apres[i];
    return [
      { valeur: gw(b), libelle: `avec ${libelle}`, cle: 'forte' },
      { valeur: gw(a), libelle: 'observée', cle: 'faible' },
      { valeur: gw(b - a), libelle: 'écart à rang égal' }
    ];
  }
  const titreRang = (r: number) =>
    r === 1 ? 'Heure la plus tendue' : `${formaterNombre(r)}e heure la plus tendue`;

  function touche(ev: KeyboardEvent, p: Panneau) {
    const dernier = points(avant, p).length - 1;
    const i = actif?.p === p ? actif.i : 0;
    const pas: Record<string, number> = { ArrowRight: 1, ArrowLeft: -1, PageDown: 25, PageUp: -25 };
    let suivant: number | null = null;
    if (ev.key in pas) suivant = Math.min(dernier, Math.max(0, i + pas[ev.key]));
    else if (ev.key === 'Home') suivant = 0;
    else if (ev.key === 'End') suivant = dernier;
    else if (ev.key === 'Escape') actif = null;
    if (suivant !== null) {
      ev.preventDefault();
      actif = { p, i: suivant };
    }
  }

  /** Hauteur du titre d'un panneau, au-dessus de son tracé. */
  const TITRE_PANNEAU = 24;
</script>

<figure class="monotone" class:plein aria-labelledby="monotone-simulee-titre">
  <figcaption class="entete">
    <h3 id="monotone-simulee-titre">
      Charge résiduelle de {annee}, heures classées de la plus tendue à la moins tendue<span
        class="lecteur">&#8239;: observée et avec {libelle}</span
      >
    </h3>
    <a class="notes" href={notes.href} onclick={notes.ouvrir}>Lire le graphique, sources, données</a
    >
    <div class="legende">
      <span class="cle"
        ><svg width="24" height="12" aria-hidden="true"
          ><line x1="1" x2="23" y1="6" y2="6" stroke={couleurApres} stroke-width="3" /></svg
        >avec le scénario</span
      >
      <span class="cle"
        ><svg width="24" height="12" aria-hidden="true"
          ><line x1="1" x2="23" y1="6" y2="6" stroke={couleurAvant} stroke-width="2" /></svg
        >observée</span
      >
      <span class="cle"
        ><svg width="24" height="12" aria-hidden="true"
          ><line class="max" x1="1" x2="23" y1="6" y2="6" /></svg
        >maximum de {annee}</span
      >
      <span class="cle" class:absent={rnMaxPluriMw === rnMaxMw}
        ><svg width="24" height="12" aria-hidden="true"
          ><line class="max-pluri" x1="1" x2="23" y1="6" y2="6" /></svg
        >maximum {anneesPluri}</span
      >
    </div>
  </figcaption>

  <div class="trace" bind:clientWidth={largeur} bind:clientHeight={hauteur}>
    {#if true}
      {@const W = Math.max(300, largeur || 840)}
      {@const empile = W < 640}
      {@const Lp = empile ? W : (W - 32) / 2}
      {@const H = plein
        ? Math.max(120, Math.floor((hauteur || 320) - TITRE_PANNEAU))
        : empile
          ? 240
          : 280}
      <div class="panneaux" class:empile>
        {#each ['annee', 'zoom'] as const as p (p)}
          {@const av = points(avant, p)}
          {@const ap = points(apres, p)}
          {@const M = { haut: 22, bas: 36, gauche: 40, droite: 12 }}
          {@const x = scaleLinear()
            .domain([p === 'annee' ? 0 : 1, p === 'annee' ? n : Math.min(zoom, n)])
            .range([M.gauche, Lp - M.droite])}
          {@const bas = Math.min(av[av.length - 1][1], ap[ap.length - 1][1])}
          {@const haut = Math.max(av[0][1], ap[0][1], rnMaxMw, rnMaxPluriMw)}
          {@const y = scaleLinear()
            .domain([Math.min(bas, p === 'annee' ? 0 : bas), haut])
            .nice()
            .range([H - M.bas, M.haut])}
          {@const chemin = (m: Monotone) =>
            m.map(([r, v], k) => `${k ? 'L' : 'M'}${x(r).toFixed(1)},${y(v).toFixed(1)}`).join('')}
          <div class="panneau">
            <p class="titre-panneau" id="monotone-simulee-{p}">
              {p === 'annee'
                ? 'Toute l’année'
                : `Les ${formaterNombre(Math.min(zoom, n))} heures les plus tendues (zoom)`}
            </p>
            <div class="trace-panneau">
              <svg
                width={Lp}
                height={H}
                viewBox="0 0 {Lp} {H}"
                role="group"
                aria-labelledby="monotone-simulee-{p}"
              >
                {#each y.ticks(empile || H < 220 ? 4 : 6) as v (v)}
                  <line
                    class={v === 0 ? 'zero' : 'grille'}
                    x1={M.gauche}
                    x2={Lp - M.droite}
                    y1={y(v)}
                    y2={y(v)}
                  />
                  <text class="graduation" x={M.gauche - 6} y={y(v) + 4} text-anchor="end"
                    >{formaterNombre(v / 1000, 0)}</text
                  >
                {/each}
                <text class="graduation unite" x={M.gauche - 6} y={M.haut - 10} text-anchor="end"
                  >GW</text
                >
                {#each x.ticks(empile ? 3 : 4) as r (r)}
                  <line class="tic" x1={x(r)} x2={x(r)} y1={H - M.bas} y2={H - M.bas + 4} />
                  <text class="graduation" x={x(r)} y={H - M.bas + 17} text-anchor="middle"
                    >{formaterNombre(r)}</text
                  >
                {/each}
                <text class="graduation" x={Lp - M.droite} y={H - 3} text-anchor="end"
                  >rang de l’heure</text
                >
                <line
                  class="max"
                  x1={M.gauche}
                  x2={Lp - M.droite}
                  y1={y(rnMaxMw)}
                  y2={y(rnMaxMw)}
                />
                {#if rnMaxPluriMw === rnMaxMw}
                  <text class="mention" x={Lp - M.droite} y={y(rnMaxMw) - 6} text-anchor="end"
                    >maximum de {annee} et de {anneesPluri}, {gw(rnMaxMw)}</text
                  >
                {:else}
                  <line
                    class="max-pluri"
                    x1={M.gauche}
                    x2={Lp - M.droite}
                    y1={y(rnMaxPluriMw)}
                    y2={y(rnMaxPluriMw)}
                  />
                  <text class="mention" x={Lp - M.droite} y={y(rnMaxPluriMw) - 6} text-anchor="end"
                    >maximum {anneesPluri}, {gw(rnMaxPluriMw)}</text
                  >
                  <text
                    class="mention"
                    x={Lp - M.droite}
                    y={y(rnMaxMw) + (y(rnMaxMw) - y(rnMaxPluriMw) < 18 ? 14 : -6)}
                    text-anchor="end">maximum de {annee}, {gw(rnMaxMw)}</text
                  >
                {/if}
                {#if actif?.p === p}
                  <line
                    class="repere"
                    x1={x(av[actif.i][0])}
                    x2={x(av[actif.i][0])}
                    y1={M.haut}
                    y2={H - M.bas}
                  />
                {/if}
                <path class="courbe" d={chemin(av)} stroke={couleurAvant} />
                <path class="courbe forte" d={chemin(ap)} stroke={couleurApres} />
                <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
                <rect
                  class="zone"
                  x={M.gauche}
                  y={M.haut}
                  width={Lp - M.gauche - M.droite}
                  height={H - M.haut - M.bas}
                  tabindex="0"
                  role="application"
                  aria-roledescription="courbe"
                  aria-label="Parcourir les heures classées : flèches gauche et droite, Page précédente et Page suivante, Début et Fin."
                  onpointermove={(ev) => {
                    const b = (
                      ev.currentTarget as SVGRectElement
                    ).ownerSVGElement!.getBoundingClientRect();
                    const rang = x.invert(((ev.clientX - b.left) / b.width) * Lp);
                    actif = { p, i: proche(av, Math.max(1, rang)) };
                  }}
                  onpointerleave={() => (actif = null)}
                  onkeydown={(ev) => touche(ev, p)}
                  onfocus={() => (actif ??= { p, i: 0 })}
                  onblur={() => (actif = null)}
                />
              </svg>
              {#if actif?.p === p}
                <Infobulle
                  x={x(av[actif.i][0])}
                  y={M.haut + 8}
                  largeur={Lp}
                  titre={titreRang(av[actif.i][0])}
                  lignes={lignes(actif.i)}
                />
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
  <p class="lecteur" aria-live="polite">
    {#if actif}{titreRang(avant[actif.i][0])} : {lignes(actif.i)
        .map((l) => `${l.libelle}, ${l.valeur}`)
        .join(' ; ')}{/if}
  </p>
</figure>

<style>
  .monotone {
    margin: 0;
    padding-top: 0.5rem;
    border-top: 1px solid var(--encre);
    font-family: var(--sans);
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  /* En-tête : titre et lien sur une ligne, légende sur la suivante (hauteur indépendante des
     réglages : ni le titre ni la légende ne portent le libellé du scénario). */
  .entete {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: baseline;
    gap: 0.15rem 1rem;
    margin: 0 0 0.35rem;
  }
  @media (max-width: 40rem) {
    .entete {
      grid-template-columns: minmax(0, 1fr);
    }
  }
  h3 {
    margin: 0;
    font-size: 1.05rem;
    line-height: 1.25;
  }
  .notes {
    font-size: 0.9rem;
    white-space: nowrap;
  }
  .legende {
    grid-column: 1 / -1;
    display: flex;
    flex-wrap: wrap;
    gap: 0.2rem 1.1rem;
    font-size: 0.9rem;
    line-height: 1.3;
    color: var(--encre);
  }
  .cle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }
  /* Quand l'année est celle du maximum pluriannuel, la clé n'a pas d'objet : sa place reste. */
  .cle.absent {
    visibility: hidden;
  }
  .trace {
    position: relative;
    width: 100%;
  }
  /* Pleine fenêtre : le tracé prend la hauteur qui reste ; positionné en absolu, il ne pèse pas sur
     la hauteur de son conteneur (pas de boucle entre mesure et mise en page). */
  .plein {
    flex: 1 1 0;
  }
  .plein .trace {
    flex: 1 1 0;
    min-height: 0;
  }
  .plein .panneaux {
    position: absolute;
    inset: 0;
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
    margin: 0;
    height: 24px;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 24px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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
  .zero {
    stroke: var(--encre);
    stroke-width: 1.5;
  }
  .tic {
    stroke: var(--encre-2);
  }
  .graduation {
    fill: var(--encre-2);
    font-size: 12px;
    font-variant-numeric: tabular-nums;
  }
  .unite {
    fill: var(--encre);
    font-weight: 600;
  }
  .max {
    stroke: var(--encre);
    stroke-width: 1.25;
    stroke-dasharray: 5 4;
  }
  .max-pluri {
    stroke: var(--encre-2);
    stroke-width: 1.25;
    stroke-dasharray: 1.5 3;
    stroke-linecap: round;
  }
  .mention {
    fill: var(--encre);
    font-size: 12px;
    font-weight: 500;
    paint-order: stroke;
    stroke: var(--papier);
    stroke-width: 3px;
    stroke-linejoin: round;
  }
  .courbe {
    fill: none;
    stroke-width: 1.75;
    stroke-linejoin: round;
  }
  .courbe.forte {
    stroke-width: 2.75;
  }
  .repere {
    stroke: var(--encre-2);
    stroke-dasharray: 3 3;
  }
  .zone {
    fill: transparent;
    cursor: crosshair;
  }
  .zone:focus-visible {
    outline: 2px solid var(--encre);
    outline-offset: 2px;
  }
</style>
