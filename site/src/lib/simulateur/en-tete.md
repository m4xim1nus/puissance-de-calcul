<!--
Texte d'en-tête de la page /simulateur, rendu au prérendu par la même chaîne que les enquêtes
(src/lib/server/enquetes.ts, rendreCorps). Aucun chiffre de source tapé à la main : un chiffre
cité s'écrit {{identifiant}} du référentiel. Ce bloc ne porte pas de note (les numéros de notes
recommenceraient dans le texte de lecture) : le prérendu le vérifie.
-->

Ce simulateur ajoute une consommation, un parc de data centers par exemple, à une année
observée du système électrique français, **heure par heure**, et montre ce qu'elle y
rencontre : les heures tendues, les heures de surplus, les prix. Il prolonge l'enquête
[« Quand ? »](/quand) : mêmes séries, mêmes définitions, mêmes limites, mais les hypothèses
se règlent dans le panneau « Hypothèses ».

## Ce que le simulateur ne modélise pas

- **Le fonctionnement du parc.** Aucune centrale n'est appelée pour servir la consommation
  ajoutée : elle s'ajoute à la charge résiduelle observée, et le simulateur regarde où elle
  tombe.
- **La formation des prix.** Le prix affiché est le prix day-ahead **observé**, formé sans
  cette consommation. Avec elle, certains prix auraient été plus élevés ; le simulateur ne
  dit pas de combien.
- **Les échanges et les voisins.** Qui servirait la consommation ajoutée (plus de nucléaire,
  moins d'éolien et de solaire arrêtés, moins d'exportations ou plus d'importations) dépend,
  heure par heure, de la saturation des interconnexions et des prix voisins. Ce site ne sait
  pas encore le dire : les données des pays voisins ne sont pas branchées.
- **Le carbone.** Aucun chiffre d'émissions n'est calculé, ni moyen ni marginal.
- **Le réseau local.** Tout est national. Quelques centaines de MW pèsent d'abord sur un
  poste électrique et sur ses lignes ; à notre connaissance, aucune capacité d'accueil en
  consommation par poste n'est publiée en open data.
- **Les pertes de réseau.** La consommation à laquelle s'ajoute X compte les pertes : X les
  inclut, le simulateur ne les calcule pas à part.
- **La forme réelle d'une consommation de data centers.** Elle est supposée plate ; la montée
  en charge d'un parc sur plusieurs années et les variations saisonnières de sa
  consommation ne sont pas représentées.
- **Le comportement lors des perturbations du réseau.** La façon dont de grandes charges
  informatiques réagissent à un creux de tension relève de l'exploitation du réseau, hors du
  calcul d'équilibre heure par heure fait ici.
- **Une vague de froid.** Le réglage « froid supplémentaire » ajoute, pendant une semaine, une
  consommation proportionnelle aux degrés réglés, avec le gradient moyen publié par RTE. Il ne
  simule ni la météo des pays voisins (un même froid peut toucher plusieurs pays), ni l'effet sur les
  importations, ni les stocks d'eau.
- **Le risque de défaillance.** RTE l'évalue en simulant de nombreux scénarios de
  météo et de disponibilité ; le simulateur rejoue une seule année observée. Dépasser le
  maximum observé de cette année n'est pas une défaillance.
