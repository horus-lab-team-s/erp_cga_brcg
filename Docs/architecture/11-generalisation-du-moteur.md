# 11 · Généralisation du moteur d'évaluation

Journal du chantier qui détache le moteur de règles du contexte Conformité pour en faire
un noyau partagé, capable de servir quatre usages : contrôler la conformité d'une pièce,
chiffrer une prestation, évaluer la charge d'un dossier, surveiller le fonctionnement
interne.

**Convention.** Contrairement aux autres journaux du dépôt, les entrées sont ici en
**ordre chronologique croissant** : c'est une séquence de pas dont chacun dépend du
précédent, et la lire à l'envers n'aurait pas de sens. Chaque entrée dit ce qui a été
fait, pourquoi, ce qui a été écarté, et l'état de la suite de tests à la fin du pas.

**Pourquoi ce chantier.** La conception cible décrit un moteur unique configuré quatre
fois. La revue du code a montré qu'il existait déjà, mais soudé à un seul domaine :
`MoteurConformite` contrôle un objet `FactureAControler` et produit une
`ConsequenceFiscale`. Il s'agit donc d'une **généralisation d'un code éprouvé**, pas d'un
développement depuis zéro — et les tests existants servent de filet pendant l'opération.

**Les six pas.**

| Pas | Objet | État |
|---|---|---|
| 1 | Créer le paquet partagé, y déplacer l'évaluateur sans le modifier | ✅ fait |
| 2 | Poser les garde-fous d'architecture du noyau | ✅ fait |
| 3 | Introduire le sujet et le schéma de faits | ✅ fait |
| 4 | Typer la conséquence | ✅ fait |
| 5 | Extraire l'agrégateur | ✅ fait |
| 6 | Prouver la généralité sur un second domaine | ✅ fait |

---

## 9 septembre 2026 — Point de départ

**Mesure de référence prise avant toute modification**, pour que chaque pas puisse être
comparé à quelque chose :

```
1150 passed, 38 skipped, in 16.74s
```

**Ce qui existait.** Un évaluateur JSONLogic restreint dans
`app/contextes/conformite/domaine/jsonlogic.py`, écrit selon les bons principes : liste
d'opérateurs explicite et close, aucune exécution de code arbitraire, expressions
régulières compilées puis mises en cache. Son commentaire d'en-tête dit déjà
« un prédicat est une structure de données, pas un programme ».

**Ce qui était soudé au domaine.** En relisant la boucle de contrôle, trois choses
seulement :

| Lié à la facture | Ce que ça devient |
|---|---|
| `facture.donnees_predicat()` | Une méthode que tout sujet fournit |
| `regle.concerne(facture)` | Un filtre de portée évalué sur les faits |
| `calculer_enjeu(consequence, facture)` | Une stratégie de valorisation par type de conséquence |

Tout le reste était déjà générique : filtre par date de vigueur, exclusion des règles
abrogées, résolution des paramètres à la date, rattrapage des règles en échec, collecte
des paramètres employés pour rendre le rapport rejouable.

---

## Pas 1 — Le déplacement, sans modification

**Fait.** `app/contextes/conformite/domaine/jsonlogic.py` déplacé en
`app/moteur/jsonlogic.py`, avec un `__init__.py` qui déclare la portée du paquet.
Trois références mises à jour, une ligne chacune :

* l'import dans `moteur_conformite.py` ;
* l'import dans `tests/test_jsonlogic.py` ;
* le chemin en dur dans `tests/test_integrite_referentiel.py`, qui liste les fichiers où
  aucune valeur légale ne doit apparaître.

**La condition qu'on s'est fixée.** Le contenu du fichier ne devait pas changer d'un
octet. Empreinte SHA-256 vérifiée avant et après : `8b1c86d6…`, identique. Git l'a
enregistré comme un renommage pur, `0 insertions, 0 deletions`.

**Pourquoi cette discipline.** Un déplacement et une modification dans le même pas rendent
impossible d'attribuer une régression à l'un ou à l'autre. Séparés, le premier se relit en
trente secondes et le second se relit sur un diff propre.

