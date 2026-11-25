<script lang="ts">
  // Trajectoires de consommation des data centers : 2024 (sites dédiés, intervalle), puis les deux
  // trajectoires du Bilan prévisionnel 2025 en 2030 et 2035. Les fourchettes du BP2023 et le
  // tendanciel de l'ADEME, sur un périmètre élargi (centres internes compris), en style distinct.
  import { scaleLinear } from 'd3-scale';
  import type { Chiffres } from '$lib/chiffres';
  import Figure from './Figure.svelte';
  import Infobulle, { type LigneInfobulle } from './Infobulle.svelte';
  import {
    idsTrajectoires,
    ligneDonnees,
    sourcesGraphique,
    trajectoires,
    type PointTrajectoire
  } from './donnees';

  let { chiffres }: { chiffres: Chiffres } = $props();

  const t = $derived(trajectoires(chiffres));
  const tableau = $derived(
    idsTrajectoires().map((id) => {
      const libelles: Record<string, string> = {
        dc_conso_sites_dedies_2024: 'Sites dédiés, 2024'
      };
      return ligneDonnees(chiffres, id, libelles[id]);
    })
  );
  const sources = $derived(sourcesGraphique(chiffres, idsTrajectoires()));

  // Décalage horizontal (vers la gauche, où les trajectoires passent plus bas) des marques
  // « périmètre élargi », en pixels, pour qu'elles ne se superposent pas aux points du BP2025.
  const DECALAGE = -16;
  const milieu = (p: PointTrajectoire) => (p.min + p.max) / 2;

  let annee = $state<number | null>(null);

  function lignesAnnee(a: number): LigneInfobulle[] {
    const de = (pts: PointTrajectoire[]) => pts.find((p) => p.annee === a);
    const l: LigneInfobulle[] = [];
    if (t.depart.annee === a)
      l.push({ valeur: t.depart.texte, libelle: 'sites dédiés (RTE)', cle: 'forte' });
    const r = de(t.rapide);
    if (r) l.push({ valeur: r.texte, libelle: 'décarbonation rapide (BP2025)', cle: 'forte' });
    const le = de(t.lente);
    if (le) l.push({ valeur: le.texte, libelle: 'décarbonation lente (BP2025)', cle: 'faible' });
    const b = de(t.bp2023);
    if (b) l.push({ valeur: b.texte, libelle: 'BP2023, centres internes compris', cle: 'autre' });
    const ad = de(t.ademe);
    if (ad)
      l.push({
        valeur: ad.texte,
        libelle: 'ADEME tendanciel, centres internes compris',
        cle: 'autre'
      });
    return l;
  }

  /** Écarte verticalement des étiquettes de fin de ligne (au moins `pas` pixels entre elles). */
  function ecarter<T extends { y: number }>(items: T[], pas: number, haut: number): T[] {
    const tri = [...items].sort((a, b) => a.y - b.y);
    for (let i = 0; i < tri.length; i++) {
      if (i === 0) tri[i].y = Math.max(tri[i].y, haut);
      else tri[i].y = Math.max(tri[i].y, tri[i - 1].y + pas);
    }
    return tri;
  }
</script>

<Figure
  id="trajectoires"
  titre="Consommation des data centers en France : 2024, puis les trajectoires de RTE pour 2030 et 2035"
  sousTitre="En TWh par an. En bleu, les sites dédiés (Bilan prévisionnel 2025 de RTE) ; en orange, des exercices sur un périmètre élargi aux centres internes, qui ne se comparent pas directement aux trajectoires bleues."
  remarques="Seules les années 2024, 2030 et 2035 sont reprises : les segments relient ces valeurs publiées et partent du milieu de l’intervalle de 2024 ; ils ne décrivent pas les années intermédiaires."
  {sources}
  lignes={tableau}
