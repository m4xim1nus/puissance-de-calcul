<script lang="ts">
  // Encart « en préparation » : ce qui manque, pourquoi, ce qui viendra. Sert pour une enquête
  // pas encore écrite comme pour une donnée absente (jeton ENTSO-E, série non publiée…) : on dit
  // ce qui manque, on n'y substitue jamais une estimation silencieuse.
  interface Props {
    titre: string;
    manque: string;
    pourquoi: string;
    viendra: string;
    /** Niveau du titre de l'encart (défaut 3). */
    niveau?: 2 | 3 | 4;
  }
  let { titre, manque, pourquoi, viendra, niveau = 3 }: Props = $props();
</script>

<aside class="chantier" aria-label="{titre} : en préparation">
  <p class="etat">En préparation</p>
  <svelte:element this={`h${niveau}`} class="titre">{titre}</svelte:element>
  <dl>
    <dt>Ce qui manque</dt>
    <dd>{manque}</dd>
    <dt>Pourquoi</dt>
    <dd>{pourquoi}</dd>
    <dt>Ce qui viendra</dt>
    <dd>{viendra}</dd>
  </dl>
</aside>

<style>
  .chantier {
    border: 1px dashed var(--encre-2);
    border-radius: 4px;
    padding: 0.9rem 1rem 0.6rem;
    font-size: 0.95rem;
    line-height: 1.5;
  }
  .etat {
    margin: 0;
    font-family: var(--sans);
    font-weight: 500;
    color: var(--encre-2);
  }
  .titre {
    margin: 0.1rem 0 0.5rem;
    font-size: 1.25rem;
  }
  dl {
    margin: 0;
  }
  dt {
    font-family: var(--sans);
    font-weight: 600;
    font-size: 0.95rem;
  }
  dd {
    margin: 0 0 0.5rem;
  }
</style>
