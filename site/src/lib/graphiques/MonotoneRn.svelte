<script lang="ts">
  // Monotone de la charge résiduelle (consommation − éolien − solaire − nucléaire disponible
  // déclaré), une courbe par année de 2022 à 2025, 2025 la plus marquée. Heures classées de la plus
  // tendue (rang 1) à la moins tendue ; zéro marqué. SVG rendu au prérendu, lisible sans JS.
  import { scaleLinear } from 'd3-scale';
  import { formaterNombre } from '$lib/format';
  import {
    ANNEES_COMPAREES,
    ecarter,
    gw,
    heureParis,
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
  const derniere = $derived(annees[annees.length - 1]);
  const couleur = (i: number) => `var(--annee-${i + 1})`;

  /** Indice de l'échantillon de rang le plus proche (les rangs sont croissants). */
  function proche(a: AnneeQuand, rang: number): number {
    let bas = 0;
    let haut = a.monotone.length - 1;
    while (haut - bas > 1) {
      const m = (bas + haut) >> 1;
      if (a.monotone[m][0] <= rang) bas = m;
      else haut = m;
    }
    return rang - a.monotone[bas][0] <= a.monotone[haut][0] - rang ? bas : haut;
  }

  // Rang survolé ou choisi au clavier (index dans l'échantillon de l'année la plus récente).
  let indice = $state<number | null>(null);
  const rangActif = $derived(indice === null ? null : derniere.monotone[indice][0]);

  function lignes(rang: number): LigneInfobulle[] {
    return [...annees].reverse().map((a) => {
      const [r, v] = a.monotone[proche(a, rang)];
      return {
        valeur: gw(v),
        libelle: r === rang ? String(a.annee) : `${a.annee} (rang ${formaterNombre(r)})`
      };
    });
  }
  const titreRang = (rang: number) =>
    rang === 1
      ? 'Heure la plus tendue de l’année'
      : `${formaterNombre(rang)}e heure la plus tendue`;

  function touche(ev: KeyboardEvent) {
    const n = derniere.monotone.length;
    const i = indice ?? 0;
    const pas: Record<string, number> = {
      ArrowRight: 1,
      ArrowLeft: -1,
      ArrowUp: 1,
      ArrowDown: -1,
      PageDown: 25,
      PageUp: -25
    };
    let suivant: number | null = null;
    if (ev.key in pas) suivant = Math.min(n - 1, Math.max(0, i + pas[ev.key]));
    else if (ev.key === 'Home') suivant = 0;
    else if (ev.key === 'End') suivant = n - 1;
    else if (ev.key === 'Escape') indice = null;
    if (suivant !== null) {
      ev.preventDefault();
      indice = suivant;
    }
  }

  const annonce = $derived(
    rangActif === null
      ? ''
      : `${titreRang(rangActif)} : ${lignes(rangActif)
          .map((l) => `${l.libelle}, ${l.valeur}`)
          .join(' ; ')}`
  );

  const QUANTILES = [
    ['p99', '1 %'],
    ['p90', '10 %'],
    ['p50', '50 %'],
    ['p10', '90 %'],
    ['p01', '99 %']
  ] as const;
</script>

<Figure
  id="monotone-rn"
  titre="Charge résiduelle, heures classées de la plus tendue à la moins tendue, 2022 à 2025"
  sousTitre="En GW, moyenne de chaque heure. Charge résiduelle = consommation − éolien − solaire − nucléaire disponible déclaré par EDF. Au-dessus de zéro, ce que doit fournir le reste du système (hydraulique, thermique, bioénergies, échanges, stockage, effacements) ; au-dessous, un surplus avant exports et pompage."
  remarques="Ce n’est pas une marge : la puissance disponible de l’hydraulique, du thermique et des importations n’est pas observée heure par heure. France continentale hors Corse. Les cent premières heures sont tracées une à une, puis une heure sur vingt ; l’infobulle donne la valeur de l’heure tracée la plus proche."
  sources={sourcesRn(q)}
  titreTableau="Tableau des données : quantiles de la charge résiduelle, 2015 à 2025"
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
          /></svg
        >{a.annee}</span
      >
    {/each}
  {/snippet}

  {#snippet trace(largeur: number)}
    {@const W = Math.max(300, largeur)}
    {@const etroit = W < 560}
    {@const M = { haut: 18, bas: 40, gauche: 40, droite: etroit ? 44 : 56 }}
    {@const H = etroit ? 300 : 360}
    {@const nMax = Math.max(...annees.map((a) => a.heures))}
    {@const x = scaleLinear()
      .domain([0, nMax])
      .range([M.gauche, W - M.droite])}
    {@const y = scaleLinear()
      .domain([Math.min(...annees.map((a) => a.minMw)), Math.max(...annees.map((a) => a.maxMw))])
      .nice()
      .range([H - M.bas, M.haut])}
    {@const graduations = y.ticks(etroit ? 5 : 7)}
    {@const chemin = (a: AnneeQuand) =>
      a.monotone
        .map(([r, v], k) => `${k ? 'L' : 'M'}${x(r).toFixed(1)},${y(v).toFixed(1)}`)
        .join('')}
    {@const fins = ecarter(
      annees.map((a, i) => ({ i, annee: a.annee, y: y(a.monotone[a.monotone.length - 1][1]) })),
      14,
      M.haut,
      H - M.bas - 4
    )}
    {@const xMax = x(1)}
    {@const yMax = y(derniere.maxMw)}
    <svg
      width={W}
      height={H}
      viewBox="0 0 {W} {H}"
      role="img"
      aria-label="Monotones de la charge résiduelle de 2022 à 2025. Maximum {gw(
        derniere.maxMw
      )} en {derniere.annee}. Valeurs détaillées dans le tableau des données."
    >
      {#each graduations as v (v)}
        <line
          class={v === 0 ? 'zero' : 'grille'}
          x1={M.gauche}
          x2={W - M.droite}
          y1={y(v)}
          y2={y(v)}
        />
        <text
          class="graduation"
          class:fort={v === 0}
          x={M.gauche - 6}
          y={y(v) + 4}
          text-anchor="end">{formaterNombre(v / 1000, 0)}</text
        >
      {/each}
      <text class="graduation unite" x={M.gauche - 6} y={M.haut - 6} text-anchor="end">GW</text>
      {#each [0, 2000, 4000, 6000, 8000] as h (h)}
        <line class="tic" x1={x(h)} x2={x(h)} y1={H - M.bas} y2={H - M.bas + 4} />
        <text class="graduation" x={x(h)} y={H - M.bas + 17} text-anchor="middle"
          >{formaterNombre(h)}</text
        >
      {/each}
      <text class="graduation" x={W - M.droite} y={H - 4} text-anchor="end"
        >heures de l’année, classées</text
      >
      <!-- Lecture du zéro, dans les zones laissées vides par les courbes. -->
      <text class="mention" x={x(nMax * 0.86)} y={y(0) - 7} text-anchor="end"
        >{etroit ? 'à fournir' : 'au-dessus : à fournir par le reste du système'}</text
      >
      <text class="mention" x={x(nMax * 0.04)} y={y(0) + 17}
        >{etroit ? 'surplus' : 'au-dessous : surplus avant exports et pompage'}</text
      >
      {#if rangActif !== null}
        <line class="repere" x1={x(rangActif)} x2={x(rangActif)} y1={M.haut} y2={H - M.bas} />
      {/if}
      {#each annees as a, i (a.annee)}
        <path
          class="courbe"
          class:forte={i === annees.length - 1}
          d={chemin(a)}
          stroke={couleur(i)}
        />
      {/each}
      <!-- Maximum de l'année la plus récente, seule valeur étiquetée sur le tracé. -->
      <circle class="point" cx={xMax} cy={yMax} r="4" fill={couleur(annees.length - 1)} />
      <text class="etiquette" x={xMax + 9} y={yMax + 4}
        >{gw(derniere.maxMw)}{etroit ? '' : `, ${heureParis(derniere.maxDebutParis)}`}</text
      >
      {#each fins as f (f.annee)}
        <text class="etiquette annee" x={W - M.droite + 6} y={f.y + 4}>{f.annee}</text>
      {/each}
      <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
      <rect
        class="zone"
        x={M.gauche}
        y={M.haut}
        width={W - M.gauche - M.droite}
        height={H - M.haut - M.bas}
        tabindex="0"
        role="application"
        aria-roledescription="courbe"
        aria-label="Parcourir les heures classées : flèches gauche et droite, Page précédente et Page suivante pour aller plus vite, Début et Fin."
        onpointermove={(ev) => {
          const r = (ev.currentTarget as SVGRectElement).ownerSVGElement!.getBoundingClientRect();
          const rang = x.invert(((ev.clientX - r.left) / r.width) * W);
          indice = proche(derniere, Math.max(1, rang));
        }}
        onpointerleave={() => (indice = null)}
        onkeydown={touche}
        onfocus={() => (indice ??= 0)}
        onblur={() => (indice = null)}
      />
    </svg>
    {#if rangActif !== null}
      <Infobulle
        x={x(rangActif)}
        y={M.haut + 8}
        largeur={W}
        titre={titreRang(rangActif)}
        lignes={lignes(rangActif)}
      />
    {/if}
    <p class="lecteur" aria-live="polite">{annonce}</p>
  {/snippet}

  {#snippet tableau()}
    <table>
      <caption class="lecteur">Quantiles de la charge résiduelle horaire, en GW, par année</caption>
      <thead>
        <tr>
          <th scope="col">Année</th>
          <th scope="col" class="num">Maximum</th>
          {#each QUANTILES as [, part] (part)}
            <th scope="col" class="num">Dépassé {part} du temps</th>
          {/each}
          <th scope="col" class="num">Minimum</th>
          <th scope="col" class="num">Heures sous zéro</th>
          <th scope="col" class="num">Heures valides</th>
        </tr>
      </thead>
      <tbody>
        {#each q.annees as a (a.annee)}
          <tr>
            <th scope="row">{a.annee}</th>
            <td class="num">{gw(a.maxMw, false)}</td>
            {#each QUANTILES as [k] (k)}
              <td class="num">{gw(a.quantilesMw[k], false)}</td>
            {/each}
            <td class="num">{gw(a.minMw, false)}</td>
            <td class="num">{formaterNombre(a.heuresNegatives)}</td>
            <td class="num">{formaterNombre(a.heuresValides)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
    <p class="note-tableau">
      GW, moyenne horaire. « Dépassé 10 % du temps » : quantile à 90 % des heures valides de l’année
      (interpolation linéaire entre rangs). Les heures non valides sont celles où une série manque.
    </p>
  {/snippet}
</Figure>

<style>
  svg {
    display: block;
    max-width: 100%;
    height: auto;
    overflow: visible;
    font-family: var(--sans);
  }
  .cle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-variant-numeric: tabular-nums;
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
    font-size: 13px;
    font-variant-numeric: tabular-nums;
  }
  .graduation.fort,
  .unite {
    fill: var(--encre);
    font-weight: 600;
  }
  .mention {
    fill: var(--encre-2);
    font-size: 13px;
  }
  /* Halo couleur papier : une étiquette reste lisible quand elle croise une courbe. */
  .mention,
  .etiquette {
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
  .point {
    stroke: var(--papier);
    stroke-width: 2;
  }
  .etiquette {
    fill: var(--encre);
    font-size: 13px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
  .etiquette.annee {
    font-weight: 500;
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
  .note-tableau {
    font-size: 0.85rem;
    color: var(--encre-2);
    max-width: 46rem;
  }
</style>
