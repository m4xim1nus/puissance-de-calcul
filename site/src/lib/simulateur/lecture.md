<!--
Texte de lecture de la page /simulateur (après les résultats), rendu au prérendu par la même
chaîne que les enquêtes (src/lib/server/enquetes.ts, rendreCorps), notes comprises. Aucun
nombre issu d'une source n'est tapé à la main : {{identifiant}} du référentiel, ou
{{source:clé|page}}. Reprend les définitions, les formulations et les limites de docs/enquetes/quand.md (version
corrigée après relecture) ; à réaligner si ce texte change. Une ligne `- ::: inclure nom :::` est
remplacée par docs/enquetes/partage/nom.md, texte commun avec « Quand ? » (pas de recopie à la main).
-->

## Lire ces résultats

**La charge résiduelle** est la consommation, moins l'éolien et le solaire produits, moins le
nucléaire **disponible** déclaré par EDF au titre de REMIT. Ce qui reste doit venir de
l'hydraulique (fil de l'eau compris), du gaz, des autres centrales thermiques, des importations
ou du stockage ; les effacements activés sont déjà retranchés de la consommation observée. Ce
n'est pas une marge : la puissance disponible de ces moyens n'est pas observée heure par heure.
Ce n'est pas non plus la « consommation résiduelle » des publications de RTE.

**« Au plus », et une fourchette.** La part de l'énergie ajoutée qui tiendrait dans le
nucléaire disponible et non produit est un plafond, avec la disponibilité déclarée par EDF, et
un plafond lâche. Même aux heures les
plus chères, ce nucléaire reste le plus souvent au-dessus de zéro : en 2025, il valait encore en moyenne
{{quand_j_heures_cheres_2025}} aux heures où le prix dépassait 150 €/MWh. Une part de ce
« reste » n'est pas mobilisable (réserves de services système, rampes, fins de cycle). D'où la
fourchette affichée : sans plancher, et en retranchant un plancher à toute heure, 1 GW par défaut,
un ordre de grandeur choisi par ce site, que le réglage « Nucléaire non mobilisable » fait varier.
Sous cette fourchette, le résultat en donne une seconde, en réintégrant les arrêts courts (moins de
sept jours) qu'EDF déclare indisponibles pour modulation.

::: inclure arrets-modulation :::

**En énergie, la limite est plus nette encore.** Servir ainsi la consommation ajoutée
demanderait autant de production nucléaire en plus sur l'année : le résultat la met en regard
de la production observée et, pour 2025, de ce que prévoit l'exploitant. La puissance restée
inemployée heure par heure ne dit pas que le combustible et le calendrier des arrêts
suivraient : une baisse de production pour économiser le combustible déplace de l'énergie dans
le temps, elle ne la perd pas. Réintégrer les arrêts courts pour modulation ne lève pas cette
limite : la production nucléaire supplémentaire nécessaire n'en est que plus haute. La frontière entre « indisponible »
et « modulé » est fixée par EDF : ce calcul n'est pas la modulation publiée par EDF ou par RTE.

