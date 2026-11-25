<script lang="ts">
  // Mise en page d'une enquête : colonne de lecture et marge de notes sur grand écran ; sur
  // téléphone, les notes sont repliées sous leur paragraphe. Les graphiques prennent la largeur
  // texte + marge.
  import { onMount } from 'svelte';
  import type { Chiffres } from '$lib/chiffres';
  import { formaterDate } from '$lib/format';
  import { GRAPHIQUES } from '$lib/graphiques/registre';
  import type { Enquete } from '$lib/enquete';

  let { enquete, chiffres }: { enquete: Enquete; chiffres: Chiffres } = $props();

  let article: HTMLElement | undefined = $state();

  onMount(() => {
    if (!article) return;
    const racine = article;
    // Sur grand écran, les notes sont toujours dépliées (au cas où le navigateur ignorerait
    // ::details-content) ; sur téléphone, elles restent repliées jusqu'au clic.
    const large = matchMedia('(min-width: 62rem)');
    const ajuster = () => {
      if (large.matches)
        racine
          .querySelectorAll<HTMLDetailsElement>('details.notes')
          .forEach((d) => (d.open = true));
    };
    ajuster();
    large.addEventListener('change', ajuster);
    // Un appel de note ouvre la note correspondante si elle est repliée.
    const ouvrir = (e: MouseEvent) => {
      const lien = (e.target as Element).closest('a[data-note]');
      if (!lien) return;
      const note = racine.querySelector(`#note-${lien.getAttribute('data-note')}`);
      const d = note?.closest<HTMLDetailsElement>('details');
      if (d && !d.open) d.open = true;
    };
    racine.addEventListener('click', ouvrir);
    return () => {
      large.removeEventListener('change', ajuster);
      racine.removeEventListener('click', ouvrir);
    };
  });
</script>

<article class="enquete" bind:this={article}>
  <header class="tete">
    <p class="rubrique">Enquête</p>
    <h1>{enquete.meta.titre}</h1>
    <p class="chapeau">{enquete.meta.question}</p>
    <p class="meta">Mis à jour le {formaterDate(enquete.meta.mise_a_jour)}</p>
  </header>
  {#each enquete.blocs as b, i (i)}
    {#if b.type === 'html'}
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html b.html}
    {:else}
      {@const Graphique = GRAPHIQUES[b.nom]}
      <Graphique {chiffres} />
    {/if}
  {/each}
</article>

<style>
  .enquete {
    max-width: var(--large);
  }
  .tete {
    margin-bottom: 2rem;
  }
  .rubrique {
    margin: 1.5rem 0 0;
    font-family: var(--sans);
    font-weight: 500;
    color: var(--encre-2);
  }
  .tete h1 {
    margin-top: 0.1em;
  }
  .tete .meta {
    margin: 0;
  }

  /* Texte de l'enquête (HTML rendu au prérendu). */
  .enquete :global(:where(p, ul, ol, h2, h3, blockquote, .avec-notes)) {
    max-width: var(--mesure);
  }
  .enquete :global(h2) {
    margin-top: 2.2em;
  }
  .enquete :global(.chiffre) {
    font-family: var(--sans);
    font-weight: 500;
    font-size: 1.06em;
    line-height: 1;
    white-space: nowrap;
  }
  .enquete :global(.appel) {
    font-family: var(--sans);
    font-weight: 600;
    font-size: 0.72em;
    line-height: 0;
    vertical-align: super;
  }
  .enquete :global(.appel a) {
    text-decoration: none;
    padding: 0 0.15em;
    color: var(--encre-2);
  }
  .enquete :global(.appel a:hover) {
    color: var(--encre);
    text-decoration: underline;
  }

  /* Notes : bloc replié sous le paragraphe (téléphone), marge de droite (grand écran). */
  .enquete :global(.avec-notes) {
    display: flex;
    flex-direction: column;
  }
  .enquete :global(.avec-notes > p) {
    margin-bottom: 0.4rem;
  }
  .enquete :global(li .avec-notes .contenu) {
    margin-bottom: 0.3rem;
  }
  .enquete :global(.notes) {
    order: 2;
    margin: 0 0 1.1rem;
    font-family: var(--serif);
    font-size: 0.875rem;
    line-height: 1.45;
    color: var(--encre);
  }
  .enquete :global(.notes > summary) {
    font-size: 0.95rem;
    width: fit-content;
    padding: 0.1rem 0;
  }
  .enquete :global(.notes-corps) {
    border-left: 2px solid var(--trait);
    padding: 0.4rem 0 0.1rem 0.75rem;
    margin-top: 0.3rem;
  }
  .enquete :global(.note + .note) {
    margin-top: 0.7rem;
    padding-top: 0.7rem;
    border-top: 1px solid var(--trait);
  }
  .enquete :global(.note p) {
    margin: 0 0 0.3rem;
    max-width: none;
  }
  .enquete :global(.note-num) {
    font-family: var(--sans);
    font-weight: 600;
    margin-right: 0.15rem;
  }
  .enquete :global(.note-citation) {
    font-style: italic;
  }
  .enquete :global(.note-cle) {
    font-family: var(--sans);
    font-weight: 600;
    color: var(--encre-2);
    margin-right: 0.2rem;
  }
  .enquete :global(.note-secondaire) {
    color: var(--encre-2);
  }
  .enquete :global(.note-plus > summary) {
    font-size: 0.92em;
    width: fit-content;
  }
  .enquete :global(.note-plus[open] > summary) {
    margin-bottom: 0.25rem;
  }
  .enquete :global(.note-plus p) {
    margin: 0 0 0.25rem;
  }
  .enquete :global(.note-cote) {
    font-family: var(--sans);
    font-size: 0.95em;
  }
  .enquete :global(.cote) {
    display: inline-block;
    min-width: 1.35em;
    text-align: center;
    font-weight: 600;
    border: 1.5px solid var(--encre);
    border-radius: 3px;
    line-height: 1.25;
    margin-right: 0.15rem;
  }

  @media (min-width: 62rem) {
    .enquete :global(.avec-notes) {
      display: block;
    }
    .enquete :global(.notes) {
      float: right;
      clear: right;
      width: var(--marge);
      margin: 0.25rem calc(-1 * (var(--marge) + var(--gouttiere))) 1.25rem 0;
      font-size: 0.8125rem;
    }
    .enquete :global(.notes-corps) {
      border-left: 0;
      padding: 0;
      margin: 0;
    }
    .enquete :global(h2) {
      clear: right;
    }
  }
  @supports selector(::details-content) {
    @media (min-width: 62rem) {
      .enquete :global(.notes > summary) {
        display: none;
      }
      .enquete :global(.notes::details-content) {
        content-visibility: visible;
        display: block;
      }
    }
  }
</style>
