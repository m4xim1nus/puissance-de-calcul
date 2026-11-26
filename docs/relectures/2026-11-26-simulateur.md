# Relecture adverse : simulateur v1 (26/11/2026)

Relecture « lectrice experte » (marchés de l'électricité, modélisation
énergétique) avant publication de la page `/simulateur`, sur le commit
`feef8f9`. Matériau relu : `docs/SIMULATEUR.md` ; la page construite et
servie en local (`npm run build`, `npm run preview`), lue en navigateur
headless sur seize scénarios (2015, 2018, 2022, 2024, 2025 ; X = 0 ;
0,1 ; 1 ; 5 ; 10 ; 20 GW ; effacement 0, 1, 100 et 500 h ; adresse
invalide), avec captures, dont une à 390 px de large ;
`site/src/lib/simulateur/` (`en-tete.md`, `lecture.md`, `phrases.ts`,
`format.ts`, `moteur.ts`, `Simulateur.svelte`, `etat.ts`, `csv.ts`) ;
`pipeline/pc/quand.py` (`simuler`, `effet_charge`, `profil_effacement`,
`LIMITES_J`) ; `pipeline/tests/cas_quand.json` ;
`data/export/horaire/2015.csv` à `2025.csv` ; `data/export/chiffres.json`
(entrée `marge_rte_hiver_2026_2027`). Contexte :
`docs/relectures/2026-11-26-quand.md` (points F1 à F6, P1 à P12) et la
version corrigée de `docs/enquetes/quand.md`, en cours dans la copie de
travail.

## Verdict

**Publiable après corrections.** Le calcul est juste : les tests
vitest du simulateur passent (24/24, parité avec la référence), et mon
recalcul indépendant tombe sur chaque valeur affichée, dans trois
scénarios avec effacement (tableau ci-dessous). Le problème est ailleurs.
Le simulateur reprend **mot pour mot** trois des raisonnements que la
relecture de « Quand ? » a jugés fautifs : le seuil fixé sur un seul
maximum (F1), le plafond lâche et sans contrainte d'énergie du nucléaire
disponible non produit (F2, F3) et la causalité attribuée aux
exportations (F4). Le texte de « Quand ? » est en cours de correction,
mais `lecture.md`, `phrases.ts` et `en-tete.md` ne le sont pas. Une
fois les deux pages publiées, elles se contrediraient. S'y ajoutent
quatre défauts propres au simulateur : les indicateurs de prix ne
dépendent pas de X pour un profil plat, ce que la page ne dit pas (SF5) ;
l'optimisme de l'effacement est mal circonscrit (SF4) ; le résultat le
plus solide, le rapprochement avec les marges de RTE, manque dans les
résultats (SF6) ; et les phrases sont mal tournées dans quelques cas
limites (forme).

## Recalculs indépendants

Recalcul en Python pur (module `csv`) depuis `data/export/horaire/AAAA.csv`,
sans `quand.py` ni le moteur du site : RN = consommation − éolien − solaire
− nucleaire_disponible ; J = max(0, nucleaire_disponible − nucleaire) ;
charge = X sauf aux N heures de RN la plus élevée (RN décroissante, puis
heure croissante).

