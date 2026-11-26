---
titre: À toi
mise_a_jour: 2026-11-26
---

<!--
Onglet « À toi » (exigence du brief) : missions à faire soi-même avec
Claude Code, par difficulté croissante. Tutoiement, ton direct, zéro
jargon de développeur. Chaque mission dit ce qu'il faut, quoi demander,
et ce qu'il faut vérifier soi-même : Claude se trompe, ce site le
montre (making-of, « Erreurs »).
Aucun chiffre du site n'est recopié ici : les missions renvoient aux pages.
-->

Ce site a été fait par Claude Code, un assistant qui lit, calcule et écrit
du code dans un dossier de ton ordinateur, sous ta direction. Tu peux
refaire une partie du travail toi-même, sans savoir programmer. Les
missions vont de la plus simple à la plus exigeante. Pour chacune : ce
qu'il te faut, quoi demander, et ce que tu dois vérifier toi-même, parce
que Claude se trompe aussi (le [making-of](/making-of#erreurs) en tient
la liste).

**Pour commencer.** Installe Claude Code (la marche à suivre est sur
[claude.com/claude-code](https://claude.com/claude-code)), crée un
dossier vide pour tes essais, ouvre un terminal dans ce dossier et tape
`claude`. Ensuite, tu écris en français, comme à quelqu'un. Une règle
pour toutes les missions : demande toujours **d'où vient chaque
chiffre** (source, date, lien) et **dans quelle unité** il est.

## 1. Ta propre consommation, heure par heure

**Il te faut** : un compteur Linky et un compte sur l'espace client
d'Enedis. Dans cet espace, active l'enregistrement de ta consommation
horaire (la « courbe de charge »), puis télécharge tes mesures en
fichier CSV. Selon la date d'activation, tu n'auras peut-être que
quelques jours ou quelques semaines : c'est assez pour commencer.

**Demande à Claude** :

> Voici l'export de ma courbe de charge Linky. Dis-moi d'abord ce que
> contient chaque colonne et dans quelle unité, sans rien calculer.
> Ensuite, récupère les prix de gros heure par heure de la zone France
> pour les mêmes jours : sur pdc.technoperchoir.fr (fichiers
> /donnees/horaire/AAAA.csv, années closes seulement) si mes mesures
> sont d'une année close, sinon sur energy-charts.info (prix day-ahead,
> zone France), et dis-moi d'où viennent ceux que tu as pris. Puis
> dis-moi quelle part de ma consommation tombe aux heures où le prix
> était le plus bas, et aux heures où il était le plus haut.

**Vérifie toi-même** :

- l'unité. Une courbe de charge donne souvent une **puissance moyenne**
  par demi-heure (en W), pas une énergie : chaque valeur multipliée par
  0,5 heure donne des Wh, à diviser par 1 000 pour des kWh. Additionne
  une journée à la main et compare avec ta consommation affichée par
  Enedis pour ce jour-là ;
- l'heure. Le fichier du site est en heure UTC, et chaque ligne marque
  le **début** de l'heure ; celui d'Enedis est en heure française.
  Demande à Claude si l'heure d'Enedis marque le début ou la fin de
  chaque demi-heure, comment il a aligné les deux, et regarde ce qu'il
  fait le jour d'un changement d'heure.

## 2. Une hypothèse du simulateur, dans le code du site

Le [simulateur](/simulateur) suppose qu'une partie du parc nucléaire
n'est jamais mobilisable, et ne te laisse régler ce « plancher » qu'entre
0 et 3 GW. C'est un choix du site, pas une donnée. Tu vas le changer.

**Il te faut** : le code du site, qui est public. Demande à Claude de le
récupérer :

> Télécharge le code de github.com/m4xim1nus/puissance-de-calcul dans ce
> dossier, puis explique-moi en cinq phrases comment il est organisé.
> Trouve où le simulateur limite le plancher nucléaire à 3 GW, montre-moi
> la ligne, passe la limite à 6 GW, puis lance le site sur mon ordinateur
> et donne-moi l'adresse à ouvrir.

**Vérifie toi-même** : ouvre l'adresse, règle le plancher à 5 GW, et lis
ce qui change dans les résultats. Puis demande à Claude **pourquoi** :
quelle quantité du calcul ce plancher modifie, et ce que le simulateur
ne modélise pas (il le dit sur sa page). Si son explication contredit la
page, c'est l'un des deux qui se trompe : cherche lequel.

## 3. Une conviction, contre les données

Choisis une phrase que tu crois vraie sur l'énergie. Par exemple :
« l'électricité française est toujours en surplus », « les data centers
font monter les prix », « une voiture électrique en France n'émet
presque rien ».

**Demande à Claude** :

> Voici une conviction : [ta phrase]. Ne me dis pas si elle est vraie.
> Cherche les données publiques qui pourraient la contredire, en
> sources primaires seulement (RTE, Enedis, CRE, ADEME, Eurostat,
> Agence internationale de l'énergie), avec pour chacune le lien, la
> date et l'unité. Dis-moi aussi ce qui manque pour trancher.

**Vérifie toi-même** : ouvre au moins deux des liens, et retrouve le
chiffre cité **à l'endroit indiqué**. Il arrive qu'une source existe
mais ne dise pas ce qu'on lui fait dire, ou que deux chiffres d'origine
différente soient combinés en un seul. Ce site a fait les deux avant de
les corriger : c'est dans le making-of.

## 4. Refaire un chiffre du site, depuis la source

Prends un chiffre de la page [« Quand ? »](/quand), par exemple le
nombre d'heures à prix négatif d'une année. Ne pars **pas** des
fichiers du site : pars des données publiques d'origine.

**Demande à Claude** :

> Je veux recalculer le nombre d'heures à prix négatif en France en
> 2025, à partir des données publiques d'origine (prix de l'enchère
> journalière pour la zone France). Trouve la source, télécharge-la,
> explique-moi ta méthode avant de calculer (heure ou quart d'heure,
> fuseau horaire, que fais-tu d'un prix à zéro), puis compare ton
> résultat avec celui du site pdc.technoperchoir.fr/quand.

**Vérifie toi-même** : si les deux chiffres diffèrent, ne choisis pas.
Demande à Claude d'où vient l'écart, et lis la note du site sur ce
chiffre (le petit renvoi à côté de chaque nombre) : la méthode y est
écrite. Un écart expliqué vaut mieux qu'un accord par hasard.

## 5. Chercher une erreur sur ce site

La mission la plus dure. Ce site est vérifié par des relectures
adverses, et il contient sûrement encore des erreurs.

**Demande à Claude** :

> Relis la page pdc.technoperchoir.fr/combien comme une experte des
> marchés de l'électricité qui cherche l'erreur. Pour chaque chiffre,
> ouvre la source citée dans la note et vérifie qu'elle dit bien ça, à
> la page indiquée, dans la même unité et pour le même périmètre.
> Classe ce que tu trouves : erreur de fond, imprécision, ou rien.

**Vérifie toi-même** : chaque « erreur » que Claude trouve, vérifie-la
dans la source avant d'y croire. Ce site a déjà corrigé à tort un
passage juste, sur la seule foi d'un signalement : c'est consigné dans
le making-of. Si l'erreur résiste à ta vérification, le code et les
données sont publics sur
[github.com/m4xim1nus/puissance-de-calcul](https://github.com/m4xim1nus/puissance-de-calcul) :
signale-la là-bas.
