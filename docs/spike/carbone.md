# Spike carbone : méthode et sources pour l'enquête « Quel carbone ? »


> **Annotation de Claude (26/11/2026, après vérification).** Le décompte de
> « 928 événements » pour modulation (§ 2.6) est faux comme mesure : il inclut
> 461 essais à puissance stable et 54 textes réduits à un lien. Le décompte retenu
> est de 407 événements (2019-2026), règle dans `pipeline/pc/remit.py`
> (`MOTIF_MODULATION`), rapport `docs/relectures/2026-11-26-modulation-agent.md`.
> **Relu de façon adverse le 26/11/2026** (`docs/relectures/2026-11-26-spike-carbone.md`) :
> chiffres C2 et C4 recalculés à l'identique, mais lecture causale non établie (météo
> commune), « recoupé par deux méthodes » faux en 2024-2025, « 3 à 5 fois » surévalué (2,8
> à 3,7), les trois cas de C4 ne sont pas des bornes, effet « lit d'eau » décrit à l'envers.
> Ne rien reprendre de ce rapport sans la relecture.

*Rédigé le 26/11/2026 par un agent (Opus), avec trois agents de recherche documentaire
(sources institutionnelles, littérature académique, facteurs d'émission). C'est un rapport de
travail **non relu** : rien n'est publiable sans relecture adverse. Les prototypes sont dans
`pipeline/explo/spike_carbone.py` (jetable). « Constaté » = calculé aujourd'hui sur les données
locales ; « non vérifié » = affirmation dont la source n'a pas été ouverte.*

La question : **quelles émissions entraînerait une consommation ajoutée de data centers en
France, heure par heure, et comment le dire sans confondre moyen et marginal ?**

## 0. Résumé

1. **Aucune source officielle ne publie de facteur marginal français récent.** RTE publie des
   intensités **moyennes** (19,6 g/kWh pour la production en 2025, émissions directes) et des
   émissions « évitées » par les exportations (27 Mt en 2025) calculées par différentiel
   d'intensités moyennes, méthode dont RTE écrit qu'elle néglige l'effet sur l'ordre de
   préséance. Le dernier contenu marginal chiffré par RTE et l'ADEME date de 2007 (450 à
   550 g/kWh pour un usage en base, parc européen de l'époque). Le règlement européen sur
   l'hydrogène tranche une question voisine par une règle de prix et un forfait (≈ 659 g/kWh
   au-delà des heures où le prix est fixé par du bas carbone), pas par une mesure.
2. **Ce que nos données mesurent de façon robuste** (éCO2mix, publiable) : un MW consommé en
   plus en France entraîne à court terme **0,06 à 0,10 t de CO2eq par MWh d'émissions
   françaises** (2023-2025 ; 0,10 en 2019-2021), soit 3 à 5 fois l'intensité moyenne ; il est
   servi pour environ un tiers par des **exportations en moins** (0,29 à 0,43 MW par MW).
3. **Ce qu'elles ne mesurent pas** : ce que ces exportations perdues font émettre chez les
   voisins. Trois méthodes testées donnent trois réponses incompatibles (0,08 à 0,90 t par MW) ;
   deux sont démontrées biaisées (météo commune ; disponibilité nucléaire déclarée en partie
   endogène, EDF déclarant des arrêts « pour modulation »).
4. **Proposition** : publier un plancher mesuré (émissions françaises), des cas bornés pour la
   part étrangère (rien, gaz, charbon ou lignite : 0,07 à 0,40 t/MWh en 2024-2025, soit 0,6 à
   3,5 Mt/an pour 1 GW plat, contre 0,17 Mt au facteur moyen), la part des heures où la
   France est moins chère que tous ses voisins (14 à 22 % en 2024-2025 : consommation ajoutée
   servie en France), et les raisons écrites pour lesquelles l'écart reste large. Le long
   terme et le plafond du marché carbone européen sont cités, pas calculés.
5. **Constats annexes à remonter** : `taux_co2` n'utilise pas les facteurs de l'annexe du
   Bilan électrique (charbon ≈ 985 contre 855 ; bioénergies ≈ 220 contre 0) ; la série
   `nucleaire_disponible` du site contient de la modulation économique déclarée (effet sur
   « Quand ? » à évaluer, pas à corriger sur la foi de ce rapport).

## 1. État de l'art

Rapports complets des agents (avec toutes les URL, pages et niveaux de vérification) : à
reverser dans `docs/spike/` après relecture ; ils sont aujourd'hui dans le dossier de travail
de la session, hors dépôt. Convention ci-dessous : **[lu]** = lu dans le document par un
agent ; **[vérifié]** = passage relu par l'agent rédacteur dans le PDF ou la page ;
**[résumé]** = seul le résumé a été lu ; **[non vérifié]** = non ouvert.

### 1.1 Les trois familles de facteurs

| Famille | Ce qu'elle mesure | Usage légitime | Ce qu'elle n'est pas |
|---|---|---|---|
| **Moyen** (attributionnel) | émissions d'une période ÷ production (ou consommation) de la période | inventaire, répartition entre consommateurs (Scope 2 « location-based ») | l'effet d'une consommation ajoutée |
| **Marginal de court terme** (opérationnel) | variation des émissions quand la demande varie, à parc donné | consommation ajoutée ou déplacée à court terme | l'effet de long terme (investissements, fermetures) |
| **Marginal de long terme** (structurel, « build margin ») | variation des émissions quand la demande modifie aussi le parc | décision durable (une vague de data centers) | une mesure : c'est le résultat d'un modèle et de ses hypothèses |

### 1.2 Facteur moyen : RTE, ADEME, AIE

- **RTE, éCO2mix, `taux_co2`** : intensité moyenne de la production française, émissions
  directes de combustion, CO2eq, hors échanges et hors construction ; facteur = facteur du
  combustible (ADEME) × rendement moyen de la filière, sans valeur publiée (page
  « eco2 emissions », sans date, [lu]). Facteurs implicites constatés au § 2.2.
- **RTE, Bilan électrique 2024**, chapitre Émissions (mars 2025) [lu] : 11,7 MtCO2eq,
  21,7 gCO2eq/kWh produit (direct) ; 30,2 g en ACV ; consommation : 10,0 MtCO2 ; annexe des
  facteurs par filière (direct et ACV, § 2.2). **Bilan électrique 2025**, rapport complet
  (mars 2026) [lu] : 19,6 g (direct), 29,0 g (ACV), consommation 20,0 g, maximum horaire 58 g.
- **Émissions « évitées » par les exportations** (RTE) : « près de 20 MtCO2eq » en 2024
  [vérifié, BE2024 Émissions p. 8] et « près de 27 MtCO2éq » en 2025 [vérifié, BE2025]. Méthode
  : pour chaque heure, différentiel entre l'intensité **moyenne** de la production française et
  celle des pays importateurs, × volume exporté. RTE l'écrit lui-même : la méthode « néglige
  certains phénomènes […] : en particulier, il n'est pas tenu compte de l'effet qu'aurait une
  modification des échanges sur l'ordre de préséance économique dans chaque pays » [vérifié,
  BE2025]. **Ce n'est pas un effet causal, et ce n'est pas un facteur marginal.** À ne jamais
  additionner à nos émissions induites (§ 3.5, double compte).
- **ADEME, Base Empreinte** (CSV open data, version de janvier 2026) [lu] : « Électricité 2024,
  mix moyen, consommation » 0,0519 kgCO2e/kWh, **ACV** (combustion 0,035 + amont 0,0131 +
  pertes 0,0038), lissé sur 2021-2024. Facteurs « par usage » (2023, méthode mensualisée /
  saisonnalisée) : chauffage 0,0645 / 0,115 ; « industrie base » 0,057 / 0,0442 ; **aucune
  ligne « data center » ni « usage continu »**. Ce sont des facteurs d'**allocation**, pas
  d'effet.
