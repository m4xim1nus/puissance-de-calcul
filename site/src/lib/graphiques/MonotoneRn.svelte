<script lang="ts">
  // Monotone de la charge résiduelle (consommation − éolien − solaire − nucléaire disponible
  // déclaré), une courbe par année de 2022 à 2025. Deux panneaux : l'année entière (zéro marqué),
  // et un zoom sur les 500 heures les plus tendues, objet de la section (repère des cent heures,
  // maximum 2015-2025). Couleur et motif de trait par année. SVG rendu au prérendu, lisible sans JS.
  import { scaleLinear } from 'd3-scale';
  import { formaterNombre } from '$lib/format';
  import {
    ANNEES_COMPAREES,
    TRAITS_ANNEES,
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
  const reference = $derived(q.rnMaxPluriannuel);
  const couleur = (i: number) => `var(--annee-${i + 1})`;
  const trait = (i: number) => TRAITS_ANNEES[i] || undefined;

  /** Rangs montrés par le zoom. */
  const RANG_ZOOM = 500;
  /** Heures tendues de la section (repère du zoom). */
  const HEURES_TENDUES = 100;

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

  type Panneau = 'annee' | 'zoom';
  // Échantillon survolé ou choisi au clavier, dans la monotone de l'année la plus récente.
  let actif = $state<{ p: Panneau; i: number } | null>(null);
  const dernierIndice = (p: Panneau) =>
    p === 'zoom' ? proche(derniere, RANG_ZOOM) : derniere.monotone.length - 1;

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

  function touche(p: Panneau, ev: KeyboardEvent) {
    const n = dernierIndice(p);
    const i = actif?.p === p ? actif.i : 0;
    const pas: Record<string, number> = {
      ArrowRight: 1,
      ArrowLeft: -1,
      ArrowUp: 1,
      ArrowDown: -1,
      PageDown: 25,
      PageUp: -25
    };
    let suivant: number | null = null;
    if (ev.key in pas) suivant = Math.min(n, Math.max(0, i + pas[ev.key]));
    else if (ev.key === 'Home') suivant = 0;
    else if (ev.key === 'End') suivant = n;
    else if (ev.key === 'Escape') actif = null;
    if (suivant !== null) {
      ev.preventDefault();
      actif = { p, i: suivant };
    }
  }

  const rangActif = $derived(actif === null ? null : derniere.monotone[actif.i][0]);
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
  sousTitre="En GW, moyenne de chaque heure. Charge résiduelle = consommation − éolien − solaire − nucléaire disponible déclaré par EDF. Au-dessus de zéro, ce que doit fournir le reste du système (hydraulique, thermique, bioénergies, échanges, stockage) ; au-dessous, un surplus avant exports et pompage. Second panneau : les 500 heures les plus tendues, agrandies."
  remarques="Ce n’est pas une marge : la puissance disponible de l’hydraulique, du thermique et des importations n’est pas observée heure par heure. Les effacements activés sont déjà retranchés de la consommation observée. France continentale hors Corse. Les cent premières heures sont tracées une à une, puis une heure sur vingt ; l’infobulle donne la valeur de l’heure tracée la plus proche."
  sources={sourcesRn(q)}
  titreTableau="Tableau des données : quantiles de la charge résiduelle, 2015 à 2025"
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
    {@const cote = W >= 760}
    {@const Wa = cote ? Math.round((W - 32) * 0.6) : W}
    {@const Wz = cote ? W - 32 - Wa : W}
    <div class="panneaux" class:juxtaposes={cote}>
      {@render panneau('annee', Wa)}
      {@render panneau('zoom', Wz)}
    </div>
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
      Maximum {reference.annees} : {gw(reference.valeurMw)}, {heureParis(reference.debutParis)} (heure
      de Paris).
    </p>
  {/snippet}
</Figure>

{#snippet panneau(p: Panneau, L: number)}
  {@const etroit = L < 480}
  {@const zoom = p === 'zoom'}
  {@const M = { haut: 18, bas: 40, gauche: 40, droite: 46 }}
  {@const H = etroit ? 290 : 340}
  {@const nMax = zoom ? RANG_ZOOM : Math.max(...annees.map((a) => a.heures))}
  {@const x = scaleLinear()
    .domain([zoom ? 1 : 0, nMax])
    .range([M.gauche, L - M.droite])}
  {@const y = scaleLinear()
    .domain(
      zoom
        ? [0, Math.max(reference.valeurMw, ...annees.map((a) => a.maxMw))]
        : [Math.min(...annees.map((a) => a.minMw)), Math.max(...annees.map((a) => a.maxMw))]
    )
    .nice()
    .range([H - M.bas, M.haut])}
  {@const points = (a: AnneeQuand) =>
    zoom ? a.monotone.slice(0, proche(a, RANG_ZOOM) + 1) : a.monotone}
  {@const chemin = (a: AnneeQuand) =>
    points(a)
      .map(([r, v], k) => `${k ? 'L' : 'M'}${x(r).toFixed(1)},${y(v).toFixed(1)}`)
      .join('')}
  {@const fins = ecarter(
    annees.map((a, i) => {
      const pts = points(a);
      return { i, annee: a.annee, y: y(pts[pts.length - 1][1]) + 4 };
    }),
    15,
    M.haut + 4,
    H - M.bas + 12
  )}
  {@const ticksX = zoom ? [1, 100, 200, 300, 400, 500] : [0, 2000, 4000, 6000, 8000]}
  {@const titre = zoom ? `Zoom : les ${RANG_ZOOM} heures les plus tendues` : 'L’année entière'}
  <div class="panneau">
    <p class="titre-panneau" id="monotone-rn-{p}">{titre}</p>
    <div class="trace-panneau">
      <svg
        width={L}
        height={H}
        viewBox="0 0 {L} {H}"
        role="img"
        aria-labelledby="monotone-rn-{p}"
        aria-describedby="monotone-rn-titre"
      >
        {#each y.ticks(etroit ? 5 : 7) as v (v)}
          <line
            class={v === 0 ? 'zero' : 'grille'}
            x1={M.gauche}
            x2={L - M.droite}
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
        {#each ticksX as h (h)}
          <line class="tic" x1={x(h)} x2={x(h)} y1={H - M.bas} y2={H - M.bas + 4} />
          <text class="graduation" x={x(h)} y={H - M.bas + 17} text-anchor="middle"
            >{formaterNombre(h)}</text
          >
        {/each}
        <text class="graduation" x={L - M.droite} y={H - 4} text-anchor="end"
          >{zoom ? 'rang de l’heure' : 'heures de l’année, classées'}</text
        >
        {#if zoom}
          <!-- Repère des cent heures tendues et maximum 2015-2025. -->
          <line
            class="repere-fixe"
            x1={x(HEURES_TENDUES)}
            x2={x(HEURES_TENDUES)}
            y1={M.haut}
            y2={H - M.bas}
          />
          <text class="mention" x={x(HEURES_TENDUES) + 5} y={y(4000)}
            >{etroit ? '100 h' : 'les 100 heures tendues'}</text
          >
          <line
            class="reference"
            x1={M.gauche}
            x2={L - M.droite}
            y1={y(reference.valeurMw)}
            y2={y(reference.valeurMw)}
          />
          <text class="mention" x={L - M.droite} y={y(reference.valeurMw) - 6} text-anchor="end"
            >max. {reference.annees} : {gw(reference.valeurMw)}{etroit
              ? ''
              : `, ${heureParis(reference.debutParis)}`}</text
          >
        {:else}
          <!-- Lecture du zéro, dans les zones laissées vides par les courbes. -->
          <text class="mention" x={L - M.droite - 4} y={y(25000)} text-anchor="end"
            >{etroit
              ? '↑ au-dessus de 0 : à fournir'
              : '↑ au-dessus de 0 : à fournir par le reste du système'}</text
          >
          <text class="mention" x={x(nMax * (etroit ? 0.22 : 0.28))} y={y(-17000)}
            >{etroit ? '↓ sous 0 : surplus' : '↓ sous 0 : surplus avant exports et pompage'}</text
          >
        {/if}
        {#if actif?.p === p && rangActif !== null}
          <line class="repere" x1={x(rangActif)} x2={x(rangActif)} y1={M.haut} y2={H - M.bas} />
        {/if}
        {#each annees as a, i (a.annee)}
          <path
            class="courbe"
            class:forte={i === annees.length - 1}
            d={chemin(a)}
            stroke={couleur(i)}
            stroke-dasharray={trait(i)}
          />
        {/each}
        {#if !zoom}
          <!-- Maximum de l'année la plus récente, seule valeur étiquetée sur ce panneau. -->
          <circle
            class="point"
            cx={x(1)}
            cy={y(derniere.maxMw)}
            r="4"
            fill={couleur(annees.length - 1)}
          />
          <text class="etiquette" x={x(1) + 9} y={y(derniere.maxMw) + 4}
            >{derniere.annee} : {gw(derniere.maxMw)}{etroit
              ? ''
              : `, ${heureParis(derniere.maxDebutParis)}`}</text
          >
        {/if}
        {#each fins as f (f.annee)}
          <text class="etiquette annee" x={L - M.droite + 6} y={f.y}>{f.annee}</text>
        {/each}
        <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
        <rect
          class="zone"
          x={M.gauche}
          y={M.haut}
          width={L - M.gauche - M.droite}
          height={H - M.haut - M.bas}
          tabindex="0"
          role="application"
          aria-roledescription="courbe"
          aria-label="{titre}. Parcourir les heures classées : flèches gauche et droite, Page précédente et Page suivante pour aller plus vite, Début et Fin."
          onpointermove={(ev) => {
            const r = (ev.currentTarget as SVGRectElement).ownerSVGElement!.getBoundingClientRect();
            const rang = x.invert(((ev.clientX - r.left) / r.width) * L);
            actif = { p, i: Math.min(dernierIndice(p), proche(derniere, Math.max(1, rang))) };
          }}
          onpointerleave={() => (actif = null)}
          onkeydown={(ev) => touche(p, ev)}
          onfocus={() => (actif ??= { p, i: 0 })}
          onblur={() => (actif = null)}
        />
      </svg>
      {#if actif?.p === p && rangActif !== null}
        <Infobulle
          x={x(rangActif)}
          y={M.haut + 8}
          largeur={L}
          titre={titreRang(rangActif)}
          lignes={lignes(rangActif)}
        />
      {/if}
    </div>
  </div>
{/snippet}

<style>
  .cle {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-variant-numeric: tabular-nums;
  }
  .panneaux {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 1.25rem;
  }
  .panneaux.juxtaposes {
    grid-template-columns: 3fr 2fr;
    gap: 2rem;
  }
  .titre-panneau {
    margin: 0 0 0.3rem;
    font-size: 0.95rem;
    font-weight: 600;
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
    stroke-width: 2;
    stroke-linejoin: round;
    stroke-linecap: round;
  }
  .courbe.forte {
    stroke-width: 3;
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
  .repere-fixe {
    stroke: var(--encre-2);
    stroke-width: 1;
  }
  .reference {
    stroke: var(--encre);
    stroke-width: 1.25;
    stroke-dasharray: 6 3;
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