**Pourquoi `app/moteur/` et non `app/partage/`.** `partage` porte de petits utilitaires
(formats, horloge, téléphone). Le noyau d'évaluation n'est pas un utilitaire : il est le
cœur du produit, il a sa propre discipline, et il mérite un paquet dont le nom la dit.

**Écarté.** Laisser un module de compatibilité à l'ancien emplacement. Trois références
seulement, et un alias survit toujours plus longtemps que prévu.

```
1150 passed, 38 skipped — identique à la référence, aucun test touché
```

---

## Pas 2 — Les garde-fous, posés avant la suite

**Fait.** Quatre tests dans `TestNoyauMoteur`, ajoutés à `tests/test_architecture.py`.

| Test | Ce qu'il interdit |
|---|---|
| `test_le_paquet_existe_et_declare_sa_portee` | Un paquet sans docstring, donc sans contrat écrit |
| `test_le_noyau_n_importe_aucun_contexte_metier` | Toute importation de `app.contextes.*` |
| `test_le_noyau_ne_depend_d_aucune_infrastructure` | Une base, une horloge, un réseau |
| `test_le_noyau_n_execute_aucun_code_arbitraire` | `eval`, `exec`, `compile`, `__import__` |

**Pourquoi maintenant et pas après.** Le noyau ne tient sa promesse que tant qu'il ignore
ce qu'est une facture. La première importation d'un contexte métier le rendrait
inutilisable par les trois autres usages, et personne ne s'en apercevrait avant d'essayer.
Après la généralisation, il n'y aurait plus rien à protéger : la dérive aurait déjà eu
lieu.

**Le quatrième test mérite un mot.** Il ferme d'avance la porte que la conception décrit
comme la façon de tout perdre. Le jour où un cas résistera à l'expression déclarative, la
tentation sera de charger une fonction Python depuis le référentiel. La suite refusera, et
forcera la bonne réponse : **ajouter un opérateur au noyau**, écrit une fois et testé,
plutôt qu'ouvrir une échappatoire.

**Les garde-fous ont été éprouvés, pas seulement écrits.** Deux sondes injectées
temporairement dans `jsonlogic.py` — un import de `conformite.domaine.entites`, puis un
appel à `eval` — font bien échouer la suite avec le message attendu. Fichier restauré,
empreinte revérifiée. Un garde-fou qu'on n'a pas vu échouer ne garde rien.

```
1154 passed, 38 skipped — les 4 nouveaux tests
```

---

## Pas 3 — Le sujet et le schéma de faits

**Fait.** Trois modules neufs et un renommage.

* **`app/moteur/faits.py`** — le protocole `Sujet`, `SchemaDeFaits`, `Fait`, `TypeFait`,
  `ErreurSchema`.
* **`app/moteur/chemins.py`** — `chemins_cites`, l'extraction des faits qu'un prédicat
  interroge, sans l'évaluer.
* **`app/contextes/conformite/domaine/schema_faits.py`** — `SCHEMA_FACTURE`, 27 faits
  déclarés. Le premier adaptateur.
* `FactureAControler.donnees_predicat()` renommé en `faits()`, deux appels touchés.

**Le protocole tient en une méthode**, `faits() -> Mapping[str, Any]`. Délibérément :
chaque exigence supplémentaire serait une raison de plus pour un domaine de ne pas pouvoir
employer le moteur. `issubclass(FactureAControler, Sujet)` rend `True` sans que la facture
hérite de quoi que ce soit.

**À quoi sert le schéma.** À refuser une règle mal écrite **au chargement**. Sans lui, une
règle qui interroge `montants.total_htt` au lieu de `montants.total_ht` ne provoque aucune
erreur visible : le fait manquant vaut absent, la comparaison rend faux, et un constat part
sur chaque pièce contrôlée. L'erreur est d'un caractère, le préjudice est un adhérent à qui
l'on reproche une anomalie qui n'existe pas.

