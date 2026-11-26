<script lang="ts">
  // Texte rendu au prérendu (HTML de rendreCorps), avec ses notes : marge de droite sur grand
  // écran, repliées sous le paragraphe sur téléphone. Copie de la mise en page des notes de
  // $lib/Enquete.svelte (non modifié : la page /quand est en relecture) ; à factoriser.
  import { onMount } from 'svelte';

  let { blocs }: { blocs: string[] } = $props();
  let racine: HTMLElement | undefined = $state();

  onMount(() => {
    if (!racine) return;
    const r = racine;
    const large = matchMedia('(min-width: 62rem)');
    const ajuster = () => {
      if (large.matches)
        r.querySelectorAll<HTMLDetailsElement>('details.notes').forEach((d) => (d.open = true));
    };
    ajuster();
    large.addEventListener('change', ajuster);
    const ouvrir = (e: MouseEvent) => {
      const lien = (e.target as Element).closest('a[data-note]');
      if (!lien) return;
      const note = r.querySelector(`#note-${lien.getAttribute('data-note')}`);
      const d = note?.closest<HTMLDetailsElement>('details');
      if (d && !d.open) d.open = true;
    };
    r.addEventListener('click', ouvrir);
    return () => {
      large.removeEventListener('change', ajuster);
      r.removeEventListener('click', ouvrir);
    };
  });
</script>

<div class="texte-annote" bind:this={racine}>
  {#each blocs as html, i (i)}
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html html}
  {/each}
</div>

<style>
  .texte-annote :global(:where(p, ul, ol, h2, h3, blockquote, .avec-notes)) {
    max-width: var(--mesure);
  }
  .texte-annote :global(h2) {
    margin-top: 2.2em;
  }
  .texte-annote :global(.chiffre) {
    font-family: var(--sans);
    font-weight: 500;
    font-size: 1.06em;
    line-height: 1;
    white-space: nowrap;
  }
  .texte-annote :global(.appel) {
    font-family: var(--sans);
    font-weight: 600;
    font-size: 0.72em;
    line-height: 0;
    vertical-align: super;
  }
  .texte-annote :global(.appel a) {
    text-decoration: none;
    padding: 0 0.15em;
    color: var(--encre-2);
  }
  .texte-annote :global(.appel a:hover) {
    color: var(--encre);
    text-decoration: underline;
  }
  .texte-annote :global(.avec-notes) {
    display: flex;
    flex-direction: column;
  }
  .texte-annote :global(.avec-notes > p) {
    margin-bottom: 0.4rem;
  }
  .texte-annote :global(.notes) {
    order: 2;
    margin: 0 0 1.1rem;
    font-family: var(--serif);
    font-size: 0.875rem;
    line-height: 1.45;
    color: var(--encre);
  }
  .texte-annote :global(.notes > summary) {
    font-size: 0.95rem;
    width: fit-content;
    padding: 0.1rem 0;
  }
  .texte-annote :global(.notes-corps) {
    border-left: 2px solid var(--trait);
    padding: 0.4rem 0 0.1rem 0.75rem;
    margin-top: 0.3rem;
  }
  @media (min-width: 62rem) {
    .texte-annote :global(.avec-notes) {
      display: block;
    }
    .texte-annote :global(.notes) {
      float: right;
      clear: right;
      width: var(--marge);
      margin: 0.25rem calc(-1 * (var(--marge) + var(--gouttiere))) 1.25rem 0;
      font-size: 0.8125rem;
    }
    .texte-annote :global(.notes-corps) {
      border-left: 0;
      padding: 0;
      margin: 0;
    }
    .texte-annote :global(h2) {
      clear: right;
    }
  }
  @supports selector(::details-content) {
    @media (min-width: 62rem) {
      .texte-annote :global(.notes > summary) {
        display: none;
      }
      .texte-annote :global(.notes::details-content) {
        content-visibility: visible;
        display: block;
      }
    }
  }
</style>