- **Méthode des usages** : note de cadrage ADEME-EDF de 2005 (chauffage 180 g, usages en base
  40 g, historique 1998-2003), citée par la note ADEME-RTE de 2007 [vérifié dans la note] ;
  valeur RE2020 du chauffage, 79 g pour 2017, « méthode moyenne mensualisée » (RTE-ADEME 2020,
  p. 207 [lu]) ; périmètre (ACV ou direct) non précisé dans les textes lus.
- **AIE** : iea.org refuse les accès automatisés. Base « Emissions Factors » (moyen,
  territorial) et rapport *Energy and AI* (avril 2025 ; ≈ 180 Mt d'émissions indirectes des
  data centers d'après des extraits) **[non vérifiés]** ; on ne sait pas si l'AIE utilise une
  intensité moyenne ou marginale.
- **AEE**, indicateur « Greenhouse gas emission intensity of electricity generation » :
  méthode lue (émissions de la production publique ÷ production brute) ; valeurs par pays dans
  un graphique interactif **[non lues]**.

### 1.3 Facteur marginal : ce que publient les institutions

**Aucune série officielle française de contenu CO2 marginal, horaire ou annuel, n'a été
trouvée** (RTE, ADEME, CRE, ministère ; recherche des agents, non exhaustive : ODRÉ et DGEC non
fouillés). Ce qui s'en approche :

- **Note ADEME-RTE du 8 octobre 2007**, « Le contenu en CO2 du kWh électrique : avantages
  comparés du contenu marginal et du contenu par usages sur la base de l'historique »
  (copie DREAL Hauts-de-France) [vérifié] : marginalité nucléaire « environ 25 % du temps » ;
  hors de ces heures, 600 à 700 g ; **« pour les usages en base : 450 à 550 g »** ; « de
  l'ordre de 400 g par kWh à l'horizon 2020 pour un usage en base ». Conclusion : méthodes
  complémentaires, la marginale « la plus adaptée » pour évaluer une décision future. Parc
  européen de 2007 (charbon et gaz, peu de renouvelables) : **historique, non transposable**.
- **RTE-ADEME, rapport chauffage** (décembre 2020, rapport complet publié en février 2021),
  chapitre 5 [lu ; citations clés vérifiées] : cinq méthodes (moyenne annuelle, saisonnalisée,
  mensualisée, marginale à parc inchangé, incrémentale à parc adapté). La marginale n'est
  « pas généralisable à un volume important » ; l'étude retient l'incrémentale « avec
  adaptation du mix », par bilans avec et sans sur un modèle européen, sans facteur unique. Et
  p. 219 : « un surplus de consommation en France peut engendrer, selon les moments, de
  moindres exports ou – plus ponctuellement – des imports, et donc le démarrage de centrales
  thermiques fossiles ailleurs en Europe. Les émissions ainsi générées ne peuvent être
  considérées comme des émissions directes en France mais doivent être introduites dans
  l'analyse dès lors que l'on souhaite mettre en œuvre un raisonnement en empreinte
  carbone. » C'est le passage institutionnel le plus proche de notre question.
- **CRE, délibération n° 2021-126 du 6 mai 2021** [vérifié] : approuve un « facteur
  d'émission fondé sur le marché » de **0,59 tCO2/MWh** (France, 2019), calculé par RTE avec
  Antares comme (prix avec SEQE − prix sans SEQE) / prix du CO2. C'est un paramètre des aides
  d'État (compensation des coûts indirects), **pas** le facteur d'une consommation ajoutée. La
  CRE y écarte les méthodes par moyen marginal observé : « en 2019, pendant au moins la moitié
  des pas de temps, il y avait un moyen européen charbon et un gaz à moins de 1 €/MWh du prix
  Spot ». Argument fort contre une attribution horaire par le prix.
- **RTE, Futurs énergétiques 2050**, chapitre 12 [lu en partie] : exportations françaises
  réduisant les émissions européennes de 34 MtCO2eq en 2030 (scénario sans fermeture), même
  famille que les « émissions évitées ». **Bilans prévisionnels 2023 et 2025** (chapitres lus) :
  aucune méthode « avec et sans » pour une consommation ajoutée ; le BP2025 traite les data
  centers en consommation, sans émissions.

### 1.4 Règles européennes voisines : l'hydrogène renouvelable

- **Règlement délégué (UE) 2023/1184** (lu sur un miroir, EUR-Lex refusant les robots ; à
  recouper) : électricité du réseau comptée renouvelable si la zone dépasse 90 % de
  renouvelables (art. 4.1), ou si son intensité est sous 18 gCO2eq/MJ avec PPA (art. 4.2) ;
  additionnalité : installation de moins de 36 mois (art. 5) ; **corrélation temporelle
  mensuelle jusqu'au 31/12/2029, horaire à partir du 1/1/2030** (art. 6) ; corrélation
  géographique : même zone, ou zone voisine à prix égal ou supérieur (art. 7).
- **Règlement délégué (UE) 2023/1185**, annexe, partie A, point 6 [vérifié sur le miroir
  lawplayer.com] : trois méthodes au choix pour l'électricité du réseau non entièrement
  renouvelable : (a) intensité **moyenne** du pays ou de la zone (partie C ; tableau A :
  France 19,6 gCO2eq/MJ, année 2020, amont compris) ; (b) **zéro** si les heures de pleine
  charge ne dépassent pas le nombre d'heures où « the marginal price of electricity was set
  by installations producing renewable electricity or nuclear power plants » l'année
  précédente, sinon **183 gCO2eq/MJ** (≈ 659 g/kWh, conversion de ma part) ; (c) la valeur de
  « the marginal unit generating electricity at the time of the production », « if this
  information is publicly available from the national transmission system operator ».
- Transposition (raisonnement, pas une règle) : le législateur a tranché une question voisine
  par une **règle de prix** (heures fixées par du bas carbone) et un forfait au-delà. Un data
  center plat, ≈ 8 760 heures de pleine charge, dépasserait ce nombre d'heures et recevrait
  le forfait. Et la méthode (c) n'est pas applicable en France : RTE ne publie pas l'unité
  marginale (à notre connaissance). Ni la règle ni le forfait ne sont une mesure physique.
- **Directive (UE) 2023/1791, art. 12, et règlement délégué (UE) 2024/1364** (miroirs) :
  déclaration des data centers à partir de 500 kW informatiques ; indicateur de part
  renouvelable (garanties d'origine, PPA, autoproduction) ; **aucun facteur d'émission de
  l'électricité** demandé. Annexe VII de la directive **[non lue]**.
- **GHG Protocol** : *Scope 2 Guidance* (2015) [lu], § 6.10 : « Companies shall not use
  marginal emission factors […] for a location-based scope 2 calculation » ; le Scope 2 est un
  inventaire, il ne mesure pas l'effet d'une consommation. *Guidelines for Quantifying GHG
  Reductions from Grid-Connected Electricity Projects* (WRI, 2007) [lu] : marges
  d'exploitation et de construction. Révision du Scope 2 en cours (consultations ouvertes le
  20 octobre 2025, appariement horaire des certificats, norme attendue fin 2027) [lu].

### 1.5 Littérature académique de référence

Métadonnées vérifiées sur Crossref par l'agent ; textes intégraux sous paywall **non lus**
(résumés seulement, sauf mention).

**Marginal de court terme par régression.**
- Hawkes, A.D. (2010). Estimating marginal CO2 emissions rates for national electricity
  systems. *Energy Policy* 38(10), 5977-5987. doi:10.1016/j.enpol.2010.05.053. Grande-Bretagne,
  ≈ 0,69 kgCO2/kWh (2002-2009) [résumé] ; échanges non traités.
- Siler-Evans, K., Azevedo, I.L., Morgan, M.G. (2012). Marginal Emissions Factors for the U.S.
  Electricity System. *Environ. Sci. Technol.* 46(9), 4742-4748. doi:10.1021/es300145v.
  ΔCO2 sur ΔG fossile, horaire, par région ; « imports and exports between regions are
  ignored » [texte lu].
- Graff Zivin, J.S., Kotchen, M.J., Mansur, E.T. (2014). Spatial and temporal heterogeneity of
  marginal emissions… *J. Econ. Behav. Organ.* 107, 248-268. doi:10.1016/j.jebo.2014.03.010.
  Émissions de toute l'interconnexion sur la charge de chaque sous-région : le producteur
  marginal peut être n'importe où [version de travail NBER lue]. **C'est la bonne structure
  pour un pays interconnecté** ; elle suppose la charge exogène, ce que notre § 2.6 montre
  faux quand la météo est commune.
- Callaway, D.S., Fowlie, M., McCormick, G. (2018). Location, Location, Location… *JAERE* 5(1),
  39-75. doi:10.1086/694179 [résumé].
- Holland, S.P., Kotchen, M.J., Mansur, E.T., Yates, A.J. (2022). Why marginal CO2 emissions
  are not decreasing for US electricity… *PNAS* 119(8), e2116632119.
  doi:10.1073/pnas.2116632119. Moyen −28 % en dix ans, marginal +7 % [résumé] : **moyen et
  marginal peuvent diverger durablement**.
- Beltrami, F., Grossi, L., Liebensteiner, M. (2025). Beyond borders: Estimating the marginal
  emission factor of electricity trade. *Energy Economics* 148, 108588.
  doi:10.1016/j.eneco.2025.108588. Le commerce est endogène ; instrument : l'éolien des
  voisins ; ignorer le commerce « results in substantial estimation biases » [résumé]. **Piste
  directe pour réparer notre § 2.6** (l'éolien des voisins est dans nos données).
- Ryan, N.A., Johnson, J.X., Keoleian, G.A. (2016). Comparative Assessment of Models and
  Methods To Calculate Grid Electricity Emissions. *Environ. Sci. Technol.* 50(17), 8937-8953.
  doi:10.1021/acs.est.5b05216 : jusqu'à 68 % d'écart entre méthodes [résumé].

**Marginal par l'ordre de mérite ou par modèle.**
- Fleschutz, M. et al. (2021). The effect of price-based demand response on carbon emissions
  in European electricity markets… *Applied Energy* 295, 117040.
  doi:10.1016/j.apenergy.2021.117040. Facteurs marginaux pour 20 pays européens, 2017-2019
  [résumé] ; traitement des échanges non vérifié.
- Biéron, M., Le Dréau, J., Haas, B. (2023). Assessment of the marginal technologies reacting
  to demand response events: A French case-study. *Energy* 275, 127415.
  doi:10.1016/j.energy.2023.127415. Seule étude trouvée sur la France avec ordres de mérite,
  hydraulique sous contrainte d'énergie et échanges (2018) ; pas de facteur en g/kWh dans le
  résumé [résumé du préprint].
- Zeyen, E., Riepin, I., Brown, T. (2024). Temporal regulation of renewable supply for
  electrolytic hydrogen. *Environ. Res. Lett.* 19(2), 024034. doi:10.1088/1748-9326/ad2239 :
  une consommation **en base** appariée à l'année peut augmenter les émissions ; l'appariement
  horaire et l'additionnalité locale l'évitent [résumé]. Riepin, I., Brown, T. (2024), *Energy
  Strategy Reviews* 54, 101488, doi:10.1016/j.esr.2024.101488 (24/7 CFE en Europe) ; Ruhnau,
  O., Schiele, J. (2023), *Energy Policy* 182, 113763, doi:10.1016/j.enpol.2023.113763 ;
  Giovanniello, M.A. et al. (2024), *Nature Energy* 9(2), 197-207,
  doi:10.1038/s41560-023-01435-0 (la conclusion dépend de l'hypothèse d'additionnalité) ;
  Xu, Q. et al. (2024), *Joule* 8(2), 374-400, doi:10.1016/j.joule.2023.12.007 [résumé non lu].

**Long terme.**
- Hawkes, A.D. (2014). Long-run marginal CO2 emissions factors in national electricity
  systems. *Applied Energy* 125, 197-205. doi:10.1016/j.apenergy.2014.03.060 [résumé].
- Gagnon, P., Cole, W. (2022). Planning for the evolution of the electric grid with a long-run
  marginal emission rate. *iScience* 25(3), 103915. doi:10.1016/j.isci.2022.103915 [résumé].
- Gagnon, P.J., Bistline, J.E.T., Alexander, M.H., Cole, W.J. (2022). Short-run marginal
  emission rates omit important impacts of electric-sector interventions. *PNAS* 119(49),
  e2211624119. doi:10.1073/pnas.2211624119 [texte lu] ; Ricks, W., Gagnon, P., Jenkins, J.D.
  (2024). Short-run marginal emission factors neglect impactful phenomena… *Energy Policy*
  189, 114119. doi:10.1016/j.enpol.2024.114119 [résumé]. **Désaccord réel de la littérature** :
  le court terme est mesurable, le long terme est pertinent pour une décision durable.

**Comptabilité moyenne avec échanges.**
- Tranberg, B. et al. (2019). Real-time carbon accounting method for the European electricity
  markets. *Energy Strategy Reviews* 26, 100367. doi:10.1016/j.esr.2019.100367 (traçage des
  flux, mesure **moyenne**) ; de Chalendar, J.A., Taggart, J., Benson, S.M. (2019). Tracking
  emissions in the US electricity system. *PNAS* 116(51), 25497-25502.
  doi:10.1073/pnas.1912950116. Electricity Maps a retiré ses signaux marginaux pour
  « major limitations » (billet lu par l'agent).
- Double compte : aucun article lu ne l'énonce en ces termes ; c'est un raisonnement (§ 3.5).

**Data centers.**
- Radovanović, A. et al. (2023). Carbon-Aware Computing for Datacenters. *IEEE Trans. Power
  Systems* 38(2), 1270-1280. doi:10.1109/TPWRS.2022.3173250 : le signal utilisé par Google est
  l'intensité **moyenne** prévue ; « the choice of the most effective grid-level signal
  requires further research » [texte arXiv lu].
- Sukprasert, T. et al. (2024). On the Limitations of Carbon-Aware Temporal and Spatial
  Workload Shifting in the Cloud. *EuroSys '24*, 924-941. doi:10.1145/3627703.3650079 : gains
  « limited and far from ideal » [résumé].
- Lindberg, J., Roald, L., Lesieutre, B. (2021), *HICSS-54*, doi:10.24251/hicss.2021.384, et
  suites : facteurs marginaux localisés pour le déplacement géographique [résumés].
- Hemmati, M. et al. (2026), arXiv:2606.09617 : **préprint** européen à horizon 2030-2050,
  hausse d'émissions françaises « below 1 MtCO₂eq » malgré 8,5 GW de data centers, parce que
  le modèle ajoute du nucléaire. Non évalué par les pairs ; modèle non précisé : ne pas citer
  comme résultat.

**Marché du carbone européen** (vérifié sur Crossref et PubMed Central par l'agent
rédacteur) : Perino, G. (2018), *Nature Climate Change* 8, 262-264,
doi:10.1038/s41558-018-0120-2 ; Rosendahl, K.E. (2019), *Nature Climate Change* 9, 734-735,
doi:10.1038/s41558-019-0579-5, et réponse de Perino, *ibid.* 736 ; Bruninx, K., Ovaere, M.
(2022), *Nature Communications* 13, 1165, doi:10.1038/s41467-022-28398-2 (§ 3.5).

**Cas français, autres.** Aucune estimation récente trouvée chez Carbone 4, IDDRI, Institut
Rousseau, Agora ou Ember (recherche de l'agent, non exhaustive). Pareschi, Georges,
Boulouchos (2017), communication de colloque : 133,5 g/kWh marginal contre 34,8 moyen pour la
France, éolien et solaire exclus, année non vérifiée : **à ne pas reprendre**.

### 1.6 Consensus et désaccords

- **Consensus** : le facteur moyen ne mesure pas l'effet d'une consommation ajoutée ; le
  marginal varie avec l'heure, la saison et le niveau de charge ; dans une zone
  interconnectée, ignorer les échanges biaise ; court et long terme sont deux questions.
- **Désaccords** : court terme (mesurable, Holland et al.) contre long terme (pertinent,
  Gagnon et al., Ricks et al.) ; additionnalité (Giovanniello et al.) ; signal moyen ou
  marginal pour piloter les data centers (Google, Electricity Maps, Lindberg et al.) ; aucune
  méthode de référence (Ryan et al. : jusqu'à 68 % d'écart).
- **Pour la France**, la littérature lue ne fournit pas de facteur marginal récent publié et
  vérifiable. Les seuls chiffres français sont anciens (ADEME-RTE 2007), d'une autre nature
  (CRE 2021, RTE « émissions évitées ») ou non publiés en revue.

## 2. Ce que nos données permettent

### 2.1 Données disponibles et leurs défauts pour le carbone

| Donnée | Source | Licence | Pas | Défauts qui comptent ici (constatés) |
|---|---|---|---|---|
| Production par filière FR, solde physique, `taux_co2`, échanges commerciaux | éCO2mix (ODRÉ) | Licence Ouverte 2.0 | 30 min → heure | `taux_co2` = intensité **moyenne de la production**, directe ; Corse absente (≈ −7 % sur l'intensité annuelle, `docs/spike/systeme.md`) |
| Nucléaire disponible déclaré | REMIT EDF | Licence Ouverte 2.0 | heure | contient des **arrêts pour modulation** déclarés « Planifiée » (§ 2.6) |
| Prix day-ahead FR, BE, DE, ES, IT-Nord, CH | ENTSO-E A44 | conditions générales (hors CC BY 4.0) | heure | GB seulement jusqu'en 2020, en GBP |
| Production par filière BE, DE, ES, IT, CH (GB 2015-2021) | ENTSO-E A75 | conditions générales | heure | voir ci-dessous |
| Flux physiques FR ↔ voisins | ENTSO-E A11 | **CC BY 4.0** (sauf IFA, doute non levé) | heure | biais de solde inexpliqué (+600 à +800 MW certaines années) |
| Charge réalisée | ENTSO-E A65 | conditions générales | heure | **FR seulement** : la charge des voisins n'est pas téléchargée |

Couverture de la production ENTSO-E des voisins (constaté, `spike_carbone.py` et requêtes
ad hoc, TWh par an) :

- **Allemagne** : complète et plausible (438 TWh en 2024 et 2025) ; gaz de houille (B03)
  absent de 2020 à 2022 (≈ 4 à 5 TWh les autres années).
- **Italie** : catégorie « autres » (B20) de **72 à 92 TWh en 2015-2017**, 60 en 2018, puis
  15 à 25 TWh : avant 2019, une grande part du thermique n'est pas classée par combustible.
  En 2025, hydraulique au fil de l'eau 1,3 TWh contre 23 à 40 TWh les années précédentes
  (6 537 heures vides) : **trou de données**, sans effet sur les émissions mais sur tout total
  de production.
- **Belgique** : 67 à 93 TWh selon les années ; « autres » 5 TWh/an jusqu'en 2020.
- **Espagne** : plausible (≈ 250 TWh) ; STEP (B10) jamais publiée.
- **Suisse** : 2015 incomplet (16 TWh) ; ≈ 40 à 56 TWh ensuite, sous la production réelle
  (non vérifiée ici) ; reclassement fil de l'eau en 2025 (2,3 → 14,5 TWh) ; aucune filière
  fossile ni déchets publiée.
- **Grande-Bretagne** : production de 2015 à mi-2021 seulement, puis rien.
- **Absents** : Pays-Bas, Autriche, Pologne, Tchéquie, Danemark, Portugal, Luxembourg. La
  « zone couplée » observable est donc **partielle** : FR, BE, DE, ES, IT, CH (+ GB jusqu'en
  2021).

**Horodatage.** Le décalage d'une heure de la production et de la charge FR d'ENTSO-E en
2023-2024 (`docs/spike/entsoe-pipeline.md`, § 3) est **contourné** : tous les prototypes
prennent la France dans éCO2mix, jamais dans A75/A65. Pour les voisins, aucune référence
indépendante : test grossier par le barycentre horaire du profil solaire de mai à juillet
(fonction `decalage`). Constaté : DE 10,72-10,77 h UTC, BE 11,11-11,20, ES 11,95-12,17,
IT 10,57-10,68 chaque année de 2016 à 2025 ; CH saute de ≈ 10,9 à 11,2 en 2020 puis revient
en 2025. **Aucun décalage d'une heure visible chez les voisins** (il déplacerait le barycentre
d'environ 1 h). Ce test ne détecte pas un décalage limité à l'hiver ni à quelques semaines.
Effet de bord : le solaire FR d'ENTSO-E est en avance d'environ 0,15 à 0,2 h sur éCO2mix
de 2016 à 2022, puis aligné en 2024-2025 ; cause non cherchée.

### 2.2 Facteurs d'émission par filière

Rapport complet de l'agent : à reverser dans `docs/` après relecture (ici, l'essentiel).
Valeurs en gCO2eq/kWh **électrique**, émissions **directes** (combustion).

**Base retenue : RTE, Bilan électrique 2025, rapport complet, annexe, p. 145** (« Hypothèses
concernant les facteurs d'émissions… »), identique au BE2024, chapitre Émissions, annexe
p. 12. C'est la seule source primaire trouvée qui donne, par filière, le direct et l'ACV. Elle
ne cite ni source ni année ; ce sont des facteurs du **parc français**.

| Code ENTSO-E | Central (RTE BE2025) | Bas | Haut | Remarques |
|---|---|---|---|---|
| B01 biomasse | 0 | 0 | 0 | convention : CO2 biogénique non compté en direct (ACV RTE : 70 ; GIEC AR5 : 130 à 890) |
| B02 lignite | 961 | 961 | 1 119 (UBA 2026, parc allemand 2025) | AR5 n'a pas de ligne lignite |
| B03 gaz de houille | 855 (« autres fossiles », proxy) | 160 | 936 | GIEC 2006 : gaz de cokerie ou de haut-fourneau, ×6 d'écart ; hypothèse |
| B04 gaz | 435 (« indéterminé ») | 331 (CCG) | 497 (TAC) | ENTSO-E ne sépare pas CCG, TAC, cogénération |
| B05 houille | 855 | 760 (AR5, médiane PC) | 969 (ADEME, combustion) | UBA 860 |
| B06 fioul | 769 | 628 (ADEME, combustion) | 769 | |
| B17 déchets | 494 | 0 | 988 | RTE : 988 sur la part **non renouvelable** ; la part fossile de B17 est inconnue (50 % en central : **hypothèse**) |
| B20 autres | 435 | 0 | 855 | contenu inconnu ; **hypothèse** |
| nucléaire, hydraulique, éolien, solaire, géothermie | 0 | 0 | 0 | direct nul par définition |

Sources des bornes : GIEC AR5 WGIII, annexe III (Schlömer et al. 2014), tab. A.III.2,
p. 1335 ; GIEC 2006, vol. 2, chap. 2, tab. 2.2 (kg/TJ PCI, à diviser par un rendement non
fourni) ; ADEME Base Carbone (CSV data.ademe.fr, lignes « centrale charbon / fioul / gaz »,
modifiées en 2018, validité « déc.-21 ») ; UBA, *Climate Change* 16/2026, tab. 4 (mars 2026).
URL et pages : rapport de l'agent (à reverser).

**`taux_co2` d'éCO2mix n'utilise pas ces facteurs (constaté).** La page éCO2mix de RTE dit
« facteur du combustible (ADEME) × rendement moyen », sans valeur numérique. Une régression
sans constante de `taux_co2 × production` sur les filières thermiques d'éCO2mix (R² ≥ 0,998
chaque année testée, 2016, 2019, 2022, 2024, 2025) donne des facteurs implicites : CCG ≈ 346
à 355 (ADEME combustion : 351), **charbon ≈ 970 à 1 000** (annexe RTE : 855 ; ADEME : 969),
fioul ≈ 760 à 781 (annexe : 769), **bioénergies ≈ 210 à 240 en 2019-2025** (annexe : 0 ;
probablement la part fossile des déchets). TAC, cogénération et « autres gaz » sont instables
(faible production, colinéarité). Conséquences : deux jeux de facteurs RTE coexistent ; on ne
mélange pas `taux_co2` et l'annexe dans un même calcul sans le dire.

**Recoupement de nos intensités moyennes** (production, facteurs centraux, constaté) avec la
figure 7.14 du BE2025 (p. 133, intensité moyenne de la production calculée par RTE depuis
ENTSO-E, lue sur le graphique par l'agent ; ce n'est pas une statistique nationale) :

| | 2017 nous / RTE | 2025 nous / RTE | Verdict |
|---|---|---|---|
| Allemagne | 391 / 406 (DE+LU) | 284 / 286 | boucle (−4 % et −1 %) |
| Espagne | 266 / 261 | 96 / 95 | boucle |
| Italie | 334 / 459 | 260 / 276 | ne boucle pas avant 2019 (catégorie « autres ») ; −6 % en 2025 |
| Belgique | 156 / 186 | 131 / 179 | ne boucle pas (−16 à −27 %) : classement de B20 et B17 ? non établi |
| Suisse | 0 / 71 | 0 / 49 | ne boucle pas : aucune filière émettrice publiée dans nos données |

Ce recoupement vérifie notre calcul, pas les données (même source, mêmes facteurs pour DE et
ES). Recoupements indépendants possibles : UBA (rapporté à la consommation, pas à la
production : 344 g en 2025 contre 284), ISPRA (CO2 seul, 256 g en 2023), DESNZ (189 g en 2023).
Périmètres différents : à comparer en ordre de grandeur seulement.

### 2.3 Prototype (a) : régimes de prix et d'échanges

Pour chaque heure où les six prix existent (FR, BE, DE, ES, IT-Nord, CH ; ENTSO-E A44, DE =
DE-AT-LU puis DE-LU), on classe la France (seuil de convergence : |écart| < 0,01 €/MWh) :
couplée à au moins un voisin ; **découplée vers le bas** (moins chère que tous) ; découplée
vers le haut ; ou **entre** (différente de tous, ni la moins chère ni la plus chère). Solde
exportateur = `ech_physiques` éCO2mix < 0. Constaté (`spike_carbone.py regimes` et
`spike_carbone_regimes_croises.py`) :

| Année | France exportatrice | = DE | = ES | Couplée à ≥ 1 voisin | Découplée vers le bas | Entre | Prix ≤ 0 | Découplée basse **et** nucléaire disponible non produit > 1 GW |
|---|---|---|---|---|---|---|---|---|
| 2019 | 92,6 % | 43,6 % | 22,5 % | 64,6 % | 9,5 % | 25,7 % | 0,3 % | 9,1 % |
| 2020 | 85,6 % | 45,9 % | 39,3 % | 77,2 % | 5,2 % | 17,4 % | 1,2 % | 4,5 % |
| 2021 | 80,0 % | 49,3 % | 34,8 % | 79,5 % | 3,3 % | 16,7 % | 0,8 % | 3,3 % |
| 2022 | 34,2 % | 34,3 % | 26,7 % | 72,4 % | 0,0 % | 26,5 % | 0,1 % | 0,0 % |
| 2023 | 87,8 % | 29,1 % | 32,8 % | 60,9 % | 4,5 % | 34,5 % | 2,1 % | 4,3 % |
| 2024 | 97,8 % | 13,9 % | 32,5 % | 44,3 % | 14,2 % | 41,6 % | 6,2 % | 13,5 % |
| 2025 | 99,0 % | 9,8 % | 36,0 % | 44,2 % | 21,8 % | 34,0 % | 8,4 % | 18,6 % |

Ce que ça dit, et ce que ça ne dit pas :

1. **Robuste.** Depuis 2024, la France exporte presque à toute heure, et son prix est
   inférieur à celui de tous ses voisins une heure sur sept (2024) à une sur cinq (2025). À
   ces heures, les contraintes du couplage (capacités aux frontières à NTC, éléments critiques
   du flow-based) limitent les exportations, et le prix français est fixé par une offre
   française : une petite consommation ajoutée est servie **en France** (nucléaire disponible
   non produit, moins d'écrêtement, moins de pompage) et ne change pas, au premier ordre, ce
   que reçoivent les voisins. Une consommation de plusieurs GW peut, elle, faire remonter le
   prix au niveau du voisin : c'est une limite d'échelle, à dire. Le prix moyen à ces heures : 44 €/MWh (2024), 52 €/MWh (2025).
2. **Non robuste : « unité marginale chez le voisin ».** Le couplage avec l'Allemagne est
   tombé de 44-49 % des heures (2019-2021) à 10-14 % (2024-2025). Et **un tiers à deux
   cinquièmes des heures sont « entre »** : avec le flow-based (frontières BE et DE), le prix
   français diffère de tous sans être extrême ; aucune règle simple n'attribue l'unité
   marginale. Identifier la technologie marginale par le prix exigerait aussi les prix du gaz,
   du charbon et du CO2 (coûts marginaux), absents de nos données (TTF, API2 : non ouverts ;
   enchères de quotas EEX : piste non vérifiée).
3. Même aux heures découplées vers le bas, **1,0 à 1,4 GW de thermique fossile français
   tourne** en moyenne (2024-2025 ; dont 0,4 à 0,7 GW de CCG) : cogénération et services
   système. L'intensité moyenne y est de 13 à 14 g/kWh. « Découplée vers le bas » ne veut pas
   dire « fossile à l'arrêt » ; cela veut dire que le fossile n'est probablement pas
   **marginal**.

### 2.4 Prototype (b) : d'où vient un MW de consommation française en plus

Régression intra-groupe sur éCO2mix seul (Licence Ouverte) : pour chaque grandeur Y (production
par filière, exportations, pompage, émissions françaises = `taux_co2` × production),
Y = β · consommation + γ · (éolien + solaire) + effets fixes année × mois × heure ×
(ouvré/week-end) ; erreurs-types groupées par jour. La variation qui identifie β est l'écart
de consommation d'un jour à l'autre, à mois et heure donnés : surtout la température.
Pour approcher une **consommation plate**, β est estimé saison par saison puis moyenné à
poids égaux (constaté, `spike_carbone.py reponse_fr` et `spike_carbone_saisons.py`) :

| Pour +1 MW consommé en France | 2019-2021 | 2023-2025 | 2024-2025 |
|---|---|---|---|
| nucléaire | +0,22 | +0,33 | +0,38 |
| hydraulique | +0,10 | +0,09 | +0,11 |
| gaz | +0,19 | +0,18 | +0,16 |
| charbon + fioul | +0,03 | +0,02 | +0,01 |
| pompage en moins | +0,04 | +0,03 | +0,05 |
| **exportations en moins** | **−0,43** | **−0,35** | **−0,29** |
| émissions **françaises** (t/MWh) | 0,097 | 0,079 | 0,068 |

Le bilan boucle (somme des sources ≈ 1, écart < 0,01) ; intervalles à 95 % de ±0,01 à
±0,03 t/MWh sur les émissions par saison, ±0,05 à ±0,18 sur le nucléaire.

- **Robuste** : l'ordre de grandeur des émissions **françaises** induites, 0,06 à 0,10 t/MWh
  (60 à 100 g/kWh), soit **3 à 5 fois l'intensité moyenne** de la production (18 à 20 g/kWh
  en 2024-2025). Le gaz français répond à toutes les saisons (+0,11 à +0,21).
- **Non robuste** : ce qui se passe chez les voisins. Un tiers du MW ajouté vient
  d'exportations en moins ; ce qu'émet le voisin qui ne les reçoit plus n'est pas dans ces
  données. Et la météo est commune : un jour froid en France l'est aussi en Allemagne, si bien
  que β mêle l'effet de la consommation française et celui de la demande voisine (biais
  chiffré au § 2.6 : il est massif sur les émissions des voisins).
- **Biais connus** : l'hydraulique de lac répond (+0,09 à +0,11) mais son eau est limitée sur
  la saison : l'énergie turbinée aujourd'hui manque plus tard, à un moment et avec des
  émissions que la régression n'attribue pas. L'estimation est de **court terme**, à parc et
  calendrier d'arrêts donnés.

### 2.5 Prototype (c) : régression des émissions de la zone sur sa charge nette (Hawkes)

Méthode de Hawkes (2010) appliquée à la zone FR + BE + DE + ES + IT + CH : variation horaire
des émissions (directes, facteurs du § 2.2) sur variation de la production moins éolien et
solaire, année par année (2019-2024 ; IT 2025 écarté pour le trou hydraulique). Constaté :
pente de **0,22 à 0,27 t/MWh** (central), 0,18 à 0,22 (bas), 0,25 à 0,32 (haut), à comparer
à une intensité moyenne de la zone de 0,14 à 0,22 t/MWh.

Pourquoi ce chiffre **ne répond pas** à notre question :

1. Il dit ce qui se passe quand **la charge de la zone** varie, pas quand la charge
   **française** varie. Test : la pente est la même (0,22 à 0,26) aux heures où la France est
   découplée vers le bas, alors qu'à ces heures une consommation française ajoutée ne peut
   pas, au premier ordre, toucher la production voisine.
2. Les différences d'une heure à l'autre sont dominées par le cycle journalier, que servent
   surtout l'hydraulique, les STEP et la modulation nucléaire : la pente mesure la réponse
   aux rampes, pas à une consommation plate. Elle sous-estime le fossile marginal dans les
   systèmes riches en hydraulique.
3. La zone est ouverte (NL, AT, PL, CZ, DK, GB après 2021 absents) : ce qui sort de la zone
   n'est pas compté.

### 2.6 Prototype (d) : expérience naturelle sur le nucléaire français

Idée : une perte de capacité nucléaire en France équivaut, au premier ordre, à une
consommation ajoutée (dans les deux cas il faut 1 MW de plus ailleurs, sauf si le nucléaire
avait de la marge non produite, qui l'absorbe dans les deux cas). Si cette perte est
**exogène**, on lit directement sa conséquence sur les émissions des voisins, sans
connaître leur charge. Régression au pas journalier, effets fixes année × mois et jour de
semaine, contrôles : consommation FR, éolien et solaire FR et voisins.

**Premier essai, faux : la disponibilité déclarée totale (REMIT) n'est pas exogène.** Le
coefficient de la production nucléaire sur la disponibilité valait −0,95 à −0,99 : toute
baisse de disponibilité devenait une baisse de production, ce qui contredisait « Quand ? »
(marge non produite importante en 2024-2025). Vérification dans le brut EDF : **928
événements « Planifiée » portent la mention d'un arrêt ou d'une baisse « pour modulation »**
(≈ 72 TWh cumulés sur 2015-2026, sur 2 173 TWh d'indisponibilité planifiée). EDF déclare
donc une partie de sa modulation économique comme indisponibilité : la série
`nucleaire_disponible` du site est en partie **endogène au prix**. À signaler aussi pour
« Quand ? » : la marge « disponible non produit » est mesurée **après** ces déclarations, elle
sous-estime donc la marge physique (effet non chiffré ; à vérifier avant toute correction,
règle du 26/11).

**Second essai : arrêts fortuits seulement** (événements « Fortuite » : 132 TWh cumulés ;
perte moyenne 0,6 à 2,4 GW selon l'année, écart-type 0,8 à 1,7 GW). Constaté, pour +1 MW
perdu par arrêt fortuit (facteurs centraux ; ± = intervalle à 95 %) :

| Période | Nucléaire produit | Exportations | Gaz FR | Émissions FR (t/h) | Émissions des voisins observés (t/h) |
|---|---|---|---|---|---|
| 2016-2019 | −0,72 | −0,51 | +0,13 | +0,08 ± 0,03 | +0,75 ± 0,21 |
| 2019-2021 | −0,69 | −0,41 | +0,14 | +0,09 ± 0,03 | +0,90 ± 0,21 |
| 2022-2024 | −0,85 | −0,74 | +0,06 | +0,02 ± 0,02 | +0,18 ± 0,17 |
| 2023-2025 | −0,58 | −0,49 | +0,06 | +0,03 ± 0,02 | +0,08 ± 0,16 |
| 2024-2025 | −0,37 | −0,33 | +0,08 | +0,03 ± 0,02 | +0,27 ± 0,20 |

Ce qui tient : la production nucléaire ne baisse que de 0,37 à 0,85 MW par MW perdu (le reste
est absorbé par la marge non produite, d'autant plus que la période est récente, ce qui est
cohérent avec « Quand ? ») ; les exportations baissent de 0,33 à 0,74 MW.

Ce qui ne tient pas : **avant 2022, les émissions des voisins montent de 0,75 à 0,90 t par MW
perdu, alors que les exportations ne baissent que de 0,41 à 0,51 MW** : il faudrait plus de
1,5 t par MWh d'exportation perdu, au-delà du lignite. Contrôle (`spike_carbone_test_fossile.py`) : la production totale des
voisins observés monte de 1,26 à 1,53 MW par MW perdu, deux à trois fois la baisse des
exportations ; c'est physiquement impossible pour une simple substitution. Les arrêts
fortuits coïncident donc avec autre chose qui fait produire les voisins (vraisemblablement la
météo commune : grand froid, canicule). Le placebo (arrêts fortuits de J+30) est nul, ce qui
écarte une tendance, pas un choc commun. **Verdict : pas de chiffre publiable par cette voie
avec nos données.** Pour la rendre utilisable, il faudrait la charge des voisins (A65, non
téléchargée) comme contrôle, ou des températures, et la production des pays manquants.

Contrôle du piège inverse : avec la consommation française comme régresseur dans la même
régression, les émissions des voisins « répondent » de **+0,53 à +0,84 t par MW** consommé
en France, total 0,62 à 0,95 t/MWh. C'est la météo commune, pas un facteur marginal. **Toute
régression des émissions européennes sur la consommation française donne un chiffre trop
haut, avec une apparence de précision** (intervalles de ±0,05).

### 2.7 Bilan : ce qui est robuste, ce qui ne l'est pas

| Résultat | Robustesse | Publiable (licence) |
|---|---|---|
| Intensité moyenne horaire de la production FR (`taux_co2`) et de la consommation (ODRÉ) | robuste ; deux jeux de facteurs RTE, Corse absente | oui (Licence Ouverte) |
| Part des heures où la France est découplée vers le bas, exportatrice, à prix ≤ 0 | robuste (règle simple, prix exacts) | oui en agrégat (prix ENTSO-E sous conditions générales ; FR seul possible via energy-charts) |
| Décomposition physique d'un MW français ajouté (nucléaire, hydraulique, gaz, exportations en moins) | ordre de grandeur robuste ; biais météo sur la part « exportations » | oui (éCO2mix seul) |
| Émissions **françaises** induites, court terme : 0,06 à 0,10 t/MWh | robuste à ± 30 % ; recoupé par deux méthodes (0,07-0,10 par la consommation ; 0,02-0,09 par les arrêts fortuits) | oui |
| Émissions **chez les voisins** induites par les exportations en moins | **non robuste** : trois méthodes, trois réponses (0,08 à 0,90 t/MWh) | seulement en bornes, construites (§ 3) |
| Unité marginale horaire chez le voisin | hors de portée sans prix des combustibles et sans modèle | — |

## 3. Proposition d'enquête

### 3.1 Question

**Une consommation ajoutée en France, plate, de X GW : quelles émissions entraînerait-elle à
court terme, en France et chez les voisins, et pourquoi le facteur moyen français ne le dit
pas ?** Sous-question explicite : à quelles heures la réponse est-elle « presque rien » (la
France a de la marge décarbonée qu'elle ne peut pas exporter), et à quelles heures dépend-elle
de ce que brûlent les voisins ?

On ne promet pas « le » facteur marginal de la France : on publie un **plancher mesuré**, des
**cas bornés** pour la part étrangère, et les raisons pour lesquelles l'écart entre les deux
reste large.

### 3.2 Indicateurs

**C1. Intensité moyenne horaire de la production et de la consommation françaises.**
gCO2eq/kWh, émissions directes. Production : éCO2mix `taux_co2` ; consommation (imports
compris) : ODRÉ `part-enr-intensite-ges-conso-tr` (depuis 2021). Moyennes annuelles
**pondérées** ; valeur annuelle de référence citée du Bilan électrique (19,6 g en 2025 pour la
production, 20,0 g pour la consommation, BE2025, à relire dans le PDF avant saisie).
*Ce que ce n'est pas* : les émissions causées par une consommation ajoutée. Il sert de
comparaison, et de piège montré : 1 GW plat × 19,6 g = 0,17 Mt/an, chiffre que l'on
rencontrera ailleurs et qui est 3 à 20 fois plus bas que C4 (2024-2025).

**C2. Heures « servies en France ».** Part des heures, et part de l'énergie d'une consommation
plate, où la France est **découplée vers le bas** (prix inférieur à celui de tous les voisins
publiés) **et** a plus de 1 GW de nucléaire disponible non produit. % des heures. Constaté :
9 % (2019), 0 % (2022), 13,5 % (2024), 18,6 % (2025). Compléments : part couplée, part
« entre » (flow-based, attribution impossible), part à prix ≤ 0. *Ce que ce n'est pas* : un
facteur d'émission ; ni la preuve que l'énergie ajoutée à ces heures est sans effet plus
tard (le nucléaire modulé économise du combustible qui aurait servi ailleurs, « Quand ? »).

**C3. D'où viendrait le MW ajouté.** Décomposition de court terme d'un MW consommé en plus,
par saison et par période (§ 2.4) : nucléaire, hydraulique, gaz, charbon et fioul, pompage en
moins, **exportations en moins**. MW par MW. Constaté en 2024-2025 : 0,38 / 0,11 / 0,16 / 0,01
/ 0,05 / **0,29**. *Ce que ce n'est pas* : une réponse causale propre pour la part
« exportations » (la météo est commune aux voisins) ; ni une réponse de long terme (parc,
calendrier des arrêts et contrats inchangés).

**C4. Émissions de court terme d'une consommation plate, en fourchette.** tCO2eq/MWh et
Mt/an pour 1 GW, émissions directes. Plancher = émissions **françaises** induites (C3,
mesuré) ; puis trois cas pour la part « exportations en moins » : remplacée chez le voisin
par (i) rien d'émetteur (renouvelables moins écrêtés, hydraulique, nucléaire), (ii) du gaz
(331 à 497 g, CCG à TAC, RTE), (iii) du charbon ou du lignite (855 à 1 119 g, RTE à UBA).
Calcul du site, constaté :

| Période | (i) plancher | (ii) gaz | (iii) charbon ou lignite | Facteur moyen FR |
|---|---|---|---|---|
| 2019-2021 | 0,10 t/MWh · 0,85 Mt/an | 0,24-0,31 · 2,1-2,7 Mt | 0,47-0,58 · 4,1-5,1 Mt | — |
| 2024-2025 | 0,07 t/MWh · 0,60 Mt/an | 0,17-0,21 · 1,4-1,9 Mt | 0,32-0,40 · 2,8-3,5 Mt | 0,0196 · 0,17 Mt |

*Ce que ce n'est pas* : un facteur marginal estimé de la zone couplée. Les cas ne sont pas
pondérés : nos données ne disent pas quelle part des exportations perdues aurait été
remplacée par quoi (§ 2.3, point 2 ; § 2.6). Le cas (iii) est un plafond de court terme ; le
cas (i) n'est pas « probable », c'est un plancher. Si la littérature retenue en § 1 donne des
facteurs marginaux de court terme par pays voisin, on pourra ajouter une ligne « littérature »,
citée comme telle, jamais recalculée.

**C5 (cité, pas calculé). Long terme.** Ce que disent RTE et la littérature sur les effets
structurels : une consommation durable change les investissements, l'exploitation du parc
nucléaire et, en Europe, le marché du carbone (§ 3.5). Texte seulement, sources primaires.

### 3.3 Ce qui peut être publié (licence ENTSO-E)

- C1, C3 et le plancher de C4 : **éCO2mix et ODRÉ seuls** (Licence Ouverte 2.0) ; REMIT EDF
  (Licence Ouverte 2.0) si besoin. Séries horaires publiables.
- C2 : utilise les prix day-ahead des voisins (A44, hors CC BY 4.0). On publie des **parts
  d'heures agrégées par an** (et par mois au plus), jamais les prix voisins horaires ; source
  citée « ENTSO-E Transparency Platform, calcul du site ». Le prix français affiché reste celui
  d'energy-charts (décision du 26/11).
- Flux par frontière (A11, CC BY 4.0) : publiables, avec attribution et mention des
  modifications ; frontière FR↔GB à part tant que l'exception IFA n'est pas levée.
- Production des voisins (A75) : n'apparaît que dans des agrégats (intensité annuelle par
  pays, à côté de la valeur RTE BE2025 fig. 7.14) ; pas de série horaire.

### 3.4 Recoupements pour `pc check`

1. Intensité de la consommation pondérée = Bilan électrique ± 2 % (existe déjà dans le spike
   système) ; intensité de la production éCO2mix = Bilan − (Corse) ± tolérance à calibrer.
2. **Facteurs implicites de `taux_co2`** (régression sans constante, § 2.2) dans une bande par
   filière (CCG 330-370, charbon 940-1 020, fioul 740-800) : détecte un changement de méthode
   de RTE ou une erreur d'unité.
3. **Bilan de la décomposition C3** : somme des coefficients (production + pompage en moins +
   exportations en moins) = 1 ± 0,02.
4. C2 : parts « basse + couplée + haute + entre » = 100 % ; prix FR ENTSO-E = energy-charts
   (contrôle existant).
5. Intensité annuelle DE et ES à facteurs RTE = BE2025 fig. 7.14 ± 5 % ; IT ± 10 % à partir
   de 2019 ; BE et CH listées comme non recoupées.
6. Plancher C4 recoupé par deux méthodes (consommation et arrêts fortuits) : signaler un écart
   au-delà d'un facteur 2.
7. Garde-fous de sens : C4 (i) ≤ (ii) ≤ (iii) ; aucune valeur de C4 inférieure à 0 ni
   supérieure au facteur du lignite ; intensité moyenne < plancher marginal (sinon, signaler).

### 3.5 Pièges qu'une experte attendra

1. **Moyen ≠ marginal.** Afficher C1 et C4 côte à côte, avec leurs noms complets, jamais un
   « facteur d'émission » sans adjectif. L'intensité de la consommation (imports compris) est
   aussi une moyenne.
2. **Double compte entre pays.** Additionner « les émissions françaises induites » et « les
   émissions évitées à l'étranger par les exportations françaises » publiées ailleurs (par
   RTE, par exemple) compte deux fois le même MWh. Une intensité de consommation qui intègre
   les imports ne s'ajoute pas à celle du pays exportateur. Notre C4 compte chaque MWh une
   fois : en France pour le plancher, chez le voisin pour la part « exportations en moins ».
3. **Court terme ≠ long terme.** Tout C1-C4 est à parc, interconnexions et calendrier
   d'arrêts donnés. À long terme, une consommation de 20 TWh/an change ce qui se construit ou
   ferme (Hawkes 2014 ; Gagnon et Cole 2022, à confirmer en § 1).
4. **Plafond du marché carbone européen (EU ETS).** La production d'électricité fossile des
   voisins (et de la France) est sous plafond. Avec le plafond fixe, des émissions
   supplémentaires dans le secteur électrique sont compensées ailleurs dans le système
   (« effet lit d'eau ») ; depuis la réserve de stabilité et la règle d'invalidation, le
   plafond cumulé dépend des émissions passées et l'effet est partiellement rétabli (Perino,
   *Nature Climate Change* 8, 262-264, 2018, doi:10.1038/s41558-018-0120-2 ; réponse de
   Rosendahl, *Nature Climate Change* 9, 734-735, 2019, doi:10.1038/s41558-019-0579-5, et
   réplique de Perino, *ibid.* 736 ; Bruninx et Ovaere, *Nature Communications* 13, 1165,
   2022, doi:10.1038/s41467-022-28398-2, qui écrivent : « Our results crucially depend on when
   the waterbed will be sealed again, which is an endogenous market outcome »). Références
   vérifiées sur Crossref et PubMed Central ; articles de Perino et Rosendahl non lus en texte
   intégral (accès payant). Conséquence : C4 mesure des émissions **physiques de court
   terme** ; dire qu'elles « s'ajoutent au climat » demande une phrase sur l'ETS. Une experte
   le demandera.
5. **Direct ≠ ACV.** C1-C4 sont en direct. Si l'on cite une ACV (RTE annexe, ADEME, GIEC
   AR5), le dire, et ne jamais comparer une ACV française (nucléaire 4 à 12 g) à un direct
   étranger. La biomasse est à 0 en direct par convention ; en ACV, 66 à 890 g selon la
   source.
6. **CO2 ≠ CO2eq.** ISPRA (Italie) et UBA (CO2 seul en tête) ne sont pas en CO2eq : ne pas
   mélanger dans un recoupement sans le dire.
7. **Production ≠ consommation** au dénominateur : UBA rapporte à la consommation (344 g en
   2025), RTE et nous à la production (284 à 286 g).
8. **Décalage d'une heure ENTSO-E FR en 2023-2024** : ne jamais prendre la France dans A75 ou
   A65 ; éCO2mix fait foi. Les voisins ne montrent pas de décalage d'une heure au test
   grossier, ce qui ne prouve pas leur exactitude horaire.
9. **Endogénéité de la disponibilité nucléaire déclarée** (§ 2.6) : arrêts pour modulation
   déclarés comme indisponibilités planifiées. Ne jamais s'en servir comme choc exogène.
10. **Météo commune** : toute régression des émissions voisines sur la consommation française
    donne un chiffre faux et précis (0,6 à 0,95 t/MWh).
11. **Flow-based** : « couplée à l'Allemagne » ne dit plus grand-chose depuis 2022 ; un tiers
    des heures sont « entre ». Ne pas attribuer une unité marginale par simple égalité de prix.
12. **Hydraulique de stock** : l'énergie turbinée en plus aujourd'hui manque plus tard ; les
    émissions de ce report ne sont pas dans une régression horaire ou journalière.
13. **Unités** : les régressions sortent des t/h par MW, c'est-à-dire des t/MWh ; une
    consommation plate de 1 GW fait 8,76 TWh/an (8,784 les années bissextiles).

### 3.6 Hors de portée, et ce qui rapprocherait

| Hors de portée aujourd'hui | Ce qu'il faudrait | Coût estimé |
|---|---|---|
| Part des exportations perdues remplacée par quoi (pondérer C4) | (1) variable instrumentale à la Beltrami et al. (2025) : l'éolien des voisins déplace les échanges indépendamment de la demande française (données déjà là) ; (2) charge réalisée des voisins (A65, même jeton) et températures (Météo-France ou réanalyse) comme contrôles de l'expérience naturelle ; (3) production NL, AT, PL, CZ, DK | faible pour (1), moyen pour (2) et (3) : téléchargement ENTSO-E déjà industrialisé |
| Technologie marginale horaire par le prix | prix du gaz, du charbon, du CO2 (TTF, API2 : non ouverts) | bloqué par la licence |
| Marginal de court terme par modèle de dispatch couplé | un modèle européen (PyPSA-Eur, Antares) et ses données | élevé ; hors d'un site d'observation |
| Marginal de long terme | modèle d'investissement ; on cite RTE et la littérature | hors de portée, citation seulement |
| Effet net sur les émissions européennes sous plafond ETS | modèle du marché des quotas | hors de portée ; phrase sourcée (§ 3.5, point 4) |
| Corse | éCO2mix ne la couvre pas | limite écrite |

### 3.7 Doutes et ce que je n'ai pas pu vérifier

- Les facteurs centraux sont ceux du **parc français** appliqués à l'Allemagne et à l'Italie :
  le lignite allemand est à 1 119 g pour l'UBA contre 961 chez RTE.
- Le contenu des catégories « autres » (B20) et « déchets » (B17) des voisins est inconnu ; la
  part fossile des déchets (50 %) est une hypothèse.
- La lecture « arrêts pour modulation » repose sur une recherche de mots dans le champ
  d'information complémentaire (« combustible », « modulation », « économi… »,
  « optimisation ») : 928 événements, dont des essais à puissance stable ; le volume exact
  d'indisponibilité **économique** n'est pas isolé.
- Les décompositions de C3 n'ont pas d'intervalle sur la moyenne des quatre saisons (seulement
  par saison).
- L'échantillon « découplée vers le bas » de 2022 est vide : C2 n'a pas de sens cette année-là
  autrement que « 0 ».
- Le seuil de convergence (0,01 €/MWh) sur des moyennes horaires de quarts d'heure depuis le
  1er octobre 2025 peut classer « entre » une heure couplée trois quarts d'heure sur quatre ;
  effet non mesuré.
- Les parts de C2 utilisent `nucleaire_disponible`, en partie endogène (§ 2.6).