### Le piège trouvé en écrivant, et absent de la conception

Les opérateurs itératifs — `some`, `none`, `all`, `map`, `filter` — **changent la portée
des `var`**. Leur second argument s'évalue dans le contexte d'un élément :

```json
{"some": [{"var": "lignes"}, {"==": [{"var": "designation"}, ""]}]}
```

`designation` n'est pas un fait racine, c'est un champ d'un élément de `lignes`. Un
extracteur naïf l'aurait rendu comme un chemin racine, le schéma l'aurait déclaré inconnu,
et le garde-fou aurait refusé une règle correcte. Le réflexe aurait alors été de désactiver
le garde-fou — c'est-à-dire de perdre tout le bénéfice pour un défaut d'extraction.

**Convention retenue :** le suffixe `[]` sur la collection, `lignes[].designation`. La même
des deux côtés, de sorte que le schéma et l'extracteur se comparent sans traduction.

Deux cas rendent volontairement l'ensemble vide plutôt qu'un chemin deviné : `{"var": ""}`,
qui désigne le sujet courant et non un fait nommé, et un `var` dont l'argument est calculé
à l'évaluation. **Le garde-fou préfère laisser passer un cas qu'il ne comprend pas à
refuser une règle valable.**

### La validation est branchée là où elle sert

Dans `MoteurConformite.__init__`, pas seulement dans les tests. Monter le moteur avec une
règle fautive échoue immédiatement :

```
la règle FAC-SONDE-999 cite un fait que le domaine « CONFORMITE_FACTURE »
ne déclare pas : « montants.total_htt » (voulez-vous dire « montants.total_ht » ?).
Déclarer le fait au schéma, ou corriger le prédicat.
```

La suggestion du fait voisin coûte une distance d'édition écrite à la main, quinze lignes,
et fait gagner un quart d'heure à chaque faute de frappe. Elle vaut son prix.

Les cinq règles réelles du référentiel valident, **y compris le cas itératif** de
`FAC-DOC-011` qui cite `lignes` et `lignes[].designation`.

### Une décision prise en cours de route

Pydantic enveloppe les erreurs levées dans un validateur de modèle : `ErreurSchema` ne
remonte telle quelle que depuis `valider_predicat`, pas depuis la construction d'un `Fait`.
C'est le comportement attendu de la bibliothèque, et le message reste ce qui porte
l'information. **On ne se bat pas contre elle pour un type d'exception** : la distinction
est documentée dans la docstring d'`ErreurSchema`, et les tests reflètent ce qui se produit
vraiment plutôt que ce qu'on aurait voulu.

```
1182 passed, 38 skipped — 28 nouveaux tests
ruff : All checks passed
```

---

## Pas 4 — La conséquence typée, et le chiffrage sorti du noyau

**Fait.** `ConsequenceFiscale` cesse d'être *la* conséquence pour devenir *une*
conséquence.

* **`app/moteur/consequence.py`** — `TypeConsequence` à quatre natures, `Consequence`,
  le port `Valorisation`, et deux valorisations fournies : `sans_enjeu` et
  `enjeu_declare`.
* **`app/contextes/conformite/domaine/valorisation.py`** — `valoriser_fiscalement`,
  l'ancien `calculer_enjeu` déplacé et réécrit pour lire les faits.
* `ConsequenceFiscale` hérite désormais de `Consequence`, avec `type` valant MONTANT.
* `MoteurConformite` reçoit la valorisation en argument, par défaut celle du domaine
  fiscal.
* `lire` exposée dans `jsonlogic.py` : le lecteur de chemin existait déjà en privé.

### Les quatre natures, et pourquoi trois d'entre elles se passent de calcul

| Nature | Qui porte la valeur | Pourquoi |
|---|---|---|
| MONTANT | Les faits du sujet | Ce qu'une facture non conforme coûte dépend de ses montants |
| POINTS | La règle | Un critère de charge qui vaut dix-huit points en vaut dix-huit quel que soit le dossier |
| NIVEAU | La règle | Un risque élevé est élevé, il ne se calcule pas |
| AJUSTEMENT | La règle | Le barème fixe la variation, le prédicat décide si elle s'applique |

