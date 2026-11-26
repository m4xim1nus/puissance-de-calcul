<script lang="ts">
  // Making-of : journal compact, décisions et erreurs en fiches filtrables. Le contenu vient des
  // fichiers Markdown du dépôt (analysés au prérendu, $lib/server/makingof.ts) ; sans JavaScript,
  // tout est lisible, seuls les filtres manquent.
  import FiltreFiches from '$lib/FiltreFiches.svelte';
  import { formaterDate } from '$lib/format';
  import type { Arbitre, Reperage } from '$lib/server/makingof';

  let { data } = $props();

  const DEPOT = 'https://github.com/m4xim1nus/puissance-de-calcul/blob/main/';
  const courbe = (t: string) => t.replace(/'/g, '’');
  const capitale = (t: string) => t.charAt(0).toUpperCase() + t.slice(1);

  /* ---------- Décisions ---------- */
  const decisions = $derived(data.decisions.entrees);
  let arbitre = $state<Arbitre | null>(null);
  const optionsArbitres = $derived(
    (["l'auteur", 'Claude'] as Arbitre[]).map((a) => ({
      valeur: a,
      libelle: capitale(courbe(a)),
      nombre: decisions.filter((d) => d.qui.some((t) => t.qui === a)).length
    }))
  );
  const decisionVisible = (qui: { qui: Arbitre }[]) =>
    arbitre === null || qui.some((t) => t.qui === arbitre);
  const decisionsAffichees = $derived(decisions.filter((d) => decisionVisible(d.qui)).length);

  /* ---------- Erreurs ---------- */
  const erreurs = $derived(data.erreurs.entrees);
  let reperage = $state<Reperage | null>(null);
  const optionsReperages = $derived(
    (['Claude lui-même', 'un agent', 'un test', "l'auteur"] as Reperage[])
      .map((r) => ({
        valeur: r,
        libelle: capitale(courbe(r)),
        nombre: erreurs.filter((e) => e.reperage === r).length
      }))
      .filter((o) => o.nombre > 0)
  );
  const erreurVisible = (r: Reperage | null) => reperage === null || r === reperage;
  const erreursAffichees = $derived(erreurs.filter((e) => erreurVisible(e.reperage)).length);

  /* ---------- Journal ---------- */
  const sessions = $derived(data.journal.entrees);
  const sommaireDetail = (parties: string[]) =>
    courbe(parties.map((p) => p.toLowerCase()).join(', '));
</script>

<svelte:head>
  <title>Making-of · Puissance de calcul</title>
</svelte:head>

<h1>Making-of</h1>
<p class="colonne">
  Ce site est construit par Claude Code, sous la direction de l’auteur. Le making-of est tenu au fil
  de l’eau dans trois fichiers du dépôt : le journal des sessions, le registre des décisions et
  celui des erreurs de Claude. Cette page les met en forme sans changer leur texte&#8239;; seul le
  rappel du format, en tête du registre des erreurs, n’est pas affiché. Le brief de départ, publié
  tel quel, est replié dans la session 1 du journal.
</p>
<nav class="sommaire" aria-label="Sections du making-of">
  <a href="#journal">Journal</a>
  <a href="#decisions">Décisions</a>
  <a href="#erreurs">Erreurs de Claude</a>
</nav>

<!-- ============================== Journal ============================== -->
<section id="journal" aria-labelledby="journal-titre">
  <h2 id="journal-titre">Journal</h2>
  <div class="texte intro">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html data.journal.intro}
  </div>
  <p class="meta source">
    Source : <a href="{DEPOT}making-of/JOURNAL.md" rel="external">making-of/JOURNAL.md</a>
  </p>

  <ol class="sessions">
    {#each sessions as s (s.id)}
      <li class="session" id={s.id}>
        <article aria-labelledby="{s.id}-titre">
          <header class="tete-session">
            <h3 id="{s.id}-titre">
              Session {s.numero}
              <span class="objet"
                ><span class="sep">·</span>
                <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                {@html s.objet}</span
              >
            </h3>
            <p class="quand">
              {#if s.date}<time datetime={s.date}>{formaterDate(s.date)}</time>{/if}{#if s.horaire},
                {courbe(s.horaire)}{/if}{#if s.enCours}
                <span class="etiquette en-cours">session en cours</span>{/if}
            </p>
            {#if s.resume.length}
              <dl class="resume">
                {#each s.resume as r (r.cle)}
                  <div>
                    <dt>{r.cle}</dt>
                    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                    <dd>{@html r.html}</dd>
                  </div>
                {/each}
              </dl>
            {/if}
          </header>

          <div class="demande">
            <!-- eslint-disable-next-line svelte/no-at-html-tags -->
            {@html s.demande}
          </div>

          {#if s.brief}
            <details class="repli brief">
              <summary>Le brief de lancement, texte intégral publié tel quel</summary>
              <div class="contenu texte">
                <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                {@html s.brief}
              </div>
            </details>
          {/if}

          {#if s.parties.length}
            <details class="repli">
              <summary>Détail : {sommaireDetail(s.parties)}</summary>
              <div class="contenu texte">
                <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                {@html s.detail}
              </div>
            </details>
          {/if}
        </article>
      </li>
    {/each}
  </ol>
</section>

<!-- ============================== Décisions ============================== -->
<section id="decisions" aria-labelledby="decisions-titre">
  <h2 id="decisions-titre">Décisions</h2>
  <div class="texte intro">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html data.decisions.intro}
  </div>
  <p class="meta source">
    Source : <a href="{DEPOT}making-of/DECISIONS.md" rel="external">making-of/DECISIONS.md</a>
  </p>

  <FiltreFiches
    id="filtre-decisions"
    intitule="Tranchée par"
    options={optionsArbitres}
    total={decisions.length}
    bind:selection={arbitre}
    unites={['décision', 'décisions']}
    affichees={decisionsAffichees}
  />

  <ol class="fiches">
    {#each decisions as d (d.id)}
      <li class="fiche" id={d.id} hidden={!decisionVisible(d.qui)}>
        <p class="meta-fiche">
          <time datetime={d.date}>{d.date ? formaterDate(d.date) : '—'}</time>
          <span class="lecteur">, tranchée par</span>
          {#each d.qui as t (t.qui)}
            <span class="etiquette" class:auteur={t.qui === "l'auteur"}
              >{courbe(t.qui)}{#if t.role}<span class="role"> · {t.role}</span>{/if}</span
            >
          {:else}
            <span class="etiquette">{d.quiTexte}</span>
          {/each}
        </p>
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
        <p class="decision">{@html d.decision}</p>
        <p class="raisons">
          <span class="cle">Raisons</span>
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html d.raisons}
        </p>
      </li>
    {/each}
  </ol>
</section>

<!-- ============================== Erreurs ============================== -->
<section id="erreurs" aria-labelledby="erreurs-titre">
  <h2 id="erreurs-titre">Erreurs de Claude</h2>
  <div class="texte intro">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html data.erreurs.intro}
  </div>
  <p class="meta source">
    Source : <a href="{DEPOT}making-of/ERREURS.md" rel="external">making-of/ERREURS.md</a>
  </p>

  <FiltreFiches
    id="filtre-erreurs"
    intitule="Repérée par"
    options={optionsReperages}
    total={erreurs.length}
    bind:selection={reperage}
    unites={['erreur', 'erreurs']}
    affichees={erreursAffichees}
  />

  <ol class="fiches">
    {#each erreurs as e (e.id)}
      <li class="fiche erreur" id={e.id} hidden={!erreurVisible(e.reperage)}>
        <article aria-labelledby="{e.id}-titre">
          <p class="meta-fiche">
            <time datetime={e.date}>{e.date ? formaterDate(e.date) : '—'}</time>
            {#if e.reperage}
              <span class="etiquette">repérée par {courbe(e.reperage)}</span>
            {/if}
          </p>
          <h3 id="{e.id}-titre">
            <!-- eslint-disable-next-line svelte/no-at-html-tags -->
            {@html e.titre}
          </h3>
          {#if e.preambule}
            <div class="preambule">
              <!-- eslint-disable-next-line svelte/no-at-html-tags -->
              {@html e.preambule}
            </div>
          {/if}
          <dl class="rubriques">
            {#each e.champs as c (c.nom)}
              <dt>{c.nom}</dt>
              <dd>
                <!-- eslint-disable-next-line svelte/no-at-html-tags -->
                {@html c.html}
              </dd>
            {/each}
          </dl>
        </article>
      </li>
    {/each}
  </ol>
</section>

<style>
  .sommaire {
    display: flex;
    gap: 0.4rem 1.25rem;
    flex-wrap: wrap;
    font-family: var(--sans);
    font-size: 1.0625rem;
  }
  section {
    border-top: 1px solid var(--trait);
    margin-top: 2.5rem;
  }
  section > h2 {
    margin-top: 1.2em;
  }
  .intro :global(blockquote) {
    color: var(--encre);
    font-size: 0.95rem;
  }
  .source {
    margin: -0.4rem 0 1.4rem;
    font-size: 0.875rem;
  }
  [hidden] {
    display: none !important;
  }

  /* ---------- Listes de sessions et de fiches ---------- */
  .sessions,
  .fiches {
    list-style: none;
    padding: 0;
    margin: 0;
    max-width: calc(var(--mesure) + 2rem);
  }
  .sessions > li + li,
  .fiches > li + li {
    margin-top: 0;
  }
  .session,
  .fiche {
    border-top: 1px solid var(--trait);
    padding: 1.1rem 0 1.2rem;
  }

  /* ---------- Journal ---------- */
  .tete-session h3 {
    margin: 0;
    font-size: 1.375rem;
  }
  .objet {
    font-weight: 500;
  }
  .sep {
    color: var(--encre-2);
    font-weight: 500;
  }
  .quand {
    margin: 0.15rem 0 0.6rem;
    font-family: var(--sans);
    color: var(--encre-2);
  }
  .en-cours {
    margin-left: 0.3rem;
    font-family: var(--sans);
  }
  .resume {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 0.15rem 0.8rem;
    margin: 0 0 0.9rem;
    font-family: var(--sans);
    font-size: 0.95rem;
    line-height: 1.35;
  }
  .resume > div {
    display: contents;
  }
  .resume dt {
    font-weight: 600;
  }
  .resume dd {
    margin: 0;
  }
  .demande {
    font-size: 1rem;
  }
  .demande :global(> p:first-child) {
    margin-bottom: 0.4rem;
    font-family: var(--sans);
    font-size: 0.95rem;
    color: var(--encre-2);
  }
  .demande :global(> p:first-child strong) {
    color: var(--encre);
    font-weight: 600;
  }
  .demande :global(blockquote) {
    color: var(--encre);
    border-left-color: var(--encre-2);
    margin-bottom: 0.9rem;
  }
  .demande :global(blockquote li + li) {
    margin-top: 0.2em;
  }

  .repli {
    margin-top: 0.5rem;
  }
  .repli > summary {
    padding: 0.25rem 0;
    font-size: 1rem;
  }
  .repli[open] > summary {
    color: var(--encre);
    font-weight: 600;
  }
  .repli > .contenu {
    margin: 0.5rem 0 0.8rem;
    padding-left: 1rem;
    border-left: 2px solid var(--trait);
    font-size: 1rem;
  }
  .contenu :global(h4) {
    font-size: 1.25rem;
    margin-top: 1.2em;
  }
  .contenu :global(h5) {
    font-family: var(--sans);
    font-weight: 600;
    line-height: 1.2;
    font-size: 1.125rem;
    margin: 1.4em 0 0.4em;
  }
  .contenu :global(table) {
    font-size: 0.875rem;
  }

  /* ---------- Fiches (décisions, erreurs) ---------- */
  .meta-fiche {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.3rem 0.5rem;
    margin: 0 0 0.4rem;
    font-family: var(--sans);
    font-size: 0.95rem;
    color: var(--encre-2);
  }
  .etiquette {
    display: inline-block;
    padding: 0 0.45em;
    border: 1px solid var(--encre-2);
    border-radius: 3px;
    color: var(--encre);
    font-size: 0.9rem;
    line-height: 1.45;
  }
  .etiquette.auteur {
    background: var(--papier-2);
    border-color: var(--encre);
    font-weight: 600;
  }
  .role {
    font-weight: 400;
    color: var(--encre-2);
  }
  .decision {
    margin: 0 0 0.45rem;
    font-size: 1.0625rem;
  }
  .raisons {
    margin: 0;
    font-size: 0.95rem;
    color: var(--encre-2);
  }
  .cle {
    font-family: var(--sans);
    font-weight: 600;
    color: var(--encre);
    margin-right: 0.25rem;
  }

  .erreur h3 {
    margin: 0 0 0.6rem;
    font-size: 1.25rem;
  }
  .preambule {
    font-size: 1rem;
  }
  .rubriques {
    margin: 0;
    font-size: 1rem;
  }
  .rubriques dt {
    font-family: var(--sans);
    font-weight: 600;
    font-size: 0.95rem;
  }
  .rubriques dd {
    margin: 0 0 0.6rem;
  }
  .rubriques dd :global(p),
  .rubriques dd :global(ol),
  .rubriques dd :global(ul) {
    margin: 0 0 0.4rem;
  }
  .rubriques dd :global(:last-child) {
    margin-bottom: 0;
  }
</style>
