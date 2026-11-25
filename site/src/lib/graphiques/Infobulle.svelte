<script lang="ts" module>
  export interface LigneInfobulle {
    valeur: string;
    libelle: string;
    cle?: 'forte' | 'faible' | 'autre';
  }
</script>

<script lang="ts">
  // Infobulle partagée : la valeur d'abord, le libellé ensuite. Elle complète les étiquettes et le
  // tableau de données, elle ne les remplace jamais.
  interface Props {
    x: number;
    y: number;
    largeur: number;
    titre?: string;
    lignes: LigneInfobulle[];
  }
  let { x, y, largeur, titre, lignes }: Props = $props();

  const LARGEUR_MAX = 260;
  const gauche = $derived(Math.max(0, Math.min(x - 20, largeur - LARGEUR_MAX)));
</script>

<div class="infobulle" style:left="{gauche}px" style:top="{y}px" role="presentation">
  {#if titre}<p class="titre">{titre}</p>{/if}
  {#each lignes as l, i (i)}
    <p class="ligne">
      {#if l.cle}<span class="cle cle-{l.cle}" aria-hidden="true"></span>{/if}
      <span class="valeur">{l.valeur}</span>
      <span class="libelle">{l.libelle}</span>
    </p>
  {/each}
</div>

<style>
  .infobulle {
    position: absolute;
    z-index: 2;
    max-width: 260px;
    transform: translateY(calc(-100% - 12px));
    padding: 0.45rem 0.6rem;
    background: var(--papier);
    border: 1px solid var(--trait);
    border-radius: 4px;
    box-shadow: 0 2px 8px color-mix(in srgb, var(--encre) 15%, transparent);
    font-family: var(--sans);
    font-size: 0.9rem;
    line-height: 1.3;
    pointer-events: none;
  }
  .titre {
    margin: 0 0 0.2rem;
    color: var(--encre-2);
  }
  .ligne {
    margin: 0;
  }
  .ligne + .ligne {
    margin-top: 0.2rem;
  }
  .valeur {
    font-weight: 600;
    color: var(--encre);
  }
  .libelle {
    color: var(--encre-2);
  }
  .cle {
    display: inline-block;
    width: 12px;
    height: 2px;
    margin-right: 0.3rem;
    vertical-align: middle;
  }
  .cle-forte {
    background: var(--donnee);
  }
  .cle-faible {
    background: var(--donnee-faible);
  }
  .cle-autre {
    background: var(--donnee-autre);
  }
</style>
