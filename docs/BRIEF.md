> **Note de publication.** Brief publié tel quel, à deux exceptions près,
> décidées par l'auteur avant la première publication (26/11/2026) : son
> prénom est remplacé par « l'auteur », et une précision sur la lectrice
> est caviardée à l'endroit marqué.

# Puissance de calcul — brief de lancement

*Nom de travail, à challenger.*

## L'idée

Un site de données sur une question simple à poser et difficile à trancher :
**le système électrique français peut-il accueillir la vague de data
centers, et à quelles conditions ?** La France vend ses data centers sur
une électricité abondante et décarbonée. C'est vrai en moyenne annuelle.
**Hypothèse de travail : la question se joue ailleurs, à l'heure, au poste
électrique et au prix.** Le site doit vérifier, chiffrer et dater, et dire
où les données contredisent l'hypothèse ou manquent. C'est un instrument
de preuve, pas un tract.

## Pour qui

D'abord pour une lectrice précise : une ingénieure, experte des marchés de
l'électricité [caviardé : précisions sur la lectrice] et de la modélisation des systèmes
énergétiques. Elle est à l'aise avec la donnée mais ne développe pas, et
elle a un esprit critique aiguisé. Elle repérera en dix secondes un
ordre de grandeur faux, une confusion entre MW et MWh ou un facteur
d'émission moyen utilisé à la place d'un facteur marginal. **Une seule
erreur de fond et le site perd toute valeur à ses yeux.** Le site reste
publiable pour un public large de professionnels de l'énergie.

Conséquences :
- pas de vulgarisation des bases (merit order, capture price, PPA, TURPE) ;
  on peut renvoyer à un glossaire replié ;
- chaque chiffre est sourcé et daté, chaque hypothèse est affichée, et
  modifiable quand c'est possible ;
- les limites et les incertitudes sont écrites, pas cachées.

## Ce qu'on attend : de l'ambition, pas un cours

Le site ne doit pas ressembler à un cours ou à une page de synthèse. Ce
qui compte :

1. **Collecter et croiser des données éparses**, hétérogènes et parfois
   pénibles à obtenir, dans un pipeline reproductible.
2. **Produire de vraies analyses** : de la modélisation simple mais juste
   (optimisation, simulation horaire), pas seulement des agrégats.
3. **Une data viz et un design de premier plan.** Cartes, profils horaires
   et heatmaps calendaires sont lisibles par une experte et beaux à
   regarder. Au moins un **module interactif signature**.

## Questions candidates (à trier, couper, compléter)

- **Combien ?** Le poids des data centers dans la consommation française
  aujourd'hui, et les trajectoires (RTE, AIE, annonces publiques).
  Distinguer les annonces, les demandes de raccordement et les mises en
  service.
- **Où ?** Carte des data centers existants et annoncés, croisée avec les
  capacités d'accueil du réseau, la production locale, les postes
  électriques et le climat (refroidissement).
- **Quand ?** Un data center consomme plat, alors que le système a des
  surplus : prix négatifs, modulation nucléaire, écrêtement. Quelle part
  d'une charge plate peut être couverte heure par heure par du
  renouvelable local et du stockage ? Que vaut une fraction de charge
  déplaçable (calculs différables) ?
- **À quel prix ?** Exposition au spot, PPA, capture prices, coût de la
  couverture horaire (logique 24/7 CFE contre appariement annuel).
- **Quel carbone ?** Facteur moyen contre facteur marginal, et effet des
  interconnexions. C'est le piège classique ; le site doit le traiter
  proprement.

**Idée de module signature** : un simulateur où l'on choisit un site, une
puissance IT, une part de flexibilité, un mix PV / éolien / batterie et un
type de contrat. Il renvoie le taux de couverture horaire, le profil de
coût et le carbone sur des années historiques réelles. Il peut être
précalculé ou résolu dans le navigateur, au choix de l'owner.

## Sources : pistes à vérifier, pas une liste close

- RTE éCO2mix et l'open data réseaux énergies (ODRÉ) : production et
  consommation par filière et par région, échanges, registre national des
  installations de production et de stockage.
- ENTSO-E Transparency Platform : prix day-ahead, production, flux
  (jeton API gratuit).
- Capacités d'accueil du réseau (Caparéseau), S3REnR, publications RTE
  sur les demandes de raccordement des grands consommateurs.
- RTE Bilan prévisionnel ; rapport de l'AIE *Energy and AI* (2025).
- Localisation des data centers : OpenStreetMap (`telecom=data_center`),
  annonces publiques (sites identifiés par l'État en 2025), presse
  spécialisée. Il n'existe probablement pas de registre ouvert ; il faut le
  dire.
- Directive européenne sur l'efficacité énergétique : obligation de
  reporting des data centers à partir de 500 kW. Vérifier ce qui est
  publié.
- Météo historique (Météo-France open data, Open-Meteo) pour le
  refroidissement et le productible PV / éolien ; PVGIS.

## Le site

- Une page d'accueil qui porte le message principal, puis les enquêtes et
  le module signature.
- **Un onglet « Making-of »** : comment le site a été construit avec Claude
  Code. Il contient :
  - un journal des sessions, avec les demandes de l'auteur citées telles
    quelles. Quand une demande est elliptique (« comme d'hab », « fais
    propre »), il faut **expliciter** ce qu'elle recouvrait ;
  - les décisions et leurs raisons, le temps passé et un ordre de grandeur
    du coût ;
  - **les erreurs de Claude**, comment elles ont été repérées et corrigées.
    C'est la section la plus importante pour un lecteur critique : ne rien
    embellir ;
  - ce brief, publié tel quel.

  Le journal est tenu **au fil de l'eau**, pas reconstruit à la fin.
- **Un onglet « À toi »** : quelques missions à faire soi-même avec Claude
  Code, par difficulté croissante. Par exemple : analyser sa propre courbe
  de charge Linky (export Enedis) ; modifier une hypothèse du simulateur
  dans le code du site ; soumettre à Claude une conviction sur l'énergie
  et lui demander les données qui la contredisent. Il faut un ton direct,
  du tutoiement et zéro jargon de dev.

## Mode de travail

- Tu es owner : stack, architecture, phasage et découpage sont à toi.
  Consulte l'auteur sur les arbitrages qui engagent le fond (périmètre des
  enquêtes, thèse de l'accueil, nom) ; pour le reste, décide et note.
- Aligne-toi sur les conventions des projets voisins dans `~/dev/`
  (`quifaitlaloi`, `leurs-voix-nos-droits`) : structure du dépôt, docs,
  build et déploiement.
- Un premier livrable doit vite être visible, puis on approfondit.
  Plusieurs enquêtes justes valent mieux que toutes les enquêtes à moitié.
- Les chiffres clés passent par des tests de cohérence : bilans qui
  bouclent, ordres de grandeur recoupés entre deux sources.
