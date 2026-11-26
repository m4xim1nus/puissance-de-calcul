<script lang="ts">
  // Un calendrier jour × heure de Paris de la charge résiduelle, sur canvas : même grammaire que le
  // calendrier des prix de l'accueil (une ligne par jour, une colonne par heure, échelle divergente
  // centrée sur zéro), en plus petit. Survol, clavier, annonce pour les lecteurs d'écran.
  import { onMount } from 'svelte';
  import { INSECABLE, formaterDate } from '$lib/format';
  import { JETONS_RN, classeRn, gw, type MatriceRn } from '$lib/quand';
  import Infobulle from './Infobulle.svelte';

  let { matrice }: { matrice: MatriceRn } = $props();

  const GAUCHE = 34;
  const HAUT = 18;
  const LIGNE = 1;
  let largeur = $state(0);
  const L = $derived(Math.max(150, largeur || 400));
  const colonne = $derived((L - GAUCHE) / 24);
  const hauteur = $derived(HAUT + matrice.jours.length * LIGNE + 2);
  const xh = (h: number) => Math.round(GAUCHE + h * colonne);

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

  let theme = $state(0);
  let canvas: HTMLCanvasElement | undefined = $state();

  function dessiner() {
    if (!canvas) return;
    void theme;
    const css = getComputedStyle(canvas);
    const v = (n: string) => css.getPropertyValue(n).trim();
    const couleurs = JETONS_RN.map(v);
    const absent = v('--prix-absent');
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(L * dpr);
    canvas.height = Math.round(hauteur * dpr);
    const ctx = canvas.getContext('2d')!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, L, hauteur);
    ctx.fillStyle = v('--encre-2');
    ctx.font = `12px ${v('--sans')}`;
    for (const h of [0, 6, 12, 18]) ctx.fillText(`${h}${INSECABLE}h`, xh(h) + 1, 12);
    matrice.jours.forEach((j, d) => {
      if (j.endsWith('-01')) ctx.fillText(MOIS[Number(j.slice(5, 7)) - 1], 0, HAUT + d * LIGNE + 9);
    });
    matrice.valeurs.forEach((ligne, d) => {
      const y = HAUT + d * LIGNE;
      ligne.forEach((val, h) => {
        ctx.fillStyle = val === null ? absent : couleurs[classeRn(val)];
        ctx.fillRect(xh(h), y, xh(h + 1) - xh(h), LIGNE);
      });
    });
  }

  $effect(() => {
    void matrice;
    void L;
    void theme;
    dessiner();
  });

  onMount(() => {
    const mq = matchMedia('(prefers-color-scheme: dark)');
    const changer = () => theme++;
    mq.addEventListener('change', changer);
    document.fonts?.ready.then(changer);
    return () => mq.removeEventListener('change', changer);
  });

  let actif = $state<{ d: number; h: number } | null>(null);

  function caseSous(ev: PointerEvent): { d: number; h: number } | null {
    const r = (ev.currentTarget as HTMLElement).getBoundingClientRect();
    const x = ((ev.clientX - r.left) / r.width) * L;
    const y = ((ev.clientY - r.top) / r.height) * hauteur;
    const h = Math.floor((x - GAUCHE) / colonne);
    const d = Math.floor((y - HAUT) / LIGNE);
    return h >= 0 && h < 24 && d >= 0 && d < matrice.jours.length ? { d, h } : null;
  }

  function touche(ev: KeyboardEvent) {
    const a = actif ?? { d: 0, h: 8 };
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
        d: Math.min(matrice.jours.length - 1, Math.max(0, a.d + dd)),
        h: Math.min(23, Math.max(0, a.h + dh))
      };
    } else if (ev.key === 'Home') suivant = { d: 0, h: a.h };
    else if (ev.key === 'End') suivant = { d: matrice.jours.length - 1, h: a.h };
    else if (ev.key === 'Escape') actif = null;
    if (suivant) {
      ev.preventDefault();
      actif = suivant;
    }
  }

  const plage = (h: number) => `${h}${INSECABLE}h – ${(h + 1) % 24}${INSECABLE}h, heure de Paris`;
  const valeurTexte = (v: number | null) => (v === null ? 'pas de donnée' : gw(v));
  const annonce = $derived.by(() => {
    if (!actif) return '';
    const v = matrice.valeurs[actif.d][actif.h];
    return `${formaterDate(matrice.jours[actif.d])}, ${plage(actif.h)} : ${valeurTexte(v)}`;
  });
</script>

<div class="calendrier" bind:clientWidth={largeur}>
  <!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
  <div
    class="zone"
    style:width="{L}px"
    style:height="{hauteur}px"
    tabindex="0"
    role="application"
    aria-roledescription="carte de chaleur"
    aria-label="Charge résiduelle {matrice.annee}, un jour par ligne, une heure par colonne. Flèches pour parcourir les cases, Page précédente et Page suivante pour avancer d’une semaine ; statistiques mensuelles dans le tableau des données."
    onpointermove={(ev) => (actif = caseSous(ev))}
    onpointerleave={() => (actif = null)}
    onkeydown={touche}
    onfocus={() => (actif ??= { d: 0, h: 8 })}
    onblur={() => (actif = null)}
  >
    <canvas bind:this={canvas} style:width="{L}px" style:height="{hauteur}px" aria-hidden="true"
    ></canvas>
  </div>
  {#if actif}
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
      titre={formaterDate(matrice.jours[actif.d])}
      lignes={[{ valeur: valeurTexte(matrice.valeurs[actif.d][actif.h]), libelle: plage(actif.h) }]}
    />
  {/if}
  <p class="lecteur" aria-live="polite">{annonce}</p>
</div>

<style>
  .calendrier {
    position: relative;
    width: 100%;
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
</style>