**Qui servirait cette consommation** (plus de nucléaire, moins d'éolien et de solaire
arrêtés, ou moins d'exportations) dépend, heure par heure, de la saturation des
interconnexions et des prix voisins. Ce site ne sait pas encore le dire : les données des pays
voisins ne sont pas branchées. On sait seulement que la France exporte massivement à ces
heures : le solde moyen affiché est un constat. Si la consommation ajoutée réduisait ces
exportations, ce qui manquerait aux voisins se mesurerait avec le facteur d'émission marginal
européen, que ce calcul ne donne pas.

**Deux maxima.** Le compte au-delà du maximum de l'année tient beaucoup à une seule heure :
dès que la consommation ajoutée est positive, l'heure du maximum se dépasse elle-même, et les
heures suivantes sont souvent nettement plus bas. Le maximum de 2015 à 2025,
{{quand_rn_max_pluri}}, remet l'échelle en place. Le système l'a couvert, mais avec d'autres
moyens : à cette heure de février 2018, du charbon et du fioul, et des importations
importantes ; en décembre 2022, des importations massives à des prix extrêmes. Dépasser un
maximum observé n'est pas une défaillance ; c'est demander au système de couvrir ce qu'il n'a
couvert que dans ses pires années, voire davantage.

**L'effacement** tombe exactement sur les heures les plus tendues de l'année observée (froid
supplémentaire compris, s'il est réglé), comme si on les connaissait à l'avance. Prévoir la charge résiduelle du lendemain est une chose ; savoir
en janvier si une heure sera parmi les plus tendues de l'année en est une autre. Le nombre
d'heures d'effacement qu'il faudrait est donc une **borne basse**. Le calcul est aussi
circulaire : les heures effacées sont, par construction, celles que compte l'indicateur du
maximum, et avec assez d'heures il tombe à zéro, ce qui ne prouve rien d'un effacement réel.
C'est une borne pour cet indicateur seulement, ni pour le risque de défaillance (les heures de
risque que simule RTE dépendent aussi des stocks d'eau et des importations), ni pour les prix.
L'énergie effacée est **perdue** : elle n'est reportée ni sur d'autres heures ni sur un autre
site. La vraisemblance d'un effacement total de plusieurs centaines d'heures par an n'est pas
discutée ici.

**Les prix** sont les prix day-ahead observés de la zone France, au pas horaire (depuis le
1er octobre 2025, moyenne des quatre quarts d'heure). La part de l'énergie ajoutée consommée à
prix nul ou négatif est une lecture du calendrier des prix, pas une facture ; pour une
consommation plate, c'est la part des heures de l'année à prix nul ou négatif, quelle que soit
la puissance. Avec quelques GW de plus, une partie de ces heures n'aurait plus été à prix nul ou
négatif : la consommation ajoutée aurait absorbé une part du surplus. Le simulateur n'affiche
pas de prix moyen payé : sans effet en retour, il se lirait comme un coût, et son écart avec
ou sans effacement comme une économie.

## Les marges de RTE : un rapprochement

La marge dont parle RTE est le résultat d'une simulation, comparée au critère public de
sécurité d'approvisionnement, une espérance de trois heures de défaillance par an
{{source:rte-bp2025-fonctionnement|p. 2}}. Dans son Bilan prévisionnel 2025, RTE évaluait les
marges de l'hiver 2026-2027 à {{marge_rte_hiver_2026_2027}} par rapport à ce critère, avant la
baisse de disponibilité nucléaire prévue pour cet hiver : la synthèse que RTE publie en
novembre 2026 ne donne plus de marge en GW {{source:rte-hiver-2026-2027|p. 15}}.

Pour une consommation plate, rapprocher la puissance réglée plus haut de ces marges est
légitime. Dans un calcul d'adéquation, ajouter X GW consommés en permanence revient à retirer
X GW de capacité toujours disponible : une consommation plate retire à peu près sa puissance à
la marge. C'est un rapprochement de ce site : RTE n'écrit pas cette équivalence pour la
consommation, mais il fait le même passage dans l'autre sens, en traduisant une hausse de la
pointe en besoin de capacité {{source:rte-bp2025-fonctionnement|p. 25}}. L'équivalence cesse
d'être exacte dès que la consommation n'est pas plate (montée en charge, report ou effacement
aux heures de pointe). Avec un effacement, le simulateur montre où la
consommation ajoutée se retire ; il ne sait pas dire combien de marge cela rend : seul un
calcul probabiliste, comme celui de RTE, le dirait.

## Ce que ce calcul ne dit pas

- ::: inclure limite-froid :::
- **Le système change.** Les années observées ne sont pas le système dans lequel arriveraient
  ces consommations : d'autres usages s'électrifient, le charbon ferme, le solaire grandit et
  déplace les heures de surplus.
- **Les stocks.** L'hydraulique de lac et les stations de pompage apportent de la puissance aux
  heures tendues, mais sur une quantité d'eau limitée : sur un épisode long, leur puissance
  n'est pas disponible à toute heure.
- ::: inclure limite-ecretement :::
- **La pointe exacte.** Les calculs sont à l'heure, hors Corse. RTE donne une pointe de
  {{pointe_conso_2025}} pour 2025, Corse comprise, au pas de la demi-heure ; la moyenne horaire
  de la même matinée est plus basse.
- **Les données absentes.** Une heure où une série manque n'entre pas dans le calcul qui en a
  besoin (le nombre d'heures retenues est affiché) ; rien n'est imputé.