C'est ce déséquilibre qui justifie le port : **une seule des quatre natures a besoin du
sujet pour se chiffrer.** Une fonction unique dans le noyau aurait donc porté la logique
d'un seul domaine au nom de tous.

### Deux décisions prises en écrivant

**La valorisation reçoit les faits, pas le sujet.** Elle ne peut donc pas aller chercher
un champ que les règles n'ont pas le droit d'interroger. Sans cette contrainte, un
chiffrage finirait par dépendre d'une donnée invisible aux règles, et deux constats issus
de la même facture cesseraient d'être explicables par les mêmes faits.

**Un seul lecteur de chemin.** `valoriser_fiscalement` lit `montants.total_ttc` avec la
fonction qu'emploient les prédicats, exposée pour l'occasion. Deux lecteurs auraient
divergé un jour sur un cas limite — une clé absente, un indice de liste — et le constat
produit n'aurait plus correspondu à la règle qui l'a déclenché.

### Le cas qu'il ne faut pas rater

`aucun rejet → aucun enjeu`, et surtout pas zéro. Un constat qui ne rejette ni la taxe ni
la charge signale une irrégularité de forme sans conséquence chiffrable. **Afficher
« 0 FCFA » laisserait croire à un enjeu nul là où il n'y a pas d'enjeu du tout**, et un
réviseur en déduirait qu'il peut passer. Un test porte ce cas nommément.

### La preuve que le pas a atteint son but

`TestValorisationInjectable` monte deux moteurs sur les mêmes règles, l'un avec la
valorisation fiscale et l'autre avec une valorisation étrangère qui rend un point par
constat. Les deux produisent **les mêmes constats** — changer le chiffrage ne change pas
quelles règles se déclenchent — et **des enjeux différents**. Tant que ce test n'existait
pas, l'injection était une intention ; elle est maintenant une propriété vérifiée.

Les tests de bout en bout qui portaient déjà sur l'enjeu passent inchangés :
`test_collecte.py` attend toujours 379 350 FCFA, désormais calculés à travers le port.

### Un test réécrit plutôt que forcé

`Valorisation` n'a que `__call__`. Un `isinstance` sur ce protocole ne dirait que « c'est
appelable », ce que n'importe quelle fonction satisfait. Plutôt que de rendre le protocole
`runtime_checkable` pour faire passer une vérification qui ne vérifie rien, le test porte
sur le **comportement** : chaque valorisation accepte le couple attendu et rend un nombre
ou rien.

```
1201 passed, 38 skipped — 19 nouveaux tests
ruff : All checks passed
```

---

## Pas 5 — L'agrégateur, et la découverte qui le justifie

**Fait.** `app/moteur/agregation.py` : le protocole `ConstatEvalue`, le modèle `Agregat`,
le port `Agregateur`, et quatre agrégateurs. `RapportConformite.enjeu_total` et
`severite_maximale` délèguent désormais au noyau.

### Ce qu'un agrégateur exige d'un constat

Trois attributs : `severite`, `enjeu`, `consequence`. Pas un de plus. Le libellé, le
fondement et la remédiation intéressent celui qui lit le rapport ; ils n'entrent dans
aucun calcul. Les tests de ce module s'écrivent donc avec un `dataclass` de trois champs,
**sans importer aucun domaine** — c'est la démonstration que l'agrégation n'en connaît
aucun.

### La découverte qui justifie tout le pas

En écrivant les deux premiers agrégateurs, une chose est apparue qui n'était pas dans la
conception : **la conformité ne fait pas de somme.**

```python
enjeu_maximal()([constat(19_250), constat(19_250)]).valeur   # 19 250
somme_des_enjeux()([constat(19_250), constat(19_250)]).valeur # 38 500
```