| Scénario | Grandeur | Recalcul | Affiché | Accord |
|---|---|---|---|---|
| 2025, 5 GW, 100 h | énergie ajoutée | 43,30 TWh (8 660 h × 5 GW) | 43,3 TWh | oui |
| | seuil d'effacement (RN de la 100e heure) | 17 930 MW | 17,9 GW | oui |
| | part dans J ; énergie | 0,527 ; 22,81 TWh | au plus 53 % ; 22,8 TWh | oui |
| | heures où J couvre la charge ; solde moyen | 1 939 h ; −9 176 MW | 1 939 h ; 9,2 GW exportés | oui |
| | heures au-delà du maximum ; sans effacement | 0 ; 4 | 0 ; 4 | oui |
| | part prix ≤ 0 ; < 0 | 0,0845 ; 0,0592 | 8 % ; 6 % | oui |
| | prix pondéré ; sans effacement | 59,66 ; 61,07 €/MWh | 59,7 ; 61,1 €/MWh | oui |
| 2022, 20 GW, 500 h | énergie ; part J ; énergie J | 165,2 TWh ; 0,080 ; 13,23 TWh | 165,2 ; 8 % ; 13,2 | oui |
| | au-delà du maximum ; sans effacement | 965 h ; 1 465 h | 965 ; 1 465 | oui |
| | nouveau maximum | 44 132 MW, 08/12/2022 0 h (Paris) | 44,1 GW, 8 déc. 2022, 0 h | oui |
| | prix pondéré ; sans effacement | 269,23 ; 275,88 €/MWh | 269,2 ; 275,9 | oui |
| 2018, 5 GW, 100 h | seuil ; part J ; heures couvertes ; solde | 25 735 MW ; 0,385 ; 403 h ; −8 907 MW | 25,7 GW ; 38 % ; 403 h ; 8,9 GW | oui |
| | prix pondéré ; sans effacement | 49,64 ; 50,20 €/MWh | 49,6 ; 50,2 | oui |
| 2025, sans effacement | 1 / 10 / 20 GW : au-delà du maximum | 1 / 36 / 450 h | idem | oui |
| 2024, 10 GW | au-delà du maximum ; part J | 130 h ; 0,278 | 130 h ; 28 % | oui |
| 2025, X = 0 | toutes grandeurs | énergie 0 ; parts et prix absents | « — », « Aucune consommation ajoutée » | oui |

Aucun écart. Les heures valides (8 757 sur 8 760 en 2025 ; 2 par an
avant ; 96 heures sans prix en 2015) sont celles qu'affiche la ligne de
couverture.

## Points de fond

### SF1. Exportations : la page reprend l'affirmation F4, et la renforce

