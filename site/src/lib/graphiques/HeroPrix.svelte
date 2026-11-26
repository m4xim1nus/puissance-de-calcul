<script lang="ts">
  // Hero de l'accueil : une année du prix day-ahead France, heure par heure. Une ligne par jour,
  // une colonne par heure de Paris. Échelle divergente centrée sur 0 €/MWh, saturée à 200 €/MWh.
  // Dessin sur canvas (8 760 cases) ; survol, clavier et tableau de données pour l'accès.
  import { onMount, untrack } from 'svelte';
  import { FINE, INSECABLE, dateParis, formaterDate, formaterNombre } from '$lib/format';
  import {
    ECRETAGE,
    LIBELLES_CLASSES,
    NEGATIF_INFIME,
    PLANCHER,
    comparaisonReference,
    statistiques,
    SEUILS,
    classe,
    grille,
    type AnneePrix,
    type Case
  } from '$lib/heatmap';
  import Infobulle, { type LigneInfobulle } from './Infobulle.svelte';

  interface Props {
    annees: number[];
    initiale: AnneePrix;
    /** Heures négatives publiées (référentiel), par année, avec la note HTML de leur source. */
    references: Record<number, { valeur: number; note: string }>;
  }
  let { annees, initiale, references }: Props = $props();

  const cache = new Map<number, AnneePrix>();
  let donnees = $state(untrack(() => initiale));
  let annee = $state(untrack(() => initiale.annee));
  let chargement = $state(false);
  let erreur = $state('');

  const jours = $derived(grille(donnees));
  const reference = $derived(references[donnees.annee]);
  const stats = $derived(statistiques(jours));
  const comparaison = $derived(
    reference ? comparaisonReference(stats.negatives, reference.valeur) : null
  );
  const partEcretee = $derived(stats.avecPrix ? stats.ecretees / stats.avecPrix : 0);
  const heures = (n: number) => `${formaterNombre(n)}${INSECABLE}${n <= 1 ? 'heure' : 'heures'}`;
  const plancher = PLANCHER.toFixed(2).replace('.', ',').replace('-', '−');
  const precisions = $derived(
    [
      reference ? '' : 'calcul du site sur les données affichées, non recoupé',
      stats.sansPrix > 0 ? `${heures(stats.sansPrix)} sans prix publié dans l’année` : ''
    ].filter(Boolean)
  );

  async function choisir(a: number) {
    annee = a;
    erreur = '';
    const connue = a === initiale.annee ? initiale : cache.get(a);
    if (connue) {
      donnees = connue;
      return;
    }
    chargement = true;
    try {
      const r = await fetch(`/donnees/prix/${a}.json`);
      if (!r.ok) throw new Error(String(r.status));
      const d = (await r.json()) as AnneePrix;
      cache.set(a, d);
      if (annee === a) donnees = d;
    } catch {
      erreur = `Les prix de ${a} n’ont pas pu être chargés.`;
      annee = donnees.annee;
    } finally {
      chargement = false;
    }
  }

  /* ---------- Géométrie ---------- */
  const GAUCHE = 42;
  const HAUT = 22;
  const LIGNE = 2;
  let largeur = $state(0);
  const L = $derived(Math.max(280, largeur || 880));
  const colonne = $derived((L - GAUCHE) / 24);
  const hauteur = $derived(HAUT + jours.length * LIGNE + 4);
  const xh = (h: number) => Math.round(GAUCHE + h * colonne);

  /* ---------- Couleurs (jetons CSS, relus à chaque changement de thème) ---------- */
  const JETONS = [
    '--prix-n0',
    '--prix-n1',
    '--prix-n2',
    '--prix-p0',
    '--prix-p1',
    '--prix-p2',
    '--prix-p3',
    '--prix-p4'
  ];
  let theme = $state(0);
  let canvas: HTMLCanvasElement | undefined = $state();

  const MOIS = [
    'janv.',
    'févr.',
    'mars',
    'avr.',
    'mai',
    'juin',
    'juil.',
    'août',
    'sept.',
    'oct.',
    'nov.',
    'déc.'
  ];

  function dessiner() {
    if (!canvas) return;
    void theme;
    const css = getComputedStyle(canvas);
    const v = (n: string) => css.getPropertyValue(n).trim();
    const couleurs = JETONS.map(v);
    const absent = v('--prix-absent');
    const papier = v('--papier');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(L * dpr);
    canvas.height = Math.round(hauteur * dpr);
    const ctx = canvas.getContext('2d')!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, L, hauteur);

    // Repères : heures en haut, mois à gauche.
    ctx.fillStyle = v('--encre-2');
    ctx.font = `13px ${v('--sans')}`;
    ctx.textBaseline = 'alphabetic';
    for (const h of [0, 6, 12, 18]) ctx.fillText(`${h}${INSECABLE}h`, xh(h) + 1, 14);
    ctx.strokeStyle = v('--trait');
    jours.forEach((j, d) => {
      if (!j.date.endsWith('-01')) return;
      const y = HAUT + d * LIGNE;
      ctx.fillText(MOIS[Number(j.date.slice(5, 7)) - 1], 0, y + 11);
      ctx.beginPath();
      ctx.moveTo(GAUCHE - 6, y + 0.5);
      ctx.lineTo(GAUCHE - 1, y + 0.5);
      ctx.stroke();
    });

    // Cases.
    const teinte = (x: number | null) => (x === null ? absent : couleurs[classe(x)]);
    jours.forEach((j, d) => {
      const y = HAUT + d * LIGNE;
      j.cases.forEach((c, h) => {
        const x0 = xh(h);
        const x1 = xh(h + 1);
        if (c.type === 'prix') {
          ctx.fillStyle = teinte(c.v);
          ctx.fillRect(x0, y, x1 - x0, LIGNE);
        } else if (c.type === 'double') {
          const m = Math.round((x0 + x1) / 2);
          ctx.fillStyle = teinte(c.v[0]);
          ctx.fillRect(x0, y, m - x0, LIGNE);
          ctx.fillStyle = teinte(c.v[1]);
          ctx.fillRect(m, y, x1 - m, LIGNE);
        } else if (c.type === 'inexistante') {
          ctx.fillStyle = absent;
          ctx.fillRect(x0, y, x1 - x0, LIGNE);
        } else {
          ctx.fillStyle = papier;
          ctx.fillRect(x0, y, x1 - x0, LIGNE);
        }
      });
    });
  }

  $effect(() => {
    void jours;
    void L;
    void theme;
    dessiner();
  });

  onMount(() => {
    const mq = matchMedia('(prefers-color-scheme: dark)');
    const changer = () => theme++;
    mq.addEventListener('change', changer);
    // Les polices arrivent après le premier dessin : on redessine les repères.
    document.fonts?.ready.then(changer);
    return () => mq.removeEventListener('change', changer);
  });

  /* ---------- Survol et clavier ---------- */
  let actif = $state<{ d: number; h: number } | null>(null);

  function caseSous(ev: PointerEvent): { d: number; h: number } | null {
    const r = (ev.currentTarget as HTMLElement).getBoundingClientRect();
    const x = ((ev.clientX - r.left) / r.width) * L;
    const y = ((ev.clientY - r.top) / r.height) * hauteur;
    const h = Math.floor((x - GAUCHE) / colonne);
    const d = Math.floor((y - HAUT) / LIGNE);
    return h >= 0 && h < 24 && d >= 0 && d < jours.length ? { d, h } : null;
  }

  function touche(ev: KeyboardEvent) {
    const a = actif ?? { d: 0, h: 12 };
    const pas: Record<string, [number, number]> = {
      ArrowUp: [-1, 0],
      ArrowDown: [1, 0],
      ArrowLeft: [0, -1],
      ArrowRight: [0, 1],
      PageUp: [-7, 0],
      PageDown: [7, 0]
    };
    let suivant: { d: number; h: number } | null = null;
    if (ev.key in pas) {
      const [dd, dh] = pas[ev.key];
      suivant = {
        d: Math.min(jours.length - 1, Math.max(0, a.d + dd)),
        h: Math.min(23, Math.max(0, a.h + dh))
      };
    } else if (ev.key === 'Home') suivant = { d: 0, h: a.h };
    else if (ev.key === 'End') suivant = { d: jours.length - 1, h: a.h };
    else if (ev.key === 'Escape') actif = null;
    if (suivant) {
      ev.preventDefault();
      actif = suivant;
    }
  }

  const prixTexte = (v: number | null) =>
    v === null
      ? 'pas de prix publié'
      : v === NEGATIF_INFIME
        ? `négatif, moins de 0,0001${FINE}€/MWh en valeur absolue`
        : `${formaterNombre(v, Math.abs(v) < 1 ? 4 : 0)}${FINE}€/MWh`;
  const plage = (h: number) => `${h}${INSECABLE}h – ${(h + 1) % 24}${INSECABLE}h`;
  const jourTexte = (date: string) => {
    const j = new Date(`${date}T12:00Z`).toLocaleDateString('fr-FR', {
      weekday: 'long',
      timeZone: 'UTC'
    });
    return `${j} ${formaterDate(date)}`;
  };

  function lignes(c: Case, h: number): LigneInfobulle[] {
    if (c.type === 'prix')
      return [{ valeur: prixTexte(c.v), libelle: `${plage(h)}, heure de Paris` }];
    if (c.type === 'double')
      return [
        { valeur: prixTexte(c.v[0]), libelle: `${plage(h)}, heure d’été` },
        { valeur: prixTexte(c.v[1]), libelle: `${plage(h)}, heure d’hiver` }
      ];
    if (c.type === 'inexistante')
      return [
        { valeur: '—', libelle: `${plage(h)} n’existe pas ce jour (passage à l’heure d’été)` }
      ];
    return [{ valeur: '—', libelle: `${plage(h)} : pas encore publié` }];
  }

  const annonce = $derived.by(() => {
    if (!actif) return '';
    const j = jours[actif.d];
    if (!j) return '';
    return `${jourTexte(j.date)}, ${lignes(j.cases[actif.h], actif.h)
      .map((l) => `${l.libelle} : ${l.valeur}`)
      .join(' ; ')}`;
  });

  /* ---------- Textes ---------- */
  const derniereDate = $derived.by(() => {
    for (let d = jours.length - 1; d >= 0; d--)
      if (jours[d].cases.some((c) => c.type === 'prix' && c.v !== null)) return jours[d].date;
    return null;
  });
  const phraseNegatives = $derived(
    `En ${donnees.annee}${donnees.provisoire && derniereDate ? ` (jusqu’au ${formaterDate(derniereDate)})` : ''}, le prix day-ahead a été strictement négatif pendant `
  );
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
</script>

