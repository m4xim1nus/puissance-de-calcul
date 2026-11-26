<script lang="ts">
  // Pyramide des puissances : un étage par ligne, une échelle logarithmique commune, chaque valeur
  // avec sa date. Jamais de somme ni d'entonnoir : les étages sont des grandeurs différentes.
  import { scaleLog } from 'd3-scale';
  import type { Chiffres } from '$lib/chiffres';
  import { formaterValeur } from '$lib/format';
  import Figure from './Figure.svelte';
  import Infobulle from './Infobulle.svelte';
  import {
    HORS_PYRAMIDE,
    horsPyramide,
    idsPyramide,
    ligneDonnees,
    pyramide,
    sourcesGraphique,
    type PointPyramide
  } from './donnees';
  import { largeurTexte, placerEtiquettes } from './etiquettes';

  let { chiffres }: { chiffres: Chiffres } = $props();

  const etages = $derived(pyramide(chiffres));
  const hors = $derived(horsPyramide(chiffres));
  const tableau = $derived(
    [...idsPyramide(), ...HORS_PYRAMIDE].map((id) => ligneDonnees(chiffres, id))
  );
  const sources = $derived(sourcesGraphique(chiffres, [...idsPyramide(), ...HORS_PYRAMIDE]));
  const remarques = $derived(
    [
      ...hors.map(
        (h) =>
          `Hors étage : ${h.libelle}, ${h.texte}. Ce n’est pas un palier du contrat, il ne figure donc pas à l’étage « Signée ».`
      ),
      'Ne figurent pas non plus la pointe appelée par une cohorte de data centers récents ni la puissance mise à disposition sur plusieurs années : ni la même cohorte, ni la même année, ni la même grandeur que les valeurs ci-dessus (voir le texte).'
    ].join(' ')
  );

  const TAILLE = 14;
  const PAS_VOIE = 19;

  const texteEtiquette = (p: PointPyramide) =>
    [p.valeur, p.date, p.precision].filter(Boolean).join(' · ');
  const etiquetteMW = (mw: number) =>
    mw >= 1000 ? formaterValeur(mw / 1000, 'GW') : formaterValeur(mw, 'MW');

  let actif = $state<{ p: PointPyramide; etage: string; x: number; y: number } | null>(null);
  let cadre: HTMLDivElement | undefined = $state();

  function montrer(p: PointPyramide, etage: string, cible: Element) {
    if (!cadre) return;
    const r = cible.getBoundingClientRect();
    const o = cadre.getBoundingClientRect();
    actif = { p, etage, x: r.left + r.width / 2 - o.left, y: r.top - o.top };
  }
</script>

<Figure
  id="pyramide"
  titre="Les puissances des data centers en France, étage par étage : recherchée, réservée (dont la pré-réservation fast-track), signée, raccordée, appelée"
  sousTitre="En MW ou GW, sur une échelle logarithmique (chaque graduation principale vaut dix fois la précédente). Chaque valeur porte sa date. Les étages ne s’additionnent pas et ne forment pas un entonnoir : ni les périmètres ni les dates ne coïncident."
  {remarques}
  {sources}
  lignes={tableau}
