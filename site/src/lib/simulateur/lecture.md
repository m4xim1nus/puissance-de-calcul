<!--
Texte de lecture de la page /simulateur (après les résultats), rendu au prérendu par la même
chaîne que les enquêtes (src/lib/server/enquetes.ts, rendreCorps), notes comprises. Aucun
nombre issu d'une source n'est tapé à la main : {{identifiant}} du référentiel, ou
{{source:clé|page}}. Reprend les définitions et les limites de docs/enquetes/quand.md.
-->

## Lire ces résultats

**La charge résiduelle** est la consommation, moins l'éolien et le solaire produits, moins le
nucléaire **disponible** déclaré par EDF au titre de REMIT. Ce qui reste doit venir de
l'hydraulique (fil de l'eau compris), du gaz, des autres centrales thermiques, des importations
ou du stockage ; les effacements activés sont déjà retranchés de la consommation observée. Ce
n'est pas une marge : la puissance disponible de ces moyens n'est pas observée heure par heure.
Ce n'est pas non plus la « consommation résiduelle » des publications de RTE.

**« Au plus ».** La part de l'énergie ajoutée qui tiendrait dans le nucléaire disponible et non
produit est un plafond, pour trois raisons : une partie de ce nucléaire est réservée aux
services système ; une baisse de production pour économiser le combustible déplace de
l'énergie dans le temps, elle ne la perd pas ; et la France exporte à ces heures-là, si bien
qu'une consommation ajoutée serait d'abord servie, en partie, par moins d'exportations. La
frontière entre « indisponible » et « modulé » est fixée par EDF : ce calcul n'est pas la
modulation publiée par EDF ou par RTE.

**Le maximum observé.** Compter les heures où la charge résiduelle, consommation ajoutée
comprise, dépasse le maximum de l'année, c'est compter les heures où le système serait allé
là où il n'a pas été vu fonctionner cette année-là. Ce n'est ni une défaillance ni une
probabilité de défaillance.

**L'effacement.** Il tombe exactement sur les heures les plus tendues de l'année observée,
comme si on les connaissait à l'avance. Aucun exploitant ne le peut : le résultat est une
borne optimiste de ce qu'un effacement de ce nombre d'heures apporte. Ce que fait le data
center pendant ces heures (reporter son calcul sur un autre site, démarrer ses groupes
électrogènes) n'est pas modélisé.

**Les prix** sont les prix day-ahead observés de la zone France, au pas horaire (depuis le
1er octobre 2025, moyenne des quatre quarts d'heure). La consommation ajoutée les « paie »
tels quels : c'est une lecture du calendrier des prix, pas une facture. Aux heures de prix
négatif ou nul, une consommation de plus aurait réduit le surplus, et parfois rendu le prix
positif.

## Les marges de RTE : une approximation du site

La marge dont parle RTE est le résultat d'une simulation, comparée au critère public de
sécurité d'approvisionnement, une espérance de trois heures de défaillance par an
{{source:rte-bp2025-fonctionnement|p. 2}}. Dans son Bilan prévisionnel 2025, RTE évaluait les
marges de l'hiver 2026-2027 à {{marge_rte_hiver_2026_2027}} par rapport à ce critère, avant la
baisse de disponibilité nucléaire prévue pour cet hiver : la synthèse que RTE publie en
novembre 2026 ne donne plus de marge en GW {{source:rte-hiver-2026-2027|p. 15}}.

Pour une consommation **plate**, rapprocher la puissance réglée plus haut de ces marges est une
approximation de ce site : ajouter X GW consommés en permanence revient, dans un calcul
d'adéquation, à retirer X GW de capacité toujours disponible. RTE n'écrit pas cette
équivalence pour la consommation ; il fait le même passage dans l'autre sens, en traduisant une
hausse de la pointe en besoin de capacité {{source:rte-bp2025-fonctionnement|p. 25}}.
L'équivalence cesse d'être exacte dès que la consommation n'est pas plate : pour RTE, la
contribution d'une consommation au risque de défaillance dépend de son profil
{{source:rte-parametrage-mc-2026|p. 16}}. Avec un effacement, le simulateur montre où la
consommation ajoutée se retire ; il ne dit pas combien de marge elle rend : seul le modèle de
RTE sait faire ce passage.

## Ce que ce calcul ne dit pas

- **Le froid extrême.** Onze années observées ne contiennent pas forcément les froids les plus
  sévères que RTE place dans ses scénarios. Une année observée n'est pas une distribution de
  risque.
- **Le système change.** Les années observées ne sont pas le système dans lequel arriveraient
  ces consommations : d'autres usages s'électrifient, le charbon ferme, le solaire grandit et
  déplace les heures de surplus.
- **Les stocks.** L'hydraulique de lac et les stations de pompage apportent de la puissance aux
  heures tendues, mais sur une quantité d'eau limitée : sur un épisode long, leur puissance
  n'est pas disponible à toute heure.
- **L'écrêtement.** L'éolien et le solaire observés sont ce qui a été produit, après les arrêts
  à prix négatif : aux heures de surplus, la charge résiduelle est surestimée.
- **La pointe exacte.** Les calculs sont à l'heure, en France continentale hors Corse ; une
  pointe à la demi-heure ou au quart d'heure est plus haute.
- **Les données absentes.** Une heure où une série manque n'entre pas dans le calcul qui en a
  besoin (le nombre d'heures retenues est affiché) ; rien n'est imputé.