Deux règles qui rejettent toutes deux la taxe d'une même facture ne la rejettent pas deux
fois : l'enjeu reste le montant de la taxe. Additionner produirait un chiffre supérieur au
préjudice réel — et un chiffre faux dans ce sens-là est celui qu'un adhérent conteste en
premier, à raison.

La charge, elle, additionne : deux critères qui pèsent chacun dix points en pèsent vingt.

**Aucune règle générale ne départage ces deux comportements.** C'est exactement pourquoi
l'agrégation devait sortir du noyau plutôt que d'y être écrite une fois pour toutes. Un
test porte nommément ce contraste : les mêmes constats, deux conclusions, toutes deux
justes.

### Les quatre agrégateurs

| Agrégateur | Domaine | Ce qu'il rend |
|---|---|---|
| `enjeu_maximal` | Conformité | Le plus grand enjeu, sans addition |
| `somme_des_enjeux` | Charge | La somme des points |
| `niveau_le_plus_eleve` | Contrôle interne, et sévérité d'un rapport | Le niveau le plus haut atteint |
| `intervalle_autour` | Tarification | Une base ajustée, encadrée par ses bornes |

Ce sont des **fabriques** et non des fonctions : `niveau_le_plus_eleve` a besoin d'un
ordre, `intervalle_autour` d'une base et de deux amplitudes. Une signature unique aurait
obligé à passer des arguments inutilisés aux deux autres.

### Trois décisions prises en écrivant

**L'ordre des niveaux est passé, jamais deviné.** Le noyau ne peut pas supposer
qu'« ELEVE » précède « CRITIQUE » alphabétiquement — c'est faux — ni que les niveaux sont
des entiers — c'est faux aussi. `niveau_le_plus_eleve` reçoit l'ordre du domaine. Au
passage, il sert deux usages : le contrôle interne et la sévérité maximale d'un rapport de
conformité, qui est le même calcul sur une autre échelle.

**Un niveau inconnu est ignoré du classement mais reste dénombré.** Mieux vaut un rapport
incomplet sur ce point qu'une exception au moment de conclure : le constat existe, et le
taire serait pire que mal le classer.

**L'agrégateur tarifaire ne retient que les ajustements.** Sans ce filtre, un enjeu fiscal
qui se glisserait dans le même rapport modifierait des honoraires. Un test porte ce cas.

### Ce que l'agrégateur n'est pas

Il ne décide pas. Un agrégateur qui suspendrait un dossier au delà d'un seuil mêlerait le
constat et la sanction, et la partie « constat » cesserait d'être rejouable sans effet de
bord. Il rend un `Agregat` ; ce qu'on en fait se décide ailleurs. C'est le principe n° 3
appliqué à l'autre bout de la chaîne.

### Un détail corrigé avant qu'il ne coûte

Le champ de dénombrement s'appelait d'abord `dénombrement`, avec accent. Python l'accepte,
les outils moins bien. Renommé sans accent avant le premier usage.

```
1223 passed, 38 skipped — 21 nouveaux tests
ruff : All checks passed
app/moteur/ : 963 lignes
```

---

## Pas 6 — La preuve

**Fait.** Un second domaine tourne sur le même moteur : l'évaluation de charge d'un
dossier.

* `app/moteur/evaluation.py` — la boucle, extraite du contexte Conformité.
* `app/contextes/portefeuille/domaine/charge.py` — schéma de faits, `DossierAEvaluer`,
  `RegleDeCharge`, les quatre tranches.
* `app/contextes/portefeuille/application/evaluation_charge.py` — le cas d'usage.
* `app/contextes/portefeuille/adaptateurs/sortant/grille_de_charge.py` — le chargeur.
* `Docs/referentiel/charge/` — sept critères en YAML, plus leur README.

### La boucle devait sortir, sinon « le même moteur » n'était qu'une figure de style

Tant que la boucle vivait dans le contexte Conformité, les quatre usages auraient partagé
des briques, pas un mécanisme. Elle est maintenant dans le noyau, avec **trois ports** qui
remplacent chacun un endroit où elle savait quelque chose de la fiscalité :

