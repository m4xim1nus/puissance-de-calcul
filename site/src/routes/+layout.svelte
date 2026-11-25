<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';

  let { children } = $props();

  const LIENS = [
    { href: '/', libelle: 'Accueil' },
    { href: '/making-of', libelle: 'Making-of' },
    { href: '/a-toi', libelle: 'À toi' }
  ];
  const actif = (href: string) =>
    href === '/' ? page.url.pathname === '/' : page.url.pathname.startsWith(href);
</script>

<svelte:head>
  <meta name="theme-color" content="#fbfbf9" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#161a1f" media="(prefers-color-scheme: dark)" />
</svelte:head>

<header class="entete">
  <a class="marque" href="/">Puissance de calcul</a>
  <nav aria-label="Navigation principale">
    {#each LIENS as l (l.href)}
      <a href={l.href} aria-current={actif(l.href) ? 'page' : undefined}>{l.libelle}</a>
    {/each}
  </nav>
</header>

<main>
  {@render children()}
</main>

<footer class="pied">
  <p>Site indépendant. Aucun traceur, aucune ressource tierce.</p>
</footer>

<style>
  .entete,
  main,
  .pied {
    max-width: var(--large);
    margin: 0 auto;
    padding-left: 16px;
    padding-right: 16px;
  }
  .entete {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: baseline;
    gap: 8px 32px;
    padding-top: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--filet);
  }
  .marque {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--encre);
    text-decoration: none;
  }
  nav {
    display: flex;
    gap: 20px;
  }
  nav a {
    color: var(--ardoise);
    text-decoration: none;
  }
  nav a:hover,
  nav a[aria-current='page'] {
    color: var(--encre);
  }
  nav a[aria-current='page'] {
    text-decoration: underline;
    text-underline-offset: 4px;
  }
  main {
    padding-top: 16px;
    padding-bottom: 48px;
    min-height: 60vh;
  }
  .pied {
    border-top: 1px solid var(--filet);
    padding-top: 16px;
    padding-bottom: 32px;
    color: var(--ardoise);
    font-size: 0.9rem;
  }
</style>
