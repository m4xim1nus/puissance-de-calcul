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
se règlent ci-dessous.

## Ce que le simulateur ne modélise pas

- **Le fonctionnement du parc.** Aucune centrale n'est appelée pour servir la consommation
  ajoutée : elle s'ajoute à la charge résiduelle observée, et le simulateur regarde où elle
  tombe.
- **La formation des prix.** Le prix affiché est le prix day-ahead **observé**, formé sans
  cette consommation. Avec elle, certains prix auraient été plus élevés ; le simulateur ne
  dit pas de combien.
- **Les échanges et les voisins.** Une partie de la consommation ajoutée serait servie par
  moins d'exportations ou plus d'importations. Ce que cela change chez les voisins, et à
  quelles émissions, n'est pas calculé.
- **Le réseau local.** Tout est national. Quelques centaines de MW pèsent d'abord sur un
  poste électrique et sur ses lignes, dont la capacité d'accueil n'est pas publiée.
- **Le risque de défaillance.** RTE l'évalue en simulant des centaines de scénarios de
  météo et de disponibilité ; le simulateur rejoue une seule année observée. Dépasser le
  maximum observé de cette année n'est pas une défaillance.