<section class="hero" aria-labelledby="hero-titre">
  <div class="tete">
    <h2 id="hero-titre">
      Prix de gros day-ahead en France, heure par heure, {donnees.annee}
    </h2>
    <p class="sous-titre">
      Prix day-ahead, en €/MWh. Une ligne par jour, du 1er janvier (en haut) au 31 décembre ; une
      colonne par heure, en heure de Paris.
      {#if donnees.provisoire && derniereDate}
        <strong>Année en cours, incomplète</strong> : prix publiés jusqu’au {formaterDate(
          derniereDate
        )}.
      {/if}
    </p>
  </div>

  <div class="annees" role="group" aria-label="Année affichée">
    {#each annees as a (a)}
      <button type="button" aria-pressed={a === annee} onclick={() => choisir(a)}
        >{a}{#if a === annees.at(-1) && a > initiale.annee}<span class="lecteur">
            (année en cours, incomplète)</span
          >*{/if}</button
      >
    {/each}
  </div>
  {#if annees.at(-1)! > initiale.annee}
    <p class="note-annees">* année en cours, incomplète.</p>
  {/if}
  {#if erreur}<p class="erreur" role="alert">{erreur}</p>{/if}

  <div class="legende" aria-label="Légende des couleurs">
    <div class="echelle">
      {#each JETONS as j, i (j)}
        <span
          class="classe"
          class:zero={i === 3}
          style:background="var({j})"
          title="{LIBELLES_CLASSES[i]} €/MWh"
        ></span>
      {/each}
    </div>
    <div class="graduations" aria-hidden="true">
      {#each SEUILS as s, i (s)}
        <span style:left="{((i + 1) / JETONS.length) * 100}%" class:zero={s === 0}
          >{formaterNombre(s)}</span
        >
      {/each}
    </div>
    <p class="legende-texte">
      <span class="fort">Prix strictement négatif</span> à gauche du zéro, positif à droite (€/MWh).
      Au-delà de {ECRETAGE}{FINE}€/MWh, la couleur sature : la valeur exacte reste dans l’infobulle.
    </p>
  </div>

  <div class="carte" class:charge={chargement} bind:clientWidth={largeur}>
    <!-- Zone « application » : les flèches parcourent les cases (rôle interactif pour l’ARIA). -->
    <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
    <div
      class="zone"
      style:width="{L}px"
      style:height="{hauteur}px"
      tabindex="0"
      role="application"
      aria-roledescription="carte de chaleur"
      aria-label="Prix day-ahead {donnees.annee}, un jour par ligne, une heure par colonne. Flèches pour parcourir les cases, Page précédente et Page suivante pour avancer d’une semaine ; tableau des données sous le calendrier."
      onpointermove={(ev) => (actif = caseSous(ev))}
      onpointerleave={() => (actif = null)}
      onkeydown={touche}
      onfocus={() => (actif ??= { d: 0, h: 12 })}
      onblur={() => (actif = null)}
    >
      <canvas bind:this={canvas} style:width="{L}px" style:height="{hauteur}px" aria-hidden="true"
      ></canvas>
    </div>
    <noscript
      ><p>Le calendrier demande JavaScript ; le décompte mensuel est ci-dessous.</p></noscript
    >
    {#if actif && jours[actif.d]}
      {@const c = jours[actif.d].cases[actif.h]}
      <div
        class="repere"
        style:left="{xh(actif.h) - 2}px"
        style:top="{HAUT + actif.d * LIGNE - 2}px"
        style:width="{xh(actif.h + 1) - xh(actif.h) + 4}px"
        style:height="{LIGNE + 4}px"
      ></div>
      <Infobulle
        x={xh(actif.h)}
        y={HAUT + actif.d * LIGNE}
        largeur={L}
        titre={jourTexte(jours[actif.d].date)}
        lignes={lignes(c, actif.h)}
      />
    {/if}
    <p class="lecteur" aria-live="polite">{annonce}</p>
  </div>

  {#if partEcretee > 0.1}
    <p class="ecretage">
      {formaterNombre(Math.round(partEcretee * 100))}{FINE}% des heures de {donnees.annee} sont au-delà
      de
      {ECRETAGE}{FINE}€/MWh : le calendrier les montre toutes dans la même couleur. Les valeurs
      exactes sont dans l’infobulle.
    </p>
  {/if}
  <div class="negatives">
    <p>
      {phraseNegatives}<strong class="nombre"
        >{heures(reference ? reference.valeur : stats.negatives)}</strong
      >{#if precisions.length}{' '}<span class="calcul">({precisions.join(`${FINE}; `)})</span
        >{/if}.
    </p>
    {#if stats.negatives > 0}
      <p class="planchers">
        {stats.planchers === 0 ? 'Aucune' : `Dont ${heures(stats.planchers)}`} à des prix compris entre
        {plancher}{FINE}€/MWh (inclus) et 0{FINE}€/MWh (exclu) : prix à peine négatifs, seuil choisi
        par le site, décompte non recoupé.
      </p>
    {/if}
    {#if reference}
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      <div class="source-ref">{@html reference.note}</div>
    {/if}
  </div>

  <ul class="speciales">
    {#if donnees.provisoire}
      <li>
        <span class="pastille vide"></span>
        Vide : jours pas encore publiés (année en cours).
      </li>
    {/if}
    <li>
      <span class="pastille" style:background="var(--prix-absent)"></span>
      Gris : pas de prix. Le jour du passage à l’heure d’été n’a que 23 heures : sa case 2 h n’existe
      pas.
    </li>
    <li>
      <span class="pastille double"
        ><span style:background="var(--prix-p2)"></span><span style:background="var(--prix-p1)"
        ></span></span
      >
      Le jour du passage à l’heure d’hiver a 25 heures : sa case 2 h est coupée en deux, à gauche 2 h
      en heure d’été, à droite 2 h en heure d’hiver.
    </li>
  </ul>

  <p class="source">
    Prix day-ahead France : Bundesnetzagentur / SMARD.de via energy-charts.info,
    <a href="https://creativecommons.org/licenses/by/4.0/" rel="external">CC BY 4.0</a>. Extraction
    du {formaterDate(dateParis(donnees.extrait_le))}. Depuis le 1er octobre 2025, le marché fixe un
    prix par quart d’heure ; le prix d’une heure affiché ici est la moyenne de ses quatre quarts
    d’heure, calculée par le site (convention de RTE). Le site arrondit les prix à l’euro, sauf
    entre −1 et 1{FINE}€/MWh (quatre décimales, comme la source).
  </p>

  <details class="donnees">
    <summary>Tableau des données : heures à prix négatif par mois, {donnees.annee}</summary>
    <table>
      <thead>
        <tr><th scope="col">Mois</th><th scope="col">Heures à prix strictement négatif</th></tr>
      </thead>
      <tbody>
        {#each stats.parMois as n, m (m)}
          <tr><th scope="row">{NOMS_MOIS[m]}</th><td class="nombre">{n}</td></tr>
        {/each}
        <tr class="total">
          <th scope="row">Année</th><td class="nombre">{stats.negatives}</td>
        </tr>
      </tbody>
    </table>
    <p class="table-note">
      Décompte du site sur les prix affichés{#if comparaison}, {comparaison.texte}{/if}.
    </p>
  </details>
</section>

<style>
  .hero {
    margin: 1.5rem 0 3rem;
    font-family: var(--sans);
  }
  .tete h2 {
    margin: 0 0 0.25rem;
    font-size: 1.45rem;
  }
  .sous-titre {
    margin: 0 0 0.9rem;
    color: var(--encre-2);
    max-width: 46rem;
    line-height: 1.4;
  }
  .sous-titre strong {
    color: var(--encre);
    font-weight: 600;
  }
  .annees {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    margin-bottom: 0.4rem;
  }
  .annees button {
    font: inherit;
    font-size: 0.95rem;
    font-variant-numeric: tabular-nums;
    padding: 0.2rem 0.55rem;
    border: 1px solid var(--trait);
    border-radius: 3px;
    background: transparent;
    color: var(--encre);
    cursor: pointer;
    min-height: 2rem;
  }
  .annees button:hover {
    border-color: var(--encre-2);
  }
  .annees button[aria-pressed='true'] {
    background: var(--encre);
    border-color: var(--encre);
    color: var(--papier);
    font-weight: 600;
  }
  .note-annees,
  .erreur {
    margin: 0 0 0.6rem;
    font-size: 0.875rem;
    color: var(--encre-2);
  }
  .legende {
    margin: 0.8rem 0 0.9rem;
    max-width: 34rem;
  }
  .echelle {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 2px;
    height: 14px;
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
  .legende-texte,
  .speciales {
    font-size: 0.875rem;
    line-height: 1.35;
    color: var(--encre-2);
    margin: 0.35rem 0 0;
  }
  .fort {
    color: var(--encre);
    font-weight: 600;
  }
  .speciales {
    list-style: none;
    padding: 0;
    margin-top: 0.6rem;
    max-width: 40rem;
  }
  .speciales li {
    display: flex;
    gap: 0.45rem;
    align-items: baseline;
  }
  .pastille {
    flex: none;
    display: inline-flex;
    width: 22px;
    height: 10px;
    border-radius: 2px;
    gap: 1px;
  }
  .pastille.vide {
    border: 1px solid var(--trait);
  }
  .pastille.double span {
    flex: 1;
  }
  .carte {
    position: relative;
    width: 100%;
    transition: opacity 0.15s;
  }
  .carte.charge {
    opacity: 0.45;
  }
  canvas {
    display: block;
    max-width: 100%;
    touch-action: pan-y;
  }
  .zone {
    max-width: 100%;
  }
  .zone:focus-visible {
    outline: 2px solid var(--encre);
    outline-offset: 3px;
  }
  .repere {
    position: absolute;
    border: 2px solid var(--encre);
    box-shadow: 0 0 0 1px var(--papier);
    pointer-events: none;
  }
  .negatives {
    margin-top: 1.2rem;
  }
  .negatives p {
    margin: 0;
    font-family: var(--serif);
    max-width: var(--mesure);
  }
  .negatives .nombre {
    font-family: var(--sans);
    font-weight: 600;
    white-space: nowrap;
  }
  .calcul {
    color: var(--encre-2);
    font-size: 0.95em;
  }
  .planchers {
    margin: 0.2rem 0 0;
    font-family: var(--serif);
    font-size: 0.95rem;
    color: var(--encre-2);
    max-width: var(--mesure);
  }
  .ecretage {
    margin: 0.6rem 0 0;
    font-size: 0.95rem;
    font-weight: 500;
    max-width: 40rem;
  }
  .source-ref {
    margin-top: 0.3rem;
    font-family: var(--serif);
    font-size: 0.875rem;
    max-width: var(--mesure);
  }
  .source {
    margin: 0.9rem 0 0;
    font-size: 0.875rem;
    color: var(--encre-2);
    max-width: 46rem;
    line-height: 1.4;
  }
  .donnees {
    margin-top: 0.6rem;
  }
  .donnees table {
    display: table;
    margin-top: 0.5rem;
  }
  .donnees th[scope='row'] {
    font-weight: 500;
    border-bottom-color: var(--trait);
  }
  td.nombre {
    text-align: right;
  }
  .total th,
  .total td {
    font-weight: 600;
  }
  .table-note {
    font-size: 0.85rem;
    color: var(--encre-2);
  }
  @media (prefers-reduced-motion: reduce) {
    .carte {
      transition: none;
    }
  }
</style>