*Endroits* : `phrases.ts`, détail de la tuile « Dans le nucléaire
disponible non produit » : « Quand ce nucléaire couvrirait toute la
consommation ajoutée (1 939 heures), la France exportait en moyenne
9,2 GW : une partie serait d'abord servie par moins d'exportations. » ;
`lecture.md`, paragraphe « Au plus », troisième raison (« si bien qu'une
consommation ajoutée serait d'abord servie, en partie, par moins
d'exportations ») ; `en-tete.md`, puce « Les échanges et les voisins »
(« serait servie par moins d'exportations ou plus d'importations ») ;
`LIMITES_J` dans `quand.py` (exporté).

*Problème* : c'est F4 tel quel. Que la France exporte à ces heures ne dit
pas qui servirait la charge ajoutée. Si les interconnexions sont
saturées, les exportations restent au plafond, et ce sont le nucléaire
qui module ou les EnR moins arrêtées qui servent la charge. Sinon, la
réponse se répartit sur le merit order de la zone couplée. La tuile
aggrave le défaut : elle met le constat (solde moyen) et la conclusion
causale dans une même phrase, sous un chiffre, à chaque réglage. Le
texte corrigé de « Quand ? » a retiré cette causalité ; le simulateur la
garde.

*Correction proposée* : tuile, « À ces heures, la France exportait en
moyenne 9,2 GW. Qui servirait la consommation ajoutée (plus de
nucléaire, moins d'EnR arrêtées, moins d'exportations) dépend de la
saturation des interconnexions, que ce site ne calcule pas. » ;
`lecture.md`, reprendre le paragraphe corrigé de « Quand ? » (« Qui
servirait réellement cette consommation… ») et retirer la troisième
raison du « au plus » ; `en-tete.md`, « pourrait être servie » ;
`LIMITES_J`, même correction (la référence exporte ce texte).

### SF2. Nucléaire disponible non produit : plafond lâche (F2) et sans contrainte d'énergie (F3)

*Endroits* : tuile « Dans le nucléaire disponible non produit » (« au
plus 87 % […] soit au plus 7,6 TWh de production nucléaire en plus sur
l'année ») ; `lecture.md`, paragraphe « Au plus ».

*Problème* : (a) Le **réglage par défaut** (1 GW, 2025) affiche « au plus
87 % », le chiffre que la relecture de « Quand ? » a montré dominé par
le plancher de J. J n'est jamais nul, même aux heures chères (0,3 GW en
moyenne sur les 100 heures tendues de 2025). Avec le plancher de 1 GW
retenu dans le texte corrigé de « Quand ? », les parts de 2025 tombent
de 87 / 52 / 32 / 17 % à **65 / 39 / 24 / 12 %** pour 1 / 5 / 10 /
20 GW (mon recalcul). (b) La tuile donne l'énergie (« au plus 22,8 TWh
de production nucléaire en plus ») sans dire ce qu'elle suppose. Ajoutée
à la production observée, elle donne pour 2025 : 395,7 TWh à 5 GW,
402,0 TWh à 20 GW (372,9 TWh observés). C'est 25 à 50 TWh au-dessus
des 350 à 370 TWh que projette l'exploitant. En **2015**, 5 GW donnent
416,4 + 22,9 = **439 TWh**, au-dessus de toute production annuelle du
parc (record de l'ordre de 430 TWh au milieu des années 2000, de mémoire :
à sourcer dans les bilans RTE avant de le citer). Le simulateur laisse
choisir ces années sans signaler la contrainte du combustible et des
arrêts. (c) La deuxième raison du « au plus » (« une baisse de production
pour économiser le combustible déplace de l'énergie dans le temps ») est
juste, mais la conclusion n'en est pas tirée.

*Correction proposée* : dans la tuile, une fourchette (2025, 5 GW sans
effacement : « entre 39 et 52 % », avec et sans plancher de 1 GW,
l'hypothèse du texte corrigé de « Quand ? »), et une phrase calculée : « Production nucléaire de
l'année ainsi portée à 395,7 TWh (observée : 372,9 TWh ; prévue par
l'exploitant pour 2026-2027 : 350 à 370 TWh). » Dans `lecture.md`,
reprendre les deux paragraphes corrigés de « Quand ? » (« Ce plafond est
lâche… », « En énergie, la limite est plus nette encore… »). Le plancher
peut devenir un réglage en v2.

### SF3. « Heures au-delà du maximum observé » : F1 reproduit, et visible dès l'ouverture

*Endroits* : tuile « Heures au-delà du maximum observé » (`phrases.ts`) ;
`lecture.md`, « Le maximum observé » ; légende du graphique ;
`en-tete.md`, puce « Le risque de défaillance ».

*Problème* : le seuil reste le maximum d'une seule année, donc d'une
seule heure. Conséquences visibles :

- au **réglage par défaut** (1 GW, 2025), la page affiche « 1 heure »,
  « Nouveau maximum : 32,4 GW » et « il faudrait effacer au moins
  1 heure ». C'est vrai pour toute valeur de X > 0 : l'heure du maximum se
  dépasse elle-même (0,1 GW donne aussi 1 heure). C'est un artefact,
  affiché en premier ;
- le sélecteur d'année invite à comparer : 130 h en 2024 contre 36 h en
  2025 pour 10 GW, alors que le maximum de 2024 (29,6 GW) est plus bas.
  L'indicateur mesure la forme du sommet de la monotone ;
- le maximum de 2015 à 2025, 38,6 GW (27/02/2018, 19 h), n'apparaît
  nulle part. Pourtant c'est lui qui remet l'échelle en place : 2025
  avec 10 GW ne le dépasse que 2 h ; avec 20 GW, 83 h, et le nouveau
  maximum (51,4 GW) le dépasse de 12,8 GW. Ce dernier résultat est fort,
  et la page ne le montre pas.

Le texte corrigé de « Quand ? » ajoute ce maximum pluriannuel ; le
simulateur ne l'a pas.

*Correction proposée* : dans la tuile, une seconde ligne « au-delà du
maximum 2015-2025 (38,6 GW, 27/02/2018) : N heures » ; quand le compte
annuel vaut 1, écrire « 1 heure : celle du maximum lui-même » ; dans
`lecture.md`, reprendre la phrase corrigée de « Quand ? » (« Ce décompte
tient beaucoup à une seule matinée… c'est demander au système ce qu'il
n'a fourni que dans ses pires années »). Calculer aussi « il faudrait
effacer au moins N heures » par rapport au maximum pluriannuel.

### SF4. Effacement : « prévision parfaite » circonscrit trop vaguement

*Endroits* : tuile du maximum (« Avec une prévision parfaite,
l'effacement suffit à ne jamais le dépasser ») ; `Simulateur.svelte`,
raison du réglage (« c'est une borne optimiste ») ; `lecture.md`,
« L'effacement » (« une borne optimiste de ce qu'un effacement de ce
nombre d'heures apporte »).

*Problème* : (a) **Circularité.** Les heures effacées sont par
construction celles que compte l'indicateur. « 0 heure » est garanti dès
que N atteint le nombre d'heures au-delà du maximum sans effacement. Le
résultat ne montre rien de plus. (b) **Ce que « prévision parfaite »
recouvre.** Prévoir la charge résiduelle du lendemain est assez facile.
La vraie difficulté est de savoir, en janvier, si une heure sera parmi
les N plus tendues de l'année, avec un budget d'heures annuel. Une règle
simple montre l'écart : effacer dès que RN dépasse la N-ième valeur de
l'année précédente, jusqu'à épuisement du budget. Calcul de cette
relecture, X = 5 GW, N = 100 h :

| Année jouée (seuil de l'année) | Prévision parfaite | Règle de seuil | Sans effacement |
|---|---|---|---|
| 2024 (seuil 2023 : 27,9 GW, atteint 11 h) | 0 h | 31 h | 42 h |
| 2022 (seuil 2021 : 29,4 GW) | 0 h | 19 h | 50 h |
| 2024 (seuil 2025 : 17,9 GW) | 0 h | 12 h | 42 h |
| 2025 (seuil 2024 : 20,6 GW) | 0 h | 0 h | 4 h |

L'écart entre la borne et une règle réaliste peut atteindre la majeure
partie de l'effet sans effacement. (c) **« Borne » de quoi ?** Pour
l'indicateur du maximum, c'est une borne exacte. Pour la sécurité
d'approvisionnement, non : les heures de RN la plus élevée d'une année
observée ne sont pas les heures où se concentre le risque simulé par RTE,
qui dépend des stocks d'eau, des importations et de centaines d'années
climatiques. Pour les prix, le classement par RN n'est pas le classement
par prix. En 2025, l'écart est faible (59,5 €/MWh avec un effacement
calé sur les prix, contre 59,7), mais ce n'est pas une borne par
construction. (d) L'énergie effacée est **perdue**, pas reportée (la
tuile « Énergie ajoutée » la retranche) : la page ne le dit pas. Si le
calcul part sur un autre site, c'est cohérent ; s'il est différé, non.

*Correction proposée* : « Par construction, les heures effacées sont
celles que compte cet indicateur : avec un budget d'heures suffisant,
il tombe à zéro. » Dans `lecture.md`, préciser « borne optimiste pour
l'indicateur du maximum observé ; ni pour le risque de défaillance, ni
pour les prix », et donner un ordre de grandeur de l'écart avec une
règle réaliste (le tableau ci-dessus, ou mieux : la règle de seuil comme
variante calculée en v2). Écrire que l'énergie effacée n'est pas reportée
sur d'autres heures. Dire aussi que la vraisemblance de 500 heures
d'effacement total d'un data center n'est pas discutée.

### SF5. Prix observés : pour un profil plat, les deux tuiles ne dépendent pas de X, et la page ne le dit pas

*Endroits* : tuiles « Énergie consommée à prix nul ou négatif » et « Prix
moyen pondéré par la consommation ajoutée » ; `lecture.md`, « Les prix ».

*Problème* : (a) Pour une consommation plate, la première tuile est la
part des heures à prix ≤ 0, et la seconde le prix moyen de l'année.
Elles affichent exactement les mêmes valeurs pour 0,1 GW et pour
20 GW : 8 % et 61,1 €/MWh en 2025. La lectrice le verra en deux
réglages, et la page devrait le dire avant elle. (b) Au-delà de quelques
GW, l'indicateur de prix nuls ou négatifs décrit des heures qui
n'existeraient plus. Sur les 732 heures à prix ≤ 0 de 2025, J vaut en
moyenne 9,0 GW, les exportations 6,7 GW et le pompage 1,9 GW. J couvre
X à 86 % de ces heures pour 5 GW, à 39 % pour 10 GW et à aucune pour
20 GW. Avec 20 GW, la plupart de ces heures n'auraient plus été à prix nul
ou négatif. « Certains auraient été plus élevés » sous-estime l'effet.
(c) **La page suggère-t-elle un coût ?** En partie. `lecture.md` dit
bien « pas une facture », mais sous les résultats. La tuile affiche un
montant en €/MWh en gros caractères, sous un intitulé qui est, dans le
vocabulaire du marché, un prix capté de consommation. Surtout, le
comparateur « Sans effacement : 61,1 €/MWh » transforme l'écart (1,4 €/MWh
à 5 GW et 100 h) en économie implicite. Or cet écart ne dit rien du
gain d'un effacement réel, qui dépendrait d'un prix déformé par la
charge elle-même.

*Correction proposée* : pour X > 0 sans effacement, écrire dans les
deux tuiles « pour une consommation plate, c'est la part des heures à
prix nul ou négatif / le prix moyen de l'année, quelle que soit la
puissance » ; retirer le comparateur « Sans effacement », ou le
remplacer par « l'écart tient au calendrier des heures effacées, ce
n'est pas une économie » ; ajouter, quand X dépasse le J moyen des
heures à prix ≤ 0 de l'année (9,0 GW en 2025), « à ce niveau, la plupart
de ces heures n'auraient plus été à prix nul ou négatif ». Renommer la
tuile, par exemple « Prix observé moyen aux heures de consommation », et
remonter « pas une facture » dans son détail.

### SF6. Le résultat le plus solide manque : le rapprochement avec les marges de RTE

*Endroits* : tuiles ; `lecture.md`, « Les marges de RTE : une
approximation du site » ; `docs/SIMULATEUR.md`, résultat 6.

*Problème* : les tuiles mettent en avant l'indicateur le plus fragile
(le maximum d'une année, SF3). Le passage le mieux fondé, qui dit
qu'une consommation plate de X GW retire environ X GW de marge, reste
dans le texte sous les résultats. Ce texte est d'ailleurs contradictoire :
son titre parle d'« une approximation du site », alors qu'il écrit que
l'équivalence vaut, dans un calcul d'adéquation, pour une charge plate
(« revient à retirer X GW de capacité toujours disponible »). Le texte
corrigé de « Quand ? » dit « légitime », et « à peu près ». Enfin,
l'entrée `marge_rte_hiver_2026_2027` est bien une « marge en capacité
équivalente » : le rapprochement est dans la bonne unité.

*Correction proposée* : ajouter une ligne de résultat, calculée sans
effacement : « Une consommation plate de 5 GW retire environ 5 GW aux
marges de 8 à 10 GW évaluées par RTE pour l'hiver 2026-2027, avant la
baisse de disponibilité nucléaire prévue pour cet hiver. » Avec
effacement : « Ce que l'effacement rend de marge n'est pas calculable
ici. » Renommer la section « Les marges de RTE : un rapprochement » et
aligner son texte sur celui, corrigé, de « Quand ? ».

## Points de précision

**SP1. Réseau local.** `en-tete.md` : « dont la capacité d'accueil n'est
pas publiée ». C'est l'affirmation absolue relevée en P11, que
« Quand ? » a corrigée (« à notre connaissance, aucune capacité d'accueil
en consommation par poste n'est publiée en open data »). Aligner.

**SP2. Périmètre de X.** La consommation éCO2mix est « pertes
comprises ». Ajouter X à cette série revient à compter les pertes de
réseau dans X. Le préciser dans la raison du réglage : « au périmètre de
la consommation nationale, pertes de réseau comprises ».

**SP3. Ce qui manque dans « Ce que le simulateur ne modélise pas ».**
(a) La montée en charge progressive d'un parc (dite dans `SIMULATEUR.md`,
pas sur la page). (b) La forme réelle de la consommation d'un data
center : le refroidissement la rend un peu thermosensible **en été**, ce
qui n'est pas plat. (c) La tenue des data centers aux creux de tension :
des déconnexions simultanées de charges de plusieurs centaines de MW
sont documentées à l'étranger (incident de juillet 2024 en Virginie,
environ 1,5 GW, rapport NERC, à vérifier avant de le citer). C'est un
risque d'exploitation, hors de l'adéquation. (d) Le carbone : aucun
chiffre d'émissions n'est calculé, ni moyen ni marginal. Le dire en une
ligne évite que la lectrice le cherche.

**SP4. Froid extrême.** `lecture.md` reprend « Onze années observées ne
contiennent pas forcément les froids les plus sévères » : P8 n'est pas
appliqué. Écrire le fait (aucune vague de froid du type de février 2012
dans 2015-2025), avec la pointe de 2012 sourcée chez RTE.

**SP5. Monotone avec effacement.** Sur le zoom, aux premiers rangs, la
courbe « avec » se confond avec la courbe observée. Les heures effacées
gardent en effet leur RN observée, qui dépasse RN + X des autres heures.
C'est juste, mais déroutant : ajouter à la légende « les heures effacées
gardent leur charge résiduelle observée ; elles occupent le haut de la
courbe ».

## Points de forme

**Fo1. Accords.** Avec 1 heure d'effacement : « sauf pendant les
1 heure de charge résiduelle… », « moins 1 heure effacées »
(`phrases.ts`). Traiter le singulier.

**Fo2. X = 0.** La tuile affiche « Le maximum reste celui observé,
31,4 GW. Ce n'est pas une défaillance. » La seconde phrase n'a de sens
que s'il y a dépassement : ne l'écrire que dans ce cas. Avec X = 0 et un
effacement non nul, le scénario ne signale pas que l'effacement est
sans objet.

**Fo3. Décimales.** `formaterNombre` supprime le zéro final : « 28 TWh »,
« 29 TWh », « 58 €/MWh » s'affichent à côté de « 29,1 TWh » et
« 61,1 €/MWh ». Garder un nombre fixe de décimales par unité (« 28,0 TWh »,
« 58,0 €/MWh »).

**Fo4. Phrase conditionnelle.** « Quand ce nucléaire couvrirait toute la
consommation ajoutée (1 939 heures), la France exportait… » mêle le
conditionnel et l'imparfait. Proposer : « Aux 1 939 heures où il aurait
suffi à couvrir toute la consommation ajoutée, la France exportait… »
(voir SF1 pour la suite).

## Lisibilité pour un non-spécialiste

Le haut de page est clair : ce que fait l'outil, ce qu'il ne fait pas,
trois réglages justifiés, l'adresse qui porte le scénario. Les
résultats décrochent : « charge résiduelle » et « nucléaire disponible
non produit » ne sont définis qu'**après** les tuiles (`lecture.md`),
et « day-ahead » ou REMIT ne le sont pas du tout. Deux lignes de
définition au-dessus des tuiles, ou une infobulle sur leur titre,
suffiraient. La tuile du nucléaire, la plus dense (une part, une énergie,
un nombre d'heures, un solde), gagnerait à être coupée en deux. Le « au
plus » en tête de valeur fonctionne bien. À 390 px, la page ne défile pas
horizontalement et les tuiles passent sur une colonne.

## Vérification des corrections (26/11/2026)

Vérification point par point sur le commit `383fd5e` (agent Opus, distinct
de la relecture). Matériau : page construite et servie en local
(`npm ci`, `npm run build`, `npm run preview`), lue en navigateur headless
(Playwright) avec captures pleine page de sept scénarios : défaut (2025,
1 GW) ; 2025, 10 GW, 100 h d'effacement ; 2022, 20 GW ; 2025, 5 GW ; 2025,
10 GW ; 2015, 5 GW ; 2025, X = 0 avec 50 h d'effacement. Sources :
`en-tete.md`, `lecture.md`, `phrases.ts`, `format.ts`, `references.ts`,
`src/lib/server/simulateur.ts`, `LIMITES_J`, `docs/SIMULATEUR.md`,
`making-of/`, `BACKLOG.md`. La relecture n'est pas refaite.

**Recalculs** (Python pur depuis `data/export/horaire/2025.csv`) : part de
5 GW dans J avec plancher de 1 GW 0,3864 (affiché 39 %) ; 1 GW 0,6491
(65 %) ; 10 GW 0,2381 (24 %) ; énergie dans J 7,604 / 22,844 / 28,044 TWh
pour 1 / 5 / 10 GW (affiché 7,60 / 22,8 / 28,0 TWh) ; heures où RN + 10 GW
dépasse 38 582 MW : 2 (affiché 2) ; au-delà du maximum de 2025 : 36 (36).
Aucun écart.

| Point | Statut | Où |
|---|---|---|
| SF1 exportations | corrigé | tuile « Heures où ce nucléaire suffirait » (« c'est un constat. Qui servirait […] ce site ne sait pas encore le dire ») ; `lecture.md` « Qui servirait cette consommation » ; `en-tete.md` « Les échanges et les voisins » ; `LIMITES_J` |
| SF2 plafond lâche et énergie | corrigé | tuile « Dans le nucléaire disponible non produit » : fourchette (défaut « au plus 65 à 87 % »), énergie avec et sans plancher, production observée, RTE publiée, prévision de l'exploitant pour la dernière année ; `lecture.md` « Au plus » et « En énergie ». Pour 2015 (5 GW : 416,4 + 22,9 TWh), seule la phrase générique sur le combustible avertit ; le record historique n'est pas cité, faute de source (la relecture demandait de le sourcer d'abord). Acceptable |
| SF3 seuil sur un seul maximum | corrigé | deux tuiles (maximum de l'année, maximum 2015-2025) ; « 1 heure […] l'heure du maximum se dépasse elle-même, et c'est la seule ici » ; « il faudrait effacer au moins N heures » pour les deux seuils ; `lecture.md` « Deux maxima ». **Reste** : N1 et N2 |
| SF4 effacement | corrigé, règle réaliste au backlog | tuile du maximum (« Par construction, les heures effacées sont celles que compte cet indicateur […] ne dit rien d'un effacement réel ») ; énergie effacée « perdue » (tuile « Énergie ajoutée ») ; `lecture.md` « L'effacement » (borne basse, ni défaillance ni prix, vraisemblance non discutée) ; règle de seuil connue à l'avance renvoyée au backlog avec raison (`DECISIONS.md`, `BACKLOG.md`) |
| SF5 prix | corrigé | prix moyen pondéré et comparateur supprimés ; tuile prix nuls : « pas une facture », « quelle que soit la puissance », part des heures à prix ≤ 0 couvertes par J (100 % à 1 GW, 86 % à 5 GW, 39 % à 10 GW en 2025) ; `lecture.md` « Les prix ». Titre de tuile non renommé, sans objet une fois le prix moyen retiré |
| SF6 marges de RTE | corrigé | tuile « Marge de sécurité d'approvisionnement » (« à peu près X GW en moins » ; « non calculable ici » avec effacement) ; section renommée « Les marges de RTE : un rapprochement ». **Reste** : N4 (p. 16) |
| SP1 réseau local | corrigé | `en-tete.md` « à notre connaissance » |
| SP2 pertes | corrigé | `en-tete.md` « Les pertes de réseau » |
| SP3 limites manquantes | corrigé | `en-tete.md` : montée en charge et variations saisonnières, perturbations du réseau (sans affirmation non sourcée, conformément au journal), carbone |
| SP4 froid extrême | **non traité** | `lecture.md` garde « Onze années observées ne contiennent pas forcément les froids les plus sévères » ; même absence que P8 de « Quand ? » ; ni écarté ni au backlog |
| SP5 monotone avec effacement | corrigé | légende : « Les heures effacées gardent leur charge résiduelle observée : elles se rangent en haut de la courbe « avec » » |
| Fo1 accords | corrigé en partie | « l'heure de charge résiduelle », « 1 heure effacée » traités ; **reste** « il faudrait effacer au moins 1 heure, en les connaissant à l'avance » (scénario par défaut, tuiles des deux maxima) |
| Fo2 X = 0 | corrigé | « Aucune consommation ajoutée : le maximum reste 31,4 GW » ; scénario « l'effacement est sans objet » |
| Fo3 décimales | corrigé | `format.ts` `twh` : 8,76 / 28,0 / 1,00 TWh |
| Fo4 conditionnel | corrigé | « où le nucléaire disponible non produit aurait suffi à couvrir toute la consommation ajoutée. La France y exportait… » |
| Lisibilité | corrigé | définitions (charge résiduelle, nucléaire disponible non produit, prix day-ahead) au-dessus des tuiles ; tuile du nucléaire coupée en deux. REMIT reste non défini (cf. Fo8 de « Quand ? ») |

### Points de fond nouveaux ou résiduels

- **N1. Tuile « maximum 2015-2025 » : « c'est demander au système ce qu'il
  n'a fourni que dans ses pires années » — faux dans cette tuile.**
  `phrases.ts`, bloc 4, écrit quand `auRef > 0`, donc précisément quand la
  charge résiduelle dépasse **tout** ce que le système a fourni de 2015 à
  2025. Exemple affiché : 2022, 20 GW, 1 349 heures, « Le nouveau maximum le
  dépasse de 19,5 GW. […] c'est demander au système ce qu'il n'a fourni que
  dans ses pires années ». Il ne l'a jamais fourni. Dans « Quand ? », la
  phrase vient après le dépassement du maximum **de l'année**, où elle est
  juste. Remplacer, dans cette tuile, par « c'est demander au système plus
  qu'il n'a jamais fourni de 2015 à 2025 », et ne garder la phrase actuelle
  que dans la tuile du maximum de l'année.
- **N2. Légende de la monotone : « Au-dessus d'un maximum observé, le
  système serait allé là où il n'a pas été vu fonctionner ».**
  `MonotoneAvantApres.svelte` l. 105. C'est la formule que F1 jugeait
  fausse, et elle l'est pour la ligne « maximum de 2025 » tracée sur le même
  graphique (31,4 GW, très en deçà de 2018 et 2022). La réserver au maximum
  2015-2025.
- **N3. « Ne tombe jamais à zéro »** (`lecture.md`, « Au plus ») : J vaut 0
  pendant 183 heures en 2025, dont 14 des 278 heures à plus de 150 €/MWh.
  C'est la moyenne (0,5 GW) qui ne tombe pas à zéro. Même correction que
  dans « Quand ? ».
- **N4. p. 16 du paramétrage du mécanisme de capacité, retirée de
  « Quand ? », gardée ici.** `lecture.md` : « pour RTE, la contribution d'une
  consommation au risque de défaillance dépend de son profil (p. 16) ». La
  page (relue dans le PDF pour cette vérification) décrit une « analyse de
  sensibilité de la contribution au risque de défaillance d'un profil de
  consommation non thermosensible comparativement à celui d'une consommation
  purement thermosensible », pour calculer un vecteur de températures. La
  paraphrase tient, mais la page parle de thermosensibilité et sert ici
  d'appui à « l'équivalence cesse d'être exacte dès que la consommation
  n'est pas plate » (montée en charge, effacement), dont elle ne dit rien.
  C'est l'usage que F5 et `ERREURS.md` ont corrigé dans « Quand ? » : les deux
  pages divergent. Retirer la citation, ou la restreindre à « une
  consommation sensible au froid pèse plus que sa valeur moyenne ».
- **N5. Phrases de fond tapées à la main dans `phrases.ts`.** « Le système
  l'a couvert avec d'autres moyens : du charbon et du fioul, et des
  importations importantes » (gardée par la date du maximum, ce qui limite
  le risque) et « avant la baisse de disponibilité nucléaire prévue pour cet
  hiver » recopient « Quand ? ». Déjà au backlog (« tirer les phrases de fond
  d'une source unique ») : pas bloquant, mais c'est ainsi que N1 s'est
  produit.

### Verdict

**Non publiable en l'état, publiable après quatre corrections de texte sans
nouvelle relecture de fond.** SF1 à SF6, les points de précision (sauf SP4)
et de forme (sauf un reste de Fo1) sont traités, et les calculs restent
justes. Mais N1 est une phrase fausse affichée à chaque scénario qui dépasse
le maximum 2015-2025, N2 réintroduit F1 dans la légende du graphique, N3 est
faux heure par heure, N4 garde l'usage de la p. 16 que « Quand ? » a corrigé.
SP4 (froid extrême) est à traiter ou à renvoyer explicitement au backlog,
avec P8 de « Quand ? ».