| Port | Ce qu'il remplace |
|---|---|
| `resolveur` | Savoir lire un paramètre daté au référentiel |
| `valorisation` | Savoir chiffrer une conséquence |
| `ignorer` | Savoir ce qui rend une règle inapplicable |

Le dernier mérite un mot. Une règle abrogée doit être écartée, mais « abrogée » est un
vocabulaire de référentiel, pas de moteur. Le domaine passe `ignorer`, et **la boucle ne
sait pas ce qu'elle écarte**.

La portée a suivi le même mouvement : `Regle.concerne` reçoit désormais les faits et non
la facture. Une portée qui lirait un champ absent du schéma écarterait des règles pour une
raison invisible à leur auteur.

### Ce que la boucle rend, et pourquoi ce n'est pas un constat

Elle rend des **déclenchements**, que le domaine habille. C'est ce qui lui permet de servir
un rapport de conformité riche — libellé, sévérité, fondement, remédiation — et un simple
score de charge, sans connaître ni l'un ni l'autre.

### Le second domaine diffère sur quatre points

| | Conformité | Charge |
|---|---|---|
| Sujet | Une pièce | Un dossier |
| Unité | Des francs | Des points |
| Agrégation | Le maximum | La somme |
| Paramètres datés | Résolus au référentiel | Aucun |

Le dernier est instructif : les seuils d'une grille de charge appartiennent au centre, qui
les révise quand il veut sans qu'aucune loi ne l'y oblige. Ils vivent donc dans les règles
plutôt qu'au référentiel, et le résolveur par défaut du moteur suffit.

**Rien n'a été ajouté au noyau pour accueillir ce domaine.** C'est la seule formulation de
la réussite qui vaille : une abstraction qu'il faut retoucher au deuxième usage n'en était
pas une.

### Le résultat, confronté à la conception

La station-service de la section 14 du document de conception :

```
CHG-BAN-001      6  Plusieurs comptes bancaires à rapprocher
CHG-ETA-001      8  Plusieurs établissements distincts
CHG-QUA-001      5  Pièces fournies mal classées
CHG-REG-001     12  Régime du réel normal
CHG-SAL-001     10  Dix salariés ou plus en paie
CHG-VOL-002     18  Volume de pièces mensuel supérieur à 200
SCORE           59  tranche Soutenu, 2,5 jours/mois
```

Cinquante-neuf points, tranche soutenue. Le chiffre annoncé par la conception, produit par
le code.

### Une convention qui surprend et qu'on garde

Un prédicat exprime la **normalité** : vrai = rien à signaler, faux = déclenchement. Pour
la charge, cela oblige à écrire « le volume est inférieur à deux cents » afin de compter
les gros volumes. La formulation déroute au premier abord.

On l'a gardée. Changer de convention pour un domaine reviendrait à avoir deux moteurs, et
l'inconfort d'une lecture inversée coûte moins cher qu'une exception à retenir.

```
1247 passed, 38 skipped — 24 nouveaux tests
ruff : All checks passed
app/moteur/ : 1 152 lignes en 6 modules
```

---

## Recadrage — remettre le second domaine dans la cohérence de base

Le pas 6 avait laissé trois points hors des principes du projet, signalés en fin de
chantier comme « ce qui reste ». C'était une facilité : un principe qu'on suspend pour le
premier usage devient un principe qu'on suspend pour tous.

### Ce qui n'allait pas

| Point | Principe enfreint |
|---|---|
| `RegleDeCharge` sans fondement ni statut | N° 2 · fondement obligatoire sur chaque règle |
| `TRANCHES` écrit en dur dans le domaine | N° 1 · aucune valeur en dur, et le principe de configuration |
| Rien ne signalait qu'un score n'est pas opposable | La discipline du contreseing, tenue partout ailleurs |

