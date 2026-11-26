<script lang="ts">
  // « En bref » du making-of, en fiche recette (demande de l'auteur) : ingrédients, temps de
  // cuisson et de préparation, étapes (une par session), valeurs « nutritionnelles » (le modèle) et
  // ce que ça donne. Lecture d'un coup d'œil pour une lectrice à l'aise avec les chiffres mais pas
  // avec le développement. Données : making-of/en-bref.json (`pc bilan`, pipeline/pc/bilan.py,
  // définitions dans sa docstring) et making-of/actions-auteur.json (minutes estimées).
  import { FINE, INSECABLE, formaterDate, formaterNombre } from '$lib/format';
  import type { ActionsAuteur, AgregatBilan, EnBref } from '$lib/server/makingof';

  let {
    bilan,
    decisions,
    erreurs,
    actions,
    etapes
  }: {
    bilan: EnBref;
    decisions: { total: number; auteur: number; claude: number; partagees: number };
    erreurs: number;
    actions: ActionsAuteur;
    etapes: { numero: number; id: string; objet: string }[];
  } = $props();

  const MODELES = { opus: 'Opus', sonnet: 'Sonnet', haiku: 'Haiku', autre: 'autre' } as const;
  type Modele = keyof typeof MODELES;

  /** 335 → « 5 h 35 » ; 42 → « 42 min ». */
  function duree(min: number): string {
    if (min < 60) return `${min}${INSECABLE}min`;
    const h = Math.floor(min / 60);
    const m = min % 60;
    return `${h}${INSECABLE}h${INSECABLE}${String(m).padStart(2, '0')}`;
  }
  /** 2 378 349 → « 2,4 M » ; 70 083 → « 70 k ». */
  function jetons(n: number): string {
    if (n >= 1e6) return `${formaterNombre(n / 1e6, n >= 1e8 ? 0 : 1)}${FINE}M`;
    if (n >= 1e3) return `${formaterNombre(n / 1e3, 0)}${FINE}k`;
    return formaterNombre(n, 0);
  }
  type Champ = 'produits' | 'dont_reflexion' | 'lus_en_cache' | 'ecrits_en_cache' | 'entree';
  const somme = (a: AgregatBilan, champ: Champ) =>
    Object.values(a.jetons).reduce((s, j) => s + (j?.[champ] ?? 0), 0);
  const ventilation = (n: Partial<Record<Modele, number>>, f: (x: number) => string) =>
    (Object.keys(MODELES) as Modele[])
      .filter((m) => n[m])
      .map((m) => `${f(n[m]!)} ${MODELES[m]}`)
      .join(', ');
  const produitsParModele = (a: AgregatBilan) =>
    ventilation(
      Object.fromEntries(Object.entries(a.jetons).map(([m, j]) => [m, j?.produits ?? 0])),
      jetons
    );
  const nbAgents = (a: AgregatBilan) => Object.values(a.agents).reduce((s, n) => s + (n ?? 0), 0);
  const usd = (n: number) => `${formaterNombre(n, 0)}${FINE}$`;
  const pluriel = (n: number, un: string, plusieurs: string) => (n > 1 ? plusieurs : un);

  const t = $derived(bilan.total);
  const d = $derived(bilan.depot);
  const sessions = $derived(bilan.sessions);
  const etape = (n: number) => etapes.find((e) => e.numero === n);
  const actionsDe = (n: number) => actions.sessions[String(n)];
  // Minutes d'actions manuelles, estimées (voir le fichier) ; null tant qu'une session n'en a pas.
  const declarees = $derived.by(() => {
    const m = sessions.map((s) => actionsDe(s.numero)?.minutes ?? null);
    return m.every((x) => x !== null) ? m.reduce((a, b) => a + (b ?? 0), 0) : null;
  });
  // Une session sans relevé de coût n'est pas close (Claude Code écrit ce relevé à la clôture
  // d'une conversation) : jetons tirés des transcriptions seules ; appels, commandes, coût absents.
  const enCours = $derived(sessions.filter((s) => s.incomplet).map((s) => s.numero));
  const jour = (iso: string) => formaterDate(iso, true);
  const releve = $derived(
    `${formaterDate(bilan.releve.slice(0, 10))} à ${bilan.releve.slice(11, 13)}${INSECABLE}h${INSECABLE}${bilan.releve.slice(14, 16)}`
  );
  const lignesCode = $derived(d.lignes_python + d.lignes_site);