>
  {#snippet legende()}
    <span class="cle"
      ><svg width="14" height="14" aria-hidden="true"
        ><circle cx="7" cy="7" r="5" fill="var(--donnee)" /></svg
      > valeur publiée</span
    >
    <span class="cle"
      ><svg width="14" height="14" aria-hidden="true"
        ><circle
          cx="7"
          cy="7"
          r="4.5"
          fill="var(--papier)"
          stroke="var(--donnee)"
          stroke-width="2"
        /></svg
      > calcul du site à partir de valeurs publiées</span
    >
    <span class="cle"
      ><svg width="14" height="14" aria-hidden="true"
        ><rect x="2" y="2" width="10" height="10" fill="var(--donnee)" /></svg
      > autre source et autre définition que les ronds du même étage</span
    >
  {/snippet}
  {#snippet trace(largeur: number)}
    {@const W = Math.max(280, largeur)}
    {@const tous = etages.flatMap((e) => e.points.map((p) => p.mw))}
    {@const x = scaleLog()
      .domain([Math.min(...tous) / 1.6, Math.max(...tous) * 1.6])
      .range([8, W - 8])}
    {@const [d0, d1] = x.domain()}
    {@const decades = x.ticks().filter((t) => /^1/.test(String(t)) && t >= d0 && t <= d1)}
    {@const mineures = x.ticks().filter((t) => /^[25]/.test(String(t)) && t >= d0 && t <= d1)}
    <div class="pyramide" bind:this={cadre}>
      <svg class="axe" width={W} height="22" viewBox="0 0 {W} 22" aria-hidden="true">
        {#each decades as t (t)}
          <text x={x(t)} y="15" text-anchor="middle">{etiquetteMW(t)}</text>
        {/each}
      </svg>
      {#each etages as e (e.cle)}
        {@const places = placerEtiquettes(
          e.points.map((p) => ({ x: x(p.mw), largeur: largeurTexte(texteEtiquette(p), TAILLE) })),
          W
        )}
        {@const dessus = Math.max(0, ...places.map((p) => -p.voie))}
        {@const dessous = Math.max(0, ...places.map((p) => p.voie))}
        {@const Y_POINT = 12 + dessus * PAS_VOIE + (dessus ? 6 : 0)}
        {@const H = Y_POINT + 24 + dessous * PAS_VOIE + 10}
        {@const ligneTexte = (voie: number) =>
          voie >= 0 ? Y_POINT + 24 + voie * PAS_VOIE : Y_POINT - 11 + (voie + 1) * PAS_VOIE}
        <div class="etage">
          <p class="tete">
            <span class="nom">{e.nom}</span>
            <span class="nature">{e.nature}</span>
          </p>
          <svg
            width={W}
            height={H}
            viewBox="0 0 {W} {H}"
            role="group"
            aria-label="Puissance {e.nom.toLowerCase()}"
          >
            {#each mineures as t (t)}
              <line class="grille mineure" x1={x(t)} x2={x(t)} y1="0" y2={H} />
            {/each}
            {#each decades as t (t)}
              <line class="grille" x1={x(t)} x2={x(t)} y1="0" y2={H} />
            {/each}
            <line class="base" x1={x(d0)} x2={x(d1)} y1={Y_POINT} y2={Y_POINT} />
            {#each e.points as p, i (p.id)}
              {@const px = x(p.mw)}
              {@const pl = places[i]}
              {@const yl = ligneTexte(pl.voie)}
              <!-- svelte-ignore a11y_no_noninteractive_tabindex (marque focalisable : l'infobulle s'affiche au clavier comme au survol) -->
              <g
                class="marque"
                tabindex="0"
                role="img"
                aria-label="{e.nom} : {texteEtiquette(p)}{p.calcul ? ', calcul du site' : ''}"
                onpointerenter={(ev) => montrer(p, e.nom, ev.currentTarget)}
                onpointerleave={() => (actif = null)}
                onfocus={(ev) => montrer(p, e.nom, ev.currentTarget)}
                onblur={() => (actif = null)}
              >
                {#if pl.voie > 0}
                  <line class="renvoi" x1={px} x2={px} y1={Y_POINT + 7} y2={yl - 12} />
                {:else if pl.voie < -1}
                  <line class="renvoi" x1={px} x2={px} y1={Y_POINT - 7} y2={yl + 4} />
                {/if}
                <rect class="cible" x={px - 12} y={Y_POINT - 12} width="24" height="24" />
                {#if p.forme === 'carre'}
                  <rect x={px - 5} y={Y_POINT - 5} width="10" height="10" class="plein" />
                {:else if p.calcul}
                  <circle cx={px} cy={Y_POINT} r="5" class="creux" />
                {:else}
                  <circle cx={px} cy={Y_POINT} r="5.5" class="plein" />
                {/if}
                <text x={pl.x} y={yl} text-anchor={pl.ancre} class="etiquette"
                  ><tspan class="v">{p.valeur}</tspan><tspan class="d"
                    >{' · '}{[p.date, p.precision].filter(Boolean).join(' · ')}</tspan
                  ></text
                >
              </g>
            {/each}
          </svg>
        </div>
      {/each}
      <svg class="axe" width={W} height="22" viewBox="0 0 {W} 22" aria-hidden="true">
        {#each decades as t (t)}
          <text x={x(t)} y="15" text-anchor="middle">{etiquetteMW(t)}</text>
        {/each}
      </svg>
      {#if actif}
        <Infobulle
          x={actif.x}
          y={actif.y}
          largeur={W}
          titre={actif.p.libelle}
          lignes={[
            {
              valeur: actif.p.valeur,
              libelle: `${actif.p.date}${actif.p.calcul ? ' · calcul du site' : ''}`
            }
          ]}
        />
      {/if}
    </div>
  {/snippet}
</Figure>

<style>
  .pyramide {
    position: relative;
  }
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
  }
  .axe text {
    fill: var(--encre-2);
    font-size: 13px;
  }
  .etage {
    border-top: 1px solid var(--trait);
    padding-top: 0.35rem;
  }
  .etage:last-of-type {
    border-bottom: 1px solid var(--trait);
  }
  .tete {
    margin: 0 0 0.2rem;
    font-size: 0.95rem;
    line-height: 1.3;
  }
  .nom {
    font-weight: 600;
    font-size: 1.05rem;
    margin-right: 0.4rem;
  }
  .nature {
    color: var(--encre-2);
  }
  .grille {
    stroke: var(--trait);
    stroke-width: 1;
  }
  .grille.mineure {
    stroke-opacity: 0.45;
  }
  .base {
    stroke: var(--trait);
    stroke-width: 1;
  }
  .renvoi {
    stroke: var(--encre-2);
    stroke-width: 1;
  }
  .plein {
    fill: var(--donnee);
    stroke: var(--papier);
    stroke-width: 2;
  }
  .creux {
    fill: var(--papier);
    stroke: var(--donnee);
    stroke-width: 2;
  }
  .etiquette {
    font-size: 14px;
    paint-order: stroke;
    stroke: var(--papier);
    stroke-width: 4px;
    stroke-linejoin: round;
  }
  .etiquette .v {
    fill: var(--encre);
    font-weight: 600;
  }
  .etiquette .d {
    fill: var(--encre-2);
  }
  .cible {
    fill: transparent;
  }
  .marque {
    outline: none;
  }
  .marque:focus-visible .cible {
    stroke: var(--encre);
    stroke-width: 1.5;
  }
</style>
