<script lang="ts">
  // Simulateur v1 (docs/SIMULATEUR.md) : hypothèses réglables, état dans l'adresse, calcul dans le
  // navigateur par le moteur (./moteur.ts, parité testée avec pipeline/pc/quand.py) sur le CSV de
  // l'année servi par le site. Le texte des hypothèses est rendu au prérendu ; les résultats
  // demandent JavaScript, et le disent.
  //
  // Mise en page revue le 26/11/2026 (retours de l'auteur ; rapport :
  // docs/relectures/2026-11-26-simulateur-ux-agent.md) :
  // - sur ordinateur, l'outil entier (réglages, résultats chiffrés, monotone) tient dans la fenêtre,
  //   sans défilement de la page ; les textes longs (ce que le simulateur ne modélise pas, détail de
  //   chaque résultat, lecture, définitions, sources) sont dans une notice, panneau latéral ouvert à
  //   la demande, à un clic de l'outil, qui laisse les réglages utilisables ;
  // - aucun réglage ne fait bouger la mise en page : la phrase du scénario a une hauteur réservée
  //   (gabarit invisible de la phrase la plus longue), les tuiles ont des hauteurs fixes, les
  //   résultats précédents restent affichés (atténués) pendant le chargement d'une autre année ;
  // - hypothèses (pupitre teinté, à gauche) et résultats (sur le papier, à droite, monotone
  //   comprise) se distinguent ;
  // - sur téléphone, le pupitre reste collé en haut de l'écran, une hypothèse à la fois, choisie
  //   par des onglets qui affichent toutes les valeurs : on voit l'effet en réglant.
  // Sans JavaScript, tout est dans le flux : réglages (inactifs) avec leurs raisons, puis la notice.
  import { onMount, tick, type Snippet } from 'svelte';
  import { typographier } from '$lib/markdown';
  import { afterNavigate, replaceState } from '$app/navigation';
  import { FINE, dateParis, formaterDate, formaterNombre } from '$lib/format';
  import { gw } from '$lib/quand';
  import { lireCsvHoraire } from './csv';
  import {
    BORNES,
    DEFAUTS,
    arrondirFroid,
    arrondirGw,
    ecrireEtat,
    lireEtat,
    type Etat
  } from './etat';
  import { heures, part, puissanceReglee, twh } from './format';
  import { phrases } from './phrases';
  import MonotoneAvantApres from './MonotoneAvantApres.svelte';
  import TableauMonotone from './TableauMonotone.svelte';
  import TexteAnnote from './TexteAnnote.svelte';
  import { simuler, type TableHoraire } from './moteur';
  import type { References } from './references';
  import type { Section } from './sections';

  interface Props {
    annees: number[];
    /** Séries sources (quand.json, `donnees.sources`). */
    sources: string;
    /** Dates d'extraction ISO (quand.json, `donnees.extractions`). */
    extractions: Record<string, string>;
    /** Maximum pluriannuel et chiffres du référentiel cités (préparés au prérendu). */
    references: References;
    /** Texte d'en-tête rendu au prérendu (ce que fait le simulateur, ce qu'il ne modélise pas). */
    enTete: string[];
    /** Texte de lecture rendu au prérendu, une section par titre de niveau 2. */
    lecture: Section[];
    /** Titre de la page, posé en tête de l'outil. */
    tete: Snippet;
  }
  let { annees, sources, extractions, references, enTete, lecture, tete }: Props = $props();

  /** Rangs exacts de la monotone (zoom du graphique) ; au-delà, un rang sur PAS. */
  const ZOOM = 600;
  const PAS = 10;

  let etat = $state<Etat>({ ...DEFAUTS });
  let ecarts = $state<string[]>([]);
  let monte = $state(false);

  // Tables déjà chargées (une par année), et chargement en cours.
  const cache = new Map<number, TableHoraire>();
  let table = $state<TableHoraire | null>(null);
  let anneeTable = $state<number | null>(null);
  let erreur = $state<string | null>(null);

  async function charger(a: number) {
    erreur = null;
    const deja = cache.get(a);
    if (deja) {
      table = deja;
      anneeTable = a;
      return;
    }
    try {
      const r = await fetch(`/donnees/horaire/${a}.csv`);
      if (!r.ok) throw new Error(`réponse ${r.status}`);
      const t = lireCsvHoraire(await r.text());
      cache.set(a, t);
      // Une réponse arrivée après un autre choix d'année est gardée en cache, pas affichée.
      if (etat.annee === a) {
        table = t;
        anneeTable = a;
      }
    } catch (e) {
      if (etat.annee === a) erreur = e instanceof Error ? e.message : String(e);
    }
  }

  /** Outil en pleine fenêtre (ordinateur) : le tracé prend la hauteur qui reste. */
  const PLEIN = '(min-width: 62rem) and (min-height: 36rem)';
  let plein = $state(false);

  onMount(() => {
    const lu = lireEtat(location.search, annees);
    etat = lu.etat;
    ecarts = lu.ecarts;
    monte = true;
    const mq = matchMedia(PLEIN);
    const suivre = () => (plein = mq.matches);
    suivre();
    mq.addEventListener('change', suivre);
    // Anciennes ancres (#presentation, #lecture-1…) et ancres de la notice : la notice s'ouvre.
    const ancre = decodeURIComponent(location.hash.slice(1));
    if (ancre && document.getElementById(ancre)?.closest('#notice')) ouvrirNotice(ancre, null);
    return () => mq.removeEventListener('change', suivre);
  });

  $effect(() => {
    if (monte) charger(etat.annee);
  });

  // replaceState n'est utilisable qu'une fois le routeur prêt (après la première navigation) :
  // appelé dès onMount, il lève une erreur et bloque les effets suivants.
  let routeurPret = $state(false);
  afterNavigate(() => (routeurPret = true));

  $effect(() => {
    if (!monte || !routeurPret) return;
    const q = ecrireEtat(etat);
    if (q !== location.search) replaceState(`${location.pathname}${q}`, {});
  });

  function regler(champ: 'xGw' | 'effacement' | 'froidC' | 'plancherGw', brut: number) {
    if (!Number.isFinite(brut)) return;
    const b = BORNES[champ];
    const v = Math.min(b.max, Math.max(b.min, brut));
    etat[champ] =
      champ === 'effacement'
        ? Math.round(v)
        : champ === 'froidC'
          ? arrondirFroid(v)
          : arrondirGw(v);
    ecarts = [];
  }

  /** « 1,5 °C ». */
  const degres = (c: number) => `${formaterNombre(c, 1)} °C`;

  const pret = $derived(table !== null && anneeTable === etat.annee);
  const xMw = $derived(Math.round(etat.xGw * 1000));
  const plancherMw = $derived(Math.round(etat.plancherGw * 1000));
  const gradient = $derived(references.gradient.mw_par_c);
  const reference = $derived(references.maxPluriannuel.valeur_mw);
  const sim = $derived(
    pret && table
      ? simuler(
          table,
          xMw,
          etat.effacement,
          ZOOM,
          PAS,
          plancherMw,
          reference,
          etat.froidC,
          gradient
        )
      : null
  );
  /** Même puissance sans effacement : comparaison des heures au-delà des maxima. */
  const plate = $derived(
    !sim || !table
      ? null
      : etat.effacement === 0
        ? sim
        : simuler(table, xMw, 0, 1, 1e9, plancherMw, reference, etat.froidC, gradient)
  );
  /** Froid seul (X nul) : les heures qu'aucun effacement de la consommation ajoutée ne supprime. */
  const seul = $derived(
    !sim || !table || etat.froidC === 0
      ? null
      : simuler(table, 0, 0, 1, 1e9, plancherMw, reference, etat.froidC, gradient)
  );
  const libelle = $derived(
    `${puissanceReglee(etat.xGw)}${etat.effacement && xMw > 0 ? `, effacés ${heures(etat.effacement)}` : ''}` +
      (etat.froidC ? `, froid supplémentaire de ${degres(etat.froidC)}` : '')
  );

  /** Résultats du scénario réglé, ou null tant que les séries de l'année ne sont pas chargées. */
  const vue = $derived.by(() => {
    if (!sim || !plate) return null;
    return {
      annee: etat.annee,
      libelle,
      sim,
      ph: phrases(
        etat,
        sim,
        plate,
        references,
        {
          maxReglable: BORNES.effacement.max,
          derniereAnnee: annees[annees.length - 1]
        },
        seul
      )
    };
  });
  // Pendant le chargement d'une autre année, les résultats précédents restent en place, atténués :
  // la mise en page ne saute pas.
  let derniere = $state.raw<NonNullable<typeof vue> | null>(null);
  $effect(() => {
    if (vue) derniere = vue;
  });
  const affiche = $derived(vue ?? derniere);
  const perime = $derived(vue === null && derniere !== null);

  const NOMS: Record<string, string> = {
    eco2mix: 'éCO2mix',
    edf_remit: 'REMIT (EDF)',
    prix: 'prix day-ahead'
  };
  const ligneSources = $derived(
    typographier(
      `Calcul du site, fait dans le navigateur sur les séries horaires publiées ` +
        `(data/export/horaire/${etat.annee}.csv) : ${sources}. Extraction : ` +
        Object.entries(extractions)
          .map(([k, iso]) => `${NOMS[k] ?? k} le ${formaterDate(dateParis(iso))}`)
          .join(', ') +
        '.'
    )
  );
  /** Ligne courte, sous les résultats : le détail est dans la notice. */
  const sourcesCourtes = $derived(
    Object.keys(extractions)
      .map((k) => NOMS[k] ?? k)
      .join(', ')
  );

  /** Rang de la tuile du nucléaire disponible non produit dans l'ordre de `phrases` : la seule qui
   * porte une seconde valeur (sa hauteur est réservée, qu'elle soit là ou non), et rangs des tuiles
   * dont la valeur peut être longue (« non calculable ici », « au plus 52 à 66 % »). Les tuiles
   * d'une rangée ont la hauteur de la plus haute : la réserve vaut pour toute la rangée. */
  const RESERVE = 5;
  const LONGUES = [1, 5];

  /** Gabarit de hauteur de la phrase du scénario : la plus longue possible (effacement et froid,
   * épisode à cheval sur deux années), jamais affichée, seulement mesurée. */
  const GABARIT = typographier(
    '2025 : consommation ajoutée de 12,5 GW à toutes les heures sauf pendant les 500 heures de ' +
      'charge résiduelle la plus élevée, froid compris (au moins 45,3 GW). Froid supplémentaire de ' +
      '11,5 °C pendant les 7 jours les plus tendus, du 28 déc. 2024 au 4 janv. 2025 : 27,6 GW de ' +
      'consommation en plus à chaque heure.'
  );

  // Résumé pour les lecteurs d'écran, différé : un curseur qu'on fait glisser n'annonce pas
  // chaque pas.
  let annonce = $state('');
  $effect(() => {
    const s = sim;
    if (!s) return;
    const texte =
      `${etat.annee}, ${libelle} : ${twh(s.energie_ajoutee_twh)} ajoutés ; ` +
      (s.froid_heures ? `${gw(s.froid_ajout_mw)} de plus pendant l’épisode de froid ; ` : '') +
      (s.part_dans_j === null || s.part_dans_j_plancher === null
        ? ''
        : `au plus ${part(s.part_dans_j_plancher)} à ${part(s.part_dans_j)} dans le nucléaire disponible non produit, avec la disponibilité déclarée par EDF` +
          (s.reintegre?.part_dans_j != null && s.reintegre.part_dans_j_plancher != null
            ? `, ${part(s.reintegre.part_dans_j_plancher)} à ${part(s.reintegre.part_dans_j)} en réintégrant ses arrêts courts pour modulation ; `
            : ' ; ')) +
      `${heures(s.heures_au_dessus_du_max ?? 0)} au-delà du maximum de l’année, ` +
      `${heures(s.heures_au_dessus_du_max_reference ?? 0)} au-delà du maximum ${references.maxPluriannuel.annees}` +
      (s.part_prix_nul_ou_negatif === null
        ? '.'
        : ` ; ${part(s.part_prix_nul_ou_negatif)} de l’énergie à prix nul ou négatif.`);
    const t = setTimeout(() => (annonce = texte), 700);
    return () => clearTimeout(t);
  });

  /* ---------- Notice : panneau latéral (avec JavaScript), texte dans le flux (sans) ---------- */

  let noticeOuverte = $state(false);
  let invocateur: HTMLElement | null = null;

  /** Ouvre la notice sur une section (ou un résultat) et y porte le focus. */
  async function ouvrirNotice(id: string, ev: MouseEvent | null) {
    if (ev) {
      if (ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
      ev.preventDefault();
      if (!noticeOuverte) invocateur = ev.currentTarget as HTMLElement;
    }
    noticeOuverte = true;
    await tick();
    const cible = document.getElementById(id);
    if (!cible) return;
    cible.scrollIntoView({ block: 'start' });
    const focus = cible.matches('h2, h3') ? cible : cible.querySelector<HTMLElement>('h2, h3');
    (focus ?? cible).focus({ preventScroll: true });
  }
  function fermerNotice() {
    noticeOuverte = false;
    invocateur?.focus();
    invocateur = null;
  }
  const lien = (id: string) => ({
    href: `#${id}`,
    ouvrir: (ev: MouseEvent) => ouvrirNotice(id, ev)
  });

  /* ---------- Pupitre sur téléphone : une hypothèse à la fois ---------- */

  type Champ = 'annee' | 'xGw' | 'effacement' | 'froidC' | 'plancherGw';
  let reglageActif = $state<Champ>('xGw');
  const onglets = $derived<{ champ: Champ; nom: string; complet: string; valeur: string }[]>([
    { champ: 'annee', nom: 'Année', complet: 'Année observée', valeur: String(etat.annee) },
    {
      champ: 'xGw',
      nom: 'Puissance',
      complet: 'Puissance appelée ajoutée',
      valeur: puissanceReglee(etat.xGw)
    },
    {
      champ: 'effacement',
      nom: 'Effacement',
      complet: 'Effacement',
      valeur: `${formaterNombre(etat.effacement)}${FINE}h`
    },
    {
      champ: 'froidC',
      nom: 'Froid',
      complet: 'Froid supplémentaire',
      valeur: degres(etat.froidC)
    },
    {
      champ: 'plancherGw',
      nom: 'Plancher',
      complet: 'Nucléaire non mobilisable',
      valeur: puissanceReglee(etat.plancherGw)
    }
  ]);
  const aDefauts = $derived(JSON.stringify(etat) === JSON.stringify(DEFAUTS));
  function remettreDefauts() {
    etat = { ...DEFAUTS };
    ecarts = [];
  }
</script>

<svelte:window
  onkeydown={(e) => {
    if (e.key === 'Escape' && noticeOuverte && monte) fermerNotice();
  }}
/>

<!-- Ordinateur : titre et accès à la notice en tête ; réglages à gauche (pupitre), scénario dessous ;
résultats à droite (chiffres, puis monotone). Téléphone : titre, pupitre collé en haut, scénario,
résultats. -->
<div class="outil" class:js={monte}>
  <div class="tete">
    {@render tete()}
    <ul class="acces" aria-label="Notice du simulateur">
      <li>
        <a
          href="#presentation"
          aria-controls="notice"
          onclick={(e) => ouvrirNotice('presentation', e)}
          >Ce que fait le simulateur, et ce qu’il ne modélise pas</a
        >
      </li>
      <li>
        <a href="#lecture-1" aria-controls="notice" onclick={(e) => ouvrirNotice('lecture-1', e)}
          >Lire ces résultats</a
        >
      </li>
      <li>
        <a
          href="#notice-definitions"
          aria-controls="notice"
          onclick={(e) => ouvrirNotice('notice-definitions', e)}>Définitions et sources</a
        >
      </li>
    </ul>
  </div>

  <section class="hypotheses" aria-labelledby="hypotheses-titre">
    <div class="zone-tete">
      <h2 id="hypotheses-titre">Hypothèses</h2>
      {#if monte}
        <button type="button" class="bouton remise" disabled={aDefauts} onclick={remettreDefauts}
          >Revenir aux valeurs par défaut</button
        >
      {/if}
      <p class="consigne">À régler. Le lien de la page porte le scénario.</p>
    </div>

    {#if monte}
      <!-- Téléphone : une hypothèse à la fois ; les onglets affichent toutes les valeurs. -->
      <div class="onglets" role="group" aria-label="Hypothèse à régler">
        {#each onglets as o (o.champ)}
          <button
            type="button"
            class="onglet"
            aria-controls="hyp-{o.champ}"
            aria-expanded={reglageActif === o.champ}
            onclick={() => (reglageActif = o.champ)}
            ><span class="onglet-nom"
              >{o.nom}{#if o.complet !== o.nom}<span class="lecteur">{' '}({o.complet})</span
                >{/if}</span
            ><span class="onglet-valeur">{o.valeur}</span></button
          >
        {/each}
      </div>
    {/if}

    <div class="hypothese" class:actif={reglageActif === 'annee'} id="hyp-annee">
      <div class="ligne-nom">
        <label class="nom" for="sim-annee">Année observée</label>
        <select
          id="sim-annee"
          value={etat.annee}
          disabled={!monte}
          onchange={(e) => {
            etat.annee = Number((e.currentTarget as HTMLSelectElement).value);
            ecarts = [];
          }}
        >
          {#each annees as a (a)}
            <option value={a}>{a}</option>
          {/each}
        </select>
      </div>
      <details class="pourquoi">
        <summary
          ><span class="defaut"
            >Défaut : {DEFAUTS.annee} ; choix : {annees[0]} à {annees.at(-1)}.</span
          > <span class="raison-lien">Raison</span></summary
        >
        <p class="raison">
          Une année observée, avec sa météo, sa disponibilité nucléaire et ses prix : 2022, année de
          faible disponibilité du parc nucléaire et de prix de crise, ne ressemble pas à 2025. Par
          défaut, la dernière année close ; l’année en cours n’est pas proposée tant qu’elle n’est
          pas close.
        </p>
      </details>
    </div>

    <div class="hypothese" class:actif={reglageActif === 'xGw'} id="hyp-xGw">
      <label class="nom" for="sim-x">Puissance appelée ajoutée</label>
      <div class="ligne-reglage">
        <input
          id="sim-x-curseur"
          type="range"
          min={BORNES.xGw.min}
          max={BORNES.xGw.max}
          step={BORNES.xGw.pas}
          value={etat.xGw}
          disabled={!monte}
          aria-label="Puissance appelée ajoutée, en GW (curseur)"
          aria-valuetext={puissanceReglee(etat.xGw)}
          oninput={(e) => regler('xGw', Number((e.currentTarget as HTMLInputElement).value))}
        />
        <span class="saisie"
          ><input
            id="sim-x"
            type="number"
            inputmode="decimal"
            min={BORNES.xGw.min}
            max={BORNES.xGw.max}
            step={BORNES.xGw.pas}
            value={etat.xGw}
            disabled={!monte}
            onchange={(e) => regler('xGw', Number((e.currentTarget as HTMLInputElement).value))}
          /> GW</span
        >
      </div>
      <details class="pourquoi">
        <summary
          ><span class="defaut"
            >Défaut : {formaterNombre(DEFAUTS.xGw)} GW ; {BORNES.xGw.min} à {BORNES.xGw.max} GW.</span
          > <span class="raison-lien">Raison</span></summary
        >
        <p class="raison">
          Puissance <strong>consommée</strong> en moyenne sur chaque heure, au périmètre de la
          consommation nationale (pertes de réseau comprises), pas puissance réservée ni raccordée :
          un data center raccordé n’utilise qu’une partie de sa puissance de raccordement (voir
          <a href="/combien">« Combien ? »</a>).
        </p>
      </details>
    </div>

    <div class="hypothese" class:actif={reglageActif === 'effacement'} id="hyp-effacement">
      <label class="nom" for="sim-effacement">Profil : plat, avec effacement</label>
      <div class="ligne-reglage">
        <input
          id="sim-effacement-curseur"
          type="range"
          min={BORNES.effacement.min}
          max={BORNES.effacement.max}
          step={BORNES.effacement.pas}
          value={etat.effacement}
          disabled={!monte}
          aria-label="Heures d’effacement par an (curseur)"
          aria-valuetext={heures(etat.effacement)}
          oninput={(e) => regler('effacement', Number((e.currentTarget as HTMLInputElement).value))}
        />
        <span class="saisie"
          ><input
            id="sim-effacement"
            type="number"
            inputmode="numeric"
            min={BORNES.effacement.min}
            max={BORNES.effacement.max}
            step={BORNES.effacement.pas}
            value={etat.effacement}
            disabled={!monte}
            onchange={(e) =>
              regler('effacement', Number((e.currentTarget as HTMLInputElement).value))}
          /> h/an</span
        >
      </div>
      <details class="pourquoi">
        <summary
          ><span class="defaut">Défaut : 0 h (plat) ; 0 à {BORNES.effacement.max} h par an.</span>
          <span class="raison-lien">Raison</span></summary
        >
        <p class="raison">
          Aucune courbe de charge de data center n’est publiée, à notre connaissance : la
          consommation est supposée constante. L’effacement la met à zéro pendant les heures où la
          charge résiduelle
          <strong>observée</strong> est la plus élevée (froid supplémentaire compris), comme si on les
          connaissait à l’avance. Les heures d’effacement qu’il faudrait sont donc une borne basse. L’énergie
          effacée est perdue : elle n’est reportée ni sur d’autres heures ni sur un autre site.
        </p>
      </details>
    </div>

    <div class="hypothese" class:actif={reglageActif === 'froidC'} id="hyp-froidC">
      <label class="nom" for="sim-froid">Froid supplémentaire</label>
      <div class="ligne-reglage">
        <input
          id="sim-froid-curseur"
          type="range"
          min={BORNES.froidC.min}
          max={BORNES.froidC.max}
          step={BORNES.froidC.pas}
          value={etat.froidC}
          disabled={!monte}
          aria-label="Froid supplémentaire sur l’épisode, en degrés (curseur)"
          aria-valuetext={degres(etat.froidC)}
          oninput={(e) => regler('froidC', Number((e.currentTarget as HTMLInputElement).value))}
        />
        <span class="saisie"
          ><input
            id="sim-froid"
            type="number"
            inputmode="decimal"
            min={BORNES.froidC.min}
            max={BORNES.froidC.max}
            step={BORNES.froidC.pas}
            value={etat.froidC}
            disabled={!monte}
            onchange={(e) => regler('froidC', Number((e.currentTarget as HTMLInputElement).value))}
          /> °C</span
        >
      </div>
      <details class="pourquoi">
        <summary
          ><span class="defaut">Défaut : 0 °C ; 0 à {BORNES.froidC.max} °C, sur 7 jours.</span>
          <span class="raison-lien">Raison</span></summary
        >
        <p class="raison">
          Pendant les 7 jours consécutifs où la charge résiduelle observée est la plus élevée, la
          consommation gagne à chaque heure ce froid multiplié par le gradient hivernal moyen publié
          par RTE, {references.gradient.texte}. Ce n’est <strong>pas</strong> un écart aux normales
          : ces jours ont déjà leur propre froid, que le site ne mesure pas, et ces degrés s’y
          ajoutent ; le même réglage ne représente donc pas le même froid d’une année à l’autre.
          Repère, en consommation plutôt qu’en degrés : selon RTE, avec des froids comparables à
          ceux du début des années 2010, les pointes de l’hiver 2026-2027 resteraient « sensiblement
          inférieures à {references.pointeFroids2010.texte} » (sauf cas très exceptionnels) ; avec les
          données de {references.froidPointe.annee}, la consommation horaire du simulateur dépasse
          ce niveau dès {references.froidPointe.texte} de plus. La borne de la plage est un choix du site.
          Le gradient est une moyenne nationale, variable dans la journée : ajouté uniformément à toutes
          les heures, il sous-estime probablement l’effet aux heures de pointe et le surestime la nuit
          ; RTE n’en publie pas la valeur aux froids extrêmes. La consommation due au froid passe avant
          la consommation ajoutée dans le nucléaire disponible non produit ; les prix restent ceux observés.
        </p>
        <div class="notes-raison">
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html references.gradient.note}{@html references.pointeFroids2010.note}{@html references
            .froidPointe.note}
        </div>
      </details>
    </div>

    <div class="hypothese" class:actif={reglageActif === 'plancherGw'} id="hyp-plancherGw">
      <label class="nom" for="sim-plancher">Nucléaire non mobilisable</label>
      <div class="ligne-reglage">
        <input
          id="sim-plancher-curseur"
          type="range"
          min={BORNES.plancherGw.min}
          max={BORNES.plancherGw.max}
          step={BORNES.plancherGw.pas}
          value={etat.plancherGw}
          disabled={!monte}
          aria-label="Plancher de nucléaire non mobilisable, en GW (curseur)"
          aria-valuetext={puissanceReglee(etat.plancherGw)}
          oninput={(e) => regler('plancherGw', Number((e.currentTarget as HTMLInputElement).value))}
        />
        <span class="saisie"
          ><input
            id="sim-plancher"
            type="number"
            inputmode="decimal"
            min={BORNES.plancherGw.min}
            max={BORNES.plancherGw.max}
            step={BORNES.plancherGw.pas}
            value={etat.plancherGw}
            disabled={!monte}
            onchange={(e) =>
              regler('plancherGw', Number((e.currentTarget as HTMLInputElement).value))}
          /> GW</span
        >
      </div>
      <details class="pourquoi">
        <summary
          ><span class="defaut"
            >Défaut : {formaterNombre(DEFAUTS.plancherGw)} GW ; 0 à {BORNES.plancherGw.max} GW.</span
          > <span class="raison-lien">Raison</span></summary
        >
        <p class="raison">
          Une part du nucléaire disponible non produit n’est pas mobilisable pour une consommation
          ajoutée (réserves de services système, rampes, fins de cycle). Le plancher est retranché à
          toute heure pour la borne basse de la fourchette ; à 0, il ne reste que la borne haute. 1
          GW est un ordre de grandeur choisi par le site, pas une donnée publiée. Repère : aux
          heures où le prix dépassait 150 €/MWh en {references.jHeuresCheres.annee}, ce nucléaire
          valait encore en moyenne {references.jHeuresCheres.texte}. La moyenne annuelle la plus
          haute de {references.maxPluriannuel.annees}, {references.jHeuresCheresMax.texte} en {references
            .jHeuresCheresMax.annee} (sur {heures(references.jHeuresCheresMax.heures)}), reste sous
          le haut de la plage. C’est un indice, pas une mesure de la part non mobilisable : à ces
          heures, une partie de ce nucléaire peut aussi être retenue pour garder du combustible.
        </p>
        <div class="notes-raison">
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html references.jHeuresCheres.note}{@html references.jHeuresCheresMax.note}
        </div>
      </details>
    </div>

    {#if ecarts.length}
      <p class="ecarts" role="status">Adresse corrigée : {ecarts.join(' ; ')}.</p>
    {/if}
  </section>

  <!-- Le scénario, appliqué à l'année : les réglages traduits dans les séries (seuil d'effacement,
  dates de l'épisode de froid). Hauteur réservée par le gabarit : elle ne bouge pas avec les
  réglages. -->
  <div class="scenario" class:perime aria-labelledby="scenario-titre" role="region">
    <div class="scenario-tete">
      <p class="scenario-titre" id="scenario-titre">Scénario appliqué à l’année</p>
      {#if monte}
        <button
          type="button"
          class="bouton remise-telephone"
          disabled={aDefauts}
          onclick={remettreDefauts}>Revenir aux défauts</button
        >
      {/if}
    </div>
    <div class="scenario-cadre">
      <p class="scenario-texte">{affiche ? affiche.ph.scenario : ''}</p>
      <p class="scenario-texte gabarit" aria-hidden="true">{GABARIT}</p>
    </div>
  </div>

  <section class="resultats" aria-labelledby="resultats-titre" aria-busy={perime}>
    <div class="zone-tete">
      <h2 id="resultats-titre">Résultats</h2>
      <p class="consigne">Ce que le calcul en tire, heure par heure, sur l’année observée.</p>
      {#if erreur}
        <p class="etat-calcul erreur" role="alert">
          Les séries de {etat.annee} n’ont pas pu être chargées ({erreur}). Rechargez la page.
        </p>
      {:else if monte}
        <p class="etat-calcul" role="status">
          {#if !vue}Chargement des séries de {etat.annee}…{/if}
        </p>
      {/if}
    </div>
    <noscript>
      <p class="sans-js">
        Les résultats sont calculés dans le navigateur, à partir des séries horaires de l’année :
        ils demandent JavaScript. Le reste de la page se lit sans. Les séries sont téléchargeables :
        {#each annees as a, i (a)}<a href="/donnees/horaire/{a}.csv" download>{a}</a>{i <
          annees.length - 1
            ? ', '
            : '.'}{/each}
      </p>
    </noscript>

    {#if monte}
      <dl class="tuiles" class:perime>
        {#if affiche}
          {#each affiche.ph.tuiles as tu, k (tu.titre)}
            <div class="tuile" class:reserve={k === RESERVE} class:longue={LONGUES.includes(k)}>
              <dt>{tu.titre}</dt>
              <dd class="valeur">
                {#if tu.qualif}<span class="qualif">{tu.qualif}</span>{/if}
                {tu.valeur}
              </dd>
              {#if k === RESERVE || tu.complement}<dd class="complement">
                  {tu.complement ?? ''}
                </dd>{/if}
              <dd class="lien-detail">
                <a
                  href="#notice-tuile-{k}"
                  aria-controls="notice"
                  onclick={(e) => ouvrirNotice(`notice-tuile-${k}`, e)}
                  >Détail<span class="lecteur">{' '}et sources : {tu.titre}</span></a
                >
              </dd>
            </div>
          {/each}
        {:else}
          {#each { length: 7 }, k (k)}
            <div
              class="tuile vide"
              class:reserve={k === RESERVE}
              class:longue={LONGUES.includes(k)}
              aria-hidden="true"
            >
              <dt>&nbsp;</dt>
              <dd class="valeur">…</dd>
              {#if k === RESERVE}<dd class="complement"></dd>{/if}
              <dd class="lien-detail">&nbsp;</dd>
            </div>
          {/each}
        {/if}
      </dl>

      <div class="graphique" class:perime>
        {#if affiche && affiche.sim.rn_max_mw !== null}
          <MonotoneAvantApres
            annee={affiche.annee}
            libelle={affiche.libelle}
            avant={affiche.sim.monotone_avant}
            apres={affiche.sim.monotone_apres}
            rnMaxMw={affiche.sim.rn_max_mw}
            rnMaxPluriMw={references.maxPluriannuel.valeur_mw}
            anneesPluri={references.maxPluriannuel.annees}
            zoom={ZOOM}
            {plein}
            notes={lien('notice-graphique')}
          />
        {/if}
      </div>

      <p class="sources-outil">
        <span class="cle">Sources</span>
        {sourcesCourtes} ; calcul du site, dans le navigateur.
        <a
          href="#notice-sources"
          aria-controls="notice"
          onclick={(e) => ouvrirNotice('notice-sources', e)}>Détail, dates d’extraction, CSV</a
        >
      </p>
    {/if}
    <p class="lecteur" aria-live="polite">{annonce}</p>
  </section>
</div>

<!-- Notice : avec JavaScript, panneau latéral fermé par défaut, ouvert depuis l'outil (les
réglages restent utilisables à côté, le détail des résultats suit les réglages) ; sans JavaScript,
texte dans le flux, sous l'outil. -->
<aside
  id="notice"
  class="notice"
  class:tiroir={monte}
  hidden={monte && !noticeOuverte}
  aria-labelledby="notice-titre"
>
  <div class="notice-tete">
    <p class="notice-titre" id="notice-titre">Notice du simulateur</p>
    {#if monte}
      <button type="button" class="bouton" onclick={fermerNotice}>Fermer</button>
    {/if}
    <ul class="notice-sommaire">
      <li>
        <a href="#presentation" onclick={(e) => ouvrirNotice('presentation', e)}
          >Ce qu’il ne modélise pas</a
        >
      </li>
      <li>
        <a href="#notice-resultats" onclick={(e) => ouvrirNotice('notice-resultats', e)}
          >Détail des résultats</a
        >
      </li>
      <li>
        <a href="#lecture-1" onclick={(e) => ouvrirNotice('lecture-1', e)}>Lire ces résultats</a>
      </li>
      <li>
        <a href="#notice-definitions" onclick={(e) => ouvrirNotice('notice-definitions', e)}
          >Définitions</a
        >
      </li>
      <li>
        <a href="#notice-sources" onclick={(e) => ouvrirNotice('notice-sources', e)}
          >Sources et données</a
        >
      </li>
    </ul>
  </div>

  <section class="notice-section" aria-labelledby="presentation">
    <h2 id="presentation" tabindex="-1">Ce que fait le simulateur, et ce qu’il ne modélise pas</h2>
    <TexteAnnote blocs={enTete} />
  </section>

  <section class="notice-section" aria-labelledby="notice-resultats">
    <h2 id="notice-resultats" tabindex="-1">Détail des résultats</h2>
    {#if affiche}
      <p class="notice-scenario">{affiche.ph.scenario}</p>
      {#each affiche.ph.tuiles as tu, k (tu.titre)}
        <div class="notice-tuile" id="notice-tuile-{k}">
          <h3 tabindex="-1">{tu.titre}</h3>
          <p class="valeur">
            {#if tu.qualif}<span class="qualif">{tu.qualif}</span>{/if}
            {tu.valeur}
          </p>
          {#if tu.complement}<p class="complement">{tu.complement}</p>{/if}
          <p class="detail">{tu.detail}</p>
          {#if tu.notes?.length}
            <div class="notes-tuile">
              <!-- eslint-disable-next-line svelte/no-at-html-tags -->
              {#each tu.notes as n, j (j)}{@html n}{/each}
            </div>
          {/if}
        </div>
      {/each}
    {:else}
      <p>
        Les résultats sont calculés dans le navigateur, à partir des séries horaires de l’année :
        ils demandent JavaScript.
      </p>
    {/if}
  </section>

  {#each lecture as s, i (i)}
    <section class="notice-section" aria-labelledby="lecture-{i + 1}">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      <h2 id="lecture-{i + 1}" tabindex="-1">{@html s.titre}</h2>
      <TexteAnnote blocs={[s.html]} />
    </section>
  {/each}

  <section class="notice-section" aria-labelledby="notice-definitions">
    <h2 id="notice-definitions" tabindex="-1">Définitions et heures renseignées</h2>
    <dl class="definitions">
      <div>
        <dt>Charge résiduelle</dt>
        <dd>
          consommation − éolien − solaire − nucléaire <strong>disponible</strong> déclaré par EDF (REMIT),
          heure par heure : ce que doivent fournir l’hydraulique, le thermique, les importations et le
          stockage. Ce n’est pas une marge.
        </dd>
      </div>
      <div>
        <dt>Nucléaire disponible non produit</dt>
        <dd>
          nucléaire déclaré disponible − nucléaire produit, heure par heure : une puissance restée
          inemployée, pas un gisement d’énergie. Il dépend de ce qu’EDF déclare indisponible, y
          compris des arrêts « pour modulation » : le résultat donne aussi la valeur en réintégrant
          ceux de moins de 7 jours, économiques. Ce n’est pas la « modulation » publiée par EDF.
        </dd>
      </div>
      <div>
        <dt>Prix day-ahead</dt>
        <dd>prix de gros de la zone France, fixé la veille pour le lendemain, heure par heure.</dd>
      </div>
    </dl>
    {#if affiche}
      {@const s = affiche.sim}
      <p class="couverture">
        Heures de {affiche.annee} (année civile, heure de Paris) : {formaterNombre(s.heures)}.
        Charge résiduelle renseignée : {formaterNombre(s.heures_rn_valides)} ; nucléaire disponible et
        produit : {formaterNombre(s.heures_j_valides)} ; prix : {formaterNombre(
          s.heures_prix_valides
        )}. Chaque résultat porte sur les heures où ses données sont renseignées.
      </p>
    {/if}
  </section>

  <section class="notice-section" aria-labelledby="notice-sources">
    <h2 id="notice-sources" tabindex="-1">Sources et données</h2>
    <p class="sources-detail">
      <span class="cle">Sources</span>
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html ligneSources}
      <a href="/donnees/horaire/{etat.annee}.csv" download>Télécharger les séries de {etat.annee}</a
      > (CSV).
    </p>
    {#if affiche && affiche.sim.rn_max_mw !== null}
      <div id="notice-graphique">
        <h3 tabindex="-1">
          Graphique : charge résiduelle de {affiche.annee}, heures classées de la plus tendue à la
          moins tendue : observée et avec {affiche.libelle}
        </h3>
        <p>
          En GW, moyenne de chaque heure. D’abord toute l’année, puis les {formaterNombre(ZOOM)} heures
          les plus tendues, sur une autre échelle. Chaque courbe est classée pour elle-même : l’heure
          de rang 1 n’est pas forcément la même avant et après.
        </p>
        <p>
          Charge résiduelle = consommation − éolien − solaire − nucléaire disponible déclaré par
          EDF. Au-dessus du maximum de l’année, le système aurait dû couvrir plus que cette année-là
          ; au-dessus du maximum 2015-2025, plus que toutes les années observées. Ni l’un ni l’autre
          n’est une défaillance.{affiche.sim.x_mw > 0 && affiche.sim.heures_effacees.length > 0
            ? ' Les heures effacées gardent leur charge résiduelle observée : elles se rangent en haut de la courbe « avec », qui s’y confond avec la courbe observée.'
            : ''} Au-delà des {formaterNombre(ZOOM)} premières heures, une heure sur dix est tracée.
        </p>
        <p class="sources-detail">
          <span class="cle">Sources</span>
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          {@html ligneSources}
        </p>
        <h4>Tableau des données : charge résiduelle à quelques rangs, observée et simulée</h4>
        <TableauMonotone
          annee={affiche.annee}
          libelle={affiche.libelle}
          avant={affiche.sim.monotone_avant}
          apres={affiche.sim.monotone_apres}
        />
      </div>
    {/if}
  </section>
</aside>

<style>
  /* ---------- Ossature ---------- */
  .outil {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    grid-template-areas: 'tete' 'hyp' 'scen' 'res';
    gap: 1rem;
  }
  .tete {
    grid-area: tete;
  }
  .hypotheses {
    grid-area: hyp;
  }
  .scenario {
    grid-area: scen;
  }
  .resultats {
    grid-area: res;
    container: resultats / inline-size;
  }
  @media (min-width: 62rem) {
    .outil {
      grid-template-columns: 22rem minmax(0, 1fr);
      grid-template-rows: auto minmax(0, 1fr) auto;
      grid-template-areas: 'tete tete' 'hyp res' 'scen res';
      gap: 0.75rem 2rem;
    }
  }
  /* Pleine fenêtre : l'outil prend la hauteur que lui laisse la page ; le pupitre défile en
     interne si une raison dépliée dépasse ; les résultats donnent au graphique la hauteur qui
     reste. */
  @media (min-width: 62rem) and (min-height: 36rem) {
    .outil {
      flex: 1 1 auto;
      min-height: 0;
    }
    .hypotheses {
      overflow-y: auto;
      overscroll-behavior: contain;
    }
    .resultats {
      display: flex;
      flex-direction: column;
      min-height: 0;
    }
    .graphique {
      flex: 1 1 0;
      min-height: 11rem;
      display: flex;
      flex-direction: column;
    }
  }

  /* ---------- Tête : titre et accès à la notice ---------- */
  .tete {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.25rem 2rem;
  }
  .acces {
    display: flex;
    flex-wrap: wrap;
    gap: 0.2rem 1.25rem;
    margin: 0;
    padding: 0;
    list-style: none;
    font-family: var(--sans);
    font-size: 0.98rem;
  }
  .acces li {
    margin: 0;
  }

  /* ---------- Hypothèses : le pupitre (teinté, encadré) ---------- */
  /* Position relative : les textes masqués à l'écran (.lecteur, en absolu) restent dans le pupitre
     et ne font pas défiler la page quand une raison est dépliée. */
  .hypotheses {
    position: relative;
    padding: 0.6rem 0.9rem 0.7rem;
    background: var(--pupitre);
    border: 1px solid var(--pupitre-bord);
    border-radius: 6px;
  }
  .zone-tete {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0 0.75rem;
    margin: 0 0 0.35rem;
  }
  h2 {
    margin: 0;
    font-size: 1.25rem;
  }
  .consigne {
    margin: 0;
    font-family: var(--sans);
    font-size: 0.92rem;
    line-height: 1.3;
    color: var(--encre-2);
  }
  .hypothese {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 0.05rem;
    padding: 0.3rem 0 0.25rem;
    border-top: 1px solid var(--pupitre-bord);
  }
  .ligne-nom {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.25rem 0.75rem;
    font-family: var(--sans);
  }
  .nom {
    font-family: var(--sans);
    font-weight: 600;
    font-size: 1.02rem;
    line-height: 1.25;
  }
  /* Curseur et saisie sur une ligne : la hauteur d'un réglage ne dépend pas de son nom. */
  .ligne-reglage {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }
  input[type='range'] {
    flex: 1 1 auto;
    min-width: 0;
    margin: 0.1rem 0;
    accent-color: var(--encre);
  }
  .saisie {
    white-space: nowrap;
    font-family: var(--sans);
  }
  input[type='number'],
  select {
    font: inherit;
    font-size: 1.02rem;
    font-variant-numeric: tabular-nums;
    color: var(--encre);
    background: var(--papier);
    border: 1px solid var(--encre-2);
    border-radius: 3px;
    padding: 0.1rem 0.4rem;
  }
  input[type='number'] {
    width: 4.2rem;
  }
  .saisie {
    display: inline-block;
    min-width: 6.6rem;
  }
  :disabled {
    opacity: 0.6;
  }
  /* Le défaut et la plage sont dans le résumé du repli « Raison » : une ligne par réglage. */
  .defaut {
    font-family: var(--sans);
    font-size: 0.88rem;
    line-height: 1.3;
    color: var(--encre-2);
  }
  .raison-lien {
    font-family: var(--sans);
    font-size: 0.88rem;
    color: var(--encre);
    text-decoration: underline;
    text-underline-offset: 0.15em;
    white-space: nowrap;
  }
  .pourquoi > summary {
    cursor: pointer;
    line-height: 1.3;
  }
  .raison {
    margin: 0.3rem 0 0.2rem;
    padding-left: 0.6rem;
    border-left: 2px solid var(--pupitre-bord);
    font-size: 0.92rem;
    line-height: 1.5;
  }
  .notes-raison {
    margin: 0.2rem 0 0.3rem;
    padding-top: 0.3rem;
    border-top: 1px solid var(--pupitre-bord);
    font-size: 0.8125rem;
    line-height: 1.4;
  }
  .ecarts {
    margin: 0.5rem 0;
    font-family: var(--sans);
    font-size: 0.92rem;
    border-left: 3px solid var(--signal);
    padding-left: 0.6rem;
  }
  .bouton {
    font: inherit;
    font-family: var(--sans);
    font-size: 0.92rem;
    color: var(--encre);
    background: var(--papier);
    border: 1px solid var(--encre-2);
    border-radius: 3px;
    padding: 0.15rem 0.6rem;
    cursor: pointer;
  }
  .bouton:hover:not(:disabled) {
    background: var(--papier-2);
  }
  .bouton:disabled {
    cursor: default;
  }
  .remise {
    margin-left: auto;
    font-size: 0.85rem;
    padding: 0.05rem 0.45rem;
  }
  .hypotheses .consigne {
    flex-basis: 100%;
    font-size: 0.86rem;
  }
  .resultats .consigne {
    flex-basis: auto;
  }
  .remise-telephone {
    display: none;
  }
  .scenario-tete {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
  }
  .onglets {
    display: none;
  }

  /* ---------- Scénario appliqué (hauteur réservée) ---------- */
  .scenario {
    font-family: var(--sans);
  }
  .scenario-titre {
    margin: 0 0 0.1rem;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--encre-2);
  }
  .scenario-cadre {
    display: grid;
  }
  .scenario-texte {
    grid-area: 1 / 1;
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.32;
  }
  .gabarit {
    visibility: hidden;
    user-select: none;
  }

  /* ---------- Résultats (sur le papier) ---------- */
  .resultats .zone-tete {
    margin-bottom: 0.4rem;
  }
  .etat-calcul {
    margin: 0;
    font-family: var(--sans);
    font-size: 0.92rem;
    color: var(--encre-2);
  }
  .etat-calcul:empty {
    display: none;
  }
  .sans-js {
    font-family: var(--sans);
    color: var(--encre-2);
    max-width: var(--mesure);
  }
  .erreur {
    color: var(--encre);
    border-left: 3px solid var(--sur-zero);
    padding-left: 0.6rem;
  }
  .perime {
    opacity: 0.45;
  }
  @media (prefers-reduced-motion: no-preference) {
    .tuiles,
    .graphique,
    .scenario {
      transition: opacity 0.2s;
    }
  }

  /* Tuiles : hauteurs fixes (titre sur deux lignes, valeur sur une, seconde valeur réservée sur la
     deuxième rangée) ; la valeur ne passe pas à la ligne. */
  .tuiles {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.6rem 1rem;
    margin: 0 0 0.6rem;
  }
  @container resultats (min-width: 36rem) {
    .tuiles {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.6rem 1.25rem;
    }
  }
  @container resultats (min-width: 54rem) {
    .tuiles {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }
  .tuile {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas: 'titre lien' 'valeur valeur' 'complement complement';
    align-content: start;
    column-gap: 0.5rem;
    border-top: 2px solid var(--encre);
    padding-top: 0.3rem;
  }
  .tuile dt {
    grid-area: titre;
    min-height: 2.4em;
    font-family: var(--sans);
    font-weight: 500;
    font-size: 0.9rem;
    line-height: 1.2;
    color: var(--encre-2);
  }
  .tuile dd {
    margin: 0;
  }
  .tuile dd.valeur {
    grid-area: valeur;
    font-family: var(--sans);
    font-weight: 600;
    font-size: 1.45rem;
    line-height: 1.2;
    margin: 0.05rem 0 0;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }
  .qualif {
    font-size: 1rem;
    font-weight: 500;
  }
  .tuile dd.complement {
    grid-area: complement;
    font-family: var(--sans);
    font-size: 0.78rem;
    line-height: 1.25;
    color: var(--encre-2);
  }
  .tuile.reserve dd.complement {
    min-height: 5em;
  }
  .lien-detail {
    grid-area: lien;
    font-family: var(--sans);
    font-size: 0.88rem;
    line-height: 1.2;
  }
  .tuile.vide dd.valeur {
    color: var(--encre-2);
  }
  /* Tuiles étroites (téléphone, deux colonnes) : la valeur peut passer à la ligne, sur deux lignes
     réservées ; le lien du détail passe sous la valeur. */
  @container resultats (max-width: 35.99rem) {
    .tuile {
      grid-template-areas: 'titre titre' 'valeur valeur' 'complement complement' 'lien lien';
    }
    .tuile dd.valeur {
      white-space: normal;
      font-size: 1.3rem;
    }
    .tuile.longue dd.valeur {
      min-height: 2.4em;
    }
    .tuile.reserve dd.complement {
      min-height: 6.25em;
    }
    .lien-detail {
      margin-top: 0.15rem;
    }
  }

  .sources-outil {
    margin: 0.5rem 0 0;
    font-family: var(--sans);
    font-size: 0.88rem;
    line-height: 1.35;
    color: var(--encre-2);
  }
  .sources-outil .cle,
  .sources-detail .cle {
    font-weight: 600;
    color: var(--encre);
  }

  /* ---------- Téléphone et tablette étroite : pupitre collé en haut, une hypothèse à la fois ---------- */
  @media (max-width: 61.99rem) {
    .outil.js .hypotheses {
      position: sticky;
      top: 0;
      z-index: 5;
      max-height: 60dvh;
      overflow-y: auto;
      overscroll-behavior: contain;
      padding: 0.45rem 0.6rem 0.4rem;
      border-radius: 0 0 6px 6px;
      box-shadow: 0 2px 6px rgb(0 0 0 / 0.18);
    }
    .outil.js .hypotheses .zone-tete {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip-path: inset(50%);
      white-space: nowrap;
    }
    .outil.js .onglets {
      display: flex;
      gap: 0.25rem;
      margin: 0 0 0.25rem;
      overflow-x: auto;
    }
    .outil.js .hypothese:not(.actif),
    .outil.js .remise {
      display: none;
    }
    .outil.js .remise-telephone {
      display: inline-block;
      white-space: nowrap;
      font-size: 0.85rem;
      padding: 0.05rem 0.45rem;
    }
    .outil.js .hypothese {
      border-top: 0;
      padding: 0.1rem 0 0;
    }
    .onglet {
      flex: 1 1 0;
      min-width: 3.4rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0.15rem 0.15rem 0.2rem;
      font: inherit;
      font-family: var(--sans);
      line-height: 1.15;
      color: var(--encre);
      background: var(--papier);
      border: 1px solid var(--pupitre-bord);
      border-bottom-width: 3px;
      border-radius: 4px;
      cursor: pointer;
    }
    .onglet[aria-expanded='true'] {
      border-color: var(--encre);
    }
    .onglet-nom {
      font-size: 0.74rem;
      color: var(--encre-2);
      white-space: nowrap;
    }
    .onglet-valeur {
      font-size: 0.92rem;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }
    .onglet[aria-expanded='true'] .onglet-valeur {
      text-decoration: underline;
      text-decoration-thickness: 2px;
      text-underline-offset: 0.2em;
    }
    .tete {
      display: block;
    }
    .acces {
      margin-top: 0.25rem;
    }
  }

  /* ---------- Notice ---------- */
  .notice {
    margin-top: 2rem;
    border-top: 1px solid var(--encre);
  }
  .notice-tete {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.3rem 1rem;
    padding: 0.6rem 0 0.5rem;
    font-family: var(--sans);
  }
  .notice-titre {
    margin: 0;
    font-weight: 600;
    font-size: 1.1rem;
  }
  .notice-sommaire {
    flex-basis: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 0.15rem 1rem;
    margin: 0;
    padding: 0;
    list-style: none;
    font-size: 0.92rem;
  }
  .notice-sommaire li {
    margin: 0;
  }
  .notice-section {
    max-width: var(--large);
    border-top: 1px solid var(--trait);
    padding-top: 0.25rem;
  }
  .notice-section > h2 {
    margin: 0.6rem 0 0.5rem;
    font-size: 1.3rem;
    scroll-margin-top: 6rem;
  }
  .notice-section > h2:focus {
    outline: none;
  }
  .notice-section > h2:focus-visible {
    outline: 2px solid var(--encre);
  }
  .notice-scenario {
    font-family: var(--sans);
    color: var(--encre-2);
    max-width: var(--mesure);
  }
  .notice-tuile {
    max-width: var(--mesure);
    margin: 0 0 1.1rem;
    padding-top: 0.35rem;
    border-top: 2px solid var(--encre);
    scroll-margin-top: 6rem;
  }
  .notice-tuile h3,
  #notice-graphique h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 500;
    color: var(--encre-2);
  }
  .notice-tuile .valeur {
    margin: 0.05rem 0 0.1rem;
    font-family: var(--sans);
    font-weight: 600;
    font-size: 1.35rem;
    line-height: 1.2;
  }
  .notice-tuile .complement {
    margin: 0 0 0.3rem;
    font-family: var(--sans);
    font-size: 0.9rem;
    color: var(--encre-2);
  }
  .notice-tuile .detail {
    margin: 0.2rem 0 0;
    font-size: 0.95rem;
    line-height: 1.5;
  }
  .notes-tuile {
    margin-top: 0.4rem;
    padding-top: 0.3rem;
    border-top: 1px solid var(--trait);
    font-size: 0.8125rem;
    line-height: 1.4;
  }
  .definitions {
    display: grid;
    gap: 0.35rem;
    margin: 0.4rem 0 0.6rem;
    max-width: var(--mesure);
    font-size: 0.95rem;
    line-height: 1.45;
  }
  .definitions dt {
    display: inline;
    font-family: var(--sans);
    font-weight: 600;
  }
  .definitions dt::after {
    content: '\00a0: ';
  }
  .definitions dd {
    display: inline;
    margin: 0;
  }
  .couverture,
  .sources-detail {
    max-width: var(--mesure);
    font-family: var(--sans);
    font-size: 0.92rem;
    line-height: 1.4;
    color: var(--encre-2);
  }
  #notice-graphique {
    max-width: var(--mesure);
    margin-top: 1.25rem;
    padding-top: 0.35rem;
    border-top: 2px solid var(--encre);
    scroll-margin-top: 6rem;
  }
  #notice-graphique p {
    font-size: 0.95rem;
    line-height: 1.5;
  }
  #notice-graphique h4 {
    margin: 1rem 0 0;
    font-size: 1rem;
  }
  /* Dans la notice, les notes du texte vont sous leur paragraphe (pas de marge de notes). */
  .notice :global(.texte-annote .avec-notes) {
    display: flex !important;
    flex-direction: column;
  }
  .notice :global(.texte-annote .notes) {
    float: none !important;
    width: auto !important;
    margin: 0 0 1.1rem !important;
  }
  .notice :global(.texte-annote h2) {
    font-size: 1.15rem;
    margin-top: 1.4em;
  }

  /* Avec JavaScript : panneau latéral, à droite, par-dessus les résultats ; le pupitre reste
     visible et utilisable à gauche. Plein écran sur téléphone. */
  .notice.tiroir {
    position: fixed;
    z-index: 30;
    top: 0;
    right: 0;
    bottom: 0;
    width: min(46rem, 100vw - 21rem);
    margin: 0;
    padding: 0 1.25rem 3rem;
    overflow-y: auto;
    overscroll-behavior: contain;
    background: var(--papier);
    border-top: 0;
    border-left: 1px solid var(--encre-2);
    box-shadow: -6px 0 18px rgb(0 0 0 / 0.22);
  }
  .notice.tiroir[hidden] {
    display: none;
  }
  .notice.tiroir .notice-tete {
    position: sticky;
    top: 0;
    z-index: 1;
    background: var(--papier);
    border-bottom: 1px solid var(--trait);
    margin: 0 -1.25rem;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
  }
  @media (max-width: 61.99rem) {
    .notice.tiroir {
      width: 100vw;
      padding: 0 1rem 3rem;
      border-left: 0;
    }
    .notice.tiroir .notice-tete {
      margin: 0 -1rem;
      padding-left: 1rem;
      padding-right: 1rem;
    }
  }
</style>