>
  {#snippet legende()}
    <span class="cle"
      ><svg width="22" height="14" aria-hidden="true"
        ><line x1="1" x2="21" y1="7" y2="7" stroke="var(--donnee)" stroke-width="2" /></svg
      > décarbonation rapide (BP2025)</span
    >
    <span class="cle"
      ><svg width="22" height="14" aria-hidden="true"
        ><line x1="1" x2="21" y1="7" y2="7" stroke="var(--donnee-faible)" stroke-width="2" /></svg
      > décarbonation lente (BP2025)</span
    >
    <span class="cle"
      ><svg width="14" height="14" aria-hidden="true"
        ><rect x="3" y="1" width="8" height="12" rx="4" fill="var(--encre-2)" /></svg
      > 2024, intervalle publié</span
    >
    <span class="cle"
      ><svg width="14" height="16" aria-hidden="true"
        ><path
          d="M3 2h8M7 2v12M3 14h8"
          stroke="var(--donnee-autre)"
          stroke-width="2"
          fill="none"
        /></svg
      > fourchette du BP2023, centres internes compris</span
    >
    <span class="cle"
      ><svg width="14" height="14" aria-hidden="true"
        ><path d="M7 1l6 6-6 6-6-6z" fill="var(--donnee-autre)" /></svg
      > tendanciel ADEME, centres internes compris</span
    >
  {/snippet}
  {#snippet trace(largeur: number)}
    {@const W = Math.max(280, largeur)}
    {@const etroit = W < 560}
    {@const M = { haut: 26, bas: 30, gauche: 30, droite: etroit ? 78 : 200 }}
    {@const H = etroit ? 320 : 380}
    {@const tous = [t.depart, ...t.rapide, ...t.lente, ...t.bp2023, ...t.ademe]}
    {@const x = scaleLinear()
      .domain([t.depart.annee - 0.6, Math.max(...tous.map((p) => p.annee)) + 0.4])
      .range([M.gauche, W - M.droite])}
    {@const y = scaleLinear()
      .domain([0, Math.max(...tous.map((p) => p.max))])
      .nice()
      .range([H - M.bas, M.haut])}
    {@const annees = [...new Set(tous.map((p) => p.annee))].sort((a, b) => a - b)}
    {@const chemin = (pts: PointTrajectoire[]) =>
      [t.depart, ...pts]
        .map((p, i) => `${i ? 'L' : 'M'}${x(p.annee)},${y(i ? p.min : milieu(p))}`)
        .join('')}
    {@const derniere = (pts: PointTrajectoire[]) => pts[pts.length - 1]}
    {@const fins = ecarter(
      [
        {
          cle: 'ademe',
          y: y(derniere(t.ademe).max),
          nom: etroit ? 'ADEME' : 'ADEME, tendanciel',
          valeur: derniere(t.ademe).texte
        },
        {
          cle: 'rapide',
          y: y(derniere(t.rapide).max),
          nom: etroit ? 'Rapide' : 'Décarbonation rapide',
          valeur: derniere(t.rapide).texte
        },
        {
          cle: 'bp2023',
          y: y(milieu(derniere(t.bp2023))),
          nom: etroit ? 'BP2023' : 'BP2023, fourchette',
          valeur: derniere(t.bp2023).texte
        },
        {
          cle: 'lente',
          y: y(derniere(t.lente).max),
          nom: etroit ? 'Lente' : 'Décarbonation lente',
          valeur: derniere(t.lente).texte
        }
      ],
      etroit ? 30 : 17,
      M.haut
    )}
    {@const xFin = x(annees[annees.length - 1]) + 16}
    <svg
      width={W}
      height={H}
      viewBox="0 0 {W} {H}"
      role="group"
      aria-label="Trajectoires de consommation des data centers, 2024 à 2035"
    >
      {#each y.ticks(4) as v (v)}
        <line class="grille" x1={M.gauche} x2={W - M.droite + 8} y1={y(v)} y2={y(v)} />
        <text class="graduation" x={M.gauche - 6} y={y(v) + 4} text-anchor="end">{v}</text>
      {/each}
      <text class="graduation unite" x={M.gauche - 6} y={M.haut - 12} text-anchor="end">TWh</text>
      {#each annees as a (a)}
        <text class="graduation" x={x(a)} y={H - 8} text-anchor="middle">{a}</text>
      {/each}
      <line class="base" x1={M.gauche} x2={W - M.droite + 8} y1={y(0)} y2={y(0)} />

      <!-- Mention du périmètre élargi, directement sur le graphique (zone vide en haut à gauche). -->
      <g class="mention" transform="translate({M.gauche + 10},{M.haut + 4})">
        <path d="M0 2h8M4 2v14M0 16h8" stroke="var(--donnee-autre)" stroke-width="2" fill="none" />
        <text x="16" y="11"
          ><tspan class="fort">Périmètre élargi</tspan>{etroit
            ? ''
            : ' : centres internes compris'}</text
        >
        {#if etroit}<text x="16" y="28">centres internes compris</text>{/if}
        <text x="16" y={etroit ? 45 : 28}>(BP2023, ADEME) : non comparable</text>
        <text x="16" y={etroit ? 62 : 45}>aux trajectoires des sites dédiés</text>
      </g>

      {#if annee !== null}
        <line class="repere" x1={x(annee)} x2={x(annee)} y1={M.haut} y2={y(0)} />
      {/if}

      <!-- Périmètre élargi : fourchettes BP2023 (en I) et tendanciel ADEME (losange), décalés. -->
      {#each t.bp2023 as p (p.id)}
        {@const cx = x(p.annee) + DECALAGE}
        <path
          class="autre"
          d="M{cx - 5},{y(p.max)}h10M{cx},{y(p.max)}V{y(p.min)}M{cx - 5},{y(p.min)}h10"
        />
      {/each}
      {#each t.ademe as p (p.id)}
        {@const cx = x(p.annee) + DECALAGE}
        {@const cy = y(p.max)}
        <path class="losange" d="M{cx},{cy - 6}l6,6l-6,6l-6,-6z" />
      {/each}

      <!-- Sites dédiés : intervalle 2024 et trajectoires du BP2025. -->
      <path class="ligne faible" d={chemin(t.lente)} />
      <path class="ligne forte" d={chemin(t.rapide)} />
      <rect
        x={x(t.depart.annee) - 4}
        y={y(t.depart.max)}
        width="8"
        height={Math.max(8, y(t.depart.min) - y(t.depart.max))}
        rx="4"
        fill="var(--encre-2)"
      />
      <text class="etiquette" x={x(t.depart.annee) + 10} y={y(t.depart.min) + 16}
        >{t.depart.texte}</text
      >
      {#each t.lente as p (p.id)}
        <circle class="point faible" cx={x(p.annee)} cy={y(p.min)} r="4.5" />
      {/each}
      {#each t.rapide as p (p.id)}
        <circle class="point forte" cx={x(p.annee)} cy={y(p.min)} r="4.5" />
      {/each}

      <!-- Étiquettes de fin, écartées pour ne pas se chevaucher. -->
      {#each fins as f (f.cle)}
        {#if etroit}
          <text class="etiquette nom" x={xFin} y={f.y - 2}>{f.nom}</text>
          <text class="etiquette" x={xFin} y={f.y + 12}>{f.valeur}</text>
        {:else}
          <text class="etiquette" x={xFin} y={f.y + 4}
            ><tspan class="nom">{f.nom}</tspan>{' · '}{f.valeur}</text
          >
        {/if}
      {/each}

      <!-- Couche de survol : une colonne par année, au pointeur comme au clavier. -->
      {#each annees as a, i (a)}
        {@const g = i === 0 ? M.gauche : (x(annees[i - 1]) + x(a)) / 2}
        {@const d = i === annees.length - 1 ? W - M.droite : (x(a) + x(annees[i + 1])) / 2}
        <!-- svelte-ignore a11y_no_noninteractive_tabindex (marque focalisable : l'infobulle s'affiche au clavier comme au survol) -->
        <rect
          class="colonne"
          x={g}
          y={M.haut}
          width={d - g}
          height={y(0) - M.haut}
          tabindex="0"
          role="img"
          aria-label="{a} : {lignesAnnee(a)
            .map((l) => `${l.libelle}, ${l.valeur}`)
            .join(' ; ')}"
          onpointerenter={() => (annee = a)}
          onpointerleave={() => (annee = null)}
          onfocus={() => (annee = a)}
          onblur={() => (annee = null)}
        />
      {/each}
    </svg>
    {#if annee !== null}
      <Infobulle
        x={x(annee)}
        y={M.haut + 4}
        largeur={W}
        titre={String(annee)}
        lignes={lignesAnnee(annee)}
      />
    {/if}
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
  }
  .grille {
    stroke: var(--trait);
    stroke-width: 1;
  }
  .base {
    stroke: var(--encre-2);
    stroke-width: 1;
  }
  .graduation {
    fill: var(--encre-2);
    font-size: 13px;
    font-variant-numeric: tabular-nums;
  }
  .unite {
    font-weight: 600;
  }
  .ligne {
    fill: none;
    stroke-width: 2;
    stroke-linejoin: round;
    stroke-linecap: round;
  }
  .ligne.forte {
    stroke: var(--donnee);
  }
  .ligne.faible {
    stroke: var(--donnee-faible);
  }
  .point {
    stroke: var(--papier);
    stroke-width: 2;
  }
  .point.forte {
    fill: var(--donnee);
  }
  .point.faible {
    fill: var(--donnee-faible);
  }
  .autre {
    stroke: var(--donnee-autre);
    stroke-width: 2;
    fill: none;
  }
  .losange {
    fill: var(--donnee-autre);
    stroke: var(--papier);
    stroke-width: 2;
  }
  .etiquette {
    fill: var(--encre);
    font-size: 14px;
    font-weight: 600;
  }
  .etiquette .nom,
  .etiquette.nom {
    fill: var(--encre-2);
    font-weight: 400;
  }
  .mention text {
    fill: var(--encre-2);
    font-size: 13.5px;
    paint-order: stroke;
    stroke: var(--papier);
    stroke-width: 4px;
    stroke-linejoin: round;
  }
  .mention .fort {
    fill: var(--encre);
    font-weight: 600;
  }
  .repere {
    stroke: var(--encre-2);
    stroke-width: 1;
  }
  .colonne {
    fill: transparent;
    outline: none;
  }
  .colonne:focus-visible {
    stroke: var(--encre);
    stroke-width: 1.5;
  }
</style>