J'avais justifié le premier point par « un critère de charge relève d'une grille interne,
pas d'un texte ». C'est vrai du **caractère** du fondement, pas de son existence. La raison
d'être du principe vaut identiquement ici : un responsable qui annonce un score sans
pouvoir dire d'où viennent ses points ne peut pas le défendre devant un client qui trouve
ses honoraires élevés. Le document de conception donnait d'ailleurs déjà l'exemple correct
en section 12, avec `valide_par: Direction de production` — je ne l'avais pas implémenté.

### Ce qui a été corrigé

**Un critère porte désormais fondement, statut, signataire et date**, exactement comme une
règle fiscale. Son validateur refuse un critère `VALIDE` sans `valide_par` ni `valide_le`,
et refuse aussi un critère qui pèse zéro point — il n'aurait pas lieu d'être.

Les sept critères de la grille portent leur fondement : « Grille de charge interne,
révision 1, critère "qualité des dépôts". Constat de production : un client qui apporte un
sac coûte environ deux fois le temps d'un client qui apporte des pièces classées. »

**Les tranches ont quitté le code** pour `Docs/referentiel/charge/tranches.yaml`, avec
leur propre fondement et leur statut. Un test interdit leur retour : il relit le source du
domaine et échoue si `minimum=0` y réapparaît. Un garde-fou qui ne surveille pas la
régression n'empêche que la première faute.

**L'évaluation dit quand elle n'est pas opposable.** `repose_sur_des_criteres_non_valides`
est l'équivalent exact de `repose_sur_des_valeurs_non_validees` côté conformité. Tant que
la grille porte `A_VALIDER`, le score sert à répartir la charge en interne, jamais à
justifier un honoraire devant un client.

Nuance tenue par un test : un dossier qui n'atteint aucun critère **n'est pas** marqué
douteux. Marquer ce cas ferait douter d'un score qui ne repose sur rien.

### Le point que je ne corrige pas, et pourquoi

Le troisième reste : les schémas de faits vivent dans leur domaine et non au référentiel.
Le document de conception annonçait l'inverse ; l'implémentation a montré que
c'était l'annonce qui était imprécise.

Un schéma de faits décrit ce que le **sujet** expose, et le sujet est du code. Le sortir en
donnée créerait une dérive possible entre deux artefacts qui doivent bouger ensemble. Un
paquet de règles varie sans le code ; un schéma de faits, non.

Le test `test_le_schema_couvre_ce_que_le_sujet_expose` tient déjà cette correspondance.
**C'est la conception qu'il faut corriger sur ce point, pas le code.**

```
1256 passed, 38 skipped — 9 tests de discipline ajoutés
ruff : All checks passed
```

---

## Le chantier est terminé

Six pas, de la mesure de référence à la preuve. **1 150 tests au départ, 1 247 à
l'arrivée, aucune régression à aucun pas.**

Ce qui existe maintenant : un noyau d'évaluation qui ne connaît ni facture, ni impôt, ni
monnaie, protégé par quatre garde-fous d'architecture éprouvés, et deux domaines qui
tournent dessus.

**Ce que cela achète.** La tarification et le contrôle interne ne sont plus des chantiers
mais des paquets de règles à écrire : un schéma de faits, des fichiers YAML, une
valorisation et un agrégateur choisis parmi ceux qui existent. Et le jour où la plateforme
s'adresse à un autre secteur, le travail est de la configuration, pas du développement.

### Ce qui reste, et qui n'est pas de ce chantier

* **La grille réelle.** Les sept critères, leurs points et les quatre tranches viennent de
  la conception, pas du centre. Ils portent tous `A_VALIDER`, et l'évaluation le dit. À
  remplacer dès réception de la grille, **sans toucher au code** : c'est précisément ce
  que le recadrage a rendu possible.
* **Les deux domaines restants.** Tarification et contrôle interne, quand leurs barèmes et
  leurs politiques seront connus. Le travail sera un schéma de faits, des fichiers de
  règles, une valorisation et un agrégateur choisis parmi ceux qui existent.