</script>

<section id="en-bref" aria-labelledby="en-bref-titre">
  <h2 id="en-bref-titre">En bref&#8239;: la recette</h2>
  <p class="colonne">
    Comment ce site est fait, présenté comme une recette de cuisine&#8239;: ce qu’il faut, combien
    de temps, qui fait quoi, et ce que ça coûte en calcul. Relevé du {releve}. Les durées et les
    jetons viennent des transcriptions de Claude Code, privées, dont seuls ces totaux sont
    publiés&#8239;; les volumes de texte et de code, du dépôt. Liseré jaune&#8239;: la part de
    l’auteur. Comment chaque chiffre est compté, et ce qu’il ne compte pas&#8239;: en bas de
    section.
  </p>

  <div class="fiche-recette">
    <div class="bloc">
      <h3 class="groupe">Ingrédients</h3>
      <ul class="ingredients">
        <li><span class="qte">1</span> ordinateur et une connexion Internet</li>
        <li>
          <span class="qte">1</span> compte Anthropic et Claude Code, l’agent de programmation, avec trois
          modèles&#8239;: Opus (le fil principal et la plupart des agents), Sonnet (des agents aux tâches
          bien cadrées), Haiku (des tâches annexes, lancées automatiquement)
        </li>
        <li>
          <span class="qte">1</span> compte GitHub, pour le dépôt public et son historique daté
        </li>
        <li>
          <span class="qte">1</span> compte Cloudflare, pour l’hébergement (Cloudflare Pages), reconstruit
          à chaque envoi
        </li>
        <li>
          <span class="qte">1</span> jeton d’accès ENTSO-E, gratuit, pour les données des pays voisins
        </li>
        <li>
          des données publiques à télécharger&#8239;: RTE et ODRÉ, energy-charts, EDF, ENTSO-E, et
          les rapports de RTE, de la CRE et de l’État
        </li>
        <li>
          des logiciels libres&#8239;: Python, uv et polars pour les données&#8239;; SvelteKit et d3
          pour le site&#8239;; git
        </li>
        <li class="auteur">
          <span class="qte">1</span> brief de {formaterNombre(d.feuillets_brief, 1)} feuillets, coécrit
          par l’auteur avec Claude sur claude.ai avant la première session (temps et coût non comptés
          ici)
        </li>
      </ul>
    </div>

    <div class="bloc">
      <h3 class="groupe">Temps</h3>
      <dl class="temps">
        <div>
          <dt>Cuisson</dt>
          <dd>
            <span class="valeur">{duree(t.actif_min)}</span>
            <span class="precision"
              >temps actif en {sessions.length}
              {pluriel(sessions.length, 'session', 'sessions')}, du {jour(sessions[0].date)} au
              {jour(sessions[sessions.length - 1].date)}&#8239;: l’IA travaille ou attend une
              réponse, pauses de plus de {bilan.pause_min}&nbsp;min retirées</span
            >
          </dd>
        </div>
        <div class="auteur">
          <dt>dont préparation par l’auteur</dt>
          <dd>
            <span class="valeur"
              >{duree(t.reponse_auteur_min)}{#if declarees !== null}&#8239;+ {duree(
                  declarees
                )}{/if}</span
            >
            <span class="precision"
              >{duree(t.reponse_auteur_min)} à lire et répondre entre deux tours de Claude (lancement
              de chaque session, retours, arbitrages)&#8239;: un ordre de grandeur, voir en bas.
              {#if declarees !== null}Plus {duree(declarees)} d’actions manuelles estimées (comptes, hébergement,
                essais sur téléphone, relectures).{:else}Plus des actions manuelles (comptes,
                hébergement, essais sur téléphone, relectures) dont la durée n’est pas encore
                estimée.{/if}</span
            >
          </dd>
        </div>
        <div>
          <dt>Feu des modèles</dt>
          <dd>
            <span class="valeur">{duree(t.calcul_modeles_min)}</span>
            <span class="precision"
              >durée cumulée des appels aux modèles&#8239;: plusieurs agents en parallèle comptent
              chacun, ce qui dépasse le temps de cuisson</span
            >
          </dd>
        </div>
        <div>
          <dt>Commandes</dt>
          <dd>
            <span class="valeur">{duree(t.commandes_min)}</span>
            <span class="precision"
              >lancées par l’IA&#8239;: tests, téléchargements de données, construction du site</span
            >
          </dd>
        </div>
      </dl>
    </div>
  </div>

  <h3 class="groupe">Étapes</h3>
  <ol class="etapes">
    {#each sessions as s (s.numero)}
      {@const e = etape(s.numero)}
      {@const a = actionsDe(s.numero)}
      <li>
        <p class="titre-etape">
          <a href="#{e?.id ?? `session-${s.numero}`}">Session {s.numero}</a>,
          {jour(s.date)}{#if e}
            {' '}<span class="sep">·</span>{' '}
            <!-- eslint-disable-next-line svelte/no-at-html-tags -->
            {@html e.objet}{/if}
        </p>
        <p class="detail-etape">
          {duree(s.actif_min)} de cuisson, dont {duree(s.reponse_auteur_min)} de réponses de l’auteur
          ({formaterNombre(s.signes_auteur, 0)} signes en {s.messages_auteur}
          {pluriel(s.messages_auteur, 'message', 'messages')}){#if a?.actions.length}&#8239;; hors
            conversation&#8239;: {a.actions.join(', ')}{#if a.minutes !== null}
              ({duree(a.minutes)}, estimé){/if}{/if}. {nbAgents(s)}
          {pluriel(nbAgents(s), 'agent', 'agents')}, {jetons(somme(s, 'produits'))} jetons produits{#if s.incomplet}{' '}
            (d’après les transcriptions seules, session pas encore close){:else}, {usd(
              s.cout_api_usd ?? 0
            )} en équivalent API{/if}.
        </p>
      </li>
    {/each}
  </ol>

  <h3 class="groupe">Valeurs nutritionnelles (pour tout le site)</h3>
  <ul class="tuiles">
    <li>
      <span class="libelle">Jetons produits</span>
      <span class="valeur">{jetons(somme(t, 'produits'))}</span>
      <span class="precision"
        >dont {jetons(somme(t, 'dont_reflexion'))} de réflexion non affichée · {produitsParModele(
          t
        )}</span
      >
    </li>
    <li>
      <span class="libelle">Jetons relus en cache</span>
      <span class="valeur">{jetons(somme(t, 'lus_en_cache'))}</span>
      <span class="precision"
        >le même contexte (fichiers, échanges) renvoyé à chaque appel&#8239;: ce n’est pas un volume
        de documents distincts</span
      >
    </li>
    <li>
      <span class="libelle">Coût équivalent API</span>
      <span class="valeur">{usd(t.cout_api_usd ?? 0)}</span>
      <span class="precision"
        >estimé par Claude Code au tarif public de l’API&#8239;: ce n’est pas une facture</span
      >
    </li>
    <li>
      <span class="libelle">Agents distincts</span>
      <span class="valeur">{nbAgents(t)}</span>
      <span class="precision"
        >{ventilation(t.agents, String)}&#8239;; un agent relancé avec son contexte compte une fois
        (le journal, lui, compte les lancements)</span
      >
    </li>
  </ul>
  {#if enCours.length}
    <p class="meta avertissement">
      Session {enCours.join(', ')} pas encore close au relevé&#8239;: ses jetons sont comptés d’après
      les transcriptions (sans Haiku)&#8239;; le feu des modèles, les commandes et le coût ne le sont
      pas encore.
    </p>
  {/if}

  <h3 class="groupe">Ce que ça donne</h3>
  <ul class="tuiles">
    <li class="auteur">
      <span class="libelle">Écrit par l’auteur en session</span>
      <span class="valeur">{formaterNombre(t.feuillets_auteur, 1)} feuillets</span>
      <span class="precision"
        >{formaterNombre(t.signes_auteur, 0)} signes en {t.messages_auteur} messages, plus {t.choix_auteur}
        choix parmi des options proposées par Claude</span
      >
    </li>
    <li>
      <span class="libelle">Écrit par Claude</span>
      <span class="valeur">{formaterNombre(d.feuillets_pages_site, 0)} feuillets</span>
      <span class="precision"
        >pages du site (enquêtes, méthode, message, making-of, citations de l’auteur comprises),
        plus
        {formaterNombre(d.feuillets_rapports, 0)} feuillets de rapports de travail versionnés (sources,
        relectures, spécifications)</span
      >
    </li>
    <li>
      <span class="libelle">Code</span>
      <span class="valeur">{formaterNombre(lignesCode, 0)} lignes</span>
      <span class="precision"
        >{formaterNombre(d.lignes_python, 0)} pour les données (Python), {formaterNombre(
          d.lignes_site,
          0
        )} pour le site, plus {formaterNombre(d.lignes_tests, 0)} lignes de tests</span
      >
    </li>
    <li>
      <span class="libelle">Décisions · erreurs</span>
      <span class="valeur">{decisions.total} · {erreurs}</span>
      <span class="precision"
        >décisions tranchées par l’auteur&#8239;: {decisions.auteur}, par Claude&#8239;: {decisions.claude},
        partagées (l’auteur sur la demande ou le fond, Claude sur la forme)&#8239;: {decisions.partagees}
        · erreurs de Claude et de ses agents, consignées</span
      >
    </li>
  </ul>

  <details class="repli methode">
    <summary>Comment c’est compté</summary>
    <div class="contenu texte">
      <ul>
        <li>
          <strong>Session</strong>&#8239;: une entrée du journal. Une conversation y est rattachée
          si elle a commencé après le début de la session noté dans le journal (à quinze minutes
          près, ces heures étant notées à la main).
        </li>
        <li>
          <strong>Cuisson</strong> (temps actif)&#8239;: périodes où une transcription (fil
          principal ou agent) enregistre une activité&#8239;; une pause de plus de {bilan.pause_min}&nbsp;minutes
          coupe la période. L’auteur n’est pas devant l’écran tout ce temps.
        </li>
        <li>
          <strong>Préparation par l’auteur</strong>&#8239;: deux parts. La première, mesurée, est la
          somme des intervalles entre la dernière activité de Claude et la demande suivante de
          l’auteur (ou sa réponse à une question), quand l’intervalle dure moins de {bilan.pause_min}&nbsp;minutes.
          Ce n’est ni une borne basse ni une borne haute&#8239;: un intervalle peut inclure une
          courte absence, et rien n’est compté des relectures faites pendant que Claude travaille ni
          des intervalles plus longs. La seconde, les actions faites hors de la conversation
          (comptes, branchement de l’hébergement, essais sur téléphone, relectures), est estimée,
          session par session (<code>making-of/actions-auteur.json</code>).
        </li>
        <li>
          <strong>Feu des modèles</strong>&#8239;: somme des durées des requêtes aux modèles,
          relevée par Claude Code (génération, attente et réseau compris). Trois agents qui
          travaillent ensemble pendant une heure comptent trois heures&#8239;: c’est une mesure de
          charge, pas de délai.
        </li>
        <li>
          <strong>Feuillet</strong>&#8239;: {formaterNombre(bilan.signes_par_feuillet, 0)} signes, espaces
          comprises (convention de l’édition française). Les signes de l’auteur sont ceux de ses messages
          et de ses réponses libres&#8239;; une option cochée n’en compte aucun, une commande (<code
            >/clear</code
          >) n’est pas un message. Les textes de Claude sont les fichiers Markdown versionnés de
          <code>docs/</code>, <code>making-of/</code> et <code>site/src/</code>, hors brief.
        </li>
        <li>
          <strong>Jetons</strong>&#8239;: l’unité de texte des modèles (en français, de l’ordre de
          trois à quatre caractères). «&#8239;Produits&#8239;»&#8239;: écrits par le modèle,
          réflexion comprise. «&#8239;Relus en cache&#8239;»&#8239;: le contexte que le modèle relit
          à chaque appel, servi par un cache&#8239;; c’est ce volume qui domine. S’y ajoutent, non
          affichés,
          {jetons(somme(t, 'ecrits_en_cache'))} jetons écrits en cache et {jetons(
            somme(t, 'entree')
          )}
          jetons lus hors cache (surtout Haiku). Le relevé de Claude Code est recoupé avec la somme des
          réponses enregistrées dans les transcriptions&#8239;: un écart de plus de 2&nbsp;% sur les jetons
          produits arrête le relevé.
        </li>
        <li>
          <strong>Coût équivalent API</strong>&#8239;: ce qu’aurait coûté ce volume au tarif public
          de l’API d’Anthropic, calculé par Claude Code. L’auteur n’a pas de relevé de ce qu’il a
          payé.
        </li>
        <li>
          Le relevé est fait par <code>pc bilan</code> (<code>pipeline/pc/bilan.py</code>) au début
          et à la fin de chaque session. Les transcriptions restent sur la machine de
          l’auteur&#8239;: on ne peut pas refaire ce calcul depuis le dépôt, seulement lire comment
          il est fait.
        </li>
      </ul>
    </div>
  </details>
</section>

<style>
  .groupe {
    margin: 1.6rem 0 0.6rem;
    font-family: var(--sans);
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: var(--encre-2);
  }
  .fiche-recette {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr));
    gap: 0 2rem;
  }
  .ingredients {
    list-style: none;
    margin: 0;
    padding: 0;
    font-size: 1rem;
  }
  .ingredients li {
    margin: 0;
    padding: 0.4rem 0 0.4rem 0.6rem;
    border-top: 1px solid var(--trait);
    border-left: 3px solid transparent;
    line-height: 1.45;
  }
  .ingredients li.auteur,
  .temps .auteur {
    border-left-color: var(--signal);
  }
  .qte {
    font-family: var(--sans);
    font-weight: 600;
    margin-right: 0.15rem;
  }
  .temps {
    margin: 0;
  }
  .temps > div {
    padding: 0.45rem 0 0.55rem 0.6rem;
    border-top: 1px solid var(--trait);
    border-left: 3px solid transparent;
  }
  .temps dt {
    font-family: var(--sans);
    font-size: 0.95rem;
    color: var(--encre-2);
  }
  .temps dd {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
  }
  .etapes {
    margin: 0;
    padding-left: 0;
    list-style: none;
    max-width: calc(var(--mesure) + 6rem);
  }
  .etapes li {
    margin: 0;
    padding: 0.5rem 0;
    border-top: 1px solid var(--trait);
  }
  .titre-etape {
    margin: 0;
    font-family: var(--sans);
    font-weight: 600;
  }
  .titre-etape .sep {
    color: var(--encre-2);
    font-weight: 400;
  }
  .detail-etape {
    margin: 0.15rem 0 0;
    font-size: 0.95rem;
    line-height: 1.5;
  }
  .tuiles {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 10rem), 1fr));
    gap: 0.75rem;
  }
  .tuiles li {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    padding: 0.7rem 0.85rem 0.8rem;
    border-top: 3px solid var(--trait);
    background: var(--papier-2);
  }
  .tuiles li.auteur {
    border-top-color: var(--signal);
  }
  .libelle {
    font-family: var(--sans);
    font-size: 0.95rem;
    color: var(--encre-2);
  }
  .valeur {
    font-family: var(--sans);
    font-size: 1.75rem;
    font-weight: 600;
    line-height: 1.15;
    color: var(--encre);
    font-variant-numeric: tabular-nums;
  }
  .precision {
    font-size: 0.875rem;
    line-height: 1.4;
    color: var(--encre-2);
  }
  .avertissement {
    margin-top: 0.6rem;
  }
  .methode {
    margin-top: 1.4rem;
    max-width: calc(var(--mesure) + 2rem);
  }
  .methode > summary {
    padding: 0.25rem 0;
  }
  .methode[open] > summary {
    font-weight: 600;
  }
  .methode > .contenu {
    margin: 0.5rem 0 0.8rem;
    padding-left: 1rem;
    border-left: 2px solid var(--trait);
  }
  .methode ul {
    padding-left: 1.1rem;
  }
  .methode li + li {
    margin-top: 0.5rem;
  }
</style>
