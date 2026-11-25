<script lang="ts">
  // Polices auto-hébergées (paquets @fontsource épinglés, servies depuis le site : aucun CDN).
  import '@fontsource/barlow-semi-condensed/latin-400.css';
  import '@fontsource/barlow-semi-condensed/latin-500.css';
  import '@fontsource/barlow-semi-condensed/latin-600.css';
  import '@fontsource-variable/source-serif-4/opsz.css';
  import '@fontsource-variable/source-serif-4/opsz-italic.css';
  import '../app.css';
  import { page } from '$app/state';

  let { children } = $props();

  const LIENS = [
    { href: '/', libelle: 'Accueil' },
    { href: '/combien', libelle: 'Combien' },
    { href: '/methode', libelle: 'Méthode' },
    { href: '/making-of', libelle: 'Making-of' },
    { href: '/a-toi', libelle: 'À toi' }
  ];
  const actif = (href: string) =>
    href === '/' ? page.url.pathname === '/' : page.url.pathname.startsWith(href);
</script>

<svelte:head>
  <meta name="theme-color" content="#edf1f2" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#101a26" media="(prefers-color-scheme: dark)" />
</svelte:head>

<a class="evitement" href="#contenu">Aller au contenu</a>

<header class="entete">
  <div class="cadre">
    <a class="marque" href="/">Puissance de calcul</a>
    <nav aria-label="Navigation principale">
      {#each LIENS as l (l.href)}
        <a href={l.href} aria-current={actif(l.href) ? 'page' : undefined}>{l.libelle}</a>
      {/each}
    </nav>
  </div>
</header>

<main id="contenu" class="cadre">
  {@render children()}
</main>

<footer class="pied">
  <div class="cadre">
    <p>
      Site indépendant, données ouvertes et publications officielles. Aucun traceur, aucune
      ressource tierce.
    </p>
  </div>
</footer>

<style>
  .cadre {
    max-width: calc(var(--large) + 2 * var(--bord));
    margin: 0 auto;
    padding-left: var(--bord);
    padding-right: var(--bord);
  }
  .evitement {
    position: absolute;
    left: -100vw;
    font-family: var(--sans);
  }
  .evitement:focus {
    left: var(--bord);
    top: 0.5rem;
    z-index: 10;
    padding: 0.2em 0.5em;
  }
  .entete {
    border-bottom: 1px solid var(--trait);
  }
  .entete .cadre {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.25rem 2rem;
    padding-top: 1rem;
    padding-bottom: 0.75rem;
  }
  .marque {
    font-family: var(--sans);
    font-size: 1.3rem;
    font-weight: 600;
    text-decoration: none;
  }
  nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 1.25rem;
    font-family: var(--sans);
    font-size: 1.0625rem;
  }
  nav a {
    color: var(--encre-2);
    text-decoration: none;
    padding: 0.15em 0;
  }
  nav a:hover {
    color: var(--encre);
  }
  nav a[aria-current='page'] {
    color: var(--encre);
    font-weight: 600;
    box-shadow: inset 0 -2px 0 var(--encre);
  }
  main {
    padding-top: 1rem;
    padding-bottom: 4rem;
    min-height: 60vh;
  }
  .pied {
    border-top: 1px solid var(--trait);
    color: var(--encre-2);
    font-family: var(--sans);
    font-size: 0.95rem;
  }
  .pied .cadre {
    padding-top: 1rem;
    padding-bottom: 2rem;
  }
  .pied p {
    margin: 0;
    max-width: var(--mesure);
  }
</style>
