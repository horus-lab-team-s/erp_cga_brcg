# 13 · Parcours d'acquisition

Journal du chantier qui construit le chemin par lequel une intention devient un client :
du formulaire déposé sur la vitrine publique jusqu'au paiement qui déclenche l'ouverture
d'un tenant.

**Convention.** Comme pour [11](11-generalisation-du-moteur.md) et
[12](12-socle-multi-tenant.md), les entrées sont en ordre chronologique croissant. Chaque
pas dépend du précédent, et ce qui a été corrigé en chemin est écrit avec ce qui l'a
révélé.

**Pourquoi ce chantier maintenant.** Le socle multi-tenant est posé, éprouvé et fermé
(voir [12](12-socle-multi-tenant.md)). Il garantit deux choses dont ce parcours a besoin
de bout en bout : qu'une demande arrivant **sans tenant** — un visiteur anonyme sur le
site public — se range chez le locataire du centre, et qu'un encaissement pourra
déclencher l'ouverture d'un sous-domaine. Les pièces existent ; ce chantier écrit ce qui
les relie.

**Le contexte concerné.** Le parcours vit dans **M**, nommé `souscription` dans le code et
« Commerce » dans le document de conception. Le nom du répertoire n'a pas été changé : un
renommage de contexte touche les imports de quatorze modules, le test d'architecture et
les migrations, pour un gain purement nominal. La correspondance est notée ici, et c'est
suffisant.

**Les pas.**

| Pas | Objet | État |
|---|---|---|
| 1 | La demande de contact, le consentement, le doublon | ✅ fait |
| 2 | Le dossier commercial et ses huit états | ✅ fait |
| 3 | Le port, les deux dépôts, la table et sa migration | ✅ fait |
| 4 | L'affectation à un responsable | ✅ fait |
| 5 | Le fil de conversation et la fenêtre WhatsApp | ✅ fait |
| 5 bis | **Recadrage** : aucune plateforme extérieure n'est bloquante | ✅ fait |
| 6 | La qualification typée | ✅ fait |
| 7 | Le socle d'orchestration : saga, boîte d'envoi, branchement HTTP | ✅ fait |
| 8 | Le relais, le provisionneur, et l'événement qui relie tout | ✅ fait |
| 9 | Le chiffrage par le moteur | ✅ fait |
| 10 | La proforma, son immuabilité et son acceptation | ✅ fait |
| 11 | L'encaissement, la relance graduée, et la boucle refermée | ✅ fait |

---

## 9 septembre 2026 — Point de départ

```
1536 passed          (avec PostgreSQL)
1458 passed, 78 skipped   (sans)
```

---

## Pas 1 — La demande de contact

**Fait.** Le premier objet du parcours, celui que dépose un visiteur depuis la vitrine
publique.

* `app/contextes/souscription/domaine/demande_de_contact.py`
* `tests/test_demande_de_contact.py` — 45 cas

### Ce qu'elle n'est pas, et c'est ce qui a dicté le reste

Le document de conception dit d'elle qu'elle n'est « ni un compte, ni un client, ni un
dossier ». La phrase a l'air d'une précaution rhétorique ; elle a en fait trois
conséquences très concrètes, et chacune se lit dans le code :

* aucune `Entreprise` du contexte B n'est créée, et aucun NIU n'est réclamé ;
* aucun compte n'est ouvert, aucun mot de passe n'est dérivé, aucun tenant n'est
  provisionné ;
* une demande sans suite se classe, elle ne se supprime pas.

Créer un compte au dépôt du formulaire produirait des milliers d'espaces vides à
surveiller, à purger et à protéger, sans qu'aucun ne corresponde à un client. C'est la
raison pour laquelle l'espace du client ne s'ouvre qu'à l'étape 9.

### Le consentement est un objet, pas un booléen

C'est la décision structurante de ce pas. Un `bool` aurait suffi à cocher une case ; il
n'aurait rien prouvé le jour où quelqu'un conteste.

`Consentement` porte trois choses qu'un booléen ne porte pas :

1. **la date** de recueil, qui fait foi ;
2. **la version du texte** affiché, versionnée au référentiel. Le texte évoluera, et un
   consentement recueilli sous l'ancien ne prouve rien sur le nouveau ;
3. **la révocation**, qui ne s'efface pas : elle s'enregistre, datée et motivée.

C'est la réponse **D5** du cadrage, mot pour mot : consenti, daté, révocable.

**La conséquence la moins évidente** est que `accorde` ne doit jamais être lu directement.
Un consentement révoqué a toujours `accorde is True` — c'est le fait historique, et il
reste vrai. Seul `vaut_maintenant` répond à la question que le reste du système a le droit
de poser. Un test vérifie explicitement ce piège, parce qu'il est exactement le genre de
raccourci qu'on prend en relisant vite.

### Deux invariants de canal, refusés au dépôt

* on ne peut pas préférer WhatsApp sans consentement **en vigueur** ;
* on ne peut pas préférer le courriel sans adresse.

Le lieu du refus compte autant que le refus. Au dépôt, cela se corrige en cochant une
case, devant le visiteur. À l'envoi, cela se découvre trois jours plus tard, sur le
tableau de bord d'un responsable qui croyait avoir écrit.

L'appel, lui, ne demande ni l'un ni l'autre : c'est pourquoi il est le canal de repli, et
c'est aussi pourquoi une révocation ne rend pas une demande intraitable — elle la fait
basculer vers l'appel.

### Pourquoi l'origine est une chaîne et non une énumération

La question de départage du projet, appliquée telle quelle : **« est-ce que cela varie
sans le code ? »**

Oui, et vite. Les sources d'arrivée sont des campagnes, des partenaires, des liens de
parrainage, des salons. Il en naîtra une par trimestre, décidée un vendredi soir. Une
énumération obligerait à déployer pour l'accueillir, et le vendredi soir on écrirait
« AUTRE ».

L'origine est donc une clé libre, normalisée (`Facebook Ads / Mars` et `facebook-ads-mars`
se rejoignent) et bornée, dont la liste connue vit au référentiel. **Une origine inconnue
n'est pas rejetée** : perdre une demande parce que la campagne n'a pas été déclarée serait
absurde, c'est le commercial qui a oublié, pas le visiteur.

Le `Canal`, à l'inverse, **est** une énumération, et pour la raison symétrique : chaque
canal suppose un adaptateur qui sait l'emprunter. Ajouter un canal, c'est écrire ce qui
l'emprunte. Cela ne varie pas sans code.

### Le doublon rapproche, il ne rejette pas

Le critère est **le numéro, et lui seul**. Pas le nom, qui s'écrit de quatre façons. Pas
le courriel, qui est facultatif. Pas le service souhaité, parce qu'un visiteur qui hésite
entre deux prestations n'a pas besoin de deux responsables : il en a besoin d'un, à qui
l'on dit qu'il hésite.

La fenêtre par défaut est de vingt-quatre heures, et c'est une **valeur par défaut**, pas
une constante : `doublon_parmi` accepte la fenêtre en argument. Le centre voudra l'ajuster
après trois mois d'usage réel, et ce changement ne doit demander ni déploiement ni
développeur.

Deux détails qui ne sautent pas aux yeux et qui ont chacun leur test :

* l'écart est **signé**. Sans borne basse, une demande déposée *après* celle qu'on examine
  passerait pour un doublon, ce qui arrive dès qu'un lot est rejoué dans le désordre ;
* on rattache à la **plus récente**, pas à la première trouvée. C'est le fil vivant, celui
  que le responsable a sous les yeux.

### Les garde-fous ont été éprouvés en les cassant

Neuf gardes du module ont été retirées une à une, et la suite relancée à chaque fois.
Chacune a produit au moins un échec. Un test qui passe aussi bien avec que sans le code
qu'il prétend vérifier ne vérifie rien, et la seule façon de le savoir est d'essayer.

---

## Pas 2 — Le dossier commercial

**Fait.** Ce que le cabinet fait d'une demande, de son dépôt à son paiement.

* `app/contextes/souscription/domaine/dossier_commercial.py`
* `tests/test_dossier_commercial.py` — 58 cas

### Pourquoi un objet de plus, alors que la demande existe déjà

Parce qu'ils n'ont ni la même durée de vie ni la même nature.

La `DemandeDeContact` est **figée** : c'est ce que le visiteur a écrit, un vendredi soir,
et cela ne changera plus jamais. Le dossier commercial, lui, est ce que le cabinet en
fait, et il change à chaque échange.

Les fondre obligerait à réécrire la demande à mesure que le dossier avance, et ferait
disparaître ce que le client avait réellement dit — qui est souvent la seule chose qui
explique un malentendu trois semaines plus tard.

### Le graphe est déclaré en un seul endroit

`TRANSITIONS` associe à chaque état l'ensemble de ceux vers lesquels on peut aller, et
**une seule méthode** le consulte. Répartir la vérification dans chaque transition
donnerait neuf endroits où l'oublier, et l'oubli ne se verrait qu'en production, sur le
dossier d'un client qui aurait sauté une étape.

Le graphe est en code, contrairement aux délais, et la raison est la même que pour le
`Canal` : chaque arête suppose quelque chose qui l'emprunte. Une transition vers
`PROFORMA_ÉMISE` suppose un générateur de proforma ; ajouter l'arête sans lui ne
produirait qu'un état où le dossier se bloque.

Trois propriétés du graphe méritent d'être lues :

* **on ne classe pas sans suite ce qui a été accepté.** Une proforma acceptée qui reste
  impayée retourne en conversation, elle ne disparaît pas. Le client s'est engagé ; le
  cabinet lui redemande, il ne l'oublie pas. C'est la seule différence notable entre
  `ACCEPTÉE` et les états qui la précèdent ;
* **`PAYÉE` est terminal**, parce que la suite n'appartient plus au commerce : l'ouverture
  du tenant relève du contexte N ;
* **`SANS_SUITE` est terminal aussi.** Un client qui revient ne rouvre pas un dossier
  classé, il dépose une nouvelle demande. Rouvrir demanderait de décider chez quel
  responsable, avec quelle ancienneté, sous quelle veille, et aucune de ces trois réponses
  n'est évidente. Déposer de nouveau les rend toutes les trois triviales.

### Les délais de veille ne sont pas dans le domaine, et c'est le point du pas

Le document de conception donne un délai par état : deux heures pour être affecté,
vingt-quatre pour être contacté, sept jours sans échange avant relance. **Aucun de ces
nombres n'apparaît dans le code.**

Ce qui reste dans le domaine est la **forme** de la règle, qui ne varie pas : un dossier
est en souffrance quand il est resté trop longtemps dans son état. Ce qui vaut « trop »
est un paramètre daté du référentiel, passé en argument à `en_souffrance`.

Un test vérifie littéralement cette propriété : il lit le fichier source et échoue si un
`timedelta(...)` y apparaît hors commentaire. C'est le garde-fou le plus utile du lot,
parce qu'il tombera le jour où quelqu'un remettra « deux heures » en dur pour aller plus
vite. Un autre test montre la même ligne de code rendant deux verdicts opposés sur le même
dossier, selon la seule table de délais.

### Deux dates qui ne se recalculent pas, et pourquoi

`affecte_le` est la date à laquelle le cabinet a pris le dossier en charge. Une
réaffectation **ne la remet pas à zéro** : la remettre effacerait précisément le retard
qu'on cherche à mesurer.

`premier_echange_le` mesure la réactivité du cabinet. `premier_contact` est donc
rejouable : le deuxième message n'est pas un deuxième premier contact. Sans cette garde,
la date glisserait à chaque message et l'indicateur mesurerait le dernier échange, ce qui
est exactement l'inverse de ce qu'on lui demande.

Ces deux dates survivent aussi à un retour en conversation. Le dossier redescend ; le
cabinet ne redevient pas réactif pour autant.

### Un test trop indulgent, découvert en cassant le code

`en_souffrance` compte depuis `depuis_le`, l'entrée dans l'état courant, et non depuis la
date de dépôt. Le test qui prétendait le vérifier mesurait à vingt heures puis à
vingt-six, sur un dossier affecté à une heure : les deux façons de compter donnaient le
même verdict aux deux instants.

**Le test passait avec le code juste et avec le code faux.** Le défaut ne s'est vu qu'en
remplaçant volontairement `self.depuis_le` par `self.demande.deposee_le` pour voir si la
suite le remarquait. Elle ne le remarquait pas.

L'instant de vérification a été déplacé **entre** les deux échéances possibles :
vingt-quatre heures et demie après le dépôt, donc seulement vingt-trois et demie après
l'affectation. Le test distingue maintenant les deux, et le mutant échoue.

C'est la leçon la plus transférable du chantier : **une assertion qui donne le bon verdict
pour la mauvaise raison ressemble en tout point à une bonne assertion.** Seul l'essai de
la faire échouer les distingue.

---

## Pas 3 — Le port, les dépôts, la table

**Fait.** Ce qui permet au parcours de survivre à un redémarrage.

* `app/contextes/souscription/domaine/ports.py` — `DepotDossiersCommerciaux`
* `app/contextes/souscription/adaptateurs/sortant/depots_memoire.py` — `DepotDossiersMemoire`
* `app/contextes/souscription/adaptateurs/sortant/depots_sql.py` — `DepotDossiersSql`
* `app/contextes/souscription/adaptateurs/sortant/tables.py` — `TableDossierCommercial`
* `app/contextes/souscription/application/acquisition.py` — `deposer_une_demande`
* `alembic/versions/20260909_1930_table_du_dossier_commercial.py`
* `tests/test_acquisition.py` — 20 cas · `tests/test_acquisition_persistance.py` — 16 cas

### Le rattachement, et ce qu'il fallait ajouter au dossier

Le doublon rapproche plutôt qu'il ne rejette : c'était écrit au pas 1, encore fallait-il
qu'un dossier puisse accueillir un second dépôt. `DossierCommercial` porte donc
`rattachees`, un tuple des demandes suivantes du même numéro dans la fenêtre.

Un tuple et non une liste : le modèle est figé, et une liste par défaut resterait
modifiable sur place malgré le gel.

Trois règles se sont imposées en l'écrivant :

* **l'état et `depuis_le` ne bougent pas.** Un client qui renvoie son formulaire ne fait
  pas repartir le délai dont dispose le cabinet pour le rappeler. L'inverse permettrait
  d'échapper indéfiniment à l'alerte en soumettant une fois par heure ;
* **un dossier fermé n'accueille rien.** Un dépôt arrivé après un paiement ou un classement
  est une nouvelle intention, pas une répétition, et il mérite son propre dossier ;
* **le doublon se mesure contre toutes les demandes du dossier**, pas contre la seule
  demande d'origine. Sans cela, le troisième envoi d'un visiteur insistant sortirait de la
  fenêtre d'un fil pourtant vivant.

### Quatre colonnes promues, une par requête réelle

Le dossier est conservé comme document, avec quatre colonnes sorties du JSON parce que
quatre questions se posent en SQL : `telephone` pour le doublon, `etat` et `depuis_le`
pour la veille, `responsable` pour l'écran « mes dossiers ». `deposee_le` est promue aussi,
pour l'ordre et non pour un filtre.

Une subtilité qui a failli passer : `deposee_le` porte la **dernière** demande arrivée, pas
la première. C'est elle qui borne la fenêtre anti-doublon pour le dépôt suivant.

### Deux mutants ont survécu, et tous deux étaient de vraies lacunes

En cassant les gardes du cas d'usage une à une, deux mutations n'ont fait échouer aucun
test.

**Le premier.** Élargir la fenêtre passée au dépôt à dix ans ne change aucun verdict,
parce que la fenêtre est appliquée deux fois : par la requête, qui borne ce qu'on lit, et
par `doublon_parmi`, qui décide. Aucune assertion sur un résultat ne pouvait s'en
apercevoir. Ce qui change, c'est le nombre de lignes lues à chaque dépôt de formulaire,
robots compris.

Un test regarde donc l'appel plutôt que le résultat — le seul du lot dans ce cas, et
l'exception est écrite dans sa docstring. **Une borne dont personne ne vérifie qu'elle est
posée finit par ne plus l'être**, et le jour où cela se voit, c'est en production sous
charge.

**Le second.** Retirer la garde qui refuse un rattachement sur un dossier fermé ne cassait
rien, parce que le cas d'usage écarte déjà les dossiers fermés avant d'appeler `rattacher`.
Les tests du cas d'usage ne pouvaient donc pas dire si la garde du domaine existait.

Elle est maintenant éprouvée là où elle vit. **Un garde-fou se teste à l'endroit où il est
posé, jamais depuis l'étage qui le rend inutile.**

### Un défaut trouvé dans la migration du chantier précédent

La migration de sécurité au niveau des lignes (`7c31af5b904e`, pas 4 du chantier 12)
dérivait sa liste de tables de `app.tables.METADONNEES`. L'intention était bonne et écrite
noir sur blanc : une liste énumérée serait juste le jour où on l'écrit et fausse à la table
suivante, et la table oubliée serait précisément celle qui fuit.

Elle était bonne **et elle était fausse**. `METADONNEES` décrit le code d'aujourd'hui, pas
le schéma tel qu'il était à cette révision. En jouant la chaîne complète sur une base
neuve, elle a échoué :

```
ProgrammingError: relation "dossier_commercial" does not exist
[SQL: ALTER TABLE dossier_commercial ENABLE ROW LEVEL SECURITY]
```

Le défaut n'apparaît **jamais** sur une base déjà migrée, puisque Alembic ne rejoue pas ce
qui est passé. Il apparaît sur une installation neuve, c'est-à-dire chez le prochain
développeur et en production. Il ne s'est vu que parce que la migration a été jouée pour
de vrai, sur une base créée pour l'occasion.

**Une migration décrit un instant de l'histoire. Lire le présent la rend mutable, et une
histoire mutable ne se rejoue pas.**

La liste y est désormais figée aux dix-sept tables de son époque, avec l'explication en
en-tête. La crainte d'origine est traitée ailleurs, et mieux : `tests/test_isolation.py`
boucle sur les métadonnées **courantes** et vérifie, dans les deux sens, qu'aucune table
cloisonnée ne laisse voir les lignes d'un autre locataire. C'est le bon partage : un test
regarde le présent, c'est son métier ; une migration regarde son époque, c'est le sien.

Une fonction `instructions_activation_pour(nom)` a été extraite pour que chaque migration
créant une table cloisonnée pose sa politique en une ligne, plutôt que de recopier le SQL.
Une politique recopiée sans `WITH CHECK` protégerait les lectures et laisserait écrire chez
le voisin — plus rare qu'une lecture fautive, et bien plus difficile à défaire.

### La table est cloisonnée, alors que le visiteur est anonyme

Il n'y a pas de contradiction, et le socle du chantier 12 le garantissait déjà : un nom
d'hôte qui ne désigne aucun tenant retombe sur le locataire du centre. C'est le cabinet
qui reçoit la demande, pas un client. La ligne lui appartient, et se cloisonne comme les
autres.

La requête du doublon est d'ailleurs la seule du contexte à interroger un numéro de
téléphone à travers toute la table, donc celle où une fuite se verrait le moins. Deux
cabinets qui démarchent la même PME ne doivent pas se découvrir l'un l'autre par un
rattachement inattendu. Un test le vérifie explicitement.

### Ce qui a été éprouvé sur une vraie base, et non supposé

La chaîne complète de migrations a été jouée sur une base créée pour l'occasion, puis
défaite, puis rejouée :

* la politique existe sur `dossier_commercial`, avec `USING` **et** `WITH CHECK` ;
* dix-huit tables portent désormais la politique ;
* un rôle **non propriétaire** ne voit que les lignes de son locataire ;
* sans variable de session posée, il ne voit **rien** — le bon défaut ;
* une écriture au nom d'un autre locataire est refusée par `WITH CHECK` ;
* `downgrade -1`, puis `downgrade base`, puis `upgrade head` : la chaîne se rejoue.

Six gardes du dépôt SQL ont ensuite été cassées une à une. Chacune a produit un échec, y
compris le filtre de locataire dans la requête du doublon.

---

## Pas 4 — L'affectation

**Fait.** L'étape 2 du parcours : désigner un responsable, ou constater que personne ne
convient.

* `app/contextes/souscription/domaine/affectation.py`
* `app/contextes/souscription/adaptateurs/sortant/regles_affectation.py`
* `app/contextes/souscription/application/affectation.py`
* `Docs/referentiel/affectation/` — cinq critères, plus le README qui explique la grille
* `tests/test_affectation.py` — 42 cas

### Le document de conception était explicite, et il avait raison

> « La règle d'affectation change tous les trimestres. Elle est donc un paquet de règles au
> Référentiel, évalué par le moteur, et non une fonction Python à redéployer. »

Une fonction Python porterait très bien ces trois critères. Il faudrait une livraison à
chaque ouverture d'agence, à chaque recrutement d'un spécialiste, à chaque fois qu'un
directeur décide qu'un dossier de création vaut deux dossiers de tenue. Ces décisions se
prennent un vendredi et s'appliquent le lundi.

C'est le **troisième domaine** à tourner sur `app/moteur/`, après la conformité et la
charge, et comme les deux autres : **rien n'a été ajouté au noyau pour l'accueillir.**

### La décision de modélisation : le sujet est une candidature

C'est ce qui porte tout le reste, et ce n'est pas évident au premier abord.

Une règle d'affectation ne dit rien sur une demande seule. « L'agence est éloignée » n'a
de sens que pour un couple demande–responsable ; « la compétence manque » aussi ; « la
charge est excessive » aussi. Le sujet évalué est donc la **rencontre** entre une demande
et un responsable possible.

On évalue autant de candidatures qu'il y a de responsables, et l'on retient la meilleure.
Modéliser la demande comme sujet obligerait chaque règle à porter en elle la façon de
parcourir l'annuaire, ce qui n'est plus une règle mais un programme.

### Deux natures de critère, et la différence est configurée

Certains critères **écartent** : un responsable sans habilitation à la création
d'entreprise ne peut pas la traiter, quelle que soit sa disponibilité. D'autres
**pénalisent** : une agence plus loin, une charge plus lourde, c'est moins bien sans être
impossible.

`redhibitoire` est un champ de la règle, donc du référentiel. C'est délibéré : **ce qui
bloque aujourd'hui sera une préférence demain, et l'inverse.** Le jour où le centre
décidera qu'une charge de plus de quarante dossiers interdit toute nouvelle affectation,
ce sera un booléen dans un fichier.

Un test le démontre littéralement : le même prédicat, la même ligne de code, deux
configurations, deux décisions opposées.

### La grille livrée, et ce qu'elle vaut

| Code | Nature | Poids | Ce qu'il dit |
|---|---|---|---|
| `AFF-CMP-001` | rédhibitoire | — | La compétence exigée par le service n'est pas détenue |
| `AFF-DIS-001` | rédhibitoire | — | Le responsable est indisponible |
| `AFF-PRX-001` | pénalisant | 30 | L'agence diffère de la région déclarée |
| `AFF-CHG-001` | pénalisant | 20 | Charge pondérée au-delà de soixante points |
| `AFF-CHG-002` | pénalisant | 40 | Charge pondérée au-delà de cent vingt points |

Tous en `A_VALIDER` : ils reproduisent la pratique décrite et attendent d'être arrêtés par
le centre. Un critère `VALIDE` sans signataire nommé est refusé au chargement, comme
partout ailleurs dans le référentiel.

Les deux critères de charge illustrent une technique qui resservira : **une progression
par paliers s'exprime en cumulant des règles**, pas en ajoutant un opérateur de palier au
moteur. Au-delà de cent vingt points, les deux se déclenchent et pèsent soixante.

### Le défaut silencieux du mécanisme, et où on l'attrape

Un prédicat qui lit `{"var": "competence"}` au lieu de `{"var": "competences"}` **ne lève
pas**. JSONLogic rend `None` pour un chemin absent, le critère devient toujours faux, et
un responsable parfaitement compétent se retrouve écarté de tous les dossiers. Rien dans
le journal ne le dirait.

Le contrôle est donc fait au **chargement**, une fois, au démarrage, avec suggestion :

```
AFF-CMP-001.yaml cite un fait que le domaine « AFFECTATION_COMMERCIALE » ne déclare pas :
« competence_requis » (voulez-vous dire « competence_requise » ?).
```

Une faute de frappe dans un fichier édité par un responsable de pôle doit échouer
bruyamment au chargement, jamais mentir à l'évaluation.

### Le classement est totalement déterminé, et c'est une exigence, pas un détail

Écartés en dernier, puis pénalité croissante, puis **identifiant croissant**.

La troisième clé n'est pas cosmétique. Deux responsables à égalité parfaite arriveront
souvent au démarrage, quand personne n'a encore de charge. Sans elle, le désigné dépendrait
de l'ordre dans lequel la base a rendu ses lignes, qu'aucune base ne garantit sans
`ORDER BY`. Deux exécutions du même cas donneraient deux réponses.

**Un système dont on ne peut pas rejouer une décision est un système dont on ne peut pas
expliquer une décision.** Le test vérifie le classement sur trois permutations des mêmes
candidats.

### Une découpe reprise en cours d'écriture

Le cas d'usage a d'abord été écrit avec un `choisir` qui rendait `Choix | None`, le `Choix`
portant les verdicts de tous les candidats. La branche « personne ne convient » devait
alors **recalculer** ce que `choisir` venait de produire, par une acrobatie qui ne
s'écrivait pas proprement.

Le défaut était en amont : les verdicts existent aussi — et surtout — quand personne n'est
retenu, c'est-à-dire au moment où l'on en a le plus besoin. Les loger dans le `Choix`
obligeait à fabriquer un choix sans choix pour les transporter.

Le domaine expose donc deux fonctions au lieu d'une : `classer`, qui rend le classement
complet, et `choix_parmi`, qui en tire le retenu. `choisir` reste comme commodité.
L'appelant qui a besoin des deux ne paie plus l'évaluation deux fois, et la branche
d'échec s'écrit en une ligne.

**Quand une branche ne s'écrit pas proprement, ce n'est presque jamais la branche qui est
en cause.**

### Le dossier sans destinataire reste `DÉPOSÉE`, et c'est voulu

Le document dit : « Une demande qui n'a pas de destinataire est un problème visible, pas
une ligne oubliée en base. »

La conséquence de code est précise : `affecter_le_dossier` **ne lève pas** quand personne
ne convient. Il rend un résultat qui le dit, avec les empêchements rencontrés, et le
dossier ne bouge pas.

On n'invente pas d'état « en file de pôle ». Le dossier qui reste `DÉPOSÉE` **est** le
signalement : la veille des deux heures le remontera. Un état à part le ferait sortir du
champ de l'alerte qui doit précisément le voir.

Les empêchements sont dédoublonnés et rendus tels quels. « Aucun responsable disponible »
ne dit pas quoi faire au responsable de pôle ; « compétence non détenue » et « responsable
indisponible » lui disent s'il manque une compétence ou des bras.

### La réaffectation écarte le titulaire, et ce n'est pas la grille qui le fait

Sans cette exclusion, la grille redésignerait le même : rien n'a changé dans ses critères.
La réaffectation automatique tournerait en rond jusqu'à la limite des trois tours, sans
que personne de nouveau ne soit prévenu.

L'exclusion est dans le geste, pas dans le référentiel. « Ce n'est pas celui qui vient
d'échouer » n'est pas un critère de routage, c'est une propriété de cette action-ci.
L'écrire au référentiel obligerait chaque règle à connaître l'affectation courante.

Quand il n'y a personne à qui passer la main, le dossier **reste chez son titulaire**. Le
vider de son responsable le rendrait invisible à la fois de lui et de la file.

### Quatorze gardes éprouvées en les cassant

Départage des égalités, rang des écartés, effet du rédhibitoire, cumul des pénalités,
insensibilité à la casse, région vide, remontée des échecs, refus d'un critère sans effet,
refus d'un critère validé sans signataire, choix du premier éligible, exclusion à la
réaffectation, séparation de la date de vigueur, conservation du motif, et absence
d'affectation quand personne ne convient. **Chacune a produit au moins un échec.**

---

## Pas 5 — Le fil de conversation

**Fait.** L'étape 3 du parcours, et le morceau dont les règles ne viennent pas de nous.

* `app/contextes/souscription/domaine/conversation.py`
* `app/contextes/souscription/adaptateurs/sortant/catalogue_modeles.py`
* `app/contextes/souscription/application/conversation.py`
* `Docs/referentiel/messagerie/modeles/` — sept modèles, plus leur README
* `tests/test_conversation.py` — 66 cas

### La règle qui gouverne tout le reste

**On ne peut écrire librement à un client que dans les vingt-quatre heures qui suivent son
dernier message.** Hors de cette fenêtre, seul un modèle approuvé à l'avance passe.

Trois conséquences qu'il faut avoir en tête avant de lire le code :

* **le premier message d'une relation part nécessairement d'un modèle**, puisque le client
  n'a encore rien écrit. Sept modèles doivent donc être approuvés avant que ce canal
  serve, et l'approbation prend de quelques heures à quelques jours.

  ⚠️ **Cette phrase a été lue, au pas 5, comme si elle valait pour le parcours entier.**
  Elle ne vaut que pour ce canal-là. Voir le [pas 5 bis](#pas-5-bis--recadrage--aucune-plateforme-extérieure-nest-bloquante) :
  le parcours se déroule sans messagerie, et un test de bout en bout le prouve ;
* **l'envoi d'un modèle ne rouvre pas la fenêtre.** Elle ne se rouvre que lorsque le
  client répond. C'est pour cela que les modèles sont rédigés pour appeler une réponse :
  un modèle qui ne fait pas écrire le client laisse la fenêtre fermée, et le suivant sera
  facturé aussi ;
* **répondre vite est gratuit.** Un responsable qui traite le fil pendant que la fenêtre
  est ouverte ne coûte rien ; le même échange repris trois jours plus tard se paie en
  modèles.

### La question de départage a eu besoin d'un second temps

C'est le point de méthode le plus important du pas, et il a failli être manqué.

« Est-ce que cela varie sans le code ? » Pour les vingt-quatre heures, la réponse est
**oui** : la plateforme pourrait changer sa règle demain. En s'arrêtant là, on met la
fenêtre au référentiel. **Ce serait une erreur, et une erreur qui ne se verrait qu'en
production.**

Il faut une seconde question : **« et qui décide ? »**

Le centre décide de ses délais de veille, de ses honoraires, de sa grille de routage. Il
**ne décide pas** de la fenêtre de service : elle lui est imposée. La rendre configurable
ferait croire le contraire à celui qui lit le fichier. Un responsable de pôle la porterait
un jour à soixante-douze heures pour se laisser du temps, le système accepterait, et les
envois échoueraient chez la plateforme sans que rien ici ne l'explique.

> **La configuration est pour ce que le centre décide. Ce que le monde impose est une
> constante, avec sa citation.**

La même distinction range la grille tarifaire dans le code, et le **catalogue des
modèles** au référentiel : leur texte, leur catégorie et leur état d'approbation sont
révisés par le centre, sans livraison.

Un test garde cette frontière : il parcourt tout `Docs/referentiel/` et échoue si la
fenêtre y apparaît, avec un message qui dit pourquoi. C'est un garde-fou qui protège une
**distinction**, pas une valeur.

### Le piège le plus coûteux, et où on l'attrape

> « Un modèle non approuvé échoue silencieusement en production alors qu'il fonctionne
> dans le bac à sable. »

Rien ne distingue les deux à l'écriture du code. Le refus est donc **local**, avant
l'appel : un modèle `EN_ATTENTE`, `REFUSE` ou `DESACTIVE` ne part pas, et le message
d'erreur nomme le piège.

Les sept modèles du référentiel sont tous `EN_ATTENTE`, parce que le compte de la
plateforme n'est pas ouvert. **C'est un état honnête**, et un test l'affirme : les
déclarer approuvés ferait passer les tests et échouer la production, ce qui est exactement
le défaut que ce pas cherche à rendre impossible.

### Le désordre est la règle, pas l'exception

Deux mécanismes de la plateforme obligent à écrire le domaine autrement qu'on le ferait
spontanément.

**Les accusés arrivent dans le désordre.** Le rappel « lu » peut précéder le rappel
« remis » : ce sont deux requêtes HTTP indépendantes. Assigner le statut reçu ferait
reculer un message de « lu » à « remis », et le tableau de bord annoncerait non lus des
messages qui l'étaient.

`StatutRemise` est donc un `IntEnum` ordonné, et le statut ne se pose pas : il
**progresse**. `ECHEC` est au sommet à dessein — un échec rapporté après un accusé de
remise est une contradiction de la plateforme, et dans le doute il faut croire l'échec :
un message annoncé remis qui ne l'était pas se découvre par un client qui n'a rien reçu.

**Les rappels sont rejoués.** C'est le mécanisme de reprise de la plateforme, pas une
anomalie. Un entrant écrit deux fois apparaîtrait deux fois dans le fil et, pire,
prolongerait la fenêtre à chaque rejeu. L'ajout au fil est donc idempotent sur
l'identifiant, pour les messages comme pour les appels.

### Le fil et la qualification sont deux choses

Un appel est journalisé avec sa durée et son issue. **Son contenu ne l'est pas**, et un
test vérifie littéralement que la classe ne porte aucun champ de plus.

Ce que le responsable retient d'un appel se saisit dans la qualification, en données
typées. Un champ de notes libres ici produirait un fil inexploitable par quoi que ce soit
d'automatique, et une qualification vide.

Une durée non nulle sur un appel non répondu est refusée : compter les sonneries comme du
temps d'échange fausserait l'indicateur qui sert à mesurer la charge réelle.

### Deux canaux, deux régimes

La fenêtre et le consentement ne valent que pour la messagerie instantanée. Un courriel
n'ouvre pas la fenêtre — la plateforme ne le voit pas — et ne s'y soumet pas non plus.
Appliquer la fenêtre au courriel interdirait d'écrire à un prospect qui n'a jamais
répondu, ce qui est exactement ce à quoi le courriel sert.

C'est aussi ce qui rend une révocation de consentement supportable : elle ferme un canal,
elle ne rend pas le prospect injoignable.

### Le fil et le dossier s'ignorent, et c'est délibéré

Le `Fil` connaît la fenêtre, les modèles et les accusés. Il ne sait pas ce qu'est un
dossier commercial. Le `DossierCommercial` connaît ses huit états et ne sait pas ce qu'est
un message.

Cette ignorance mutuelle est ce qui permettra au fil de servir la relation avec un adhérent
déjà client, qui n'a plus de dossier commercial du tout. Le lien est un geste, et il
s'écrit dans `application/conversation.py`.

**Un appel sans réponse ouvre la conversation.** Ce n'est pas une négligence :
`premier_echange_le` mesure la réactivité **du cabinet**, pas la disponibilité du client.
Un responsable qui a appelé trois fois dans l'heure a fait son travail, et l'indicateur
doit le dire même si personne n'a décroché.

### Vingt-trois gardes éprouvées en les cassant

Borne stricte de la fenêtre, sortant qui ne l'ouvre pas, courriel qui ne l'ouvre pas,
dernier entrant plutôt que premier, refus du libre hors fenêtre, consentement, régime du
courriel, modèle non approuvé, marketing, compte de paramètres, comptage par le plus grand
numéro, statut qui ne recule pas, échec au sommet, rejeu des messages, rejeu des appels,
durée sur appel non répondu, date d'approbation, et les quatre lignes de la grille
tarifaire, plus les deux gardes du cas d'usage. **Chacune a produit au moins un échec.**

---

## Pas 5 bis — Recadrage : aucune plateforme extérieure n'est bloquante

**Demandé par le cabinet, à la relecture du pas 5 :**

> « Je ne veux pas que Meta soit bloquant : le système doit être totalement fonctionnel
> sans que ce module n'en dépende. »

**La demande est juste, et le pas 5 avait le défaut qu'elle décrit.**

* `app/contextes/souscription/domaine/canaux.py`
* `app/contextes/souscription/adaptateurs/sortant/plan_de_contact.py`
* `Docs/referentiel/messagerie/canaux.yaml`
* `tests/test_canaux.py` — 22 cas

### Ce que le pas 5 avait installé sans le vouloir

Une dépendance dure. Le raisonnement était correct pièce par pièce, et faux dans son
résultat :

1. sur un fil neuf, la fenêtre de service est fermée, puisque le client n'a rien écrit ;
2. hors fenêtre, seul un modèle approuvé passe ;
3. aucun modèle n'est approuvé, puisque le compte de la plateforme n'est pas ouvert ;
4. **donc aucun premier contact n'est possible.**

Le parcours entier attendait l'approbation d'un tiers. Ce n'était écrit nulle part comme
une décision, c'était la conséquence non regardée de trois règles justes.

Le journal du pas 5 le disait d'ailleurs à sa dernière ligne, et le disait comme une
fatalité : « ce qui bloque, et qui ne demande aucun développeur : les sept modèles doivent
être soumis ». **Une phrase qui commence par « ce qui bloque » sur une dépendance externe
mérite d'être relue comme un défaut de conception, pas comme un point de calendrier.**

### Le principe rétabli

**Une messagerie instantanée est un confort, pas une infrastructure.** Le centre travaille
depuis des années sans elle. Le système doit pouvoir en faire autant, du dépôt de la
demande jusqu'au paiement.

La garantie tient en une phrase : **le canal plancher est le téléphone, et un téléphone
n'a pas d'API.** Pas de compte à vérifier, pas de modèle à faire approuver, pas de palier
de messagerie, pas de fenêtre de service. Le numéro est le seul champ réellement
obligatoire de la demande de contact ; un responsable peut toujours le composer.

Tant qu'un numéro est joignable, le parcours avance. Tout le reste est du gain de temps
par-dessus.

### Le plan de contact, et pourquoi il est configuré

`Docs/referentiel/messagerie/canaux.yaml` dit quels canaux le centre exploite et dans quel
ordre il s'y replie.

Ici, la question **« et qui décide ? »** rend l'autre réponse qu'au pas 5. Ouvrir un compte
de messagerie, arrêter le courriel automatique, réserver un canal à certains services :
c'est bien le centre qui décide. Le plan vit donc au référentiel, à côté de la fenêtre de
service qui, elle, reste une constante du code.

Les deux fichiers se touchent et disent l'inverse l'un de l'autre, ce qui est exactement ce
que la distinction demande. Chacun porte l'avertissement qui renvoie à l'autre.

État arrêté aujourd'hui :

| Canal | Rang | Actif | Motif |
|---|---|---|---|
| `APPEL` | 0 | oui | — |
| `COURRIEL` | 1 | oui | — |
| `WHATSAPP` | 2 | **non** | Compte non ouvert, aucun modèle approuvé |

**Le jour où la plateforme s'ouvre, un `actif: true` dans ce fichier suffit.** Rien d'autre
ne bouge dans le système.

### La règle de repli

La préférence du client d'abord, toujours. Puis les canaux actifs, dans l'ordre du plan. Le
premier qui satisfait ses conditions l'emporte.

| Canal | Ce qu'il exige |
|---|---|
| messagerie | actif au plan, consentement en vigueur, **et plateforme prête** |
| courriel | actif au plan, et une adresse renseignée |
| appel | actif au plan. Rien d'autre. |

La troisième condition de la messagerie est celle que le pas 5 avait oublié de rendre
facultative.

Trois propriétés méritent d'être notées :

* **la préférence du client n'est jamais réécrite.** Le repli est une décision d'exécution,
  prise à l'instant du contact. Réécrire la préférence effacerait ce que le client avait
  demandé, et l'on ne saurait plus, en rétablissant le canal, qui rebasculer ;
* **les motifs d'écartement sont conservés dans l'ordre.** Sans eux, on ne saura pas
  pourquoi un client qui avait coché la messagerie a reçu un appel ;
* **un canal absent du plan n'est jamais employé.** Ne pas le déclarer, c'est ne pas
  l'exploiter ; l'essayer quand même contournerait une décision du centre.

Quand plus rien ne convient, la fonction **lève**. Il faut pour cela que l'appel ait été
désactivé, et le message le nomme. Rendre `None` obligerait chaque appelant à traiter un
cas qui ne devrait jamais arriver, et l'un d'eux le traiterait en ne faisant rien.

### Un défaut de signature, corrigé

`preparer_message_libre` avait `canal=CanalMessage.WHATSAPP` en valeur par défaut.

C'est petit, et c'est exactement le couplage à retirer : **un défaut qui désigne le canal
le plus contraint fait écrire, sans y penser, du code qui ne fonctionne que si une
plateforme tierce est prête.** Le paramètre est devenu obligatoire ; nommer son canal à
chaque appel oblige à savoir lequel on emprunte.

### Le test qui porte la garantie

`TestLeParcoursEntierSansMessagerie` déroule le parcours de bout en bout — dépôt,
affectation, choix du canal, appel, conversation, qualification, chiffrage, proforma,
acceptation, paiement — **avec le plan réel du référentiel**, où la messagerie est
inactive.

Il porte sur le plan réel et non sur un plan d'essai, et c'est le point : aujourd'hui, en
production, la messagerie n'existe pas. Le test doit mesurer ce que le centre a réellement
arrêté.

> ⚠️ Si un jour ce test échoue, c'est qu'une dépendance dure à une plateforme tierce s'est
> réintroduite. Ne pas le contourner en activant la messagerie : chercher l'étape qui en
> dépend, et la rendre indifférente.

Treize gardes du module ont été cassées une à une. Chacune a produit au moins un échec.

---

## Pas 6 — La qualification typée

**Fait.** L'étape 4, que le document appelle « la plus importante du parcours, et celle
qu'on sous-estime ».

* `app/contextes/souscription/domaine/qualification.py`
* `app/contextes/souscription/adaptateurs/sortant/questionnaires.py`
* `Docs/referentiel/qualification/` — deux questionnaires, plus leur README
* `app/moteur/faits.py` — un principe affiné, voir plus bas
* `tests/test_qualification.py` — 61 cas

### Ce qui est en jeu

> « La différence entre du texte libre et une donnée typée est toute la différence entre un
> dossier qu'un humain doit relire et un dossier qu'un moteur peut évaluer. »

Le responsable ne rédige pas des notes : il remplit un questionnaire dont chaque réponse
est typée, datée, et porte sa source. Le champ libre existe, il sert aux nuances, et **il
n'entre dans aucun calcul**.

Ce dernier point n'est pas une restriction technique, c'est ce qui garantit qu'un montant
proposé est explicable. Un chiffrage qui dépendrait d'une phrase écrite à la volée ne se
rejouerait pas et ne se défendrait pas devant un client. Un test le vérifie littéralement :
la note n'apparaît pas dans `faits()`.

### Un principe du projet affiné, parce que l'implémentation l'a contredit

L'en-tête de `app/moteur/faits.py` affirmait depuis le chantier 11 :

> « Un schéma vit dans le code, à côté du sujet qu'il décrit, pas au référentiel avec les
> règles. »

Et le document de conception exige l'inverse pour ce pas-ci :

> « Le questionnaire lui-même est une configuration. Ajouter une question ne doit pas
> demander un déploiement. »

**Les deux ont raison, et l'affirmation du moteur était trop large.** Son argument était :
un schéma décrit ce que le sujet expose, or le sujet est du code, donc ajouter un fait
suppose que quelque chose l'expose désormais. La prémisse est vraie de la facture, du
dossier à évaluer et de la candidature. Elle est **fausse de la qualification**, dont le
sujet est un questionnaire rempli par un humain : y ajouter une question ne suppose aucun
code, cela suppose qu'on pose une question de plus.

La règle générale, écrite dans `faits.py` :

> **Un schéma vit là où vit son sujet.** Sujet en code, schéma en code. Sujet en
> configuration, schéma produit à partir d'elle.

Ce qui ne change pas, c'est qu'ils doivent bouger ensemble. Un schéma de code se vérifie
par un test qui le confronte au sujet ; un schéma configuré se vérifie **par
construction**, puisque la même configuration produit les deux. `Questionnaire.schema()`
tient en une ligne, et c'est tout le pont.

Le noyau ne voit pas la différence : il reçoit un `SchemaDeFaits`, d'où qu'il vienne. C'est
le quatrième usage du même moteur, et rien ne lui a été ajouté.

### Le piège du langage, qui aurait coûté cher

⚠️ **`isinstance(True, int)` rend vrai en Python.**

Sans garde, cocher une case sur une question qui attend un nombre d'associés enregistrerait
« 1 associé ». Le chiffrage tournerait sur cette valeur, la proforma partirait, et **rien
ne le signalerait jamais** : un dossier à un associé est parfaitement plausible.

Un booléen est donc refusé explicitement là où un entier ou un montant est attendu. Le même
raisonnement vaut dans l'autre sens : convertir par la vérité de Python ferait de la chaîne
« non » un vrai, ce qui est exactement l'inverse de la réponse donnée par le client.

### Le piège nommé par le document

> « Stocker les réponses dans un champ de texte libre, ou dans un objet sans schéma. Le jour
> où le moteur de tarification en a besoin, il faut tout ressaisir. »

Une réponse à une question absente du questionnaire est donc **refusée**, et non rangée
dans un coin. Un dictionnaire qui accepte tout est un objet sans schéma déguisé.

Le refus tombe à la saisie, où le responsable a encore le client au téléphone et peut
demander. Le laisser passer le ferait découvrir au chiffrage, quand il a raccroché.

### Deux défauts trouvés par les tests, dont un qui dépasse ce module

**Le premier.** `Questionnaire.schema()` échouait sur un ENUM sans valeurs, mais le
constructeur non : un questionnaire invalide pouvait exister en mémoire et ne se briser
qu'au moment de chiffrer. Le schéma est désormais construit **à la construction**. Un objet
qu'on ne peut pas fabriquer de travers vaut mieux qu'un objet qu'on vérifie plus tard,
parce que « plus tard » finit par vouloir dire « en entretien ».

**Le second, et il vaut pour tout le dépôt.** Un test attendait un refus sur une note trop
longue et n'en a pas eu :

```python
M(note="x" * 99)                             # refusé
m.model_copy(update={"note": "x" * 99})      # ACCEPTÉ, 99 caractères
```

**`model_copy` ne revalide pas.** C'est documenté chez Pydantic et facile à oublier, parce
que **tout le domaine repose dessus** pour ses transitions figées. Une contrainte de champ
protège le constructeur et laisse passer la copie.

L'exposition réelle a été inventoriée : sur les onze `model_copy(update=…)` du contexte,
dix écrivent des valeurs calculées ou des champs sans contrainte. Un seul écrivait un champ
borné depuis une saisie, et c'était celui-ci. Il vérifie maintenant lui-même.

> **Toute copie qui écrit un champ contraint depuis une saisie doit vérifier elle-même.**

### La version du questionnaire est conservée

Pour la même raison que la version du barème employé au chiffrage : six mois plus tard,
personne ne doit se demander sur quelles questions un dossier a été qualifié.

La complétude se juge d'ailleurs **contre le questionnaire qu'on lui donne**, pas contre un
questionnaire porté par la qualification. C'est l'appelant qui décide s'il confronte une
qualification ancienne à sa version d'origine ou à celle d'aujourd'hui, et les deux
réponses sont légitimes selon la question posée.

### Un test qui relie deux contextes

Le questionnaire de tenue comptable doit demander tout ce que la grille de charge du
contexte B évalue. Un test compare les deux ensembles et échoue si un fait manque.

Sans lui, le chiffrage tournerait sur des faits absents et **chaque critère échouerait en
silence** : le moteur signale les règles cassées, mais un fait manquant ne casse rien, il
rend simplement le prédicat faux.

### Un mutant survivant, et ce qu'il a révélé

Désactiver le contrôle de doublons du questionnaire ne faisait échouer aucun test : le
schéma du moteur les refuse déjà, avec son propre message contenant les mêmes mots.

Les deux contrôles coexistent volontairement — ils ne s'adressent pas aux mêmes gens : celui
du moteur parle de faits à un développeur, celui du questionnaire nomme le service et le
fichier à un responsable de pôle qui édite du YAML. Mais **un test qui passe aussi bien
avec que sans le contrôle ne dit rien de son existence.** L'assertion porte maintenant sur le
message propre au questionnaire.

### Quinze gardes éprouvées en les cassant

Case cochée contre entier, case cochée contre montant, vérité de Python sur les booléens,
valeur hors liste d'un ENUM, question inconnue, vide sur une obligatoire, note dans les
faits, réponse empilée au lieu d'être remplacée, ordre des manquantes, codes en double,
schéma éprouvé à la construction, rang des questions, borne de la note, version conservée.
**Chacune a produit au moins un échec.**

---

## Pas 7 — Le socle d'orchestration

**Fait.** Demandé par le cabinet, qui posait trois questions au passage : les services
sont-ils up, l'interconnexion tient-elle, et le motif Saga est-il employé.

* `app/orchestration/saga.py` · `boite_d_envoi.py`
* `app/infrastructure/tables_orchestration.py` · `depots_orchestration.py`
* `alembic/versions/…_socle_orchestration_saga_et_boite.py`
* `app/contextes/souscription/adaptateurs/entrant/routes_acquisition.py` — 7 routes
* `tests/test_saga.py` — 37 cas · `tests/test_acquisition_http.py` — 18 cas

### L'inventaire, mesuré et non supposé

Les trois réponses, dans l'ordre où elles ont été cherchées :

* **les services ne tournaient pas.** La pile déclare quatre services ; elle n'était pas
  démarrée. L'application, elle, démarre et répond ;
* **les modules étaient bien câblés** : cent opérations HTTP sur quatre-vingt-quinze
  chemins, treize routeurs. J'ai d'abord compté cinq routes et me suis trompé : cette
  version de FastAPI conserve les routeurs inclus au lieu de les aplatir. Le schéma
  OpenAPI dit la vérité ;
* **le parcours d'acquisition n'exposait rien.** Six pas de domaine, d'application et
  d'adaptateurs sortants, et **aucune route**. Tout était construit, rien n'était
  joignable.

### La saga, et surtout quand ne pas en mettre

Le motif est employé, et son en-tête commence par dire quand il ne sert à rien :
**une saga est inutile pour ce qui tient dans une transaction.** Ce système est un
monolithe modulaire ; deux écritures dans deux contextes partagent la même transaction, et
un `COMMIT` suffit. Y poser de la machinerie de compensation serait du culte du modèle.

Elle sert exactement là où la transaction s'arrête : les **effets hors base**. Sur les sept
étapes d'ouverture d'un tenant, trois en produisent, et une ne se défait pas du tout.

Deux règles portent le mécanisme :

* **la reprise en avant est le défaut, la compensation l'exception.** Un échec de
  provisionnement est presque toujours passager. Compenser sur un échec technique
  détruirait un tenant à moitié créé pour une coupure de trois secondes ;
* **une étape à effet externe doit déclarer ce qu'on en fait** — compensation, ou
  irréversibilité motivée. Se taire est refusé à la construction. C'est le défaut classique
  des sagas : on écrit six compensations, on oublie la septième, et l'oubli ne se voit
  jamais au moment où on le commet puisque le chemin nominal fonctionne parfaitement.

### La boîte d'envoi, et le problème qu'aucun soin ne répare

Écrire puis publier perd l'événement à la panne. Publier puis écrire annonce un fait qui
n'a pas eu lieu. **Aucun des deux n'est acceptable, et ce n'est pas un problème
d'attention mais de structure.**

L'événement est donc écrit dans la même transaction que le fait, et publié séparément.
La contrepartie est entière et assumée : « au moins une fois », jamais « exactement une
fois », donc tout consommateur doit être idempotent. C'est la raison pour laquelle les sept
étapes d'ouverture le sont.

### Une permission qu'il ne fallait pas réutiliser

Le jeu de permissions n'avait rien de commercial, puisque le parcours n'existait pas. La
solution facile était de réutiliser `LIRE_DOSSIER`.

**Un prospect n'est pas un adhérent** : il n'a ni dossier, ni comptabilité, ni pièces.
Réutiliser les permissions du portefeuille aurait donné au commercial l'accès à la
comptabilité de tous les adhérents, et privé le chargé de clientèle de la file des
demandes. `LIRE_PROSPECT` et `QUALIFIER_PROSPECT` coûtent deux membres d'énumération ; la
confusion aurait coûté une fuite dont personne n'aurait vu la cause.

---

## Pas 8 — Le relais, le provisionneur, et l'événement qui relie tout

**Fait.** La boucle que le document de conception annonçait comme manquante.

> « Les sept étapes existent, la reprise après incident aussi, la table et le répertoire
> aussi. **Ce qui manque est l'événement qui les relie**, pas les pièces. »

* `app/orchestration/relais.py`
* `app/contextes/tenants/domaine/substitution.py`
* `app/contextes/tenants/adaptateurs/sortant/provisionneur_local.py`
* `app/contextes/tenants/application/ouverture_sur_paiement.py`
* `app/contextes/transverse/adaptateurs/entrant/routes_orchestration.py` — 3 routes
* `tests/test_relais.py` — 18 cas · `tests/test_ouverture_sur_paiement.py` — 27 cas ·
  `tests/test_orchestration_http.py` — 7 cas

### Le défaut que le pas 7 avait laissé

La boîte d'envoi se remplissait et **ne se vidait jamais**. C'était un mécanisme à moitié
écrit, et le genre de moitié qui ne se voit pas : la table grossit, les événements
attendent, et rien ne signale que personne ne les lit.

### La partie subtile : l'ordre par clé quand ça casse

Deux événements de la même clé doivent être traités dans l'ordre d'émission. Lire du plus
ancien au plus récent suffit **tant que tout passe**.

Quand un événement échoue, les suivants de la même clé doivent attendre avec lui. Sinon le
rejeu du premier, au tour suivant, arriverait **après** le second : l'ordre serait inversé
au pire moment, celui d'un incident. Les autres clés continuent, elles : un tenant bloqué
ne doit pas retenir les quatre-vingt-dix-neuf autres.

Trois lignes de code, et le genre de propriété dont l'absence ne se découvre qu'en
production, sur un `TenantOuvert` traité avant le `PaiementEncaissé` qui l'a causé.

### Le seul comportement honnête pour un provisionneur incomplet

Quatre étapes sur sept sont de vraies écritures en base et sont réellement exécutées.
Trois demandent une infrastructure qui n'existe pas.

Trois comportements possibles, un seul est honnête :

* **lever** bloquerait toutes les installations de développement à la troisième étape ;
* **réussir en silence** produirait un tenant marqué actif dont le schéma n'existe pas,
  mensonge que la première requête découvrirait ;
* **substituer en le déclarant** laisse la chaîne se dérouler et rend la différence
  lisible.

L'étape substituée inscrit son nom, et `ouverture_reellement_complete` rend faux tant qu'il
en reste une. **« La saga est terminée » et « le tenant est utilisable » ne sont pas la
même question**, et un test l'affirme. Le jour où l'infrastructure existe, on passe trois
fonctions de plus au constructeur ; rien d'autre ne bouge.

### Trois défauts trouvés, et chacun par un mécanisme différent

**Le domaine m'a repris.** La compensation de l'activation appelait `abandonner`, et le
cycle de vie a refusé : « seule une ouverture en cours peut échouer, or le tenant est
ACTIF ». C'était le domaine qui avait raison. Un tenant qui a été actif **a existé** : son
sous-domaine a répondu, son lien est parti, le client a pu s'y connecter. Le déclarer en
échec d'ouverture réécrirait cette histoire, et l'on ne saurait plus distinguer un
provisionnement qui n'a jamais abouti d'un client auquel on a retiré son accès. Défaire une
activation est une **résiliation**.

**Un test m'a repris.** Le motif de l'abandon entrait dans l'exécution et pas dans le
contexte : les compensations retombaient sur leur valeur par défaut, et un tenant résilié
portait « ouverture annulée » là où le client aurait lu « paiement contesté ». Le moteur
injecte désormais le motif avant de compenser, parce qu'**une compensation a besoin de
savoir pourquoi elle défait.**

**Un mutant survivant m'a repris**, et c'est le plus instructif. Deux mutations du
provisionneur ne faisaient échouer aucun test, celles qui touchaient l'idempotence des
actions prises isolément. La raison est structurelle : **la saga saute les étapes qu'elle a
enregistrées**, donc ses tests ne peuvent pas montrer ce qui arrive quand on rejoue une
étape déjà faite.

Or c'est exactement le scénario pour lequel elle existe. Le moteur enregistre l'avancement
**après** l'effet ; une panne entre les deux fait rejouer une étape sur un tenant qui l'a
déjà dépassée.

Le test ajouté rejoue chaque action directement sur un tenant déjà ouvert. **Cinq des sept
ont échoué**, sur une transition interdite : `_avancer` comparait l'égalité et tentait donc
de faire *reculer* le tenant. Corrigé par une comparaison de rang.

> Une reprise après incident qui échoue sur une transition interdite échoue au moment
> précis où l'on en a le plus besoin.

### Le test d'architecture m'a arrêté aussi

Le cas d'usage, en couche `application`, importait le provisionneur, en couche
`adaptateurs`. Une flèche de l'intérieur vers l'extérieur.

La correction n'a pas été de déclarer une exception mais de reconnaître que « cette
ouverture est-elle réelle ? » est **une question métier**, posée par le cas d'usage et par
la console, pas un détail du provisionneur. Les trois notions ont déménagé au domaine.

C'est le troisième chantier où ce test bloque, et les trois fois il avait raison.

### Pourquoi une route et non une boucle de fond

Le passage de publication est une tâche d'arrière-plan par nature. Il est ici une route, et
c'est un choix d'étape.

Une boucle démarrée au lancement tournerait **dans chaque réplique**, et deux répliques
publiant le même lot doubleraient les remises. Elle serait **invisible aux tests**, qui ne
peuvent pas attendre un intervalle. Et elle **masquerait ses échecs** derrière un journal
que personne ne lit encore.

Le jour où l'ordonnanceur existera, il appellera cette fonction, et rien du socle ne
changera.

### Vingt-trois gardes éprouvées en les cassant

Neuf pour le relais, douze pour le provisionneur et le cas d'usage, deux rejouées après
correction. **Deux ont survécu au premier tour**, et c'est ce qui a révélé le défaut
d'idempotence.

---

## Pas 9 — Le chiffrage

**Fait.** L'étape 5 du parcours, et le **cinquième domaine** à tourner sur `app/moteur/`.
Rien ne lui a été ajouté.

* `app/contextes/souscription/domaine/tarification.py`
* `app/contextes/souscription/adaptateurs/sortant/grille_tarifaire.py`
* `Docs/referentiel/tarification/` — 2 barèmes, 7 règles, plus le README
* `tests/test_tarification.py` — 30 cas

### Un intervalle, jamais un prix

Trois valeurs, et chacune protège quelqu'un : le **plancher** protège la marge du centre,
le **plafond** protège le client d'un chiffrage abusif, la **référence** est ce que le
système recommande.

Rendre un nombre unique aurait un défaut simple : le responsable en dévierait de toute
façon, et l'écart ne serait mesuré nulle part.

### La décision la moins visible, et la plus importante

**Les ajustements en proportion portent sur la base, jamais sur le cumul.**

Appliqué au cumul, un taux rendrait le résultat dépendant de l'ordre des règles. Or
l'ordre des règles est celui du répertoire de fichiers, c'est-à-dire l'alphabet.

> **Un tarif qui change parce qu'un fiscaliste a renommé un fichier est indéfendable.**

La garantie est **structurelle** et non défensive : la valorisation ne voit que les
`faits`, et le cumul n'y figure pas. Elle ne peut donc pas produire un résultat dépendant
de l'ordre, même en s'y efforçant. `base` est un fait pour cette raison précise.

Le test mélange les règles sur douze permutations et compare. Pour vérifier qu'il ne
mesure pas du vide, une mutation a réécrit `chiffrer` en version séquentielle, appliquant
chaque ajustement au cumul : le test tombe.

### Une heuristique retirée avant qu'elle ne coûte

La première valorisation devinait la nature d'un ajustement par sa magnitude : « une valeur
strictement comprise entre moins un et un est un taux ». Cela tenait tant qu'aucun
ajustement en francs ne valait moins d'un franc, c'est-à-dire tant que personne n'écrivait
une remise de cinquante centimes.

**Une heuristique dans un moteur de prix est un défaut en attente : elle ne se trompe
qu'une fois, et elle se trompe sur une facture.** L'unité de la conséquence déclare
désormais la nature, et le noyau la transporte sans la lire — ce qu'il fait de toutes les
unités.

### Les débours ne sont pas des honoraires

Frais de notaire, droits d'enregistrement, frais de greffe : le centre les avance, il ne
les gagne pas. Ils entrent donc dans la proposition comme des lignes à part, et :

* **aucune règle ne les ajuste** ;
* **l'amplitude de négociation ne les touche pas** ;
* `dans_l_intervalle` porte sur les honoraires seuls.

Négocier ne peut pas porter sur l'argent d'un tiers. Confondre les deux ferait qu'un rabais
de vingt pour cent sortirait de la poche du centre sur la part qu'il ne gagne pas, et
personne ne s'en apercevrait avant le bilan.

### Le schéma se compose avec celui du questionnaire

`schema_de_tarification(questionnaire)` rend les faits du questionnaire du service, plus
trois que le système calcule : `base`, `score_charge`, `service`.

Une composition, pas une déclaration parallèle. Les redéclarer créerait deux listes à tenir
d'accord, et la dérive ne se verrait qu'au premier chiffrage faux. **Ajouter une question
au questionnaire ouvre donc un fait de plus aux règles de prix, sans déploiement**, et
c'est voulu.

C'est aussi ce qui relie le pas 6 au pas 9 sans mécanisme intermédiaire.

### Le défaut le plus coûteux du lot, et pourquoi il est le plus coûteux

Un prédicat qui lit `{"var": "associe"}` au lieu de `{"var": "associes"}` ne casse rien.
JSONLogic rend `None`, le critère devient toujours faux, et **l'ajustement s'applique sur
tous les dossiers**.

Il ne provoque aucune erreur, aucune alerte, aucun test rouge. Il fait perdre de l'argent à
chaque devis, ou en fait gagner indûment, jusqu'à ce que quelqu'un compare deux
propositions à la main.

Le contrôle est donc fait au chargement, contre le questionnaire du service concerné. Il ne
peut pas être global comme celui des quatre autres domaines : le schéma dépend du service.

### La charge entre comme un ajustement parmi les autres

`score_charge` est un fait, et deux règles de tarification s'en servent, avec deux paliers
qui se cumulent. C'est ce qui relie directement l'effort estimé au prix demandé,
**sans mécanisme séparé** : la matrice de charge du contexte B alimente la tarification du
contexte M par un simple fait.

### Quinze gardes éprouvées en les cassant

Trois mutations ont d'abord été mal ciblées et ont survécu sans rien prouver : elles
touchaient des chemins morts. Les refaire correctement les a toutes tuées, y compris celle
qui réécrit le chiffrage en séquentiel.

> Une mutation qui survit demande d'abord de vérifier qu'elle change vraiment le
> comportement. Compter un faux survivant comme une lacune de test fait écrire des tests
> qui ne servent à rien.

---

## Pas 10 — La proforma

**Fait.** Les étapes 6, 7 et 8 du parcours : arrêter le tarif, émettre le document,
recueillir l'acceptation qui vaut contrat.

* `app/contextes/souscription/domaine/proforma.py`
* `app/contextes/souscription/adaptateurs/sortant/tables.py` — `TableProforma`
* `alembic/versions/…_table_de_la_proforma.py`
* `tests/test_proforma.py` — 44 cas · `tests/test_proforma_persistance.py` — 13 cas

### La règle qui commande le module

> « Le document émis est figé pour toujours. On ne le régénère jamais. Si le montant
> change, une **nouvelle version** est émise, avec un nouveau numéro, et l'ancienne reste
> consultable, marquée comme remplacée. »

Il n'existe donc dans ce module **aucune méthode qui change un montant**. La seule façon
d'en obtenir un autre est `nouvelle_version`, et elle rend **un couple** : la précédente
marquée remplacée, et la nouvelle.

Rendre la seule nouvelle laisserait l'appelant marquer l'ancienne, ou l'oublier. Une
ancienne non marquée resterait opposable : **deux proformas actives pour le même
engagement, à deux montants**.

### Le défaut trouvé en éprouvant la contrainte sur une vraie base

J'avais posé le numéro en clé primaire et ajouté une contrainte d'unicité
`(locataire, numero)`. L'essai a rejeté le doublon — **mais sur la mauvaise
contrainte** : le message parlait de `pk_proforma`.

La clé primaire portait donc le numéro seul, et **deux cabinets n'auraient jamais pu avoir
tous deux `PRO-2026-0001`**. C'est pourtant le cas normal : un numéro de proforma est
séquentiel par cabinet.

Les autres tables du contexte s'en tirent avec une clé simple parce que leurs identifiants
sont opaques et tirés au sort, donc uniques par construction. Le numéro d'une proforma est
l'inverse : il est lisible, prévisible, et **il doit l'être** — un client le cite au
téléphone.

La clé est désormais composite. Deux tests le vérifient dans les deux sens : deux cabinets
avec le même numéro passent, le même cabinet deux fois échoue.

> Lire le message d'une contrainte qui vient de mordre vaut mieux que constater qu'elle a
> mordu.

### La séparation des rôles est constatée, jamais imposée

Celui qui chiffre et celui qui engage peuvent être la même personne dans un petit centre.
Le domaine enregistre les deux séparément et expose `separation_respectee` ; il ne refuse
pas.

Refuser rendrait le produit inutilisable dans un cabinet de trois personnes, et ferait
contourner la traçabilité par un compte partagé, **ce qui est bien pire que la situation
qu'on voulait éviter**. C'est une règle de contrôle interne qui constatera, et le contrôle
interne constate.

### L'écart au barème se motive

Dans l'intervalle, le responsable module librement. **Hors de l'intervalle, le motif est
obligatoire** et le modèle refuse à la construction. Un rabais exceptionnel reste possible,
mais il laisse une trace nominative.

`ecart_a_la_reference` est signé : c'est ce que le pilotage agrège pour voir la dérive. Un
cabinet qui vend systématiquement sous la référence a un problème de barème, pas de
commerciaux.

### Le lien d'acceptation

Signé, daté, à usage unique, **et sans compte**. Demander une inscription à ce moment
précis fait perdre une partie des prospects et n'apporte rien : le compte se crée à
l'ouverture du tenant.

Trois soins qui ne se voient pas :

* **le sceau couvre la version**, pas seulement le numéro. Sans elle, un lien émis pour la
  v1 permettrait d'accepter la v2, et le client accepterait un montant qu'il n'a jamais
  vu ;
* **les champs scellés sont séparés par un caractère qui ne peut apparaître dans aucun**.
  Une concaténation nue laisserait deux triplets différents produire le même sceau ;
* **le lien est vérifié avant la proforma**. Un lien mal signé ne doit rien apprendre sur
  l'existence ou l'état d'une proforma : c'est la seule chose qui protège un numéro
  devinable.

`employe_a` lève au second appel, et c'est délibéré : cette méthode **porte** l'unicité
d'usage, et la rendre idempotente reviendrait à ne pas l'avoir.

### La numérotation continue, et pourquoi le numéro s'attribue à l'émission

Réserver un numéro avant d'émettre paraît prudent et produit des trous : le responsable
abandonne, le numéro est perdu, la série saute.

Une série trouée n'est pas un défaut esthétique. **Un contrôle qui constate un saut demande
où est passé le document manquant, et « nulle part » est une réponse qu'on ne peut pas
prouver.**

`dernier_numero` peut mentir, et le port le dit : entre la lecture et l'écriture, une autre
requête a pu émettre. C'est la contrainte d'unicité qui arbitre, et l'appelant traite le
conflit en relisant. Verrouiller la série entière sérialiserait toutes les émissions du
cabinet pour une garantie identique.

### Dix-sept gardes éprouvées en les cassant

Motif hors intervalle, bornes de l'écart, séparation constatée, rang annuel, numéro
illisible, série trouée, empreinte, marquage de la remplacée, remplacement d'une acceptée,
transmission héritée, date de transmission, annulation d'une acceptée, sceau couvrant la
version, expiration, usage unique, ordre des vérifications, lien d'une autre version.
**Chacune a produit au moins un échec.**

---

## Pas 11 — La relance graduée, et la boucle refermée

**Fait.** Le parcours se déroule maintenant de la demande déposée au sous-domaine qui
répond, sans trou.

* `app/contextes/souscription/domaine/relance.py`
* `app/contextes/souscription/adaptateurs/sortant/plan_de_relance.py`
* `app/contextes/souscription/application/encaissement_du_parcours.py`
* `Docs/referentiel/relance/paliers.yaml`
* `tests/test_relance.py` — 30 cas

### Chaque nombre de ce fichier coûte de l'argent, et peut coûter le canal

Hors fenêtre de service, une relance part en modèle utilitaire, donc **facturée**. Une
relance automatique mal réglée coûte à chaque déclenchement.

Pire, et c'est ce que le pas 5 avait établi : un numéro qui envoie beaucoup de messages non
lus voit sa note baisser puis ses quotas se réduire. **Relancer trop détruit le canal
lui-même**, et le canal conditionne aussi l'appel, puisque les deux dépendent du même
palier de messagerie.

Serrer ces délais paraît toujours une bonne idée le jour où l'on regarde le taux de
transformation. C'en est une mauvaise le mois suivant.

### Quatre règles, et ce que chacune évite

**Le délai court depuis la transmission, jamais depuis l'émission.** Une proforma émise et
jamais transmise ne se relance pas : relancer un client qui n'a rien reçu le laisse
perplexe et fait passer le cabinet pour désorganisé.

**Un palier franchi ne se rejoue pas.** Le balayage tourne toutes les heures ; sans cette
garde, le client recevrait vingt-quatre messages par jour.

**Un seul palier par passage, le plus avancé qui soit dû.** Si le balayage a été arrêté une
semaine, trois paliers sont dus. On n'en envoie qu'un. Envoyer les trois ferait recevoir au
client trois messages dans la même minute : il n'y verrait pas un système remis en route,
il y verrait du harcèlement.

**Après le dernier palier, on s'arrête et on le dit.** Le silence d'un client après trois
relances est une information ; continuer à écrire n'en est pas une.

### Le ton est une variable, pas un modèle

Trois modèles quasi identiques se font approuver trois fois par la plateforme, se corrigent
trois fois, et divergent au premier oubli. Un seul modèle, une variable de ton, et un test
vérifie que les trois paliers du référentiel emploient bien le même.

Un autre vérifie que ce modèle **existe au catalogue** : un plan qui nomme un modèle
inexistant ferait échouer chaque relance au moment de l'envoi, et l'échec ne se verrait
qu'à la première.

### Une acceptée impayée n'est pas une relance de plus

À trente jours, elle retourne en conversation. Le client s'est engagé et n'a pas réglé :
ce n'est plus un problème de relance automatique, c'est un dossier qu'un humain reprend.

Continuer à envoyer des modèles à quelqu'un qui a signé et pas payé ne produit rien qu'une
facture de messagerie.

### Le suivi ne vit pas sur la proforma

Elle est figée et vaut contrat. Y inscrire un compteur de relances ferait changer un
document contractuel pour une raison qui n'a **rien de contractuel**. Le suivi est un objet
à part, et un test vérifie que la proforma ne porte aucun champ de relance.

### La boucle refermée, et l'idempotence tenue des deux côtés

L'encaissement fait trois gestes qui vont ensemble : le dossier passe à `PAYÉE`,
l'événement `PaiementEncaissé` est déposé dans la boîte d'envoi **dans la même
transaction**, et le relais le publiera pour la saga d'ouverture.

Le prestataire rejoue ses rappels, parfois plusieurs jours après. La garde du dossier
suffit à ne pas encaisser deux fois ; celle de la saga suffit à ne pas ouvrir deux tenants.
**Aucune des deux ne suffit seule** : sans la première, un rejeu déposerait un second
événement et la boîte grossirait de faits déjà traités ; sans la seconde, un événement
publié deux fois par le relais — ce qui est son régime normal — ouvrirait deux tenants.

Un test parcourt les deux : le rappel rejoué trois jours plus tard n'ouvre pas un second
préfixe de stockage.

### La clé de l'événement est la référence du dossier

Pas le numéro de la proforma, ce qui paraîtrait plus naturel. C'est cette clé que la saga
emploie pour retrouver son exécution, et prendre le numéro casserait le jour où une **v2**
est acceptée : la saga repartirait de zéro sur un tenant à moitié ouvert.

### La charge ne transporte que ce que l'ouverture demande

Ni le montant, ni l'identité du client. **Un événement qui transporte des données dont
personne n'a besoin finit par en transporter qu'on ne voulait pas voir circuler** : les
journaux, les files et les sauvegardes le recopient tous.

### Un contrôle qui vérifiait l'ordre au lieu de la contiguïté

Le plan de relance refuse les rangs troués. Ma première version comparait à
`sorted(set(rangs))`, ce qui laissait passer `[1, 3]` : les rangs étaient bien triés et
distincts, et il manquait le 2. Le test l'a attrapé au premier essai.

Seize gardes éprouvées en les cassant, seize échecs.

---

## État à la fin du pas 11

```
2105 passed                (avec PostgreSQL)
1994 passed, 111 skipped   (sans)
```

soit 569 cas de plus qu'au point de départ, dont 16 qui n'ont de sens qu'avec une vraie
base. L'écart entre les deux colonnes est la mesure de ce qui ne peut pas être vérifié
sans elle : politique de cloisonnement, colonnes promues, contraintes d'unicité.

**Ce que le parcours sait faire aujourd'hui.** Recevoir une demande, en refuser les formes
incohérentes au moment où elles se corrigent, recueillir un consentement qui se prouve et
se révoque, reconnaître un visiteur qui revient, conserver tout cela dans une table
cloisonnée dont la politique a été vérifiée en production simulée, désigner un responsable
selon une grille qui vit au référentiel, expliquer ce choix, et dire ce qui manquait quand
personne ne convient.

**Ce qu'il sait faire depuis le pas 5.** Ouvrir un fil, savoir à chaque instant s'il peut
écrire librement ou s'il lui faut un modèle, refuser localement ce que la plateforme
refuserait, compter ce que chaque envoi coûte, encaisser des accusés qui arrivent dans le
désordre sans jamais reculer, et journaliser un appel sans en conserver le contenu.

**Ce qu'il sait faire depuis le pas 6.** Poser un questionnaire configuré par service,
refuser à la saisie ce qui n'est pas du bon type, conserver la source et l'horodatage de
chaque réponse, dire ce qui manque encore, et rendre au moteur des faits qui n'ont jamais
traversé un champ de texte libre.

**Ce qu'il sait faire depuis les pas 7 et 8.** Publier ses événements sans jamais en perdre
ni en inventer, enchaîner les sept étapes d'ouverture d'un tenant avec leurs compensations,
reprendre là où un incident l'a arrêté, dire ce qu'une ouverture n'a pas réellement fait,
et se faire appeler par HTTP.

**Ce qu'il sait faire depuis le pas 9.** Chiffrer une prestation en rendant un intervalle
plutôt qu'un prix, appliquer des ajustements qui commutent, séparer les honoraires des
débours, et conserver la version du barème employée.

**Ce qu'il sait faire depuis le pas 10.** Arrêter un tarif en exigeant un motif hors
intervalle, émettre un document figé avec son empreinte et sa version de modèle, produire
une nouvelle version sans jamais toucher l'ancienne, numéroter en continu par cabinet, et
recueillir une acceptation par un lien signé, daté, à usage unique et sans compte.

**Ce qu'il sait faire depuis le pas 11.** Relancer une proforma sans réponse selon un plan
configuré, un palier à la fois, et s'arrêter au dernier. Rendre une acceptée impayée à un
humain plutôt qu'à un automate. Et surtout : **encaisser, déposer l'événement, et voir le
sous-domaine répondre**, sans qu'un rappel rejoué n'ouvre un second tenant.

**Le parcours se déroule désormais de bout en bout**, de la demande déposée sur la vitrine
au tenant ouvert. Un test le parcourt en entier ; son échec signifierait qu'un client a
payé et que rien ne se passe.

**Ce qui reste à brancher, et qui est nommé.** L'ordonnanceur qui appellera le relais et le
balayage de relance, la table du suivi de relance, celle de la qualification, le registre
durable des tenants dans les routes d'orchestration, l'adaptateur qui monte les
candidatures d'affectation, et les deux rôles PostgreSQL en exploitation, sans lesquels les
politiques de cloisonnement ne s'appliquent jamais.

**Ce qui ne bloque rien, contrairement à ce que ce journal affirmait au pas 5.** Les sept
modèles attendent leur soumission à la plateforme, et le parcours fonctionne sans eux : le
plan de contact se replie sur l'appel et le courriel, et le test de bout en bout le prouve
sur le plan réel du référentiel.

Les soumettre reste utile, et sans urgence de mise en service : cela ouvrira un canal de
plus, il coûtera un `actif: true` dans un fichier, et rien d'autre ne bougera.

**Ce qui manque au pas 4 pour être branché.** Les candidatures sont montées par un
adaptateur qui n'existe pas encore : il faudra lire l'annuaire des collaborateurs
(contexte K), la carte des agences et la charge en cours (contexte B). Le domaine et le
cas d'usage sont prêts et éprouvés ; ce qui les alimente ne l'est pas. C'est un choix
d'ordre, pas un oubli : la grille devait exister avant qu'on sache la remplir, faute de
quoi l'adaptateur aurait dicté sa forme au domaine.

---

## Pas 12 — Les deux rôles PostgreSQL, et la sonde qui cesse de mentir

### Le manque le plus ancien du projet

Depuis le chantier 2, chaque table cloisonnée porte une politique de sécurité au niveau
des lignes. Vingt-et-une tables aujourd'hui, une politique chacune, un test qui les
parcourt toutes et vérifie les deux sens. Le socle a l'air complet.

Il ne l'est pas, et la raison tient en une phrase de la documentation PostgreSQL :

> **Table owners normally bypass row security policies.**
> — *PostgreSQL, Row Security Policies, §5.9*

Trois catégories échappent aux politiques : le **propriétaire** de la table, un rôle
portant l'attribut **`BYPASSRLS`**, et un **superutilisateur**, toujours.

Or les migrations créent les tables, donc les possèdent. Une installation ordinaire donne
le même rôle aux migrations et à l'application. L'application possède alors ses tables, et
les politiques ne s'appliquent **jamais à elle**. Le cloisonnement du multi-cabinet repose
sur le seul filtre applicatif, que le moindre SQL textuel contourne.

⚠️ **Et rien ne le signale.** Le service répond. La recette passe. La suite de tests est
verte. C'est ce qui rend ce défaut particulier : il n'a aucune manifestation. On l'apprend
le jour où un adhérent voit la facture d'un autre.

Le fichier `README` du chantier 2 le disait déjà. Une ligne de `README` n'échoue pas.

### Ce que ce pas a construit

Trois choses, dans cet ordre : **constater**, **publier**, **corriger**.

`app/infrastructure/roles.py` demande à la base si le rôle courant est soumis aux
politiques, et rend un verdict. Il ne corrige rien : créer un rôle demande des droits que
l'application n'a pas, et ne doit pas avoir.

Cinq verdicts, parce que cinq causes qui appellent cinq gestes différents.

| Verdict | Cause | Le geste qui le lève |
|---|---|---|
| `APPLIQUE` | Aucune. C'est l'état attendu. | — |
| `CONTOURNE_SUPERUTILISATEUR` | Le rôle est superutilisateur. | Changer de rôle. Rien d'autre ne le corrige. |
| `CONTOURNE_BYPASSRLS` | L'attribut `BYPASSRLS`. | `ALTER ROLE … NOBYPASSRLS` |
| `CONTOURNE_PROPRIETAIRE` | Le rôle possède les tables. | Jouer `outils/roles-postgresql.sql` |
| `POLITIQUES_ABSENTES` | Une table cloisonnée sans politique. | Jouer les migrations |

**Un verdict unique aurait été plus simple, et inutilisable.** « Le cloisonnement ne
s'applique pas » envoie lire le code. Chaque cause porte donc sa phrase et son geste, et
celui qui déploie à trois heures du matin repart avec le fichier à jouer.

⚠️ **L'ordre des vérifications va du plus grave au plus réparable.** Un rôle peut relever
de plusieurs causes à la fois : le rôle des tests est superutilisateur *et* propriétaire.
Le verdict doit nommer celle qu'aucune configuration ne corrige, parce qu'un
superutilisateur contourne même `FORCE ROW LEVEL SECURITY` et que lire la suite ne sert
alors à rien.

**Une table sans politique compte comme un contournement**, et passe avant la propriété.
Un rôle parfaitement configuré sur une table sans politique n'est pas mieux protégé qu'un
propriétaire. La cause diffère, la conséquence est la même.

### La sonde de santé cesse de dire « opérationnel » sans regarder

Le constat se prend **une fois au démarrage**, et non à chaque appel : la sonde s'exécute
toutes les quelques secondes, et la réponse ne change que par un geste d'exploitation,
jamais entre deux requêtes. La contrepartie est nommée dans le code : une table ajoutée
sans politique pendant que le processus tourne ne se verra qu'au redémarrage suivant. Elle
est acceptable parce qu'une migration se joue avec un redémarrage.

`GET /sante` publie ensuite le verdict :

```json
{
  "etat": "operationnel",
  "base_de_donnees": "joignable",
  "cloisonnement": "CONTOURNE_PROPRIETAIRE",
  "cloisonnement_explication": "le rôle « cga » possède 21 table(s) cloisonnée(s) et contourne donc leurs politiques. Voir outils/roles-postgresql.sql : les migrations et l'application doivent employer deux rôles distincts."
}
```

⚠️ **Elle ne rend pas `503` pour autant, et c'est un choix.** Un cloisonnement contourné ne
rend pas le service indisponible : le retirer du trafic ne protège aucune donnée et prive
les adhérents d'un service qui fonctionne. La sanction est ailleurs, et plus dure.

### La seule exception au principe « on démarre quand même »

Partout ailleurs dans ce projet, une dépendance défaillante n'empêche pas le processus de
se lever. Le répertoire des tenants n'échoue pas le démarrage : un répertoire vide rend
`404`, ce qui est désagréable mais franc, et refuser de démarrer priverait aussi la vitrine
et la sonde, qui n'ont besoin d'aucun tenant.

**Le cloisonnement fait exception**, et la raison est que la comparaison ne tient pas. Un
service qui démarre sans cloisonnement ne tombe pas en panne : il **fonctionne**. Il
répond, il sert, et il sert les données de deux cabinets sans séparation. Entre une panne
franche et un service qui marche en mélangeant, la panne franche est préférable.

**En production, un contournement constaté refuse le démarrage.**

Avec une distinction qui compte, et qui est écrite dans le code : *« j'ai demandé et la
réponse est mauvaise »* n'est pas *« je n'ai pas pu demander »*. Une base momentanément
injoignable ne refuse rien. Confondre les deux empêcherait tout redémarrage pendant une
coupure réseau, c'est-à-dire exactement pendant l'incident où l'on redémarre.

**Hors production, aucun refus.** La suite de tests s'exécute avec un rôle superutilisateur
et contourne donc les politiques. C'est assumé : elle a besoin d'écrire pour deux
locataires afin de vérifier qu'ils ne se voient pas. Lui retirer le contournement lui
retirerait son moyen de mesurer.

### Le script d'exploitation, éprouvé sur une vraie base

`outils/roles-postgresql.sql` crée les deux rôles :

| Rôle | Ce qu'il fait | Qui l'emploie |
|---|---|---|
| `cga_migration` | Crée, possède et modifie le schéma. | Alembic, seul. |
| `cga_app` | Lit et écrit les données. Ne possède rien. | L'application. |

⚠️ **Ce fichier ne peut pas être une migration Alembic.** Créer un rôle demande des droits
qu'Alembic n'a précisément pas dans cette architecture, et un rôle est un objet de
l'**instance**, pas de la base : il survit à un `downgrade`, et deux bases de la même
instance le partagent. *Une migration décrit un instant de l'histoire d'un schéma ; ceci
décrit l'installation d'une instance.*

Deux points du script méritent d'être signalés parce qu'ils s'oublient et ne se voient pas
tout de suite.

`ALTER DEFAULT PRIVILEGES FOR ROLE cga_migration` accorde à `cga_app` les droits sur les
tables **qui n'existent pas encore**. Sans cette clause, chaque migration future créerait
une table à laquelle l'application n'aurait aucun accès, et la panne n'apparaîtrait qu'à la
première requête après le déploiement. La mention `FOR ROLE` est indispensable : les droits
par défaut se rattachent au rôle qui crée l'objet, pas à celui qui écrit la ligne.

`NOSUPERUSER NOBYPASSRLS` est écrit explicitement alors que ce sont les valeurs par défaut.
Un défaut se change sans bruit ; une ligne écrite se relit et se compare. C'est l'unique
attribut qui, retiré par mégarde, annule silencieusement tout le cloisonnement de la
plateforme.

**Le script était incomplet, et l'épreuve l'a dit.** Jouer les migrations sous
`cga_migration` a échoué sur `permission denied for schema public`. Depuis
**PostgreSQL 15**, le schéma `public` n'accorde plus `CREATE` au pseudo-rôle `PUBLIC` : un
script écrit pour la 14 crée deux rôles parfaitement configurés dont l'un ne peut rien
créer. Le `GRANT USAGE, CREATE ON SCHEMA public TO cga_migration` a été ajouté, et la
chaîne complète des migrations passe.

### L'épreuve, sur une base montée pour l'occasion

Base neuve, script joué, chaîne complète des migrations sous `cga_migration`, puis le
diagnostic sous chacun des trois rôles :

| Rôle | Verdict |
|---|---|
| `cga` (superutilisateur, celui des tests) | `CONTOURNE_SUPERUTILISATEUR` |
| `cga_migration` (propriétaire de 21 tables) | `CONTOURNE_PROPRIETAIRE` |
| `cga_app` (celui de l'application) | `APPLIQUE` |

Un verdict n'est pas une preuve. Le cloisonnement a donc été mesuré sur `cga_app`, avec
deux dossiers posés par le propriétaire :

| Ce qu'on tente | Ce qui se passe |
|---|---|
| Lire sans variable de session | **0 ligne** |
| Lire avec `app.locataire = CAB-A` | **1 ligne**, celle de `CAB-A` |
| Insérer chez `CAB-B` | **Refusé** (`WITH CHECK`) |
| `UPDATE` sur la ligne de `CAB-B` | **0 ligne touchée** |
| `DELETE` sur la ligne de `CAB-B` | **0 ligne supprimée** |

Le premier cas est celui qui se vérifie le moins et qui compte le plus : sans variable de
session, `current_setting(…, true)` rend `NULL`, la comparaison rend `NULL`, et la
politique refuse. Un code qui oublierait de poser le locataire ne verrait **rien**, au lieu
de tout voir.

### Une justification écrite avant d'être vérifiée, et corrigée

Le constat a été branché dans la fixture de `test_isolation.py`, avec cette raison : *sans
lui, toute la suite pourrait passer au vert avec un rôle qui contourne, donc sans rien
vérifier.*

**C'était faux.** Un `ALTER ROLE … BYPASSRLS` fait échouer vingt-deux cas sur vingt-quatre,
parce que chaque cas vérifie les deux sens et que le sens « invisible au locataire A »
tombe aussitôt. La suite était saine sans ce constat.

Ce qu'il apporte est plus modeste, et suffit à le garder : il change **vingt-deux échecs en
un diagnostic**. Sans lui, la sortie répète « 2 lignes attendues, 0 obtenues » vingt-deux
fois sans jamais nommer la cause. Avec lui, la fixture s'arrête avant de semer, sur une
phrase qui nomme le rôle, l'attribut fautif et le fichier qui le corrige.

*Une affirmation portée par un commentaire se vérifie comme un garde se mute.* Celle-ci ne
l'avait pas été, et le commentaire disait le faux dans un fichier dont le rôle est
précisément de ne pas mentir sur ce qu'il prouve.

### Un défaut de production trouvé en chemin, et le type qui l'empêche de revenir

En cherchant qui lisait le réglage de persistance, une ligne a sauté aux yeux :

```python
# app/contextes/transverse/adaptateurs/entrant/dependances.py
def garnir_le_repertoire() -> int:
    if configuration().persistance != "sql":
        return 0
```

Le réglage vaut `"memoire"` ou `"postgresql"`. La production **exige** `"postgresql"` et
refuse de démarrer autrement. La valeur `"sql"` n'a **jamais** été acceptée nulle part.

Conséquence : **le répertoire des tenants n'était jamais garni en production**, et tout
sous-domaine rendait `404`. La passerelle consulte ce répertoire pour résoudre chaque nom
d'hôte ; vide, elle ne résout rien.

⚠️ **Et deux tests le couvraient au vert**, parce qu'ils forçaient eux-mêmes la valeur
fautive :

```python
def _config_sql():
    return configuration().model_copy(update={"persistance": "sql"})
```

Ils vérifiaient le défaut au lieu du comportement. C'est la forme la plus coûteuse d'un
test : il occupe la place de celui qui aurait attrapé la faute.

**La correction ne s'arrête pas à la valeur.** Corriger `"sql"` en `"postgresql"` laisserait
la même faute possible demain. Deux gestes structurels :

Le réglage devient un **type fermé** — `Literal["memoire", "postgresql"]` — et une valeur
inconnue est refusée **au chargement de la configuration**, avec le nom du réglage et la
liste des valeurs admises, avant qu'aucune requête n'arrive. La faute se déplace là où elle
se règle.

La question se pose par une **propriété nommée**, `config.en_base`, et non par une
comparaison de chaîne recopiée dans chaque module. *Une comparaison écrite à la main s'est
déjà trompée de valeur ; une question posée une seule fois ne le peut plus.* Les quatre
comparaisons du projet, y compris celle des exigences de production, passent par elle.

*Le rapport avec ce pas est direct : les deux défauts sont de la même famille. Une chose
juste sur le papier, jamais confrontée à ce que la machine en fait, et rien qui échoue pour
le signaler.*

### Un piège examiné, et écarté

Le `\d dossier_commercial` de l'épreuve a montré `pk_dossier_commercial PRIMARY KEY btree
(reference)` — une clé primaire sur une colonne seule, exactement la forme corrigée au
pas 10 sur la proforma, où deux cabinets ne pouvaient jamais porter tous deux le numéro
`PRO-2026-0001`.

**Ce n'est pas le même défaut.** Une référence de dossier vaut `dos-a1b2c3d4e5f60718`, seize
caractères tirés d'un UUID : elle est unique de façon globale par construction, et deux
cabinets ne peuvent pas la partager. Le numéro de proforma, lui, était lisible et séquentiel
par cabinet, donc voué à la collision.

La condition qui en ferait un défaut est nommée ici pour le jour où elle se présentera : si
la référence devient un jour lisible et séquentielle par cabinet — `DOS-2026-0001`, ce
qu'un centre de gestion demandera tôt ou tard — la clé primaire devra devenir composite le
même jour.

*Un schéma qui ressemble à un défaut connu se vérifie avant de se corriger. Corriger par
ressemblance ferait payer une migration à une table qui n'a rien.*

### Ce que les mutations ont vérifié

Onze mutations, toutes tuées, et chacune tue exactement le test qui la vise.

| Mutation | Ce qui tombe |
|---|---|
| Le contrôle `relforcerowsecurity` retiré | `FORCE` cesse d'être reconnu |
| Le cas superutilisateur désactivé | L'ordre des vérifications ne tient plus |
| Le cas des politiques absentes désactivé | Une table sans politique passe pour cloisonnée |
| Le cas `BYPASSRLS` désactivé | L'attribut n'est plus nommé pour lui-même |
| Le refus de démarrage rendu inactif | La production démarre sur un contournement |
| Le refus de démarrage rendu systématique | La production ne démarre plus jamais |
| Une base injoignable refuse le démarrage | Un redémarrage devient impossible en coupure |
| Le verdict tu dans la sonde | Quatre cas tombent |
| L'explication tue | Le geste correcteur disparaît |
| `NON_CONSTATE` tu | L'absence de constat redevient indiscernable |
| Le `503` rendu en `200` | La sonde recommence à mentir |

La sonde de santé n'avait **aucun** test sur son chemin `503` : elle lisait la base depuis
le chantier 2, et rien ne vérifiait qu'elle rendait bien `503` plutôt que `200` avec un état
dégradé dans le corps. Un orchestrateur lit le code de statut, jamais le corps ; un `200`
accompagné de `"etat": "degrade"` garde le conteneur en rotation. C'est couvert maintenant,
avec le cas qui vérifie que le message du pilote de base — qui nomme l'hôte, le port et
l'utilisateur — reste au journal et ne part pas dans un corps de réponse souvent exposé
sans authentification.

### État à la fin du pas 12

**2 124 tests passent** avec PostgreSQL, lint propre. Dix-neuf de plus qu'au pas 11.

**Ce que le projet sait faire qu'il ne savait pas.** Dire si ses données sont réellement
cloisonnées, le publier sur sa sonde de santé avec le geste qui corrige, et refuser de
démarrer en production quand elles ne le sont pas. Le manque le plus ancien du projet est
comblé, et il l'est de la seule façon qui tienne : par un constat que la machine prend
elle-même, pas par une ligne de documentation.

**Ce qui reste à brancher, et qui est nommé.** L'ordonnanceur qui appellera le relais et le
balayage de relance, la table du suivi de relance, celle de la qualification, le registre
durable des tenants dans les routes d'orchestration, et l'adaptateur qui monte les
candidatures d'affectation.

**Ce qui est passé de « à faire » à « à jouer ».** Les deux rôles PostgreSQL ne sont plus un
travail de conception mais une commande d'installation, écrite, éprouvée sur une base
neuve, et dont l'oubli se voit désormais tout seul.

---

## Pas 13 — L'ordonnanceur, ou qui appelle

### Le manque

La boîte d'envoi se remplissait et personne ne la vidait. Les proformas sans réponse
attendaient une relance que rien ne déclenchait. Tout le mécanisme existait depuis les
pas 7, 8 et 11 ; il lui manquait **quelqu'un qui appelle**.

Un client pouvait payer, l'événement était déposé, et le tenant ne s'ouvrait que si un
administrateur pensait à appeler `POST /orchestration/publication` à la main.

### Les trois façons de se tromper, et pourquoi elles se ressemblent

Un ordonnanceur écrit comme une boucle qui dort est faux de trois façons, et les trois
ne se découvrent qu'en exploitation.

Il **perd son échéancier au redémarrage.** Le compte à rebours vit en mémoire, un
déploiement le remet à zéro, et un travail quotidien sur une plateforme redéployée chaque
matin ne passe jamais. Rien ne le signale : le processus a bien démarré.

Il **double sur deux instances.** Deux processus qui dorment le même intervalle se
réveillent tous les deux, et le client reçoit deux relances identiques à la même seconde.
Ce n'est pas théorique : une mise à jour sans coupure fait tourner l'ancienne et la
nouvelle version ensemble pendant quelques secondes.

Il **ne se teste qu'en attendant.** Vérifier qu'un travail horaire passe bien demande une
heure, ou des ruses sur l'horloge répandues dans tout le code.

Les trois ont la même cause : **la décision, l'exclusion, l'état et l'appel sont mêlés
dans une seule boucle.** La découpe les sépare.

| Où | Quoi | Ce que cela rend possible |
|---|---|---|
| `app/orchestration/ordonnanceur.py` | La décision : qu'est-ce qui est dû ? | L'instant est un argument. Vérifier un travail quotidien coûte une soustraction |
| `app/orchestration/tour.py` | Le déroulement d'un tour | Un exécutant qui lève, un qui réussit : trois lignes de test, aucune base |
| `app/infrastructure/verrou.py` | L'exclusion entre instances | Deux sessions, une seule qui travaille, éprouvé sur une vraie base |
| `passage_ordonnance` | L'état, en base | Le compte à rebours survit au redéploiement |
| `app/infrastructure/boucle_de_fond.py` | L'appel | Ce qui reste est **exactement** ce qu'un test ne peut pas vérifier sans attendre |

### La règle qui distingue un ordonnanceur d'un compteur

**Un travail en retard ne se rattrape pas N fois.** Un processus arrêté trois jours, avec
une cadence horaire, ne doit pas produire soixante-douze passages au redémarrage.

Aucun travail de ce système n'est cumulatif. Le relais publie ce qui attend, quel qu'en
soit l'âge. Le balayage regarde ce qui est dû maintenant. Rejouer un passage manqué ne
produirait rien qu'une seconde relance au même client, c'est-à-dire précisément ce qu'on
cherche à éviter.

Deux autres règles, du même genre, écrites parce qu'elles s'oublient.

**Un travail jamais passé est dû immédiatement.** Une installation neuve qui attendrait
une heure avant son premier tour laisserait croire à une panne pendant une heure. Et le
premier passage est celui qui révèle les erreurs de configuration : on le veut tout de
suite.

**Le recul après échec est plafonné, et ne descend jamais sous la cadence.** Sans
plafond, dix échecs d'affilée sur une cadence horaire repousseraient la reprise à plus de
quarante jours : le travail serait mort sans que rien ne l'ait déclaré mort. Sans
plancher, un travail horaire qui échoue une fois repasserait au bout de deux secondes,
et un unique échec deviendrait le moyen d'accélérer un travail lent.

Au delà de vingt échecs consécutifs, le travail est **abandonné** et ne repart pas seul.
C'est voulu : un travail qui échoue vingt fois a un défaut que la vingt-et-unième
tentative ne corrigera pas, et continuer masque le problème derrière un journal qui
défile.

### Le verrou, et pourquoi ce n'est pas une table

Une table de verrous demande d'écrire une ligne, de la relire, de la supprimer, et surtout
de la **nettoyer quand le processus meurt sans la rendre**. C'est ce dernier point qui
pourrit : la ligne reste, elle dit « quelqu'un travaille », et personne ne travaille plus.
Il faut alors un délai d'expiration, donc une horloge, donc un second mécanisme pour
arbitrer les horloges qui divergent.

Un verrou consultatif PostgreSQL **tombe tout seul** quand la connexion se ferme,
proprement ou parce que le processus a été tué. Rien à nettoyer, rien à expirer, aucune
horloge à arbitrer.

⚠️ **La variante de transaction, et non celle de session.** Le verrou de session se rend
explicitement, et **se perd** dès qu'une connexion mise en réserve est rendue au bac puis
reprise par un autre appel : le déverrouillage part alors sur une autre connexion, ne
trouve rien, et le verrou reste pris. C'est un défaut typique des applications qui mettent
leurs connexions en réserve, et celle-ci le fait.

⚠️ **`hash()` de Python ne peut pas servir à calculer la clé.** Il est salé par processus
depuis la 3.3 : deux instances calculeraient deux clés pour le même nom, chacune prendrait
son verrou, et l'exclusion n'existerait pas. Le défaut serait invisible sur une machine de
développement à un seul processus, et se manifesterait en production par des relances en
double. Une empreinte cryptographique est employée pour sa **stabilité**, pas pour sa
résistance.

L'exclusion a été mesurée, pas supposée : deux sessions, la première obtient le verrou, la
seconde rend `False` sans lever, un troisième nom passe sans être bloqué, et le verrou
tombe aussi bien sur validation que sur annulation.

### Une erreur de conception, trouvée en faisant tourner

Le tour rendait d'abord **deux** états par travail : une marque de début, à valider avant
d'appeler l'exécutant, et une marque de fin. L'intention était de détecter un processus tué
en cours de travail, qui ne repasse jamais par la ligne qui écrit la fin. C'était écrit,
commenté, et justifié dans trois docstrings.

⚠️ **Cela ne pouvait pas fonctionner.** Le verrou est un verrou de **transaction** : il
tombe à la validation. Valider la marque de début en cours de tour aurait rendu le verrou
au milieu du travail, et une seconde instance serait entrée. Les deux mécanismes se
contredisaient.

Et le raisonnement était faux d'un cran plus haut encore. Avec un verrou de transaction, un
processus tué ne laisse **rien** : sa transaction est annulée, son verrou tombe avec sa
connexion, et le tour suivant repart d'un état propre. **Il n'y a aucun état « commencé
sans fini » à détecter** — la marque de début résolvait un problème que cette conception
n'a pas.

`debute_le` est conservé et écrit avec `termine_le`, en une seule fois : il mesure la durée
d'un tour, ce qui reste utile et n'a jamais demandé deux écritures.

*Deux mécanismes corrects séparément peuvent se contredire. Ce qui l'a révélé n'est ni la
relecture ni le test : c'est le premier tour réel, qui a levé sur une violation de clé
primaire.*

### La couture que seule la boucle pouvait révéler

Le premier tour hors requête a échoué sur `LocataireNonEtabli`.

L'intergiciel HTTP fait deux choses que l'on croyait n'en faire qu'une : il ouvre l'unité
de travail **et** il établit le locataire courant. La première pose le cloisonnement dans
la session ; la seconde alimente `courant()`, que les dépôts lisent pour se construire.

La route ne pouvait pas révéler le manque, puisqu'elle s'exécute toujours après
l'intergiciel. Il fallait un chemin sans requête pour que la couture se voie.

⚠️ Le refus disait exactement ce qu'il fallait : *« une lecture de données sans locataire
servirait des lignes arbitraires sans que rien ne le signale »*. **C'est le refus qui a
rendu la couture visible.** Une valeur par défaut l'aurait laissée passer, et le tour
aurait tourné pour un locataire arbitraire.

### Deux façons de faire tourner les travaux, et aucune n'est « la bonne »

Un ordonnanceur **extérieur** appelle `POST /orchestration/ordonnancement` à son rythme. Il
survit au redémarrage de l'application, se règle sans la toucher, et son état se lit
ailleurs. C'est le défaut.

Une boucle **dans le processus** ne demande rien à installer. Sur un serveur unique, c'est
la différence entre un système qui marche après un lancement et un système qui attend qu'un
exploitant lise une documentation.

⚠️ **Les deux ensemble sont sûrs**, et c'est ce qui permet de ne pas trancher : le verrou
arbitre. Mais sûr n'est pas la même chose que voulu, et c'est pourquoi
`CGA_ORDONNANCEUR_EN_PROCESSUS` vaut `false` par défaut. Une installation qui pilote ses
travaux de l'extérieur verrait sinon une seconde source d'appels dont elle ignore
l'existence, et passerait un temps déraisonnable à comprendre pourquoi ses compteurs
doublent.

### Ce que la boucle fait, et ce qu'elle ne fait pas

Elle ne décide pas ce qui est dû. Elle ne fait pas le travail. **Elle ne fait que dormir
et rappeler**, et c'est délibérément tout : ce qui reste est exactement ce qu'un test ne
peut pas vérifier sans attendre.

Trois propriétés y sont écrites, et chacune est une panne évitée.

**Elle attend sur l'événement d'arrêt, pas sur une horloge.** Un arrêt demandé une seconde
après le début d'une attente de cinq minutes ferait attendre l'orchestrateur cinq minutes,
et il finirait par tuer le processus.

**Le tour est appelé dans un fil.** Le tour ouvre une session, interroge la base et
publie : c'est du code bloquant. L'appeler directement figerait la boucle d'événements
pendant toute sa durée, donc toutes les requêtes HTTP en cours. Une publication d'une
seconde bloquerait une seconde le service entier, et cela ne se verrait que sous charge.

**Rien ne propage, et la boucle ne meurt pas.** Une exception non rattrapée tuerait la
tâche sans bruit : l'application continuerait de servir, la boucle serait morte, et plus
rien ne publierait. C'est la panne la plus coûteuse possible, puisqu'elle est invisible.

### Une mutation qui survit ne dit pas toujours que le garde est inutile

Le mutant qui remplace `to_thread(un_tour)` par `un_tour()` — c'est-à-dire celui qui fige
tout le service — **a survécu**.

Le test comptait trente battements et vérifiait qu'il en restait vingt. Or **un compteur
borné finit par atteindre son total même après un gel** : il met simplement plus longtemps.
Le cas mesurait la complétion, pas la fluidité.

Il mesure maintenant le nombre de battements dans une **durée de mur fixée**. Sans gel, la
fenêtre en autorise une quarantaine ; avec un gel de cent cinquante millisecondes sur deux
cents, il en reste moins de dix. Le mutant tombe.

*Une mutation qui survit dit d'abord que le test ne mesure pas ce qu'il croit mesurer.*

Un second enseignement, du même passage. Le mutant qui remplace l'attente sur l'événement
par un sommeil faisait **pendre** la suite trente secondes au lieu de l'échouer. Toutes les
attentes sur une tâche de boucle sont désormais bornées. *Un test qui pend est pire qu'un
test qui échoue : il ne dit pas ce qui ne va pas, il immobilise la chaîne d'intégration, et
il pousse à lancer la suite en arrière-plan, c'est-à-dire à ne plus la regarder.*

### Un écart entre le modèle et la base, trouvé en interrogeant `alembic check`

La commande compare le schéma déclaré au schéma migré. Passée sur la nouvelle table, elle
n'a rien trouvé — et a signalé un écart ancien sur `tenant`.

Le modèle déclarait `unique=True` sur la colonne `slug`, **sensible à la casse**. La
migration posait un index d'expression sur `lower(slug)`, **insensible**. Les deux bases ne
se comportaient donc pas de la même façon : une base migrée refusait « Station » à côté de
« station », une base montée par `create_all` — c'est-à-dire **celle de toute la suite de
tests** — les acceptait toutes les deux. Deux tenants auraient répondu au même nom d'hôte,
et le second aurait servi les données du premier.

⚠️ **Et un test vérifiait précisément cela, au vert.** `test_l_unicite_ignore_la_casse`
passait — mais grâce au dépôt, qui écrit `tenant.slug.lower()`, et non grâce à la base. En
retirant ce `.lower()`, le cas virait au rouge alors que la contrainte de la base est ce
qu'il prétend vérifier. Le test était vert pour une raison différente de celle qu'il
énonçait, dans une classe nommée `TestLUniciteEstArbitreeParLaBase`.

Mesuré, plutôt que supposé :

| Modèle | Dépôt | Le cas de la casse |
|---|---|---|
| Ancien (`unique=True`) | normalise | **vert**, grâce au dépôt |
| Ancien (`unique=True`) | ne normalise plus | **rouge** |
| Corrigé (index d'expression) | ne normalise plus | **vert**, grâce à la base |

Le modèle déclare maintenant l'index d'expression, et un cas écrit en **SQL direct**, sans
dépôt et sans ORM, mesure ce que la base refuse indépendamment de ce que le code qui y mène
a la bonne idée de faire.

### Une table sans cloison, et le garde-fou qui l'a exigée nommée

`passage_ordonnance` est la première table du système à ne porter aucun `locataire`. Un
travail périodique n'appartient à aucun cabinet : le relais vide la boîte de tout le monde.
Lui donner un propriétaire obligerait à en choisir un au hasard.

`test_toute_table_cloisonnee_porte_sa_colonne` a échoué aussitôt, en réclamant que
l'exemption soit **nommée avec sa raison**. C'est exactement ce qu'il doit faire : rien ne
distingue à la lecture une table que l'on a décidé d'exempter d'une table dont on a oublié
le mixin. La raison est maintenant écrite à trois endroits qui se répondent — la table, la
migration, et la liste des exemptions.

### Où va la cadence, et pourquoi pas au référentiel

Le partage se fait sur deux questions, et la seconde a été ajoutée à ce chantier.

**« Est-ce que cela varie sans le code ? »** Oui, la cadence varie d'un déploiement à
l'autre. **« Et qui décide ? »** L'exploitant, pas un fiscaliste.

Le référentiel porte ce que la loi prévoit, et ce qui s'y trouve est validé par quelqu'un
qui répond du chiffre. Une cadence de publication est un réglage de machine : elle va à la
configuration de déploiement.

### Ce que les mutations ont vérifié

Vingt mutations, toutes tuées, dont une qui a demandé de corriger le test avant de tomber.

| Mutation | Ce qui tombe |
|---|---|
| Échéance stricte (`>` au lieu de `>=`) | Chaque travail glisse d'un intervalle, tous les tours |
| Le cas du travail abandonné désactivé | Un travail mort est retenté sans fin |
| Un travail jamais passé n'est plus dû | Le premier démarrage ne fait rien |
| Le recul sans plafond | Quarante jours d'attente sans que rien ne le dise |
| Le recul sans plancher | Un échec devient le moyen d'accélérer un travail lent |
| Le succès décrémente au lieu de remettre à zéro | Un travail qui marche une fois sur deux recule sans fin |
| L'échec n'avance pas la date de fin | Le recul ne s'applique jamais |
| Le réveil peut rendre zéro | La boucle monopolise un cœur |
| La cadence n'est plus vérifiée | Une cadence nulle donne une boucle chaude |
| Un échec d'exécutant propage | Un balayage cassé arrête la publication |
| Un travail sans exécutant est ignoré | Une faute de frappe donne un travail qui ne tourne jamais |
| Un travail sans exécutant compte comme un échec | Un défaut de branchement conduit à l'abandon |
| Deux écritures au lieu d'une | Le verrou serait rendu au milieu du tour |
| Le motif d'échec perd le type | « connection refused » sans dire quelle couche |
| La boucle dort au lieu d'écouter l'arrêt | Un redéploiement attend l'échéance |
| Le tour est appelé hors du fil | Le service entier fige pendant chaque publication |
| Une exception tue la boucle | Plus rien ne publie, et rien ne le dit |
| Pas de recul après panne | Une base en difficulté est martelée |
| L'intervalle est figé au démarrage | La cadence ne se change plus sans redéployer |
| L'arrêt annule au lieu d'attendre | Un tour est interrompu au milieu |

### État à la fin du pas 13

**2 177 tests passent** avec PostgreSQL, 2 029 sans, lint propre. Cinquante-trois de plus
qu'au pas 12.

**Ce que le projet sait faire qu'il ne savait pas.** Tourner tout seul. Un événement déposé
dans la boîte est publié sans que personne appelle, à une cadence réglable sans
redéploiement, sans qu'une seconde instance le publie deux fois, et sans qu'une panne de la
base ou d'un abonné n'arrête ce qui marche encore. L'état de chaque travail se lit sur une
route, y compris celui qui n'a jamais démarré.

**Ce qui reste à brancher, et qui est nommé.** Le balayage de relance attend la table de
son suivi : son domaine est éprouvé depuis le pas 11, mais le déclarer comme travail
maintenant en ferait un « travail sans exécutant », que le tour signale précisément parce
que c'est un défaut de branchement. Restent aussi la table de la qualification, le registre
durable des tenants dans les routes d'orchestration, et l'adaptateur qui monte les
candidatures d'affectation.

**Une limite nommée pour le jour où elle comptera.** Le tour tourne pour le locataire par
défaut, c'est-à-dire le centre. C'est correct aujourd'hui : l'ouverture d'un tenant est une
saga du centre, pas du tenant qu'elle crée. Le jour où un tenant entreprise produira ses
propres événements, le tour devra boucler sur les locataires actifs et le verrou porter le
nom du locataire. La forme est prête — le nom du verrou est déjà une variable — la boucle
ne l'est pas.

---

## Pas 14 — Le registre des services

### Le manque

La plateforme est un monolithe modulaire destiné à se découper en services.
Quatorze contextes bornés, un graphe de dépendances établi flux par flux, et la règle
qu'aucun ne lit la base d'un autre. Cette découpe est ce qui rendra l'extraction
possible.

Elle était **déclarée dans un fichier de test**.

Le graphe y était tenu — le test échouait à la moindre arête interdite — et il était
**invisible à l'exécution**. Aucune route ne savait dire quels services existent.
Aucun tableau de bord ne savait répondre à « si le Référentiel tombe, qui s'arrête ? ».
Et le tableau « ce qui tourne aujourd'hui » de la section 17 du document de conception
était de la **prose recopiée à la main**, qui dérivait dès qu'on oubliait de la mettre
à jour.

⚠️ C'est la même famille de défaut que les pas 12 et 13 : quelque chose de juste sur le
papier, jamais confronté à ce que la machine en fait.

### « L'état du service » n'est pas une question, c'en est trois

C'est la décision qui commande tout le reste de ce pas.

| La question | Ce qui la fait changer | À quel rythme |
|---|---|---|
| **Construction** — est-ce écrit ? | Quelqu'un livre du code | Quelques fois par semaine |
| **Exécution** — répond-il maintenant ? | Une base tombe | À l'improviste, pour quelques minutes |
| **Dépendance** — qu'est-ce qui tombe avec lui ? | Le graphe change | Quelques fois par an |

⚠️ **Les mêler en un seul champ produit un registre qui ment dans les deux sens.** Un
service complet dont la base est tombée serait « incomplet ». Un service à peine
commencé mais dont le processus tourne serait « opérationnel ». Le second est le plus
coûteux : c'est celui qui fait croire qu'une fonctionnalité existe.

### Rien de ce qui peut être constaté n'est déclaré

**L'état de construction est constaté sur le disque et sur l'application montée.**
L'écrire à la main dans la déclaration aurait été plus simple, et il aurait dérivé —
comme a dérivé la prose du document. Un service dont on retire les routes redevient
automatiquement « en construction », sans que personne y pense.

⚠️ La joignabilité se constate sur le **schéma OpenAPI**, jamais sur `app.routes` :
cette version de FastAPI conserve des enveloppes autour des routeurs inclus, et
parcourir `app.routes` rend zéro route de contexte. Le piège avait déjà coûté un
comptage faux au pas 8 ; il est cette fois écrit dans le code qui le contourne.

⚠️ Et `EN_SERVICE` exige **des routes et un domaine**. Des routes sans règles derrière
elles ne sont pas un service, c'est une façade sur du vide.

**L'état d'exécution est constaté par une sonde**, quand le service en fournit une.
Trois sur quatorze en fournissent aujourd'hui. Les onze autres rendent `SANS_SONDE`,
qui est distinct de « répond » : un registre qui déclarerait sains les services qu'il
n'interroge pas serait exactement la sonde complaisante que le pas 12 a supprimée.

**L'état de dépendance est calculé sur le graphe**, la seule chose ici qui soit
déclarée à la main. Elle l'est parce qu'un graphe de dépendances métier ne se devine
pas : l'ordre des imports dit ce que le code **fait**, pas ce qu'il a le **droit** de
faire.

### Ce que le registre ne fait pas

Il ne découvre rien. Un registre de découverte — celui qui apprend à l'exécution qu'une
instance vient de démarrer sur tel port — n'a de sens que lorsque les services sont
réellement séparés et déployés indépendamment. Ils ne le sont pas.

Le jour où un service partira vivre ailleurs, cette déclaration deviendra sa fiche
d'inscription, et la découverte s'ajoutera sans rien retirer. Le préfixe HTTP est déjà
déclaré par service : c'est là-dessus qu'une passerelle routera.

### Ce que le registre a immédiatement révélé

| Constat | Ce qu'il dit |
|---|---|
| **Tenants est en `CAS_D_USAGE`** | Il n'expose aucune route de lui-même : il est piloté par le Transverse et par l'ordonnanceur. C'est un fait, pas un oubli, et il était invisible |
| **Le Référentiel entraîne 12 services** | La réponse qui manquait à « faut-il réveiller quelqu'un ? » |
| **Le Pilotage n'entraîne personne** | Il lit tout le monde et personne ne le lit. Son arrêt n'interrompt aucune production |
| **Le Transverse entraîne 11 services** | C'est celui dont l'arrêt se voit le plus vite : plus personne n'entre |

### Un niveau qui manquait, et le manque s'est vu tout de suite

La sonde des Tenants signale un répertoire vide. C'est le symptôme d'un garnissage
échoué neuf fois sur dix — et tout sous-domaine rend alors 404. C'est aussi
parfaitement normal sur une installation neuve, où aucun tenant n'existe encore.

Rendue `EN_PANNE`, elle marquait **treize services** comme ayant un appui tombé sur une
base vierge. Le registre affichait treize services en difficulté alors que rien
n'allait mal.

⚠️ Pire : ma propre docstring écrivait *« un répertoire vide n'est pas toujours une
panne »* juste au-dessus du code qui rendait une panne. Le commentaire et le code se
contredisaient.

D'où un troisième niveau, `SUSPECT` : quelque chose mérite un regard, sans certitude.
**Un appui suspect n'entraîne personne.** La règle qui va avec est écrite dans le code :
une sonde qui hésite entre les deux doit choisir `SUSPECT`, parce que le coût d'un
suspect qui était une panne est qu'on la voit une consultation plus tard, tandis que le
coût d'une panne qui n'en était pas une est qu'**on cesse de lire les alertes**.

### Une sonde cassée que le registre a rattrapée

La première rédaction de la sonde des Tenants appelait `repertoire.tous()`, méthode qui
n'existe pas. Le registre l'a marquée `EN_PANNE` avec le `AttributeError` en motif, et a
rendu les treize autres fiches.

C'est exactement son devoir : une sonde mal écrite ne doit pas priver l'exploitant du
registre au moment précis où il en a besoin. Le manque réel était ailleurs — un
répertoire qui ne sait pas dire combien il tient — et il a été comblé par un `__len__`.

### Le test d'architecture m'a arrêté pour la quatrième fois, et il avait raison

Ma sonde du Référentiel importait sa fonction `service()` depuis
`adaptateurs/entrant/routes_http`. Le test l'a refusée : on n'entre chez un autre
contexte que par sa surface publique.

⚠️ **C'est le point du registre tout entier.** Une sonde qui entre chez un autre service
par une porte dérobée est précisément le couplage qui empêchera de l'extraire un jour.
Le jour où le Référentiel vivra ailleurs, cette ligne deviendra un appel HTTP à sa
propre sonde. Elle ne deviendra pas un problème.

### Une mutation qui survit parce qu'elle ne change rien

Remplacer la fermeture transitive par les voisins directs dans `qui_tombe_avec` **n'a
eu aucun effet**. Vérification faite : le graphe est entièrement **plat**. Aucun service
n'a de dépendance indirecte seule ; tout ce dont un service dépend transitivement, il en
dépend aussi directement.

La mutation a donc survécu parce qu'elle n'a aucune conséquence aujourd'hui, non parce
que le test était faible.

La fermeture reste la bonne implémentation : le graphe ne restera pas plat, et le jour
où il cessera de l'être, la version directe commencerait à sous-déclarer en silence. Un
cas fige donc la platitude du graphe — pour qu'elle se signale quand elle cessera — et
un second éprouve la propriété sur un graphe greffé où elle se voit.

*Une mutation qui survit demande d'abord de vérifier qu'elle change vraiment le
comportement. Parfois la réponse est non, et c'est le constat qui est intéressant.*

Deux autres mutations avaient d'abord survécu pour une raison différente, et celle-là
condamnait le test. Aucun des quatorze services réels n'expose de routes sans domaine,
donc aucun ne distinguait les deux implémentations du garde. Le cas emploie maintenant
un service fabriqué dans un répertoire temporaire. *Un cas ne peut mesurer un garde que
s'il existe une situation où le garde change quelque chose.*

### Un test qui pend, encore

La mutation retirant la mémoire des visités dans le parcours du graphe faisait
**pendre** la suite au lieu de l'échouer — quarante-cinq secondes, puis un arrêt forcé.
Même leçon qu'au pas 13, et même correction : l'appel est désormais borné par un fil
dont on vérifie qu'il s'est terminé.

⚠️ Le cas doit aussi interroger le graphe **depuis un tiers**, et non depuis un membre
du cycle : le garde « on ne repasse pas par le point de départ » coupe déjà un cycle qui
reboucle sur lui. C'est un cycle étranger au service interrogé qui fait boucler, et
c'est le cas dangereux.

*Un registre qui fige le service est pire qu'un registre qui se trompe — c'est lui qu'on
consulte quand plus rien ne va.*

### Ce que les mutations ont vérifié

Huit mutations, huit tuées, dont trois ont demandé de corriger le test avant de tomber.

| Mutation | Ce qui tombe |
|---|---|
| Le préfixe sans borne sur le séparateur | `/souscription` attrape `/souscriptions-tierces` : des services déclarés joignables sans l'être |
| `SUSPECT` compte comme une panne | Treize services en difficulté sur une installation neuve |
| Un appui tombé n'est plus un problème | La sonde dit que le service tourne, le registre tait qu'il ne peut rien faire |
| Une sonde qui lève n'est plus rattrapée | Le registre entier devient inconsultable pour une sonde mal écrite |
| Les sondes appelées au fil des fiches | Le Référentiel sondé douze fois par consultation |
| `SANS_SONDE` devient `REPOND` | Le registre affirme précisément la chose qu'il ne sait pas |
| `EN_SERVICE` sans exiger de domaine | Une façade sur du vide passe pour un service |
| Le parcours sans mémoire des visités | Le registre ne rend plus la main sur un cycle |

### État à la fin du pas 14

**2 221 tests passent** avec PostgreSQL, 2 073 sans, lint propre. Quarante-quatre de plus
qu'au pas 13.

**Ce que le projet sait faire qu'il ne savait pas.** Dire quels services existent, jusqu'où
chacun est construit, lequel répond, et surtout **ce qui tombe avec lui**. Le graphe qui
vivait dans un fichier de test est maintenant la source unique : le même objet interdit
une arête à la relecture et répond à `GET /transverse/services`. Deux vérités recopiées
finissent toujours par diverger, et celle qui dérive est celle que personne ne relit.

**Ce qui reste à brancher, et qui est nommé.** Onze services sur quatorze n'ont pas de
sonde, et le registre le dit plutôt que de le masquer. La table du suivi de relance, celle
de la qualification, le registre durable des tenants dans les routes d'orchestration, et
l'adaptateur qui monte les candidatures d'affectation restent au tableau.

**Une limite nommée.** Le registre décrit **ce dépôt**. Il ne découvre aucune instance,
n'interroge aucun service distant, et ne saurait pas dire qu'une réplique est tombée. Ce
n'est pas un manque tant que les services partagent un processus ; ce le deviendra le jour
où le premier partira, et ce jour-là la déclaration deviendra une fiche d'inscription.

---

## Pas 15 — L'architecture cadrée sur HashiCorp Consul

### Pourquoi ce pas suit immédiatement le registre

Le pas 14 a sorti la déclaration des quatorze services du fichier de test pour la
rendre lisible à l'exécution. Ce pas la rend **applicable par le maillage**.

C'est la même déclaration, à deux points d'application différents :
`tests/test_architecture.py` la fait respecter à la relecture, en lisant les imports
réels ; Consul la fait respecter à l'exécution, par mTLS entre services. Aucun des
deux ne remplace l'autre. Le test attrape l'import interdit avant qu'il ne soit
livré ; le maillage attrape l'appel réseau qu'aucun import ne trahit.

### La correspondance, terme à terme

| Ce qu'on a | Ce que Consul en fait |
|---|---|
| `SERVICES` (nom, lettre, plan, objet) | Les enregistrements du catalogue |
| `prefixes` HTTP | Les tags de routage de la passerelle |
| `Sonde` et ses trois verdicts | Les contrôles de santé, avec leurs trois niveaux |
| `ARETES_AUTORISEES` | Les **intentions** du maillage, appliquées par mTLS |
| `EtatDeConstruction` | **Rien.** Consul décrit ce qui tourne, pas ce qui est fait |

La dernière ligne mérite d'être dite plutôt que tue. « Jusqu'où ce service est-il
écrit » n'a aucun équivalent chez Consul, et n'a pas à en avoir : cette question
reste au registre.

### Les quatorze services s'enregistrent, dans un seul processus

C'est le point qui surprend, et c'est le plus utile de ce pas.

Un agent Consul peut porter plusieurs services ; rien n'oblige à un processus par
service. Les quatorze s'enregistrent donc dès aujourd'hui, à la même adresse et au
même port, **chacun avec son propre contrôle de santé**.

Le bénéfice est immédiat, sans rien extraire : Consul montre la santé service par
service alors que tout vit encore ensemble. Et le jour où l'un part vivre ailleurs,
seule son adresse change dans l'appel au générateur. **L'extraction cesse d'être une
refonte pour devenir un déménagement.**

### Les trois niveaux se rencontrent, et ce n'est pas un hasard

Consul traduit les codes de statut de ses contrôles HTTP en trois niveaux, et un
seul code déclenche l'intermédiaire.

| Code rendu | Niveau Consul | Ce que le registre y met |
|---|---|---|
| `2xx` | *passing* | `REPOND`, et aussi `SANS_SONDE` |
| **`429`** | *warning* | `SUSPECT` |
| tout le reste | *critical* | `EN_PANNE` |

⚠️ **`429` n'est pas employé ici pour ce qu'il veut dire en HTTP.** C'est la
convention de Consul, et s'en écarter ferait ranger un service suspect parmi les
services morts — c'est-à-dire retirer du trafic un service qui fonctionne, sur un
répertoire de tenants vide.

Le rapprochement des trois niveaux n'est pas une coïncidence heureuse : le registre
en a trois parce qu'un état d'exécution en a naturellement trois, et Consul avait
fait le même constat avant nous.

⚠️ **`SANS_SONDE` rend `200`, et il faut le justifier.** Onze services sur quatorze
n'ont pas encore de sonde. Les rendre critiques afficherait un tableau Consul rouge
en permanence, et un tableau rouge en permanence n'est plus lu. Le corps de la
réponse porte l'état exact : la nuance reste disponible à qui la veut.

### Les deux pièges de la traduction

Ce sont les deux endroits où le générateur peut se tromper en produisant une
configuration parfaitement valide.

**Le graphe doit être inversé.** `ARETES_AUTORISEES` est déclaré **source vers
destinations** — « la Comptabilité lit le Portefeuille » — parce que c'est la forme
qui se relit quand on modifie un service. Consul déclare l'inverse : une entrée par
**destination**, listant ses sources admises, parce que c'est la destination qui
décide de laisser entrer.

⚠️ Engendrer sans inverser produirait des intentions syntaxiquement valides et
sémantiquement retournées : le maillage refuserait **tout le trafic réel** en
laissant passer celui qui n'existe pas.

**Le socle doit être développé.** `ARETES_AUTORISEES` ne mentionne pas le socle ;
c'est `autorises_pour` qui l'ajoute, parce que le recopier dans dix entrées ferait
dix endroits où l'oublier. Un générateur qui lirait le dictionnaire brut produirait
un maillage où **plus personne ne peut lire le Référentiel**, c'est-à-dire où plus
aucun calcul fiscal, comptable ou social n'est possible.

Les deux sont couverts par un cas qui parcourt le graphe entier, plus sa
contre-épreuve : sans elle, un générateur qui autoriserait tout le monde passerait.

### Le refus par défaut est la moitié du mécanisme

Une liste d'autorisations sur un maillage permissif est une liste de commentaires.

⚠️ Ce n'est pas une précaution théorique : Consul admet les deux réglages, et le
permissif est celui qui laisse une installation fonctionner pendant qu'on croit avoir
cloisonné. **C'est exactement la leçon du pas 12** — une règle parfaitement écrite qui
ne s'applique à personne ne se signale jamais, et c'est la troisième fois que ce
projet rencontre cette forme.

### Le sens est unique : le dépôt écrit, Consul applique

C'est la règle qui décide de tout le reste, et elle est écrite dans le module comme
dans le README d'exploitation.

Une intention corrigée à la main dans l'interface de Consul serait invisible dans le
dépôt, absente de la revue, perdue au prochain déploiement, et le test d'architecture
continuerait d'affirmer une découpe qui ne serait plus celle appliquée par le
maillage. Ce serait le défaut que le pas 14 vient de corriger, avec un tour de plus :
la vérité serait alors **hors de portée du code**.

Quand une dépendance change : on modifie `ARETES_AUTORISEES`, on relit le test
d'architecture, on régénère. Jamais l'inverse.

### Deux décisions de détail qui se paient cher

**Aucun nom Consul ne porte de tiret bas.** Consul emploie les noms de service dans
son interface DNS, où le tiret bas n'est pas admis par la RFC 1123 :
`creation_entreprise` serait irrésolvable sous son nom Python, et la panne
n'apparaîtrait qu'au premier appel entre services. Un cas vérifie aussi que la
transformation ne fait pas converger deux noms distincts.

**Un service critique n'est pas retiré tout de suite.** Soixante-douze heures avant
retrait du catalogue. Un service retiré disparaît de l'écran de l'exploitant au moment
précis où il le cherche, et « service inconnu » est bien pire que « service en panne ».

### Le jeton de sonde n'a pas de valeur par défaut

Les chemins de santé sont protégés, comme tout ce qui décrit l'architecture : la liste
de ce qui tombe avec quoi est une carte des points de rupture, et énumérer les services
est le premier geste de qui cherche quoi arrêter.

Consul sait porter un en-tête d'autorisation sur ses contrôles. Le jeton vient donc de
l'exploitation, jamais du dépôt.

⚠️ **Sans jeton, les définitions sont engendrées quand même**, avec des contrôles qui
échoueront en `401`. C'est franc : Consul dira les quatorze services critiques, et
l'exploitant cherchera le jeton. Fournir un défaut ferait pire, en laissant croire que
la protection est levée.

### Ce que les mutations ont vérifié

Quatorze mutations, toutes tuées, dont une a demandé de corriger le test.

| Mutation | Ce qui tombe |
|---|---|
| Le graphe non inversé | Le maillage refuse tout le trafic réel |
| Le socle ignoré | Plus personne ne peut lire le Référentiel |
| Le tiret bas conservé | Un service irrésolvable en DNS |
| Un jeton par défaut inventé | La protection paraît levée alors qu'elle tient |
| Le retrait immédiat d'un service critique | « Service inconnu » au lieu de « en panne » |
| Une entrée d'intention vide émise | Deux façons de dire le même refus |
| L'action `deny` au lieu d'`allow` | Deux mécanismes de refus, une question à deux réponses |
| Le maillage permissif autorisé | Les intentions deviennent des commentaires |
| `SUSPECT` rendu en `503` | Un signal incertain retire un service du trafic |
| `SUSPECT` rendu en `200` | L'avertissement disparaît |
| `SANS_SONDE` rendu en `503` | Tableau Consul rouge en permanence |
| `EN_PANNE` rendu en `200` | Consul garde un service mort dans le trafic |
| Le graphe rendu dans la sonde | La carte des points de rupture battue toutes les 10 s |
| Un nom inconnu rendu en `200` | Un service inexistant déclaré sain |

`EN_PANNE` rendu en `200` avait d'abord survécu : aucun des quatorze services n'est
réellement en panne dans un processus de test, donc le garde ne changeait rien. Le cas
force désormais la panne par une sonde. *C'est la troisième fois de ce chantier qu'un
cas ne peut mesurer un garde faute d'une situation où le garde change quelque chose.*

### État à la fin du pas 15

**2 246 tests passent** avec PostgreSQL, 2 098 sans, lint propre. Vingt-cinq de plus
qu'au pas 14.

**Ce que le projet sait faire qu'il ne savait pas.** Produire, depuis sa propre
déclaration de services, la configuration complète d'un maillage Consul : les quatorze
enregistrements avec leurs contrôles, les onze jeux d'intentions inversés et socle
développé, et le refus par défaut. La découpe qui n'était vérifiée qu'à la relecture
devient applicable à l'exécution, sans qu'aucune ligne ne soit recopiée.

**La direction nommée pour la gestion des accès.** Keycloak reprendra
l'authentification, les jetons, le second facteur et la politique de mot de passe. La
ligne à ne pas franchir est écrite dès maintenant : **Keycloak dira qui parle ; le
domaine gardera ce qu'il a le droit de faire, pour qui, et depuis quand.** En
particulier `permissions_de(roles)` — qui sait que valider une écriture et écarter un
constat ne s'accordent pas au même rôle — est une règle métier du CGA, pas une
configuration cliquée. Et le **mandat**, daté et révocable, n'a pas d'équivalent chez
Keycloak : le forcer en usurpation d'identité couperait en deux la seule trace qui
répond à « le comptable X, agissant pour le tenant Z ».

**Ce qui reste à brancher.** Onze services sur quatorze n'ont pas de sonde, et le
registre le dit. La table du suivi de relance, celle de la qualification, le registre
durable des tenants, et l'adaptateur des candidatures d'affectation restent au tableau.

---

## Pas 16 — Le balayage branché, et deux défauts qu'il a révélés

### Le manque

L'ordonnanceur n'avait qu'un seul travail. Le balayage de relance avait son domaine
éprouvé depuis le pas 11, et il lui manquait la table de son suivi : le déclarer sans
elle en aurait fait un « travail sans exécutant », que le tour signale précisément
parce que c'est un défaut de branchement.

### La table vit à part du document, et c'est une décision

La proforma est figée et vaut contrat : ce qui a été envoyé à un client doit ressortir
à l'identique dix ans plus tard, y compris devant un tribunal.

⚠️ Y inscrire un compteur de relances ferait **changer un document contractuel pour
une raison qui n'a rien de contractuel**, et chaque balayage réécrirait une ligne dont
la stabilité est précisément la propriété qu'on lui demande.

`suivi_de_relance` a donc sa table, sa clé composite `(locataire, proforma)` pour la
même raison que la proforma — un numéro est séquentiel par cabinet — et son port à
part dans le domaine.

### Le test d'architecture m'a arrêté pour la cinquième fois

Le premier branchement a fait importer la Souscription par le Transverse, où vit
l'ordonnanceur. Le graphe n'autorise au Transverse que le Référentiel et les Tenants.

Il avait raison, et pas pour une raison de forme. Un ordonnanceur qui importe chaque
service dont il fait tourner un travail devient un **point de couplage central** : il
faut le modifier pour ajouter un travail, il traîne au démarrage tout ce que ces
services traînent, et le jour où l'un part vivre ailleurs il faut le découdre.

**Le sens est donc inversé : le service déclare, l'ordonnanceur consulte.** C'est
exactement ce que fait déjà le registre pour les sondes.

| Où | Quoi |
|---|---|
| `app/orchestration/inscription.py` | Le registre. Ne connaît que des noms, des cadences et des fonctions |
| `souscription/adaptateurs/entrant/travail_de_relance.py` | La Souscription déclare son travail, chez elle |
| `app/main.py` | La composition assemble. **Le seul endroit qui a le droit de connaître tous les services** |

⚠️ **Adaptateur entrant, et non sortant.** L'ordonnanceur *appelle* ce code, comme une
requête HTTP appelle une route. Ce qui entre dans le contexte est un adaptateur
entrant, quel que soit le protocole — ici, un appel de fonction déclenché par une
horloge.

### Une justification qui plaidait pour le contraire de ce qu'elle justifiait

L'ordre des travaux était écrit ainsi depuis le pas 13 : *« Le relais avant le balayage
de relance : le balayage dépose ses envois dans la boîte, et les déposer juste après un
passage du relais les ferait attendre un tour entier. »*

**Cet argument plaide pour l'ordre inverse.** Si le retard était réel, il faudrait faire
passer le balayage d'abord.

La vraie raison est autre : **le relais est le chemin vital**. C'est lui qui ouvre les
tenants payés, et un client qui règle attend que son sous-domaine réponde. Le faire
passer derrière un balayage qui parcourt des centaines de proformas ajouterait la durée
du parcours au délai d'ouverture.

Et le coût invoqué n'existait pas : les envois du balayage attendent le passage suivant
du **relais**, toutes les quelques secondes, et non celui du **balayage**, toutes les
heures.

*Une justification se relit comme un garde se mute : en se demandant ce qu'elle
impliquerait si elle était vraie.*

### Un défaut du domaine, révélé par la chaîne complète

L'en-tête de `relance_due` affirmait depuis le pas 11 : *« Si le balayage a été arrêté
une semaine, trois paliers peuvent être dus. On n'en envoie qu'un, le plus avancé, et
les précédents sont marqués employés avec lui : ils n'ont plus d'objet. »*

**Rien ne le faisait.** Le domaine rendait un seul rang, et l'appelant n'inscrivait que
celui-là.

La conséquence, mesurée sur une proforma transmise depuis huit jours, plan à 3, 7 et
14 jours :

| Passage | Ce qui part | Rangs inscrits |
|---|---|---|
| 1 | rang **2** | `(2,)` |
| 2 | rang **1** | `(2, 1)` |

⚠️ **Le client reçoit un rappel moins urgent après un rappel plus urgent.** « Dernier
rappel avant clôture », puis « petit rappel amical ».

Aucune garde ne l'attrapait, parce que **chaque envoi était individuellement correct**.
Seule la chaîne complète, tournée deux fois, l'a montré.

La correction met la règle là où elle appartient : `RelanceADeclencher` porte désormais
`rangs_couverts`, tous les paliers que cet envoi consomme, et le domaine décide.
Calculer un `range(1, rang + 1)` dans l'adaptateur aurait supposé des rangs contigus et
sans trou — vrai aujourd'hui, et supposition invisible le jour où ça changerait.

### Un ordonnanceur sans travail, et le silence qu'il faisait

Le montage par inscription a un défaut propre : si la composition n'est pas jouée, le
registre est vide et **le tour ne fait rien, sans que rien ne le dise**.

Ce n'est pas théorique : quatre cas de `test_ordonnancement_branche.py` appelaient le
tour sans créer l'application. Ils sont passés au rouge pour la bonne raison.

Un ordonnanceur sans travail tourne indéfiniment sans rien faire : la boîte d'envoi ne
se vide plus, les tenants payés ne s'ouvrent plus, et **aucune requête n'échoue pour le
signaler**. Le rapport porte donc `aucun_travail_inscrit`, et le journal le dit en
`error` — pas en `warning`, qui se range dans le bruit de démarrage.

### Deux tests qui n'avaient aucune assertion

En écrivant la persistance du suivi, deux fonctions ont été rédigées avec leur
docstring et **sans leur corps**. La suite est passée au vert.

⚠️ C'est la pire forme de test, pire qu'un test absent : il occupe la place de celui qui
aurait attrapé la faute, il compte dans le total, et son nom affirme une propriété que
rien ne vérifie.

Un garde-fou a été posé : aucun corps de test ne peut se réduire à sa docstring. Il ne
réclame **pas** d'assertion, et c'est délibéré — une vingtaine de cas de cette suite
vérifient qu'un appel *ne lève pas*, et l'absence d'exception y est l'assertion. Leur
nom le dit. Exiger un `assert` les obligerait à écrire `assert True`, ce qui
n'ajouterait rien et masquerait la distinction. Ce qui est interdit est le corps vide,
où rien n'est même appelé.

### Ce que les mutations ont vérifié

Dix mutations, toutes tuées, dont deux ont demandé d'écrire le cas qui manquait.

| Mutation | Ce qui tombe |
|---|---|
| Seul le rang envoyé inscrit au suivi | Un rappel moins urgent suit un rappel plus urgent |
| Le suivi existant écrasé au lieu d'être repris | Un rang antérieur redevient libre et repart |
| L'identifiant sans le rang | La seconde relance remplace la première, en silence |
| La clé avec le rang | Les paliers cessent d'être sérialisés |
| Une impayée déposée comme relance | Un client engagé reçoit un modèle de relance |
| Le montant dans la charge | Des données circulent dans les journaux et les sauvegardes |
| `rangs_couverts` réduit au rang envoyé | Le défaut d'origine, dans le domaine cette fois |
| Le dernier palier jamais signalé | Le responsable ignore qu'un dossier cesse d'être suivi |

Les deux survivants du premier passage tenaient à la même cause : **le cas n'exerçait
pas le chemin**. L'un demandait un suivi déjà avancé sur une proforma dont le palier
n'était plus dû ; l'autre, deux relances successives sur la même proforma. C'est la
quatrième fois de ce chantier qu'un cas ne peut mesurer un garde faute d'une situation
où le garde change quelque chose.

### État à la fin du pas 16

**2 267 tests passent** avec PostgreSQL, 2 111 sans, lint propre. Vingt-et-un de plus
qu'au pas 15.

**Ce que le projet sait faire qu'il ne savait pas.** Relancer tout seul. Une proforma
transmise sans réponse voit son palier partir à l'échéance, une seule fois, jamais dans
le désordre, et l'événement est publié au passage suivant du relais. Une acceptée
impayée remonte à un humain sans recevoir de message. Et l'ordonnanceur a deux travaux,
déclarés chacun par le service qui les possède.

**Ce qui reste à brancher.** L'abonné qui postera réellement les `RelanceDue` — le
balayage dépose, le relais publie, et personne n'écoute encore. La table de la
qualification, le registre durable des tenants dans les routes d'orchestration, et
l'adaptateur qui monte les candidatures d'affectation. Onze services sur quatorze
restent sans sonde.

---

## Pas 17 — La boucle se referme : quelqu'un écoute enfin

### Le manque

Le balayage déposait, le relais publiait, **personne n'écoutait**. Les `RelanceDue`
partaient en « publié sans abonné » : comptés, jamais remis, et aucun client relancé.

### Le sens s'inverse une seconde fois

Le même mur qu'au pas 16, et la même réponse. Celui qui poste les relances appartient
à la Souscription ; le relais vit dans le Transverse, à qui le graphe interdit de lire
la Souscription.

Le registre d'inscription gagne donc un second versant, symétrique du premier : les
travaux s'inscrivent, **les abonnés aussi**.

⚠️ **Des fabriques, et non des abonnés.** Un abonné construit ses dépôts sur la
session de la requête ou du tour en cours ; inscrire l'objet au démarrage conserverait
une session déjà fermée, panne qui n'apparaîtrait qu'au second événement traité.

⚠️ **Plusieurs abonnés par événement sont admis**, contrairement aux travaux où un nom
vaut identité. Un `TenantOuvert` intéresse légitimement le provisionnement et, demain,
la facturation. Mais la même fabrique n'est inscrite qu'une fois : empiler produirait
trois envois du même message au même client.

### Le canal se choisit à la remise, jamais au dépôt

C'est la décision structurante de ce pas.

Entre le dépôt de l'événement et sa remise, il peut s'écouler un tour, une reprise
après panne, ou une journée d'arriéré. Pendant ce temps, un client peut avoir
**révoqué son consentement**, le centre peut avoir désactivé un canal au référentiel,
ou la messagerie peut avoir cessé d'être prête.

⚠️ Un canal figé au dépôt ferait partir un message sur un consentement révoqué. Le
recalculer à la remise le rend impossible.

### Aucune plateforme extérieure n'est bloquante, éprouvé pour de bon

C'est la règle du pas 5 bis, et ce module est le premier à la subir vraiment.

Le parcours complet a été joué sur une base réelle, avec un prospect qui **préfère la
messagerie, a consenti, et n'a pas d'adresse électronique** :

| Étape | Ce qui s'est passé |
|---|---|
| Balayage | dépose `RelanceDue` au rang 3, dernier palier |
| Relais | publie l'événement |
| Remise | messagerie non prête → écartée ; pas de courriel → écarté ; **appel** |
| Carnet | `rap-rel-PRO-2026-0001-3` → « rappeler au sujet de la proforma PRO-2026-0001 (relance de rang 3) » |

Meta n'a rien bloqué. Le repli est descendu jusqu'au plancher, et un humain a du
travail.

⚠️ **L'appel n'envoie rien : il inscrit une tâche.** C'est ce qui rend le plancher
réel. Un système dont le dernier recours serait encore un envoi automatique n'aurait
aucun plancher : il dépendrait toujours d'une passerelle, et une panne de celle-ci
arrêterait toute relance.

### Le carnet des rappels, et pourquoi la veille ne suffisait pas

Le dossier commercial sait déjà dire qu'il est **en souffrance** : resté trop
longtemps dans le même état. C'est une alerte de flux, et elle répond à « qu'est-ce
qui est bloqué ».

Un rappel répond à autre chose : « le système a décidé de vous confier ce contact-ci,
**pour ce motif-là** ». Un client sans courriel et sans consentement ne sera jamais
joignable autrement qu'au téléphone, et son dossier peut n'être en souffrance nulle
part — la relance est due, elle n'a simplement aucun canal automatique.

⚠️ **Sans ce carnet, le repli par appel ne serait pas un repli mais un silence** : la
relance serait comptée comme remise, et personne n'appellerait.

Deux règles y sont écrites, et chacune évite un appel de trop. Le motif est
**obligatoire et en clair** : une liste de références obligerait le responsable à
rouvrir chaque dossier, il cesserait de la lire, et le trou reviendrait par un autre
chemin. Et clore **demande de se nommer**, parce que c'est la question qu'on pose
quand un client rappelle en disant « on m'a déjà répondu ».

Un rappel clos refuse un second appel — `409`, pas `200`. Répondre `200` ferait qu'un
second collaborateur croirait avoir pris le contact alors que le premier l'avait pris.

### Le même piège, pour la troisième fois

`rappel_a_passer` a d'abord eu une clé primaire sur `identifiant` seul. L'écriture a
échoué sur `session.get()`, ce qui a révélé la vraie question : cet identifiant dérive
de celui de l'événement, qui dérive du **numéro de proforma**, lequel est séquentiel
par cabinet.

`rap-rel-PRO-2026-0001-2` existe donc chez chaque cabinet qui relance sa première
proforma au rang 2. Le premier à relancer aurait empêché tous les autres.

Troisième occurrence après la proforma au pas 10 et le suivi de relance au pas 16. La
règle générale se lit maintenant, et elle est écrite dans les trois tables :

> **Toute clé dérivée d'une numérotation par cabinet doit porter le locataire.**

### Ce que les mutations ont vérifié

Vingt-deux mutations sur ce pas, toutes tuées, dont une a demandé de réécrire le cas.

| Mutation | Ce qui tombe |
|---|---|
| Le canal figé au dépôt | Un message part sur un consentement révoqué |
| Le consentement ignoré | Idem, par un autre chemin |
| Un refus d'envoi avalé | La relance est comptée remise, le client n'a rien reçu |
| La messagerie sans passerelle, en silence | On croit le client relancé |
| L'appel qui envoie un courriel | Le plancher redevient une dépendance |
| Le montant dans le contexte du gabarit | Des données circulent dans les journaux |
| Les motifs d'écart perdus | On ignore pourquoi un client qui avait coché la messagerie a été appelé |
| La clé du rappel non composite | Un seul cabinet peut relancer |
| Un second appel toléré | Deux collaborateurs appellent le même client |
| Le nom facultatif à la clôture | On ne sait plus qui a parlé au client |
| Le motif vide | Le carnet devient illisible, donc ignoré |
| Les rappels clos listés en attente | La liste ne se vide jamais |
| L'ordre inversé | Le client qui attend le plus longtemps passe en dernier |

Le survivant tenait à un cas mal construit : il faisait **préférer le courriel** au
client, si bien que le courriel l'emportait immédiatement et que le consentement ne
décidait de rien. Le vrai scénario est une révocation **après** le dépôt de la
demande — le domaine refuse qu'une demande naisse avec la messagerie préférée sans
consentement, mais rien n'empêche un client de se retirer pendant qu'une relance
attend d'être remise. C'est exactement le trou qu'un canal figé laisserait ouvert.

### État à la fin du pas 17

**2 287 tests passent** avec PostgreSQL, 2 126 sans, lint propre. Vingt de plus qu’au
pas 16.

**Ce que le projet sait faire qu'il ne savait pas.** Relancer un client jusqu'au bout,
sans dépendre d'aucune plateforme extérieure. Une proforma sans réponse voit son
palier partir à l'échéance ; si la messagerie n'est pas ouverte, le courriel prend le
relais ; s'il n'y a pas d'adresse, un rappel atterrit sur l'écran d'un humain avec son
motif en clair. Le parcours d'acquisition fonctionne de la demande déposée sur la
vitrine jusqu'au tenant ouvert, **et jusqu'à la relance de celui qui n'a pas répondu.**

**Ce qui reste à brancher.** La table de la qualification, le registre durable des
tenants dans les routes d'orchestration, et l'adaptateur qui monte les candidatures
d'affectation. Onze services sur quatorze restent sans sonde. Et le gabarit de
courriel `relance_proforma` doit exister au catalogue du service de notification : le
code est demandé, le gabarit ne l'accompagne pas encore.

---

## Pas 18 — Le gabarit manquant, et le garde-fou qui l'aurait vu

### Le manque, que le pas 17 avait nommé

L'abonné de relance réclamait un gabarit de courriel nommé `relance_proforma`. Ce
code n'existait **nulle part** : le catalogue n'en contenait que cinq, tous
`compte.*`.

La conséquence était complète et silencieuse. `gabarit()` rendait `None`, `envoyer()`
rendait `False`, la remise levait `RemiseImpossible`, le relais comptait un échec,
puis un autre, puis mettait l'événement en quarantaine. **Aucune relance ne serait
jamais partie par courriel**, et le seul signe en aurait été une ligne
`Gabarit de courriel introuvable` dans un journal.

### Ce que les garde-fous existants ne pouvaient pas voir

Le fichier des courriels vérifiait déjà trois correspondances, et sérieusement : le
catalogue contre le catalogue de démonstration, le catalogue contre les contextes de
référence, et **chaque gabarit contre le contexte que ses appelants fournissent**.

⚠️ Les trois portaient sur des listes **tenues à la main**. Elles restent parfaitement
cohérentes entre elles quand on oublie d'y ajouter une entrée : c'est la définition
même d'un contrôle qui ne peut pas attraper un oubli.

Aucune ne posait la question qui manquait : *les codes que l'application réclame
existent-ils ?*

Le nouveau cas **lit le code** plutôt qu'une liste. Il parcourt `app/` en AST,
reconnaît deux formes — une chaîne passée à `envoyer(...)`, une constante de module
nommée `CODE_COURRIEL…` — et vérifie que chaque code trouvé est au catalogue. Il ne
peut pas rester d'accord avec un oubli.

⚠️ **Et il est doublé d'une contre-épreuve qui compte davantage.** Un scan qui ne
trouverait plus rien passerait au vert en ne vérifiant rien, ce qui est exactement la
forme de test dont ce chantier s'est méfié quatre fois. Un second cas exige donc que
le scan trouve au moins deux codes.

La contre-épreuve a été jouée : en remettant le code fautif d'origine, le cas tombe.

### Deux décisions dans le gabarit lui-même

**Pas de bouton d'action.** Le lien d'acceptation d'une proforma est signé, daté et à
usage unique : il expire. Le remettre à chaque relance obligerait à en forger un
nouveau depuis le gabarit, c'est-à-dire à donner à un modèle de courriel le pouvoir de
fabriquer un consentement contractuel. La relance rappelle l'existence du document ;
l'accepter passe par le lien d'origine ou par une réponse au cabinet.

**Un avertissement qui annonce la fin du suivi automatique.** « Sans réponse, cette
proposition cessera d'être relancée et votre dossier sera repris par votre
interlocuteur. » C'est vrai — le plan s'épuise au dernier palier — et le dire évite
qu'un client conclue au désintérêt.

### Une attente fausse, corrigée par le référentiel

L'épreuve de bout en bout a été rejouée avec un prospect **qui a une adresse
électronique**, en attendant que le courriel l'emporte. Un rappel téléphonique a été
créé à la place.

Ce n'est pas un défaut. Le plan de contact du référentiel place **l'appel au rang 0** :

```yaml
- canal: APPEL      # rang 0
- canal: COURRIEL   # rang 1
- canal: WHATSAPP   # rang 2, inactif
```

Le centre a décidé d'appeler d'abord, et le système respecte sa décision. C'est
exactement ce que l'en-tête de `canaux.py` annonce depuis le pas 5 bis : *« l'ordre
est celui du centre, pas une hiérarchie technique : il peut vouloir appeler d'abord,
ou écrire d'abord, selon ses effectifs du moment. »*

*C'est mon attente qui était fausse, pas le code. Un système de configuration réussi
se reconnaît à ce qu'il surprend celui qui a écrit le mécanisme.*

Le maillon qui était réellement cassé — la résolution du gabarit — a donc été éprouvé
pour lui-même : le code se résout, aucune clé ne manque, et le rendu porte bien le
numéro et le délai.

### État à la fin du pas 18

**2 289 tests passent** avec PostgreSQL, lint propre.

**Ce que le projet sait faire qu'il ne savait pas.** Envoyer réellement la relance par
courriel quand le plan du centre le prévoit, et refuser au démarrage tout code de
gabarit qui n'existe pas.

**Ce qui reste à brancher.** La table de la qualification, le registre durable des
tenants dans les routes d'orchestration, et l'adaptateur qui monte les candidatures
d'affectation. Onze services sur quatorze restent sans sonde.

---

## Pas 19 — Le tenant payé qui n'existait nulle part

### Le défaut le plus grave du chantier

L'ouverture d'un tenant écrivait dans un registre **en mémoire**, y compris en
persistance PostgreSQL. Une ligne de commentaire l'annonçait depuis le pas 8, et le
motif invoqué — « cela demande la double vérification du jeton » — n'a pas résisté à la
mesure.

Parcours complet joué sur une vraie base :

```
tour : ✓ relais : 1 publié(s)      saga : TERMINEE
lignes dans la table tenant : 0
```

⚠️ **Le système annonçait le succès de ce qu'il n'avait pas fait.** Le client payait,
l'exécution était marquée terminée, l'événement publié, et le tenant disparaissait au
redémarrage suivant. Le sous-domaine d'un abonnement payé rendait alors 404.

Rien n'échouait. C'est la troisième rencontre de cette forme sur ce chantier, après les
politiques de cloisonnement qui ne s'appliquaient à personne (pas 12) et le gabarit de
courriel qui n'existait pas (pas 18).

**Aucun test de domaine ne pouvait l'attraper.** La saga était correcte, le
provisionneur était correct, le dépôt SQL était correct. *C'est le câblage qui était
faux, et seul un parcours complet le montre.*

### Écrire en base ne suffit pas

La passerelle résout chaque nom d'hôte dans un répertoire **en mémoire**, garni depuis
la table **au démarrage**. Écrire la ligne sans inscrire au répertoire ferait que le
sous-domaine d'un client qui vient de payer ne répondrait qu'au prochain
redéploiement.

*Un client qui règle attend que son espace s'ouvre, pas la prochaine livraison.*

`RegistreDurable` écrit donc aux deux endroits. Un composite plutôt qu'une méthode de
plus sur le dépôt SQL : le dépôt ne doit rien savoir du répertoire de la passerelle,
qui appartient à un autre contexte et vivra dans un autre processus le jour où les
services seront séparés.

⚠️ **L'ordre compte.** La base d'abord, le répertoire ensuite. Si la base refuse — un
slug déjà pris —, l'exception remonte et le répertoire n'a rien appris : la passerelle
ne servira pas un tenant qui n'existe pas. L'ordre inverse laisserait un tenant
joignable en mémoire et absent de la base : le défaut d'origine, avec une fenêtre plus
courte.

⚠️ **Et `par_slug` lit en base, jamais au répertoire.** Celui-ci peut être incomplet.
Le provisionnement s'en sert pour savoir si un slug est déjà pris, et cette question ne
souffre pas d'à-peu-près : deux tenants sur le même sous-domaine se serviraient l'un
les données de l'autre.

### Un second défaut, révélé par la première correction

Le registre durable branché, la saga s'est arrêtée au **deuxième pas** :

```
saga : EN_COURS · franchies : ['SLUG_RESERVE']
motif : LIGNE_CREEE : tenant « station-bonaberi » introuvable au répertoire
```

Le tenant venait pourtant d'être écrit.

La cause est une décision explicite du projet : `autoflush` est **coupé**, parce qu'il
enverrait des `INSERT` au moindre `SELECT` intercalé, rendrait l'ordre des écritures
imprévisible et ferait échouer des contraintes loin du code fautif. *On écrit quand on
le décide.*

Or la saga d'ouverture **relit ce qu'elle vient d'écrire**, pas après pas : elle
réserve le slug, cherche le tenant par son slug pour créer sa ligne, le cherche encore
pour l'étape suivante. Sans vidage, chaque lecture manque l'écriture précédente.

Le registre vide donc explicitement. ⚠️ **Vider n'est pas valider** : la transaction
gouverne toujours l'atomicité, et le vidage ne fait qu'envoyer les écritures pour que
les lectures de la même transaction les voient.

*Une décision globale saine peut rendre faux un contrat local. Ce qui l'a montré n'est
ni la relecture ni un test unitaire, mais le parcours réel.*

### Ce que la chaîne fait maintenant

```
tour : ✓ relais | ✓ relance
saga   : TERMINEE · franchies : 7 étapes
tenant : tnt-station · station-bonaberi · ACTIF · PRET
répertoire : joignable · ACTIF
```

### Une fenêtre nommée plutôt que fermée

Le répertoire est inscrit **avant** la validation de la transaction. Si celle-ci est
annulée après coup, il garde une entrée que la base n'a pas.

La fenêtre est étroite et la conséquence bénigne : le prochain garnissage la corrige,
et entre-temps la passerelle sert un tenant dont les tables sont vides, ce qui donne un
espace sans données plutôt qu'une fuite. La fermer demanderait d'accrocher
l'inscription à la validation de la session, donc de lier le registre au cycle de vie
de SQLAlchemy pour un gain que l'exploitation ne verra pas.

*Une limite écrite vaut mieux qu'une limite corrigée au mauvais prix.*

### Ce que les mutations ont vérifié

Cinq mutations sur le registre, toutes tuées, plus la contre-épreuve du câblage
d'origine.

| Mutation | Ce qui tombe |
|---|---|
| L'écriture en base retirée | Le défaut d'origine, exactement |
| L'inscription au répertoire retirée | Le sous-domaine attend le redéploiement |
| Le vidage retiré | La saga s'arrête au deuxième pas |
| L'ordre inversé | Un tenant joignable et absent de la base |
| `par_slug` lit au répertoire | Le provisionnement croit un slug libre alors qu'il est pris |
| **Le registre mémoire remis** | Deux cas du parcours complet tombent |

Un cas de ce fichier attendait `Exception` plutôt qu'`IntegrityError`. Une attente
aveugle passerait aussi sur une faute de frappe dans le test lui-même, et le cas
affirmerait que la base refuse là où c'est le test qui plante.

### État à la fin du pas 19

**2 298 tests passent** avec PostgreSQL, lint propre.

**Ce que le projet sait faire qu'il ne savait pas.** Ouvrir un tenant pour de bon. Un
paiement encaissé écrit la ligne, mène la saga à son terme, active le tenant, et rend
son sous-domaine joignable **dans la seconde**, sans attendre un redéploiement.

**Ce qui reste à brancher.** La table de la qualification et l'adaptateur qui monte les
candidatures d'affectation. Onze services sur quatorze restent sans sonde.

---

## Pas 20 — La qualification que la route jetait

### Ce qui manquait n'était pas la table

Le tableau des restes portait « la table de la qualification » depuis le pas 6. La
lecture du code a montré autre chose, et de pire.

La route `POST /acquisition/dossiers/{reference}/qualification` construisait la
qualification, validait chaque réponse au type de sa question, rendait l'avancement,
les manquantes et les faits — puis **n'en gardait rien**. `qualification` était une
variable locale.

⚠️ Un responsable qui répondait à cinq questions sur douze et revenait le lendemain
**recommençait à zéro**, sans qu'aucune erreur ne se produise. Chaque appel rouvrait
une qualification vide et n'enregistrait que ce qu'il venait de recevoir.

Quatrième rencontre sur ce chantier d'un geste qui annonce un résultat qu'il n'a pas
produit, après le cloisonnement inappliqué, le gabarit inexistant et le tenant payé
qui n'existait nulle part.

### La reprise, et non l'ouverture

Le correctif tient en une ligne, et c'est celle qui manquait :

```python
qualification = qualifications.trouver(reference) or ouvrir_une_qualification(
    reference, questionnaire
)
```

⚠️ **`trouver` rend `None` plutôt que de lever.** Une qualification absente veut dire
« pas encore commencée », qui est l'état de tout dossier neuf : ce n'est pas une
anomalie. Lever obligerait chaque appelant à rattraper une exception pour ouvrir une
qualification vide, ce qu'il fait de toute façon.

### L'écriture après la dernière réponse, jamais au fil

Les réponses sont appliquées à un objet figé, et l'enregistrement n'a lieu qu'une fois
le lot entier validé.

⚠️ Un lot dont la troisième réponse est fautive ne laisse donc **pas** les deux
premières en base. Le responsable corrige et renvoie son lot entier, sans avoir à se
demander ce qui est déjà passé. Écrire au fil des réponses paraîtrait plus prudent et
ferait exactement l'inverse : un état partiel dont personne ne connaît la composition.

Une mutation le vérifie : déplacer l'enregistrement dans la boucle fait tomber le cas
du lot fautif.

### La version du questionnaire, conservée avec les réponses

C'est ce qui rend une qualification relisible. Un questionnaire évolue ; une question
ajoutée rendrait « incomplètes » toutes les qualifications déjà closes si l'on
mesurait l'avancement contre la version du jour.

Elle est **promue en colonne** pour être interrogeable : « quelles qualifications
emploient encore la version 1 » se pose avant de retirer un questionnaire.

### Une route de lecture, sans laquelle le reste serait invisible

`GET /acquisition/dossiers/{reference}/qualification` dit où l'on en est.

⚠️ Sans elle, le responsable qui reprend un dossier ne pourrait découvrir son
avancement **qu'en renvoyant des réponses**, c'est-à-dire en écrivant pour lire.

Un dossier jamais qualifié rend `200` avec `commencee: false`, et non `404`. Un `404`
laisserait croire que le dossier n'existe pas, alors qu'il attend seulement d'être
qualifié.

### Une clé composite, pour la quatrième fois

`(locataire, dossier)`. Une référence de dossier est propre au cabinet qui l'a émise.
Après la proforma, le suivi de relance et le carnet des rappels, la règle établie au
pas 17 s'applique sans discussion.

### Ce que les mutations ont vérifié

Trois mutations sur la route, trois tuées, plus huit cas de persistance.

| Mutation | Ce qui tombe |
|---|---|
| L'ouverture systématique au lieu de la reprise | Le défaut d'origine, exactement |
| L'enregistrement retiré | Deux cas : la reprise et la lecture |
| L'enregistrement déplacé dans la boucle | Un lot fautif laisse des réponses derrière lui |

Les cas de persistance emploient le **questionnaire réel du référentiel**, et non un
questionnaire d'essai : un questionnaire fabriqué vérifierait le mécanisme et tairait
une incohérence entre le domaine et ce que le centre a réellement rédigé.

Le dossier d'épreuve est déposé par la **route publique**, puis retrouvé dans la file
du responsable. La route publique ne rend pas la référence, et c'est délibéré : la
livrer au visiteur lui donnerait de quoi deviner celles des autres.

### État à la fin du pas 20

**2 311 tests passent** avec PostgreSQL, lint propre.

**Ce que le projet sait faire qu'il ne savait pas.** Qualifier un prospect en plusieurs
fois. Le responsable répond à ce qu'il sait, rappelle le client, complète, et
l'avancement se cumule. Ce qui a été appris survit au redémarrage, et se relit sans
écrire.

**Ce qui reste à brancher.** L'adaptateur qui monte les candidatures d'affectation, et
onze services sur quatorze restent sans sonde.

---

## Pas 21 — L'affectation qui exigeait ce que personne ne sait

### Une route utilisable en test, inutilisable en service

Le domaine de l'affectation est éprouvé depuis le pas 4 : cinq critères configurés au
référentiel, une grille, un classement, un choix motivé. La route, elle, **exigeait
que l'appelant fournisse les candidats** — avec pour chacun son nombre de dossiers
ouverts et sa charge pondérée.

⚠️ Aucune console ne peut savoir cela. Il aurait fallu refaire côté client le calcul
de la charge de tous les collaborateurs avant chaque affectation.

Les candidats sont désormais **facultatifs**. Absents, le serveur les monte depuis
l'annuaire des collaborateurs et la charge lue sur les dossiers. Présents, ils sont
employés tels quels — et cela reste utile : *« si je recrute un chargé de formalités
de plus, qui prendrait ce dossier ? »* est une question que la direction pose, et à
laquelle l'annuaire réel ne peut pas répondre.

### Le message du prospect n'est pas sa région

Une ligne de la route passait `dossier.demande.message` dans le champ `region_demande`.

Le formulaire public a **six champs, délibérément** — « chaque champ de plus est un
visiteur de moins » — et aucun n'est une région. Le message est du texte libre.

⚠️ Le champ `region_demande` est comparé à des **noms d'agence**. Un prospect qui
écrit « je suis à Bonabéri, près du marché » aurait fait correspondre une agence par
coïncidence de mots, et **une affectation se serait décidée sur un mot du texte
libre**. Le critère aurait été asymétrique par accident, ce qui est pire que nul.

Le référentiel avait déjà tranché la question, dans la règle elle-même :

> Une région non déclarée rend `meme_agence` faux, donc pénalise tout le monde
> également. L'effet est nul sur le classement, et c'est voulu : on ne devine pas où
> habite quelqu'un qui n'a rien dit.

*Le vide est franc ; la coïncidence ne l'est pas.*

### Ce que l'annuaire monte, et ce qu'il refuse de deviner

| Donnée | Source | Remarque |
|---|---|---|
| Le responsable | Les comptes du cabinet | |
| La disponibilité | L'état du compte | `ACTIF` seul, voir plus bas |
| La charge | Les dossiers non terminés | Agrégat SQL, index posé au pas 2 |
| Les compétences | Les rôles tenus | Dérivation assumée, faute d'un référentiel |
| La région | **Vide** | Non collectée par le formulaire |
| L'agence | **Vide** | Un compte n'en porte pas |

⚠️ **Les rôles porteurs sont dérivés de la permission, jamais recopiés.** Un rôle créé
demain avec `QUALIFIER_PROSPECT` entrera dans la liste sans que personne y pense ; une
liste écrite à la main l'aurait oublié, et le nouveau collaborateur n'aurait jamais
reçu de dossier sans qu'aucune erreur ne se produise.

L'administrateur en est exclu : il peut **affecter** un dossier, pas en **recevoir**
un. Celui qui répartit n'est pas celui qui traite.

### Absent, ou présent mais indisponible

La distinction décide de ce qu'un responsable lit quand personne n'a été affecté.

Un compte **sans rôle porteur** est absent : il n'a jamais eu vocation à prendre ce
dossier, et le lister encombrerait les empêchements de tous les comptables du cabinet.

Un porteur **suspendu** est candidat et indisponible : il entre dans le classement,
une règle rédhibitoire l'en écarte, et il apparaît dans les empêchements —
« Porteur ESSAI, compte suspendu ». C'est exactement ce qu'on veut lire.

⚠️ La disponibilité tient à `ACTIF` **seul**, et non à « pas suspendu ». Un compte en
attente d'activation n'a jamais ouvert de session : lui confier un dossier le
laisserait sans responsable réel jusqu'à ce que quelqu'un s'aperçoive que la personne
n'est jamais venue.

### La charge se lit au moment de l'affectation

Jamais mémorisée. Deux dossiers déposés à une minute d'intervalle doivent voir des
charges différentes, sans quoi ils iraient tous deux au même collaborateur — c'est
exactement le déséquilibre que le critère de charge existe pour éviter.

Elle est comptée par un **agrégat SQL**, et non par une liste chargée puis comptée en
Python : l'affectation interroge cette charge à chaque dossier déposé, et charger tous
les dossiers de l'année pour en compter une poignée ferait grossir le coût avec
l'historique. L'index `ix_dossier_responsable` porte `(locataire, responsable, etat)`
depuis le pas 2, posé pour cette requête.

⚠️ Les états terminaux sont exclus : un dossier payé ou sans suite ne pèse plus sur
personne, et les compter ferait qu'un ancien collaborateur productif paraîtrait
surchargé pour toujours.

### Une approximation nommée plutôt que masquée

La charge pondérée vaut le nombre de dossiers. La matrice de pondération de la
section 26 du document n'existe pas encore.

La rendre à zéro ferait croire à un cabinet où personne n'est chargé, et le critère de
charge cesserait de départager quoi que ce soit. Le nombre de dossiers ordonne
correctement ; il ne prétend rien de plus, et le code le dit.

### Ce que les mutations ont vérifié

Sept mutations, toutes tuées, dont une a demandé d'écrire le cas qui manquait.

| Mutation | Ce qui tombe |
|---|---|
| La région reprise du message | La réserve de proximité disparaît du motif |
| Les rôles porteurs recopiés | Trois cas, dont la dérivation depuis la permission |
| Tous les comptes deviennent candidats | Les empêchements se remplissent de comptables |
| La charge pondérée à zéro | Le critère de charge cesse de départager |
| Une agence inventée | La proximité penche sur une donnée fabriquée |
| Les candidats fournis ignorés | La simulation d'effectif devient impossible |
| **Le porteur suspendu déclaré disponible** | Deux cas, sur un annuaire fabriqué |

Le dernier avait d'abord survécu : **aucun compte porteur du jeu de démonstration
n'est suspendu**, le seul compte suspendu n'ayant pas de rôle qui prenne des dossiers.
Le garde ne changeait donc rien sur les données réelles. Le cas emploie maintenant un
annuaire fabriqué. *Cinquième fois de ce chantier qu'un cas ne peut mesurer un garde
faute d'une situation où le garde change quelque chose.*

### État à la fin du pas 21

**2 328 tests passent** avec PostgreSQL, lint propre. Dix-sept de plus qu'au pas 20.

**Le dernier maillon nommé du parcours est branché.** De la demande déposée sur la
vitrine au tenant ouvert, en passant par l'affectation, la qualification, le chiffrage,
la proforma, l'encaissement et la relance, chaque étape est alimentée par ce que le
système sait réellement — et dit franchement ce qu'il ne sait pas.

**Ce qui reste.** Onze services sur quatorze n'ont pas de sonde, et le registre le dit.
La matrice de pondération de charge, la région au formulaire et l'agence au compte sont
trois données que le métier devra décider de collecter ou non : le code fonctionne sans
elles et le montre.

---

## Pas 22 — Les sondes, et le sens qui s'inverse une troisième fois

### Onze services muets

Le registre du pas 14 disait `SANS_SONDE` pour onze services sur quatorze, et le
disait honnêtement. Il restait à leur en donner une.

⚠️ Le registre ne peut pas les importer : il vit dans `app/registre/`, que le test
d'architecture empêche d'importer **aucun** contexte métier. Ce n'est pas une
contrainte formelle. Un registre qui importerait chaque service pour le sonder
deviendrait le point par lequel tout se charge, et l'on veut précisément pouvoir
consulter l'état de la plateforme **quand elle va mal**.

**Le service déclare, le registre consulte.** Troisième fois que ce sens s'inverse
après les travaux périodiques (pas 16) et les abonnés aux événements (pas 17).

### Une faute légale et invisible

Trois sondes vivaient dans le module du registre, dont celle du **Référentiel**.

Le graphe autorise au Transverse de lire le Référentiel : la faute était donc
**légale, et pour cela invisible**. La quatrième sonde aurait été refusée par le test
d'architecture, et l'on aurait découvert à ce moment-là qu'il fallait tout déplacer.

*Une règle qui n'attrape une faute qu'à la quatrième occurrence est une règle qui
laisse s'installer les trois premières.*

### Ce que chaque sonde vérifie, et pourquoi ce niveau-là

| Service | Ce qui est vérifié | Verdict si absent |
|---|---|---|
| A · Référentiel | Les paramètres se chargent, et il y en a | **Panne** : douze services en dépendent |
| B · Portefeuille | La grille de charge et ses tranches | **Suspect** : il sait dire qui est qui sans elle |
| D · Conformité | Les paquets de règles | **Panne** : le centre engagerait son agrément à l'aveugle |
| E · Comptabilité | Le plan SYSCOHADA et les journaux | **Panne** : aucune écriture imputable |
| F · Obligations | Le catalogue des obligations | **Panne** : les pénalités courent en silence |
| K · Transverse | La clé de chiffrement **et** le répertoire de la passerelle | **Panne** puis **suspect** |
| L · Vitrine | Le contenu éditorial | **Suspect** : le site répond, il ne montre rien de neuf |
| M · Souscription | **Cinq** paquets du parcours | **Panne** : chacun bloque une étape |
| N · Tenants | *(rien)* | Son répertoire est vérifié par le Transverse, voir ci-dessous |

⚠️ **Le choix entre panne et suspicion n'est pas une nuance de ton.** Une panne marque
tous les dépendants comme ayant un appui tombé ; une suspicion n'entraîne personne.
Rendre `EN_PANNE` un constat qui a une explication innocente peint la moitié du
tableau en rouge sur une installation neuve, et une sonde qui crie au loup finit
ignorée.

### Le test d'architecture a corrigé un placement, pour la sixième fois

La sonde du répertoire des tenants avait été écrite dans le contexte N. Refusée : les
Tenants appartiennent au socle et ne dépendent de **rien**, pas même du Transverse.

Il avait raison, et pas pour une raison de forme. Le répertoire est celui de la
**passerelle** : garni au démarrage, consulté à chaque requête pour résoudre un nom
d'hôte, et vivant avec l'intergiciel qui le lit. Un répertoire vide se manifeste par
des `404` sur tous les sous-domaines, ce qui est un symptôme du Transverse.

*Le contexte N décide qu'un tenant existe ; le Transverse décide qu'un nom d'hôte
répond. Ce sont deux questions, et la sonde suit la seconde.*

Le contexte N reste donc `SANS_SONDE`, ce qui est exact : il n'a pas de configuration
propre dont l'absence l'empêcherait de travailler.

### La sonde de la Souscription vérifie cinq paquets, et s'arrête au premier manquant

Le parcours d'acquisition lit cinq configurations distinctes, et chacune bloque une
étape différente : sans catalogue, aucun devis ; sans questionnaire, aucune
qualification ; sans barème, aucun chiffrage ; sans plan de contact, aucun message ;
sans plan de relance, aucune relance.

⚠️ Une installation à laquelle il manque un seul de ces fichiers **répond normalement
jusqu'à l'étape concernée**, puis échoue sur un client réel.

Le premier manquant arrête la vérification, délibérément. Les cinq chargements sont
indépendants et l'on pourrait tous les tenter pour rendre la liste complète : un
exploitant corrige un fichier à la fois, et une liste de cinq lignes lui ferait croire
à cinq problèmes distincts là où le premier est souvent la cause des autres — un
dossier de référentiel mal monté les fait tous manquer ensemble.

Le motif nomme le paquet **et** son dossier : « les questionnaires de qualification :
rien de chargé depuis /…/referentiel/qualification ».

### Six services restent muets, et c'est un choix

La Collecte, la Clôture, le Social, la Création d'entreprise, le Pilotage et les
Tenants n'ont
aujourd'hui aucune configuration propre dont l'absence les empêcherait de travailler.

⚠️ **Leur inventer une sonde qui rend toujours « rien à signaler » serait pire que
l'absence** : le registre affirmerait les avoir interrogés. `SANS_SONDE` existe pour
cela, et le registre le distingue de `REPOND` depuis le pas 14.

### Un garde-fou que le module d'inscription ne peut pas porter

Le module d'inscription **ne vérifie pas** les noms de service. Aller chercher la
liste lui ferait importer la déclaration, donc créer le cycle qu'on évite.

Une sonde inscrite sous « refentiel » ne serait jamais appelée, le service resterait
`SANS_SONDE`, et rien ne dirait pourquoi. Le test garde donc la correspondance, avec
sa contre-épreuve : sans elle, une composition vidée passerait — aucune sonde inscrite
ne vise un service inconnu, trivialement.

### État à la fin du pas 22

**2 332 tests passent** avec PostgreSQL, lint propre.

**Ce que le projet sait faire qu'il ne savait pas.** Répondre, service par service, à
« celui-ci peut-il travailler ? ». **Huit** des quatorze le disent, six disent qu'on ne
leur a pas demandé, et aucun ne prétend aller bien sans avoir été interrogé.

**Ce qui reste.** Trois données que le métier devra décider de collecter ou non : la
matrice de pondération de charge, la région au formulaire, l'agence au compte. Le code
fonctionne sans elles et le montre.

---

## Pas 23 — La recette, ou l'instrument qui a trouvé quatre défauts

### Ce que coûtait de ne pas l'avoir

Quatre défauts majeurs de ce projet n'étaient visibles **que** par la chaîne entière,
jouée sur une vraie base :

| Pas | Le défaut | Ce qui l'a révélé |
|---|---|---|
| 12 | Des politiques de cloisonnement qui ne s'appliquaient à personne | Un rôle non propriétaire, essayé à la main |
| 18 | Un gabarit de courriel réclamé sous un nom inexistant | Un envoi réel, tenté à la main |
| 19 | Un tenant payé dont la table restait vide | Un paiement, joué à la main |
| 20 | Une qualification validée puis jetée | Deux appels, tapés à la main |

⚠️ **Aucun test de domaine ne pouvait les atteindre.** Chaque pièce était correcte
prise seule : le défaut vivait dans le câblage.

Et tous ont été trouvés **en tapant un script à la main**, ce qui veut dire que le
suivant ne l'aurait pas été.

### Ce que la recette vérifie, et ce qu'elle ne vérifie pas

Elle ne vérifie **aucune règle métier** : c'est le travail des cent autres fichiers.
Elle vérifie que les pièces sont **branchées entre elles**.

Trois scénarios, sur PostgreSQL, par HTTP là où des routes existent.

**Le parcours entier.** Un visiteur remplit le formulaire public à six champs. Le
responsable le trouve dans sa file — la route publique ne rend pas la référence, la
livrer donnerait de quoi deviner celles des autres. Il affecte **sans rien fournir**,
qualifie **en deux passages**, chiffre, et le paiement encaissé ouvre le tenant. On
vérifie alors la ligne **en base** et le sous-domaine joignable **tout de suite**.

**La relance sans réponse.** Une proforma transmise il y a quinze jours. Trois tours
d'ordonnanceur : le balayage dépose, le relais publie, l'abonné remet. Le plan du
centre plaçant l'appel au rang 0, un rappel atterrit sur le bureau du responsable avec
son motif. Il clôt en se nommant, et un second essai rend `409`.

**Le prospect qui préfère écrire.** ⚠️ Ce troisième scénario existe parce que le
second ne suffisait pas : le plan met l'appel en premier, si bien que **la branche
courriel n'était jamais empruntée** et que le gabarit aurait pu ne pas exister sans
que la recette s'en aperçoive. La préférence du client étant essayée avant l'ordre du
plan, un prospect qui coche « écrivez-moi » l'emprunte.

### La recette mord : les trois défauts rejoués

Chacun a été réintroduit dans le code, et la recette est passée au rouge.

| Défaut réintroduit | Scénario qui tombe |
|---|---|
| Le registre des tenants en mémoire | Le parcours entier |
| La qualification jetée | Le parcours entier |
| Le gabarit sous un nom inexistant | Le prospect qui préfère écrire |

⚠️ **Le troisième ne tombait pas avant l'ajout du troisième scénario**, et c'est
précisément ce que cette vérification a servi à découvrir. Une recette qu'on ne met
pas à l'épreuve est une recette dont on ignore ce qu'elle couvre.

### Deux manques que la recette a nommés

**Aucune route n'émet une proforma ni n'encaisse son acceptation.** Le domaine et les
cas d'usage existent, éprouvés ; la surface HTTP manque. La recette passe par le cas
d'usage, ce qui exerce le même code que la route du jour où elle existera — et
l'écrire noir sur blanc transforme un trou silencieux en reste nommé.

**La base PostgreSQL naît vide**, contrairement au mode mémoire qui naît garni. La
recette emploie `amorcer`, le même geste qu'une installation neuve, ce qui l'éprouve
au passage.

### Un piège d'outillage qui a coûté un quart d'heure

La première version ouvrait une `Session` brute pour un pas du scénario. Un test
interrompu au milieu l'a laissée **`idle in transaction`**, et cette session a bloqué
tous les `DROP TABLE` des exécutions suivantes.

⚠️ Le symptôme est le pire possible : les tests **pendent sans rien dire**. Ni erreur,
ni message, ni rapport. Le diagnostic a demandé d'aller interroger
`pg_stat_activity` :

```
 pid  |        state        | wait_event_type |          requete           |   depuis
------+---------------------+-----------------+----------------------------+-----------
 8675 | idle in transaction | Client          | SELECT dossier_commercial… | 00:09:06
 8673 | active              | Lock            | DROP TABLE dossier_commer… | 00:09:06
```

La recette emploie désormais l'unité de travail partout : elle ferme sa session quoi
qu'il arrive. *Une ressource qu'un test ouvre à la main est une ressource qu'un test
interrompu laisse ouverte.*

### État à la fin du pas 23

**2 335 tests passent** avec PostgreSQL, lint propre.

**Ce que le projet sait faire qu'il ne savait pas.** Vérifier tout seul que ses pièces
sont branchées. Les quatre défauts de câblage de ce chantier ont été trouvés à la main
et ne pouvaient l'être autrement ; le cinquième sera trouvé par la chaîne d'intégration.

---

## Pas 24 — La proforma sort enfin par l'API, et la machine à états se met à tourner

### Le dernier trou du parcours

Trois gestes du parcours n'avaient **aucune route** : émettre une proforma, la
transmettre, et recevoir son acceptation. Le domaine existait depuis le pas 10,
éprouvé ; la surface HTTP manquait.

⚠️ La conséquence est simple à dire : **aucune console n'aurait pu émettre une
proforma**. La recette du pas 23 le contournait en passant par le cas d'usage, et
c'est en l'écrivant que le trou est devenu impossible à ignorer.

### Une machine à états que rien ne conduisait

En branchant l'émission, la recette a échoué aussitôt :

```
dossier … à l'état AFFECTEE : le passage vers PROFORMA_EMISE n'existe pas.
```

Le dossier commercial a huit états et des transitions vérifiées depuis le pas 2.
**Aucune route ne les faisait avancer.** Un dossier affecté restait `AFFECTÉE` quoi
qu'on fasse : qualifier, chiffrer, rien ne le déplaçait.

⚠️ *Une machine à états qu'aucune route ne peut conduire est décorative.* Elle
protégeait des transitions que personne ne pouvait tenter.

**La règle retenue : l'état suit ce que le geste prouve, pas ce qu'il espère.**

| Geste | Ce qu'il prouve | Transition |
|---|---|---|
| Une réponse **déclarée** est enregistrée | On a parlé au prospect | `AFFECTÉE → EN CONVERSATION` |
| La qualification devient **complète** | Le dossier est instruit | `EN CONVERSATION → QUALIFIÉE` |
| Le chiffrage est demandé | Une proposition existe | `QUALIFIÉE → CHIFFRÉE` |
| La proforma est émise | Le tarif est arrêté | `CHIFFRÉE → PROFORMA ÉMISE` |
| Le client accepte par son lien | Il s'engage | `PROFORMA ÉMISE → ACCEPTÉE` |

⚠️ **Une qualification incomplète ne fait rien avancer.** C'est la garde qui compte :
avancer sur la première réponse ferait franchir l'étape à un dossier dont il manque
neuf questions sur onze, et le chiffrage porterait sur des faits absents. *L'état suit
l'achèvement, pas l'activité.*

⚠️ **Une transition impossible est ignorée, jamais levée.** Un dossier déjà chiffré
qu'on requalifie ne recule pas. La qualification a bien été enregistrée, et refuser la
requête pour une raison d'état ferait perdre le travail du responsable au moment où il
corrige une réponse.

### La route d'acceptation est publique, et elle doit l'être

Un client n'a pas de compte, et lui en imposer un pour signer un devis ferait perdre
la moitié des acceptations. **Le lien signé est l'authentification** : scellé sur le
numéro, la version et l'échéance, à usage unique.

⚠️ Le sceau est vérifié **avant** la proforma. Une vérification qui lirait d'abord le
document permettrait de sonder l'existence d'un numéro sans posséder de lien, ce qui
est précisément ce qu'on refuse ailleurs par des `404`.

⚠️ **Le lien n'est rendu qu'à l'émission.** Le remettre à chaque lecture de la
proforma multiplierait les chemins par lesquels un engagement contractuel peut fuiter.

Et `accepter` rend **trois** valeurs, dont le lien **employé** : le conserver
permettrait de le rejouer, et une acceptation rejouée est une seconde signature sur le
même engagement. La première rédaction de la route n'en dépliait que deux, et la
recette l'a dit.

### Deux décisions dans l'émission

**Le montant est arrêté par un humain, jamais recopié du chiffrage.** Le moteur
propose un intervalle ; un collaborateur habilité décide, et le motif devient
obligatoire hors de l'intervalle. Recopier la référence par défaut ferait disparaître
la décision derrière un automatisme, et le jour d'un litige personne ne saurait qui a
fixé le prix.

**Le compte qui chiffre est celui de la session**, jamais un champ du corps. Le
laisser déclarer permettrait d'attribuer un tarif à un collègue.

⚠️ Le numéro est tiré de la série, et **le conflit est possible** : entre la lecture du
dernier et l'écriture, une autre requête a pu émettre. C'est la contrainte d'unicité
qui arbitre, et le refus rend `409` plutôt que `500` — le responsable renvoie sa
demande, et la seconde tentative prend le numéro d'après. Verrouiller la série entière
sérialiserait toutes les émissions du cabinet pour une garantie identique.

### Une observation que la recette a livrée en passant

`region_siege` **est** collectée : elle figure au questionnaire de qualification.

La région existe donc, mais **après** l'affectation dans le chemin nominal. Le pas 21
avait conclu qu'elle n'était pas collectée ; la vérité est plus précise, et ouvre une
possibilité qu'il faut nommer sans la construire : une **réaffectation** après
qualification pourrait, elle, employer la région, et le critère de proximité cesserait
alors d'être neutre.

### État à la fin du pas 24

**2 337 tests passent** avec PostgreSQL, lint propre.

**Ce que le projet sait faire qu'il ne savait pas.** Conduire le parcours entier par
son API : le formulaire public, la file du responsable, l'affectation, la
qualification, le chiffrage, l'émission de la proforma, sa transmission, son
acceptation par le client sans compte — et le dossier avance à chaque geste, refusant
ce qui n'a pas été prouvé.

**Le seul geste encore sans route** est l'encaissement de l'acceptation. Le cas d'usage
existe et la recette l'exerce ; il attend son branchement au fournisseur de paiement,
qui est une décision d'exploitation plutôt qu'un travail de conception.

---

## Pas 25 — L'encaissement, et la séparation des rôles qu'il révèle

### Le dernier geste

Confirmer l'encaissement d'une proforma acceptée n'avait pas de route. Le parcours
était conduit par l'API jusqu'à l'acceptation du client, puis s'arrêtait.

### Pourquoi ce n'est pas un crochet de prestataire

C'était la question à trancher, et le projet avait déjà écrit la réponse ailleurs.

Le fournisseur de paiement employé **ne signe pas** ses notifications : ni empreinte,
ni en-tête de signature. Le module qui les reçoit le dit et en tire la bonne
conclusion : *« un statut payé ne se déduit jamais de cet appel seul : c'est le
rapprochement qui fait foi »*.

⚠️ Or ce geste **ouvre un tenant** : il crée un espace, des tables, un sous-domaine.
Le déclencher sur une notification non signée reviendrait à laisser un inconnu
provisionner de l'infrastructure en devinant un numéro de proforma.

**Un collaborateur habilité confirme donc, après rapprochement.** C'est un geste de
plus, et c'est le prix de ne pas ouvrir un espace sur parole.

### La séparation des rôles, que la recette a mise en évidence

La recette a échoué sur un `403`, et le refus était juste : le compte de direction qui
mène le parcours n'a pas `GERER_COMPTES`.

Vérification faite, la permission choisie est **exactement celle que la plateforme
emploie déjà** pour l'acte équivalent — l'activation d'un accès dans l'autre flux de
souscription — et elle n'appartient qu'à l'administrateur.

*Le commercial conclut la vente ; l'administrateur ouvre l'accès.* La recette fait
donc intervenir deux personnes, comme le cabinet le ferait, et vérifie **dans le même
scénario** que le commercial se voit refuser ce geste. C'est là que la séparation
compte, plus que dans un test isolé.

### Trois décisions dans la route

**Le sous-domaine est choisi par un humain, jamais dérivé du nom.** C'est une adresse
publique, que le client lira, dictera au téléphone et verra sur ses documents. La
dériver de « Station Bonabéri & Fils SARL » produirait quelque chose d'illisible, et
la changer plus tard casserait les liens déjà distribués.

**Il est validé ici, pas à l'ouverture.** La saga le réserve, mais elle tourne **plus
tard**, dans un tour d'ordonnanceur, et son refus n'arriverait à personne :
l'événement partirait en quarantaine et le client attendrait. ⚠️ Refuser tout de suite
met l'erreur devant les yeux de celui qui peut la corriger.

**L'identifiant de l'événement dérive du dossier**, non d'un tirage. Le relais garantit
« au moins une fois », et deux confirmations du même encaissement doivent porter le
même événement.

### Rejouable sans dommage, et la réponse le dit

Un dossier déjà payé ne dépose pas de second événement. Deux collaborateurs qui
confirment le même encaissement à une minute d'intervalle n'ouvrent pas deux tenants,
et la réponse porte `rejeu: true` plutôt que de faire silence.

La recette le vérifie en confirmant **deux fois**, puis en comptant les lignes de la
table `tenant` : une seule.

### Le test d'architecture, pour la septième fois

La première rédaction faisait importer l'atelier d'orchestration par la Souscription
pour atteindre la boîte d'envoi. Refusée : on n'entre chez un autre contexte que par
sa surface déclarée.

Le remède n'a pas été de contourner mais d'**exposer** : la boîte d'envoi n'est le
métier de personne, elle vit avec l'infrastructure au même titre que le journal
d'audit, et tout contexte a vocation à y déposer un fait qu'il vient d'établir.

⚠️ La reconstruire dans chaque appelant aurait été pire que l'import fautif : en
persistance mémoire, deux fabriques sont **deux boîtes**. L'une déposerait, l'autre
publierait, et rien ne partirait jamais sans qu'aucune erreur ne se produise.

*Sept refus, sept fois raison, et jamais pour une raison de forme.*

### État à la fin du pas 25

**Le parcours est conduit de bout en bout par l'API.** Un visiteur sans compte remplit
six champs ; le responsable l'affecte, le qualifie, le chiffre, émet la proforma et la
transmet ; le client l'accepte par un lien signé, sans compte ; l'administrateur
confirme l'encaissement ; l'ordonnanceur ouvre le tenant et le sous-domaine répond.

La recette joue exactement cette suite, sur PostgreSQL, en requêtes HTTP.

**Ce qui reste** n'est plus du code : trois données que le métier devra décider de
collecter ou non — la matrice de pondération de charge, la région au formulaire public
(elle existe au questionnaire, donc après l'affectation), l'agence au compte.

---

## Pas 26 — La chaîne d'intégration, et le garde-fou qui avait rétréci

### Une phrase à vérifier

Le pas 23 se terminait ainsi : *« les quatre défauts de câblage de ce chantier ont été
trouvés à la main ; le cinquième sera trouvé par la chaîne d'intégration. »*

Encore fallait-il que cette chaîne existe, et qu'elle exécute réellement ce que la
phrase suppose. Elle existe, elle est solide, et **elle avait silencieusement
rétréci**.

### Un garde-fou juste le jour où il a été écrit

Le fichier de vérification portait une étape remarquable :

```yaml
- name: Aucun test de persistance ne doit avoir été sauté
  run: pytest tests/test_persistance.py -q --no-header | grep -q "29 passed"
```

Son intention est excellente, et son commentaire la disait : les tests qui exigent une
base **se sautent sans bruit, en vert**, et une chaîne sans base afficherait « tests
passés » en n'ayant vérifié aucun cloisonnement.

⚠️ **Mais il couvrait un fichier sur dix-huit.**

`test_persistance.py` était le seul à réclamer une base le jour où l'étape a été
écrite. Dix-sept autres sont apparus depuis — l'isolation, les rôles PostgreSQL, le
verrou consultatif, l'ordonnancement branché, le suivi de relance, le carnet des
rappels, la qualification, le registre durable, et **la recette de bout en bout**
elle-même.

Mesuré : sans base, **181 tests se sautent**. L'étape en surveillait 29.

Et son compte figé avait un second défaut, dans l'autre sens : ajouter un test à ce
fichier cassait la chaîne pour rien, ce qui apprend à retoucher un garde-fou sans le
lire.

**Le contrôle porte désormais sur la suite entière** : aucun test sauté, quel qu'il
soit et pour quelque raison que ce soit. Il ne peut ni rétrécir avec le temps, ni
protester quand la suite grandit.

⚠️ Il emploie `-rs`, qui fait dire à pytest **pourquoi** un test a été sauté. Sans lui,
l'échec annoncerait un saut sans dire lequel, et le premier geste serait de relancer la
chaîne au lieu de lire. Éprouvé : le message rendu porte la cause **et la commande de
remède**.

Et la sortie est conservée plutôt que la suite relancée : deux minutes doublées
apprendraient à ne plus attendre la chaîne.

### Un nom qui vieillit est un nom que personne ne lit

L'intitulé du travail annonçait « ruff et **1000 tests** sur PostgreSQL ». La suite en
compte plus du double.

*Un intitulé chiffré vieillit, et personne ne le corrige parce que personne ne le
lit.* Il n'y a plus de nombre dedans.

### L'outil qui avait trouvé le défaut le plus discret n'était pas dans la chaîne

`alembic check` compare le schéma **déclaré** au schéma **migré**. C'est lui qui a
révélé, au pas 13, que le modèle posait un `unique=True` sensible à la casse là où la
migration posait un index d'expression insensible : la base de production refusait
« Station » à côté de « station », celle des tests les acceptait toutes les deux, et
deux tenants auraient répondu au même nom d'hôte.

Rien ne pouvait le signaler — chaque déclaration était valide prise seule — et
**l'outil n'était appelé nulle part automatiquement**. La divergence pouvait donc
revenir.

Elle est maintenant vérifiée à chaque proposition, et le contrôle a été éprouvé : en
réintroduisant la divergence du pas 13, `alembic check` la refuse en la nommant.

### État à la fin du pas 26

**2 337 tests passent**, lint propre, chaîne rejouée localement de bout en bout :
migrations, absence d'écart, suite complète, aucun test sauté.

**Ce que le projet sait faire qu'il ne savait pas.** Se garder lui-même sans qu'on le
lui demande. Les trois garde-fous qui comptent — la découpe en contextes, l'absence
d'écart entre modèle et migrations, et l'emploi réel de la base — s'exécutent à chaque
proposition, et aucun ne peut rétrécir en silence.

*Un garde-fou qui nomme ce qu'il surveille finit par ne plus surveiller que ce qu'il
nomme.*

---

## Pas 27 — Le document parlait du projet au passé

Le pas 26 a vérifié ce que la chaîne d'intégration prétendait surveiller. Le même geste
appliqué au **document de conception** donne le même genre de résultat, parce que c'est
le même défaut : *une phrase écrite une fois ne se met pas à jour toute seule.*

### Le tableau qui promettait ce qui était déjà livré

La section 17 s'intitule « Ce qui tourne, et ce qui reste à brancher ». Elle est le seul
endroit où un lecteur pressé va chercher l'état réel de la plateforme, donc le seul
endroit où une erreur se propage sans être discutée.

Confrontée au dépôt, elle annonçait **encore à brancher** :

- le **registre durable des tenants** — écrit au pas 19 ;
- les **candidatures d'affectation** — écrites au pas 20 ;
- la **qualification en base** — écrite au pas 21.

Et elle comptait « vingt-et-une tables » là où il y en a **26, dont 24 cloisonnées**.

Aucune de ces lignes n'était fausse le jour où elle a été écrite. Elles sont devenues
fausses en ne bougeant pas.

⚠️ **Le sens de l'erreur compte.** Un tableau qui sous-estime la plateforme fait
travailler quelqu'un sur ce qui existe déjà. Un tableau qui la surestime fait vendre ce
qui n'existe pas. Le premier coûte des journées, le second coûte la confiance ; ici
c'était le premier, et c'est le seul des deux qui passe inaperçu longtemps.

### Ce qui a remplacé la prose

Les quinze lignes du nouveau tableau ne sont pas recopiées : **chaque chiffre a été
obtenu en interrogeant le système au moment de la republication**. Le nombre de routes
vient du routeur, le nombre de tables des métadonnées SQLAlchemy, le nombre de
migrations de l'historique Alembic, le nombre de services du registre.

La note qui accompagnait le tableau disait « ce tableau était de la prose recopiée, et
il dérivait ». Elle dit maintenant :

> ⚠️ Il dérivera de nouveau, et c'est pourquoi il ne fait pas foi. La plateforme répond
> elle-même : la route `GET /transverse/services` le dit à l'instant où on le demande.

*Un document ne peut pas rester vrai ; il peut seulement dire où se trouve la vérité.*
C'est exactement le motif du registre de services du pas 18 — le service déclare, le
mécanisme central consulte — appliqué cette fois à la documentation elle-même.

### Trois décisions enterrées dans un journal

Le chantier a produit trois choix que **seul le cabinet peut trancher**, et ils
n'existaient nulle part où le cabinet les verrait. Ils étaient dans ce journal, c'est-à-
dire dans un document que personne ne lit pour prendre une décision.

Ils rejoignent `09-questions-ouvertes.md`, sous « Structurantes pour la conception ». Une
quatrième s'est ajoutée en cours de vérification, et c'est l'objet de la sous-section
suivante :

**Q13 · La région au formulaire public.** Elle est collectée, mais au questionnaire de
qualification, donc **après** l'affectation. Le premier collaborateur est choisi sans
tenir compte de la distance. Le référentiel l'avait anticipé : une région non déclarée
pénalise tout le monde également, donc le critère de proximité s'annule au lieu de se
fausser. Le cabinet arbitre entre un septième champ au formulaire — *chaque champ de
plus est un visiteur de moins* — et une réaffectation après qualification, que le
domaine sait déjà faire.

**Q14 · L'agence du collaborateur.** Le critère de proximité compare la région du
prospect à l'agence du responsable. **Un compte ne porte pas d'agence.** Tant que la
réponse manque, ce critère ne départage personne, et c'est écrit dans le code plutôt que
masqué.

**Q15 · La pondération de la charge.** L'affectation choisit le moins chargé, et la
charge vaut aujourd'hui le **nombre de dossiers en cours**. C'est une approximation
nommée : elle ordonne correctement, elle ne prétend rien de plus. Un dossier de création
de SARL pèse-t-il autant qu'une adhésion simple ? Un dossier bloqué depuis trois
semaines pèse-t-il encore ? Sans ces réponses, inventer une matrice produirait un
classement qui paraît savant et ne repose sur rien.

*Une approximation nommée est une dette ; une approximation silencieuse est un piège.*

### Vérifier ses propres phrases avant de les publier

Un pas qui reproche à un document de dériver ne peut pas publier des affirmations non
vérifiées. Les quatre du paragraphe précédent ont donc été confrontées au code, une par
une, et toutes tiennent :

| Affirmation | Vérifiée où | Verdict |
| --- | --- | --- |
| Le formulaire public a six champs | `DepotDeDemande` | ⚠️ Sa propre docstring dit « Six champs, pas trente. Chaque champ de plus est un visiteur de moins. » La formule que je croyais mienne était déjà dans le code. |
| La charge vaut le nombre de dossiers | `annuaire_des_candidats.py` | `charge_ponderee=Decimal(ouverts)`, commenté comme dérivation assumée. |
| Un compte ne porte pas d'agence | `annuaire_des_candidats.py` | `agence_responsable=""`, avec le motif écrit à côté : vide, jamais deviné. |
| Une région absente ne fausse rien | `Candidature.meme_agence` | `bool(region) and region == agence` : région vide vaut `False` pour **tous** les candidats, donc le critère s'annule au lieu de mentir. |

Et la limite de réaffectation vaut bien `REAFFECTATIONS_MAXIMALES = 3`.

### La cinquième question, que la vérification a fait apparaître

En relisant l'annuaire des candidats pour contrôler la troisième ligne, un cinquième
commentaire du même genre s'est présenté :

> Les rôles tenus, faute d'un référentiel de compétences. C'est une dérivation assumée :
> un chargé de formalités *a* la compétence « formalités », et rien ne le dit ailleurs
> aujourd'hui.

L'affectation exige la **compétence requise** par le service demandé, et le code la
déduit du **rôle tenu**. La déduction tient tant qu'un rôle vaut une compétence. Elle
cesse de tenir dès qu'un junior en formation tient le rôle avant la compétence, ce qui
est le cas ordinaire dans un cabinet qui recrute.

C'est devenu **Q16**. Elle n'a pas été trouvée en cherchant des questions : elle a été
trouvée en vérifiant une phrase voisine.

*Relire son propre code pour contrôler une affirmation en révèle une autre qu'on n'avait
pas pensé à contrôler.* C'est le même rendement que la recette du pas 23, obtenu par le
même moyen : regarder ce que le système fait plutôt que ce qu'on croit qu'il fait.

### État à la fin du pas 27

**2 337 tests passent**, lint propre. Aucun code n'a changé : ce pas ne touche que ce
que le projet dit de lui-même.

**Ce que le projet sait faire qu'il ne savait pas.** Dire où il en est sans qu'on ait à
le croire sur parole, et poser au cabinet les **quatre** questions que le chantier a fait
naître, là où le cabinet les lira. Elles ne bloquent aucun développement : le code a
choisi, dans les quatre cas, l'approximation qui s'annule proprement plutôt que celle
qui décide à la place du centre.

*Un document dit ce qu'il croit ; un système dit ce qu'il est. Le premier doit renvoyer
au second, jamais le remplacer.*

---

## Pas 28 — Le parcours savait avancer, il ne savait pas se dégager

Le pas 27 a vérifié ce que le document disait du projet. Appliqué au **code**, le
même geste donne une question simple : *quelles capacités écrites et testées
n'ont aucun appelant ?*

Trois, toutes dans le même dossier commercial.

| Capacité | Écrite | Testée | Appelée par |
| --- | --- | --- | --- |
| `classer_sans_suite` | oui | oui | **personne** |
| `en_souffrance` | oui | oui | **personne** |
| `reaffecter_le_dossier` | oui | oui | **personne** |

Neuf arêtes du graphe des transitions mènent à `SANS_SUITE`. Aucune n'était
empruntable.

### La garde que rien ne déclenchait

`charge_par_responsable` porte ce commentaire, écrit au pas 2 :

> ⚠️ **Les états terminaux sont exclus.** Un dossier payé ou sans suite ne pèse
> plus sur personne, et les compter ferait qu'un ancien collaborateur productif
> paraîtrait surchargé pour toujours.

La garde est juste. Rien ne la déclenchait, puisque rien ne mettait jamais un
dossier à `SANS_SUITE`.

**Mesuré sur la base réelle avant d'écrire une ligne** : trois prospects affectés
le 5 janvier, jamais rappelés, pèsent encore trois dossiers le 2 septembre. Le
domaine sait dire qu'ils dorment ; personne ne le lui demande. Et l'affectation,
qui choisit le moins chargé, punit indéfiniment celui qui les a reçus.

*Une garde que rien ne déclenche protège moins qu'une garde absente : l'absente,
on la voit.*

### Ce que la veille fait, et ce qu'elle refuse de faire

Un troisième travail périodique, déclaré par la Souscription et consulté par
l'ordonnanceur, comme les deux autres. Il dépose une alerte interne par dossier
immobile au-delà du délai de son état.

⚠️ **Il ne classe rien.** C'est la règle du chantier appliquée une fois de plus :
*l'état suit ce que le geste prouve, pas ce qu'il espère.* Un prospect qui ne
répond pas n'a rien refusé ; le silence prouve qu'aucun échange n'a eu lieu, pas
qu'il n'y en aura jamais. Classer sur un silence ferait décider la machine à la
place du centre, et sur la seule information qu'elle n'a pas.

Le classement est donc une route, et c'est un humain qui l'emprunte.

### Le marqueur, et pourquoi il n'est pas une commodité

Une alerte doit partir **une fois**. Sur un dossier oublié six mois, balayé tous
les quarts d'heure, la répéter produirait plus de dix-sept mille alertes pour un
seul fait, et la seule chose qu'on apprendrait est à ne plus les lire.

La première idée était de laisser la boîte d'envoi dédoublonner sur
l'identifiant. **Elle ne dédoublonne pas** : `deposer` réécrit la ligne de même
identifiant et remet `publie_le` à `None`. L'alerte serait donc **republiée**, pas
ignorée. La vérification a pris deux minutes et a évité un mécanisme qui aurait
produit exactement l'inverse de son intention.

Le marqueur vit donc sur le dossier, `signale_le`, et il est effacé par
`_passer_a` — le seul chemin par lequel l'état change, donc le seul endroit où
« l'attente recommence » est vrai. Un dossier qui bouge puis se rendort est
signalé de nouveau ; un dossier qui ne bouge pas ne l'est qu'une fois.

⚠️ **Aucune migration.** Le marqueur n'est pas promu en colonne : rien ne le
requête, la veille charge les ouverts d'un état qu'elle chargeait déjà. `alembic
check` confirme qu'il n'y a aucun écart. Une colonne de plus aurait été une
migration, un index à décider, et une occasion de divergence de plus, pour une
lecture qui ne coûte rien.

### Le motif de classement est un vocabulaire, pas du texte libre

« pas intéressé », « Pas intéressé », « pas interessé » et « ne répond pas au
tel » sont quatre lignes d'un tableau et une seule réalité. Un motif saisi
librement se compte à la main, donc ne se compte pas.

Neuf motifs vivent au référentiel, et le moteur n'en connaît aucun : il sait
qu'un motif appartient à la liste et qu'un motif peut exiger une précision. En
ajouter un ne demande aucun déploiement.

⚠️ Le plus important des neuf est **`jamais-rappele`**. C'est le seul dont la
cause est chez le cabinet, et le seul sur lequel une décision d'organisation
change quelque chose. Le distinguer d'`injoignable` est tout l'intérêt du
vocabulaire : dans un cas le prospect n'a pas pu être atteint, dans l'autre
personne n'a essayé.

Et `autre` exige une précision, sans quoi elle devient la rubrique majoritaire en
six mois et le vocabulaire ne sert plus à rien.

### La route qui répondait sans exister

`GET /acquisition/dossiers/en-souffrance`, écrite après `/dossiers/{reference}`,
était **injoignable**. FastAPI essaie les routes dans l'ordre de déclaration : le
paramètre capturait le segment littéral, et la réponse était

> `404 — aucun dossier commercial en-souffrance`

Un 404 assez crédible pour qu'on conclue que rien ne dort, plutôt que que la
route n'est jamais appelée.

*Une route masquée ne lève aucune erreur, ne manque à aucun test qui ne l'appelle
pas, et se signale par une réponse plausible.* Seul l'appel la trouve. Le
commentaire qui interdit de la redescendre est sur place, et le cas qui le garde
appelle la route et lit ce qu'elle rend.

### Le garde-fou qui était annoncé et n'existait pas

`travail_de_relance` portait cette phrase à côté de ses fabriques :

> `test_travail_de_relance.py` garde cette unicité en comptant les fabriques.

**Ce fichier n'existait pas.** Et le défaut qu'il devait empêcher s'était produit
deux fois.

En mémoire, un magasin *est* la persistance : deux instances sont deux bases sans
lien. Mesuré :

- **les dossiers** — `routes_acquisition` et `abonne_de_relance` en déclaraient
  chacun un. Un dossier déposé par le formulaire public était introuvable pour
  l'abonné, et `poster_une_relance` levait `DossierIntrouvable` sur **chaque**
  relance, jusqu'à la quarantaine ;
- **les proformas** — `routes_acquisition` et `travail_de_relance` en déclaraient
  chacun un, sous le commentaire affirmant le contraire. La route émettait dans
  l'un, le balayage lisait l'autre, et il trouvait **zéro proforma à relancer**
  quel que soit le nombre émis.

⚠️ **C'est la panne la plus coûteuse de sa catégorie parce qu'elle ne casse
rien.** Un balayage qui rend « rien à faire » et un balayage qui ne voit rien se
ressemblent exactement. Deux appels parfaitement corrects lisaient deux vérités
différentes.

Le second n'a pas été cherché : le garde écrit pour le premier l'a nommé au
premier passage. Il lit **le code**, par son arbre syntaxique, et non une liste
tenue à la main, parce qu'une liste qu'il faut penser à mettre à jour ne
surveille que ce qu'on a pensé à y mettre.

*Un commentaire qui nomme un garde-fou vaut moins qu'un garde-fou : il rassure
autant et ne surveille rien.*

### Ce que les mutations ont dit

Onze mutations, onze tuées, dont celle qui remet la route littérale après la
route à paramètre et celle qui fait réapparaître un second magasin.

Une a d'abord survécu : supprimer l'idempotence de `signaler`. Elle change bien
le comportement, mais **aucun appelant ne l'atteint**, la veille gardant avant
d'appeler. Plutôt que de retirer la garde ou de la laisser sans mesure, le
contrat a été éprouvé là où il vit, au domaine, avec la raison écrite : `signale_le`
répond à « depuis quand quelqu'un est censé savoir », et l'écraser ferait paraître
neuve une alerte vieille de trois semaines.

### Ce qui reste, et qui est nommé

La **reprise automatique** — `reaffecter_le_dossier`, troisième capacité sans
appelant — n'est pas branchée dans ce pas. L'en-tête du dossier commercial prévoit
une réaffectation après vingt-quatre heures sans contact ; c'est un acte, pas une
alerte, et il mérite son propre pas.

⚠️ La veille est d'ailleurs réglée à 48 heures sur `AFFECTÉE`, et non 24,
précisément pour ne pas alerter au moment où la machine reprendrait la main.

L'alerte n'a **aucun abonné**, et c'est assumé plutôt que subi : en brancher un
supposerait de décider à qui elle est remise, par quel canal et à quelle heure,
trois choix qui appartiennent au cabinet. Le fait est enregistré, durablement et
daté, en attendant qui le lira. La console, elle, ne dépend pas de la veille :
elle calcule l'état réel, et un ordonnanceur arrêté ne la rend pas fausse.

### État à la fin du pas 28

**2 383 tests passent** (46 de plus), aucun sauté, lint propre, `alembic check`
sans écart, 111 chemins HTTP, 3 travaux périodiques.

**Ce que le projet sait faire qu'il ne savait pas.** Se dégager. Dire ce qui
dort, une fois, et rendre sa capacité à un collaborateur quand un humain a
tranché. Et refuser de trancher à sa place.

*Une capacité sans appelant n'est pas une fonctionnalité en attente : c'est une
promesse que le code se fait à lui-même.*

---

## Pas 29 — La main qui passe, et le critère qui ne servait à rien

Le pas 28 laissait une capacité sans appelant sur trois : `reaffecter_le_dossier`.
La brancher a demandé un travail périodique et une route. **Elle a surtout révélé
que le critère de charge, sur lequel toute l'affectation repose, n'avait aucun
effet.**

### Le seul geste que la plateforme s'autorise sans qu'on le lui demande

La veille signale et ne touche à rien. La reprise **agit** : elle désigne
quelqu'un d'autre. C'est une exception à la règle du chantier, et elle est écrite
comme telle plutôt que glissée.

Elle tient parce que **le silence prouve ici exactement ce qu'on en conclut**.
Classer sans suite prétendrait savoir ce que le prospect veut, ce que personne ne
sait. Reprendre la main ne prétend rien sur le prospect : elle constate qu'aucun
échange n'a été enregistré depuis vingt-quatre heures, ce qui est un fait, et en
tire une conséquence sur **l'organisation du cabinet**, qui est son domaine.

Le geste est borné, réversible, et sans effet de bord : le dossier reste ouvert,
**rien n'est écrit au prospect**, le précédent responsable n'est pas sanctionné,
la limite de trois reprises appartient au domaine, et `actif: false` au
référentiel arrête tout sans redéploiement.

### Vingt-quatre heures pour reprendre, quarante-huit pour signaler

Ce n'est pas un réglage de confort. La reprise remet l'ancienneté à zéro : un
dossier n'atteint donc les 48 heures de la veille **que si la reprise n'a pas pu
aboutir**.

L'alerte cesse de dire « personne n'a rappelé », qui serait du bruit, et dit
*« la machine a essayé de passer la main et n'a pas pu »*, sur quoi un responsable
de pôle peut agir.

⚠️ **La recette l'a appris en tombant.** Le scénario de la veille, écrit au pas
28, a cessé de passer dès la reprise branchée : l'événement déposé était
`DossierRepris` et non `DossierEnSouffrance`. Elle mesure désormais le cas qui
donne son sens à l'alerte, un dossier dont les trois reprises sont épuisées.

*Deux mécanismes qui alertent sur le même silence produisent deux alertes pour un
fait, et celle qu'on lit finit par être celle qu'on croit.*

### Le va-et-vient entre deux personnes

`reaffecter` n'écartait que le titulaire du moment. La grille choisit le moins
chargé, et celui qui vient de rendre le dossier redevient aussitôt le moins
chargé.

**Mesuré sur cinq collaborateurs équivalents** : alpha → beta → alpha → beta. Les
trois reprises consommées, **deux personnes touchées sur cinq**, les trois autres
jamais sollicitées.

Le refus du domaine nommait pourtant le symptôme depuis le premier jour : « au-
delà, la règle d'affectation tourne en rond ». Elle tournait en rond bien avant la
limite.

Le dossier porte maintenant `responsables_passes`, et `reaffecter` refuse de
rendre la main à qui l'a déjà eue. Après correction :

| Effectif | Avant | Après |
| --- | --- | --- |
| 5 candidats | 2 personnes, 3 tours brûlés | **4 personnes**, 3 tours |
| 2 candidats | 2 personnes, 3 tours brûlés | 2 personnes, **1 tour**, deux restants pour un humain |

⚠️ Aucune migration : le champ vit dans le document JSON, comme `signale_le`.

### Et le défaut que tout cela a fait sortir

En écrivant le cas « deux dossiers repris dans le même passage ne vont pas au
même », il a échoué : les deux allaient à `beta`. La charge était pourtant bien
relue entre les deux — `{alpha: 1, beta: 1}` au second tour.

Les pénalités étaient **identiques** : 30 pour beta chargé comme pour gamma vide.

La grille du centre pénalise la charge **par seuils** : vingt points au-delà de
soixante, quarante de plus au-delà de cent vingt. Le moteur valorise une pénalité
fixe, jamais proportionnelle. **En dessous de soixante points, tous les candidats
sont donc exactement équivalents**, et le classement tombait sur l'identifiant.

Mesuré :

> Vingt dossiers déposés, quatre collaborateurs équivalents et vides au départ.
> **alpha : 20. beta : 0. gamma : 0. delta : 0.**

Le document de conception écrit « l'affectation choisit le moins chargé ». C'était
faux pour les soixante premiers points de chacun, c'est-à-dire **pour toute la vie
d'un cabinet qui démarre**.

### Le correctif est une clé de tri, pas une règle

Corriger dans la grille aurait demandé un seuil tous les cinq points, soit douze
règles pour exprimer une proportionnalité que le moteur ne sait pas valoriser.

Le classement compte désormais quatre clés, et chacune répond à une question
différente :

1. **Écartés en dernier.** Un empêchement n'est pas une grande pénalité, c'est
   autre chose : il ne se rattrape par aucun avantage.
2. **Pénalité croissante.** Ce que la grille du centre juge, et elle seule.
3. **Charge croissante.** *À préférence égale, on répartit.*
4. **Identifiant croissant.** La reproductibilité.

Après correction, les mêmes vingt dossiers : **5, 5, 5 et 5**.

⚠️ La troisième clé ne renverse jamais la deuxième, et un cas le garde : un
collaborateur vide mais éloigné ne passe pas devant un collaborateur chargé de la
bonne agence. Trente points de proximité ne se rattrapent pas en étant moins
chargé. Les seuils restent le jugement du centre ; la répartition est une
propriété du tri.

### Ce que les mutations ont dit

Dix-sept mutations, dix-sept tuées, dont le retour à l'ancienne clé de tri et
l'inversion charge/pénalité.

Deux ont d'abord survécu, et chacune a produit un cas :

- **le drapeau `actif` ignoré** — aucun cas ne le mettait à faux. *Un cas ne peut
  mesurer un garde que s'il existe une situation où le garde change quelque
  chose* ;
- **la charge remplacée par un dictionnaire vide** dans le travail — tous les cas
  ne reprenaient qu'**un** dossier, et la propriété ne se voit qu'à partir de
  deux. C'est ce cas-là, écrit pour tuer la mutation, qui a fait tomber la grille.

### Une porte pour l'humain aussi

`POST /acquisition/dossiers/{ref}/affectation` levait un **409** sur un dossier
déjà affecté. Le passage de main par un responsable de pôle, annoncé par
l'en-tête du dossier commercial depuis le premier jour, n'était joignable par
aucune route.

La même route désigne et redésigne, et la bascule porte sur **l'état** et non sur
la présence d'un responsable : un dossier en conversation a un responsable et ne
se réaffecte pas.

Au passage, le commentaire de cette route annonçait « la veille des deux heures »,
valeur qu'aucun fichier n'a jamais portée. Il renvoie désormais au référentiel
plutôt qu'à un nombre.

### État à la fin du pas 29

**2 411 tests passent** (28 de plus), aucun sauté, lint propre, `alembic check`
sans écart, 111 chemins HTTP, 4 travaux périodiques, 6 scénarios de recette.

**Ce que le projet sait faire qu'il ne savait pas.** Passer la main tout seul,
sans jamais la rendre à qui l'a déjà laissée tomber. Et répartir vraiment, ce
qu'il annonçait depuis deux chantiers sans le faire.

*Le critère le plus dangereux n'est pas celui qui manque : c'est celui qui
figure, qu'on cite, et qui ne change rien.*

---

## État des lieux au 11 septembre 2026

⚠️ **Ceci n'est pas un pas de construction.** Aucune ligne de code n'a changé pour
l'écrire. C'est une mesure, prise au dépôt, et confrontée aux six chantiers que le
document de conception annonce en section 39.

### Ce que le dépôt porte

| Mesure | Valeur |
| --- | --- |
| Code applicatif | 54 653 lignes |
| Code de test | 31 561 lignes, 85 fichiers, **2 411 cas** |
| Chemins HTTP | 111 |
| Tables | 26, dont 24 cloisonnées ; 14 migrations |
| Référentiel | 43 fichiers YAML, dont 24 règles à prédicat |
| Travaux périodiques | 4 |
| Journal de chantier | 3 chantiers, 44 pas |

### Contexte par contexte, ce qui est branché et ce qui ne l'est pas

| Contexte | Lignes | Routes | Tables | Fichiers de test | Sonde |
| --- | --- | --- | --- | --- | --- |
| M · souscription | 15 033 | 31 | 8 | 28 | oui |
| K · transverse | 9 187 | 23 | 6 | 24 | oui |
| E · comptabilité | 3 489 | 10 | 2 | 10 | oui |
| C · collecte | 3 124 | 8 | 2 | 3 | non |
| B · portefeuille | 2 514 | 4 | 1 | 9 | oui |
| I · création d'entreprise | 2 302 | 9 | 1 | 1 | non |
| F · obligations | 2 276 | 6 | 0 | 2 | oui |
| N · tenants | 2 028 | 0 | 1 | 11 | non |
| G · social | 1 902 | 4 | 2 | 1 | non |
| H · clôture | 1 565 | 2 | 0 | 1 | non |
| D · conformité | 1 526 | 5 | 0 | 10 | oui |
| A · référentiel | 897 | 3 | 0 | 12 | oui |
| J · pilotage | 882 | 1 | 0 | 1 | non |
| L · vitrine | 879 | 4 | 0 | 1 | oui |

⚠️ **Le nombre de lignes ne dit rien de la maturité.** Sept contextes servent
encore des `donnees_demo` : collecte, comptabilité, conformité, création
d'entreprise, portefeuille, social et transverse. Le rapport le plus parlant est
ailleurs : **28 fichiers de test pour la souscription, un seul pour le social**,
à volume de code comparable au cinquième.

Et : 26 383 lignes dans les trois contextes qu'ont traversés les trois chantiers,
21 544 dans les onze autres. Le projet a **de la profondeur là où la discipline
est passée, et de la surface ailleurs.**

### Les six chantiers du document, un par un

| Chantier | Verdict | Ce qui le justifie |
| --- | --- | --- |
| 1 · Les trois démarches externes | ⚠️ **non lancées** | Vérification d'entreprise, domaine, serveur. Aucune ne demande un développeur, et la première conditionne tout le canal de messagerie. |
| 2 · Les sept modèles de message | ⚠️ **rédigés, non soumis** | Ils attendent la démarche 1. |
| 3 · Le moteur d'évaluation | ✅ **terminé** | Chantier 1 du journal, 6 pas. Quatre domaines de règles s'évaluent : conformité, affectation, tarification, charge. Bornes datées, constats versionnés. |
| 4 · Le socle multi-tenant | ✅ **terminé** | Chantier 2, 8 pas. Deux rôles PostgreSQL, cloisonnement au niveau des lignes constaté au démarrage, test d'isolation, sous-domaine qui répond dans la seconde. |
| 5 · Le parcours d'acquisition | ⚠️ **complet en code, pas éprouvé en réel** | Chantier 3, 30 pas. Six scénarios de recette sur PostgreSQL par HTTP, du formulaire public au tenant ouvert. Voir la réserve ci-dessous. |
| 6 · La production comptable | ⚠️ **maquettée** | Les cinq contextes existent et exposent 33 routes, mais 4 tables sur 26, et l'essentiel sert des données de démonstration. |

### La réserve du chantier 5, nommée plutôt que tue

Le document dit : « terminé quand un parcours complet est déroulé avec un vrai
numéro et un vrai paiement ». Deux choses manquent, et une seule est du code.

**L'encaissement du parcours d'acquisition est manuel.** Un administrateur saisit
une `reference_externe`. Or l'intégration du prestataire existe, éprouvée,
commentée incident par incident — et elle est branchée à **l'autre flux**, celui
des devis et souscriptions, avec sa notification entrante `/souscription/
notification/tara`.

⚠️ **Deux parcours d'encaissement cohabitent donc sans se rejoindre** : `devis →
engagement → paiement → activation` d'un côté, `demande → dossier → proforma →
acceptation → encaissement saisi → tenant` de l'autre. Aucun des deux n'est faux ;
ils n'ont simplement jamais été raccordés, et c'est le prochain chantier évident.

**La messagerie n'est pas ouverte**, et rien n'en dépend : le repli descend vers
le courriel puis vers l'appel. C'est une démarche administrative, pas du code.

### L'estimation

Un pourcentage unique ment toujours un peu, parce qu'il mélange ce qui est dur et
ce qui est long. En voici trois, qui ne disent pas la même chose.

- **Le socle : fait.** Moteur, cloisonnement, orchestration, boîte d'envoi, saga,
  registre de services, chaîne d'intégration. C'est la partie qu'on ne refait pas
  et dont tout dépend. **La plus difficile est derrière.**
- **Le produit vendable — la vague 1 : environ 85 %.** Le chemin fonctionne de
  bout en bout sur une vraie base. Ce qui reste est le raccordement du paiement
  réel, une démarche administrative, et un essai en conditions réelles.
- **Le produit complet — la vague 2 comprise : environ la moitié.** La production
  comptable est dessinée, pas branchée, et c'est le gros du travail restant.
  Elle sera cependant plus rapide que ne le suggère son volume : le moteur écrit
  en vague 0 y rend son investissement, et la conformité y devient un paquet de
  règles à écrire plutôt qu'un chantier.

*Ce qui a été construit n'est pas la moitié du produit : c'est ce sur quoi la
seconde moitié se posera sans être réécrite.*

### Ce qui sépare de la mise en service, dans l'ordre

1. Les **trois démarches externes** — une demi-journée du centre, rien à coder,
   et elles bloquent le canal depuis le premier jour.
2. Le **raccordement du paiement réel** au parcours d'acquisition.
3. Un **essai grandeur nature** : un vrai prospect, un vrai numéro, un vrai
   règlement, un vrai tenant.
4. Les **quatre questions structurantes** — Q13 à Q16 — dont aucune ne bloque,
   mais dont chacune rend le système plus juste.

⚠️ **Rien n'est commité depuis le début des trois chantiers.** C'est le seul
élément de cet état des lieux qui ne relève d'aucune décision technique.

---

## Pas 30 — Les deux parcours d'encaissement se rejoignent

L'état des lieux du 11 septembre avait nommé ce chantier : *« deux parcours
d'encaissement cohabitent sans se rejoindre »*. Le parcours d'acquisition vendait
sans encaisser — un administrateur saisissait une référence à la main — pendant
que l'intégration du prestataire, éprouvée et commentée incident par incident,
tournait à côté pour le flux des devis et souscriptions.

C'est ce qui séparait le produit de « vendable ».

### Ce qui était générique, et ce qui ne l'était pas

Le règlement, le rapprochement, l'idempotence, le contrôle de montant et
l'expiration sont imposés par le **prestataire** : ils sont les mêmes qu'on règle
un abonnement ou une proforma. La **suite** diffère : une souscription réglée
s'active et ouvre un accès ; une proforma réglée ouvre un tenant.

Tout était écrit pour la souscription seule. `appliquer_evenement` faisait
`souscriptions.lire(paiement.souscription)` sans se demander si c'en était une.

La suite est devenue un `SuiteDuPaiement`, choisi d'après `paiement.nature` dans
une **table** passée à la fonction. C'est le motif d'inversion de l'ordonnanceur
et du registre : *le mécanisme central ne connaît pas ses cas, il consulte.*
Ajouter un troisième objet payable n'ouvrira plus ce fichier.

⚠️ `SuiteDeSouscription` est le code d'avant, **déplacé sans être réécrit**.
C'était la condition pour que le raccordement ne change rien au flux qui
fonctionnait : un déplacement se relit, une réécriture se vérifie.

### Un champ qui allait mentir

Le paiement portait `souscription: str`. Le parcours allait y écrire un numéro de
proforma.

C'est exactement le défaut du pas 21, où le message libre d'un prospect voyageait
dans un champ nommé `region_demande` et servait à décider d'une affectation. Le
champ est devenu `reference_reglee`, colonne et index compris, par une migration
jouée dans les deux sens.

*Un nom qui ment coûte plus cher qu'une migration : il se lit dans les journaux,
dans les exports, et dans la tête de celui qui écrira la requête suivante.*

⚠️ `nature`, elle, n'est **pas** une colonne : rien ne l'interroge. Elle vit dans
le document JSON, et les lignes déjà écrites se relisent avec sa valeur par
défaut, `SOUSCRIPTION`, qui est ce qu'elles sont toutes.

### Qui choisit l'adresse, quand plus personne n'est là

Le slug du futur tenant est *choisi par un humain, jamais dérivé du nom* : c'est
une adresse, elle se communique, on n'en change pas.

Tant que l'encaissement était saisi à la main, ce choix tenait dans le même geste.
**Dès lors que l'opérateur notifie tout seul, plus personne n'est là pour
choisir.**

Le slug est donc retenu **avant** le règlement, sur le dossier, par le
collaborateur qui prépare l'espace — et `retenir_le_slug` refuse de le remplacer :
une adresse annoncée au client ne se change pas en cours de règlement. Rejouable
avec la même valeur, pour qu'une demande relancée après un appel manqué
n'échoue pas.

Un règlement notifié sur un dossier sans adresse retenue **n'ouvre rien** et le
dit, sous une action que la supervision cherche.

### L'argument qu'il a fallu réexaminer, pas contourner

La route de confirmation manuelle portait ceci, et c'était juste :

> Le fournisseur **ne signe pas** ses notifications. Or ce geste ouvre un tenant.
> Le déclencher sur une notification non signée reviendrait à laisser un inconnu
> provisionner de l'infrastructure **en devinant un numéro de proforma**.

Le risque nommé était réel **parce que rien n'était initié de notre côté** : la
notification serait arrivée sur un numéro de proforma, qui est imprimé sur un
document et que le client cite au téléphone.

⚠️ Il disparaît dès lors que le paiement est créé avant l'appel. Une notification
ne produit d'effet que si elle se rapproche d'un paiement **que nous avons créé**,
sur une clé d'idempotence que nous avons tirée et jamais publiée, pour un montant
que nous avons fixé et qui est vérifié. Deviner un numéro de proforma ne suffit
plus à rien.

Le commentaire a été réécrit pour dire ce qui a changé, plutôt que supprimé. Et la
confirmation manuelle **reste** : un client qui règle en espèces au guichet
n'emprunte aucun téléphone. Les deux chemins dérivent le même identifiant
d'événement du dossier, donc une seule saga — la recette le vérifie en confirmant
à la main un règlement déjà notifié, et en comptant les tenants.

### Ce que les mutations ont dit

Onze mutations, onze tuées. Deux ont d'abord survécu :

- **une nature sans suite passait en silence** — aucun cas n'exerçait le câblage
  manquant. C'est pourtant le seul cas où l'argent arrive et où personne ne sait
  quoi en faire ;
- **la suite ouvrait malgré l'absence d'adresse retenue** — un cas que
  l'automatisation vient précisément de rendre possible, et qui ne pouvait pas
  exister tant qu'un humain fournissait le slug dans le même geste.

### Le test d'architecture, une huitième fois

La première version de `SuiteDeProforma` montait ses dépôts elle-même, en
important les routes. Refusée : la couche application ne dépend pas des
adaptateurs.

⚠️ Il avait raison, et pas pour une raison de forme : le module serait devenu
inutilisable par tout appelant qui n'est pas une route, **à commencer par la
réconciliation** — qui est précisément l'autre chemin devant produire le même
effet. Tout est injecté ; c'est le comptoir qui câble.

### Un privilège hérité est un privilège que la prochaine base n'aura pas

En remettant le schéma à neuf pour vérifier les migrations, un cas des rôles
PostgreSQL a cessé de passer. Le diagnostic rendait « appliqué » là où il aurait
dû nommer le contournement du propriétaire.

La cause n'était pas dans le code : le cas s'appuyait sur les privilèges que
`PUBLIC` portait sur le schéma d'une base héritée. **Depuis PostgreSQL 15, un
schéma `public` recréé n'accorde plus rien à `PUBLIC`** — le rôle propriétaire ne
voyait aucune table.

Il aurait donc échoué en intégration continue, sur une base neuve, jamais sur le
poste où il a été écrit. Le décor accorde maintenant explicitement, et le cas a
été éprouvé sur un schéma dépouillé. C'est la seconde fois que ce défaut se
présente au projet, après le `GRANT CREATE ON SCHEMA public` du socle.

### État à la fin du pas 30

**2 423 tests passent**, aucun sauté, lint propre, `alembic check` sans écart sur
un schéma remigré de zéro, 15 migrations, 112 chemins HTTP, 7 scénarios de
recette.

**Ce que le projet sait faire qu'il ne savait pas.** Vendre. Un client accepte sa
proforma, un collaborateur prépare son espace et demande le débit, le client
valide sur son téléphone, et son espace s'ouvre — sans qu'aucun humain ne
confirme quoi que ce soit.

*Deux mécanismes corrects qui ne se parlent pas coûtent plus cher qu'un
mécanisme manquant : on ne cherche pas ce qu'on croit avoir.*

---

## Pas 31 — Le filet qui n'était jamais jeté

Le pas 30 a rendu le produit vendable en faisant reposer l'encaissement sur la
notification du prestataire. Restait à vérifier ce qui se passe **quand elle
n'arrive pas**.

Le module de réconciliation existait, et se décrivait lui-même :

> Le filet : repêcher les encaissements dont la notification ne nous est jamais
> parvenue. […] C'est le scénario qui coûte le plus cher : l'argent est parti, le
> service n'est pas ouvert, le client attend. Au bout d'un moment il repaie — et
> c'est là que le double-encaissement apparaît, non pas par un défaut de notre
> code, mais par **notre silence**.

⚠️ **Ce filet n'était jamais jeté.** `reconcilier` n'avait qu'un appelant : une
route qu'un exploitant devait penser à cliquer, sous `LIRE_PILOTAGE`. *Le module
écrit contre notre silence était lui-même silencieux.*

Quatrième capacité du chantier à exister sans appelant automatique, après
`classer_sans_suite`, `en_souffrance` et `reaffecter_le_dossier`.

### Ce que le pas 30 a changé à l'enjeu

Tant que le parcours faisait confirmer l'encaissement à la main, une notification
perdue se rattrapait par le geste humain qui suivait : le collaborateur voyait le
règlement sur son relevé et confirmait.

Depuis que le parcours s'appuie sur la notification, **une notification perdue est
un client qui a payé et dont l'espace ne s'ouvre pas.** Rien ne l'aurait signalé
avant trente jours, quand le balayage remonte les acceptées impayées — et il
aurait alors réclamé son règlement à quelqu'un qui avait payé.

⚠️ **La péremption vivait dedans aussi.** Rien d'autre ne fait expirer un
paiement : sans ce travail, une opération abandonnée restait « en attente »
indéfiniment et encombrait le rapprochement de candidats morts.

### Brancher le filet aurait produit une tempête d'appels

La réconciliation interrogeait **chaque** paiement en attente à chaque passage.
C'était sans conséquence tant qu'un humain cliquait de temps en temps.

Toutes les cinq minutes, sur une opération que l'abonné a abandonnée et qui reste
en attente vingt-quatre heures, cela fait **288 appels au prestataire pour un
paiement que personne ne validera jamais.**

Le compteur `verifications` portait déjà ce commentaire, écrit au pas où il a été
créé : *« sert à repérer les opérations sur lesquelles on s'acharne »*. Il sert
désormais à ne plus s'acharner : l'espacement double à chaque tentative et
plafonne à une heure.

| | Sans espacement | Avec |
| --- | --- | --- |
| Appels sur 24 h pour un paiement abandonné | **288** | **26** |
| Délai avant le premier appel | 5 min | 5 min |

⚠️ **Vingt-six, et non vingt-sept** comme mon estimation de tête l'annonçait. Le
cas qui compte les appels a corrigé le commentaire que j'avais écrit avant lui.
*Un chiffre estimé dans un commentaire est un chiffre faux qui a l'air d'une
mesure.*

Et la contre-épreuve est gardée : l'espacement **ne retarde pas le premier
appel**. Échanger 288 appels inutiles contre un client qui attend plus longtemps
serait un mauvais marché.

### L'ordre des cinq travaux

La réconciliation passe **juste après le relais**, avant tout le reste. C'est le
seul travail qui touche à de l'argent déjà encaissé ; elle passe donc avant la
relance, qui réclamerait sinon son règlement à quelqu'un qui vient de payer.

⚠️ **C'est aussi le seul qui appelle le réseau.** Un prestataire lent retarde le
tour entier, et c'est assumé : l'ordonnanceur compte les échecs, recule, et
abandonne au bout de vingt tentatives. Un travail qui traiterait le réseau à part
demanderait un second mécanisme d'exécution pour un seul cas.

### La recette, huitième volet

Un client règle. **Aucune notification n'est postée.** Le prestataire, interrogé
par nous, répond que c'est réglé — et l'espace s'ouvre.

⚠️ Avec sa contre-épreuve, qui est le cœur du volet : quand le prestataire ne
répond pas, les tours passent et **rien ne bouge**. Sans elle, un filet qui
ouvrirait tous les tenants sans rien vérifier passerait le premier cas sans
broncher.

### État à la fin du pas 31

**2 436 tests passent**, aucun sauté, lint propre, `alembic check` sans écart sur
un schéma remigré de zéro, 112 chemins HTTP, **5 travaux périodiques**, 11
scénarios de recette.

**Ce que le projet sait faire qu'il ne savait pas.** Rattraper un règlement dont
personne ne l'a prévenu, sans harceler le prestataire pour autant.

*Un filet qu'on ne jette pas n'est pas un filet : c'est une corde bien rangée.*

---

## Pas 32 — Le garde-fou qui ne gardait qu'une forme de donnée

La vague 1 étant close côté code, j'ai appliqué une dernière fois la méthode qui a
produit les quatre pas précédents, mais sur **tout le dépôt** : *quelles fonctions
publiques ne sont nommées dans aucun test ?*

Le balayage en a rendu **65 sur 698**. La plupart sont éprouvées indirectement, par
l'agrégat qui les appelle — ce n'est pas la même chose qu'« intestées ».

Trois entrées venaient du journal d'audit, qui est le seul endroit du projet dont
une faiblesse ne se voit jamais.

### Le premier diagnostic était faux

`expurger`, `calculer_empreinte` et `corps_canonique` semblaient n'avoir aucun
appelant. **Elles en ont un** : elles sont appelées dans leur propre module, par
`EntreeAudit.poser`. Mon balayage excluait le fichier d'origine.

⚠️ Vérifier avant d'annoncer a évité de « corriger » un chaînage parfaitement
branché. *Un outil de détection produit des suspects, pas des verdicts.*

### Mais le garde-fou, lui, ne tenait pas

Le module d'audit porte cette phrase depuis le premier jour :

> `_EXPURGES` retire ces clés à l'écriture — **un garde-fou, parce que compter sur
> la vigilance de l'appelant est ce qui finit toujours par échouer.**

Éprouvé à la main sur six formes de données, il en laissait passer deux.

| Forme | Avant | Après |
| --- | --- | --- |
| `{"mot_de_passe": "…"}` | masqué | masqué |
| `{"compte": {"mot_de_passe": "…"}}` | masqué | masqué |
| **`{"comptes": [{"mot_de_passe": "…"}]}`** | **en clair** | masqué |
| **`{"jetons": ["…", "…"]}`** | **en clair** | masqué |
| `{"Mot De Passe": "…"}` | en clair | masqué |
| `{"reference_externe": "eyJhbGci…"}` | intact | intact |

**La récursion descendait dans les dictionnaires et pas dans les listes.** Un
secret rangé dans une liste entrait en clair dans un journal lu par tous les
porteurs de `LIRE_AUDIT` et conservé dix ans.

⚠️ Et la comparaison étant exacte, **`jetons` n'est pas `jeton`** : une clé au
pluriel portant une liste de secrets fuyait entièrement. Le cas est d'autant plus
probable que c'est précisément sous une clé au pluriel qu'on range plusieurs
secrets.

### Latent, et c'est le sujet

Cinq appelants passent aujourd'hui une liste au journal — `sorted(portee)`,
`sorted(charge_utile)`, les codes de réserves d'un dépôt. **Ce sont des listes de
chaînes** : rien ne fuit à cette heure.

Le défaut était donc latent exactement autant que la vigilance sur laquelle ce
garde-fou existe pour ne pas compter. Le premier à écrire
`apres={"comptes": [c.model_dump() for c in comptes]}` aurait versé des empreintes
de mots de passe dans un journal conservé dix ans, et rien ne l'aurait signalé.

*Un garde-fou qui ne couvre qu'une forme de donnée reporte l'échec, il ne l'évite
pas. Et un garde-fou sans test est une intention.*

### Ce que le fichier de cas garde

Soixante-huit cas, dont la contre-épreuve qui manquait : **les données ordinaires
traversent intactes**. Sans elle, un masque qui expurgerait tout passerait chacun
des autres, et le journal d'audit ne dirait plus rien.

Deux décisions y sont gardées explicitement :

- **le masquage se fait par la clé, jamais par la valeur.** On ne masque pas ce
  qui *ressemble* à un secret : deviner produirait des faux positifs illisibles —
  une référence de paiement masquée parce qu'elle ressemble à un jeton — et des
  faux négatifs rassurants ;
- **une clé sensible portant un objet est masquée en entier**, et non parcourue.
  Descendre d'abord laisserait le secret sous une clé que `_EXPURGES` ne connaît
  pas : `{"jeton": {"valeur": "…"}}` serait sorti inchangé.

⚠️ Les cas passent par `EntreeAudit.poser` et non par `expurger` seule : c'est la
**construction de l'entrée** qui doit masquer, et vérifier la fonction sans son
appelant laisserait passer le jour où l'appel disparaît.

Six mutations, six tuées, dont celle qui restaure exactement le défaut trouvé et
celle qui déplacerait l'expurgation après le calcul de l'empreinte — ce qui
rendrait toute entrée expurgée invérifiable.

### État à la fin du pas 32

**2 504 tests passent** (68 de plus), aucun sauté, lint propre. Aucune migration :
le correctif ne touche qu'une fonction de domaine et la liste qu'elle consulte.

**Ce que le projet sait faire qu'il ne savait pas.** Tenir sa promesse la plus
ancienne : *rien de secret n'entre au journal*, quelle que soit la forme sous
laquelle un appelant le présente.

*La dette la plus chère n'est pas le garde-fou absent — on le voit. C'est le
garde-fou présent qui ne couvre que le cas auquel on avait pensé.*

### Remesure au 11 septembre 2026, après les pas 30 à 32

⚠️ Toujours pas un pas de construction : une mesure.

| | 11/09, matin | 11/09, soir |
| --- | --- | --- |
| Pas faits | 44 | **47** |
| Tests | 2 411 | **2 504** |
| Travaux périodiques | 4 | **5** |
| Chemins HTTP | 111 | **112** |
| Produit utilisable | ~55 % | **~60 %** |

Ce qui a bougé tient en une ligne : **les trois chantiers restants de la vague 1
n'en sont plus.** Le raccordement du paiement (pas 30) et le filet des règlements
perdus (pas 31) étaient les deux seuls éléments de code ; le pas 32 est une dette
de sécurité remboursée, hors périmètre de vague.

Il ne reste de la vague 1 **rien qui se code** : les trois démarches externes et
un essai grandeur nature. Les 40 % restants sont donc, à une ligne près, la
vague 2.

*Les quarante pour cent restants iront plus vite que les soixante faits : le
moteur, le cloisonnement, l'orchestration, la boîte d'envoi, la saga et le
mécanisme de paiement sont écrits une fois et servent partout.*

---

## Pas 33 — Le rapport mène à l'écriture, enfin

Premier pas hors du parcours d'acquisition. Avant de construire, j'ai déroulé la
chaîne comptable sur PostgreSQL pour voir ce qu'elle fait vraiment — la méthode
qui a trouvé quatre défauts de câblage au chantier 3.

### Mon estimation de « maquette » était fausse

Mesuré : l'amorçage écrit **6 entreprises, 30 pièces justificatives, 14 écritures,
6 plans d'imputation** en base. Les 33 routes de la chaîne répondent. La balance
d'AGRO-NKOLO SA est équilibrée à 11 018 700, l'échéancier porte ses obligations, la
complétude se calcule.

⚠️ J'avais classé la vague 2 « maquettée, 25 % » parce que sept contextes
contiennent un `donnees_demo.py`. **La présence d'un jeu de démonstration ne dit
rien de la persistance** : ici il sert à *amorcer* une vraie base, pas à se
substituer à elle. *Un indice n'est pas une mesure.*

### Ce qui manquait vraiment

`proposition_ecriture.py` annonce depuis sa première ligne ce qu'il referme :

> C'est ce qui referme le parcours E03 → E02 → E10 des maquettes : la boîte de
> réception mène au rapport, **le rapport mène à l'écriture**.

**Aucune route ne l'empruntait.** `proposer_ecriture_achat` n'était appelée que par
le jeu de démonstration.

Le comptable disposait donc de deux gestes sans passerelle : contrôler une facture
d'un côté — ce que la route de conformité appelle elle-même *« l'acte central du
produit »* — et saisir une écriture à la main de l'autre. Le moteur savait déduire
la seconde du premier, **TVA rejetée comprise**, et personne ne le lui demandait.

⚠️ La conséquence n'est pas une commodité perdue. Un comptable qui saisit à la main
récupère une TVA que le moteur venait de refuser, et **rien ne le signale avant le
contrôle fiscal**.

### Proposer, jamais enregistrer

Le module pose la règle, et la route la respecte :

> Le comptable garde la main. Un logiciel qui comptabiliserait tout seul
> déplacerait la responsabilité vers l'éditeur — or c'est le Centre qui engage son
> agrément.

`POST /comptabilite/dossiers/{e}/propositions` contrôle et rend. **Rien n'est
écrit.** Et ce qu'elle rend est **le corps de la requête suivante, au champ près** :
l'écran n'a qu'à le poster vers `/ecritures`. Un client qui recomposerait les
lignes à partir du rapport referait le travail du moteur, et le referait autrement
le jour où une règle change.

Éprouvé sur les cinq factures canoniques du § 13.5, dont les verdicts sont
verrouillés ailleurs :

| Facture | Verdict | Résultat |
| --- | --- | --- |
| F-2026-0413 | Conforme | 3 lignes, équilibrée |
| F-2026-0412 | TVA non déductible | **4 lignes** — la TVA rejetée s'incorpore au coût |
| F-2026-0415 | Avertissement | 3 lignes |
| F-2026-0414 | **Anomalie bloquante** | refus, l'anomalie nommée, **aucun numéro consommé** |

### Le numéro est pressenti, jamais réservé

`proposer_ecriture_achat` exige un numéro pour construire son entité. Celui-ci
vient du registre et sert à l'affichage : il n'est pas consommé.

⚠️ Le réserver créerait un trou si le comptable renonce — et *un trou dans un
journal est le premier signal que cherche un contrôleur*. Un cas propose, refuse,
propose de nouveau, et vérifie que le numéro n'a pas avancé. Un second poste la
saisie et vérifie que le numéro obtenu **est** celui annoncé : un numéro pressenti
qui ne serait pas celui attribué serait pire que pas de numéro du tout.

### Une permission, et pas deux

`SAISIR_ECRITURE` seule. Exiger aussi `CONTROLER_CONFORMITE` rendrait le chemin sûr
plus difficile que le chemin libre : un comptable habilité à saisir mais pas à
contrôler passerait par la saisie manuelle et perdrait la vérification.

*Un garde-fou qui coûte plus cher que son contournement ne garde rien.*

Le contrôle n'est pas ici un droit qu'on accorde, c'est une contrainte qu'on
impose.

### Le test d'architecture, une neuvième fois

Ma première version montait le moteur de conformité en important ses adaptateurs.
Refusé : *on n'entre chez l'autre que par sa surface publique.*

⚠️ Il avait raison, et le motif est concret : le montage aurait existé en **deux
exemplaires**, celui de la conformité et le mien. Ils auraient divergé au premier
changement de dépôt, et deux écrans auraient rendu **deux verdicts sur la même
facture**.

Le montage a donc déménagé vers `conformite/api.py`, et les deux appelants y
passent. L'arête `comptabilite → conformite` était déjà déclarée au registre des
services : la dépendance était autorisée, c'est la porte qui ne l'était pas.

### Le garde-fou que personne ne pouvait remettre à zéro

Cinq cas tombaient **au montage de leur décor**, seulement en suite complète.

La limitation de débit autorise trente connexions par cinq minutes et par adresse.
Quinze fichiers de test ouvrent une session, certains une par cas : le compteur
survivait d'un cas au suivant, et la suite épuisait le budget.

⚠️ `Limiteur.vider` portait pourtant déjà la mention **« destinée aux tests »**.
La méthode existait ; l'objet était hors d'atteinte, l'intergiciel construisant le
sien. Le limiteur par défaut est désormais partagé et joignable, et le décor le
vide avant chaque cas.

*Un garde-fou de production qu'aucun décor ne peut réinitialiser fait tomber les
cas pour une raison qui n'est pas la leur — et l'on finit par désactiver le
garde-fou plutôt que par le comprendre.*

C'est la pire forme d'échec : il ne se reproduit pas isolément, donc on le croit
imaginaire.

### État à la fin du pas 33

**2 517 tests passent** (13 de plus), aucun sauté, lint propre, 113 chemins HTTP.
Aucune migration : la route ne persiste rien, c'est sa raison d'être.

**Ce que le projet sait faire qu'il ne savait pas.** Tirer une écriture d'une
facture contrôlée, avec le verdict qui commande la forme de l'écriture, et refuser
de proposer quoi que ce soit sur une pièce que le droit interdit de comptabiliser.

*Deux gestes corrects sans passerelle laissent à un humain le soin d'un
raccordement que la machine sait faire — et c'est lui qu'on blâmera.*

---

## Pas 34 — Un moteur d'échange, pas un pilote Sage

Demande du cabinet : *« il faut des adaptateurs pour que notre système s'adapte au
système final »*. Un centre de gestion ne remplace pas le logiciel de ses
adhérents — il s'y branche.

### Ce qui n'existait pas, et ce qui existait déjà

Mesuré : **rien** pour l'échange comptable. `FormatTransmission` existe, mais il
sert aux portails de l'administration — CSV, JSON, XML pour la DGI. Le document de
conception ne parle d'« export » que pour la sortie d'un tenant.

En revanche `EcritureComptable` **est** le pivot : journal, exercice, numéro, date,
libellé, pièce, référence externe, et ses lignes avec compte, sens, montant, tiers
et lettrage. Rien à inventer.

### Le refus d'écrire `ExportateurSage`

Écrire une classe par logiciel conduit au même endroit à chaque fois : trois
classes qui font la même chose à trois virgules près, qui divergent au premier
correctif, et un quatrième logiciel qui demande un déploiement.

⚠️ **Le format est donc une donnée du référentiel.** Un profil déclare son
séparateur, son encodage, sa fin de ligne, son format de date, l'ordre de ses
colonnes et la forme du sens. Brancher un progiciel de plus, c'est déposer un
fichier YAML.

C'est la même discipline que la grille d'affectation, le plan de relance et les
délais de veille. *Ce qui varie d'un client à l'autre n'appartient pas au code.*

Deux profils livrés : `sage-ligne100` et `pivot-csv`. Le même exercice, deux
fichiers différents :

| | `pivot-csv` | `sage-ligne100` |
| --- | --- | --- |
| Encodage | utf-8 | **cp1252** |
| Fin de ligne | `\n` | `\r\n` |
| Décimale | `.` | `,` |
| Sens | colonne unique, D/C | colonnes débit et crédit |
| Compte | tel quel | complété à 8 positions |

⚠️ Le profil Sage porte sa propre réserve, reprise par l'API : **il n'a pas été
confronté à une installation réelle du client.** Le jour où le centre fournira un
fichier d'exemple issu de son Sage, c'est ce fichier qui fera foi — et le corriger
ne demandera aucun déploiement. C'est le sens même du mécanisme.

### Les trois pièges qui coûtent un fichier entier

Deux d'entre eux ne se voient qu'**après** l'import chez le client.

**L'encodage.** Beaucoup d'importeurs francophones attendent `cp1252`. Livrer de
l'UTF-8 abîme *tous* les libellés accentués. Déclaré au profil, jamais supposé, et
le fichier part **en octets** : le faire passer par du JSON le reconvertirait.

**Le séparateur dans un libellé.** Il décale toutes les colonnes suivantes. On
substitue, **on n'entoure pas de guillemets** : les importeurs hérités prennent le
guillemet pour un caractère du libellé, et le client verrait `"Quincaillerie"` avec
ses guillemets dans son grand livre, sur chaque ligne, pour toujours.

**Le séparateur de milliers.** `2 840 000,00` est lu comme `2` par un importeur qui
coupe au premier caractère non numérique — et il ne le dit pas.

### Ce qui ne sort jamais

**Un brouillon n'est pas engagé par le centre.** L'exporter le ferait tenir pour
arrêté par le client, qui déclare avec — puis découvre au contrôle que le centre l'a
corrigé depuis.

Le lot est refusé **en entier et nominativement**. Filtrer en silence livrerait un
fichier incomplet, et l'écart ne se verrait qu'à la balance.

### Le cas qui a cessé de mesurer, et le garde qui l'a dit

Une mutation a survécu : remplacer l'encodage du profil par `utf-8`. Mon cas
n'assertait que sur l'en-tête `Journal;Date;NoPiece;Compte` — de l'ASCII pur, où
les deux encodages produisent **les mêmes octets**. Il n'éprouvait pas un encodage,
il éprouvait qu'il y avait des octets.

J'ai donc ajouté une assertion sur un accent, et avec elle un garde :
`assert accentues, "ce cas ne mesure plus rien"`.

⚠️ **Il a mordu immédiatement.** Le profil Sage n'exporte pas le libellé de
l'écriture, seulement celui des lignes : mon accent tombait dans une colonne
absente. Sans ce garde, le cas serait redevenu décoratif en silence.

*Un cas d'encodage dont l'accent tombe dans une colonne absente ne mesure rien.*

### Trois invariants du domaine, rencontrés en écrivant les cas

Chacun a refusé mon décor, et chacun m'a appris une règle réelle :

- une écriture validée porte **qui** l'a validée et **quand** — *« le Centre engage
  sa responsabilité : la validation est un acte personnel »* ;
- elle porte **sa pièce justificative** — *« sans elle, la traçabilité est rompue
  dès le premier maillon »* ;
- on ne saisit pas sur un compte absent du plan.

### Et le garde-fou qui a fait tomber mes propres cas

Trois cas échouaient en suite complète : un autre fichier laisse un brouillon dans
le journal des achats, partagé, et l'export refusait le lot.

⚠️ **Le garde-fou fonctionnait.** C'étaient mes cas qui dépendaient d'un état qui
ne leur appartenait pas. Ils possèdent désormais leur journal — les opérations
diverses — et y posent leur propre écriture, saisie puis validée par l'API. Au
passage, ils éprouvent la chaîne réelle au lieu de s'appuyer sur un décor.

C'est la deuxième fois en deux pas. *Un cas qui lit ce que d'autres ont écrit
n'éprouve pas ce qu'il croit.*

### État à la fin du pas 34

**2 543 tests passent** (26 de plus), aucun sauté, lint propre, 115 chemins HTTP.
Aucune migration : l'échange ne persiste rien, il rend.

**Ce que le projet sait faire qu'il ne savait pas.** Livrer ses écritures au
logiciel du client, dans la forme que ce logiciel attend, sans qu'aucun nom de
progiciel ne figure dans le code.

*Un adaptateur par logiciel est une dette qui grandit avec le marché ; un moteur
piloté par un profil est un marché qui grandit sans dette.*

---

## Pas 35 — Les manifestes, et le contrôle qui les a corrigés

Le cabinet a tranché : la plateforme ira en orchestrateur de conteneurs. Les
manifestes existent désormais, dans `deploiement/kubernetes/`.

### Ce qui était déjà prêt, et qu'on ne rattrape pas après coup

Mesuré avant d'écrire une ligne :

- **le verrou consultatif** — `pg_try_advisory_xact_lock`, transactionnel, relâché
  à la validation : N répliques peuvent tourner, un travail ne s'exécute qu'une
  fois ;
- **l'état de l'ordonnanceur en base**, pas en mémoire : un redéploiement ne remet
  aucun compteur à zéro ;
- **`/sante` qui interroge réellement la base** et rend 503 ;
- **14 enregistrements Consul et 11 intentions** engendrés depuis la déclaration :
  les mêmes données donnent les `Service` et les règles de réseau.

Ces quatre points sont ceux qu'on ne greffe pas sur un système en production. Ils
étaient là.

### La décision centrale tient en une ligne

⚠️ **La sonde de vivacité ne teste jamais la base.**

`/sante` rend 503 quand la base est injoignable. C'est exactement ce qu'il faut
pour la *disponibilité* : le pod sort du service, on cesse de lui envoyer des
adhérents.

C'est exactement ce qu'il ne faut pas pour la *vivacité*. Redémarrer un processus
parce que la base est tombée ne répare rien — la base est toujours tombée. On
obtient la flotte entière en redémarrage, les journaux perdus à chaque cycle, et la
panne, qui était dans la base, devient indiscernable d'une panne applicative.

*Une sonde de vivacité qui teste une dépendance transforme une panne de dépendance
en panne générale.*

La vivacité teste donc le port. Le démarrage a sa propre sonde : les confondre
oblige à choisir entre un démarrage étranglé et une panne détectée trois minutes
trop tard.

### Cinq autres décisions, chacune avec son piège

| Décision | Ce que l'autre choix coûte |
| --- | --- |
| Volume **`ReadWriteMany`** | `ReadWriteOnce` marche à une réplique et casse à la seconde, sans message utile. Le défaut n'apparaît **jamais en essai**. |
| Migration en **`Job`** | Un conteneur d'initialisation tourne sur chaque pod : trois répliques, trois migrations simultanées, et une migration pendant qu'une ancienne version sert le trafic. |
| **Deux clés de secret**, deux rôles | Le même rôle pour la migration et l'application rend le cloisonnement inopérant **sans qu'aucune erreur ne se produise**. |
| Certificat **générique, donc DNS-01** | HTTP-01 ne délivre pas de générique. Sans lui, chaque cabinet demanderait une intervention et l'ouverture d'un tenant cesserait d'être immédiate. |
| Ordonnanceur **séparé, une réplique** | Le verrou rend deux répliques *correctes* — c'est ce qui rend la mise à jour progressive sûre — mais le gain est nul et le bruit réel. |

⚠️ Le certificat générique est une **contrainte sur le choix du registrar**, et elle
se décide avant l'achat du domaine — pas après.

### Le contrôle a trouvé deux défauts dans les manifestes qu'il garde

Un manifeste ment sans rien casser. Une variable `CGA_ORDONNANCEUR_EN_PROCESUS` —
un « S » de moins — est acceptée par l'orchestrateur, ignorée par l'application, et
la boucle de fond ne démarre jamais. Aucune erreur, aucun journal : des relances
qui ne partent pas, découvertes par un client.

Le cas qui confronte chaque variable à `Configuration` a donc été écrit. **Il a
mordu immédiatement, sur mes propres manifestes** :

- `CGA_SECRET_JETONS` — inventée. La vraie clé est `CGA_CLE_CHIFFREMENT` ;
- une seconde adresse de base nommée comme une variable d'environnement, alors
  que c'est une clé de secret que seul le `Job` consomme. Renommée `url-base-migration`
  pour qu'on ne la branche pas par mégarde sur l'API.

*Un fichier de configuration qui nomme une clé inexistante ne fait rien, en
silence. C'est la panne la moins chère à éviter et la plus chère à trouver.*

### Neuf mutations, sur les manifestes eux-mêmes

Chacune restaure un défaut réel, et chacune est tuée : la variable mal
orthographiée, la vivacité branchée sur `/sante`, le volume mono-écrivain, la
migration sur le rôle de l'application, le certificat non générique, l'émetteur en
HTTP-01, l'étiquette `:latest`, un mot de passe versionné, et la boucle de fond
allumée dans chaque réplique.

### Ce que ces manifestes ne font pas, écrit plutôt que sous-entendu

Ils ne déploient **pas PostgreSQL** : une base de production se prend administrée,
ou s'installe avec un opérateur qui sait sauvegarder et restaurer. Un `StatefulSet`
écrit à la main donne l'illusion des deux.

Ils ne portent ni supervision ni journalisation centralisée.

⚠️ **Ils ne sont pas éprouvés sur un cluster réel.** Ils sont lus, contrôlés contre
la configuration, et mutés — pas appliqués. Et la section 37 arrête toujours
l'hébergement sur un serveur unique : ces manifestes sont la marche suivante,
préparée pour que l'ajout de machines ne coûte rien au code.

### État à la fin du pas 35

**2 560 tests passent** (17 de plus), aucun sauté, lint propre. Six manifestes,
aucune ligne de code applicatif modifiée.

**Ce que le projet sait faire qu'il ne savait pas.** Se déployer sur plusieurs
machines sans qu'aucune décision de conception ne soit à reprendre — et refuser un
manifeste qui nommerait une clé que le code ignore.

*Un manifeste n'échoue pas : il applique autre chose que ce qu'on croit lui avoir
demandé.*

---

## Pas 36 — Le client remplissait les champs du système

Le chaînon amont de la vague 2 : **un adhérent dépose ses justificatifs**. J'ai
déroulé le parcours avec un vrai compte du jeu de démonstration, `jp.nkoa` de
Bâtiment Plus, avant d'écrire une ligne.

### Deux choses tenaient, et il faut le dire

L'adhérent voit **sa seule entreprise sur six**, ses huit pièces, ses trois
demandes. Déposer sur le dossier d'un autre est refusé, et le message ne confirme
même pas que ce dossier existe — un message qui distinguerait « inconnu » de
« hors de votre périmètre » permettrait d'énumérer les dossiers du cabinet.

La **portée** tenait. C'est le **contenu** qui ne tenait pas.

### Ce qu'un client pouvait déclarer de lui-même

La route acceptait l'entité du domaine comme corps de requête. Mesuré :

| Prétention du client | Enregistrée ? |
| --- | --- |
| `etat: COMPTABILISEE` | **oui** |
| `reference_ecriture: AC-000042` | **oui** |
| `empreinte: aaaa…` fabriquée | **oui** |
| `depose_le: 2020-01-01`, six ans plus tôt | **oui** |
| `recue_le` de son choix | **oui** |
| `depose_par` | **personne** |

Chacune a une conséquence précise. La complétude et le score de risque lisent
l'état : **une pièce manquante se cachait en se déclarant comptabilisée.** Les
délais de collecte, les relances et la veille lisent la date de dépôt : un dépôt
antidaté fabriquait un historique. Et l'acte n'avait **aucun auteur**, alors
qu'une session était ouverte — dans un projet dont tout le reste tient qu'un acte
est personnel.

### Le domaine écrivait la règle, la route donnait la plume

C'est ce qui rend ce défaut instructif. Rien ne manquait à la connaissance du
projet :

- `recue_le` porte ce commentaire au domaine : *« horodatée par le système à
  l'arrivée effective. **Seule celle-ci fait foi** »* ;
- le module de collecte affirme, quinze lignes plus bas, que *« l'empreinte est
  recalculée par le serveur et fait foi, ce qui rend la détection de doublon
  indépendante de ce que le client affirme »*. C'était vrai de `/fichiers` — qui
  borne sa lecture et détermine le type par les octets — et **faux de
  `/pieces`** ;
- et le contexte comptable énonce la discipline : *« Il ne porte ni numéro, ni
  état, ni valideur. Ce qu'un client ne peut pas envoyer n'a pas besoin d'être
  contrôlé. »*

**La comptabilité l'appliquait. La collecte, non.** Le même dépôt savait refuser
de croire le client sur le type MIME et le croyait sur l'état comptable.

### Ce que le système pose désormais

| Champ | Posé par |
| --- | --- |
| `identifiant` | le serveur, **dérivé de l'empreinte** |
| `recue_le` | l'horloge du serveur |
| `etat` | `REÇUE`, toujours |
| `depose_par` | la session ouverte |
| `taille_octets`, `empreinte` | le magasin, par relecture |
| `reference_ecriture`, `reference_rapport` | les contextes qui les produisent |

⚠️ **L'empreinte est relue, jamais crue.** Le fichier est rechargé et son
empreinte recalculée : cela vérifie à la fois que le client ne l'a pas inventée
**et que le magasin n'a pas été altéré**. C'est le seul moment du parcours où
cette vérification coûte une lecture déjà nécessaire.

⚠️ **La date déclarée reste admise, mais bornée** à quatre-vingt-dix jours. Le
domaine a raison de l'admettre : une pièce remise par coursier a été déposée avant
d'être saisie. Six ans, non — c'est une reprise d'historique, geste du cabinet.

### Refusé, et non ignoré

Un champ du système envoyé par le client produit un **422 qui le nomme**.

Ignorer aurait rendu un 201 à un client qui croit avoir posé l'état. Il ne l'a pas
posé — mais rien ne le lui dit, et l'intégrateur qui a écrit ce script ne
l'apprendra jamais. *Un critère silencieusement absent est indiscernable d'un
critère satisfait.*

### Deux conséquences que je n'avais pas prévues

**Le dépôt est devenu rejouable.** L'identifiant dérivant de l'empreinte,
redéposer le même fichier rend la **même** pièce : une seule ligne. Un client dont
la connexion tombe après l'envoi recevait auparavant un 409 « déjà reçu » sur sa
propre reprise — un refus qui lui disait qu'il avait fauté alors qu'il avait bien
fait. C'est mieux que le 409, et c'est la discipline de la boîte d'envoi et de la
saga : *rejouer ne doit rien casser.* La description de la route a été réécrite.

**Une pièce sans document n'est plus déposable.** L'empreinte est obligatoire. Le
domaine admet une pièce sans fichier, et il a raison — mais ce cas-là s'appelle une
**demande de pièce**, il a son agrégat, ses routes, son échéance et son caractère
bloquant. Accepter un dépôt sans document ferait entrer dans la boîte de réception
des lignes que rien ne permet de contrôler, et la complétude les compterait comme
reçues.

### Le cas qui distingue « relu » de « cru »

Une mutation a survécu : remplacer le recalcul de l'empreinte par la valeur reçue.
Tant que le client envoie la vraie clé, les deux donnent le même résultat.

Ce qui les sépare est un **magasin altéré** : un contenu qui ne correspond plus à
sa clé. Le cas range un tel fichier et vérifie que le dépôt refuse en nommant
l'altération — et dit **de ne rien déposer**, parce que poursuivre sur un document
dont l'intégrité est rompue est pire que s'arrêter.

Sept mutations, sept tuées.

### État à la fin du pas 36

**2 581 tests passent** (21 de plus), aucun sauté, lint propre. Aucune migration :
le domaine n'a pas changé, seule la porte.

**Ce que le projet sait faire qu'il ne savait pas.** Accepter un dépôt d'un client
sans le laisser écrire ce qui engage le cabinet.

*Une route qui accepte l'entité du domaine comme corps de requête donne au client
la plume du système — et le domaine a beau écrire la règle, c'est la route qui
décide.*

---

## Pas 37 — Une classe de défaut, pas un cas isolé

Le pas 36 a trouvé une route qui laissait un client déclarer l'état, l'auteur et
l'horodatage d'une pièce. La question qui suit n'est pas « est-ce corrigé ? » mais
**« combien y en a-t-il d'autres ? »**

### Le balayage, et ce qu'il a d'abord montré

Trente-cinq routes acceptent un corps de requête. Le balayage en rend :

- **une** qui accepte une entité du domaine ;
- **zéro** qui expose un champ dont le système est propriétaire.

⚠️ Mais le premier balayage écrit rendait **une route sur cent vingt-deux**. Les
contextes sont montés en sous-routeurs, et `app.routes` ne rend que le premier
niveau. Il aurait déclaré « aucun défaut » sur un dépôt qu'il n'avait pas lu.

*Un contrôle qui ne regarde rien passe toujours.* C'est pourquoi ce fichier
commence par vérifier qu'il voit cent routes et trente corps, avant de vérifier
quoi que ce soit d'autre.

### La seule route restante, et pourquoi elle reste

`POST /conformite/controler` accepte `FactureAControler`, une entité du domaine.

Vérifié plutôt que supposé : ses sept champs sont **purement descriptifs** —
contexte, destinataire, document, émetteur, lignes, montants, règlement. Aucun
état, aucun auteur, aucun horodatage. Et la route **ne persiste rien** : elle
calcule un verdict et le rend.

Il n'y a donc aucun champ dont le système soit propriétaire, et c'est précisément
cette description que l'appelant doit fournir. L'exception est nommée, avec son
motif, et un cas vérifie que **chaque exception porte le sien** : une exception
sans motif est une exception qu'on ajoutera sans y penser.

⚠️ Un autre cas vérifie que les exceptions sont **toutes employées**. Laissée en
place une fois devenue inutile, une exception rouvrirait la porte le jour où
quelqu'un réemploie ce nom, sans qu'aucune discussion n'ait lieu.

### Deux contrôles, parce qu'un seul ne suffit pas

Le premier attrape la **réutilisation d'un agrégat** : trois lignes gagnées, et le
client tient la plume du système.

Le second attrape un modèle de requête écrit exprès **mais qui expose un champ de
trop** — un `etat`, un `depose_par`, un `recue_le`. C'est le cas le plus probable
maintenant que le premier est gardé : on recopie un champ de l'entité sans y
penser.

Vingt-trois noms sont surveillés, regroupés par ce qu'ils défont :

| Famille | Ce qu'un client qui l'écrit défait |
| --- | --- |
| `etat`, `statut` | la complétude et le score de risque, qui lisent l'état |
| `recue_le`, `cree_le`, `publie_le`… | les relances, la veille, les délais de collecte |
| `depose_par`, `saisie_par`, `validee_par` | l'audit : un acte est personnel, jamais usurpé |
| `reaffectations`, `verifications`, `tentatives` | les compteurs qui bornent les mécanismes |
| `empreinte_mot_de_passe` | ce qui n'entre jamais par une requête ordinaire |

⚠️ **La reconnaissance se fait par le nom, et c'est assumé.** Un champ du système
baptisé autrement lui échappera. Ce n'est pas une raison de ne rien contrôler :
le cas ordinaire est celui qu'on attrape, et c'est celui-là qui se produit.

Un dernier cas vérifie que **chaque nom surveillé existe réellement** dans le code,
par lecture de l'arbre syntaxique. Une liste de noms qui vieillit surveille des
fantômes ; un champ renommé fait tomber ce cas, et c'est le seul moment où
quelqu'un relira la liste.

### Quatre mutations

Dont la restauration exacte du défaut du pas 36 — la route reprend
`PieceJustificative` comme corps — et la neutralisation du balayage lui-même.
Toutes tuées.

### État à la fin du pas 37

**2 610 tests passent** (29 de plus), aucun sauté, lint propre. Aucune ligne de
code applicatif modifiée : ce pas ne fait que garder ce que le précédent a
corrigé.

**Ce que le projet sait faire qu'il ne savait pas.** Refuser, à la proposition
suivante, la route qui redonnerait au client la plume du système.

*Corriger un défaut sans chercher ses frères, c'est accepter de le retrouver.*

---

## Pas 38 — Le miroir : ce qui sort

Le pas 37 garde ce qu'un client peut **écrire**. Restait à garder ce qu'il peut
**lire**.

### Le défaut avait déjà existé, et le projet en porte la mémoire

`Compte.empreinte_mot_de_passe` est marqué `exclude=True`, avec ce commentaire :

> Le défaut a existé : la route publique de définition du mot de passe rendait le
> compte, **empreinte comprise**, à un appelant non authentifié. Une empreinte
> Argon2 livrée est de la matière à casser hors ligne, tranquillement, sans limite
> de tentatives et sans que rien ne l'enregistre.

Et la correction retenue mérite d'être répétée : *« l'exclusion est portée par le
champ, et non par chaque route : une exclusion à écrire route par route est une
exclusion qu'on oubliera à la prochaine. »*

**Rien à corriger, donc. Tout à garder.**

### Ce que le premier balayage a rendu, et pourquoi il fallait le refaire

Trente-trois réponses portaient « un champ sensible ». Trente-et-une étaient des
faux positifs sur `code` — qui désigne ici un code métier, un code de règle, un
code de journal. Une quatre-vingt-quatorzième partie de bruit.

⚠️ **Une liste de mots sensibles mal choisie ne produit pas un contrôle prudent :
elle produit un contrôle qu'on désactive.**

Le balayage refait sur les noms réels du projet en rend cinq, et le tri est plus
instructif que le compte :

| Champ | Porteur | Verdict |
| --- | --- | --- |
| `mot_de_passe` | `DemandeConnexion`, `DemandeDefinition` | ✅ **requête** : c'est ainsi qu'on se connecte |
| `secret` | `DemandeDefinition` | ✅ requête |
| `secret` | `Enrolement` | ✅ **rendu une fois**, à l'enrôlement, puis oublié |
| `cle_chiffrement` | `Configuration` | ✅ ne sort par aucune route |
| `empreinte_mot_de_passe`, `secret_totp` | `Compte` | ✅ `exclude=True` |

*Un modèle de requête n'est pas un modèle de réponse* : c'est la distinction qui
rend ce contrôle utilisable plutôt qu'insupportable.

### Un faux ami, et ce qu'il enseigne

`Verdict.jeton_fond` a été signalé. C'est un **jeton de couleur de fond**, pour
l'affichage d'un verdict de conformité.

⚠️ Un contrôle par le nom attrape ce qui s'appelle comme un secret, pas ce qui en
est un. C'est écrit dans le fichier plutôt que découvert par le prochain.

### Ce qui est gardé alors que rien ne le menace

`sceau` figure dans la liste surveillée bien qu'aucune réponse ne le porte.

Le lien d'acceptation est **signé, daté, à usage unique**, et il tient lieu de
preuve d'identité pour un client qui n'a pas de compte. Le rendre par une route
permettrait à n'importe quel collaborateur d'accepter une proforma **à la place du
client**. Le contrôle garde une propriété vraie aujourd'hui, pour qu'elle le reste.

### Mon propre garde a trouvé cinq fantômes dans ma propre liste

Le cas qui vérifie que chaque nom surveillé existe a échoué sur cinq des dix noms
que j'avais écrits : `password`, `motdepasse`, `cle_api`, `graine`,
`empreinte_jeton` ne désignaient rien.

La réponse n'est pas de les retirer. Ce sont précisément les noms qu'on emploie
sans réfléchir, en recopiant une bibliothèque anglophone ou la charge utile d'un
prestataire. Ils sont passés dans une seconde liste, **`NOMS_PROSCRITS`**, dont la
propriété gardée est l'**absence** :

> Le jour où un modèle porte un champ `password`, ce cas échoue — et c'est voulu.
> Le nom doit rejoindre `CHAMPS_SENSIBLES`, ce qui est un geste conscient, précédé
> d'une question : *ce champ doit-il vraiment exister, et sous ce nom-là ?*

⚠️ Les deux listes sont l'inverse l'une de l'autre, et les deux sont nécessaires :
**l'une garde ce qui existe, l'autre garde ce qui n'existe pas encore.**

### Ce qu'un essai n'aurait pas trouvé

Interroger les routes du jeu de démonstration ne montre aucune fuite : les comptes
de démonstration n'ont pas tous d'empreinte, et un champ vide ne fuit pas.

Il fuirait en production, sur des comptes réels. *Une fuite qui dépend des données
ne se trouve pas en essayant* : le contrôle porte donc sur les **modèles**.

### État à la fin du pas 38

**2 632 tests passent** (22 de plus), aucun sauté, lint propre. Aucune ligne de
code applicatif modifiée.

Quatre mutations, quatre tuées, dont la restauration du défaut historique : retirer
`exclude=True` de l'empreinte du mot de passe.

**Ce que le projet sait faire qu'il ne savait pas.** Refuser, à la proposition
suivante, le modèle qui laisserait sortir ce qui ne doit pas sortir — et poser une
question avant qu'un champ nommé `password` n'existe.

*Un contrôle de sécurité qui crie trente-et-une fois pour rien se désactive avant
d'avoir servi une fois.*

---

## Pas 39 — Le troisième volet : ce qu'un appelant peut faire

Le pas 37 garde ce qu'un client peut **écrire**, le pas 38 ce qu'il peut **lire**.
Restait le troisième : ce qu'il peut **faire**.

### Vingt-huit routes sur cent vingt-deux n'exigent aucune permission

Toutes vérifiées une par une, toutes légitimes. **Et c'est précisément pourquoi ce
pas existe** : une liste de vingt-huit exceptions toutes justifiées est une liste
où la vingt-neuvième passera inaperçue.

Elles se rangent en cinq familles, et chacune a sa raison en une phrase :

| Famille | Pourquoi aucune permission |
| --- | --- |
| **La vitrine** (4) | C'est un site. Il est public par destination. |
| **Le premier contact** (4) | Un visiteur n'a pas de compte, et c'est ce que ces routes existent pour changer. |
| **L'authentification** (7) | On ne peut pas exiger d'être connecté pour se connecter. |
| **Les liens signés** (5) | Le sceau ou la référence tient lieu de preuve, pour un client qui n'a pas de compte. |
| **Les appels de machines** (2) | Le prestataire et l'orchestrateur n'ont pas de session. |
| **Le référentiel normatif** (3) | Des taux qui viennent du Code général des impôts : les cacher ne protégerait rien. |
| **Les outils de recette** (2) | Fermés par le code, pas par un déploiement bien fait. |

⚠️ La liste est **close**. Une route nouvelle sans contrôle fait échouer le cas et
oblige à écrire son motif. *Écrire un motif est peu de travail ; ne pas pouvoir en
écrire un est l'information recherchée.*

Et un second cas retire de la liste ce qui n'y a plus sa place : une route depuis
gardée doit en sortir, sinon elle passe pour publique et plus personne ne vérifie.

### Une affirmation que rien ne tenait

Quatre routes sont publiques parce que, dit la docstring, *« la référence est
longue et non devinable »*.

Vérifié : `SO-b122bf55c8e640fa`, seize caractères hexadécimaux tirés d'un UUID4,
soit **64 bits d'aléa**. L'affirmation est vraie.

⚠️ **Rien ne la tenait.** Si `_reference` devenait un compteur — `SO-1`, `SO-2` —
ces quatre routes deviendraient l'**annuaire des clients du cabinet** : nom,
téléphone, courriel, NIU, montants. Aucun test ne l'aurait vu.

Le seuil retenu est de 48 bits, avec son motif : au-dessous, une énumération
devient concevable. Et la contre-épreuve est là — une constante de seize
caractères passerait le contrôle d'entropie sans peine.

*Une docstring qui justifie une route publique par une propriété du code doit
avoir un cas qui garde cette propriété.*

### Un motif trop court est un motif qu'on ne relit pas

Mon propre critère a mordu : plusieurs motifs disaient « Même raison. » ou
« Contenu du site public. » Illisibles seuls, donc inutiles au relecteur qui
arrivera dans six mois.

Le cas exige entre vingt et trois cent vingt caractères. La borne haute compte
autant que la basse : *une exception dont le motif tient à un paragraphe est une
exception qui n'en est pas une.* Les courtes se relisent ; les longues se croient
sur parole.

### Ce que le contrôle ne dit pas, écrit comme un cas

Il vérifie qu'une permission est **exigée**, jamais que c'est **la bonne**. Un
`LIRE_DOSSIER` là où il faudrait `VALIDER_ECRITURE` lui échappe.

C'est écrit dans un cas plutôt que dans un commentaire, pour qu'on ne prenne pas
ce fichier pour plus qu'il n'est.

### Deux outils de recette, fermés par le code

La boîte aux lettres de développement rend **404 hors mode démonstration** — « un
point d'entrée absent se cherche moins qu'un point d'entrée refusé ». La
simulation d'encaissement est refusée **dès qu'une clé de prestataire réelle est
configurée** : *« un encaissement réel ne se fabrique pas »*.

⚠️ Le second refus lit `fournisseur.simule` et non la configuration. Mon premier
cas patchait la clé et ne voyait rien : le comptoir est monté une fois, et régler
la clé après coup ne l'atteint pas. C'est le fournisseur qui porte la réponse,
donc c'est lui qu'il faut interroger — écrit dans le cas.

### Cinq mutations, cinq tuées

Dont la référence devenue compteur, la route qui perd son `exiger`, et la boîte de
recette qui s'ouvre en production.

### État à la fin du pas 39

**2 643 tests passent** (11 de plus), aucun sauté, lint propre. Aucune ligne de
code applicatif modifiée.

Le triptyque est complet : **ce qu'un client écrit, ce qu'il lit, ce qu'il fait.**

**Ce que le projet sait faire qu'il ne savait pas.** Exiger une phrase de celui qui
ouvrira la prochaine route au public.

*Vingt-huit exceptions justifiées se relisent. Vingt-neuf, dont une qui n'a jamais
été discutée, ne se relisent plus.*

---

## Pas 40 — Le document ne suivait plus le code

Demande du cabinet : *« j'espère que tu continues la mise à jour de notre artefact
au fur et à mesure, car cela doit être un recueil complet de ce projet de façon
exhaustive. »*

J'ai vérifié avant de répondre. **La réponse était non.**

### Ce que je mettais à jour, et ce que je ne mettais pas

À chaque pas, je republiais : l'en-tête, le nombre de pas, le nombre de tests, et
**une ligne dans le tableau de la section 17**.

Mesuré : sur douze mécanismes construits depuis le pas 26, **quatre n'avaient
aucune mention** dans le document — le profil d'échange, la proposition
d'écriture, le vocabulaire des motifs, et l'orchestrateur de conteneurs. Les huit
autres n'existaient qu'en une ligne de tableau.

⚠️ La substance de quatorze pas vivait **uniquement dans le journal**, un fichier
de quatre mille lignes que personne ne lit pour comprendre le système.

*Tenir un tableau de bord à jour n'est pas tenir un document à jour.* Le chiffre
en tête disait « 54 pas » et le corps en racontait quarante.

### Six sections écrites

| | Ce qu'elle porte |
| --- | --- |
| **42 · L'orchestration en marche** | Les cinq travaux, l'ordre par conséquence de panne, le verrou qui rend la mise à jour progressive sûre, et le filet qui n'était jamais jeté. |
| **43 · Le dossier qui dort** | La garde que rien ne déclenchait, les trois gestes et la règle qui les sépare, la reprise qui tournait entre deux personnes, le vocabulaire des motifs. |
| **44 · Le règlement, de bout en bout** | Les deux parcours qui ne se rejoignaient pas, la suite enfichable, le champ qui allait mentir, et l'argument qu'il a fallu réexaminer plutôt que contourner. |
| **45 · S'adapter au logiciel du client** | Le format comme donnée, les deux profils, les trois pièges dont deux ne se voient qu'après l'import, et la réserve assumée. |
| **46 · Les trois surfaces** | Ce qu'un client écrit, lit, fait. Le domaine qui écrivait la règle pendant que la route décidait. Les deux listes inverses. |
| **47 · Le déploiement en orchestrateur** | La sonde de vivacité qui ne teste jamais la base, les cinq décisions et leur piège, et ce que les manifestes ne font pas. |

Chacune porte ce que le journal contient de plus utile : **le défaut mesuré, le
chiffre compté, et la phrase qui empêche d'y retomber.**

### Ce que l'écriture a révélé sur le document lui-même

⚠️ **Les identifiants d'ancre ne suivent pas les numéros affichés.** `s20` est la
section 36, `s25` la section 37, `s21` la section 40. J'ai nommé mes sections
`s42` à `s47` en croyant ces identifiants libres : ils désignaient les sections 8
à 13.

Le document a porté pendant une republication **six ancres en double**. Le
sommaire y renvoyait, et un lecteur cliquant sur « 46 · Les trois surfaces »
serait tombé sur « 12 · Le parcours construit ».

Un contrôle a été ajouté à la vérification de republication : doublons d'ancre,
liens sans cible, sections orphelines du sommaire. *Une numérotation qui a divergé
une fois divergera encore, et rien dans le rendu ne la signale.*

### État à la fin du pas 40

**2 643 tests passent**, inchangés : aucun code n'a bougé. Le document compte
**51 sections**, 51 liens de sommaire, aucun doublon, zéro tiret quadratin,
471 Ko.

**Ce que le projet sait faire qu'il ne savait pas.** Se raconter en entier, et pas
seulement se compter.

*Un document qui affiche le bon nombre de pas et n'en raconte que les trois quarts
est plus trompeur qu'un document périmé : le chiffre y fait foi.*

---

## Pas 41 — La recette de la vague 2 : du justificatif à la déclaration

### Ce qui manquait

Le dossier de conception énonce le « fini quand » de la vague 2 en une phrase :
*un adhérent dépose ses justificatifs, ils sont contrôlés, imputés, et la
déclaration se prépare.*

Cette phrase traverse **quatre contextes bornés** : B · Collecte pour le dépôt,
D · Conformité pour le contrôle, C · Comptabilité pour l'imputation,
F · Obligations pour la déclaration. Chacun possédait ses cas, et ils passaient.
**Aucun ne vérifiait la phrase.**

C'est exactement l'état dans lequel se trouvait le parcours d'acquisition avant sa
propre recette, au chantier 3. Celle-là avait trouvé quatre défauts de câblage que
cent fichiers de domaine ne pouvaient pas atteindre : une politique de
cloisonnement qui ne s'appliquait à personne, un gabarit de courriel réclamé sous
un nom absent, un tenant payé dont la table restait vide, une qualification jetée
par sa propre route.

*Un cas de domaine mesure une règle. Il ne mesure jamais si quelqu'un l'appelle.*

### Ce qui a été écrit

`tests/test_recette_de_la_production.py`, sur PostgreSQL réel, par HTTP, avec les
comptes du jeu de démonstration : l'adhérent `jp.nkoa@batimentplus.cm` et le
comptable `a.bouba@cga-brcg.cm`, sur le dossier `M081234567890P`.

**Un seul cas pour la chaîne, et c'est délibéré.** La découper en huit cas
indépendants demanderait de reconstruire l'état à chaque fois, donc de le
fabriquer, donc de ne plus éprouver le câblage. Ce qui est vérifié ici est
précisément ce qui relie les étapes.

| Étape | Ce qui est prouvé |
| --- | --- |
| 1 | L'adhérent dépose un PDF, le magasin le reçoit sous son empreinte |
| 2 | La déclaration est lue **avant** toute écriture : point de départ |
| 3 | Le comptable contrôle une facture, le moteur propose une écriture |
| 4 | L'écriture est saisie **telle que proposée**, elle naît brouillon |
| 4 bis | La déclaration **n'a pas bougé** : un brouillon n'engage personne |
| 5 | La validation la rend immuable, et nomme son auteur |
| 6 | La balance la porte, et elle est équilibrée |
| 7 | La déclaration a bougé **de son montant exact de TVA** |
| 7 bis | Une TVA refusée par la conformité ressort en TVA rejetée |
| 8 | Le fichier part au format Sage Ligne 100, en cp1252 |

Et quatre contre-épreuves : une facture bloquante ne produit aucune écriture, un
brouillon ne part pas chez le client, l'adhérent ne lit pas la comptabilité, un
adhérent ne dépose pas sur le dossier d'un autre.

### Les cinq passages au vert qui ne prouvaient rien

Les cinq cas sont passés **du premier coup**. C'est le signal que quelque chose ne
mesure pas, et trois défauts se cachaient derrière.

**Premier : l'assertion de présence.** Le cas vérifiait que la déclaration n'était
pas vide. Or le jeu de démonstration en remplit déjà une. L'assertion passait
même si l'écriture qu'on venait de valider n'y figurait pas. Remplacée par un
écart : la déclaration est lue avant, relue après, et la différence doit valoir
exactement la TVA de l'écriture.

*Une somme non vide ne dit pas qui l'a remplie. Seul l'écart désigne un terme.*

**Deuxième : l'écart ne distinguait pas le brouillon.** La mutation qui supprime
le filtre `etat is VALIDEE` de la déclaration **survivait**. Logique : la lecture
d'avant se faisait avant toute saisie, donc l'écriture manquait des deux côtés du
filtre, et compter les brouillons ne changeait rien à l'écart mesuré.

L'enjeu n'est pas théorique. Une écriture brouillon peut être corrigée, reprise,
supprimée. Si la déclaration la comptait, le cabinet déclarerait de la TVA sur un
travail que son comptable n'a pas terminé, et corriger après dépôt se paie en
pénalités.

Une **troisième lecture** a été insérée, entre la saisie et la validation : elle
doit être rigoureusement égale à celle d'avant. La mutation meurt.

*Pour mesurer un filtre, il faut se placer des deux côtés du filtre.*

**Troisième : le rejet fiscal n'était pas mesuré.** La mutation qui annule
`rejetee += ligne.montant` survivait aussi, faute d'assertion sur ce champ.

C'est pourtant **le maillon qui fait le métier d'un centre de gestion agréé.**
Une facture réglée en espèces au-delà du plafond reste comptabilisable, la charge
est bien engagée. Mais sa TVA n'est pas récupérable. Ce refus naît dans le
contexte D, se pose sur la ligne comme attribut fiscal dans le contexte C, et doit
ressortir dans le contexte F à la ligne « TVA rejetée ». Trois contextes, trois
équipes possibles, un seul chiffre. Si l'un des trois se tait, la déclaration
réclame à l'État une TVA que le contrôle fiscal refusera, et le cabinet répond de
ce chiffre-là.

L'étape 7 bis a été ajoutée. La facture `F-2026-0412` du jeu de démonstration a été
retenue parce qu'elle porte exactement ce cas : TVA refusée, charge admise,
opération comptabilisable. Le cas mesure trois choses :

* la TVA rejetée augmente **du montant exact** de la ligne 445 de cette écriture ;
* la TVA déductible **admise** ne bouge pas, car rejetée veut dire retirée ;
* le motif voyage avec le chiffre, car un rejet sans motif est indéfendable
  devant le vérificateur.

*Un rejet affiché mais pas appliqué est pire que pas de rejet du tout : il donne
au cabinet la certitude d'avoir contrôlé.*

### Les douze mutations

| Le maillon cassé | Verdict |
| --- | --- |
| La pièce déposée n'est pas enregistrée | tuée |
| L'auteur du dépôt n'est plus la session | tuée |
| La proposition ignore le verdict de conformité | tuée |
| L'écriture validée n'entre pas en balance | tuée |
| L'export laisse sortir les brouillons | tuée |
| La permission ne s'exige plus sur un dossier | tuée |
| Le périmètre du portefeuille ne se vérifie plus | tuée |
| La déclaration compte aussi les brouillons | tuée |
| La TVA déductible ne s'additionne pas | tuée |
| D : le moteur ne refuse plus la TVA réglée en espèces | tuée |
| C : l'attribut fiscal ne se pose pas sur la ligne | tuée |
| F : la TVA rejetée n'est plus retirée de l'admise | tuée |
| F : le motif du rejet ne remonte pas | tuée |

Douze pour douze, après avoir renforcé les trois assertions creuses.

### Ce que mon propre outil a cassé

Le script de mutation sauvegarde le fichier, le modifie, lance les cas, puis le
restaure. Appliqué à un chemin **qui n'existait pas**, le `cp` de sauvegarde
échoue en silence, et la restauration écrit alors l'ancienne sauvegarde à ce
chemin neuf.

C'est ainsi qu'est apparu
`app/contextes/obligations/adaptateurs/sortant/lecture_des_ecritures.py`,
copie conforme de `dependances.py` du contexte transverse, posée là par erreur.

**Le test d'architecture l'a vu.** Le fichier importait
`transverse.adaptateurs.sortant.depots_memoire`, un module interne, depuis le
contexte obligations. Sans cette garde, un fichier mort de 600 lignes serait
resté dans l'arbre, et le premier junior à l'ouvrir aurait cru y lire quelque
chose de vrai.

*Un outil qui restaure sans vérifier que la cible existait fabrique du code
plutôt que d'en rendre.* Le script exige désormais que le fichier existe avant de
commencer.

C'est la troisième fois que le test d'architecture arrête quelque chose que je
n'avais pas vu, et la première fois qu'il arrête une chose que je n'avais pas
voulue.

### État à la fin du pas 41

**2 648 tests passent** sur PostgreSQL réel, en 2 min 39 s. `ruff` propre.

**Ce que le projet sait faire qu'il ne savait pas.** Prouver sa promesse, et pas
seulement ses règles. La vague 2 a désormais sa recette, comme le parcours
d'acquisition a la sienne.

**Ce qui reste ouvert.** Le sens import du moteur d'échange, de Sage vers nous.
La spécification du fichier DIPE, qui bloque la paie. Le barème d'honoraires.

*Une promesse qu'aucun cas ne relit n'est pas une promesse, c'est une intention.*

---

## Pas 42 — La reprise : relire ce que le logiciel du client nous envoie

### Ce qui manquait, et ce que cela coûtait

Le pas 35 avait construit le moteur d'échange dans **un seul sens** : écrire un
fichier au format du logiciel de l'adhérent. Sage Ligne 100, un pivot CSV, et un
profil YAML pour en brancher un de plus sans déploiement.

Le sens retour manquait, et ce n'est pas un détail de confort. **Un adhérent
n'arrive jamais vierge.** Il arrive avec dix mois d'écritures chez son ancien
comptable, et la première chose que le centre doit savoir faire est de les
reprendre. Sans cela, la plateforme ne se vend qu'à des entreprises qui se créent,
c'est-à-dire presque à personne.

### L'asymétrie, qui tient tout le module

⚠️ **L'import n'est pas le miroir de l'export, et le croire coûte cher.**

À l'export, les données sont les nôtres. Le pivot les garantit, l'équilibre est
tenu par l'entité, les comptes viennent du plan. Il ne reste qu'à mettre en forme,
et la seule question est de savoir ce que le destinataire accepte.

À l'import, **rien n'est garanti**. Le fichier vient d'un système que nous n'avons
pas écrit, exporté par quelqu'un que nous ne connaissons pas, souvent repris à la
main dans un tableur entre les deux.

Trois règles en découlent, et chacune a son cas.

**1 · Rien n'entre à moitié.** Un lot partiellement importé est un grand livre
déséquilibré, et personne ne sait de combien. Le refus porte sur le lot entier,
qu'une seule ligne soit en cause ou quatre cents.

**2 · Toutes les anomalies d'un coup.** Un fichier de reprise fait quatre mille
lignes et se corrige une fois. Rendre la première erreur seule condamne
l'exploitant à quarante allers-retours ; il abandonnera avant, et saisira à la
main.

**3 · Ce qui entre est un brouillon.** Une écriture venue d'ailleurs n'a été
validée par personne au centre. La faire entrer validée ferait engager la
responsabilité du cabinet sur le travail d'un autre, sans qu'aucun collaborateur
ne l'ait lue.

La symétrie se retient en une phrase : **on n'exporte que du validé, on n'importe
que du brouillon.**

### Le piège qui ne se signale pas

Un fichier `cp1252` lu en `utf-8` casse sur le premier accent. C'est le bon cas :
l'erreur est franche, immédiate, et le message dit quel encodage était attendu.

L'autre sens ne casse **jamais**. Presque tout octet a un sens en `cp1252`, donc
un fichier UTF-8 s'y décode sans la moindre erreur et rend un texte parfaitement
valide et parfaitement faux. Le client importe, et découvre « SociÃ©tÃ© » dans
chaque libellé de son grand livre. Définitivement : une fois entrés, les libellés
abîmés ne se rattrapent plus.

Le lecteur cherche donc les traces du charabia et **refuse** plutôt que d'accepter.
Le cas porte sa contre-épreuve : il vérifie d'abord que `cp1252` accepte bien ces
octets, sans quoi le piège aurait disparu et le cas ne mesurerait plus rien.

### Quatre décisions qui n'allaient pas de soi

**Le numéro du fichier ne devient jamais le nôtre.** Le reprendre tel quel serait
naturel et serait une faute : *« la continuité de la séquence est une propriété du
registre entier, jamais d'une écriture isolée »*. Deux reprises sur le même journal
se marcheraient dessus. C'est le registre qui numérote, et le numéro d'origine part
en référence externe — sans quoi le comptable perd tout point commun entre les deux
systèmes, et ne retrouve plus la pièce au classeur de l'adhérent.

**Le mode contrôle est le défaut.** Reprendre un exercice est irréversible en
pratique : les écritures entrent en brouillon, donc elles se suppriment, mais
personne ne supprime quatre mille brouillons à la main. Le rapport de contrôle a
**exactement la même forme** que celui de l'application ; deux formes différentes
obligeraient l'exploitant à comparer, et il ne le ferait pas.

**La reprise passe par la même porte que la saisie.** Écrire dans le dépôt
directement serait plus court, et serait le moyen sûr de faire entrer par l'import
ce que la saisie refuse. *Une porte dérobée n'est pas une porte dérobée parce qu'on
la cache : c'est une porte dérobée parce qu'elle n'a pas la même serrure.*

**On contrôle tout, puis on écrit tout.** Enregistrer une à une et s'arrêter à la
trois centième laisserait deux cent quatre-vingt-dix-neuf écritures en base. Les
trois contrôles d'environnement ont donc été extraits en une fonction publique,
appelable sans rien écrire. Les recopier dans la reprise aurait produit le défaut
qui se paie le plus cher ici : deux contrôles qui divergent, celui de l'import
devenant plus laxiste que celui de la saisie.

### Le premier aller-retour, et ce qu'il a trouvé tout de suite

Le seul cas qui compte vraiment : **ce que nous écrivons, savons-nous le relire ?**
Paramétré sur les profils réels du référentiel, jamais sur un profil forgé.

Il a échoué au premier essai. Le profil Sage ne porte **pas** de libellé
d'écriture, seulement un libellé de ligne. Je m'en servais comme repli pour nommer
l'écriture, puis je comparais ce repli aux lignes suivantes pour détecter deux
écritures sous un même numéro. Résultat : chaque ligne d'une même écriture était
déclarée en conflit avec la première.

*Un repli est légitime pour nommer, jamais pour contrôler.* Comparer un repli à un
autre repli fait conclure à un conflit que le fichier ne dit pas.

### Ce que les mutations ont appris

**Vingt mutations, vingt tuées** après deux corrections de fond.

**Première : je rejouais une règle du pivot dans le module qui déclare ne pas les
rejouer.** La mutation « un montant nul passe » survivait. En regardant pourquoi :
le pivot refuse déjà le montant nul ou négatif, **dans les mêmes mots** — « le
montant d'une ligne est strictement positif : c'est le sens qui porte la direction,
jamais le signe ». Mon contrôle était un doublon exact.

Le module a été allégé, pas le cas renforcé. *Deux contrôles qui disent la même
chose divergent au premier correctif, et c'est alors le plus laxiste des deux qui
fait loi sans que personne ne s'en aperçoive.*

En contrepartie, une discipline a été posée : **toute règle du pivot doit ressortir
en anomalie nommée, jamais en trace de validation.** C'est ici, et uniquement ici,
que des données étrangères rencontrent le domaine. Un exploitant comptable à qui
l'on montre `string_pattern_mismatch` conclut que l'outil est cassé, pas son
fichier.

**Deuxième : la reprise citait un rang d'écriture dans un champ documenté comme un
rang de fichier.** La mutation qui remplace le rang par l'indice survivait, faute
d'assertion. Le champ `ligne` d'une anomalie dit « le numéro dans le fichier, en
comptant l'en-tête, parce que c'est ce que montre le tableur de l'exploitant ». La
reprise y mettait l'indice de l'écriture dans le lot.

L'écart n'est visible que sur la seconde écriture : ligne 4 du fichier, indice 2.
Le lot lu porte désormais le rang de départ de chaque écriture, et le cas l'exige.

**Troisième, la plus instructive : le contrôle d'environnement n'avait aucun cas à
lui.** Le supprimer entièrement ne cassait rien, parce que mon cas de compte
inconnu était attrapé plus tôt par le lecteur, à qui la route passe le plan.

Il fallait donc ce que le lecteur **ne peut pas** voir : un journal que le cabinet
n'a pas, et une date hors des bornes de l'exercice. Rien dans un fichier ne dit
qu'un journal existe. Sans ce cas, l'import serait devenu la porte dérobée qu'il
prétend ne pas être.

### La troisième copie est celle qui dit qu'il faut partager

La fixture qui monte l'application sur PostgreSQL amorcée existait **deux fois**,
dans les deux recettes, et une troisième allait naître pour ce fichier. Elle est
remontée au `conftest`, sous deux noms : `plateforme_amorcee` pour qui veut
l'enrichir, `plateforme` pour qui n'a rien à y ajouter.

⚠️ Les deux noms ne sont pas une coquetterie : un fichier de cas qui veut enrichir
la fixture ne peut pas le faire sous le même nom, il se demanderait lui-même. La
recette du parcours redéfinit donc `plateforme` en s'appuyant sur l'autre.

*Trois exemplaires d'un amorçage divergent au premier correctif, et les cas qui en
dépendent commencent alors à mesurer des mondes différents sans que rien ne le
dise.*

### État à la fin du pas 42

**2 692 tests passent** sur PostgreSQL réel, en 6 min 54 s. `ruff` propre sur le
dépôt entier.

Le fichier de reprise compte 44 cas, dont **36 tournent sans base de données** :
seule la classe qui éprouve la route est marquée. Marquer le fichier entier ferait
taire l'essentiel du sens sur une machine sans PostgreSQL.

**Ce que le projet sait faire qu'il ne savait pas.** Reprendre le passé d'un
adhérent, et pas seulement produire son présent. Le moteur d'échange a désormais
ses deux sens, avec **un seul profil pour les deux** : ce qu'un logiciel sait
recevoir, il sait le renvoyer.

**Ce qui reste ouvert.** Le barème d'honoraires, toujours le manque le plus proche.
La spécification du fichier DIPE, qui bloque la paie. Les modèles d'états
financiers.

*Ce qu'un profil ne sait pas écrire, il ne sait pas le relire, et c'est une bonne
contrainte : elle interdit aux deux sens de diverger.*

---

## Pas 43 — La clôture d'exercice, et le défaut que sa construction a révélé

### Ce qui manquait

Sans clôture, la plateforme ne survit pas à sa deuxième année.

Le contexte savait **lire** un exercice terminé : la liasse fiscale s'assemble, le
tableau de passage se calcule, la balance boucle. Il ne savait pas le **fermer**.
L'entité `Exercice` portait un attribut `clos` depuis le premier jour, et rien
dans le produit ne le posait jamais.

La permission `CLOTURER_EXERCICE` existait aussi depuis le début : nommée dans
`EXIGE_MOTIF`, attribuée au réviseur et à la direction, **et citée dans la
documentation des routes de clôture qui expliquait pourquoi elle n'était pas
exposée.** Aucune route ne l'appelait. C'est la troisième capacité sans appelant
trouvée dans ce projet, après `classer_sans_suite` et `reconcilier`.

Et fermer ne suffit pas. Un exercice fermé dont les soldes ne passent pas au
suivant laisse une entreprise qui recommence chaque janvier avec une caisse vide,
aucun fournisseur à payer et un capital disparu.

### La règle, en deux lignes

| Classes | Nature | Traitement |
| --- | --- | --- |
| 1 à 5 | comptes de **situation** | reportés, solde pour solde |
| 6 à 8 | comptes de **gestion** | remis à zéro, jamais reportés |

Une charge de transport payée en 2026 ne pèse pas sur 2027 : elle a joué son rôle,
elle a formé le résultat, et c'est **le résultat** qui passe, pas la charge.
Reporter un compte de gestion doublerait les charges de l'exercice suivant, d'un
montant que personne ne saurait retrouver, puisque rien ne distinguerait alors la
charge reportée de la charge réelle.

**Le bouclage n'est pas une vérification annexe : c'est la preuve.** Le contrôle
qui existait déjà dit que la somme des comptes de situation, en débit moins
crédit, vaut exactement le résultat. Formulé autrement : *l'écriture d'à-nouveau
s'équilibre par construction*, dès lors que la balance de départ est équilibrée.
C'est la raison pour laquelle l'opération est possible, et un bouclage qui échoue
signale que la balance est fausse, pas que l'à-nouveau l'est.

### Ce qui a été tranché, et ce qui a été laissé ouvert

**Tranché : le journal des à-nouveaux est séparé.** Ce n'est pas du rangement.
L'écriture de reprise n'est pas une opération de l'entreprise : aucune facture,
aucun règlement, aucun tiers ne lui correspond. La mêler aux opérations diverses
la rendrait indiscernable d'une régularisation saisie à la main, alors qu'un
vérificateur la cherche en premier. Séparée, elle se lit d'un coup d'œil : un
journal des à-nouveaux porte **une** écriture par exercice, et toute autre chose y
est suspecte.

**Tranché : la clôture ouvre l'exercice suivant.** L'entité garantissait déjà que
les exercices se suivent sans trou ni chevauchement, donc la date d'ouverture du
suivant n'est pas un choix. Exiger que l'exploitant l'ouvre à part créerait le
pire état possible : un exercice fermé sans successeur, dans lequel plus rien ne
se saisit et dont les soldes ne sont allés nulle part. Seule la **fin** du suivant
reste un choix, et elle est rare.

⚠️ Et découvert au passage : **le portefeuille est entièrement en lecture seule.**
Aucune route n'y crée quoi que ce soit. Sans cette décision, la clôture aurait
buté à chaque fois sur un exercice suivant inexistant, sans aucun moyen de le
créer.

**Tranché : l'à-nouveau est validé, et par celui qui clôt.** Toute autre écriture
naît en brouillon pour que le comptable la relise. Celle-ci n'est pas saisie : elle
est calculée à partir d'écritures déjà validées. La laisser en brouillon aurait une
conséquence absurde et précise : l'exercice suivant s'ouvrirait sur une balance
vide, puisque la balance ne compte que le validé.

**Laissé ouvert : l'affectation du résultat.** Le résultat est porté au compte
`13 Résultat net de l'exercice`, et il y reste. Le répartir entre réserves, report
à nouveau et dividendes est une décision de l'assemblée des associés, prise après
la clôture, parfois des mois après, et qui peut ne jamais être prise. *Un logiciel
qui virerait d'office le résultat en report à nouveau écrirait dans les comptes une
décision que personne n'a votée.*

### Une documentation qui confondait deux actes

Le module de clôture disait que la clôture « suppose l'archivage de l'accusé de
dépôt ». C'était tenir pour un seul acte ce qui en fait deux, et dans le mauvais
ordre : la liasse se fabrique **à partir** des comptes arrêtés, donc le dépôt est
postérieur. Attendre l'accusé pour reporter les soldes laisserait l'entreprise
travailler de janvier à mai sans caisse d'ouverture. Aucun cabinet ne procède
ainsi.

### Le défaut que la construction a révélé

L'à-nouveau a échoué à sa première écriture : *une écriture validée porte sa pièce
justificative.* Le message était juste, mais **l'erreur venait de la relecture
depuis PostgreSQL**, pas de la validation. L'écriture invalide avait été écrite.

Trois lignes suffisent à montrer pourquoi :

```python
validee = brouillon.model_copy(update={"etat": VALIDEE})
validee.etat                 # VALIDEE
validee.piece_justificative  # None
```

⚠️ **`model_copy` ne rejoue aucun validateur.** C'est écrit dans la documentation
de pydantic, et c'est même son intérêt : la copie est rapide parce qu'elle ne
vérifie rien. Le contrat est donc l'inverse de celui qu'on lui prête en le lisant
dans du code métier, où il ressemble à un constructeur.

**Le défaut atteignait une route réelle**, et la plus ordinaire qui soit : la
pièce justificative est facultative à la saisie, parce qu'un comptable impute
souvent avant que la pièce ne lui parvienne. La validation ne la réclamait pas. Un
dossier entier pouvait donc être validé sans aucune pièce, et l'anomalie ne se
serait vue qu'à la relecture, des jours plus tard, dans une pile d'appel muette.

⚠️ **Et en persistance mémoire, l'objet n'est jamais reconstruit : l'invariant
n'existait tout simplement pas.** Les cas passaient, la démonstration passait.

### La classe, pas l'instance

Un balayage a mesuré l'exposition : **93 appels à `model_copy(update=…)`** dans
36 fichiers, dont **15 dans 8 classes qui portent un invariant de cohérence**.

Huit, c'est réparable en entier. `app/partage/copie.py` porte désormais
`transiter`, qui relit les champs depuis l'instance et revalide le modèle complet.
Les quinze appels ont été convertis, et un contrôle garde la conversion : aucune
classe à validateur `after` ne peut se recopier sans revalider.

⚠️ `transiter` lève aussi sur un **champ inconnu**. `model_copy` accepte
`update={"etat_": …}` et rend une copie inchangée : une faute de frappe sur un nom
de champ produit une transition qui ne transite pas, et rien ne le signale.

Un cas garde le piège lui-même dans le temps : il vérifie que `model_copy` laisse
toujours passer. Il n'éprouve pas notre code, il éprouve pydantic, et il existe
pour que personne ne conclue un jour qu'on peut revenir en arrière.

### Les vingt-six mutations

Quatre survivantes, et chacune a enseigné quelque chose.

**Une écriture morte.** Supprimer l'enregistrement de l'exercice neuf ne cassait
rien : la seconde écriture, en fin de geste, portait déjà les deux changements.
Le commentaire qui la justifiait — « l'ouverture précède l'à-nouveau, sinon
l'écriture serait refusée » — était faux : l'objet est passé directement, jamais
relu. L'ordre retenu est meilleur que celui que je défendais : **si l'à-nouveau
échoue, rien n'a été écrit**, au lieu d'un exercice neuf sans report.

**Un contrôle sans cas.** Clore 2026 avant 2025 n'était arrêté par rien de mesuré,
parce que le jeu de démonstration ferme tous ses exercices antérieurs. Rien dans le
produit n'oblige pourtant à clore dans l'ordre.

**Une affirmation que rien ne tenait.** Chercher l'exercice suivant par libellé
plutôt que par date survivait, et pour cause : aucun jeu de libellés du projet ne
met les deux méthodes en désaccord. Le libellé est pourtant une **étiquette** —
`Exercice.libelle` est une chaîne libre, et un dossier repris arrive avec « EX01 ».
Le contrat est désormais fixé par un cas aux libellés délibérément artificiels, et
le cas dit qu'il l'est.

**Un balayage qui ne balayait plus.** Supprimer la boucle du contrôle de classe ne
faisait échouer aucun cas : un contrôle qui ne trouve rien peut avoir raison, ou
n'avoir rien regardé. Il exige maintenant d'avoir vu au moins vingt classes à
invariant, et nommément `EcritureComptable`, `PieceJustificative`, `Habilitation`.

### État à la fin du pas 43

**2 728 tests passent** sur PostgreSQL réel, en 2 min 59 s. `ruff` propre.

**Ce que le projet sait faire qu'il ne savait pas.** Passer une année. Arrêter les
comptes, reporter les soldes, ouvrir l'exercice suivant, et refuser de le faire
tant que quelque chose cloche — en disant tout ce qui cloche d'un coup.

**Ce qui reste ouvert.** L'affectation du résultat, qui appartient à l'assemblée.
Le barème d'honoraires. La spécification du fichier DIPE. Les modèles d'états
financiers. Et le portefeuille, qui reste en lecture seule partout ailleurs.

*Une entité qui change d'état ne se recopie pas : elle transite, et une transition
qui mène à un état interdit doit être refusée.*

---

## Pas 44 — Voir venir le seuil, plutôt que le constater

### Le scénario, écrit dans le code depuis le premier jour

Le domaine du portefeuille porte `diagnostiquer_seuil`, avec une docstring qui dit
exactement ce qu'il faut en faire :

> *Une entreprise passe au régime du réel en septembre. Son comptable, qui suit le
> dossier de loin, continue de facturer sans TVA jusqu'en décembre. Au contrôle,
> l'administration considère le prix perçu comme un montant toutes taxes comprises
> et en extrait la taxe : l'entreprise doit alors une TVA qu'elle n'a jamais
> encaissée, majorée des pénalités.*
>
> *Le rôle du logiciel n'est pas de constater le franchissement après coup — c'est
> de l'annoncer avant.*

**Personne ne l'appelait.** La fonction attend un chiffre d'affaires en argument,
et aucun code n'en calculait un. C'est la quatrième capacité sans appelant trouvée
dans ce projet, après `classer_sans_suite`, `reconcilier` et `CLOTURER_EXERCICE`.

Un balayage a compté le reste : **treize exports du portefeuille n'avaient aucun
appelant hors de leur propre contexte.**

### Pourquoi chez les Obligations, et pas au portefeuille

Le portefeuille ne dépend d'aucun contexte, et c'est voulu : il porte l'histoire
juridique des dossiers, qui ne doit rien à la comptabilité. Or le chiffre
d'affaires vient des livres.

Le contexte F · Obligations voit les deux, et c'est sa raison d'être : **le seuil
commande ce que l'entreprise doit.** Le franchir ne change pas le dossier, il
change les obligations — assujettissement à la TVA, périodicité des déclarations,
tenue d'une comptabilité complète.

### Le chiffre d'affaires n'est pas la classe 7

La classe 7 porte tous les produits, y compris les intérêts de prêts reçus et les
transferts de charges. Les compter gonflerait le chiffre d'affaires d'une
entreprise qui place sa trésorerie ou refacture des frais.

La conséquence est précise et coûteuse : c'est ce chiffre qui se compare au seuil.
Un chiffre gonflé déclenche un reclassement au réel que l'entreprise **ne doit
pas**, lui fait prendre un numéro de TVA, facturer avec taxe, et déposer des
déclarations dont elle n'était pas redevable. Le compte 70 seul, donc.

Et la somme est `crédit − débit`, jamais le seul crédit : **les avoirs diminuent le
chiffre d'affaires.** Une entreprise qui annule la moitié de ses ventes verrait
sinon un chiffre brut qui n'existe nulle part.

### Deux mesures, deux sens, et les confondre coûte cher

| Ce qu'on mesure | Ce que c'est | Ce qu'on en fait |
| --- | --- | --- |
| L'exercice **clos** | un **fait** : le chiffre est définitif | le reclassement est dû |
| L'exercice **en cours** | une **veille** : le chiffre est partiel | il est encore temps d'agir |

Ne regarder que l'exercice clos revient à constater après coup, c'est-à-dire à
faire précisément ce que le domaine dit de ne pas faire. Ne regarder que
l'exercice en cours ferait manquer un franchissement acquis.

⚠️ **Clos, et non pas simplement terminé.** Un exercice dont la date de clôture est
passée mais que le cabinet n'a pas arrêté porte encore des écritures à venir : le
présenter comme un fait ferait réclamer un reclassement sur un chiffre qui va
bouger. Le pas 43 venait de donner au produit le moyen de clore ; celui-ci s'en
sert.

### Ce module n'extrapole pas, et c'est une décision

Un chiffre d'affaires à 60 % du seuil à mi-exercice « annonce » 120 % en fin
d'année, et il serait tentant de le dire. Ce serait inventer un nombre.

Une entreprise saisonnière rend l'extrapolation linéaire fausse : une école
réalise son chiffre en septembre, un négociant de matériaux en saison sèche. Le
rapport porte donc le chiffre réel **et la part de l'exercice écoulée**, pour que
celui qui lit juge lui-même.

*Un logiciel qui extrapole sans le dire fait prendre une projection pour un fait.*

### Le régime se lit à la date d'observation

C'est la subtilité la plus fine du module, et une mutation a montré que rien ne la
tenait.

L'écart ne se voit que dans une fenêtre précise : un exercice clos franchi, et un
reclassement inscrit **après** cette clôture. C'est exactement la situation d'un
cabinet qui fait son travail : il a vu le franchissement et l'a régularisé au
1er janvier.

Lire le régime à la clôture de l'exercice mesuré maintiendrait l'alerte **pour
toujours** sur un dossier régularisé. *Le collaborateur apprendrait à l'ignorer, et
il ignorerait aussi la vraie.*

Aucun dossier de démonstration ne change de régime dans cette fenêtre. Le cas le
fabrique, et c'est la seule façon de mesurer la règle.

### La surveillance est une lecture, pas une alerte poussée

Le réflexe aurait été un travail périodique déposant des alertes. Trois raisons de
ne pas le faire, et elles sont écrites plutôt que subies.

**La boîte d'envoi ne déduplique pas.** `deposer` réécrit la ligne et remet
`publie_le` à zéro : un dépôt à chaque passage réalerterait indéfiniment.

**Marquer le dossier demanderait d'écrire dans le portefeuille**, dont l'entité est
une histoire juridique et non un plan de travail.

**Et *à qui* l'alerte est remise, par quel canal, à quelle heure** sont trois choix
qui appartiennent au cabinet. C'est le raisonnement déjà consigné pour
`DossierEnSouffrance` au pas 29.

La revue du portefeuille est donc une route, **triée par urgence décroissante**, et
filtrée par défaut sur ce qui demande un regard. *Une revue qui rend cent dossiers
dont trois méritent un regard se lit une fois, puis plus jamais.*

⚠️ Le tri place le **fait** avant la **prévision**, quel que soit le taux. Un
dossier à 120 % sur son exercice en cours est plus « avancé » qu'un dossier franchi
à 101 % l'an dernier ; il est pourtant moins urgent, puisque le second est déjà en
infraction.

### Trois défauts trouvés en construisant

**Aucun dossier de démonstration n'a le moindre chiffre d'affaires.** Le constater
a évité d'écrire une recette qui aurait comparé deux zéros en paraissant mesurer
quelque chose. Les cas HTTP fabriquent donc la vente par les routes réelles,
saisie puis validation, ce qui éprouve la chaîne au passage.

**Une assertion vraie sur une liste vide.** Un cas affirmait que tous les dossiers
rendus par la revue filtrée étaient à surveiller, et il passait — parce que la
liste était vide. `all()` sur rien vaut vrai.

**Les conclusions ne sortaient pas en JSON.** `reclassement_du` et `a_surveiller`
étaient des propriétés ordinaires, donc absentes de la réponse : l'écran aurait
reçu le diagnostic sans la conclusion, et aurait dû refaire le raisonnement chez
lui. *C'est-à-dire l'écrire une seconde fois, et le voir diverger au premier
correctif.*

### Une aide qu'on ne pouvait pas employer

`statut_initial` existe depuis le premier jour, et sa docstring nomme son site
d'appel : *« pour que le contexte I, quand il convertira un dossier de création en
adhérent, n'ait pas à connaître la mécanique des périodes »*.

Le contexte I montait son `StatutRegime` à la main. Non par négligence : il avait
besoin de dire de quel dossier de création le régime venait, et la fonction
n'acceptait pas de précision.

*Une aide qu'on ne peut pas employer n'aide personne, et elle est pire qu'une
absence d'aide : elle laisse croire que le motif `CREATION` est posé en un seul
endroit alors qu'il l'est en deux.*

### Les treize mutations

Deux survivantes, toutes deux du même genre : **le cas existait, mais pas dans la
fenêtre où la règle change quelque chose.**

La lecture du régime à la date d'observation survivait, parce que tous les
dossiers de démonstration avaient changé de régime des années avant l'exercice
mesuré. La portée du portefeuille survivait, parce que les cas HTTP employaient le
réviseur, qui voit tout le cabinet — il fallait un comptable au portefeuille
restreint.

*Un garde ne se mesure que là où il change quelque chose, et c'est rarement là où
le jeu de démonstration nous place.*

### État à la fin du pas 44

**2 747 tests passent** sur PostgreSQL réel, en 3 min 55 s. `ruff` propre.

**Ce que le projet sait faire qu'il ne savait pas.** Dire à un adhérent qu'il
approche du seuil avant qu'il ne le franchisse, sur le chiffre de ses livres et non
sur celui qu'il croit réaliser. C'est le service pour lequel un centre de gestion
agréé existe.

**Ce qui reste ouvert.** Inscrire le changement de régime : le portefeuille demeure
en lecture seule, et le reclassement doit encore se poser à la main en base. Le
barème d'honoraires. Le fichier DIPE. Les modèles d'états financiers.

*Une capacité sans appelant n'est pas une fonctionnalité en attente : c'est une
promesse que le code fait et que le produit ne tient pas.*

---

## Pas 45 — Inscrire le changement de régime, et fermer la boucle

### Ce que le pas 44 laissait en suspens

La surveillance voyait un dossier franchir le seuil. Le portefeuille était
**entièrement en lecture seule** : le reclassement devait se poser à la main en
base, hors de tout contrôle, et la surveillance continuait d'alerter. Elle disait
ce qu'il fallait faire ; le faire restait hors du produit.

Ce pas donne au portefeuille sa première route d'écriture :
`POST /portefeuille/entreprises/{niu}/regimes`.

### Ce qu'une inscription est

Un statut daté **ne se modifie pas**. Changer de régime, c'est fermer la période en
cours à une date et en ouvrir une nouvelle le même jour. La période fermée garde
son motif et sa précision d'origine : c'est sous ce régime-là que les factures de
l'époque ont été contrôlées.

Une date d'effet **future** est le cas normal : un franchissement vu en novembre
prend effet au 1er janvier, et le cabinet qui fait son travail l'inscrit dès qu'il
le voit. Une date **passée** est admise aussi, pourvu qu'aucun exercice clos ne la
traverse.

### Les refus, et ce que chacun protège

| Refus | Ce qu'il protège |
| --- | --- |
| Un exercice clos traversé | Ses comptes ont été arrêtés, souvent déclarés, sous le régime en vigueur ; les faire relever d'un autre contredirait ce que le cabinet a signé |
| Le même régime | Une période de plus qui ne change rien rend l'histoire illisible |
| Une cause qui ne produit pas ce régime | On ne passe pas à l'IGS par dépassement de seuil |
| Un retour à l'IGS avant la période probatoire | Une entreprise n'oscille pas d'un régime à l'autre au gré de sa conjoncture |
| Une date qui effacerait une période | L'histoire ne se réécrit pas par la date d'effet |
| Une justification vide | Personne ne saurait dans trois ans pourquoi ce dossier a changé de régime |

⚠️ **La porte de sortie de la période probatoire.** Si l'option volontaire menait
aussi à l'IGS, on inscrirait « option » là où il faudrait « retour après
probatoire », et le contrôle ne jouerait jamais. Le passage à l'IGS n'admet donc
que deux causes : le retour après probatoire, et la décision de l'administration,
qui n'attend pas.

La correction n'est admise nulle part : elle ne se distingue pas d'un retour
déguisé. **Question ouverte**, à trancher avec le cabinet.

`retour_au_synthetique_admis`, écrite depuis le premier jour et jamais appelée, a
enfin son appelant.

### Qui peut inscrire

Une permission nouvelle, `INSCRIRE_STATUT`, au réviseur et à la direction seuls, et
**motif exigé**. Changer ce qu'une entreprise doit à l'administration engage le
cabinet au même titre que clore un exercice : mêmes personnes, même exigence.

Le comptable qui tient le dossier et y saisit ne peut pas en changer le régime ; un
cas le vérifie avec le comptable réel du dossier, pas avec un tiers.

Le texte de justification sert deux fois : il est transmis au contrôle
d'autorisation, qui le porte au journal d'audit, et il devient la précision du
nouveau statut. Deux champs auraient invité à écrire « voir audit » dans l'un.

### Le garde-fou qui comptait sans lire

Les dépôts du portefeuille refusaient déjà un enregistrement qui ferait disparaître
des périodes. **Ils ne comparaient que leur nombre**, et la documentation le disait.

Tant qu'aucune route n'écrivait, c'était sans conséquence. Dès qu'une route écrit,
une mise à jour qui garde deux périodes mais fait passer 2021 de l'IGS au réel
passait : même nombre, histoire réécrite, et les factures de 2021 se retrouvaient
contrôlées sous un régime qu'elles n'ont jamais connu.

La règle est remontée dans le domaine, `ecart_d_histoire` : une période close se
retrouve à l'identique, la période ouverte ne peut que recevoir sa date de fin, et
de nouvelles périodes peuvent s'ajouter.

⚠️ **Chaque dépôt portait sa propre copie, et elles ne disaient même pas la même
phrase** : « un statut daté ne se modifie pas » en mémoire, « ne se remplace pas »
en base. Un cas existant cherchait la première ; il a été aligné sur la phrase
unique.

### Un paramètre lu trop tôt

Le premier essai de refus par la route a rendu **une erreur interne** au lieu du
refus motivé. La route lisait la durée de la période probatoire au référentiel
**avant** d'appeler le domaine, et le référentiel ne la connaît qu'à partir du
1er janvier 2026 : toute date d'effet antérieure échouait sur la lecture du
paramètre, avant même que le domaine ait pu dire qu'elle traversait un exercice
clos.

Le domaine reçoit maintenant **une question plutôt qu'une réponse** : une fonction
qui lit le paramètre, appelée seulement si la règle en a besoin. Et si le
référentiel ne dit rien à cette date, la route refuse en le disant, plutôt que de
supposer une durée.

### La surveillance punissait le cabinet diligent

En fermant la boucle, un défaut du pas 44 est apparu. Un franchissement vu en
novembre, inscrit aussitôt avec effet au 1er janvier : le régime **en vigueur**
restait l'IGS jusqu'au 31 décembre, et le dossier restait signalé. Deux mois
d'alerte sur un dossier réglé, et le collaborateur apprend à l'ignorer.

La surveillance rend désormais `reclassement_inscrit_au`, et un passage au réel déjà
inscrit éteint l'alerte. Seul un passage **au réel** compte : un statut futur à
l'IGS, que l'entité admet pour un portefeuille repris d'un autre logiciel, ne
répond pas à un franchissement.

⚠️ **Une contre-épreuve du pas 44 était devenue fausse**, et elle a été réécrite
plutôt que forcée. Elle affirmait qu'un dossier observé le 31 décembre devait
alerter, alors que ce dossier portait déjà son reclassement au 1er janvier. Elle
confondait « avant la date d'effet » et « avant l'inscription » : le domaine ne
connaît que la première.

### La boucle, par HTTP

Un cas la parcourt entière sur PostgreSQL : une vente de 61 millions fait franchir
le seuil sur l'exercice en cours ; la surveillance signale le dossier ; le réviseur
inscrit le passage au réel au 1er janvier ; la route rend le dossier résolu à cette
date, assujetti à la TVA ; la surveillance cesse d'alerter et dit pourquoi.

### Les quinze mutations

Deux survivantes. **Une borne** : une date d'effet au 31 décembre tombe encore dans
l'exercice clos, et aucun cas ne distinguait « pendant » de « strictement pendant ».
**Un état que la route ne produit pas mais que l'entité admet** : deux périodes à
l'IGS qui se suivent. Le garde qui les distingue d'un reclassement est utile
précisément pour les données que le produit n'a pas écrites lui-même.

### État à la fin du pas 45

**2 777 tests passent** sur PostgreSQL réel, en 3 min 10 s. `ruff` propre.

**Ce que le projet sait faire qu'il ne savait pas.** Aller du chiffre des livres à
l'acte : voir le seuil approcher, inscrire le reclassement, et cesser d'alerter.

**Ce qui reste ouvert.** La correction d'un régime mal saisi à l'origine. Le
rattachement et l'adhésion, toujours en lecture seule. Le barème d'honoraires, le
fichier DIPE, les modèles d'états financiers.

*Un garde-fou qui compte sans lire est suffisant tant que personne n'écrit. Le jour
où l'on ouvre l'écriture, c'est lui qu'il faut relire en premier.*

---

## Pas 46 — L'abattement CGA s'accordait sur la parole de l'écran

### Ce qui a été trouvé

Le pas devait donner l'écriture à l'adhésion, comme le pas 45 l'a donnée au régime.
En cherchant qui lisait l'adhésion, on a trouvé plus grave.

La route de liasse fiscale, `GET /cloture/dossiers/{niu}/liasse/{exercice}`, recevait
un paramètre de requête **`adherent_sur_l_exercice`, `True` par défaut**. C'est lui
qui commandait l'abattement CGA, une déduction sur le bénéfice imposable. Toute liasse
l'accordait donc, que l'entreprise ait adhéré ou non, sauf si l'écran pensait à dire
le contraire.

Sa description le reconnaissait : « passé et non déduit : la question se répond en
comparant des intervalles d'adhésion, et c'est au portefeuille de le faire ». La dette
était connue, écrite, et son défaut était le plus dangereux des deux possibles.

⚠️ **C'est le Centre qui atteste l'adhésion.** Une liasse qui accorde l'abattement à
tort n'est pas une erreur de calcul de l'adhérent : c'est une attestation fausse du
Centre, et c'est son agrément qui répond.

### Le seuil que personne ne lisait

Le droit a une seconde condition : CGI art. 118, le centre assiste les entreprises
dont le chiffre d'affaires annuel **n'excède pas 100 millions**. Le paramètre
`SEUIL_ADHESION_CGA` était au référentiel, **validé**, avec une note qui disait :
« c'est le critère d'éligibilité du métier même du cabinet ».

**Aucune ligne de code ne le lisait.** Une entreprise adhérente devenue trop grande
recevait l'abattement chaque année.

C'est la même famille que les pas 43 et 44 : une capacité écrite, documentée, et sans
appelant. Mais ici, l'absence d'appelant ne laissait pas une fonctionnalité en
attente : elle accordait un avantage fiscal indu.

### Ce qui a été fait

**La question de l'adhésion est posée au portefeuille**, comme le passage fiscal le
demandait depuis le premier jour : `Entreprise.adherente_sur_toute_la_periode`.

⚠️ **Une même adhésion, pas une suite d'adhésions.** Une résiliation au 30 juin suivie
d'une réadhésion au 1er juillet couvre chaque jour de l'année, et c'est pourtant une
rupture : deux contrats, deux dates d'effet. Un contrôle jour par jour aurait conclu à
une adhésion continue. Une mutation qui remplace la règle par ce comptage est tuée.

**Le droit est apprécié dans le domaine de la clôture**, `apprecier_le_droit` : adhésion
sur tout l'exercice, chiffre d'affaires sous le seuil, et un seuil inconnu du
référentiel ferme le droit. *Attester une éligibilité qu'on ne peut pas vérifier est
précisément la faute à éviter.* Le seuil lui-même reste éligible : la loi dit « n'excède
pas ».

**La liasse ne lit plus la requête.** Elle rend `droit_cga` avec son motif : une
déduction qui apparaît ou disparaît sans explication fait croire à une erreur de
calcul, et le réviseur la « corrigerait » en sens inverse.

Le paramètre du passage fiscal s'appelait `adherent_sur_l_exercice` ; il s'appelle
désormais `droit_a_l_abattement_cga`. *L'ancien nom mentait par omission* : il laissait
croire que l'adhésion suffisait.

Au passage, la route de liasse **recalculait le chiffre d'affaires à la main**, en
doublon de la projection partagée écrite au pas 44. Elle emploie désormais la
projection.

### La lecture prudente, et pourquoi

Le texte ne dit pas si une adhésion prise en cours d'exercice ouvre l'abattement pour
cet exercice. Le code répond **non**, et c'est inscrit en **question ouverte Q17**, avec
le dossier de démonstration qui en fait un cas concret : réadhérent au 1er juillet 2022,
sans abattement pour 2022.

La prudence a ici un sens précis : accorder à tort est une attestation fausse du
Centre, refuser à tort se rattrape par réclamation. Si le cabinet établit le contraire,
une seule méthode change.

La question **Q18**, la correction d'un régime mal saisi, laissée ouverte au pas 45, est
inscrite au même endroit.

### Les cas

Seize cas. Les bornes de la couverture, jour par jour. Le seuil et le franc de plus.
Et par la route, sur PostgreSQL, avec des ventes produites par la saisie : à
60 millions l'abattement figure, à 150 millions il disparaît et dit pourquoi — et
**un écran qui envoie encore `adherent_sur_l_exercice=true` ne rouvre rien**. Ce dernier
cas garde le défaut d'origine dans le temps.

**Neuf mutations, neuf tuées du premier coup.** Ce n'est pas suspect cette fois : chaque
cas avait été écrit contre une borne ou une condition précise, et la contre-épreuve à
60 millions empêche une liasse qui n'accorderait jamais l'abattement de les faire tous
passer.

### État à la fin du pas 46

**2 793 tests passent** sur PostgreSQL réel, en 3 min 17 s. `ruff` propre.

**Ce que le projet sait faire qu'il ne savait pas.** Refuser d'attester ce qu'il ne peut
pas vérifier. L'abattement CGA suit désormais les faits du dossier et de ses livres, et
dit pourquoi il figure ou ne figure pas.

**Ce qui reste ouvert.** Q17 et Q18. L'adhésion et le rattachement, toujours en lecture
seule : le pas prévu pour eux reste à faire, et il devra respecter la même règle que
l'adhésion elle-même, dont la date d'effet est fiscalement porteuse.

*Un paramètre qui décide d'un avantage fiscal ne se reçoit pas d'un écran. Il se
constate, et un défaut à `True` est la pire façon de ne pas le constater.*

---

## Pas 47 — Relire le document avant de continuer

### La demande

« Faudrait te rassurer que notre artefact est à jour. » Le document de conception doit
être un recueil complet du projet ; six pas venaient de s'y ajouter l'un après l'autre,
et aucun n'avait relu ce qui existait déjà.

### Ce que la vérification a établi

**La version en ligne est bien le fichier local.** Le contenu publié a été relu et
comparé au fichier source, ligne à ligne : une seule différence, la première ligne,
qui portait dans le fichier local une enveloppe `<!doctype html><html><head>…<body>`
complète. L'outil de publication ajoute lui-même cette enveloppe et ne la double pas,
si bien que la page en ligne n'en portait qu'une. Le fichier source ne doit pourtant
pas la contenir : elle a été retirée.

**Mais le document n'était plus exact partout.** Six sections ajoutées ne suffisent pas
à tenir un recueil à jour, si les sections anciennes continuent d'affirmer l'état
d'avant.

### Ce qui était périmé

**La section 17, « Ce qui tourne aujourd'hui »**, affirme que chaque chiffre de son
tableau est mesuré au moment de la republication. Il datait d'avant le pas 41 :

| Ce qu'elle disait | Ce qui a été mesuré |
| --- | --- |
| 115 chemins HTTP | 127 routes sur 120 chemins |
| 28 routes sur 122 sans permission | 28 routes sur 127, liste close inchangée |
| 35 corps de requête balayés | 38 |
| Production comptable : premier chaînon posé | Du justificatif à la déclaration, éprouvé de bout en bout |
| Échange piloté par un profil | Dans les deux sens, avec un seul profil |
| Recette : onze scénarios | Deux recettes, 48 cas HTTP sur PostgreSQL |

Inchangés, et vérifiés comme tels : les cinq travaux périodiques, les quinze
migrations, les vingt-huit routes publiques.

Sept lignes manquaient, pour des capacités construites depuis : la reprise, la
clôture d'exercice, les transitions revalidées, la surveillance des seuils, le
portefeuille et sa seule route d'écriture, l'abattement CGA. Deux décisions métier
aussi, puisqu'elles commandent désormais du code écrit : Q17 et Q18.

**La section 51** annonçait dans « Ce qui reste à faire » que le portefeuille demeurait
en lecture seule. La section 52 l'avait levé. La phrase dit maintenant l'un et
l'autre.

**La section 2** comptait « les vingt-deux pas déjà faits ». Un nombre écrit dans le
texte dérive dès le pas suivant ; il renvoie maintenant au décompte de l'en-tête, qui
est mis à jour à chaque publication.

### Ce qui était mal rangé

**Le sommaire entassait les sections 48 à 53 dans la même ligne que la 47**, parce que
chaque ajout avait accroché son lien derrière le précédent. Elles se lisaient comme un
seul paragraphe.

**Et les sections 42 à 53 étaient rangées sous « Annexes »**, alors qu'elles racontent
des pas construits. Elles ont leur groupe, « VIII · Le journal de construction », et les
quatre annexes retrouvent le leur.

### Ce qui manquait au glossaire

Douze termes entrés dans le code aux pas 41 à 46 n'y figuraient pas : abattement CGA,
à-nouveau, clôture d'exercice, exercice clos, mutation, période probatoire, profil
d'échange, reprise, seuil d'adhésion, seuil d'assujettissement, statut daté,
transition. Un recueil qui emploie un mot sans le définir oblige le lecteur à le
chercher dans le code.

### État à la fin du pas 47

Aucun code n'a bougé : **2 793 tests**, inchangés. Le document compte **57 sections**,
toutes au sommaire, une ligne chacune, **40 termes** au glossaire, aucun lien sans cible,
aucun tiret quadratin. Publié en version 47.

*Ajouter une section ne met pas un recueil à jour. Il faut relire celles qui affirment
l'état d'avant, et remesurer chaque chiffre qui prétend l'être.*

---

## Pas 48 — Admettre un dossier au Centre, et résilier son adhésion

### Pourquoi maintenant

L'adhésion est l'objet même d'un centre de gestion agréé, et le portefeuille ne savait
pas l'écrire. Le pas 46 venait de rendre l'abattement CGA dépendant de l'adhésion
**réelle** : sans moyen de l'inscrire, la seule adhésion qui comptait était celle posée
à la main en base.

Deux routes, sous la permission `INSCRIRE_STATUT` et motif exigé :
`POST /portefeuille/entreprises/{niu}/adhesions` et
`POST /portefeuille/entreprises/{niu}/adhesions/resiliation`.

### L'asymétrie qui tient le module

L'entité le dit depuis le premier jour : la date d'effet d'une adhésion est
**fiscalement porteuse**, elle ouvre l'abattement et l'exonération de patente.

| Geste | Date d'effet admise | Pourquoi |
| --- | --- | --- |
| Adhérer | jamais avant le jour de l'inscription | le sens qui **accorde** un avantage ne remonte pas le temps |
| Résilier | une date passée, sans traverser d'exercice clos | le sens qui **retire** est le sens prudent, mais il ne réécrit pas ce que le Centre a attesté |

Antidater d'un seul jour suffit à mal faire : si ce jour tombe dans l'exercice, il peut
faire basculer la couverture de l'exercice entier, donc l'abattement.

⚠️ **L'horloge est lue par la route, jamais par le domaine.** Le domaine reçoit le jour
d'inscription en argument : c'est ce qui rend la règle d'antidate éprouvable sans
attendre minuit.

### L'éligibilité se déclare à l'admission, et c'est assumé

L'article 118 réserve le Centre aux entreprises dont le chiffre d'affaires n'excède pas
100 millions. Au pas 44, la règle était « le chiffre se lit dans les livres, jamais
déclaré ». Elle ne peut pas valoir ici : une entreprise qui adhère n'a en général encore
aucune écriture chez le Centre, et le portefeuille ne lit pas la comptabilité.

Le chiffre est donc **déclaré avec sa source**, et porté dans la précision de
l'adhésion. C'est une première barrière, pas la seule : à chaque liasse, le pas 46
apprécie le droit sur les livres. Une déclaration fausse à l'admission ne produit
aucun avantage ; elle se voit à la première clôture, et l'on saura sur quoi le Centre
s'était fondé pour admettre.

### Le numéro s'attribue, il ne se reçoit pas

`ADH-année-séquence`, sur **tout le portefeuille**, pour la même raison que le numéro
d'une écriture : la continuité d'une séquence appartient au registre. Le jeu de
démonstration le montre, avec ADH-2022-014 et ADH-2022-019 sur deux dossiers
différents. Une demande qui porte un numéro est refusée à la validation du corps.

### La raison de la résiliation va au journal d'audit

Une période porte le motif et la précision de son **ouverture**, et le garde-fou
d'histoire du pas 45 n'autorise sur une période ouverte qu'une chose : recevoir sa date
de fin. Réécrire la précision pour y ajouter la raison de la fin effacerait la
déclaration d'éligibilité faite à l'admission, justement ce qu'un vérificateur
demandera. La justification de la résiliation est exigée au contrôle d'autorisation,
qui la porte au journal.

### Ce que les épreuves ont appris

**Une règle de l'entité rejouée, une fois de plus.** Le domaine refusait une adhésion
antérieure à la création de l'entreprise ; l'entité le refuse déjà. Une mutation qui
supprime le contrôle survivait. Même correction qu'au pas 42 : le contrôle recopié est
retiré, et le refus de l'entité ressort en **refus nommé**, en `409` au lieu d'une
erreur interne. Le cas est éprouvé sur une entreprise dont l'immatriculation est à
venir, forme que prend un dossier converti depuis une création.

**Une mutation tuée pour une mauvaise raison.** Le mutant « antidate acceptée »
employait `timedelta`, que le module n'importe pas : le code plantait, et treize cas
échouaient sans rien mesurer. Rejouée avec un mutant valide, elle est tuée par les deux
cas qui comptent. *Une mutation tuée par un plantage ne prouve rien sur le cas.*

**Un compte suspendu pris pour un comptable.** Le seul titulaire du dossier intermittent
de démonstration est le collaborateur parti en avril, dont le compte est suspendu. Le
cas de permission mesurait le refus de session, pas le refus de permission. Il emploie
désormais un comptable actif, sur un dossier qu'il tient.

### Les chiffres remesurés

Deux routes et deux corps de requête de plus : **129 routes sur 122 chemins, 40 corps
de requête**, vingt-huit routes toujours sans permission. La section 17 du document a
été remise à jour dans la même publication, suivant la leçon du pas 47.

### État à la fin du pas 48

**2 821 tests passent** sur PostgreSQL réel, en 5 min. `ruff` propre. **Dix-neuf
mutations valides, dix-neuf tuées.**

**Ce que le projet sait faire qu'il ne savait pas.** Admettre et résilier, avec une date
d'effet qui ne ment pas, un numéro que personne ne choisit, et une éligibilité dont on
garde la source.

**Ce qui reste ouvert.** Le rattachement, dernier statut en lecture seule. La revue des
adhérents devenus inéligibles en cours de route. Q17 et Q18.

*Le sens qui accorde un avantage ne remonte pas le temps. Celui qui le retire le peut,
tant qu'il ne contredit pas ce qui a été signé.*

---

## Pas 49 — La borne d'un seuil est une donnée légale

### Ce qui a été trouvé

Le pas devait écrire la revue des adhérents devenus inéligibles. En la préparant, la
comparaison au cœur de `diagnostiquer_seuil` a arrêté la lecture :

```python
franchi = chiffre_affaires >= seuil
```

Sa propre documentation dit qu'elle sert `SEUIL_ASSUJETTISSEMENT_TVA` et
`SEUIL_COMPTABILITE_OBLIGATOIRE`. Or leurs fondements, au référentiel, ne disent pas la
même chose de la valeur même :

| Seuil | Texte | La valeur elle-même… |
| --- | --- | --- |
| Assujettissement TVA | « supérieur à 50 000 000 » | n'est **pas** atteinte |
| Adhésion CGA | « n'excède pas 100 000 000 » | reste éligible |
| Acte notarié SARL | « capital n'excède pas 1 000 000 » | n'exige pas de notaire |
| Espèces TVA | « au moins égale à 100 000 » | est visée |
| Comptabilité obligatoire | « dès 10 M » | oblige |
| Système normal | le minimal pour qui « reste sous » 60 M | relève du normal |

**Un même opérateur ne pouvait pas avoir raison pour les deux seuils que la fonction
nommait**, et il avait tort pour celui de la TVA. Une entreprise à 50 000 000 exactement
était déclarée en franchissement, et invitée à un reclassement au réel que la loi ne lui
impose pas. Aucun cas ne mesurait la borne : elle n'était écrite nulle part.

### Ce qui a été fait

**La borne vit au référentiel, sur chaque version, à côté de la valeur et de son
fondement.** `Borne.INCLUSE` quand la valeur même atteint le seuil, `Borne.EXCLUSE`
quand il faut la dépasser. Sur la version, et non sur le paramètre : une loi de finances
peut changer la formulation sans changer le montant.

**Une seule fonction compare**, `seuil_atteint`, et `ParametreResolu.atteint` s'appuie
sur elle. Un seuil qui ne déclare pas sa borne **lève** plutôt que de supposer : c'est au
franc près que l'erreur se commet, et au franc près qu'elle coûte.

Toutes les comparaisons de seuil du code passent désormais par elle : le diagnostic de
seuil, la surveillance et sa route, le droit à l'abattement, l'admission au Centre, le
système de la liasse. `diagnostiquer_seuil` reçoit la borne **obligatoirement**, et le
diagnostic la rend avec lui : « franchi » ne se comprend qu'avec elle.

**Un contrôle d'intégrité l'exige** sur chaque version de chaque `SEUIL_*` et
`CAPITAL_MINIMUM_*`, versions passées comprises : une version ancienne sans borne ferait
échouer la relecture d'une liasse des années plus tard. Et il **lie la borne à la
formulation citée dans le fondement** : si l'un change sans l'autre, il échoue.

### Ce que l'annotation a elle-même appris

En annotant les dix seuils, la borne de l'acte notarié a été marquée « à confirmer,
retenue incluse ». Relu en entier, le texte dit « capital **n'excède pas** 1 000 000 » :
exclue. *La borne avait été devinée à l'envers, dans le pas même qui existe pour qu'on
cesse de la deviner.* Le cas de liaison au fondement l'empêche maintenant.

**Deux comparaisons avaient raison par hasard.** Le droit à l'abattement (`<=`) et le
système de la liasse (`>=`) comparaient comme leurs textes le demandent, sans que rien ne
le dise. Elles lisent maintenant la borne ; un cas au franc près le garde pour chacune.

**Et le document de conception enseignait le défaut.** Le principe n° 1, « aucune valeur
légale en dur », montrait comme code attendu `if montant >= seuil`. La valeur venait bien
du référentiel ; l'opérateur, lui, restait en dur. Il a été corrigé dans la même
publication.

### Ce que les mutations ont appris

**Dix mutations, dix tuées**, après une survivante : le droit à l'abattement calcule son
verdict et son motif **en deux endroits**. Une mutation du motif laissait le droit ouvert à
100 000 000 exactement tout en écrivant « au-delà du seuil ». Un réviseur qui lit le motif
aurait corrigé la liasse dans le mauvais sens. Un cas vérifie désormais, sur cinq montants
dont la borne, que le motif ne contredit jamais le verdict.

### État à la fin du pas 49

**2 837 tests passent** sur PostgreSQL réel, en 4 min 38 s. `ruff` propre. Aucune route
nouvelle : la surface de la section 17 est inchangée.

**Ce que le projet sait faire qu'il ne savait pas.** Comparer un montant à un seuil comme
le texte le dit, et refuser de comparer quand le texte n'a pas été lu.

**Ce qui reste ouvert.** La revue des adhérents devenus inéligibles, qui peut maintenant
s'écrire sur une comparaison juste. Le rattachement. Q17 et Q18.

*Une valeur légale sortie du code n'est qu'à moitié sortie si l'opérateur y reste.*

---

## Pas 50 — La revue des adhérents qui grandissent

### L'intervalle que rien ne couvrait

Le Centre admet une entreprise sur un chiffre d'affaires **déclaré** (pas 48). Il refuse
l'abattement à la liasse quand les **livres** dépassent le seuil de l'article 118
(pas 46). Entre les deux, rien ne lui disait qu'un adhérent grandissait.

Découvrir le dépassement à la liasse, c'est le découvrir des mois après la clôture, au
moment où l'adhérent attend un abattement qu'il n'aura pas. La route
`GET /obligations/eligibilite-des-adherents` comble l'intervalle.

### Ce que la revue est

Les deux mesures du pas 44, calculées par la même fonction : l'exercice clos donne un
**fait** (`hors_champ`), l'exercice en cours une **veille**. Triée par urgence, le fait
avant la prévision, filtrée par défaut sur ce qui demande un regard. La borne vient du
référentiel, suivant le pas 49 : à 100 000 000 exactement, l'adhérent reste dans le
champ.

### Ce qu'elle n'est pas

**Elle ne résilie rien.** Sortir du champ de l'article 118 n'éteint pas l'adhésion de
plein droit ; c'est une information que le cabinet porte à son adhérent, et la décision
passe par la route de résiliation, son motif et son journal.

**Elle ne revoit que les adhérents.** Un non-adhérent à 300 millions n'appelle aucune
démarche du Centre ; le faire figurer noierait ceux qui en appellent une.

**Elle ne parle pas le vocabulaire du régime.** Le diagnostic de seuil rend un
« reclassement requis » et un « régime actuel ». Rendus tels quels dans une revue
d'adhésion, ils feraient lire à un collaborateur qu'un adhérent doit changer de régime
fiscal. Les mesures sont retraduites, sans être recalculées, et un cas vérifie
qu'aucun des deux mots ne sort.

### Le piège de l'alerte anticipée

Le diagnostic ne lève plus d'alerte **une fois le seuil franchi** : l'alerte anticipée
vaut « pas encore franchi, mais proche ». Une revue qui ne regarderait que l'alerte
laisserait sortir un adhérent à 120 % sur son exercice en cours, au moment précis où il
faut l'appeler. `a_surveiller` retient donc l'exercice en cours **au-delà** du seuil
autant que celui qui s'en approche.

### Ce que les épreuves ont appris, une nouvelle fois

**Une mutation tuée par un plantage.** Le mutant « borne ignorée » employait `Borne`,
que la route n'importe pas : le code plantait, et l'épreuve paraissait réussie. C'est
exactement le piège noté au pas 48, et il a resurgi deux pas plus tard.

**Et le mutant valide n'était tué que par une relecture.** Rejoué correctement, il
n'échouait que sur l'assertion qui relit le champ `borne` rendu, pas sur le classement.
Un cas par la route a été ajouté : une vente de 100 000 000 exactement, saisie et
validée, reste dans le champ. Le mutant tombe désormais sur le comportement.

*Une épreuve qui échoue ne dit rien tant qu'on n'a pas lu pourquoi elle échoue.*

**Douze épreuves valides, douze tuées.** La boucle avec le pas 48 est éprouvée par HTTP :
un adhérent résilié sort de la revue.

### État à la fin du pas 50

**2 850 tests passent** sur PostgreSQL réel, en 4 min 43 s. `ruff` propre.
**130 routes sur 123 chemins**, 40 corps de requête, 28 routes sans permission.

**Ce que le projet sait faire qu'il ne savait pas.** Voir un adhérent sortir du champ du
Centre avant la liasse qui le lui apprendrait trop tard.

**Ce qui reste ouvert.** Le rattachement. Q17 et Q18. Les maquettes d'états
financiers, le fichier DIPE, le barème d'honoraires.

*Une revue qui dit le vrai dans le mauvais vocabulaire fait prendre une décision
fausse.*

---

## Pas 51 — Mesurer les écrans, et trouver la porte qui manquait

### La mesure qui corrigeait une estimation

Au pas 50, l'avancement du frontend avait été estimé à 40 %, avec cette réserve : c'était
l'estimation la moins sûre. Elle a été mesurée : quelles routes du backend le frontend
appelle-t-il réellement ?

**Première mesure : 19 %. Elle était fausse.** L'expression régulière s'arrêtait à la
parenthèse de `${encodeURIComponent(niu)}` : tout chemin à paramètre était tronqué, donc
non reconnu. Les pages de comptabilité, de grand livre, de clôture existaient bien. Un
analyseur qui suit les accolades imbriquées a remplacé l'expression.

**Mesure corrigée : 40 routes sur 130, soit 31 %.** Quelques routes ne demandent aucun
écran par nature — le webhook de paiement, la santé, l'ordonnancement — et ne changent pas
l'ordre de grandeur. Les routes construites aux pas 41 à 50 (reprise, clôture, seuils,
régime, adhésion, éligibilité) n'ont presque aucun écran.

*Une mesure qui confirme une estimation se vérifie autant qu'une mesure qui la dément.*

### La porte d'entrée qui manquait

La mesure affichait l'acquisition à **0 route sur 19**, alors que la vitrine porte deux
formulaires. Les deux composaient un lien `wa.me` et **n'appelaient jamais
`POST /acquisition/demandes`**.

Leur en-tête le justifiait : « le point d'entrée n'existe pas encore ». Il existait depuis
le chantier 3. Le motif était resté, et la conséquence était lourde : **aucune demande
venue du site n'entrait dans le système.** Ni l'affectation à un responsable, ni la veille
des dossiers immobiles, ni la reprise automatique, ni la relance ne voyaient jamais un
vrai prospect. Une demande partait dans une conversation WhatsApp, hors de toute trace.

C'est la famille la plus fréquente de ce projet, sous une forme nouvelle : non plus une
capacité sans appelant, mais **une justification restée en place après que le manque a été
comblé ailleurs**.

### Ce qui a été fait

Une action serveur, `app/lib/actions-acquisition.ts`, suivant la règle du frontend : le
navigateur ne parle jamais au backend. Le formulaire de contact **enregistre la demande et
ouvre WhatsApp** : WhatsApp reste le canal professionnel dominant au Cameroun, et
l'ouverture doit suivre immédiatement le clic, faute de quoi le navigateur la bloquerait
comme une fenêtre surgissante. L'issue de l'enregistrement s'affiche sous le bouton.

⚠️ **Le consentement transmis est celui que le visiteur a donné, pas plus.** La case dit
« me recontacter au sujet de ma demande » : ce n'est pas un consentement WhatsApp. La
demande part avec `consentement_whatsapp: false`, et le backend rappelle par téléphone.

⚠️ **L'action se valide elle-même** : elle est joignable par un POST direct. Consentement
exigé, bornes revérifiées.

⚠️ **Le formulaire de la bannière n'est pas branché.** Il n'a aucune case de consentement ;
y enregistrer des données personnelles suppose d'en ajouter une à un écran validé par le
cabinet. Question ouverte **Q19**.

### L'essai réel

Backend et site démarrés, l'action serveur appelée exactement comme le navigateur le fait,
par son identifiant de construction. Une demande valide est enregistrée : dossier créé,
état `DEPOSEE`, numéro normalisé en `+237…`, en attente d'affectation. Un POST direct sans
consentement est refusé par l'action.

**Et un numéro étranger a rendu au visiteur la trace brute de pydantic** : « 1 validation
error for DemandeDeContact », des noms de types, un lien vers pydantic.dev.

### La correction qui était restée privée

Pydantic enveloppe une `ValueError` de validateur dans une `ValidationError`, qui **est**
une `ValueError`. Une route qui renvoie `str(refus)` croit rendre la phrase du domaine et
rend la trace entière.

La comptabilité le savait : elle avait sa fonction de déballage, avec un commentaire
décrivant cette trace mot pour mot. **Elle était privée à ses routes.** Onze autres sites de
refus renvoyaient `str(refus)`, dont la route publique, celle des visiteurs anonymes.

La fonction est remontée dans `app/partage/erreurs.py`, les onze sites la emploient, la
copie locale a été retirée. Un contrôle balaie toutes les routes et refuse qu'un
`except ValueError` renvoie `str()` ; il prouve qu'il balaie, et qu'il verrait le défaut
revenir. Rejoué, l'essai réel rend au visiteur : « +33612345678 n'est pas un numéro
camerounais exploitable. Neuf chiffres commençant par 6 pour un mobile… ».

*Une correction qui reste privée corrige un écran, et laisse le défaut à tous les autres.*

### État à la fin du pas 51

**2 856 tests passent** sur PostgreSQL réel. `ruff` propre. Frontend : typage, lint et
construction de production sans erreur.

**Ce que le projet sait faire qu'il ne savait pas.** Recevoir un prospect depuis son site.
Le parcours d'acquisition, construit sur trois chantiers, a enfin sa porte d'entrée.

**Ce qui reste ouvert.** Q19 et la bannière. Les écrans des pas 41 à 50. Le rattachement.

---

## Pas 52 — Un écran pour la veille des seuils, et le mode démonstration qui mentait

### L'écran

La mesure du pas 51 avait compté 40 routes appelées par le frontend sur 130. Les deux
revues qui font le métier d'un centre agréé n'en faisaient pas partie : le seuil de
régime (pas 44) et l'éligibilité des adhérents (pas 50). Aucun collaborateur ne pouvait
les voir.

`/obligations/veille-des-seuils`, sous « Obligations fiscales » : les deux revues côte
à côte, triées par urgence dans l'ordre du backend, filtrées par défaut sur ce qui demande
un regard, avec un lien pour afficher tout le portefeuille. L'exercice en cours s'affiche
avec sa part écoulée, jamais extrapolé. Garde de permission avant tout appel, comme les
autres écrans : sans `LIRE_COMPTABILITE`, l'écran refuse en nommant la permission.

⚠️ **L'écran ne refait aucun raisonnement.** `reclassement_du`, `hors_champ`,
`a_surveiller` viennent du backend. Les recalculer à l'écran ferait une seconde règle, qui
divergerait à la prochaine correction, comme celle de la borne au pas 49. Les pastilles
de statut ont reçu quatre valeurs fermées, et « Reclassement dû » et « Hors champ »
prennent le ton du retard : ce sont des faits acquis, pas des prévisions.

### L'essai réel qui a trouvé le défaut

Backend et site démarrés, une session ouverte, une vente de 45 millions saisie et validée
sur un dossier encore à l'IGS. La page s'est rendue, et **le dossier n'y figurait pas**.

Interrogée directement, la route de la revue lisait **zéro** chiffre d'affaires ; la
balance de la comptabilité, sur le même dossier, lisait 45 millions.

### La famille entière

En persistance mémoire, le mode de démonstration et de développement, chaque contexte
construisait son propre dépôt. Mesuré sur l'application :

| Dépôt mémoire | Constructions | Mémoïsées |
| --- | --- | --- |
| Écritures | 4 contextes | 1 |
| Entreprises | 5 contextes | 2, **séparément** |
| Pièces | 2 contextes | 1 |
| Demandes de pièces | 2 contextes | 1 |

Les conséquences, chacune silencieuse : une écriture saisie invisible des revues, de la
liasse et du pilotage ; un régime inscrit au portefeuille invisible des obligations ; un
exercice fermé par la clôture écrit dans un magasin jeté aussitôt ; et la comptabilité
vérifiant qu'un exercice est clos **contre un portefeuille neuf**.

Sa propre documentation l'annonçait pourtant : « la comptabilité ne stocke pas ses propres
exercices, et c'est volontaire : deux registres d'exercices divergeraient, et l'on
saisirait dans un exercice ouvert d'un côté, clos de l'autre ». Le principe était juste ;
le code construisait le second registre.

Le garde posé au pas 28 pour la même famille ne balayait **que la Souscription**.

⚠️ **En base PostgreSQL, tout était juste**, parce que la base est unique, et tous les cas
par la route tournent sur PostgreSQL. C'est le mode que l'on montre au cabinet qui
mentait, et il mentait sans erreur.

### Ce qui a été fait

Chaque contexte propriétaire tient son magasin dans `adaptateurs/sortant/magasins_memoire.py`,
avec une fabrique mémoïsée et une fonction pour le vider : la comptabilité ses écritures,
le portefeuille ses entreprises, la collecte ses pièces et ses demandes. Les voisins le
lisent par l'`api`. Six fichiers de routes rebranchés.

Un contrôle balaie **l'application entière** : une seule construction par sorte de dépôt,
et jamais dans une fonction rejouée à chaque appel. Il prouve qu'il balaie, il verrait le
défaut revenir, et il mesure aussi le comportement : ce qu'écrit la comptabilité est ce
que lisent les obligations. Sa limite est écrite : un constructeur de porteur, comme le
`Comptoir` de la Souscription, est supposé mémoïsé plutôt que vérifié.

Rejoué, l'écran affiche : ETS TCHOUMBA & FILS, 45 000 000, 90 % du seuil, 70 % de
l'exercice écoulé, « À surveiller ».

### Relevé en passant

L'écran de l'échéancier affiche toujours « le contexte Social n'existe pas encore » ; ce
contexte existe, avec cinq routes. L'avertissement est à revoir avec le calcul qu'il
justifie.

### État à la fin du pas 52

**2 862 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de
production. **42 routes appelées par le frontend sur 130.**

**Ce que le projet sait faire qu'il ne savait pas.** Montrer aux collaborateurs les deux
revues qui font le métier du Centre, et montrer au cabinet une démonstration qui dit
vrai.

*Un mode de démonstration qui ment sans erreur est plus dangereux qu'un mode qui plante :
on le montre au client.*

## Pas 53 — Le geste qui répond à l'alerte, et la ligne qui disait « sous le seuil » à 140 %

### Pourquoi

Le pas 52 affichait « Reclassement dû » sur la veille des seuils, et ne permettait rien.
La route qui inscrit le changement de régime existait depuis le pas 45 ; aucun écran ne
l'appelait. Le réviseur voyait l'alerte et devait inscrire le passage au réel ailleurs,
c'est-à-dire nulle part dans l'application.

### Ce qui a été fait

**Une action serveur** (`app/lib/actions-portefeuille.ts`, `inscrireReclassement`) qui
appelle `POST /portefeuille/entreprises/{niu}/regimes` avec le régime `REEL` et la cause
`DEPASSEMENT_SEUIL`, puis revalide la page.

⚠️ **Le régime et la cause ne se choisissent pas.** C'est le seul geste qui répond à
l'alerte affichée. Proposer tous les régimes et toutes les causes ferait de l'écran
d'alerte un formulaire générique, d'où l'on pourrait inscrire un retour à l'IGS qui n'a
rien à y faire.

**Un composant replié** (`app/components/obligations/InscrireReclassement.tsx`), sur le
modèle de la contre-passation : un bouton qui déplie une date d'effet et une
justification. Inscrire un changement de régime engage le cabinet ; un formulaire ouvert
sur chaque ligne inviterait à le remplir par habitude.

- **La date d'effet est proposée** : le 1er janvier qui suit l'exercice clos mesuré,
  modifiable. Un libellé d'exercice qui n'est pas une année ne propose rien, plutôt que de
  deviner une date fausse.
- ⚠️ **La justification n'est jamais préremplie.** Elle part au journal d'audit. Un texte
  composé d'avance serait un motif que personne n'a écrit, validé d'un clic. L'indication
  grisée en suggère la forme sans l'écrire.
- **L'écran ne rejoue pas les règles du backend.** Une date qui traverse un exercice clos
  est refusée par le domaine, et le refus est affiché tel quel.

**Le bouton n'apparaît que sur un reclassement dû**, c'est-à-dire constaté sur un exercice
clos, et pour qui détient `INSCRIRE_STATUT`, lue une fois par la page serveur. Un
exercice en cours déjà au-delà du seuil reste une veille : son chiffre est partiel, et
inscrire un changement de régime sur une prévision serait décider à la place des livres.

### La dérive des permissions

Pour garder le bouton, il fallait tester `INSCRIRE_STATUT` côté frontend, et le type
`Permission` de `app/lib/acces.ts` ne la connaissait pas. Comparé à l'énumération du
backend, il lui en manquait **trois** : `INSCRIRE_STATUT`, `LIRE_PROSPECT`,
`QUALIFIER_PROSPECT`. Les rôles, eux, concordaient.

Ajoutées. ⚠️ **Aucun contrôle ne garde encore cette concordance** : les deux dépôts sont
séparés, et un test du backend qui lirait un fichier du frontend lierait leurs cycles. La
dérive se voit aujourd'hui au moment où l'on écrit un bouton, parce que le typage refuse
une permission inconnue ; elle ne se voit pas pour une permission que personne ne teste.
Point ouvert.

### L'essai réel

Backend en mémoire, pré-rempli par un lanceur de travail d'une vente validée de
70 millions sur l'exercice 2025 d'un dossier à l'IGS (l'exercice 2025 est clos dans la
démonstration, et les routes refusent à juste titre d'y saisir). Site en production
locale.

| Essai | Résultat |
| --- | --- |
| Page vue par le réviseur | « Reclassement dû », bouton présent |
| Page vue par le comptable du dossier | « Reclassement dû », **bouton absent** |
| Justification de dix caractères | refus de l'écran, lisible |
| Date d'effet au 01/06/2025 | refus du domaine : l'exercice clos 2025 serait traversé |
| Date d'effet au 01/01/2026 | « Passage au réel inscrit au 01/01/2026. » |
| Action appelée directement par le comptable | « Action non permise : INSCRIRE_STATUT est requise », le dossier reste dû |

### Le défaut trouvé par l'essai

Après l'inscription, la page rechargée a affiché, pour ce dossier à **140 % du seuil** :
« **Sous le seuil** ».

Le diagnostic ne lève aucune alerte sur un dossier déjà au réel, puisqu'il n'y a plus rien
à reclasser. L'écran du pas 52 écrivait « Sous le seuil » pour **toute ligne sans alerte**.
C'était faux depuis le premier jour pour les dossiers de démonstration au réel, mais
invisible : ils étaient à zéro. L'inscription l'a rendu flagrant, la ligne passant de
« Reclassement dû » à « Sous le seuil » comme si le chiffre avait baissé.

La conclusion sans alerte lit désormais le régime rendu par le backend, à la date
d'observation : « Au réel », ou « Sous le seuil ». Rejoué : le dossier inscrit et les
dossiers de démonstration au réel affichent « Au réel », les dossiers à l'IGS « Sous le
seuil ».

### État à la fin du pas 53

Aucun code du backend touché : **2 862 tests**, inchangés. Frontend : typage, lint,
construction de production. **43 routes appelées par le frontend sur 130** (33 %).

**Ce que le projet sait faire qu'il ne savait pas.** Répondre à l'alerte de reclassement
depuis l'écran qui la lève, avec la même garde, le même motif et les mêmes refus que la
route.

*Une conclusion par défaut est une affirmation : « sous le seuil » écrit faute de mieux
a dit une chose fausse pendant un pas entier, sans que personne la lise.*

## Pas 54 — La liasse dit pourquoi l'abattement figure, ou pourquoi il manque

### Pourquoi

Le pas 46 avait fait du droit à l'abattement CGA un constat, rendu dans la liasse avec son
motif, et sa docstring le disait : « une déduction qui apparaît ou disparaît sans
explication fait croire à une erreur de calcul, et le réviseur la corrigerait en sens
inverse ».

L'écran de la liasse **n'affichait pas ce motif**. Le type `Liasse` du frontend ignorait
le champ `droit_cga`, que la route rendait depuis huit pas.

### Le cas muet trouvé en lisant le calcul

Avant d'afficher, il fallait savoir ce qu'afficher. `_abattement_cga` écarte l'abattement
dans trois situations, et une seule était expliquée :

| Situation | Droit | Abattement | Explication avant ce pas |
| --- | --- | --- | --- |
| Pas d'adhésion sur tout l'exercice, ou chiffre au-delà du seuil | fermé | absent | le motif du droit |
| Résultat nul ou déficitaire après réintégrations | **ouvert** | absent | **aucune** |
| Taux `ABATTEMENT_CGA_BENEFICE` absent du référentiel | **ouvert** | absent | **aucune** |

Dans les deux derniers cas, la liasse rendait un droit ouvert, un motif « adhésion sur tout
l'exercice, chiffre d'affaires sous le seuil », et pas d'abattement. C'est exactement
l'apparence d'un oubli.

⚠️ **S'abstenir reste juste** dans les deux cas : un abattement sur un déficit augmente le
report déficitaire, et un taux supposé serait une valeur légale inventée. Ce qui manquait
n'était pas la règle, c'était sa phrase.

### Ce qui a été fait

**Backend.** `_abattement_cga` rend désormais la ligne **ou** le motif de l'écart :
`(ligne, None)`, `(None, motif)` quand le droit est ouvert, `(None, None)` quand le droit
est fermé, puisque son propre motif l'explique déjà. `PassageFiscal.abattement_cga_ecarte`
le porte, et la liasse le rend.

Relevé en passant : la docstring de `etablir_le_passage` disait « ce paramètre s'appelait
`droit_a_l_abattement_cga` », c'est-à-dire son nom actuel. Il s'appelait
`adherent_sur_l_exercice`. Corrigé.

**Frontend.** Le type `Liasse` reçoit `droit_cga` et `abattement_cga_ecarte`. Sous le
résultat fiscal, une ligne dit l'un des trois cas, chacun avec son intitulé : « Abattement
CGA accordé », « Pas d'abattement CGA », « Droit à l'abattement CGA ouvert, abattement
écarté ». Les phrases viennent toutes du backend.

L'état vide du tableau de passage disait « aucun abattement applicable » : il ne le
prétend plus, la ligne du droit l'explique.

Le commentaire de l'écran affirmait que la clôture n'existait pas côté backend. Vrai à son
écriture, faux depuis le pas 43. Réécrit : la route existe, aucun écran ne l'offre, et une
clôture n'est pas un dépôt de DSF.

### Les épreuves

- Trois cas de domaine : le déficit se dit, le taux absent se dit, et **rien ne se dit**
  quand l'abattement figure ou que le droit est fermé (la contre-épreuve : un motif écrit
  dans tous les cas ne dirait rien).
- Deux cas par la route sur PostgreSQL : un déficit avec droit ouvert rend son motif, un
  droit fermé n'en rend pas.
- Cinq mutations, toutes tuées par une assertion : motif du déficit supprimé, motif du taux
  supprimé, motif écrit sur droit fermé, champ non transmis par la route, champ non porté
  par le passage.

### L'essai réel

Backend en mémoire, site en production locale, réviseur connecté.

| Dossier | Ce que l'écran a rendu |
| --- | --- |
| Les deux dossiers de démonstration, tels quels | « Droit à l'abattement CGA ouvert, abattement écarté : résultat nul ou déficitaire… » |
| Un dossier avec 20 millions de ventes ajoutés | « Abattement CGA accordé : adhésion sur tout l'exercice, chiffre d'affaires sous le seuil d'adhésion. » |
| Un dossier avec 150 millions de ventes | « Pas d'abattement CGA : chiffre d'affaires de 150 000 000 FCFA au-delà du seuil d'adhésion de 100 000 000 FCFA (CGI art. 118)… » |

⚠️ **La première ligne est la plus parlante.** Les dossiers de démonstration sont
déficitaires sur 2026. Chaque liasse montrée au cabinet présentait donc le cas muet : un
droit ouvert, et pas d'abattement, sans un mot.

### État à la fin du pas 54

**2 866 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de
production. 43 routes appelées par le frontend sur 130, inchangé : la liasse était déjà
lue, elle était mal lue.

**Ce que le projet sait faire qu'il ne savait pas.** Dire, sur la liasse, pourquoi
l'impôt de l'adhérent bénéficie ou non de l'abattement du Centre, dans chacun des trois
cas.

*Une route qui rend un champ que l'écran ignore ne compte pas dans la couverture des
écrans, et c'est pourtant une capacité perdue : la mesure par routes ne voit pas les
champs.*

## Pas 55 — Un bouton de clôture, et l'exercice qu'on pouvait fermer en septembre

### Pourquoi

La clôture d'exercice existe côté backend depuis le pas 43 : elle arrête les comptes,
passe les à-nouveaux et ouvre l'exercice suivant. Aucun écran ne l'offrait. Le pas 54 l'a
noté en réécrivant le commentaire de l'écran de la liasse.

### Le défaut trouvé avant d'écrire une ligne d'écran

L'écran de la liasse s'ouvre par défaut sur **l'année en cours**. Avant d'y poser un
bouton, il fallait savoir ce qu'il ferait sur cet exercice-là. La liste des obstacles de la
clôture compte neuf causes ; **aucune ne vérifiait que l'exercice est terminé**.

Le 14 septembre 2026, un réviseur pouvait donc clore 2026. Conséquences, toutes
définitives :

- l'exercice 2026 fermé ne reçoit plus d'écriture ;
- les opérations de fin septembre à décembre n'ont nulle part où aller, puisque 2027 s'ouvre
  le 1er janvier et refuse leurs dates ;
- et le produit ne sait pas rouvrir un exercice clos, délibérément.

Le premier clic sur le bouton, tel qu'il se serait présenté, aurait fait perdre trois mois
et demi à un dossier.

⚠️ **Les cas par la route s'appuyaient sur le défaut.** Écrits en 2026, ils closaient 2026
à la date du jour, et passaient parce que la route l'acceptait. Aucun ne mesurait l'instant.

### Ce qui a été fait, backend

- `MotifEmpechement.EXERCICE_NON_TERMINE` : la clôture est refusée tant que la date du jour
  n'est pas **postérieure** à la date de clôture. Le dernier jour aussi est refusé : ses
  opérations ne sont pas toutes passées. La phrase donne la première date possible.
- L'instant est reçu par le cas d'usage, jamais lu : la route le lit sur l'horloge.
- Les cas par la route se jouent désormais le 15 janvier 2027, par `horloge_figee`, avec
  leur raison écrite. Un cas nouveau joue la route le 14 septembre 2026 : refus, 2026 reste
  ouvert, 2027 n'est pas créé.
- Cas de domaine : en septembre et le 31 décembre à 23 h 59, refusé ; le 1er janvier,
  possible (la contre-épreuve, à la borne) ; appliquer en cours d'exercice n'écrit rien.
- Quatre mutations tuées : garde supprimée, dernier jour admis, lendemain refusé, première
  date possible fausse.

### Ce qui a été fait, frontend

**Un panneau « Clôture de l'exercice »**, en dernier sur l'écran de la liasse : on arrête
des comptes qu'on vient de lire. Il n'apparaît que pour `CLOTURER_EXERCICE`. Sur un exercice
déjà clos, il le dit et ne propose rien ; l'état se lit au portefeuille
(`/portefeuille/entreprises/{niu}/statuts`), à la date de clôture.

**Deux temps, comme la route.**

1. Le réviseur écrit son motif et **contrôle** : rien n'est écrit. Le rapport rend tous les
   obstacles d'un coup, avec leurs phrases et ce qui est en cause, ou ce que la clôture fera :
   le résultat porté au compte 13, le nombre de lignes d'à-nouveau, l'exercice suivant, et s'il
   sera ouvert par la clôture elle-même.
2. Si la clôture est possible, un second formulaire renvoie **le motif contrôlé**, pas un texte
   retouché entre-temps, avec une case de confirmation : l'exercice ne se rouvre pas, et la
   DSF n'est pas déposée pour autant. La case est vérifiée par l'action serveur, pas seulement
   par le navigateur.

⚠️ **Le second temps ne fait pas confiance au premier.** Entre le contrôle et l'application,
un collègue peut saisir un brouillon ; le backend rejoue tous les obstacles, et l'écran
affiche le rapport refusé tel quel.

Le message de réussite nomme l'écriture d'à-nouveau, l'exercice ouvert, et rappelle que la
déclaration reste à déposer.

### L'essai réel

Site en production locale, backend en mémoire.

| Essai | Résultat |
| --- | --- |
| Comptable sur la liasse | aucun panneau de clôture |
| Réviseur, horloge réelle (14/09/2026), contrôle | refus : « l'exercice 2026 se termine le 31/12/2026… Première date possible : le 01/01/2027 » |
| Réviseur, backend daté du 15/01/2027, motif « RAS » | refus lisible de l'écran |
| Contrôle | possible, résultat −4 570 650, 3 lignes, 2027 à ouvrir |
| Application sans la case | refus : « un exercice clos ne se rouvre pas » |
| Application confirmée | clos, à-nouveau `2027/AN/000001`, 2027 ouvert |
| Page rechargée | « Exercice clos », plus de bouton |

### État à la fin du pas 55

**2 875 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de
production. **45 routes appelées par le frontend sur 130** (35 %).

**Ce que le projet sait faire qu'il ne savait pas.** Clore un exercice depuis l'écran, en
voyant d'abord ce que la clôture fera, et ne plus pouvoir clore un exercice qui court encore.

*Un geste irréversible se contrôle au moment de le rendre accessible : tant que personne ne
pouvait cliquer, personne n'avait regardé ce que le clic ferait aujourd'hui.*

## Pas 56 — La CNPS que personne ne voyait

### Pourquoi

L'écran des obligations portait un avertissement : « le contexte G · Social n'existe pas…
l'échéancier est ici calculé sans salariés ». Relevé dès le pas 52 comme périmé, puisque ce
contexte existe avec ses routes. En le vérifiant, la question n'était pas le commentaire,
c'était ce qu'il cachait.

### Ce que la mesure a montré

Le catalogue des obligations désigne la CNPS comme **le piège le plus coûteux du métier** :
l'impôt libératoire n'efface pas les cotisations sociales, et un adhérent au synthétique se
découvre débiteur de plusieurs années. `TypeObligation.concerne` le code avec soin.

Et pourtant :

| Site qui calcule un échéancier | Présence de salariés |
| --- | --- |
| Route de l'échéancier | paramètre de requête, **faux par défaut**, envoyé par aucun écran |
| Route des relances | non acceptée : faux |
| Dossier de TVA | non acceptée : faux |
| Tableau de bord du pilotage | non acceptée : faux |

**La CNPS et les retenues sur salaires n'apparaissaient donc jamais**, ni à l'échéancier, ni
aux relances, ni au pilotage. Aucun retard social n'a jamais été compté.

La cause est écrite dans les contrats du social : « F · Obligations ne lit **pas** ce contexte,
et c'est structurant… le graphe de dépendances gagnerait une arête qui ne sert qu'à répondre
par oui ou non ». Éviter une arête avait coûté l'obligation elle-même.

### Le second défaut, trouvé en écrivant la réponse

`Contrat.couvre_la_periode`, qui décide si un contrat compte dans un mois pour le DIPE et la
paie, testait **le premier et le dernier jour du mois**. Un contrat du 10 au 20 mars ne
couvre ni l'un ni l'autre : mesuré, il rendait `False`. Le saisonnier et le remplaçant, qui
sont exactement ce contrat-là, disparaissaient du DIPE et de la paie de leur mois.

### Ce qui a été fait

**Social.**

- `Contrat.couvre_l_intervalle(du, au_inclus)` : le chevauchement réel, sur la convention
  `[debut, fin[`. `couvre_la_periode` s'appuie dessus.
- `a_employe_sur(contrats, du, au_inclus)` : la seule question que les obligations posent.
- Le choix des dépôts sort des routes vers `adaptateurs/sortant/magasins.py`
  (`depots_du_social`), exporté par l'`api` : l'échéancier doit lire **le même** personnel que
  celui que les routes du social écrivent, sans quoi le défaut du pas 52 revenait.

**Obligations.**

- `generer_echeancier(..., emploie_sur)` remplace `a_des_salaries: bool = False`. **Sans valeur
  par défaut** : un appelant qui oublie la question ne compile plus. C'est la correction de la
  classe, pas des quatre sites.
- La question est posée **pour chaque période** : une embauche le 20 juin donne la CNPS de juin
  à décembre, pas de janvier. Et seulement aux obligations qui en dépendent : la TVA n'attend
  pas le fichier du personnel.
- `adaptateurs/sortant/effectif.py` lit les contrats du dossier **une fois**, puis répond.
- ⚠️ **Le social qui ne répond pas ne bloque pas les obligations.** La réponse devient `None`,
  l'obligation figure quand même, marquée `effectif_a_confirmer`. Une obligation montrée à tort
  se vérifie ; une obligation omise se paie, avec les majorations.
- Les quatre sites passent la question. Le paramètre de requête `a_des_salaries` n'existe plus ;
  l'envoyer n'a aucun effet.

**Registre.** L'arête `obligations → social` est déclarée, avec sa raison, sur le modèle de
`souscription → portefeuille` : une seule question.

**Frontend.** L'avertissement périmé de l'écran des obligations est remplacé ; une obligation
« à confirmer » le dit sous son libellé.

> **Rectificatif, pas 61.** Faux en partie : seul le commentaire du code a été remplacé. Le
> bandeau visible de l'écran disait toujours « le contexte Social n'existe pas encore », au-dessus
> des douze CNPS que ce pas venait de faire apparaître. Voir le pas 61.

### Le cas qui attendait ce jour

`test_le_graphe_d_aujourd_hui_est_plat` constatait qu'aucun service n'avait de dépendance
indirecte seule, et qu'une mutation remplaçant la fermeture transitive par les voisins directs
survivait donc sans effet. Il était écrit « pour se signaler le jour où il cessera d'être vrai ».

**C'est tombé.** La Clôture lit les Obligations, qui lisent désormais le Social : la Clôture
dépend du Social sans arête directe. Le cas est réécrit sur le nouveau constat, et un second
éprouve la fermeture sur le graphe réel : la mutation « voisins directs », qui survivait, est
maintenant tuée.

⚠️ Limite écrite : le registre ne distingue pas une arête qui **dégrade** d'une arête qui **fait
tomber**. Il déclare la Clôture et les Obligations touchées par l'arrêt du Social, alors que la
lecture est tolérante. C'est le bon sens de l'erreur pour un exploitant, et une nuance que le
registre ne sait pas encore porter.

### Les épreuves

- Social : le contrat du 10 au 20 compte dans son mois ; les quatre bornes du mois ;
  `a_employe_sur` sur plusieurs contrats et sur aucun.
- Obligations : période par période (embauche le 20 juin, et le mois entier est bien demandé) ;
  personnel muet, CNPS à confirmer et TVA intacte ; la TVA n'interroge pas le personnel.
- Panne du social simulée : la question rend `None`.
- Par les routes, sur PostgreSQL : un employeur a 12 CNPS ; un dossier sans personnel n'en a
  aucune ; l'ancien paramètre n'a plus d'effet ; **une embauche par la route du social, contrat
  du 10 au 20 octobre, fait naître la CNPS d'octobre et d'octobre seulement** ; les relances du
  13 octobre portent la CNPS de l'employeur et pas celle du dossier sans personnel.
- Pilotage : le 17 août, « CNPS 07/2026 » figure au retard déclaratif de l'employeur. Ce cas est
  né d'une mutation survivante : le pilotage privé de la question ne cassait rien.
- Mutations tuées : l'ancien test des bornes, fin incluse, dernier jour exclu, inconnu omis,
  marque absente, question posée sur l'exercice entier, question posée à la TVA, relances sans
  personnel, pilotage sans personnel, panne traitée comme « pas de salariés », voisins directs
  dans le registre.

### L'essai réel

Écran des obligations, backend en mémoire, réviseur connecté : les deux employeurs de la
démonstration ont désormais 12 CNPS et 12 retenues sur salaires sur 2026 ; le dossier sans
personnel n'en a aucune.

⚠️ La CNPS de janvier s'affiche avec **211 jours de retard** : la démonstration n'enregistre
aucun dépôt. C'est ce que l'écran aurait dû montrer au cabinet depuis le premier jour.

### État à la fin du pas 56

**2 894 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de
production. 45 routes appelées par le frontend sur 130, inchangé : aucune route nouvelle,
mais trois routes et un tableau de bord qui disent enfin la vérité sur les cotisations.

**Ce que le projet sait faire qu'il ne savait pas.** Voir, relancer et compter les
obligations sociales d'un employeur, mois par mois, y compris pour le saisonnier d'une
semaine.

*Une dépendance évitée n'est pas une dépendance supprimée : la question reste posée, et si
personne n'y répond, c'est la valeur par défaut qui répond à sa place.*

## Pas 57 — Admettre et résilier depuis le portefeuille

### Pourquoi

L'adhésion est l'objet même d'un centre de gestion agréé. Le backend sait l'inscrire et la
résilier depuis le pas 48, avec ses règles : jamais antidatée, numérotée par le registre,
refusée au-delà du seuil de l'article 118, jamais résiliée à travers un exercice clos. Aucun
écran ne le permettait.

### Relire la règle avant d'exposer le geste

La leçon du pas 55 : un geste qui devient cliquable se contrôle à ce moment-là. Relue, la règle
tient : antidate refusée contre l'horloge de la route, chevauchement refusé, numéro attribué,
exercice clos protégé.

**Ce qui manquait n'était pas dans le domaine, mais dans ce que l'écran pouvait savoir.** La
liste du portefeuille rendait « adhérente : oui ou non » à la date du jour. Deux situations y
étaient indiscernables :

| Situation réelle | Ce que la liste disait | Ce que l'écran aurait proposé |
| --- | --- | --- |
| Adhésion en cours, **déjà résiliée** pour dans dix jours | adhérente | « Résilier », refusé : rien à résilier |
| Adhésion **à venir**, déjà inscrite pour dans dix jours | non adhérente | « Admettre », refusé : chevauchement |

### Ce qui a été fait

**Backend.** La ligne du portefeuille porte `adhesion_jusqu_au` (la fin déjà inscrite de
l'adhésion en cours, borne exclue) et `adhesion_a_venir` (la plus proche prise d'effet future).
Cas par la route, puis cas directs sur la résolution de la ligne, nés de deux mutations
survivantes : une adhésion qui commence **le jour même** est en cours et non à venir, et c'est
la **plus proche** des adhésions à venir qui est dite.

**Frontend.** La colonne Adhésion du portefeuille, pour `INSCRIRE_STATUT`, propose le seul
geste que le dossier admet :

| État | Affichage | Geste |
| --- | --- | --- |
| Adhérent, rien de résilié | « En cours », numéro | Résilier |
| Adhérent, fin inscrite | « plus adhérent le … » | aucun |
| Adhésion à venir | « adhérent à compter du … » ou « nouvelle adhésion le … » | aucun |
| Non adhérent | « Non » | Admettre |

- **Admettre** : date d'effet proposée à aujourd'hui, jamais avant ; chiffre d'affaires déclaré
  et sa source ; justification. Le formulaire dit avant l'envoi les deux vérités qui surprennent :
  pas d'antidate, et une adhésion prise en cours d'exercice n'ouvre pas l'abattement CGA de cet
  exercice (Q17).
- **Résilier** : **aucune date proposée**, elle se prend sur la lettre reçue, pas sur le jour où
  l'on remplit le formulaire ; justification ; rappel que la veille reste couverte et qu'un
  exercice clos ne se traverse pas.
- Une réadhésion déjà inscrite s'affiche aussi sur un dossier encore adhérent : sinon « plus
  adhérent le 24/09 » se lit comme un départ. Deux contrats jointifs restent deux contrats, et
  l'abattement de l'exercice en dépend (pas 46). Ce détail est venu de l'essai réel.

### L'essai réel

Site en production locale, backend en mémoire, actions serveur appelées comme le navigateur les
appelle.

| Essai | Résultat |
| --- | --- |
| Page, réviseur | six « Résilier », aucun « Admettre » : tous les dossiers de démonstration sont adhérents |
| Page, comptable | aucun geste |
| Comptable appelant l'action directement | « Action non permise : INSCRIRE_STATUT est requise » |
| Justification de cinq caractères | refus de l'écran |
| Résiliation au 01/06/2024 | refus du domaine : exercices clos 2024, 2025 |
| Résiliation dans dix jours | inscrite ; la ligne dit « plus adhérent le 24/09/2026 » et ne propose plus rien |
| Admission antidatée d'un jour | refus : « ne prend pas effet avant le jour de son inscription » |
| Admission à 150 millions | refus : CGI art. 118 |
| Admission dans dix jours, « 62 000 000 » avec espaces | inscrite ; la ligne ajoute « nouvelle adhésion le 24/09/2026 » |

Au passage, pour les essais : dans une requête d'action serveur, **les champs du formulaire
doivent précéder la racine `0`**. Dans l'ordre inverse, le décodage rend un formulaire vide, et
l'action répond « Dossier non désigné » sans que rien ne soit faux dans le code.

### État à la fin du pas 57

**2 897 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de
production. **47 routes appelées par le frontend sur 130** (36 %).

**Ce que le projet sait faire qu'il ne savait pas.** Admettre un dossier au Centre et résilier
son adhésion depuis l'écran du portefeuille, sans jamais proposer un geste que le dossier
refuse.

*Un écran qui propose un geste que le domaine refuse n'est pas protégé par le refus : il apprend
à cliquer pour voir.*

## Pas 58 — La déclaration déposée qu'on relançait encore

### Pourquoi

Le pas 56 a rendu la CNPS visible, avec « 211 jours de retard » en janvier sur la démonstration.
La question suivante allait de soi : **comment une obligation cesse-t-elle d'être en retard ?**

### Ce que la sonde a mesuré

L'échéancier ne se stocke pas : il se recalcule à chaque lecture, et chaque obligation naît
« à faire ». Le port `DepotObligations` existe, sans aucune réalisation. L'accusé d'un dépôt est
consigné au registre du portail, que l'échéancier ne lisait pas.

Une sonde a joué le parcours complet de la TVA de juillet par les routes (second facteur,
préparation, constat de l'accusé, 200), puis relu :

| Lecture | Résultat, déclaration déposée |
| --- | --- |
| Échéancier au 20 septembre | `('A_FAIRE', True)` : à faire, **en retard** |
| Relances du 16 août | `('TVA', '2026-07-31', 1)` : **la relance J+1 part** |

La relance J+1 est celle que le catalogue décrit comme « le jour où la pénalité commence à
courir ». **Le produit relançait un adhérent pour une déclaration qu'il avait déposée**, et le
tableau de bord de la direction comptait le retard dans son score.

### Ce qui a été fait

**Transverse.** `reference_de_depot(entreprise, code, debut, fin)` : l'identité d'un dépôt,
calculable sans préparer de document. Elle sort de `DocumentATransmettre.reference`, qui
l'emploie désormais : une seconde formule divergerait, et chaque déclaration redeviendrait « en
retard ». `tous()` est déclaré au port du portail ; les deux réalisations l'avaient.

**Obligations.** `generer_echeancier(..., accuse_de)` : **obligatoire, sans valeur par défaut**,
comme `emploie_sur` au pas 56. Une obligation dont l'accusé existe est **déclarée à la date de
l'accusé**, avec son numéro : les mêmes champs que le constat de dépôt, jamais la date de lecture.

`adaptateurs/sortant/accuses.py` lit tous les accusés du locataire **une fois** et les indexe par
référence. ⚠️ **Pas de repli silencieux**, contrairement au personnel : une réponse inventée serait
fausse dans les deux sens, relancer des adhérents à jour ou taire des retards réels.

Les quatre sites passent la question : échéancier, relances (une lecture pour tout le
portefeuille), dossier de TVA, pilotage.

### Un contrôle qui ne pouvait jamais parler

La recevabilité d'un dépôt refuse une obligation « portant déjà sa date de dépôt »
(`OBLIGATION-DEJA-DECLAREE`). L'échéancier naissant toujours « à faire », ce contrôle ne se
déclenchait par **aucune** route : seul le refus de l'accusé existant protégeait du double dépôt.
Il se déclenche maintenant. Le cas qui le prouve est né d'une mutation survivante, qui retirait les
accusés au dossier de TVA sans rien casser.

### Les épreuves

- Domaine : l'obligation déposée est déclarée à la date de l'accusé, avec son numéro, et n'est plus
  en retard ; un accusé de juillet ne dépose ni août ni la CNPS de juillet ; sans accusé, l'obligation
  échue reste en retard.
- Par les routes, dans l'application entière : avant le dépôt, en retard et relancée (la
  contre-épreuve) ; après, déclarée à l'échéancier, aucune relance, retard absent du pilotage ; et
  les deux blocages présents au dossier de TVA.
- Mutations tuées : accusé ignoré, référence construite sur l'exercice, date de la période au lieu
  de celle de l'accusé, portail muet, relances, pilotage, échéancier et dossier de TVA privés des
  accusés.

### L'essai réel

Écran des obligations, backend en mémoire : la TVA de juillet affichait « 30 j de retard · En
retard ». Dépôt par la route, second facteur compris. La même ligne affiche « Déclarée ».

### Ce qui reste, et c'est le pas suivant

**Seule la TVA a une route de dépôt.** La CNPS, les retenues sur salaires, l'IGS, la DSF et la
patente n'en ont aucune : ces obligations resteront « en retard » quoi qu'il arrive, maintenant
qu'elles sont visibles. Le pas 58 rend juste ce qui se dépose ; il ne donne pas encore le moyen de
constater le reste.

### État à la fin du pas 58

**2 906 tests passent** sur PostgreSQL réel. Aucun écran modifié : l'écran des obligations
affichait déjà le statut rendu, il rendait un statut faux. 47 routes appelées par le frontend
sur 130.

**Ce que le projet sait faire qu'il ne savait pas.** Cesser de relancer, et de compter en
retard, une déclaration de TVA déposée.

*Un calcul refait à chaque lecture oublie tout ce qui s'est passé entre deux lectures, sauf ce
qu'on lui demande explicitement de relire.*

## Pas 59 — Constater le dépôt de ce qui n'est pas la TVA

### Pourquoi

Le pas 58 fait reconnaître un dépôt dès que son accusé existe. Seule la TVA savait consigner
le sien. La CNPS, les retenues sur salaires, l'IGS, la DSF et la patente restaient donc « en
retard » quoi qu'il arrive, et la CNPS était relancée chaque jour depuis qu'elle est visible.

### Le second obstacle, dans le registre

Le registre des accusés de l'atelier est une seule instance, créée pour le guichet de la DGI,
et il refusait tout accusé dont le guichet n'était pas **le sien** : « Un accusé CNPS ne prouve
rien devant la DGI ». La garde avait raison sur le fond, et se trompait d'appui. Même s'il avait
existé une route, **aucun accusé CNPS n'aurait pu être consigné**.

Le document à transmettre porte déjà son guichet. Le contrôle compare désormais l'accusé au
**guichet du document**, en mémoire comme en base : le registre tient les accusés du locataire
pour tous ses guichets, et un accusé CNPS ne s'attache toujours pas à une déclaration DGI.

### Ce qui a été fait

**Catalogue.** `TypeObligation.portail`, **sans valeur par défaut** : un défaut « DGI » aurait
consigné une cotisation sociale au mauvais guichet sans que rien ne le signale. CNPS au guichet
CNPS ; retenues sur salaires rattachées à la DGI **sous réserve** (question Q20, le DIPE réunissant
retenues et cotisations) ; les autres à la DGI.

**Cas d'usage.** `constater_un_depot_hors_tva` consigne l'accusé d'une obligation déposée hors de
la plateforme, la fait passer à déclarée et l'écrit au journal d'audit. Il refuse :

| Cas | Pourquoi |
| --- | --- |
| La TVA | elle a son parcours, qui contrôle la recevabilité ; le constater ici la contournerait |
| Une obligation déjà déclarée | un second accusé ferait croire à une rectificative |
| Un dépôt daté de l'avenir | on ne consigne pas ce qui n'a pas eu lieu |
| Un dépôt au plus tard le dernier jour de la période | une déclaration porte sur une période écoulée ; sauf obligation payable d'avance, comme la patente |

⚠️ **Ce que ce constat ne prouve pas.** Le dépôt de TVA confronte l'accusé à un bordereau préparé :
les chiffres déposés sont ceux que la plateforme a calculés. Ici **aucun bordereau n'existe**. Le
document consigné est le constat lui-même, et son empreinte prouve ce que le réviseur a déclaré, pas
ce que le guichet a reçu. Sans pièce jointe, l'accusé le dit par `verifiable`.

**Route.** `POST /obligations/dossiers/{entreprise}/depots`, sous `DEPOSER_DECLARATION` et second
facteur. Le corps refuse tout champ en trop, dont le guichet. **L'obligation est retrouvée à
l'échéancier, jamais reçue** : la CNPS d'un dossier sans salariés répond `404`, avec les périodes qui
existent.

### Les épreuves

- Registre : un accusé CNPS se consigne sur un document CNPS dans le registre créé pour la DGI ; un
  accusé CNPS ne s'attache toujours pas à un document DGI.
- Par la route : avant le constat, la CNPS de juillet est en retard ; après, déclarée à la date de
  l'accusé, au guichet CNPS, non vérifiable, sans relance J+1. La patente se constate pendant sa
  période.
- Refus : TVA, second constat, dépôt en cours de période, le dernier jour, dans l'avenir, obligation
  absente de l'échéancier, guichet fourni par l'appelant, sans second facteur, comptable.
- Sur PostgreSQL : constat persistant, relu déclaré, second refusé.
- Dix mutations tuées, dont les deux registres remis sur leur propre guichet et la CNPS rangée au
  guichet de la DGI.

### Ce qui n'est pas fait

**Aucun écran.** Le frontend ne connaît pas le parcours du second facteur : il ne fait que lire la
préparation du dépôt de TVA. Un bouton « constater » s'y heurterait à un refus que l'écran ne saurait
pas lever. L'écran viendra avec ce parcours.

### État à la fin du pas 59

**2 921 tests passent** sur PostgreSQL réel. Aucun écran modifié. 131 routes au backend
(une de plus), sur 124 chemins ; 41 corps de requête ; 47 routes appelées par le frontend.

**Ce que le projet sait faire qu'il ne savait pas.** Faire cesser le retard d'une CNPS, d'une
DSF ou d'une patente déposée hors de la plateforme, au bon guichet, en disant ce que ce constat
ne prouve pas.

*Une garde juste posée sur le mauvais appui ne se voit pas tant que personne ne passe par là :
elle refusait une porte qui n'existait pas encore.*

## Pas 60 — Le second facteur qui tombait devant le mot de passe

### Pourquoi

Le pas 59 a laissé le constat des dépôts sans écran, faute de parcours de second facteur au
frontend. Avant d'exposer ce parcours, il fallait relire ce que le backend fait de
l'enrôlement.

### La faille

`POST /transverse/second-facteur` engendrait un secret, **écrasait celui du compte**, et rendait le
nouveau. Aucune condition, sinon d'être connecté. Le scénario :

1. l'intrus connaît le mot de passe d'un réviseur, ou vole sa session ;
2. il appelle l'enrôlement : le secret du réviseur est remplacé par un secret que l'intrus détient ;
3. il renforce la session avec un code de son propre appareil ;
4. il dépose des déclarations, qui sont les actes pour lesquels le second facteur existe.

**Le second facteur tombait devant le premier.** Et le vrai titulaire perdait le sien sans rien
savoir, jusqu'au jour où ses codes étaient refusés.

Le code le justifiait : « Le réenrôlement est permis et journalisé : un téléphone se perd, et le
remplacer ne doit pas exiger la création d'un nouveau compte. Ce qui protège, c'est que l'acte
laisse une trace datée, pas qu'il soit impossible. » La trace arrivait après les dégâts.

### Ce qui a été fait

| Situation | Avant | Désormais |
| --- | --- | --- |
| Premier enrôlement | la session suffit | la session suffit, **et le titulaire est prévenu par courriel** |
| Remplacement | la session suffit | **session renforcée par un code de l'appareil actuel**, sinon `409` sans secret |
| Appareil perdu | le titulaire se ré-enrôlait | **un tiers habilité** réinitialise, avec motif |

**La réinitialisation** (`POST /transverse/comptes/{identifiant}/second-facteur/reinitialisation`,
`GERER_COMPTES`, motif de trente caractères) :

- ⚠️ **jamais sur son propre compte** : un administrateur dont le mot de passe a fui retirerait
  sinon son facteur, puis en enrôlerait un nouveau ;
- ⚠️ **ferme toutes les sessions du titulaire** : une session renforcée ouverte sur l'appareil perdu
  déposerait encore quinze minutes ;
- prévient le titulaire par courriel ;
- **n'enrôle rien à sa place** : qui détiendrait le secret d'un autre détiendrait son second facteur.

Deux gabarits de courriel, déclarés avec leur contexte d'appel, comme le veut le contrôle des
gabarits. Le tableau des actions sensibles de `05-securite-multitenant.md` porte les deux gestes, et
la limite restante.

### La limite qui reste, écrite

Un compte **jamais enrôlé** s'enrôle avec sa session : qui a le mot de passe d'un réviseur qui n'a pas
encore enrôlé peut le faire à sa place. Le courriel au titulaire est aujourd'hui la seule parade.
Enrôler à l'activation du compte la fermerait.

### Les épreuves

- **Le scénario de la faille, joué jusqu'au dépôt** : l'intrus reçoit `409` et aucun secret, son dépôt
  est refusé, et le secret du titulaire fonctionne toujours (la contre-épreuve).
- Premier enrôlement accepté et notifié ; remplacement accepté sous session renforcée, l'ancien
  appareil ne vaut plus.
- Réinitialisation : sessions fermées (la session renforcée du titulaire rend `401`), titulaire
  prévenu, nouvel enrôlement possible ; refus sur son propre compte, sans facteur, sans permission,
  motif court.
- Sur PostgreSQL, secret scellé en base : remplacement refusé et secret intact, réinitialisation
  persistante.
- Mutations tuées : garde retirée (la faille elle-même), remplacement impossible même renforcé,
  premier enrôlement bloqué, route qui croit la session renforcée, son propre compte admis, sessions
  non révoquées, notification envoyée à personne.

### État à la fin du pas 60

**2 931 tests passent** sur PostgreSQL réel. 132 routes sur 125 chemins, 42 corps de requête,
28 routes sans permission (inchangé). Aucun écran modifié : le parcours de second facteur au
frontend est le pas suivant, et il se construit maintenant sur une règle qui tient.

**Ce que le projet sait faire qu'il ne savait pas.** Résister à un mot de passe volé pour les
actes qui exigent le second facteur, et remplacer l'appareil perdu d'un collaborateur sans rouvrir
la faille.

*Une mesure de sécurité se juge contre ce qu'elle doit arrêter : un second facteur qu'on remplace
avec le premier n'arrête rien de ce qui le justifie.*

## Pas 61 — Le second facteur à l'écran, le constat de dépôt, et un bandeau qui mentait

### Pourquoi

Le pas 59 a laissé le constat des dépôts hors TVA sans écran : le frontend ne connaissait pas le
parcours du second facteur. Le pas 60 a fermé la faille qui rendait ce facteur contournable. Le
parcours pouvait maintenant se construire sur une règle qui tient.

### Le bandeau qui mentait, et le rectificatif

En lisant l'écran des obligations pour y poser le constat, le bandeau visible disait encore :
« **Cet échéancier suppose que le dossier n'a pas de salariés.** Le contexte Social n'existe pas
encore… ». Le pas 56 avait corrigé le calcul et le commentaire du code, et son journal affirmait
« l'avertissement périmé est remplacé ». **C'était faux** : l'essai réel de ce pas avait compté les
CNPS dans la page sans relire la phrase au-dessus. L'écran affichait douze cotisations sous une
phrase qui niait leur existence.

Le bandeau est retiré. Il n'en reste qu'un, conditionnel, quand une obligation porte
`effectif_a_confirmer`, c'est-à-dire quand il est vrai. Le pas 56 porte un rectificatif daté plutôt
qu'une réécriture : un journal qu'on corrige en silence ne vaut plus comme journal.

### Ce qui a été fait

**La porte du second facteur** (`PorteSecondFacteur.tsx`), devant tout geste qui l'exige :

| État du compte | Ce que l'écran propose |
| --- | --- |
| Jamais enrôlé | associer une application : la clé s'affiche une fois, par groupes de quatre, avec le lien `otpauth://` ; puis le premier code |
| Enrôlé | un code, et c'est tout |
| Session renforcée | le geste lui-même |

⚠️ **L'écran ne propose jamais de ré-enrôler.** Depuis le pas 60, un compte enrôlé ne remplace pas
son facteur sans code, et un appareil perdu se réinitialise par l'administrateur. Un bouton « nouvel
appareil » inviterait le geste que le backend refuse. Le renforcement revalide toute l'application :
chaque écran relit `facteur_fort` au serveur.

**Le constat de dépôt** (`ConstatDepot.tsx`), en panneau sous l'échéancier, pour
`DEPOSER_DECLARATION` :

- la liste propose les obligations hors TVA non déposées dont la période a commencé. **C'est un
  affichage, pas une règle** : la date impossible, la TVA, l'obligation absente sont refusées par le
  backend, et sa phrase s'affiche ;
- le formulaire dit avant l'envoi qu'aucun bordereau n'est confronté, et que le guichet vient du
  catalogue.

⚠️ **L'heure de Douala.** Le backend horodate en UTC et laisse la conversion à l'affichage. Le
réviseur saisit l'heure portée par l'accusé, à Douala. Envoyée telle quelle, un dépôt fait il y a
moins d'une heure arrivait **une heure dans le futur**, et le backend le refusait comme « postérieur
à maintenant ». L'action convertit, avec le décalage écrit une fois (UTC+1, sans heure d'été).

**La réinitialisation**, sur l'écran des comptes, jusqu'ici en lecture seule « faute de confirmations
explicites ». Elle vient avec la sienne : motif, et une case qui dit que les sessions du titulaire
seront fermées. Le compte connecté ne reçoit pas le bouton. Elle est venue la première parce que,
depuis le pas 60, un appareil perdu n'avait plus d'autre remède.

**Relevé en passant, et corrigé** : le refus d'une TVA au constat affichait le chemin du parcours
dédié en gabarit, `{entreprise}` compris. Il est rendu pour le dossier, et un cas le garde.

### L'essai réel

Site en production locale, backend en mémoire, actions serveur appelées comme le navigateur.

| Essai | Résultat |
| --- | --- |
| Écran des obligations, réviseur | plus de bandeau « Social n'existe pas » ; la porte propose d'associer une application |
| Enrôlement | clé rendue ; courriel au titulaire (pas 60) |
| Code faux | « Code refusé. Vérifier que l'heure du téléphone est à l'heure… » |
| Code juste | « Session renforcée pour quinze minutes » ; la page rechargée montre le formulaire |
| CNPS de juillet, déposée le 12/08 à 10 h 30 | consignée ; la ligne dit « Déclarée » |
| CNPS d'août, **déposée il y a dix minutes, heure de Douala** | consignée : la conversion d'heure tient |
| TVA appelée directement | refusée, chemin du parcours dédié |
| Écran des comptes, administrateur | un seul bouton « Réinitialiser », celui du réviseur enrôlé |
| Réinitialisation | faite ; la session du réviseur est fermée (la page le renvoie à la connexion) |

### État à la fin du pas 61

**2 931 tests passent** sur PostgreSQL réel (le fichier du constat rejoué après la dernière
retouche du message). Frontend : typage, lint, construction de production. **51 routes appelées
par le frontend sur 132** (39 %).

**Ce que le projet sait faire qu'il ne savait pas.** Enrôler et présenter un second facteur depuis
l'écran, consigner le dépôt d'une CNPS ou d'une DSF à l'heure où il a eu lieu, et remédier à un
appareil perdu sans rouvrir la faille.

*Un essai réel qui compte les lignes d'une page sans en relire les phrases prouve le calcul, pas
l'écran.*

## Pas 62 — Le premier enrôlement se prouve par la boîte aux lettres

### Pourquoi

Le pas 60 a écrit sa limite : un compte **jamais enrôlé** s'enrôlait avec sa seule session. Qui
volait le mot de passe d'un réviseur qui n'avait pas encore associé d'application l'enrôlait à sa
place, renforçait la session et déposait. Or ce sont justement les comptes qui n'ont pas encore
enrôlé qu'un attaquant choisit.

### Le défaut trouvé en préparant la correction

La correction passe par un lien reçu par courriel, donc par un nouveau type de jeton. En relisant
`definir_mot_de_passe`, qui consomme les jetons de mot de passe : **il ne vérifiait pas le type du
jeton**. Aujourd'hui sans conséquence, les trois types existants servant tous à définir un mot de
passe. Mais le lien d'enrôlement, ajouté tel quel, aurait aussi **redéfini le mot de passe du compte**,
et donné le compte entier à qui ne devait recevoir qu'une clé. Contrôle ajouté avant le nouveau type.

### Ce qui a été fait

**Backend.**

- `TypeJeton.ENROLEMENT`, valable **trente minutes** : il est demandé depuis une session ouverte, par
  quelqu'un qui attend le courriel devant l'écran.
- `JETONS_DE_MOT_DE_PASSE` : seuls l'activation, la réinitialisation et l'invitation définissent un
  mot de passe.
- `POST /transverse/second-facteur`, pour un compte jamais enrôlé, **ne rend plus de clé** : il émet le
  lien, l'envoie à l'adresse du compte (`compte.second_facteur_confirmation`) et répond
  `confirmation_par_courriel: true`. Pour un compte enrôlé, rien ne change : remplacement sous session
  renforcée (pas 60).
- `POST /transverse/second-facteur/confirmation` consomme le lien et rend la clé, **une fois**. Refusé
  en `410`, avec le message commun des liens : jeton inconnu, expiré, déjà utilisé, d'un autre type,
  ou **d'un autre compte** (le refus ne dit pas à qui il appartenait).
- `enroler_second_facteur(..., lien_confirme=False)` : **le défaut est le refus**. Un premier enrôlement
  sans lien lève `PreuveDeBoiteRequise` ; seule la confirmation passe `True`.
- La route de confirmation rejoint la liste close des routes sans permission, avec son motif ; le
  contrôle de la liste l'a exigé.

**Frontend.**

- La porte du second facteur n'affiche plus de clé : « Associer une application » annonce le lien
  envoyé.
- `/second-facteur/confirmation`, où mène le lien : un bouton « Afficher ma clé », puis la clé et le
  premier code. ⚠️ **Le jeton n'est présenté qu'au clic**, jamais à l'ouverture de la page : les
  messageries professionnelles ouvrent les liens pour les analyser, et un jeton consommé à l'affichage
  l'aurait été par l'antivirus.
- La clé et la saisie du code sont devenues deux composants partagés (`CleEtCode.tsx`).

### Les épreuves

- Le mot de passe seul ne rend aucune clé ; le lien part à l'adresse du compte ; le compte reste non
  enrôlé.
- Le lien d'un autre compte est refusé sans nommer son propriétaire ; il ne sert qu'une fois ; il expire
  après trente minutes (horloge figée) ; il ne redéfinit pas le mot de passe ; un lien « mot de passe
  oublié » ne confirme pas un enrôlement.
- Le cas d'usage refuse par défaut un premier enrôlement sans lien.
- Les tests qui enrôlaient directement passent désormais par le lien retenu (`enroler_par_le_courriel`),
  comme un utilisateur ; le journal d'audit du parcours complet sur PostgreSQL porte l'émission du lien.
- Mutations tuées : premier enrôlement direct à la route, lien d'un autre compte admis, lien d'un autre
  type admis (tuée par un cas ajouté pour elle), lien non consommé, défaut « lien réputé confirmé », lien
  d'enrôlement accepté comme mot de passe, lien valable un jour.

Au passage, une hypothèse de test fausse : « mot de passe oublié » répond `202`, pas `200`. Le code avait
raison, le cas a été corrigé.

### L'essai réel

Backend en mémoire en mode démonstration, pour lire le courriel retenu ; site en production locale.

| Essai | Résultat |
| --- | --- |
| Demande depuis une seconde session du même mot de passe | aucune clé ; « un lien vient d'être envoyé » |
| Courriel retenu | adressé à a.bouba, lien `/second-facteur/confirmation?jeton=…` |
| Ouverture de la page du lien | bouton « Afficher ma clé », aucune clé visible |
| Lien présenté par un autre compte | « Ce lien n'est plus valable » |
| Clic du titulaire | clé rendue (le jeton avait donc survécu à l'ouverture de la page) |
| Second clic | « Ce lien n'est plus valable » |
| Premier code | session renforcée ; le constat de dépôt apparaît sur les obligations |

### État à la fin du pas 62

**2 938 tests passent** sur PostgreSQL réel. 133 routes sur 126 chemins, 43 corps de requête, 29 routes
sans permission (la confirmation, motif inscrit). Frontend : typage, lint, construction de production ;
52 routes appelées sur 133.

**Ce que le projet sait faire qu'il ne savait pas.** Refuser à un mot de passe volé l'enrôlement d'un
compte qui n'en avait pas encore.

*Chaque nouvelle sorte de lien interroge toutes les portes qui consomment des liens : celle du mot de
passe ne regardait pas lesquels elle ouvrait.*

## Pas 63 — Les auteurs qu'on écrivait dans la requête

### Pourquoi

Une mesure des routes sans écran, regroupées par contexte, a désigné le parcours d'acquisition :
**dix-huit routes, aucun écran**. Depuis le pas 51, le formulaire du site y dépose ses demandes ;
aucun collaborateur ne pouvait les voir. Avant de construire la console, la leçon des pas 55 et 60
imposait de relire ce que ces routes acceptent.

### Ce que la relecture a trouvé

**Deux auteurs s'écrivaient dans le corps de la requête.**

| Route | Champ | Ce qu'il permettait |
| --- | --- | --- |
| `POST /acquisition/rappels/{id}/fait` | `par` | écrire qu'un collègue avait appelé le client ; le docstring disait « se nommer est obligatoire : un carnet où l'on peut clore sans nom ne dit plus qui a parlé au client » |
| `POST /acquisition/dossiers/{ref}/proforma` | `valide_par` | écrire « direction » comme validateur du prix. Le contrôle interne lit `chiffre_par != valide_par` pour juger la séparation des tâches : **le contrôle était simulé** |

Pourquoi le contrôle des corps de requête (pas 36) ne les avait pas vus : il compare les noms à une
liste (`depose_par`, `saisie_par`, `validee_par`, `emis_par`), et **aucun des deux n'y était**. Il ne
regardait pas non plus les modèles imbriqués.

Les autres candidats du balayage ont été lus et sont légitimes : `expire_le` à l'acceptation d'une
proforma est scellé dans le lien signé ; `depose_le` d'une pièce est borné et documenté ; les dates
d'obtention d'un RCCM ou d'un accusé sont des faits extérieurs.

### Ce qui a été fait

**Le contrôle d'abord, par la forme et non par le nom.** `test_aucun_auteur_ne_se_declare` : tout champ
`par` ou `*_par`, **à tout niveau d'imbrication**, est un auteur, et aucun corps de requête n'en porte.
Écrit avant la correction, il a échoué sur exactement les deux cas. Une contre-épreuve sur un modèle
fabriqué garantit qu'un détecteur cassé ne passerait pas en silence.

**Les routes ensuite.**

- Rappel : le corps ne porte plus rien et refuse tout champ ; `fait_par` est le compte de la session.
- Proforma : `valide_par` n'est plus reçu, et tout champ inconnu est refusé. Le prix est engagé par le
  compte de la session, le même qui chiffre. ⚠️ **`separation_respectee` vaut donc `False`, et c'est la
  vérité** : aucun geste distinct de validation n'existe. Le contrôle interne le verra, au lieu de lire une
  validation déclarée. La réponse de la proforma rend désormais `chiffre_par`, `valide_par` et
  `separation_respectee`, pour que la console le dise. Une validation par un second collaborateur sera,
  le jour venu, sa propre route sous sa propre session.

### Les épreuves

- Recette du parcours sur PostgreSQL : une proforma envoyée avec `valide_par` est refusée (`422`) ; émise
  sans, elle est chiffrée et engagée par `C-001`, séparation non respectée. Un rappel clos avec `par` est
  refusé ; clos avec `{}`, il porte `C-001`.
- Mutations tuées : `valide_par` remis en dur (tuée seulement une fois la réponse enrichie : elle survivait,
  rien ne montrant ce champ), rappel clos au nom d'un autre, refus des champs inconnus retiré, détecteur
  d'auteurs cassé.

### Ce qui n'est pas fait

**La console d'acquisition elle-même.** Ce pas rend ses routes dignes d'être exposées ; l'écran est le
pas suivant.

### État à la fin du pas 63

**2 940 tests passent** sur PostgreSQL réel. Surface inchangée : 133 routes, 43 corps de requête,
29 routes sans permission. Aucun écran modifié.

**Ce que le projet sait faire qu'il ne savait pas.** Dire qui a vraiment appelé un client et qui a
vraiment engagé le cabinet sur un prix, et refuser qu'une requête l'écrive à sa place.

*Un contrôle qui ment en disant « respecté » coûte plus qu'un contrôle qui dit « non respecté » : le
second appelle une décision, le premier l'empêche.*

## Pas 64 — La console des demandes entrantes

### Pourquoi

Depuis le pas 51, le formulaire du site dépose les demandes des visiteurs dans le parcours
d'acquisition. Aucun écran ne les montrait. Le pas 63 a rendu ses routes sûres ; celui-ci les
expose.

### Relire avant d'exposer, encore

Deux constats, trouvés en jouant les routes en mémoire avant d'écrire l'écran.

**Une réserve fausse dans chaque motif d'affectation.** Le critère de proximité du référentiel
(`AFF-PRX-001`) pénalisait tout candidat quand le visiteur n'avait déclaré aucune région, avec ce
commentaire : « l'effet est nul sur le classement, et c'est voulu ». Le classement était intact.
Mais le motif de **chaque** affectation venue du site, qui ne collecte aucune région, portait
« réserves : Agence différente de la région déclarée ». La console l'aurait affiché partout, et un
responsable aurait lu qu'on avait pesé une région que personne n'avait déclarée.

Corrigé **dans la configuration, pas dans le code** : le prédicat se tait quand la région est vide.
Un test existant s'appuyait sur la présence de cette réserve pour prouver que le message du prospect
n'est pas employé comme région ; son observation s'est inversée (c'est désormais l'absence de réserve
qui le prouve), et une mutation qui réemploie le message comme région le fait bien tomber.

**Des identifiants là où l'on attend des personnes.** La liste des dossiers rendait `responsable:
"C-001"`. Elle rend désormais `responsable_nom`, lu à l'annuaire une fois par requête ; `None` pour une
affectation simulée avec un effectif hypothétique.

### Ce qui a été fait

**La console** `/acquisition`, sous « Demandes entrantes » dans le menu, pour `LIRE_PROSPECT` :

| Panneau | Contenu | Geste |
| --- | --- | --- |
| Rappels à passer | le motif en clair, depuis quand | « J'ai appelé » (`QUALIFIER_PROSPECT`), au nom de la session |
| Ce qui dort | immobilité et délai de l'état, date du signalement | aucun : c'est une alerte |
| Dossiers en cours | prospect, téléphone, service, état, responsable nommé | « Affecter » ou « Réaffecter » (`AFFECTER_DOSSIER`), « Sans suite » avec un motif du vocabulaire (`QUALIFIER_PROSPECT`) |

- L'ordre est celui du backend, qui est l'ordre d'urgence.
- Aucun auteur ne part dans les corps de requête (pas 63).
- Une affectation sans candidat convenable s'affiche comme un fait (« aucun collaborateur ne
  convient »), pas comme une panne : le backend rend `200` avec les empêchements.
- Qualifier, chiffrer, émettre la proforma et encaisser restent sans formulaire ; l'en-tête de la page
  le dit.

### L'essai réel

Backend en mémoire, site en production locale.

| Essai | Résultat |
| --- | --- |
| Trois demandes déposées par la route publique du site | trois dossiers « Déposée » à la console |
| Comptable | pas d'entrée au menu, « Accès réservé » |
| Administrateur, direction | la console |
| Affecter | « Affecté. retenu parmi 2 candidats, aucun critère déclenché » : plus de réserve de proximité |
| Sans suite avec un motif inventé | refus du backend, qui cite les motifs du référentiel |
| Sans suite, motif « injoignable » | « Dossier classé sans suite. Il n'est pas supprimé. » |
| Page rechargée | le dossier affecté affiche « Bernadette MBALLA » et « Réaffecter » ; le dossier classé a quitté la liste |

Le panneau des rappels n'a pas été éprouvé à l'écran : aucun rappel n'existe en démonstration sans
parcours de relance complet. La route, elle, est éprouvée par la recette du parcours (pas 63).

### État à la fin du pas 64

**2 943 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**59 routes appelées par le frontend sur 133** (44 %) : sept routes du parcours d'acquisition ont
maintenant un écran.

**Ce que le projet sait faire qu'il ne savait pas.** Montrer au cabinet les prospects qui lui ont écrit
par le site, les confier à quelqu'un, les rappeler, et clore ceux qui s'arrêtent.

*Un commentaire qui dit « l'effet est nul » parle de ce qu'il mesure ; le texte affiché à un humain est
un autre effet.*

## Pas 65 — Le prix se calcule sur ce que le dossier sait

### Pourquoi

Le pas suivant de la console devait porter la fiche d'un dossier : qualification, chiffrage,
proforma. Relue avant d'être exposée, la chaîne du prix s'est révélée ouverte à la requête.

### Ce que la relecture a trouvé

**Les faits du chiffrage venaient de la requête.** Le modèle le reconnaissait : « la
qualification n'est pas encore persistée ; le jour où sa table existe, la route les lira et ce
corps disparaîtra ». La qualification était persistée depuis un pas antérieur, et personne n'avait
fait disparaître le corps. **La recette elle-même le montrait** : elle qualifiait huit réponses,
dont un capital d'un million et un chiffre d'affaires de 10 à 50 millions, puis chiffrait en
envoyant les deux premières seulement (`forme_juridique`, `associes`). Le capital et le chiffre
d'affaires, qui font le prix, n'entraient pas dans le calcul, et le cas passait.

**L'intervalle de la proforma venait aussi de la requête.** L'émission recevait le plancher, la
référence et le plafond du barème. Or le motif n'est exigé qu'en dehors de cet intervalle :
**un plancher abaissé faisait passer un rabais sans motif**.

**Un dossier non qualifié recevait une proposition chiffrée**, et le docstring affirmait l'inverse
(« chiffrer un dossier qui n'est pas qualifié serait refusé par le domaine ») : la transition
n'était tentée que sur un dossier déjà qualifié, et le calcul se faisait dans tous les cas.

**La proforma émise ne gardait ni les lignes du calcul, ni les débours, ni les faits** : le domaine
avait prévu les trois champs (« les faits de la qualification au moment du chiffrage »), et la route
ne les remplissait jamais.

Au passage : `DemandeDeQualification` affirmait encore dans son docstring, donc dans le schéma
OpenAPI, que la qualification n'était pas persistée.

### Ce qui a été fait

`_proposition_du_dossier`, **une seule fonction pour le chiffrage et pour l'émission** :

- elle lit la qualification **enregistrée** et refuse en `409` si elle est incomplète, en nommant les
  questions qui manquent ; puis elle refuse un dossier qui n'est pas qualifié ;
- elle calcule la proposition sur ces faits ;
- elle rend les faits à conserver, avec le score de charge déclaré à côté.

`DemandeDeChiffrage` ne porte plus que `score_charge` et `debours`, et refuse tout autre champ.
`TarifAArreter` ne porte plus que le montant, le motif, `score_charge` et `debours` : l'intervalle et
la version du barème sont recalculés à l'émission. La proforma conserve lignes, débours et faits, et sa
réponse rend l'intervalle et les faits.

⚠️ **Ce qui reste déclaré : le score de charge.** La matrice de charge existe au portefeuille pour une
entreprise suivie, pas pour un prospect. Le score reste déclaré par le responsable, mais il est conservé
sur la proforma avec les faits : un score minoré se lit sur le document. Question ouverte Q21.

### Les épreuves

- Recette du parcours : un chiffrage qui envoie des faits est refusé (`422`) ; une émission qui déclare un
  plancher est refusée (`422`) ; l'intervalle de la proforma est celui du chiffrage.
- Un dossier à moitié qualifié ne se chiffre pas, et le refus nomme `capital_social`.
- **Le prix suit la réponse enregistrée** : porter le capital à cinquante millions après un premier
  chiffrage fait monter la référence (règle `TAR-CAP-001`). C'est le cas qui aurait vu le défaut.
- Un montant sous le plancher recalculé est refusé sans motif, émis avec ; la proforma garde
  `capital_social` et le score de charge.
- Mutations tuées : faits partiels remis en dur (l'ancien comportement), qualification incomplète admise,
  plancher de l'émission non recalculé, proforma sans faits (tuée une fois la réponse enrichie).

Rectification en cours de pas : j'avais d'abord écrit que la recette chiffrait avec des faits « sans
rapport » avec la qualification. C'étaient les deux premières réponses sur huit. Le docstring et ce journal
disent ce qui était vrai.

### État à la fin du pas 65

**2 946 tests passent** sur PostgreSQL réel. Aucun écran modifié ; 59 routes appelées par le frontend.
La fiche du dossier (qualification, chiffrage, proforma) peut maintenant se construire sur des routes
qui calculent le prix à partir du dossier.

**Ce que le projet sait faire qu'il ne savait pas.** Chiffrer un prospect sur ce qu'on a appris de lui,
et refuser qu'un rabais passe sans motif par un intervalle déclaré.

*Un corps de requête qui devait disparaître « le jour où » disparaît rarement seul : il faut une date,
ou un contrôle qui le cherche.*

## Pas 66 — La fiche du dossier, et la remise accordée à qui n'avait rien dit

### Pourquoi

La console du pas 64 montre les demandes ; il fallait pouvoir travailler un dossier : lire la
demande, qualifier le prospect, chiffrer.

### Ce qu'un premier chiffrage a montré

En jouant les routes avant d'écrire l'écran, une qualification complète sur les huit questions
obligatoires a produit une proposition avec **une remise de 50 000 FCFA, « Statuts apportés par le
client »**, alors qu'aucune réponse n'avait été donnée sur les statuts.

La règle `TAR-STA-001` s'écrit `statuts_apportes == false`, avec la convention du moteur :
**vrai, rien à signaler ; faux, l'ajustement s'applique**. La question est **facultative**. Sans
réponse, le fait est absent, le moteur le lit `None`, `None == false` rend faux : la remise
s'appliquait. **Une information inconnue valait remise.** Le docstring de la qualification promettait
l'inverse : « un prédicat qui les cite le dira par `missing` » ; la règle ne le faisait pas, et rien ne
l'y obligeait.

### Où corriger : pas dans le moteur

Le moteur sert quatre domaines. En conformité, une facture sans NIU doit bien déclencher sa règle : y
traiter un fait absent comme « rien à signaler » ouvrirait une autre faille. **C'est la tarification qui
décide qu'un prix ne se fonde pas sur ce qu'on ignore.**

Dans `chiffrer` : les faits cités par chaque règle sont extraits (`chemins_cites`, déjà employé pour
valider les règles au chargement). Une règle qui cite un fait sans réponse est **écartée**, et la
proposition le dit dans ses échecs : « TAR-STA-001 : sans réponse à « statuts_apportes », ajustement non
appliqué ». Une règle qui cite `missing` traite l'absence elle-même et reste évaluée. Seules les règles
applicables à ce service, à cette date, sont signalées.

Épreuves : sans réponse, pas d'ajustement et un échec nommé ; avec « oui » la remise joue, avec « non »
elle ne joue pas (la règle n'a pas été éteinte) ; une règle en `missing` reste évaluée. Sur le parcours
réel, la remise n'apparaît qu'après la réponse « oui ». Trois mutations tuées : fait absent de nouveau
évalué, règles en `missing` écartées aussi, écart non signalé.

### La fiche

`/acquisition/[reference]`, ouverte depuis le nom du prospect dans la console :

| Panneau | Contenu |
| --- | --- |
| La demande | téléphone, adresse, canal souhaité, message tel qu'écrit, motif de l'affectation |
| Qualification | **engendrée depuis le questionnaire du référentiel** : libellé, type, valeurs admises, unité, aide, caractère obligatoire ; les questions manquantes marquées ; les réponses déjà enregistrées reprises |
| Chiffrage | fermé tant que la qualification est incomplète, avec la liste de ce qui manque ; puis l'intervalle, les lignes, et **les ajustements écartés faute de réponse, présentés comme des questions à poser** |

- Aucune question n'est écrite dans l'écran : ajouter une question au questionnaire l'ajoute à la fiche.
- Seules les réponses renseignées partent : le backend refuse une réponse vide à une question
  obligatoire, et la qualification se complète au fil des appels. Conséquence assumée : une réponse
  facultative ne s'efface pas depuis l'écran.
- Le score de charge est saisi et présenté comme déclaré (Q21).
- **L'émission de la proforma n'est pas proposée** : aucune page ne permet encore au client de
  l'accepter, et un lien d'acceptation sans destination serait une promesse vide. Elle viendra avec
  cette page.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Console | le nom du prospect mène à sa fiche |
| Fiche neuve | les questions du référentiel, dont la question facultative sur les statuts ; chiffrage fermé |
| Deux réponses | « Enregistré. Il manque encore : capital_social, … » |
| « deux » associés | « « associes » attend ENTIER, « deux » n'en est pas un » |
| Réponses complètes, « 1 000 000 » avec espaces, « non » | « Qualification complète » ; la fiche reprend « non » ; le calcul s'ouvre |
| Calcul sans réponse sur les statuts | 200 000 · 250 000 · 375 000, aucune ligne, et l'échec nommé |
| Réponse « oui » sur les statuts | référence 200 000, remise TAR-STA-001 appliquée |
| Comptable | « Accès réservé » |

Avant la correction, le dossier sans réponse sur les statuts sortait à 200 000 FCFA de référence : une
remise de 50 000 FCFA sur une information que personne n'avait donnée.

### État à la fin du pas 66

**2 950 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**64 routes appelées par le frontend sur 133** (48 %).

**Ce que le projet sait faire qu'il ne savait pas.** Qualifier un prospect depuis un écran que le
questionnaire du référentiel dessine, et le chiffrer sans qu'une réponse manquante accorde une remise.

*Dans un calcul qui convertit l'absence en valeur, l'ignorance finit toujours par avoir un prix.*

## Pas 67 — La proforma envoyée, lue et acceptée, et les numéros qu'on énumérait

### Pourquoi

La fiche du pas 66 s'arrêtait avant la proforma : aucune page ne permettait au client de
l'accepter. Ce pas ferme la boucle commerciale à l'écran : arrêter le montant, envoyer le lien,
laisser le client lire et accepter.

### Ce que la relecture a trouvé

**On énumérait les proformas du cabinet.** L'acceptation est publique, et son docstring disait :
« Le sceau est vérifié avant la proforma. Une vérification qui lirait d'abord le document permettrait
de sonder l'existence d'un numéro sans posséder de lien. » **Le code lisait la proforma d'abord** :
numéro inconnu, `404` ; numéro existant au sceau faux, `422`. Les numéros sont séquentiels
(`PRO-2026-0001`, `0002`…) : sans aucun lien, on dressait la liste des propositions du cabinet.

Le test qui gardait la règle **acceptait `404` ou `422`**, tout en citant la règle dans son docstring :
la tolérance laissait passer exactement le défaut décrit. Resserré sur `422`.

**Un sceau malformé produisait une erreur 500** : la construction du lien levait une erreur de validation
non rattrapée, masquée jusque-là par le `404` qui arrivait avant. Il reçoit désormais le même refus qu'un
sceau bien formé mais faux.

**Aucune route ne montrait au client ce qu'il acceptait.** Un engagement signé sur un prix qu'on n'a pas
vu ne se défend pas.

### Ce qui a été fait

**Backend.**

- Acceptation : `exiger_valide` (usage, échéance, sceau) **avant** toute lecture ; le sceau se vérifie sans
  lire, puisqu'il porte sur le numéro, la version et l'échéance.
- `GET /acquisition/proformas/{numero}/consultation`, publique, **dans le même ordre** : sans lien valable,
  un numéro existant et un numéro inventé reçoivent la même réponse. Elle rend le prix, les lignes, les
  débours, l'état et l'échéance, **rien d'interne** (ni intervalle, ni auteurs, ni faits). Lire ne consomme
  rien. Inscrite à la liste close des routes publiques, avec son motif.
- Un contrôle de version écrit au premier jet a été **retiré** : une nouvelle version prend un nouveau
  numéro et marque l'ancienne « remplacée », dont le lien lit donc l'ancienne à la bonne version ; le
  contrôle ne pouvait jamais se déclencher, et une mutation l'a montré en survivant. Le vrai cas, l'état
  « remplacée », est rendu par la consultation et refusé à l'acceptation par le domaine.

**Frontend.**

- Fiche du dossier, panneau « Proforma » pour un dossier chiffré : montant, motif, score de charge. Le lien
  d'acceptation, rendu une seule fois par le backend, **s'affiche une fois** avec la consigne de l'envoyer
  maintenant, construit sur l'adresse publique du site ; puis « J'ai envoyé le lien au client » note la
  transmission, qui arme la relance. La séparation des tâches non respectée est dite.
- `/proforma/[numero]`, sur la vitrine, **jamais indexée** : le prix et ce qui le compose ; un lien qui ne
  vaut pas n'affiche rien d'autre qu'un refus ; une proforma acceptée, remplacée ou annulée ne propose pas
  d'accepter ; l'accord exige le nom et la qualité du signataire, et une case qui dit ce qu'il fait. Textes
  en français seulement, traduction à faire.

### Les épreuves

- Sans lien, un numéro existant et un numéro inventé répondent `422`, à l'acceptation comme à la consultation.
- La consultation montre le prix et rien d'interne ; la lire deux fois ne consomme rien, l'acceptation suit, et
  la relecture dit « acceptée » ; le lien d'une autre version est refusé.
- Mutation tuée : proforma lue avant le sceau.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Fiche d'un dossier chiffré | panneau « Émettre la proforma » |
| Montant sous le plancher, sans motif | « montant 199999 hors de l'intervalle [200000 ; 375000] sans motif… » |
| Avec motif | PRO-2026-0001 émise, séparation non respectée signalée, lien affiché une fois |
| Fiche rechargée | plus de formulaire ; « En attente de l'accord du client » |
| « J'ai envoyé le lien » | transmission notée, relance armée |
| Page du client | « Votre proposition », 199 999 FCFA, sans intervalle interne, bouton d'accord |
| Sceau falsifié, puis numéro inventé | le même message de refus |
| Accord sans la case | « Cochez la case pour confirmer votre accord » |
| Accord | enregistré ; la page rouverte dit « déjà accepté » sans bouton ; le dossier est « Acceptée » |

Deux contrôles de mon script d'essai étaient faux et ont été refaits : une expression régulière trop large
avait pris un texte du formulaire de contact pour la réponse de l'action, et un montant était cherché avec
une espace ordinaire au lieu de l'espace fine du format français.

### État à la fin du pas 67

**2 954 tests passent** sur PostgreSQL réel. 134 routes sur 127 chemins, 43 corps de requête, 30 routes
sans permission (la consultation, motif inscrit). Frontend : typage, lint, construction de production ;
**68 routes appelées sur 134** (51 %).

**Ce que le projet sait faire qu'il ne savait pas.** Conduire un prospect de sa demande à son accord signé
entièrement à l'écran, en lui montrant ce qu'il accepte, sans qu'un inconnu puisse compter les proformas
du cabinet.

*Un test qui accepte deux réponses dont l'une est le défaut qu'il décrit ne garde rien : il récite la règle.*

## Pas 68 — Le règlement à l'écran, et l'espace qui pouvait s'ouvrir à la mauvaise adresse

### Pourquoi

Le pas 67 conduisait le prospect jusqu'à son accord. Restait le règlement, qui ouvre son espace.

### Ce que la relecture a trouvé

Deux chemins mènent à l'encaissement :

| Chemin | Adresse de l'espace |
| --- | --- |
| Paiement par téléphone | retenue sur le dossier à la demande de règlement, annoncée au client, employée par la notification de l'opérateur |
| Règlement en espèces ou par virement, confirmé à la main | **reçue dans la requête, jamais confrontée à celle retenue** |

Un client à qui l'on avait annoncé `station-bonaberi` et qui réglait finalement au guichet voyait son
espace s'ouvrir à l'adresse tapée ce jour-là ; celle qu'on lui avait donnée n'existait pas. Deux espaces
possibles pour un seul engagement.

**Corrigé dans le cas d'usage, donc pour les deux chemins** : `encaisser_l_acceptation` retient l'adresse
par `retenir_le_slug`, qui refuse une adresse différente de celle déjà retenue et retient celle-ci quand
aucune ne l'était. Le dossier dit ensuite laquelle a été ouverte.

**La fiche ne savait pas quelle proforma faire régler** : la lecture d'un dossier rend désormais ses
proformas (numéro, version, état, montant, dates), **jamais leur lien d'acceptation**.

### Ce qui a été fait, à l'écran

Panneau « Règlement » sur la fiche d'un dossier accepté, pour `GERER_COMPTES` ; les autres lisent que le
règlement se confirme par l'administration du cabinet.

- **Demander le paiement par téléphone** : adresse et téléphone ; l'écran dit que le client doit valider son
  code, et qu'aucun encaissement n'a encore eu lieu.
- **Règlement reçu autrement** : adresse, référence du reçu ou du virement, et une case « j'ai constaté le
  règlement ; la confirmation ouvre l'espace du client », vérifiée aussi par l'action serveur.
- **Une adresse retenue s'affiche en lecture seule** dans les deux formulaires.
- Un dossier payé affiche la date et l'espace ouvert.

### Les épreuves

- Recette sur PostgreSQL : règlement demandé à `boulangerie-wouri`, puis encaissement à une autre adresse,
  **refusé** ; à la bonne adresse, l'espace s'ouvre. Un encaissement sans demande préalable retient son adresse
  sur le dossier.
- La fiche liste les proformas du dossier et ne contient pas le lien d'acceptation.
- Mutation tuée : adresse non confrontée à l'encaissement.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Fiche d'un dossier accepté, direction | « le règlement se confirme par l'administration » |
| Même fiche, administrateur | les deux formulaires |
| Demande par téléphone, `station-bonaberi` | « Demande envoyée au +237699112233 : le client doit valider sur son téléphone. mode simulé » |
| Fiche rechargée | l'adresse s'affiche en lecture seule |
| Confirmation sans la case | refusée |
| Confirmation à `autre-espace`, par appel direct | « l'espace « station-bonaberi » est déjà retenu, « autre-espace » ne peut pas le remplacer » |
| Confirmation à l'adresse retenue | « Règlement confirmé. L'espace « station-bonaberi » s'ouvre. » |
| Seconde confirmation | « déjà confirmé : aucun second espace n'est ouvert » |
| Fiche | « Payé le 14/09/2026 · espace « station-bonaberi » », sans formulaire |

### État à la fin du pas 68

**2 957 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production ;
**70 routes appelées par le frontend sur 134** (52 %).

**Ce que le projet sait faire qu'il ne savait pas.** Conduire à l'écran un prospect de sa demande sur le site
jusqu'à l'ouverture de son espace, par téléphone ou au guichet, à l'adresse qu'on lui a annoncée.

*Deux chemins vers le même geste doivent passer par la même règle, sans quoi c'est le moins surveillé qui décide.*

## Pas 69 — L'écran des comptes invite et suspend, et l'administrateur qui recevait le secret d'activation

### Pourquoi

Depuis le pas 61, l'écran des comptes ne savait faire qu'un geste : réinitialiser le second facteur d'un
collaborateur. Inviter une recrue et suspendre un départ, les deux gestes quotidiens d'une administration de
cabinet, passaient encore par un appel direct à l'API.

### Ce que la relecture a trouvé

**L'invitation rendait le lien d'activation à l'administrateur.** Le modèle de réponse portait
`lien_provisoire`, le secret en clair, avec ce motif : « rendu uniquement parce qu'aucun service d'envoi réel
n'est branché ; dès que le module d'envoi sera greffé, ce champ doit disparaître ». Le service de courriel
était branché depuis longtemps, et le champ était resté.

Ce n'était pas un simple secret de trop dans une réponse : **l'administrateur qui invitait pouvait activer
lui-même le compte qu'il créait**, choisir son mot de passe, enrôler son second facteur (le lien de preuve du
pas 62 part à l'adresse du compte, que l'administrateur venait de saisir, mais le premier mot de passe lui
suffisait déjà à se connecter) et agir sous le nom du collaborateur. Un écran qui aurait affiché ce champ
aurait rendu la faute ordinaire.

**Corrigé** : `Invitation` ne porte plus que le compte et la date d'expiration du lien. Le lien part au
collaborateur par courriel ; en démonstration, la boîte de recette le montre.

**Un administrateur pouvait suspendre son propre compte.** Le geste ferme les sessions ; un administrateur
seul laissait le cabinet sans personne pour gérer les comptes, et sans autre remède qu'une intervention en
base. **Corrigé dans le cas d'usage** : `suspendre_compte` lève `SuspensionRefusee` quand la cible est
l'auteur, la route répond 409 avec la phrase.

**Le titulaire suspendu n'était pas prévenu.** Il découvrait la suspension au refus de sa connexion, sans
savoir s'il s'agissait d'une erreur de mot de passe. La route envoie désormais le gabarit `compte.suspendu`.

**Une question pour la direction (Q22).** L'administrateur n'a aucune permission comptable ou déclarative,
mais il peut inviter tous les rôles, réviseur compris, donc s'inviter lui-même sous une seconde adresse. Le
code ne tranche pas : la question est posée, et chaque invitation reste au journal d'audit.

### Ce que l'écran a dû résoudre

**L'administrateur ne lit pas le portefeuille.** Il ne détient pas `LIRE_DOSSIER`, et
`GET /portefeuille/entreprises` l'exige. Le formulaire d'invitation ne peut donc pas lui proposer la liste des
dossiers à cocher. Plutôt que d'élargir une lecture du portefeuille à un rôle qui en a été privé exprès,
l'écran s'adapte : **un rôle qui lit le portefeuille coche des cases, un administrateur saisit les NIU**. Le
backend reste juge, et le NIU inconnu ne donne accès à rien.

**Une portée vide est admise, et elle ne donne rien.** Seuls l'adhérent et l'inspecteur exigent une portée,
et ils ne s'invitent pas ici. Un comptable invité sans dossier est un cas réel (une prise de poste avant la
répartition du portefeuille) ; l'écran le dit sous la liste : « sans dossier désigné, le collaborateur n'en
voit aucun tant qu'un dossier ne lui est pas affecté ». « Tout le cabinet » est l'autre extrême, et il se
coche explicitement : le formulaire part sur « des dossiers ».

### Ce qui a été fait, à l'écran

- Panneau **« Inviter »** : adresse, prénom, nom, téléphone, rôle (les rôles internes, sans adhérent ni
  inspecteur), date de début, périmètre. Le message de réussite dit à qui le lien est parti et jusqu'à quand il
  vaut ; il ne montre pas le lien.
- Bouton **« Suspendre »** sur chaque ligne active qui n'est pas la sienne : motif d'au moins dix caractères,
  case « les sessions ouvertes seront fermées ; le compte n'est pas supprimé », vérifiée aussi par l'action
  serveur.
- Fichiers : `app/lib/actions-administration.ts` (`inviterUnCollaborateur`, `suspendreUnCompte`),
  `app/components/administration/GestesComptes.tsx` (`InvitationCollaborateur`, `SuspendreCompte`), page
  `(collaborateur)/comptes`.

### Les épreuves

- `test_inviter_puis_activer_puis_se_connecter` lit désormais le secret **dans le courriel retenu**, comme le
  collaborateur, et vérifie qu'il n'apparaît nulle part dans la réponse.
- `test_la_suspension_previent_le_titulaire_et_ne_se_retourne_pas_contre_soi`.
- Les cas de domaine qui suspendaient « C-1 » en agissant sous « C-1 » agissent désormais sous un
  administrateur distinct : ils encodaient la faute.
- Mutations tuées : auto-suspension admise ; secret rendu sous un autre nom de champ que `lien_provisoire`.
  **Une première mutation avait survécu parce qu'elle était mal posée** : le champ ajouté l'avait été à une
  autre classe, et pydantic ignorait l'argument. Refaite sur `Invitation`, elle est tuée par l'assertion qui
  cherche le secret dans le texte brut de la réponse, et non un nom de champ.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Page des comptes, administrateur | panneau « Inviter », bouton « Suspendre » sur les lignes actives |
| Invitation d'un comptable sans dossier | admise : « Invitation envoyée à q.vide@cga-brcg.cm. Le lien vaut jusqu'au 28/09/2026. » |
| Invitation avec deux NIU saisis | compte en attente d'activation, rôle comptable |
| Réponse de l'action | aucun `jeton=`, aucun lien |
| Boîte de recette | le lien d'activation, dans le courriel du collaborateur |
| Même adresse une seconde fois | « l'adresse … est déjà celle d'un compte. Si la personne a perdu son mot de passe, lui envoyer un lien de réinitialisation » |
| Suspension sans la case | « Cochez la confirmation : les sessions ouvertes seront fermées. » |
| Suspension de Christelle NDONGO | « Compte suspendu, sessions fermées, titulaire prévenu. » ; état SUSPENDU ; sa connexion répond 401 ; courriel `compte.suspendu` retenu |
| Suspension de son propre compte, par appel direct | « on ne suspend pas son propre compte … Demander à un autre administrateur. » |

### État à la fin du pas 69

**2 958 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production ;
**72 routes appelées par le frontend sur 134** (54 %).

**Ce que le projet sait faire qu'il ne savait pas.** Accueillir une recrue et fermer l'accès d'un départ depuis
l'écran, sans que l'administrateur voie jamais le secret de quelqu'un d'autre.

*Un champ provisoire qui attend « dès que » ne part jamais seul : il faut qu'un pas le cherche.*

## Pas 70 — Confier un dossier et fermer un rôle, et l'historique que l'affectation réécrivait

### Pourquoi

L'écran des comptes invitait et suspendait depuis le pas 69. Restaient trois routes d'administration sans
formulaire : confier un dossier à une habilitation, fermer une habilitation, fermer les sessions d'un compte.
Son en-tête le disait : « les routes existent, les formulaires non ».

### Ce que la relecture a trouvé

**L'affectation réécrivait le passé.** Confier un dossier ajoutait son NIU à la portée de l'habilitation. Or la
portée n'est pas datée : elle vaut pour tout l'intervalle de l'habilitation. Essai sur la démonstration, avant
correction :

| Question posée à `GET /transverse/dossiers/{niu}/acces?a_la_date=2024-01-10` | Réponse |
| --- | --- |
| Avant d'affecter la clinique à Léonard FOTSO (habilitation H-004, ouverte en 2021) | C-004 absent |
| Après la lui avoir affectée le 14/09/2026 | **C-004 présent, en janvier 2024** |

L'historique des habilitations existe pour répondre à une question : qui était habilité le jour d'un dépôt. Le
dépôt des habilitations le dit en toutes lettres (« rendre seulement les actives serait une erreur de
conception »), la route de fermeture aussi (« c'est elle qui permettra de dire dans trois ans qui était
habilité »). L'affectation lui faisait mentir, sans trace visible autre qu'une ligne de journal.

**Corrigé dans le domaine**, par `Habilitation.affecter(niu, le, identifiant_successeur, par)` :

| Cas | Ce qui est enregistré |
| --- | --- |
| L'habilitation commence aujourd'hui ou plus tard | la portée s'étend sur place ; il n'y a aucun passé à réécrire |
| L'habilitation a déjà couru | elle est fermée ce jour (borne exclue, motif `AFFECTATION_DOSSIER`), et une **successeur** s'ouvre ce jour, avec l'ancienne portée plus le dossier, la même fin prévue, et l'auteur de l'affectation comme `accordee_par` |

La route rend **l'habilitation active après l'affectation**, dont l'identifiant peut différer de celui de l'URL.
Le journal note laquelle.

**La même méthode acceptait quatre cas qu'elle devait refuser** :

| Cas | Pourquoi c'est une faute |
| --- | --- |
| Habilitation d'un adhérent ou d'un inspecteur | lui ouvrir un autre NIU lui donnait la comptabilité d'une autre entreprise, la faute que l'en-tête du module appelle la plus coûteuse ; leur périmètre suit une souscription ou une mission |
| Habilitation fermée | l'étendre rouvrait en silence un accès terminé, sur tout son passé |
| Dossier déjà dans la portée | le journal disait qu'on avait affecté ce qui l'était déjà |
| Habilitation transverse | déjà refusé ; conservé |

Une habilitation relayée par une affectation antérieure n'est pas « terminée » : son refus désigne la
successeur au lieu de conseiller d'en ouvrir une nouvelle, ce qui aurait créé un doublon du rôle. Ce message a
été reformulé **après l'essai réel**, qui l'avait montré trompeur.

**Un administrateur pouvait fermer sa propre habilitation**, et perdre `GERER_COMPTES` à la date dite : le même
défaut que l'auto-suspension du pas 69, par une autre porte. `fermer_habilitation` lève désormais
`FermetureRefusee` (409). Le cas de domaine qui fermait « H-1 » de « C-1 » en agissant sous « C-1 » agit sous
un administrateur distinct.

**L'écran ne pouvait pas agir sur un rôle** : la liste des comptes rendait les rôles, pas les habilitations.
`LigneCompte.habilitations` porte désormais les habilitations actives à la date, avec leur identifiant.

### Ce qui a été fait, à l'écran

Panneau **« Habilitations du jour »** sur l'écran des comptes, une ligne par habilitation active : collaborateur,
rôle, dossiers, date de début.

- **Confier un dossier** (pour `AFFECTER_DOSSIER`) : un NIU, un bouton « Confier à compter d'aujourd'hui ».
  Masqué sur une habilitation transverse, d'adhérent ou d'inspecteur, où le refus est certain ; le backend
  reste juge des autres cas. Le message dit quand l'habilitation a été relayée, et que l'historique antérieur
  reste intact.
- **Fermer ce rôle** (jamais le sien) : date, motif (départ, changement de poste, remplacement, fin de mission,
  correction) et une case qui nomme le rôle et la personne, rappelle que l'habilitation ne se rouvre pas et que
  le compte n'est pas suspendu.
- **Fermer ses sessions**, sur chaque compte actif qui n'est pas le sien : le geste d'un appareil perdu ou d'une
  session douteuse. Le titulaire se reconnecte, l'intrus non.
- Les dates s'affichent sans passer par `new Date("2026-09-30")`, qui est minuit UTC et afficherait le 29 sur
  un serveur réglé à l'ouest de Greenwich.

### Les épreuves

`tests/test_affectation_datee.py`, 14 cas : relais le jour même, accès absent la veille et présent le jour
même (avec la contre-épreuve du dossier d'origine resté lisible), fin prévue transmise, extension sur place
d'une habilitation qui commence, les quatre refus, enregistrement et journal de la successeur, auto-fermeture,
et par la route la question « qui avait accès au 10/01/2024 » posée avant et après.

Sept mutations, **toutes tuées** : extension toujours sur place, adhérent admis, habilitation fermée admise,
doublon admis, fin prévue perdue, auto-fermeture admise, route rendant l'ancienne habilitation au lieu de la
successeur.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Page des comptes, administrateur | panneau « Habilitations du jour », gestes présents |
| C-004 sur la clinique au 10/01/2024, avant | absente |
| Confier la clinique à H-004 (NIU saisi en minuscules) | « confié à compter du 14/09/2026 : l'habilitation H-004 est relayée par H-696098e23815, et l'historique antérieur reste intact » |
| C-004 au 10/01/2024, après | **absent** ; au 14/09/2026 : présent |
| Confier de nouveau à H-004 | refusé (message reformulé ensuite, voir plus haut) |
| Confier un dossier à l'habilitation d'un adhérent | « son périmètre suit une souscription ou une mission, il ne s'étend pas par affectation » |
| Fermer le rôle de Léonard FOTSO sans la case | « Cochez la confirmation : une habilitation fermée ne se rouvre pas. » |
| Avec la case, au 30/09/2026, motif départ | « elle ne vaut plus à compter du 30/09/2026 » |
| Fermer sa propre habilitation H-002 | « on ne ferme pas sa propre habilitation : demander à un autre administrateur » |
| Fermer les sessions de Léonard FOTSO | « 1 session fermée » ; sa session répond 401 |
| Seconde fois | « Aucune session ouverte. » |

### État à la fin du pas 70

**2 972 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production ;
**75 routes appelées par le frontend sur 134** (56 %).

**Ce que le projet sait faire qu'il ne savait pas.** Répartir le portefeuille et fermer un rôle depuis l'écran,
en gardant vraie la réponse à « qui avait accès à ce dossier tel jour ».

*Un ensemble qui n'a pas de date prend celle de son contenant : ajouter un élément aujourd'hui, c'est l'ajouter depuis toujours.*

## Pas 71 — La contre-passation qui rouvrait un exercice clos, et une couverture enfin mesurée

### Pourquoi

Le pas devait donner un écran à la validation et à la contre-passation d'une écriture, que ma mesure de
couverture comptait parmi les routes sans écran. Deux découvertes ont changé le pas.

### Rectificatif : la couverture des écrans n'était pas mesurée

Du pas 57 au pas 70, le journal et le document annonçaient une couverture (« 75 routes sur 134 » à la fin du
pas 70) obtenue **en ajoutant à la main** les routes branchées à chaque pas. Rejouée pour de vrai, la mesure
donnait **79**. L'addition ignorait que l'écran de saisie appelait déjà la validation et la contre-passation :
leur adresse porte la clé de l'écriture, `${cle}`, qui vaut « 2026/AC/12 », trois segments, et ma première
mesure faisait correspondre un morceau interpolé à un seul segment.

La mesure est désormais un script du dépôt, `Backend_erp_cga/outils/couverture_des_ecrans.py`, qui lit les
routes de l'application et les chaînes-chemins du frontend, et laisse un `${…}` couvrir plusieurs segments.
Elle se rejoue : `CGA_PERSISTANCE=memoire python -m outils.couverture_des_ecrans --liste`. Son en-tête dit aussi
ce qu'elle ne mesure pas : qu'une route soit appelée ne dit pas que l'écran est bon.

### Ce que la relecture a trouvé

L'écran de saisie proposait déjà « Contre-passer ». Le cas d'usage le disait :

> Elle porte la date du jour où l'on s'aperçoit de l'erreur, **jamais** celle de l'écriture d'origine. On ne
> retouche pas le passé.

**Aucune ligne ne le tenait.** La date venait de la requête et n'était comparée à rien, et le brouillon inverse
naissait sans aucun des contrôles d'exercice de la saisie. Sonde sur PostgreSQL, par la route, avant correction :

| Essai | Résultat |
| --- | --- |
| Clore 2026 (horloge au 15/01/2027), puis contre-passer une écriture de 2026 | **201** : brouillon dans l'exercice 2026, daté du 15/01/2027, hors de ses bornes |
| Valider ce brouillon | **200** |
| Balance de l'exercice 2026 clos | **modifiée** |
| Contre-passer au 01/01/2020 | **201**, six ans avant l'écriture annulée |

La clôture refusait bien les brouillons qui subsistent (`BROUILLON_SUBSISTANT`), mais un brouillon pouvait naître
**après** elle, par cette porte, puis se valider : la validation ne regardait pas l'exercice non plus. La liasse
remise à l'administration devenait fausse après coup, par un bouton de l'écran.

### La correction

**Un seul contrôle d'exercice pour trois gestes.** `_exiger_l_exercice(libelle, date, exercice)` est appelé par
la saisie (inchangée), par la validation et par la contre-passation. Trois copies auraient divergé ; c'est
précisément la contre-passation, restée sans contrôle, qui ouvrait l'exercice clos.

| Geste | Contrôles |
| --- | --- |
| Validation | exercice connu, du même libellé que l'écriture, non clos, date dans ses bornes |
| Contre-passation | les mêmes, plus : jamais avant la date de l'écriture d'origine (`ContrepassationAntidatee`) |

- `exercice` est un argument **exigé, sans défaut**, des deux cas d'usage ; les routes le lisent au portefeuille,
  la clôture passe l'exercice suivant pour valider son à-nouveau.
- Un exercice fourni qui n'est pas celui de l'écriture est un **refus bruyant** : mieux vaut qu'un appelant
  distrait échoue que de contrôler la mauvaise chose.
- **Le même jour que l'origine reste admis** : c'est le jour du constat quand l'erreur se voit à la relecture.
  Ce qui est refusé, c'est d'annuler avant.
- **Une erreur d'un exercice clos ne se contre-passe plus dans cet exercice** : elle se corrige dans l'exercice
  ouvert, par une écriture ordinaire et motivée, et la phrase le dit.
- Un constat postérieur à la clôture d'un exercice encore ouvert (janvier 2027 pour 2026) est refusé avec la
  date à retenir : « dater au plus tard du 31/12/2026 ».

### Ce qui a été fait, à l'écran

- Le formulaire de contre-passation porte une **date de constat**, proposée au jour même, bornée entre la date
  de l'écriture d'origine et la clôture de l'exercice, et ramenée à la clôture quand aujourd'hui la dépasse.
- La page lit les exercices du dossier (`lireExercicesDuDossier`, sur la fiche complète). **Sur un exercice clos,
  aucun geste** : « corriger dans l'exercice ouvert » pour une écriture validée, « ce brouillon ne s'engage
  plus » pour un brouillon.
- Une fiche illisible laisse les gestes : le backend reste juge, et masquer sur une lecture échouée ferait
  croire à un exercice clos.

### Les épreuves

`tests/test_contrepassation_bornee.py`, 9 cas : refus dans un exercice clos sans rien écrire, antidatation,
jour même admis, constat hors bornes avec la date à retenir, exercice inconnu, exercice incohérent, validation
d'un brouillon après clôture, et par la route la sonde rejouée (clôture puis contre-passation refusée, balance
intacte, aucun brouillon né) et l'antidatation d'un jour. Ce dernier cas choisit une écriture postérieure au
1er janvier, pour que la veille reste dans l'exercice : une première écriture du cas dépendait d'une condition
qui pouvait ne rien mesurer.

Huit mutations, **toutes tuées** : contre-passation sans contrôle d'exercice, validation sans contrôle,
antidatation admise, jour même refusé, exercice clos admis, bornes non vérifiées, exercice incohérent admis,
route de validation sans exercice.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Saisie, SARL BATIMENT PLUS, 2026 ouvert | trois « Contre-passer » |
| Constat au 01/01/2020 | « le 01/01/2020 tombe hors de l'exercice 2026 (01/01/2026 au 31/12/2026) » |
| Constat la veille de l'origine (11/07/2026) | « la contre-passation serait datée du 11/07/2026, avant l'écriture 2026/AC/000001 du 12/07/2026 qu'elle annule » |
| Constat au 15/01/2027 | « … Une erreur d'un exercice encore ouvert se corrige dans cet exercice : dater au plus tard du 31/12/2026. » |
| Constat au 14/09/2026 | « Contre-passation enregistrée en brouillon sous AC n° 4. » |

**Non exercé en réel** : l'affichage sur un exercice clos. La démonstration n'a aucune écriture dans ses
exercices clos, et le serveur suit l'horloge réelle, qui ne permet pas de clore 2026 en septembre 2026. Le refus
lui-même est éprouvé sur PostgreSQL par la route ; l'affichage, seulement par le typage et la construction.

### État à la fin du pas 71

**2 981 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production ;
**80 routes appelées par le frontend sur 134** (59 %), mesurées par le script.

**Ce que le projet sait faire qu'il ne savait pas.** Corriger une écriture sans pouvoir rouvrir, par la
correction, un exercice déjà déclaré ; et dire sa couverture d'écrans par une mesure qui se rejoue.

*Un commentaire qui dit « jamais » sans ligne qui refuse est une promesse faite au lecteur, pas au code.*

## Pas 72 — Le brouillon qui ne se corrigeait pas, et la clôture qu'une pièce oubliée fermait pour toujours

### Pourquoi

Le pas 71 a borné la validation et la contre-passation. En le relisant, une phrase restait sans ligne pour la
tenir : « un brouillon se corrige ou se supprime avant validation ». Or la clôture refuse tout brouillon qui
subsiste.

### Ce que la relecture a trouvé

**Quatre endroits promettaient un geste qu'aucune route ne permettait :**

| Où | Ce qui était écrit |
| --- | --- |
| L'écran, après chaque saisie | « Elle figure ci-dessous et reste modifiable tant qu'elle n'est pas validée. » |
| L'entité | une propriété `modifiable`, vraie pour un brouillon, lue par personne |
| Le refus de contre-passer un brouillon | « Un brouillon se corrige ou se supprime avant validation. » |
| L'obstacle de clôture `BROUILLON_SUBSISTANT` | « Chacune est à valider ou à supprimer. » |

Et quatre autres : la reprise, deux fois (« les écritures entrent en brouillon, donc elles se suppriment »), et la
clôture, deux fois (« une reprise mal faite laisse des brouillons qu'on supprime »).

**L'impasse, sur PostgreSQL, par la route :**

| Essai | Résultat |
| --- | --- |
| Saisir une écriture sans pièce justificative (le champ n'est pas obligatoire à l'écran) | 201, brouillon |
| La valider | 409 : « une écriture validée porte sa pièce justificative » |
| La contre-passer | 409 : « on ne contre-passe qu'une écriture validée » |
| Clore l'exercice en janvier 2027 | refusé : `BROUILLON_SUBSISTANT` |

Aucune route ne corrigeait, aucune ne supprimait. **Un oubli de saisie fermait l'exercice à la clôture pour
toujours.**

### Ce qui a été décidé, et ce qui ne l'a pas été

**Corriger, oui. Supprimer, non.** Une suppression ne serait pas une issue : elle laisserait un trou dans la
séquence, que la clôture refuse aussi (`SEQUENCE_TROUEE`) et que l'administration cherche en premier. Corriger
réécrit le contenu **au même numéro**.

**Abandonner un brouillon qui n'aurait jamais dû exister : question ouverte Q23.** L'entité dit délibérément
« il n'y a pas de troisième état ». Un état ABANDONNÉ, la numérotation à la validation, ou valider puis
contre-passer : c'est une question de pratique comptable, qu'un expert du cabinet doit trancher. Elle compte
surtout pour une reprise appliquée sur le mauvais fichier, dont les quatre mille brouillons n'ont toujours pas
d'autre issue.

### La correction

`corriger_un_brouillon(cle, correction, journaux, plan, exercice, depot, par)` et
`POST /comptabilite/dossiers/{entreprise}/ecritures/{exercice}/{journal}/{numero}/correction`, sous
`SAISIR_ECRITURE`.

- **Ce qui change** : date, libellé, pièce, référence externe, lignes (`CorrectionDeBrouillon`, `extra="forbid"`).
- **Ce qui ne change pas** : journal, exercice, numéro. Ils forment la clé ; changer de journal retirerait un
  numéro d'une séquence pour en prendre un dans une autre. Un `numero` glissé dans la requête répond 422.
- **Tous les contrôles de la saisie sont rejoués** : journal, comptes au plan, exercice ouvert, date dans ses
  bornes.
- **`saisie_par` devient l'auteur de la correction** : c'est lui qui a écrit le contenu que la validation
  engagera.
- **Refus** : une écriture validée (« la contre-passer, puis saisir l'écriture juste ») ; une contre-passation en
  brouillon, dont les lignes sont l'inverse exact de l'origine et qui deviendrait une écriture ordinaire se
  disant contre-passation.
- Le dépôt refusait déjà d'écraser une écriture validée : la correction ne peut pas atteindre ce que la
  validation a engagé, même par un appel concurrent.
- Les sept passages faux, dans six fichiers, sont réécrits : l'obstacle de clôture dit désormais « à valider, ou à
  corriger puis valider », et la reprise ne prétend plus que ses brouillons se suppriment.

### Ce qui a été fait, à l'écran

- Sur chaque brouillon ordinaire, un bouton **« Corriger »** ouvre le **formulaire de saisie lui-même**,
  prérempli, à son numéro. Un seul formulaire pour les deux gestes : deux finiraient par ne plus accepter la même
  écriture. L'action serveur de saisie et celle de correction partagent aussi leur relecture (`contenuSaisi`).
- Le journal s'affiche sans se choisir ; le formulaire offre autant de lignes que le brouillon en compte, et
  jamais moins de huit.
- Un brouillon sans pièce porte la mention **« sans pièce : à corriger avant de valider »**.
- Une contre-passation en brouillon n'a pas de bouton « Corriger ».
- Deux formulaires ouverts sur la même page ont chacun leur liste de comptes : HTML exige des identifiants
  uniques.

### Les épreuves

`tests/test_correction_de_brouillon.py`, 8 cas : le brouillon sans pièce qui se corrige puis se valide, la clé
qui reste, l'auteur qui change, un numéro ou un journal glissés refusés, l'écriture validée et la contre-passation
refusées, les contrôles de saisie rejoués sans rien écrire, et par la route la sonde entière (saisie sans pièce,
validation refusée, correction, validation, correction refusée, clôture possible). Le cas « l'adhérent ne corrige
pas » envoyait d'abord des lignes vides : la requête tombait en 422 **avant** le contrôle d'accès, et le cas ne
mesurait rien ; il envoie désormais un corps valide et exige 403.

Sept mutations, **toutes tuées** : écriture validée corrigeable, contre-passation corrigeable, contrôles non
rejoués, auteur conservé, pièce non reprise, champs en trop admis, route sans permission.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Saisie d'un achat sans pièce, comptable, SARL BATIMENT PLUS | OD n° 1, brouillon |
| Page de saisie | « sans pièce : à corriger avant de valider », un bouton « Corriger » |
| Validation | « une écriture validée porte sa pièce justificative… » |
| Correction avec la pièce PJ-2026-0914 | OD n° 1, pièce et libellé corrigés, toujours brouillon |
| Correction datée du 01/02/2027 | « le 01/02/2027 tombe hors de l'exercice 2026… » |
| Validation | « Écriture OD n° 1 validée. » |
| Correction après validation | « validée : elle ne se corrige plus. La contre-passer, puis saisir l'écriture juste. » |
| Contre-passation | OD n° 2 en brouillon ; sa ligne offre « Valider », pas « Corriger » |

### État à la fin du pas 72

**2 989 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production ;
**81 routes appelées par le frontend sur 135** (60 %), mesurées par le script.

**Ce que le projet sait faire qu'il ne savait pas.** Corriger une saisie inachevée sans créer de trou, et ne plus
laisser un champ oublié fermer un exercice à la clôture.

*Un message d'erreur qui conseille un geste impossible est plus cruel qu'un refus sec : il envoie chercher un bouton qui n'existe pas.*

## Pas 73 — Comptabiliser une pièce contrôlée, et la TVA qu'on récupérait en changeant un mot

### Pourquoi

La route qui propose l'écriture d'une facture contrôlée se dit elle-même « le cœur du produit » : la boîte de
réception mène au rapport, le rapport mène à l'écriture. Elle n'avait pas d'écran. Et l'écran de détail d'une
pièce (E02) affichait « Valider et comptabiliser » : un bouton `type="button"`, **sans aucune action**.

### Ce que la relecture a trouvé

La route affirmait, dans la documentation de son corps de requête :

> **Le régime n'est pas demandé** : il est lu au portefeuille. Le laisser fournir par l'appelant permettrait de
> récupérer une TVA qu'une entreprise au synthétique ne récupère jamais, en cochant une case.

**Aucune ligne ne lisait le portefeuille.** `proposer_ecriture_achat` décidait de la TVA récupérable sur
`facture.destinataire.regime`, c'est-à-dire sur la facture envoyée dans la requête. Le moteur de conformité lit
aussi ce régime pour choisir ses règles. Sonde par la route, facture conforme F-2026-0413 :

| Dossier de la proposition | Destinataire déclaré | Lignes proposées |
| --- | --- | --- |
| ETS TCHOUMBA & FILS (IGS) | IGS | 612 1 431 000 / 401 1 431 000 |
| ETS TCHOUMBA & FILS (IGS) | **REEL** | 612 1 200 000 / **4451 231 000** / 401 1 431 000 |
| ETS TCHOUMBA & FILS (IGS) | REEL, **NIU de SARL BATIMENT PLUS** | acceptée, mêmes lignes |

231 000 FCFA de TVA déductible pour une entreprise qui n'en déduit aucune, en changeant un mot. Et une facture
adressée à une autre entreprise se proposait sans refus dans ce dossier.

### La correction

`rattacher_au_dossier(facture, niu, regime)`, fonction pure de la comptabilité, appelée par la route avant le
contrôle de conformité :

| Cas | Effet |
| --- | --- |
| Destinataire nommé par un autre NIU | refus `FactureDUnAutreDossier`, 409 |
| Destinataire sans NIU | reçoit celui du dossier, et la rectification est dite |
| Régime déclaré différent de celui du portefeuille à la date de l'opération | remplacé, et la rectification est dite |
| Dossier inconnu du portefeuille | 404 ; aucun régime à la date : 409 |

- La réponse porte un champ **`rectifications`** : une TVA qui disparaît sans explication se « corrige » à la
  main.
- **Le contrôle de conformité se fait sur la facture rattachée.** Une mutation qui contrôlait la facture
  d'origine survivait à la première batterie : aucun cas ne mesurait une règle dépendant du régime du
  destinataire. Le cas ajouté emploie FAC-ACH-007 (TVA non déductible sur règlement en espèces), qui ne vise que
  les destinataires au réel : sur le dossier IGS, déclaré au réel, elle ne parle plus ; chez son vrai destinataire,
  au réel, elle parle.
- La lecture du dossier au portefeuille est extraite (`_dossier_du_portefeuille`) : l'exercice et le régime se
  lisent au même endroit.

**Ce qui n'est pas corrigé, et pourquoi.** `POST /conformite/controler` lit toujours le régime déclaré. La
conformité est une **feuille** du graphe des contextes, sans arête vers le portefeuille, et c'est délibéré. Son
verdict ne comptabilise rien ; la route qui comptabilise, elle, rattache désormais. Un appelant qui connaît le
dossier doit rattacher avant de contrôler.

### Trois cas existants reposaient sur le défaut

`test_proposition_http.py` et la recette de production proposaient la **facture bloquante**, adressée à
BOULANGERIE LA COLOMBE, dans le dossier de SARL BATIMENT PLUS. La route l'acceptait, et les cas mesuraient le
blocage par conformité sur une facture proposée au mauvais dossier. Ils la proposent désormais chez son
destinataire. Le cas « aucun numéro n'est consommé » garde la proposition au mauvais dossier, et exige
maintenant son refus (409).

### Ce qui a été fait, à l'écran

Sur la fiche d'une pièce (E02), pour qui détient `SAISIR_ECRITURE`, le bouton décoratif devient un parcours en
deux temps :

1. **« Proposer l'écriture »** (ou « …, conséquence fiscale comprise » quand un constat est majeur) : rien n'est
   écrit. Les lignes s'affichent en débit et crédit, avec le numéro pressenti et les rectifications du
   portefeuille. Une ligne de TVA rejetée porte **« TVA non déductible (FAC-ACH-007) »** : le moteur la garde en
   4451, marquée par un attribut fiscal que la déclaration de TVA lit, et l'imputation finale est laissée au
   cabinet (`consequences_fiscales.py`). Sans la mention, l'écran montrait une TVA récupérable que le moteur venait
   de refuser.
2. **« Enregistrer en brouillon »** : l'écriture entre au journal, et le lien mène à l'écran de saisie où elle se
   relit et se valide.

**Le navigateur n'envoie que la référence de la pièce.** Les deux actions serveur relisent la facture et
refont la proposition : des lignes renvoyées par le navigateur pourraient être retouchées entre l'affichage et
l'enregistrement. Le bouton ne dit plus « valider », puisqu'il ne valide rien.

Un rôle qui lit les pièces sans saisir (la direction, par exemple) lit « la comptabilisation est réservée à qui
saisit les écritures » ; par appel direct, l'action répond « SAISIR_ECRITURE est requise ».

**Restent décoratifs** sur cet écran : « Demander une facture rectificative » et « Écarter un constat ».

### Rectificatif : le compte C-004 est Léonard FOTSO

Le journal du pas 70, la section 76 du document, un commentaire du domaine des habilitations, l'en-tête et un nom
de cas de `test_affectation_datee.py`, et un commentaire du frontend nommaient « Laure FOTSO » ou « une
comptable ». Le jeu de démonstration nomme **Léonard** FOTSO. J'avais supposé un prénom et accordé au féminin
sans vérifier. Les passages sont corrigés en place.

### Les épreuves

`tests/test_proposition_rattachee.py`, 9 cas : le régime remplacé et dit, un régime identique qui ne rectifie
rien, un NIU manquant rattaché, une facture adressée ailleurs refusée ; par la route, la TVA d'un dossier IGS
déclaré au réel, la TVA d'un dossier au réel déclaré IGS, le contrôle de conformité sur la facture rattachée
(avec sa contre-épreuve), le refus d'une autre entreprise, le dossier inconnu.

Sept mutations, **toutes tuées** : route sans rattachement, régime non remplacé, autre destinataire admis, NIU
manquant non rattaché, rectification tue, contrôle sur la facture d'origine (tuée au second passage),
rectifications non rendues.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Fiches F-2026-0413 et 0412, comptable | « Proposer l'écriture » ; l'ancien « Valider et comptabiliser » absent |
| Fiche F-2026-0414 (bloquante) | aucun bouton de proposition |
| Proposer 0413 | SARL BATIMENT PLUS : 612 1 200 000 / 4451 231 000 / 401 1 431 000, aucune rectification |
| Journal après la proposition | 3 écritures : rien d'écrit |
| Enregistrer | AC n° 4, brouillon ; 4 écritures |
| Proposer 0412 (espèces) | 4451 marquée `tva_deductible: false`, règle FAC-ACH-007 |
| Proposer 0414 par appel direct | non comptabilisable : « anomalie bloquante (FAC-ID-003) » |
| Fiche 0413, direction | « réservée à qui saisit les écritures », sans bouton |
| Enregistrer par la direction, appel direct | « SAISIR_ECRITURE est requise » |

### État à la fin du pas 73

**2 998 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production ;
**82 routes appelées par le frontend sur 135** (60 %), mesurées par le script.

**Ce que le projet sait faire qu'il ne savait pas.** Aller, à l'écran, d'une facture contrôlée à son écriture en
brouillon, avec la TVA que le portefeuille autorise et non celle que la requête réclame.

*Un commentaire qui dit « lu au portefeuille » ne lit rien : seule une ligne lit.*

## Pas 74 — Les pièces que le cabinet attend : demander, rattacher, relancer, classer

### Pourquoi

La fiche d'une pièce (E02) gardait, après le pas 73, deux boutons sans action : « Demander une facture
rectificative » et « Écarter un constat ». Avant de brancher le premier, la relecture de la collecte a trouvé
bien plus qu'un bouton manquant.

### Ce que la relecture a trouvé

Le domaine des demandes de pièce est ancien et soigné. Il dit : « le cabinet ne peut relancer que ce qu'il sait
attendre », « une relance non tracée n'a pas eu lieu », « une demande satisfaite ne se relance jamais ; c'est la
première cause d'exaspération d'un adhérent ».

**Aucune route ne créait, ne satisfaisait, ne classait ni ne traçait une demande.** Seul l'amorçage de
démonstration en créait. En service :

| Ce que le domaine promettait | Ce qui se passait |
| --- | --- |
| Une attente devient explicite et opposable | aucune demande ne pouvait naître |
| Une demande satisfaite ne se relance jamais | une pièce reçue ne satisfaisait rien : la demande restait ouverte, et `GET /collecte/relances` la proposait aux jalons J+7, J+15, J+30 |
| Chaque relance est tracée avec sa date et son canal | aucune relance émise n'était jamais enregistrée : la liste de défense du Centre restait vide |

Et le domaine laissait passer trois fautes : **satisfaire deux fois** écrasait la date et ajoutait une seconde
pièce ; **une relance datée d'avant la demande**, ou tracée deux fois le même jour par le même canal, était
admise ; **classer sans suite** n'avait aucune méthode, donc aucune date.

### Ce qui a été fait, au backend

**Le domaine.** `DemandePiece` porte désormais `piece_a_rectifier`, `demandee_par` et `classee_le`. `satisfaire`
refuse une demande qui n'est plus ouverte, la pièce même qu'elle doit remplacer, et une date antérieure à la
demande. `relancer` refuse une date antérieure et une relance déjà tracée ce jour par ce canal.
`classer_sans_suite(motif, le)` exige le motif et ne se fait qu'une fois.

**Les cas d'usage** (`collecte/application/demandes_de_piece.py`) et **quatre routes**, chacune vérifiant la
permission **et** le dossier de la demande :

| Geste | Route | Permission |
| --- | --- | --- |
| Demander la rectificative d'une pièce | `POST /collecte/pieces/{id}/rectificative` | `CONTROLER_CONFORMITE` : qui a vu l'anomalie |
| Rattacher la pièce reçue | `POST /collecte/demandes/{id}/satisfaction` | `IDENTIFIER_PIECE` : qui identifie les pièces |
| Tracer une relance émise | `POST /collecte/demandes/{id}/relances` | `RELANCER_ADHERENT` : qui suit la relation |
| Classer sans suite | `POST /collecte/demandes/{id}/classement` | `RELANCER_ADHERENT` |

- **La rectificative prend le dossier et le type de la pièce**, jamais de la requête, et elle est bloquante.
- **Une seule demande ouverte par pièce** : la seconde est refusée en nommant la première.
- **La satisfaction exige une pièce du même dossier**, reçue **après** la demande, et qui n'est pas elle-même à
  rectifier. Ces deux derniers gardes viennent de l'essai réel : la pièce PJ-2026-0019, reçue en juillet et
  elle-même visée par une demande de rectificative, a satisfait la demande d'une autre facture émise le 3 août.
- **Rien n'est satisfait automatiquement à la réception.** Deviner qu'une facture reçue répond à telle demande,
  c'est deviner ; une demande close à tort ne se relance plus, et la pièce n'arrive jamais.
- **Tracer n'est pas émettre.** Le geste consigne un appel ou un message déjà envoyé par le collaborateur ; le jour
  où la messagerie émettra elle-même, elle tracera par ce même cas d'usage.
- **L'adhérent est prévenu par courriel** (gabarit `piece.rectificative_demandee`) : chaque compte adhérent actif du
  dossier reçoit la référence et le motif. Zéro compte n'est pas une erreur, et la réponse le dit.
- Les demandes de démonstration nomment désormais leur pièce.

**Deux gardes du projet ont servi.** Le contrôle de surface des permissions a refusé mes routes : le contrôle
d'accès était caché dans une fonction d'aide, invisible à la lecture du corps de la route. Chaque route appelle
désormais `exiger(...)` en première ligne. Le catalogue des gabarits a exigé un contexte de référence pour le
nouveau courriel.

### Ce qui a été fait, à l'écran

- **Fiche d'une facture (E02)** : « Demander une facture rectificative » ouvre un formulaire. Le motif part
  prérempli avec le verdict du contrôle, à reformuler pour l'adhérent ; la date d'attente est facultative. Si une
  rectificative est déjà ouverte pour la pièce, la fiche l'affiche à la place du bouton : « Rectificative demandée
  le 03/08/2026 (DP-2026-001), suivie dans les pièces attendues ».
- **La fiche ne connaît que la référence de la facture** : l'action cherche la pièce du dossier qui la porte. Si
  **deux pièces** portent la même facture, c'est un doublon, et l'action refuse de choisir.
- **Nouvelle page « Pièces attendues »** (`/pieces/attendues`, liée depuis la boîte de réception) : les demandes
  ouvertes, avec leur motif, la pièce à rectifier et les relances tracées. Chaque geste n'apparaît qu'à qui peut le
  faire : rattacher pour `IDENTIFIER_PIECE`, tracer et classer pour `RELANCER_ADHERENT`, et « lecture seule » sinon.
  Classer demande un motif et une case.

**Reste décoratif** sur la fiche : « Écarter un constat ». Écarter une règle fiscale sur une pièce demande une
conception à part (motif, second regard, conséquence sur la liasse) ; ce n'est pas un bouton qu'on branche en
passant.

**La démonstration ne compte aucun chargé de clientèle** : la relance et le classement sont éprouvés par les tests de
route, sur un compte habilité pour l'occasion, et pas en essai réel.

### Les épreuves

`tests/test_demandes_de_piece.py`, 11 cas : les transitions du domaine, le dossier pris de la pièce, une seule
demande ouverte par pièce, une pièce d'un autre dossier refusée ; par les routes, la demande et le courriel à
l'adhérent de SARL BATIMENT PLUS, la seconde demande refusée, la satisfaction refusée par la pièce à rectifier, par
une pièce reçue avant la demande et par une pièce elle-même à rectifier, puis acceptée, puis refusée une seconde
fois, et le chargé de clientèle qui trace, voit sa relance en double refusée, ne classe pas hors de son portefeuille
(404), classe, et ne relance plus une demande classée.

**Deux écritures de cas étaient fausses, et le code juste.** Le premier chargé de clientèle habilité était un
fiscaliste transverse, qui voyait tout : le refus hors portefeuille ne se mesurait pas. Et j'attendais 403 là où
le projet répond délibérément 404, pour ne pas confirmer l'existence d'un dossier hors périmètre. Un troisième cas
mesurait le garde de date au lieu du garde « pièce à rectifier » : il emploie désormais une pièce récente.

Douze mutations, **toutes tuées** : satisfaire deux fois, pièce à rectifier qui se satisfait, relance en double,
classer deux fois, doublon de demande admis, pièce d'un autre dossier admise, dossier pris ailleurs que de la pièce,
adhérent non prévenu, classement sans contrôle de dossier, relance sans permission, pièce antérieure admise, pièce
à rectifier admise.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Fiche F-2026-0414, comptable | « Rectificative demandée le 03/08/2026 (DP-2026-001), suivie dans les pièces attendues » |
| Fiche F-2026-0435 | bouton « Demander une facture rectificative » |
| Demande pour 0435 | « Demande DP-2026-20F570CF émise. 1 compte adhérent prévenu par courriel. » |
| Seconde demande | « une demande de rectificative est déjà ouverte pour la pièce PJ-2026-0024 : DP-2026-20F570CF… » |
| Fiche 0435 rechargée | « Rectificative demandée le 14/09/2026 » à la place du bouton |
| Demande pour F-2026-0412 | « 2 pièces portent la facture F-2026-0412 (PJ-2026-0900, PJ-2026-0001) : arbitrer le doublon… » |
| Boîte de recette | un courriel à jp.nkoa@batimentplus.cm, référence F-2026-0435 |
| Pièces attendues, comptable | DP-2026-002 listée, « Rattacher la pièce reçue », pas de « Tracer » |
| Rattacher PJ-2026-0013 à DP-2026-002 | « la pièce PJ-2026-0013 est celle qu'il faut rectifier » |
| Rattacher PJ-2026-0019, **premier essai** | **acceptée** : c'est le défaut, corrigé ensuite |
| Rattacher PJ-2026-0019, après correction | « reçue le 21/07/2026, avant la demande DP-2026-002 du 03/08/2026 : elle ne peut pas y répondre » |
| Classer par le comptable, appel direct | « RELANCER_ADHERENT est requise » |

### État à la fin du pas 74

**3 009 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production ;
**87 routes appelées par le frontend sur 139** (62 %), mesurées par le script.

**Ce que le projet sait faire qu'il ne savait pas.** Demander une pièce à un adhérent, le prévenir, rattacher ce qu'il
envoie, et garder la trace datée de chaque relance : la défense du Centre le jour d'une contestation.

*Un domaine qui promet sans route n'est qu'un règlement intérieur : personne ne l'applique, et tout le monde le croit appliqué.*

## Pas 75 — La boîte de réception affichait une collecte inventée

### Pourquoi

Au pas 74, un commentaire de la boîte de réception des pièces (E03) disait : « le canal de réception et le statut
du cycle de vie appartiennent au contexte C · Collecte, **non implémenté**. Ils sont simulés dans
`lib/collecte-demo.ts` ». La collecte existe au backend depuis de nombreux pas, avec ses pièces, leurs canaux et
leurs états. La question était simple : l'écran affichait-il encore la simulation ?

### Ce que la mesure a trouvé

Oui. Chaque ligne était une **facture du jeu de conformité**, et son canal et son statut sortaient d'une table
écrite à la main, par référence. Comparaison avec la collecte réelle :

| Mesure | Résultat |
| --- | --- |
| Factures affichées | 29 |
| Canal faux | **17** |
| Statut faux | **16** |
| F-2026-0412 | « Reçue », donc à traiter ; au backend, **comptabilisée** |
| F-2026-0419, 0421, 0422 | « Rapprochée », « Lue », « Reçue » ; au backend, comptabilisées |
| Pièces reçues sans facture extraite (PJ-2026-0005, 0006, 0028, 0029) | **absentes de l'écran** |

Un comptable qui descendait la file au clavier voyait « Reçue » sur une facture déjà passée au journal, et pouvait la
comptabiliser une seconde fois. Les pièces qu'il fallait justement ouvrir, celles dont rien n'était encore extrait,
n'apparaissaient pas. La conformité, elle, était réelle ; tout ce qui l'entourait ne l'était pas.

Et la barre d'actions groupées offrait « Marquer comme lues », « Demander une rectification » et « Réaffecter » :
trois boutons **sans action ni route**.

### Ce qui a été fait

**La ligne est une pièce de la collecte**, plus une facture. La page construit les lignes côté serveur, par une
jointure de quatre lectures :

| Donnée | Source |
| --- | --- |
| La pièce : canal, état, montant, fournisseur, dates | `GET /collecte/pieces` |
| « Rectif. demandée » | une demande **réellement ouverte** sur la pièce (`GET /collecte/demandes`), et non un verdict bloquant |
| La conformité | le contrôle du flux, joint par référence de facture |
| Le nom de l'entreprise | le portefeuille ; à défaut, le NIU (un rôle qui lit les pièces sans lire le portefeuille voit un écran juste) |

- **Deux pièces peuvent porter la même facture** : la clé de ligne est l'identifiant de pièce. F-2026-0412
  apparaît deux fois, « Lue » par le portail (le doublon à arbitrer) et « Comptabilisée » par WhatsApp.
- **Une pièce sans facture extraite n'a pas de verdict** : sa colonne de conformité dit « à identifier », son aperçu
  dit qu'aucune facture n'a été extraite, et elle ne s'ouvre pas en E02, qui est désigné par la référence de facture.
- « Archivée » rejoint les statuts de pastille ; les canaux du filtre sont ceux des pièces présentes.
- **`lib/collecte-demo.ts` est supprimé.**
- Les trois boutons décoratifs sont retirés ; la barre dit qu'aucune action groupée n'est disponible, et que chaque
  pièce se traite sur son rapport. La rectification se demande pièce par pièce, avec son motif (pas 74).

**Une erreur de ma part, rattrapée.** En supprimant le fichier simulé, j'ai lancé par réflexe `git rm --cached`, qui
modifie l'index git. Aucune opération git n'a été autorisée sur ce projet. J'ai annulé la mise en index
(`git reset -q HEAD -- …`) : la suppression reste dans l'arbre de travail, non indexée, comme tout le reste du travail
depuis le premier pas. Le seul fichier indexé, `Backend_erp_cga/app/moteur/jsonlogic.py`, l'était déjà au début de la
session.

### Ce qui n'a pas été éprouvé comme d'habitude

**Aucun code backend n'a changé** : pas de nouveau test, pas de mutation. Le frontend n'a pas de banc de test.
L'épreuve est la mesure elle-même (le script de comparaison ci-dessus, rejoué contre la collecte de démonstration)
et l'essai réel.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Réviseur (portée transverse) | 30 pièces à l'API, **30 lignes** à l'écran |
| Comptable C-004 | 18 pièces à l'API, **18 lignes** à l'écran |
| F-2026-0412 | deux lignes : « Portail · Lue · Majeur » et « WhatsApp · Comptabilisée · Majeur » |
| PJ-2026-0028 | « SARL BATIMENT PLUS · 05/08/2026 · Application mobile · Reçue · à identifier » |
| F-2026-0424 | « Application mobile · Rectif. demandée · Bloquant » (la demande DP-2026-002 est ouverte) |
| Actions groupées | « Marquer comme lues » et « Réaffecter » absents |

### État à la fin du pas 75

**3 009 tests passent** (inchangé, aucun code backend modifié). Frontend : typage, lint, construction de production ;
**87 routes appelées par le frontend sur 139** (62 %).

**Ce que le projet sait faire qu'il ne savait pas.** Montrer au comptable la file des pièces telle qu'elle est, et non
telle qu'une table de démonstration l'imaginait.

*Une donnée simulée « en attendant » devient fausse le jour où la vraie existe, et personne ne le remarque : elle a toujours l'air juste.*

## Pas 76 — Le tableau de bord ne montrait que le prénom de vrai

### Pourquoi

Le pas 75 a trouvé une simulation « temporaire » survivante dans la boîte de réception. La question suivante allait
de soi : en restait-il d'autres ? La recherche des mots « TEMPORAIRE », « simulé », « factice », « non implémenté »
dans le frontend a mené à `lib/donnees-demo.ts`, importé par une seule page : **le tableau de bord, la page
d'accueil de chaque collaborateur**.

### Ce que la relecture a trouvé

L'en-tête de la page le disait honnêtement : seul le prénom venait de la session ; les quatre indicateurs, les
échéances, les anomalies et les « dossiers incomplets » venaient de `donnees-demo.ts`, parce que « le contexte
J · Pilotage n'existe pas ». **Le pilotage existait**, comme les obligations, la collecte et la conformité, qui
rendent tout ce que la page affichait.

| Ce que chaque collaborateur voyait, quel que soit son portefeuille | Ce qui était vrai |
| --- | --- |
| « 18 dossiers suivis, sur 128 au cabinet » | 6 pour un réviseur, 3 pour le comptable C-004 |
| « 6 échéances sous 7 jours, dont 5 au 15 août » | 12 (réviseur), 10 (comptable), et 94 ou 73 en retard |
| « 37 pièces en attente, 12 arrivées aujourd'hui » | 16 (réviseur), 11 (comptable) |
| « 3 anomalies bloquantes, 1 depuis 22 jours » | 4 |
| La date : « 9 août 2026 » | le jour réel |
| Une échéance du 15 août affichée « 24 jours de retard » le 9 août | incohérente avec elle-même |

Et trois autres écarts, trouvés en branchant la page :

- **Le lien « File complète » menait à `/conformite`**, une page qui n'existe pas. L'entrée de menu « Conformité »,
  elle, est marquée « à venir » et inerte : la vérification de toutes les entrées du menu contre les pages présentes
  n'a trouvé que celle-là, correctement neutralisée.
- **Un compteur de notifications « 4 » écrit en dur** dans l'en-tête de la boîte de réception et de la fiche d'une
  pièce. Aucune notification n'existe.
- **Le type frontend d'une pièce ne correspondait pas à la réponse.** Il déclarait `en_attente_de_traitement`, que
  la route ne rend pas : c'est une propriété de l'entité, jamais sérialisée. TypeScript ne voit pas l'écart entre un
  type et une réponse réseau ; le champ valait `undefined`. **Le compte des pièces « en cours de traitement » de
  l'espace adhérent valait toujours zéro.** Le type déclarait aussi le montant en chaîne ; le backend rend un nombre.

### Ce qui a été fait

**Le tableau de bord lit la journée réelle** (`lireLaJournee`) :

| Élément | Source |
| --- | --- |
| Dossiers suivis | `GET /portefeuille/entreprises` |
| Échéances | l'échéancier de chaque dossier ; non déposées, en retard ou à 30 jours au plus, par date |
| Échéances sous 7 jours, en retard | les mêmes lignes, `jours_restants` et `en_retard` tels que le backend les calcule |
| Pièces en attente, dont à identifier | `GET /collecte/pieces` : `traitee` faux ; `identifiee` faux |
| Anomalies à traiter | les constats bloquants puis majeurs du contrôle, sur les pièces ni comptabilisées ni archivées |
| Pièces attendues | les demandes ouvertes, regroupées par dossier : nombre, bloquantes, plus ancienne |

- **La page compte, elle ne décide pas.** Retard, jours restants, traitement, gravité : tout arrive résolu.
- **« Dossiers incomplets » devient « Pièces attendues »** : il affichait des pièces « manquantes sur attendues » que
  rien ne calcule. Ce que le système sait, ce sont les pièces demandées ; le panneau les montre sous ce nom.
- Un montant que le backend n'estime pas s'écrit « non estimé », jamais zéro.
- **Un échéancier illisible ne fait pas tomber la page** : il est ignoré, et l'indicateur des dossiers le dit.
- **Un rôle sans lecture des pièces** voit « hors de votre rôle » dans les panneaux concernés.
- Un échéancier par dossier, faute de lecture consolidée : sur quelques dizaines de dossiers, les appels partent en
  parallèle. Au-delà, il faudra une route consolidée au backend, pas un cache ici ; c'est écrit dans le code.
- **`lib/donnees-demo.ts` est supprimé** (par `rm`, sans commande git), et les compteurs « 4 » retirés.
- Le type `LignePiece` du frontend reprend **champ pour champ** le modèle du backend ; l'espace adhérent et le tableau
  de bord lisent `!traitee`.
- Une erreur de lint antérieure, dans l'espace adhérent (un `<a>` vers le tableau de bord au lieu d'un lien de
  navigation), est corrigée en passant.

### Ce qui n'a pas été éprouvé comme d'habitude

Aucun code backend n'a changé : pas de test ni de mutation. L'épreuve est la comparaison, en essai réel, entre
chaque chiffre affiché et le même chiffre recalculé directement depuis l'API, pour trois rôles.

### L'essai réel

| Rôle | Écran | Recalculé depuis l'API |
| --- | --- | --- |
| Réviseur | 6 dossiers · 12 sous 7 jours, 94 en retard · 16 pièces en attente, dont 4 à identifier | 6 · 12 · 94 · 16 · 4 |
| Comptable C-004 | 3 dossiers · 10 sous 7 jours, 73 en retard · 11 pièces, dont 1 à identifier | 3 · 10 · 73 · 11 · 1 |
| Compte C-007, rôle chargé des formalités | 6 · 12 · 94 · 16 · 4 | 6 · 12 · 94 · 16 · 4 |
| Adhérent de SARL BATIMENT PLUS, espace adhérent | 5 pièces en cours de traitement | 5 non traitées (avant : 0 affiché) |

Aucune des anciennes phrases inventées (« sur 128 au cabinet », « dont 5 au 15 août ») n'apparaît plus.

**Les 94 retards sont réels** : la démonstration ne dépose presque aucune déclaration de 2026. C'est une information sur
le jeu de démonstration, que l'ancien écran masquait sous des chiffres rassurants.

### État à la fin du pas 76

**3 009 tests passent** (inchangé, aucun code backend modifié). Frontend : typage, lint, construction de production ;
**87 routes appelées par le frontend sur 139** (62 %).

**Ce que le projet sait faire qu'il ne savait pas.** Ouvrir la journée d'un collaborateur sur son portefeuille à lui, à
la date du jour, avec des chiffres qu'on peut recompter.

*Un tableau de bord inventé est pire qu'un tableau de bord vide : le vide fait poser la question, l'inventé y répond faux.*

## Pas 77 — Une confrontation des types du frontend au schéma du backend, et le grand livre sans montants

### Pourquoi

Le pas 76 a corrigé un champ de pièce que le frontend lisait et que le backend ne rendait pas. C'était une instance.
La classe est plus large : `appeler<T>(chemin)` affirme au compilateur que la réponse a la forme `T`, et **rien ne le
vérifie**. Le typage passe, l'écran s'affiche, le champ vaut `undefined`. Ce pas corrige la classe, puis ce qu'elle
trouve.

### L'outil : deux scripts qui se répondent

**`Frontend_erp_cga/outils/types-des-appels.mjs`** lit chaque appel `appeler<T>(…)` **avec le compilateur
TypeScript** (et non par expressions régulières) : la méthode, le chemin (morceaux interpolés remplacés par `{}`,
chaîne de requête retirée) et les champs de `T` à plat, en descendant dans les objets et les tableaux. Il s'arrête sur
ce qu'il ne sait pas lire (`Record<string, …>`, `unknown`, union de plusieurs objets) sans inventer de champ.

**`Backend_erp_cga/outils/contrat_des_ecrans.py`** fait correspondre chaque appel à sa route du schéma OpenAPI, résout
la réponse 200 ou 201 (références, tableaux, `T | null`) et confronte les champs :

| Verdict | Sens | Effet |
| --- | --- | --- |
| ABSENT | le frontend lit un champ que la réponse ne contient pas | échec du script |
| SANS ROUTE | aucun chemin du schéma ne correspond, avec cette méthode | échec du script |
| ILLISIBLE | chemin non littéral, ou réponse sans schéma d'objet | signalé, non bloquant : non vérifié, pas juste |

Usage, depuis `Backend_erp_cga` : `CGA_PERSISTANCE=memoire python -m outils.contrat_des_ecrans [--detail]`.

**Ce qu'il ne vérifie pas**, écrit dans son en-tête : le **type** de chaque champ (le montant rendu en nombre et
attendu en texte du pas 76 lui échapperait), les champs que le frontend ignore (ce n'est pas un défaut), les corps de
requête (le backend les refuse déjà par `extra="forbid"`).

### Le script s'est trompé deux fois avant d'avoir raison

- **Il comparait la mauvaise route.** Un `{}` du frontend pouvait couvrir plusieurs segments, et il préférait les routes
  littérales : `/acquisition/dossiers/{}` désignait une route voisine, et la fiche d'un dossier était jugée contre une
  liste. Il essaie désormais **segment pour segment** d'abord, plusieurs segments ensuite, et en dernier le chemin
  privé de son `{}` final (une chaîne de requête construite à part).
- **Il déclarait absent ce qu'il ne pouvait pas lire.** Les lignes d'une proforma sont `list[dict[str, str]]` au
  backend, sans champs nommés. Ces sous-arbres sont maintenant **opaques** : leurs enfants sont « non vérifiés »,
  jamais « absents ».

Chaque constat a été **confirmé contre une vraie réponse** avant d'être corrigé.

### Ce qu'il a trouvé

| Appel | Champs lus sans exister | Effet à l'écran |
| --- | --- | --- |
| Grand livre | `numero`, `debit`, `credit` (le backend rend `cle_ecriture`, `sens`, `montant`) | **chaque ligne affichait « AC / undefined » et « — » au débit comme au crédit** : seul le solde progressif était rempli |
| Balance | `libelle` (la balance se calcule sur les écritures ; l'intitulé est au plan) | **la colonne « Intitulé » était vide pour chaque compte** |
| Santé comptable | `trous_de_sequence.manquants` (le backend dit `numeros_manquants`) | latent : l'écran ne compte que les ruptures |
| Plan comptable | `classe`, `sens_normal` | latent : aucun écran ne les lit |

Le commentaire du type `LigneEcriture`, dans le même fichier, racontait déjà cette faute : « ce type déclarait `debit` et
`credit`, qui n'ont jamais existé côté backend… le premier écran à s'en servir a affiché des montants vides ». Elle avait
été corrigée pour les lignes d'écriture, et gardée pour le grand livre, trois types plus bas.

### Ce qui a été corrigé

- **Les quatre types** reprennent les champs du backend, chacun avec un commentaire qui date l'écart.
- **Le grand livre** affiche la clé de l'écriture (« 2026/AC/000003 ») et range le montant dans la colonne de son sens.
- **La balance** lit l'intitulé au plan comptable, joint par numéro de compte ; un compte absent du plan de référence
  affiche un tiret, et un plan illisible ne fait pas tomber la balance.

### Les épreuves

**Le script, éprouvé comme un test** : quatre défauts réintroduits un par un dans les types, et restaurés ensuite.

| Défaut réintroduit | Verdict |
| --- | --- |
| Le champ inventé du pas 76 (`en_attente_de_traitement`) | **détecté**, ABSENT |
| `debit` à la place de `sens` dans le grand livre | **détecté**, ABSENT |
| `manquants` à la place de `numeros_manquants`, champ imbriqué | **détecté**, ABSENT |
| `/plans-comptables`, un appel vers nulle part | **détecté**, SANS ROUTE |

Aucun code applicatif du backend n'a changé (seuls ses outils) : la suite reste celle du pas 74.

### L'essai réel

| Écran | Avant | Après |
| --- | --- | --- |
| Grand livre du 401, SARL BATIMENT PLUS | « 03/07/2026 AC / undefined LOCATION ENGINS BONABÉRI — — (1 669 500) » | « 03/07/2026 2026/AC/000003 LOCATION ENGINS BONABÉRI — 1 669 500 (1 669 500) » ; les trois crédits (1 669 500, 2 350 000, 1 431 000) retombent sur le solde de 5 450 500 |
| Balance | « 401 0 5 450 500 » (intitulé vide) | « 401 Fournisseurs, dettes en compte 0 5 450 500 » |

### Ce qui reste non vérifié

**Dix appels sont ILLISIBLES**, et le script les nomme à chaque passage :

- **sept routes rendent un dictionnaire libre** (`dict[str, Any]`) au lieu d'un modèle : la fiche d'un dossier
  d'acquisition, son questionnaire, sa qualification (lecture et enregistrement), son chiffrage, la demande de règlement,
  et la révocation de sessions (`dict[str, int]`). Leur schéma OpenAPI ne décrit rien, donc rien ne se confronte. C'est
  un défaut de documentation du backend : le jour où ces routes déclareront leur modèle, le script les vérifiera sans
  changement ;
- **trois appels ont un chemin non littéral** : l'aide commune des actions de collecte (pas 74) et deux lectures du
  social, qui construisent leur chemin dans une variable.

**Pourquoi ce n'est pas un test de la suite.** Depuis la scission, le backend et le frontend sont deux dépôts, et la
chaîne d'intégration du backend refuse tout test sauté. Un test qui exigerait le frontend et Node serait sauté partout
sauf ici. L'outil se lance donc à la main, comme la mesure de couverture, et le journal dit quand il a été passé.

### État à la fin du pas 77

**3 009 tests passent** (inchangé). Frontend : typage, lint, construction de production.
**Contrat des écrans : 61 appels vérifiés, 0 champ absent, 10 non vérifiés.** **87 routes appelées sur 139** (62 %).

**Ce que le projet sait faire qu'il ne savait pas.** Dire, à la demande, si un écran lit des champs que le backend ne
rend pas, au lieu de le découvrir devant un grand livre sans montants.

*Le compilateur garantit que le code est d'accord avec lui-même. Personne ne garantissait qu'il était d'accord avec le serveur.*

## Pas 78 — Plus aucun appel invérifiable : sept routes typées, et un outil qui sait lire davantage

### Pourquoi

Le pas 77 a laissé dix appels « ILLISIBLES » : l'outil de confrontation ne pouvait ni confirmer ni infirmer ce que ces
écrans lisaient. Un non-vérifié n'est pas un juste. Ce pas les rend tous vérifiables.

### D'où venaient les dix

| Cause | Appels | Côté |
| --- | --- | --- |
| La route rend un dictionnaire libre (`dict[str, Any]`, `dict[str, int]`) | fiche d'un dossier d'acquisition, questionnaire, qualification (lecture et enregistrement), chiffrage, révocation de sessions | backend : **le schéma OpenAPI ne décrivait aucun champ** |
| La route répond 202, que l'outil ne lisait pas | demande de règlement | l'outil |
| Le chemin est une concaténation de deux gabarits (`…/salaries` + `?a_la_date=…`) | deux lectures du social | l'outil |
| Le chemin passe par une fonction d'aide | l'aide commune des gestes sur une demande de pièce (pas 74) | le code |

### Ce qui a été fait

**Au backend, sept routes déclarent leur modèle de réponse** : `FicheDuDossier` (le dossier commercial et ses
`ProformaDuDossier`), `QuestionnairePublie`, `EtatDeQualification` (et son `Avancement`), `PropositionChiffree`,
`SessionsFermees`, `AccuseDOubli`. Ce n'est pas qu'un confort d'outil : la documentation OpenAPI de ces routes ne disait
rien de ce qu'elles rendent, et elle le dit désormais.

- **La qualification a trois formes** (non commencée, lue, enregistrée), qui ne portent pas les mêmes champs. Un seul
  modèle, dont les champs propres à une forme sont facultatifs, et `response_model_exclude_unset` : la réponse garde
  exactement ses champs, sans ajouter de `null` qu'un écran lirait comme une valeur.
- **Les totaux d'une proposition** sont des propriétés du domaine ; `PropositionChiffree` en fait des champs calculés.
- **`AccuseDOubli`** ne porte que la phrase : une réponse qui dirait si l'adresse est connue permettrait d'énumérer les
  comptes du cabinet. Le modèle l'écrit.

**La preuve que rien n'a changé pour les écrans : une capture avant, une capture après.** Un script joue le parcours
entier (demande, affectation, questionnaire, qualification vide, partielle avec note, complète, lecture, chiffrage avec
débours, fiche du dossier, révocation, oubli de mot de passe) et enregistre chaque réponse ; il est rejoué après le
typage, et les deux captures sont comparées **au champ près**, références aléatoires normalisées. Résultat : **neuf
réponses identiques**.

**Ma faute, rattrapée par cette capture.** À la première comparaison, trois routes ne répondaient plus : questionnaire,
chiffrage et fiche du dossier renvoyaient une erreur 422 réclamant leurs propres champs en paramètres de requête. J'avais
inséré les classes de modèle **entre le décorateur `@routeur` et la fonction** : le décorateur enregistrait la classe
comme route. La console d'acquisition aurait été cassée. Les classes sont remontées au-dessus des décorateurs, et la
comparaison est repassée.

**Une preuve plus faible, dite comme telle.** Le dossier capturé n'avait pas encore de proforma : la liste
`proformas` a été comparée vide. Ses entrées sont construites, comme avant, en chaînes déjà sérialisées, que le modèle
reprend telles quelles ; l'équivalence est raisonnée, pas mesurée sur une proforma réelle.

**L'outil lit davantage** : les réponses 202, et les chemins concaténés par `+` (deux littéraux concaténés restent un
littéral).

**Au frontend**, les trois gestes sur une demande de pièce écrivent leur appel typé au point d'usage ; l'aide ne reçoit
plus qu'une promesse et garde la gestion d'erreur.

### Les épreuves

- **Contrat des écrans : 73 appels sur 73 vérifiés** (les trois gestes de collecte comptent désormais chacun pour un).
- **Les routes nouvellement typées sont réellement contrôlées** : trois défauts réintroduits dans les types du frontend,
  tous détectés, fichiers restaurés.

| Défaut réintroduit | Verdict |
| --- | --- |
| Un champ inventé dans la fiche d'un dossier | ABSENT |
| `numero_proforma` au lieu de `numero`, dans la liste imbriquée des proformas | ABSENT |
| `attendues` au lieu de `total`, dans l'avancement de la qualification | ABSENT |

- **3 009 tests passent** sur PostgreSQL réel, après le typage.

### L'essai réel

| Parcours | Résultat |
| --- | --- |
| Fiche d'un dossier d'acquisition, direction | le dossier et son questionnaire s'affichent |
| Enregistrer la qualification complète, par l'écran | « Qualification complète : le dossier peut être chiffré. » ; avancement 8 sur 11, complète |
| Chiffrer, par l'écran | proposition rendue (base 250 000, plancher 200 000, plafond 375 000) ; la fiche passe à « Chiffrée » |
| Fermer les sessions d'un comptable, écran des comptes | « 1 session fermée. » |
| Rattacher une pièce reçue avant la demande, pièces attendues | la phrase du refus, comme au pas 74 |

### Ce que l'outil ne vérifie toujours pas

- **Le type des champs**, chaîne ou nombre (limite du pas 77).
- **La présence effective d'un champ facultatif.** Avec `response_model_exclude_unset`, un champ décrit par le schéma peut
  manquer dans une forme de la réponse : `commencee` n'est pas rendu par l'enregistrement d'une qualification. L'outil voit
  le champ au schéma et le compte présent. Aucun écran ne lit aujourd'hui `commencee` sur cette réponse ; c'est écrit ici
  pour que ce ne soit pas découvert plus tard.

### État à la fin du pas 78

**3 009 tests passent.** Frontend : typage, lint, construction de production.
**Contrat des écrans : 73 appels vérifiés, 0 absent, 0 non vérifié.** **87 routes appelées sur 139** (62 %).

**Ce que le projet sait faire qu'il ne savait pas.** Documenter chaque réponse lue par un écran, et dire pour chacune, sans
exception, que l'écran ne lit rien qui n'existe.

*Un contrôle qui laisse une zone « illisible » dit où chercher le prochain défaut. Tant qu'elle existe, il n'a pas fini.*

## Pas 79 — Le contrat des écrans compare aussi la nature et la nullité des champs

### Pourquoi

Après les pas 77 et 78, l'outil de confrontation vérifiait que chaque champ lu par un écran **existe** dans la réponse.
Il laissait deux limites écrites : la **nature** du champ (un nombre lu comme du texte : le montant du pas 76 serait
passé) et sa **nullité** (un champ que la réponse peut rendre `null`, déclaré toujours présent à l'écran).

### Ce qui a été fait, dans l'outil

- **Chaque champ reçoit sa nature JSON**, des deux côtés : `texte`, `nombre`, `booleen`, `tableau`, `objet`, ou `autre`.
  Côté frontend, le compilateur TypeScript (une union de littéraux comme `"DEBIT" | "CREDIT"` est du texte) ; côté
  backend, le schéma OpenAPI, qui décrit la **sérialisation** : un `Decimal` sort en texte, un `float` en nombre.
  `null` est retiré avant de conclure. Un champ `autre` n'est jamais comparé.
- **Chaque champ reçoit sa nullité**, des deux côtés.
- **Deux verdicts bloquants de plus** :

| Verdict | Sens |
| --- | --- |
| TYPE | le champ existe, mais sa nature diffère : un nombre lu comme du texte, un tableau lu comme un objet |
| NULLITÉ | la réponse peut rendre le champ `null`, et l'écran le déclare toujours présent |

**Ce que l'outil compare réellement** : 958 couples de champs dont la nature est connue des deux côtés. Dix ne le sont
pas, et c'est juste : la valeur d'un paramètre du référentiel (texte, nombre ou booléen selon le paramètre) et l'attribut
fiscal d'une ligne d'écriture, déclaré `unknown` à l'écran.

**Ce qu'il ne voit toujours pas**, écrit dans son en-tête : la nullité d'un champ `unknown` (TypeScript réduit
`unknown | null` à `unknown`), et les **valeurs** d'une énumération.

### Ce que la nature a trouvé

**Rien.** 958 champs comparés, aucune divergence : les types avaient été alignés à la main aux pas 76 et 77. Ce résultat,
trop propre pour être cru sans épreuve, a été éprouvé (voir plus bas).

### Ce que la nullité a trouvé

La première mesure a relevé **12 champs**. Sept étaient des faux positifs (`attribut_fiscal`, justement déclaré
`unknown | null`) ; c'est ce qui a conduit à écarter les champs `autre`. Restaient cinq cas réels, sans défaut visible
aujourd'hui, mais faux :

| Champ | Réalité du backend | Ce que l'écran supposait | Risque |
| --- | --- | --- | --- |
| `detail_rejets.piece`, `.code_regle`, `.motif` (déclaration de TVA) | peuvent être `null` | toujours présents | la clé de ligne était `${piece}${code_regle}` : deux rejets sans pièce auraient donné deux fois la clé « nullnull » |
| `sens_solde` (balance) | `null` pour un compte soldé | toujours présent | latent : aucun écran ne le lit |
| `commencee` (lecture d'une qualification) | toujours renseigné, mais **mon modèle du pas 78** le décrivait `bool \| None` | toujours présent | le défaut était dans le modèle, pas dans l'écran |

### Ce qui a été corrigé

- **`LigneRejet`** reprend le modèle du backend champ pour champ, `ecriture` et `compte` compris. L'écran des déclarations
  prend pour clé l'écriture, le compte et le rang, toujours renseignés ; il affiche l'écriture quand la pièce manque, un
  tiret quand la règle manque, « motif non renseigné » quand le motif manque.
- **`sens_solde`** est déclaré `"DEBIT" | "CREDIT" | null`.
- **`EtatDeQualification.commencee`** devient `bool = False` au backend : une qualification est commencée ou non, jamais
  inconnue. Le défaut ne s'émet pas, puisque les routes n'envoient que les champs renseignés. La capture du pas 78, rejouée,
  est **identique**.

### Les épreuves

**Le défaut du pas 76 réintroduit** (`montant_ttc` déclaré en texte) : **détecté**, « montant_ttc (écran texte, réponse
nombre) ».

| Défaut réintroduit | Verdict |
| --- | --- |
| La pièce d'un rejet déclarée non nulle | **NULLITÉ** |
| Le sens du solde déclaré non nul | **NULLITÉ** |
| Les relances d'une demande déclarées en objet au lieu d'un tableau | **TYPE**, « écran objet, réponse tableau » |
| `traitee` déclaré en texte | **TYPE**, « écran texte, réponse booleen » |

Tous les fichiers restaurés après chaque essai ; le typage repasse.

**3 009 tests passent** sur PostgreSQL réel après le resserrement du modèle de qualification.

### L'essai réel

| Écran | Résultat |
| --- | --- |
| Déclaration de TVA de SARL BATIMENT PLUS, juillet 2026 | « Pièce · Règle · Motif du rejet · TVA écartée » puis « PJ-2026-0001 · FAC-ACH-007 · Le règlement en espèces de cette facture dépasse le seuil légal… », comme l'API (379 350) |

### État à la fin du pas 79

**3 009 tests passent.** Frontend : typage, lint, construction de production.
**Contrat des écrans : 73 appels vérifiés ; noms, natures et nullité ; 0 écart.** **87 routes appelées sur 139** (62 %).

**Ce que le projet sait faire qu'il ne savait pas.** Dire qu'un écran ne lit pas un nombre comme du texte, ni une valeur
toujours présente là où le serveur peut ne rien rendre.

*Un outil qui ne trouve rien doit prouver qu'il aurait trouvé : sans cette preuve, « aucun écart » ne veut rien dire.*

## Pas 80 — « À combien de pour cent ? » : une grille des écrans, et une mesure qui la confronte

### Pourquoi

La question a été posée : « nous sommes déjà à combien de pour cent ? ». Le projet n'avait pas de réponse mesurée.
Deux chiffres existaient, et aucun ne répondait :

- **la couverture des routes** (62 %) dit quelle part du backend un écran appelle, pas si les écrans attendus sont
  faits ; elle ignore en plus la méthode : lire les pièces (`GET /collecte/pieces`) y comptait comme les déposer
  (`POST`, même chemin) ;
- **le contrat des écrans** (100 %) dit que les écrans existants lisent juste, pas qu'ils existent.

Et l'inventaire des écrans (`07-inventaire-ecrans.md`) portait un tableau « ce qui est construit — 18 août 2026 » qui
affirmait encore que le tableau de bord était fictif et l'écran des comptes en lecture seule. Mesurer à partir de lui
aurait reproduit la faute des pas 75 et 76 : une affirmation écrite une fois et jamais revérifiée.

### Ce qui a été fait

**Une grille déclarative**, `Docs/architecture/avancement/grille-des-ecrans.yaml` : les **14 écrans de l'inventaire**
(E00 à E13, avec leur priorité) et **7 espaces hors inventaire** (acquisition, comptes, pilotage, veille des seuils,
social, souscription, exploitation). Pour chacun, ses pages et **les gestes qu'il doit permettre**, chaque geste
rattaché à sa route backend, ou déclaré `route: null` avec la raison. **142 gestes.**

⚠️ **Les gestes sont une proposition du pas 80**, déduite de l'inventaire, des parcours par profil et des routes. Ils sont
à valider par le cabinet. Ajouter un geste fait baisser le pourcentage : la mesure suit la cible, et c'est voulu.

**Une mesure**, `Backend_erp_cga/outils/avancement_des_ecrans.py` :

| État d'un geste | Sens |
| --- | --- |
| BRANCHÉ | la route existe, et **une page de l'écran atteint** un appel qui la désigne avec cette méthode |
| À BRANCHER | la route existe ; aucune page de l'écran ne l'atteint |
| SANS BACKEND | aucune route ne le permet encore |

**La grille est contrôlée avant d'être mesurée** : une route citée qui n'existe pas, une page absente, un « sans backend »
sans note la font refuser. Les routes que la grille ne cite pas sont signalées (aucune aujourd'hui, hors une liste
d'infrastructure écrite dans le script).

### La mesure s'est trompée deux fois avant d'être juste

**Premier chiffre : 56 %, et il était flatteur.** Un geste comptait « branché » dès qu'**un écran quelconque** appelait
la route. L'accueil adhérent (E06) et « Mes échéances » (E09) sortaient à 100 % parce que des écrans **collaborateurs**
lisaient les mêmes routes.

**Correction : rattacher chaque appel aux pages qui l'atteignent.** Le relevé du frontend (`types-des-appels.mjs
--pages`) part de chaque `page.tsx` et des `layout.tsx` qui l'enveloppent, et suit avec le compilateur **les symboles
employés** (composants, fonctions, actions serveur) jusqu'aux appels `appeler(…)`. Suivre les symboles plutôt que les
imports évite qu'une page qui importe une fonction d'un module soit créditée de tous les appels du module. Le relevé
inclut aussi, désormais, les appels **non typés** : sans eux, la méthode d'un appel manquait. Chiffre : 51 %.

**Deuxième correction : la grille rattachait des gestes au mauvais écran.** Le script signale maintenant, pour un geste
« à brancher », les pages qui l'atteignent ailleurs. Six cas :

| Geste | Atteint par | Verdict |
| --- | --- | --- |
| Inscrire un changement de régime | la veille des seuils | **erreur de grille**, déplacé |
| Lire l'éligibilité des adhérents | la veille des seuils | **erreur de grille**, déplacé |
| Enrôler un second facteur | la porte posée sur les obligations | **erreur de grille** : la page est ajoutée à E00 |
| Lire la fiche complète, les statuts d'un dossier | la saisie, la clôture | **vrai manque** : la fiche adhérent 360° n'existe pas |
| Les pièces attendues, les échéances, côté adhérent | les écrans collaborateurs | **vrai manque** : l'espace adhérent ne les montre pas |

### Le résultat

**53 % des gestes attendus sont branchés** (75 sur 142 ; 56 à brancher ; 11 sans backend), soit **57 % des gestes que
le backend permet déjà**.

| Lecture | Avancement |
| --- | --- |
| Priorité 1 : E00 structure, E02 détail d'une pièce | **75 %** (12 sur 16) |
| Priorité 2 : E03 boîte de réception, E06 accueil adhérent, E07 dépôt | 53 % (9 sur 17) |
| Priorité 3 : E01 tableau de bord, E05 échéancier, E08 hors ligne, E09 mes échéances | 56 % (9 sur 16) |
| Priorité 4 : E04 fiche adhérent 360°, E13 création d'entreprise | **24 %** (4 sur 17) |
| Priorité 5 : E10 saisie, E11 constructeur de règle, E12 clôture | 57 % (13 sur 23) |
| Hors inventaire (7 espaces) | 53 % (28 sur 53) |

Les écarts les plus nets : **E13 création d'entreprise à 11 %** (8 gestes d'écriture à brancher), **E07 dépôt d'un
justificatif à 0 %**, **la souscription à 0 %** (12 gestes), **l'exploitation à 0 %** (7 gestes), et **E08 hors ligne**,
qui relève d'une application mobile inexistante. En tête : **E01 tableau de bord à 100 %**, la console d'acquisition à
93 %, les comptes à 90 %.

Les **11 gestes sans backend** : recherche globale, notifications, écarter un constat, marquer des pièces comme lues,
photographier un document, les deux gestes hors ligne, les trois écritures du référentiel (modifier un paramètre,
construire une règle, valider une version), rétablir un compte suspendu.

### Les épreuves de l'outil

| Essai | Résultat |
| --- | --- |
| Une route inventée dans la grille | grille refusée, code 1 |
| Une page inexistante dans la grille | grille refusée, code 1 |
| Un geste sans backend et sans note | grille refusée, code 1 |
| Remplacer une condition par `false` dans la fiche d'une pièce | **aucune baisse** : l'analyse est statique, le composant reste écrit dans la page |
| Retirer réellement l'appel de la demande de rectificative | E02 passe de 4 à 3 gestes, le total de 53 à 52 % |

La quatrième ligne est une **limite**, écrite : la mesure suit ce que le code référence, pas ce qui s'exécute. Du code mort
dans une page la flatterait.

### Ce qui a été mis à jour ailleurs

- `07-inventaire-ecrans.md` : le tableau périmé est remplacé par un renvoi à la grille et à la mesure, daté, avec la
  consigne « rejouer la mesure plutôt que la recopier » ; la phrase « les écrans d'administration ne modifient rien » est
  rectifiée.
- Le contrat des écrans relit maintenant les appels non typés : **82 appels, 0 écart**.

Aucun code applicatif n'a changé (outils et documentation) : **3 009 tests**, inchangés.

### État à la fin du pas 80

**Avancement des écrans : 53 %** (57 % sur ce que le backend permet). **Contrat des écrans : 82 appels, 0 écart.**
**Couverture des routes : 87 sur 139** (62 %).

**Ce que le projet sait faire qu'il ne savait pas.** Répondre à « à combien de pour cent ? » par un chiffre qui se rejoue,
écran par écran, et qui dit ce qu'il ne mesure pas.

*Un pourcentage sans liste de référence est une humeur. Avec une liste, il devient une question qu'on peut contester ligne par ligne.*

## Pas 81 — L'adhérent dépose sa pièce, voit ce que le cabinet attend, et ses échéances

### Pourquoi

Au pas 80, la mesure d'avancement plaçait l'espace adhérent loin derrière : **E07 dépôt d'un justificatif à 0 %**, E09
« mes échéances » à 0 %, E06 accueil à 67 %. Après un échange sur l'écart à l'objectif, la décision a été prise
d'enchaîner les lots d'écrans, en commençant par celui-ci : c'est le geste le plus attendu de l'adhérent.

### Ce que la relecture a trouvé

Le commentaire de l'espace adhérent disait que le dépôt manquait parce que **« le magasin de fichiers n'a pas d'adaptateur
réel »**. C'était faux depuis longtemps : le magasin local sur disque existe, avec la route d'envoi du fichier, qui lit
le type réel dans les octets, borne la taille à 20 Mo et recalcule l'empreinte. Une affirmation périmée, encore, bloquait
un geste que le backend permettait.

Et **Next.js refuse par défaut toute action serveur de plus d'un mégaoctet** : une facture photographiée au téléphone
aurait été refusée avant même d'atteindre le backend, sans message lisible.

### Ce qui a été fait

| Écran | Geste | Route |
| --- | --- | --- |
| E07 | Envoyer le document, puis déclarer la pièce avec l'empreinte rendue | `POST /collecte/fichiers`, puis `POST /collecte/pieces` |
| E06 | « Ce que le cabinet attend de vous » : les demandes ouvertes du dossier | `GET /collecte/demandes` |
| E09 | « Mes échéances » : les obligations non déposées, retards d'abord | `GET /obligations/dossiers/{niu}/echeancier` |

- **Mobile d'abord, un seul champ obligatoire** : le document. Nature, fournisseur, numéro, date, montant et un mot pour le
  cabinet sont repliés sous « Préciser (facultatif) ». Le sélecteur accepte photo et PDF sans imposer l'appareil photo.
  Cibles tactiles d'au moins 44 px.
- **Le canal est posé par l'écran** (`PORTAIL`), pas choisi par l'adhérent : le laisser choisir fausserait les délais de
  collecte par canal.
- **La seconde étape ne croit pas la première** : le backend relit le fichier et recalcule l'empreinte. **Le dépôt est
  rejouable** : renvoyer le même fichier retrouve la même pièce, et un adhérent dont la connexion tombe recommence sans
  créer de doublon. Le formulaire se vide après un envoi réussi.
- **`appeler` accepte un formulaire multipart** (`formulaire: FormData`), sans poser l'en-tête de contenu que `fetch` doit
  écrire lui-même : l'outil de contrat continue de voir cet appel.
- **La limite des actions serveur passe à 21 Mo** dans `next.config.ts` : les 20 Mo du backend, plus l'enveloppe
  multipart. Le commentaire exige que les deux limites bougent ensemble.
- **Trois lectures indépendantes** : un échéancier illisible s'annonce (« le cabinet le suit ») sans priver l'adhérent de ses
  pièces ni du dépôt.

### L'essai réel

Avec l'adhérent de SARL BATIMENT PLUS :

| Essai | Résultat |
| --- | --- |
| Page « Mon espace » | « Envoyer une pièce », « Ce que le cabinet attend de vous » (la rectificative demandée), « Mes échéances » (retards d'abord), « Mes pièces » |
| Envoi d'une image PNG, facture d'achat, QUINCAILLERIE DU WOURI, « 125 000 » | « Pièce reçue. Le cabinet la traitera… » ; 8 → 9 pièces ; pièce REÇUE, canal PORTAIL, montant 125 000 |
| Renvoi du même fichier | reçu, **toujours 9 pièces** : rejouable |
| Envoi d'un fichier texte | « Type de document refusé. Formats acceptés : PDF, JPEG, PNG, TIFF… » |
| Montant « cent mille » | « Montant illisible : écrivez-le en chiffres » |
| Relecture du document déposé | 200, `image/png`, identique octet pour octet |
| Liste « Mes pièces » rechargée | la nouvelle pièce y figure, par le portail |
| Dépôt d'un fichier ou d'une pièce dans le dossier d'ETS TCHOUMBA, par appel direct | **404** ; lecture de ses demandes : 404 |

Aucun code backend n'a changé : **3 009 tests**, inchangés.

### État à la fin du pas 81

**Avancement des écrans : 56 %** (79 gestes sur 142 ; 60 % de ce que le backend permet), contre 53 % au pas 80.
**Priorité 2 : 71 %** (contre 53 %) ; E06 accueil adhérent 100 %, E07 dépôt 67 % (la photographie hors ligne relève de
l'application mobile), E09 mes échéances 100 %. Contrat des écrans : 84 appels, 0 écart. Couverture des routes : 88 sur 139.

**Ce que le projet sait faire qu'il ne savait pas.** Laisser l'adhérent envoyer sa facture depuis son téléphone, et lui dire
ce que le cabinet attend encore de lui et quand ses déclarations tombent.

*Un « impossible » écrit dans un commentaire se vérifie avant de s'obéir : celui-ci datait d'un magasin qui n'existait pas encore.*

## Pas 82 — Le tunnel de création d'entreprise s'actionne, et ses dates ne se fournissent plus

### Pourquoi

Deuxième lot d'écrans : la création d'entreprise (E13), **11 %** à la mesure du pas 80. Le pipeline montrait les
dossiers par étape ; aucun ne s'ouvrait, n'avançait ni ne se convertissait. Les neuf routes existaient.

### Ce que la relecture a trouvé

**Aucun test n'appelait les routes de création.** Le domaine était éprouvé, sa couche HTTP jamais, et deux défauts y
vivaient. Sonde par la route, avant correction :

| Essai | Résultat |
| --- | --- |
| `POST /creations/CR-2026-0013/etape?a_la_date=2019-01-01`, vers le suivi d'immatriculation | **200** : jalon daté du **01/01/2019**, après un dépôt CFCE du 30/07/2026 |
| Convertir CR-2026-0015, en mémoire | **200**, `enregistree_au_portefeuille: false`, et l'entreprise **introuvable au portefeuille (404)** |

- **Les écritures datées par la requête.** Ouvrir, franchir, recevoir une pièce, abandonner et convertir acceptaient
  `a_la_date`. La chronologie du dossier se cassait, et avec elle le délai du guichet, que le contexte appelle « le seul
  chiffre que le cabinet puisse lui opposer ». La faute du pas 71, par une autre porte.
- **L'entreprise convertie perdue en mémoire.** La route n'écrivait qu'en base SQL. En démonstration, le client converti
  était « invisible de tous les écrans qui comptent », exactement ce que l'en-tête de la route dit empêcher.

### Les corrections

- Les cinq écritures prennent la date de **l'horloge du projet**. Les lectures (pipeline, fiche) gardent `a_la_date` :
  lire à une date passée ne réécrit rien.
- **Une date d'obtention d'identifiant future est refusée** (422) : elle raccourcirait le délai du guichet.
- **La conversion range l'entreprise dans le magasin mémoire du portefeuille** quand il n'y a pas de base, celui que les
  routes du portefeuille lisent.

`tests/test_creation_http.py`, 5 cas : l'étape datée du jour malgré `a_la_date=2019-01-01`, l'ouverture datée du jour,
l'identifiant futur refusé, l'entreprise convertie présente au portefeuille (et la seconde conversion refusée), le
comptable refusé (403). **Trois mutations tuées** : date de la requête sur l'étape, conversion non rangée, identifiant
futur admis.

### Ce qui a été fait, à l'écran

- **Pipeline** : un panneau « Nouveau dossier » (fondateur, dénomination, forme, activité, siège, capital), qui affiche les
  **pièces à réunir pour la forme choisie**, lues au backend. La référence (« CR-2026-B4D4 ») est tirée par l'action ;
  chaque carte ouvre désormais la fiche.
- **Fiche d'un dossier** (`/creation-entreprise/[reference]`), dans l'ordre du travail : ce qui bloque, l'étape suivante,
  les pièces, les identifiants, les jalons.
  - **Seules les étapes que le backend dit ouvertes** sont proposées : un cran en avant.
  - **À la livraison, la conversion** : régime d'entrée et centre des impôts **choisis**, adhésion cochée par défaut, et une
    case « l'entreprise entre au portefeuille ».
  - **Chaque pièce manquante** se marque reçue d'un clic.
  - **Les identifiants vont avec leur date**, vérifié à l'écran et au backend.
  - **L'abandon** demande un motif et une case.
- **Aucune date d'acte n'est envoyée** par ces actions.

### L'essai réel

Compte C-007, rôle chargé des formalités :

| Essai | Résultat |
| --- | --- |
| Ouvrir EKANI TRANSPORTS, SARL, capital « 1 000 000 » | « Dossier CR-2026-B4D4 ouvert, en qualification. » ; la fiche propose « Passer à Constitution » et 9 pièces à marquer |
| Marquer une pièce reçue, puis franchir vers la constitution | jalons QUALIFICATION et CONSTITUTION, **datés du 14/09/2026** |
| Sauter à la livraison, par appel direct | « … LIVRAISON n'est pas atteignable. Ouvertes : ABANDONNE, DEPOT_CFCE. » |
| RCCM obtenu le 01/12/2026 | « cette date n'est pas encore passée » |
| NIU sans date | « NIU et sa date d'obtention vont ensemble » |
| CR-2026-0014 : RCCM et NIU datés, puis livraison | enregistrés ; la fiche propose la conversion |
| Convertir sans la case, puis avec | refusé, puis « SAHEL DISTRIBUTION SA entre au portefeuille sous le NIU M998877665544A » ; **200** au portefeuille |
| Abandonner EKANI TRANSPORTS sans la case, puis avec | refusé, puis abandonné ; la fiche montre le motif et ne propose plus d'étape |

**La grille d'avancement ignorait la nouvelle fiche** : E13 se mesurait à 3 gestes sur 9 alors que les huit gestes étaient
branchés. La page est ajoutée à la grille ; c'est le fonctionnement voulu, puisqu'une page nouvelle doit y être déclarée.

### État à la fin du pas 82

**3 014 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 61 %** (87 gestes sur 142 ; 66 % de ce que le backend permet), contre 56 % au pas 81.
**E13 création d'entreprise : 100 %** (contre 11 %) ; **priorité 4 : 71 %** (contre 24 %). Contrat des écrans : 92 appels,
0 écart. Couverture des routes : 96 sur 139 (69 %).

**Ce que le projet sait faire qu'il ne savait pas.** Conduire la création d'une entreprise de l'ouverture du dossier à son
entrée au portefeuille, avec une chronologie que personne ne peut antidater.

*Une couche que personne n'appelle n'est pas une couche sûre : c'est une couche que personne n'a encore essayé de tromper.*

## Pas 83 — Payer ne suffit plus à ouvrir un dossier, et la souscription en ligne a ses écrans

### Pourquoi

Troisième lot d'écrans : la souscription en ligne, **0 %** des 12 gestes à la mesure du pas 82. Le backend savait
chiffrer un devis, encaisser par Mobile Money, ouvrir l'accès, appeler les mensualités et relancer ; aucun écran ne
s'en servait. Avant de brancher le moindre bouton, la méthode habituelle : relire les routes et les éprouver.

### Ce que la relecture a trouvé

**Un inconnu pouvait lire la comptabilité d'une autre entreprise pour le prix d'une adhésion.** L'engagement d'un devis
est public, le NIU y est déclaré par le visiteur, et l'encaissement ouvrait aussitôt un compte adhérent portant ce NIU.
Rejoué de bout en bout avant correction, en mode démonstration :

| Essai | Résultat |
| --- | --- |
| Devis d'adhésion au NIU de SARL BATIMENT PLUS (M081234567890P), courriel d'un inconnu | **201** |
| Engagement (paiement validé d'office) | lien d'activation dans la boîte du payeur |
| Mot de passe défini, connexion | rôle ADHÉRENT, dossier M081234567890P |
| `GET /portefeuille/entreprises/M081234567890P`, `/collecte/pieces`, l'échéancier | **200**, fournisseurs et montants compris |
| `POST /collecte/fichiers` | **201** : l'inconnu dépose dans le dossier d'autrui |

Refuser seulement les NIU déjà au portefeuille ne suffirait pas : un NIU est imprimé sur chaque facture, et un concurrent
souscrirait avec celui d'une entreprise pas encore cliente.

**Et le geste qui répare était impraticable.** La liste des souscriptions payées à activer exigeait `LIRE_PILOTAGE`, que
seule la direction détient ; l'ouverture de l'accès exige `GERER_COMPTES`, que seul l'administrateur détient. Personne ne
pouvait faire les deux moitiés du geste.

### Les corrections

- **Le traitement automatique n'ouvre plus jamais d'accès à un dossier.** L'encaissement reste acquis, la souscription
  reste PAYÉE (donc visible), et le journal note `souscription.verification_requise`. Une prestation qui n'ouvre pas de
  dossier (formation, domiciliation) n'est pas concernée.
- **`activer_souscription` exige une `VerificationDIdentite`** (auteur, description d'au moins vingt caractères), sans
  valeur par défaut : l'oublier est une erreur à l'écriture du code, pas une ouverture silencieuse. Le journal
  `souscription.activee` porte `verifiee_par` et la vérification.
- **La route d'ouverture** (`POST /souscription/souscriptions/{reference}/activation`) prend un corps `{verification}`
  fermé aux champs inconnus : l'auteur est la session, jamais un champ qu'on remplirait au nom d'un collègue.
- **La liste à activer** se lit avec `GERER_COMPTES` **ou** `LIRE_PILOTAGE`.
- **Le message d'engagement** ne promet plus « l'accès s'ouvre dès la confirmation ».
- Question ouverte **Q24** : comment prouver en ligne qu'on représente l'entreprise.

Treize tests encodaient l'ouverture automatique. Ils passent désormais par l'étape du cabinet, sans rien perdre de ce
qu'ils mesuraient (rejeu idempotent, échec d'ouverture laissé PAYÉ, trace complète, survie au redémarrage sur PostgreSQL).
`tests/test_souscription_verifiee.py`, 16 cas : aucun compte ni courriel après un paiement au NIU d'autrui, connexion
impossible, le cabinet voit le paiement, le journal le dit ; la route refuse l'anonyme (401), le comptable (403), une
vérification absente, vide, courte ou qui impose son auteur (422), une référence inconnue (404) ; l'ouverture nomme son
auteur ; l'administration lit ce qu'elle doit ouvrir. **Cinq mutations tuées** : ouverture sans vérification, route sans
permission, auteur accepté du corps, auteur absent du journal, description non exigée.

### Ce qui a été fait, à l'écran

- **Souscrire en ligne** (`/souscrire`, lien depuis « Devenir adhérent ») : le catalogue **au barème du backend**, les
  services sur étude annoncés à part, et le formulaire du devis. Le NIU s'y accompagne d'une phrase qui dit que l'accès
  s'ouvre après vérification.
- **Le devis** (`/souscrire/devis/[reference]`) : montants figés, validité, et le paiement derrière une case. Un devis
  engagé, caduc, abandonné ou incomplet ne propose pas de payer.
- **Le suivi** (`/souscrire/suivi/[reference]`) : l'état dit en clair (« Payée » explique l'attente de vérification), puis
  les mensualités une fois l'abonnement en vigueur.
- **Souscriptions en ligne**, côté cabinet (`/souscriptions`), un panneau par rôle : les payées à ouvrir (direction et
  administration), le geste d'ouverture avec description et case (administration), le rapprochement et l'appel des
  mensualités et les services à suspendre (direction), les relances d'impayés (chargé de clientèle).
- **Le menu accepte une entrée ouverte par plusieurs permissions** (`ouAussi`) : ces trois rôles n'en ont aucune en commun.

### Ce que l'écran a appris en chemin

- **L'écran « accès réservé » orientait vers la mauvaise personne.** Sa liste des profils était recopiée à la main :
  `GERER_COMPTES` y était ouverte à la direction, `LIRE_COMPTABILITE` fermée au fiscaliste. Il lit désormais la matrice
  du backend (`/transverse/roles`). `/comptes` dit maintenant « Administrateur », seul profil qui l'ouvre.
- **Une aide qui recevait le chemin rendait l'appel invérifiable**, le piège du pas 78 : l'outil de contrat l'a signalé
  à la première mesure. L'aide reçoit désormais la promesse, et l'appel typé reste au point d'usage.
- **L'état d'un devis était deviné** (« OUVERT ») : relu au domaine, c'est `EMIS`. L'outil de contrat ne compare pas les
  énumérations, et le commentaire le dit.
- **L'estimation de création** chiffre sur un barème local au frontend et n'appelle pas ce contexte : elle sort de la
  grille de la souscription.

### L'essai réel

Serveurs réels, mode démonstration :

| Essai | Résultat |
| --- | --- |
| `/souscrire` | catalogue, adhésion à 12 500 FCFA, services sur étude annoncés à part |
| Devis au NIU de SARL BATIMENT PLUS, par un inconnu | redirigé vers `/souscrire/devis/DV-…` |
| « Payer et souscrire » | « … L'accès au dossier s'ouvrira après vérification de l'identité par le cabinet. » |
| Suivi | « Payée », l'attente expliquée ; **aucun courriel d'activation** |
| Second engagement | « … produirait un second débit pour la même prestation. » |
| `/souscriptions` en comptable | accès réservé, « Administrateur, Chargé de clientèle et Direction » |
| En direction | la ligne, sans geste d'ouverture ; rapprochement : 0 paiement interrogé ; ouverture forcée par appel direct : `GERER_COMPTES est requise` |
| En administration, description « vu » | « Décrivez la vérification faite (au moins vingt caractères)… » |
| Description complète, case cochée | « Accès ouvert à curieux@exemple.cm ; le lien d'activation lui est parti. » ; le suivi dit « Active » |
| En chargé de clientèle | relances du jour, pas de liste à ouvrir |

L'essai a trouvé un défaut que les tests ne voyaient pas : **la description trop courte revenait avec le message anglais
de la validation** (« String should have at least 20 characters »). L'action le dit en français, au seuil du backend.

### État à la fin du pas 83

**3 030 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 70 %** (99 gestes sur 142 ; 76 % de ce que le backend permet), contre 61 % au pas 82.
**Souscription : 100 %** (contre 0 %). Contrat des écrans : 104 appels, 0 écart. Couverture des routes : 108 sur 139 (77 %).

**Ce que le projet sait faire qu'il ne savait pas.** Vendre une adhésion en ligne de bout en bout, sans ouvrir le dossier
d'une entreprise à quiconque a payé en son nom.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Encaisser prouve qu'on a payé. Cela n'a jamais prouvé pour qui.*

## Pas 84 — L'exploitation a son écran, et deux gestes promis existent enfin

### Pourquoi

Quatrième lot : l'exploitation de la plateforme, **0 %** des 7 gestes. Le backend savait décrire ses quatorze services,
faire tourner l'ordonnanceur et vider la boîte d'envoi ; personne ne pouvait le voir sans appeler l'API à la main.

### Ce que la relecture a trouvé

**Deux mécanismes de sûreté s'arrêtaient sur une promesse écrite.**

- L'ordonnanceur **abandonne** un travail après vingt échecs d'affilée. Son code disait : « il faut un geste
  d'exploitation pour le reprendre ». Ce geste n'existait nulle part.
- Le relais met **en quarantaine** un événement refusé dix fois, « lisible et rejouable à la main ». Rien ne le
  rejouait.

Concrètement : une relance des proformas abandonnée après une panne de base, ou l'ouverture d'un tenant payé tombée en
quarantaine, le restaient jusqu'à ce que quelqu'un modifie la base à la main, sans trace au journal. Un écran qui aurait
seulement affiché « abandonné » aurait montré un problème sans issue.

**Les cinq routes de lecture rendaient des dictionnaires libres** : l'outil de contrat des écrans ne pouvait pas les
vérifier.

**Le réinitialiseur des tests oubliait les passages de l'ordonnanceur** : un test qui abandonnait un travail le laissait
abandonné pour tous les tests suivants du processus.

### Les corrections

- **`Passage.reprendre()`** : le compteur d'échecs revient à zéro et la fin est effacée, pour que le travail soit **dû
  au prochain tour** (on veut savoir tout de suite si la cause est corrigée). Le début et le dernier échec sont gardés :
  l'écran ne dit pas « jamais passé », et la trace de ce qui a été corrigé reste. Refusée sur un travail non abandonné,
  qu'elle ferait marteler sa cause.
- **`EvenementSortant.remettre_en_circulation()`** : hors quarantaine, tentatives à zéro (sans quoi le premier nouvel
  échec l'y renverrait), dernier échec gardé. Le rejeu est sans danger parce que tout abonné est idempotent. Refusée
  sur un événement publié ou déjà dans la file.
- **Deux routes**, sous `GERER_COMPTES`, avec un motif d'au moins dix caractères dans un corps fermé aux champs
  inconnus ; l'auteur (la session) et le motif vont au journal : `POST /orchestration/ordonnancement/{travail}/reprise`
  (404 inconnu, 409 non abandonné), `POST /orchestration/quarantaine/{identifiant}/remise` (404 hors quarantaine). La
  direction, qui lit la quarantaine avec `LIRE_AUDIT`, ne la rejoue pas.
- **Cinq modèles de réponse déclarés** (registre, santé, file, quarantaine, travaux). Les réponses ont été capturées
  avant et après, avec un événement en quarantaine et un travail abandonné semés : **identiques**. La santé d'un service
  garde son motif absent quand il n'y a rien à dire (`response_model_exclude_none`).
- Le réinitialiseur remet les passages à zéro.

⚠️ **Le piège du pas 78 a failli se reproduire** : la première insertion d'un modèle s'est faite entre le décorateur
d'une route et sa fonction. Repéré à la relecture et vérifié par analyse de l'arbre syntaxique, avant tout essai.

`tests/test_exploitation_gestes.py`, 22 cas (domaine et routes), la liste close des routes d'orchestration mise à jour,
et un cas sur **PostgreSQL réel** (la fin effacée passe en base, l'événement revient dans la file, le journal porte les deux
gestes). **Huit mutations tuées** : reprise sans garde, fin conservée, tentatives conservées, remise ouverte à
`LIRE_AUDIT`, reprise hors journal, motif non exigé, passages non réinitialisés, remise non enregistrée.

### Ce qui a été fait, à l'écran

**Exploitation** (`/exploitation`, menu d'administration) :

- **Un bandeau** réunit ce qu'on vient chercher : services en difficulté, travaux abandonnés, événements en quarantaine.
- **Services** : les quatorze, construction et exécution séparées, le motif d'un service suspect, le nombre de services
  qu'il entraîne. « Contrôler » appelle la santé d'un service à la demande, pas à chaque affichage : c'est le chemin que
  Consul interroge toutes les dix secondes.
- **Travaux périodiques** : cadence, dernier passage, échecs, et « Reprendre » avec motif sur un travail abandonné ; «
  Faire un tour ».
- **Boîte d'envoi** et **quarantaine** : identifiants et motifs, jamais la charge ; « Publier un lot » et « Remettre en
  circulation ».
- La direction voit la file et la quarantaine, sans les gestes. L'entrée de menu est ouverte à `LIRE_PILOTAGE` plutôt
  qu'à `LIRE_AUDIT` : l'inspecteur détient cette dernière, et n'a pas à trouver l'exploitation dans son menu.

**`appeler` accepte des statuts qui sont des réponses** (`accepter`) : la santé d'un service suspect répond 429 avec son
motif dans le corps (convention de Consul), et l'écran aurait sinon affiché « 429 Too Many Requests ».

### L'essai réel

Serveur en mémoire, avec un événement `TenantOuvert` en quarantaine et le travail « relance » abandonné :

| Essai | Résultat |
| --- | --- |
| `/exploitation` en administration | bandeau « Travail abandonné : relance » et « 1 événement en quarantaine » ; Transverse « Suspect : aucun tenant au répertoire… » |
| Contrôler le Transverse (429) | « Contrôle de transverse : Suspect », motif lisible |
| Reprendre « relais », qui tourne | « … n'est pas abandonné (0 échec(s) d'affilée, abandon à 20) » |
| Reprendre « relance », motif « ok », puis motif complet | refus en français, puis « « relance » reprend » ; dernier passage « dû maintenant » |
| Faire un tour | 5 travaux passés, « relance » compris |
| Remettre EV-Q-1, puis une seconde fois | « TenantOuvert [SO-ESSAI-84] est de retour dans la file », puis « aucun événement en quarantaine » |
| Publier un lot | 1 publié ; journal : `travail_repris` et `evenement_remis`, auteur C-002, motifs |
| Direction | file et quarantaine, aucun geste ; publication forcée : « GERER_COMPTES est requise » |
| Comptable | accès réservé, profils lus au backend |

### Ce que l'essai a appris sur l'outillage

La base locale s'était arrêtée ; relancée par `outils/postgres-local.sh`, elle affiche une URL **sans mot de passe**.
Avec elle, **cinq tests de sécurité des lignes échouaient** comme si le cloisonnement était cassé : le test construisait
l'URL du rôle restreint en remplaçant « cga:cga@ », ne trouvait rien, et se connectait en superutilisateur. L'URL est
désormais analysée ; les deux formes passent.

Une limite est notée, sans correction dans ce pas : un événement en quarantaine **ne retient pas** les événements
suivants de la même clé, qui partent avant lui. Le relais ne retient une clé que dans le lot où elle a échoué.

### État à la fin du pas 84

**3 055 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 75 %** (108 gestes sur 144 ; 81 % de ce que le backend permet), contre 70 % au pas 83.
**Exploitation : 100 %** (contre 0 %). Contrat des écrans : 113 appels, 0 écart. Couverture des routes : 117 sur 141 (82 %).

**Ce que le projet sait faire qu'il ne savait pas.** Montrer à l'exploitant ce qui ne va pas, et lui permettre de le
réparer sans toucher la base, avec une trace de qui l'a fait et pourquoi.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un mécanisme de sûreté qui s'arrête sur « il faudra un geste » n'est pas un mécanisme de sûreté : c'est une panne différée.*

## Pas 85 — L'échange avec le logiciel du client s'actionne, et une reprise ne double plus un exercice

### Pourquoi

Cinquième lot : la priorité 5, **57 %**. Le plus cohérent de ses manques est l'échange comptable de E10 : exporter les
écritures vers le logiciel du client, reprendre le fichier de son logiciel précédent, choisir le format, lire le plan
d'imputation du dossier. Les quatre routes existaient ; aucun écran. Sans reprise, la plateforme ne se vend qu'aux
entreprises qui se créent.

### Ce que la relecture a trouvé

Sonde sur les données de démonstration, avant correction :

| Essai | Résultat |
| --- | --- |
| Reprendre l'export du dossier M065544332211L dans ce même dossier, en contrôle | recevable, aucune anomalie |
| L'appliquer, puis l'appliquer une seconde fois | « appliqué » les deux fois ; journal des achats : **2 → 4 → 6 écritures** |
| Appliquer un fichier réduit à son en-tête | `applique: true`, zéro écriture |

- **Une reprise appliquée deux fois doublait l'exercice**, sans retour : les écritures entrent en brouillon, et un
  brouillon ne se supprime pas (Q23). Un double clic, un rafraîchissement, un collègue qui reprend le même export
  suffisaient. Réimporter dans un dossier son propre export faisait la même chose.
- **Un fichier sans écriture « s'appliquait »** : l'exploitant croyait sa reprise faite.
- **`recevable` n'était pas dans la réponse** : c'était une propriété non sérialisée, et un écran aurait dû recopier la
  règle.

### Les corrections

- **Une écriture du fichier est refusée, en anomalie, quand le dossier contient déjà une écriture de même contenu** :
  journal, date, référence externe, lignes (compte, sens, montant), quel que soit l'état. Le libellé n'en fait pas partie,
  parce qu'un autre logiciel le reformate ; les montants se comparent en décimaux, pour que « 2840000.00 » et « 2840000 »
  se reconnaissent. Deux écritures identiques dans le même fichier sont refusées aussi.
- **Ce n'est pas une empreinte du fichier** : un fichier retouché d'une ligne passerait et doublerait tout le reste.
- **Deux écritures sans référence et de numéros d'origine différents ne sont pas des doublons** : le numéro d'origine
  devient leur référence, et il les distingue. Un cas le montre.
- **Un fichier sans écriture est une anomalie**, en contrôle comme en application.
- **`recevable` est exposé** dans le rapport.
- Q23 le note : le cas le plus probable de brouillons indésirables (le même fichier deux fois) est fermé.

`tests/test_reprise_comptable.py` : 6 cas sur PostgreSQL réel (seconde application refusée, doublon visible dès le
contrôle, export réimporté refusé, doublon interne et numéros d'origine distincts, fichier vide, fichier sain recevable)
et un cas sur l'empreinte. **Sept mutations tuées** : doublon présent admis, doublon interne admis, fichier vide
appliqué, libellé dans l'empreinte, référence hors de l'empreinte, montant comparé en texte, `recevable` non exposé.

### Ce qui a été fait, à l'écran

**Échange avec le logiciel du client** (`/comptabilite/echange`, sous Comptabilité) :

- **Exporter** : exercice, format (lu au référentiel, avec sa remarque et son encodage), journal facultatif. Un lot qui
  contient un brouillon est refusé en entier, et le refus s'affiche.
- **Reprendre un fichier** (réservé à `SAISIR_ECRITURE`) : « Contrôler » d'abord ; « Appliquer : n écritures en brouillon »
  n'apparaît qu'après un contrôle recevable, et **toute modification du formulaire efface le rapport** : on n'applique
  pas un fichier sur la foi du contrôle d'un autre. Les anomalies s'affichent toutes, avec leur ligne du fichier.
- **Plan d'imputation du dossier** : comptes par défaut et règles propres, là où l'on compare une reprise ou un export.

**Les octets de l'export passent intacts.** Le profil Sage est en cp1252 : `appeler` lit du JSON, donc de l'UTF-8, et
aurait abîmé chaque accent sans que rien ne le signale avant l'import chez le client. Une fonction `telecharger` lit les
octets, l'action les rend en base64, et le navigateur les reconstitue dans un fichier typé avec le jeu de caractères du
profil. **L'outil de contrat reconnaît `telecharger`** : retiré de sa liste, l'export sort « à brancher » ; présent, il
est branché.

### L'essai réel

Serveurs réels, compte C-004 (comptable), dossier M065544332211L :

| Essai | Résultat |
| --- | --- |
| Export au format Sage | `M065544332211L-2026-sage-ligne100.csv`, `text/csv; charset=cp1252` ; **octets identiques** à ceux du backend ; « é » en 0xE9, aucune séquence UTF-8 |
| Exercice « 20 » | « Choisissez un exercice (quatre chiffres) et un format. » |
| Reprendre l'export du dossier, contrôle puis application | deux anomalies « une écriture identique existe déjà » ; écritures : 2 → 2 |
| Lot sain : contrôle, application, seconde application | recevable ; `2026/OD/000001` ; puis « … Le fichier a-t-il déjà été repris ? » |
| Fichier réduit à l'en-tête | « le fichier ne contient aucune écriture : rien ne serait repris. » |
| Chargé de clientèle | export présent, reprise absente ; reprise forcée : « SAISIR_ECRITURE est requise » |

Limite dite : le déclenchement du téléchargement dans le navigateur (reconstitution du fichier depuis le base64) n'a
pas été exercé dans un vrai navigateur ; les octets rendus par l'action l'ont été.

### État à la fin du pas 85

**3 062 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 78 %** (112 gestes sur 144 ; 84 % de ce que le backend permet), contre 75 % au pas 84.
**Priorité 5 : 74 %** (contre 57 %), E10 à 100 %. Contrat des écrans : 117 appels, 0 écart. Couverture des routes : 121 sur
141 (85 %).

**Ce que le projet sait faire qu'il ne savait pas.** Accueillir un adhérent avec le passé de son ancien logiciel, et
rendre ses écritures au sien, sans qu'une fausse manœuvre double son exercice ni abîme ses accents.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un contrôle qui dit « recevable » à un fichier déjà repris ne contrôle pas le fichier : il contrôle sa syntaxe.*

## Pas 86 — La fiche adhérent 360° existe, et « qui a accès » ne nomme plus les autres clients

### Pourquoi

Sixième lot : la fiche adhérent 360° (E04), **38 %**. Le portefeuille listait les dossiers ; aucun ne s'ouvrait. Cinq
routes attendaient : la fiche complète, les statuts à une date, les identifiants douteux, les accès au dossier, la
complétude de la collecte.

### Ce que la relecture a trouvé

**« Qui a accès à ce dossier » révélait les autres dossiers du cabinet.** `GET /transverse/dossiers/{niu}/acces` rendait
chaque habilitation entière, portée comprise. Essai sur les données de démonstration : l'adhérent de SARL BATIMENT PLUS
(A-001), qui détient `LIRE_DOSSIER` sur son propre dossier, lisait la portée de la chargée de clientèle, soit **les NIU de
six autres clients du cabinet**. Un comptable lisait de même les dossiers confiés à ses collègues. Le projet rend
pourtant 404 plutôt que 403 sur un dossier hors périmètre précisément pour ne rien apprendre de son existence.

L'essai réel de la fiche a trouvé deux défauts de plus :

- **Les statuts à une date antérieure à l'histoire d'un dossier rendaient 500.** Au 01/01/2019, SARL BATIMENT PLUS n'a
  aucun régime connu (sa première période commence le 15/03/2021) : l'exception du domaine remontait sans être traduite.
- **La liste du portefeuille à cette date tombait entière** : un seul dossier sans statut faisait échouer tous les autres.

### Les corrections

- **La portée est ramenée au dossier consulté.** La réponse garde qui, quel rôle, depuis quand, accordé par qui ; une
  habilitation transverse garde sa portée nulle, qui ne nomme rien. La réponse est une vue : l'habilitation en base n'est
  pas modifiée.
- **Les statuts hors de l'histoire rendent 409**, avec le message du domaine, qui nomme les périodes connues. Pas 404 : le
  dossier existe.
- **La liste à une date omet les dossiers sans statut à cette date** : le cabinet ne connaissait alors ni leur régime ni
  leur centre.

`tests/test_acces_au_dossier.py`, 6 cas (adhérent, comptable et direction ne lisent que le dossier demandé ; la réponse
garde ce qui répond à la question ; la base n'est pas modifiée ; le hors-périmètre reste refusé).
`tests/test_statuts_hors_histoire.py`, 3 cas. **Six mutations tuées** : portée entière, portée transverse remplacée,
habilitation écrasée en base, liste sans garde, statuts sans garde, statuts en 404.

### Ce qui a été fait, à l'écran

**Fiche du dossier** (`/portefeuille/[niu]`, ouverte depuis chaque dénomination du portefeuille), dans l'ordre de ce
qu'on y cherche :

- **Un bandeau** : identifiants douteux du dossier, et collecte du mois précédent quand elle empêche le dépôt.
- **Statuts à une date choisie** (`?au=`) : régime, centre, TVA, adhésion, exercice, obligations mandatées. Une date hors
  de l'histoire affiche le message du backend.
- **Collecte du mois précédent**, celui dont la TVA se dépose : pièces reçues, traitées, en souffrance ; demandes
  ouvertes, en retard, bloquantes ; et la phrase du backend plutôt qu'un pourcentage, parce que ce n'est pas une
  exhaustivité. Panneau réservé à `LIRE_PIECE`.
- **Histoire des statuts** : régimes, centres, adhésions et mandats, chaque période avec son motif.
- **Exercices, dirigeants, associés, tiers.**
- **Qui a accès** : compte, rôle, étendue (« ce dossier » ou « tout le cabinet »), depuis quand, accordé par qui.
- **Un dossier hors périmètre et un dossier inconnu rendent la même page introuvable.**

**Portefeuille** : les identifiants douteux en tête, chacun menant à sa fiche.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| C-004 (comptable), fiche de SARL BATIMENT PLUS | les six panneaux ; bandeau « 2 pièce(s) indispensable(s) manquante(s), dépôt impossible » ; **aucun NIU d'un autre client dans la page** |
| Statuts du jour, puis au 01/01/2019 | « Régime Réel, Centre CDI », puis « aucun régime connu au 2019-01-01. Périodes déclarées : [2021-03-15… » (500 avant correction) |
| Fiche d'un dossier confié à un collègue, puis d'un NIU inconnu | 404 et 404 |
| Direction, fiche de M065544332211L | accès « tout le cabinet », exercices |
| Liste du portefeuille au 01/01/2019, par l'API | 200 (500 avant correction) |

Deux limites dites. Le panneau des identifiants douteux n'a été vu que vide : aucun identifiant de démonstration n'est
hors format. Les comptes sont affichés par identifiant (« C-004 ») : leurs noms ne se lisent qu'avec `GERER_COMPTES`.

### État à la fin du pas 86

**3 071 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 81 %** (117 gestes sur 144 ; 88 % de ce que le backend permet), contre 78 % au pas 85.
**Priorité 4 : 100 %** (E04 et E13). Contrat des écrans : 122 appels, 0 écart. Couverture des routes : 124 sur 141 (87 %).

**Ce que le projet sait faire qu'il ne savait pas.** Ouvrir un dossier et y lire, au même endroit, ce qui ne va pas, ce
qu'il était à une date, pourquoi, et qui peut le voir.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Répondre à « qui a accès à ce dossier » n'autorise pas à dire « et à quels autres ».*

## Pas 87 — L'échéancier se termine, et ses chiffres ne se fournissent plus

### Pourquoi

Septième lot : l'échéancier consolidé (E05), **50 %**. L'écran lisait l'échéancier et préparait la déclaration de TVA ;
il ne consignait pas le dépôt de TVA, n'estimait aucune pénalité, ne montrait ni les relances du jour ni le catalogue.

### Ce que la relecture a trouvé

Quatre défauts, tous rejoués avant correction :

| Essai | Résultat |
| --- | --- |
| Pénalité de 1 000 000 FCFA, échéance 15/07/2026, au 15/09/2026 | **130 000 FCFA** : taux fixe de **10 %** écrit dans la route, alors que le référentiel porte **25 %, validé** (CGI art. L95 et L96) ; avec `taux_fixe=0`, **0 FCFA** |
| Constat du dépôt de la TVA de janvier 2026, accusé daté du **01/12/2026**, le 15/09/2026 | **200**, obligation « déclarée » |
| Relances d'échéance au 08/01/2027, sept jours avant les échéances des obligations de décembre | **aucune** : exercice « 2026 » par défaut, et seul pris en compte |
| Déclaration et dépôt de TVA sans exercice explicite | « 2026 » par défaut : une période de 2027 aurait été calculée sur les écritures de 2026 |

- **La pénalité** : la route recevait ses taux de la requête. Le référentiel, qui fait l'extensibilité du projet, était
  cité dans les descriptions et jamais lu. L'estimation annonçait moins de la moitié de ce que l'adhérent paierait,
  exactement la « surprise au paiement » que l'en-tête de la route dit éviter.
- **La date d'accusé** : les deux gardes (pas de dépôt futur, pas de dépôt avant la fin de la période) étaient écrites
  dans le constat hors TVA seul. Le parcours le plus contrôlé du produit, celui de la TVA, n'en avait aucune.
- **Les exercices** : trois routes avaient `exercice="2026"` pour défaut. Rien ne se voyait en 2026.

### Les corrections

- **La pénalité lit le référentiel** à la date de l'échéance (celle où le retard commence) et rend les deux paramètres
  résolus : valeur, texte, source, statut, validateur. Les taux ne se passent plus en paramètre ; un taux absent du
  référentiel est un refus (409), jamais une supposition.
- **Une garde de date commune**, `verifier_la_date_du_depot`, appelée par les deux parcours de constat, **avant** la
  recevabilité : c'est la date qui est fausse, et le message doit le dire.
- **Les relances** portent sur tout exercice ouvert avant la date et clos depuis moins d'un an : les obligations d'un
  exercice se déposent jusqu'à plusieurs mois après sa clôture.
- **L'exercice de la déclaration et du dépôt de TVA** est, par défaut, celui du dossier qui contient la fin de période ;
  aucun ne la contient : 409 qui nomme les exercices connus.

`tests/test_echeancier_dates_et_taux.py`, 9 cas. **Cinq mutations tuées** : TVA sans garde de date, garde du futur
retirée, taux fixe en dur, exercice « 2026 » par défaut, relances d'un seul exercice.

### Ce qui a été fait, à l'écran

- **Échéancier** (`/obligations`) :
  - **Relances d'échéance du jour**, sur tout le portefeuille : jalon, dossier, obligation, échéance, et « pénalité en
    cours » au J+1.
  - **Estimer une pénalité** pour une obligation en retard du dossier : le total n'apparaît jamais sans ses deux taux,
    leur statut et leur texte. L'écran n'envoie aucun taux.
  - **Catalogue des obligations** : guichet, périodicité, jour limite, à qui elle s'applique.
- **Déclaration de TVA** (`/obligations/declarations`) : **Consigner le dépôt**, proposé seulement si la période est
  recevable et pas encore déposée, à qui détient `DEPOSER_DECLARATION`, derrière le second facteur. L'heure saisie est
  celle de Douala ; la conversion en UTC, qui existait pour le constat hors TVA, est sortie dans `heure-douala.ts` pour
  servir aux deux sans se recopier.

### L'essai réel

Compte C-003 (réviseur), SARL BATIMENT PLUS :

| Essai | Résultat |
| --- | --- |
| Estimer 1 000 000 FCFA, échéance 15/07, au 15/09 | 280 000 FCFA ; taux fixe 25 %, VALIDE, « CGI art. L95 et L96… » |
| Montant nul ; date antérieure à l'échéance | refus en français ; « il n'y a pas de pénalité à calculer » |
| TVA de janvier sans second facteur | porte du second facteur, pas de formulaire |
| Après renforcement : accusé du 01/12/2026 ; du 20/01/2026 | « postérieur à maintenant » ; « la période se termine le 31/01/2026 » |
| Accusé DGI-2026-01-0042 du 12/02/2026 | consigné, réserve assumée `REFERENTIEL-NON-VALIDE` ; formulaire retiré ; échéancier : « Déclarée » |

**L'essai a trouvé un défaut que personne n'avait vu** : sous l'accusé déposé, l'écran affichait « le NaN/NaN/NaN ».
`dateCourte`, `dateLongue` et `periode` ajoutaient `T00:00:00` à la chaîne reçue ; une date-heure devenait invalide.
Les trois fonctions gardent désormais le jour d'une date-heure, ce qui répare tous leurs appels. Limite dite : le jour
gardé est celui de l'horodatage UTC ; un accusé saisi entre minuit et une heure à Douala s'afficherait la veille.

Le panneau des relances n'a été vu que vide : le 15/09/2026 ne tombe sur aucun jalon. Le cas du 08/01/2027 est éprouvé
par les tests.

### État à la fin du pas 87

**3 080 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 84 %** (121 gestes sur 144 ; 91 % de ce que le backend permet), contre 81 % au pas 86.
**Priorité 3 : 88 %** (contre 62 %), E05 à 100 %. Contrat des écrans : 126 appels, 0 écart. Couverture des routes : 127 sur
141 (90 %).

**Ce que le projet sait faire qu'il ne savait pas.** Tenir l'échéancier jusqu'au dépôt de TVA consigné, et annoncer une
pénalité que l'adhérent paiera vraiment, avec le texte qui la fonde.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un paramètre cité dans une description et jamais lu n'est pas configuré : il est décoré.*

## Pas 88 — La boîte de réception reçoit au guichet, et un refus ne nomme plus le dossier d'autrui

### Pourquoi

Huitième lot : la boîte de réception (E03, **64 %**) et le document scanné d'une pièce (E02). Quatre gestes à brancher :
enregistrer une pièce reçue au cabinet (fichier puis pièce), lire les relances de pièces du jour, télécharger le document
d'une pièce.

### Ce que la relecture a trouvé

**Le bouton « Importer des pièces » était décoratif.** Il figurait sur la boîte de réception depuis sa construction, sans
action : une facture remise au guichet ne pouvait pas s'enregistrer, et le délai de collecte du dossier se mesurait sans
elle. Le même piège que le bouton groupé retiré au pas 75.

Les routes elles-mêmes tenaient : hors périmètre refusé, type réel lu dans les octets, empreinte recalculée. Deux
constats, jugés assumés par la conception, ne sont pas corrigés : un même document peut appuyer deux dossiers
(« deux adhérents peuvent légitimement déposer le même document »), et l'indication « déjà présent » d'un dépôt dit
qu'un fichier identique est déjà au magasin, ce qui suppose d'en détenir les octets.

### Ce que l'essai réel a trouvé

| Essai | Résultat |
| --- | --- |
| L'adhérent de LA COLOMBE demande le document d'une pièce de SARL BATIMENT PLUS | « aucun dossier **M081234567890P** accessible… » : le NIU du client propriétaire, et une réponse différente d'une pièce inexistante |
| Télécharger le document d'une pièce de démonstration | « Le document est introuvable au magasin », sur **toutes** les pièces de démonstration |
| Déclarer un dépôt au 01/12/2026 | refusé, mais « une pièce **plus ancienne** relève d'une reprise d'historique » |

- **Le NIU d'autrui dans un refus.** Cinq routes retrouvent le dossier sur la ressource demandée (fiche d'une pièce, son
  document, la demande de rectificative, une demande de pièce, une facture de démonstration) et appelaient
  `exiger_dossier`, dont le message nomme le NIU. Ce message est juste quand l'appelant a écrit le NIU dans l'adresse ; il
  fuit quand le NIU est lu sur la ressource. Les identifiants de démonstration étant séquentiels, on énumérait. **La
  docstring de la route de démonstration de la conformité affirmait déjà** qu'un hors-périmètre et une référence
  inexistante rendaient la même réponse.
- **Des documents annoncés et absents.** Les pièces de démonstration portaient une empreinte fabriquée sur leur référence
  et une taille inventée (180 Ko), sans fichier.

### Les corrections

- **`exiger_dossier` accepte `introuvable`** : le texte que la route rend pour une ressource inconnue. Les cinq routes le
  passent ; hors périmètre et absence ne se distinguent plus. Les routes où l'appelant écrit lui-même le NIU gardent le
  message qui invite à demander l'affectation.
- **Les documents de démonstration existent** : un PDF d'une page par pièce, valide (lu par `pdftotext`), portant les
  données de la facture, avec sa vraie empreinte et sa vraie taille. Ils sont rangés au magasin là où les pièces de
  démonstration sont chargées (magasin mémoire, amorçage), et nulle part ailleurs. Le doublon délibéré garde un autre
  fichier, donc une autre empreinte.
- **Une date de dépôt future est dite future.**

`tests/test_ressources_hors_perimetre.py`, 8 cas. **Huit mutations tuées**, dont une qui avait d'abord survécu : les
documents rangés sur disque par une exécution précédente faisaient passer le cas « chaque pièce rend son document » même
quand plus rien ne les rangeait. Le cas part désormais d'un magasin vide.

### Ce qui a été fait, à l'écran

- **Importer des pièces** (boîte de réception, `DEPOSER_PIECE`) : dossier, canal (guichet, courriel, WhatsApp, demandé et
  jamais supposé : les délais se mesurent par canal), date de dépôt déclarée, document, et ce qu'on sait de la pièce. Le
  corps du dépôt est **partagé avec le portail de l'adhérent** : une seule implémentation, les mêmes contrôles.
- **Relances à émettre aujourd'hui** (pièces attendues, `RELANCER_ADHERENT`) : jalon, demande, dossier, canal, escalade au
  delà de trente jours, et un lien vers la demande pour tracer la relance.
- **Document reçu** (détail d'une pièce) : un bouton par pièce portant la facture. Le document est **téléchargé, jamais
  inséré dans la page** : le backend le rend en pièce jointe avec `nosniff`. L'utilitaire de téléchargement est partagé avec
  l'export comptable du pas 85.

### L'essai réel

Magasin de fichiers vide au démarrage, compte C-004 (comptable) :

| Essai | Résultat |
| --- | --- |
| Canal « PORTAIL » envoyé par appel direct | « Indiquez comment la pièce est arrivée… » |
| Dépôt daté du 01/12/2026 ; un document HTML déguisé en PDF | « dans l'avenir » ; « Type de document refusé » |
| Facture remise au guichet le 11/09, saisie le 15/09 | pièce `PJ-M08123-7aad84d87869a839`, déposée le 11/09, canal « déposée au cabinet » |
| Détail de F-2026-0412 | trois documents : la pièce du guichet et les deux pièces de démonstration, tous téléchargés en PDF |
| L'adhérent de LA COLOMBE force le document de la pièce du guichet | « pièce PJ-M08123-… introuvable. », sans NIU |
| Chargée de clientèle ; comptable ; direction | panneau des relances ; pas de panneau ; pas de bouton d'import |

Limite dite : l'essai compare les documents de démonstration à leur empreinte côté backend (tests) ; la liste des pièces
ne rendant pas l'empreinte, l'essai réel vérifie leur nom, leur type et leur téléchargement. Le panneau des relances n'a
été vu que vide.

### État à la fin du pas 88

**3 088 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 87 %** (125 gestes sur 144 ; **94 %** de ce que le backend permet), contre 84 % au pas 87.
**Priorité 2 : 88 %** (contre 71 %), priorité 1 : 81 %. Contrat des écrans : 128 appels, 0 écart. Couverture des routes :
129 sur 141 (91 %).

**Ce que le projet sait faire qu'il ne savait pas.** Recevoir au guichet une facture papier, la retrouver au dossier avec
son document, et refuser à un tiers de dire à qui elle appartient.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une docstring qui promet un comportement n'est pas un test : c'est une hypothèse que personne n'a encore réfutée.*

## Pas 89 — Le fichier du personnel s'écrit, et un matricule ne déplace plus un salarié

### Pourquoi

Neuvième lot : le social et la paie (2 gestes sur 5). L'écran lisait le personnel et la déclaration du mois ; il
n'embauchait pas, n'ouvrait aucun contrat et n'affichait aucun bulletin.

### Ce que la relecture a trouvé

Sonde par un comptable qui suit LA COLOMBE, SARL BATIMENT PLUS et AGRO :

| Essai | Résultat |
| --- | --- |
| Inscrire sur LA COLOMBE un salarié au matricule `SAL-0004`, « INTRUS » | **201** : NKOULOU, salarié de BATIMENT, **renommé INTRUS et passé chez LA COLOMBE**, contrat de 410 000 FCFA compris |
| Ouvrir, par l'adresse de LA COLOMBE, un contrat au matricule `SAL-0001` | **201** : le salarié d'AGRO change de dossier |
| Ouvrir un CDI chevauchant le CDD en vigueur de TSANGA | **201**, puis bulletin d'août : **409**, « à cheval sur deux contrats » |
| Contrat dont la fin précède le début | **500** |

- **Le premier défaut faisait disparaître un salarié de la déclaration sociale de son employeur**, donc des
  cotisations CNPS dues pour lui. La route rangeait le salarié sous son matricule, sans regarder qui le portait.
- **Le second venait du rattachement** : la route rattachait le salarié au dossier **de l'adresse** avant d'écrire le
  contrat.
- **Le troisième rendait la paie impossible** pour tous les mois couverts, sans que l'écriture ait rien refusé.
- **Et le geste qui répare n'existait pas** : la route disait « un contrat ne se modifie pas, on le ferme et on en ouvre
  un nouveau », et aucune route ne fermait un contrat.

Deux autres constats, non corrigés : le bulletin calculait son net, ses charges et son coût employeur **sans les rendre**
(six propriétés non sérialisées), et le **groupe de risque professionnel** est un paramètre de requête, « A » par défaut,
que le dossier ne porte pas (question ouverte **Q25**).

### Les corrections

- **`application/personnel.py`**, trois cas d'usage :
  - `inscrire_un_salarie` refuse un matricule déjà attribué (409), dans ce dossier ou ailleurs. Le refus nomme la
    personne quand elle est du même dossier, et personne quand elle est d'un autre ;
  - `ouvrir_un_contrat` exige un salarié **du dossier de l'adresse** (sinon « introuvable », exactement comme un matricule
    inconnu) et refuse un chevauchement (409), en disant quoi faire : clore d'abord ;
  - `clore_un_contrat` et sa route `POST …/salaries/{matricule}/contrats/cloture` : fin exclue, comme partout dans le
    contexte ; clore « le 01/10 » laisse septembre au contrat clos.
- **Le rattachement se prend sur le salarié**, après vérification de son dossier. Le dépôt SQL en a besoin à chaque
  requête : l'essai sur PostgreSQL l'a rappelé, le premier jet l'ayant retiré.
- **Une fin avant le début rend 422.**
- **Le bulletin rend ses six totaux** (brut taxable, retenues salariales, charges patronales, net à payer, coût employeur,
  réserve de validation). L'écran ne recalcule pas le net, dont les avantages en nature sont exclus.

`tests/test_personnel_protege.py`, 11 cas, dont un sur **PostgreSQL réel** (inscrire, ouvrir, clore, rouvrir, chaque geste
une requête). **Sept mutations tuées** : matricule réattribuable, salarié d'autrui accepté, chevauchement accepté, nom
d'autrui dans le refus, fin avant début en 500, clôture sans garde, net non rendu. Une huitième mutation, rattacher au
dossier de l'adresse, s'est révélée **équivalente** une fois le salarié vérifié : elle n'est pas comptée.

### Ce qui a été fait, à l'écran

**Social et paie** (`/social`) :

- **Embaucher** (`SAISIR_ECRITURE`) : identité, numéro CNPS facultatif, et le premier contrat. Si le contrat échoue après
  l'inscription, l'écran le dit et le contrat s'ouvre depuis la ligne du salarié.
- **Sur chaque ligne** : « Bulletin », et pour qui saisit, « Clore » et « Nouveau contrat ».
- **Le bulletin** du mois affiché, dans l'ordre d'une fiche de paie : rémunération, retenues, net à payer, charges de
  l'employeur, coût employeur ; chaque taux à valider est marqué. Le groupe de risque se choisit, et l'écran dit qu'il est
  à confirmer sur la notification CNPS.

### L'essai réel

Compte C-004 (comptable) :

| Essai | Résultat |
| --- | --- |
| Embaucher sur LA COLOMBE au matricule `SAL-0004` | « le matricule SAL-0004 est déjà attribué… » ; BATIMENT garde NKOULOU et TSANGA |
| Embaucher Paul ESSOMBA, CDD de magasinier | « … est embauché » |
| CDI au 15/09 par-dessus son CDD ; contrat sur `SAL-0001` | « … Deux contrats ne se chevauchent pas : clore le contrat en vigueur… » ; « aucun salarié au matricule SAL-0001 dans ce dossier » |
| Clore au 01/10, puis CDI au 01/10 à 150 000 FCFA | « il court jusqu'au 01/10/2026 exclu » ; « Contrat CDI ouvert » |
| Bulletin d'août de NKOULOU | net à payer 373 010 FCFA ; coût employeur 571 478 FCFA en groupe A, **587 565 FCFA en groupe C** |
| Chargée de clientèle | bulletins lisibles, aucun geste d'écriture |

Limite dite : un CDD sans date de fin est accepté ; la règle de durée des contrats à durée déterminée n'est pas au
référentiel.

### État à la fin du pas 89

**3 099 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 89 %** (129 gestes sur 145 ; **96 %** de ce que le backend permet), contre 87 % au pas 88.
Social et paie : 100 %. Contrat des écrans : 133 appels, 0 écart. Couverture des routes : 132 sur 142 (92 %).

**Ce que le projet sait faire qu'il ne savait pas.** Tenir le fichier du personnel d'un adhérent, de l'embauche au
changement de contrat, jusqu'au bulletin, sans qu'une saisie dans un dossier ne retire un salarié d'un autre.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une route qui range sous une clé sans regarder qui la porte déjà n'enregistre pas : elle remplace.*

## Pas 90 — Tout ce que le backend permet est à l'écran, et le rulebook n'est plus lisible par un adhérent

### Pourquoi

Dixième lot, et le dernier des gestes qu'un backend permet déjà : le catalogue des règles de conformité et l'essai d'une
règle sur une facture (E11), le plan de la liasse (E12), l'état des canaux de contact (acquisition), la veille d'un seul
dossier (veille des seuils).

### Ce que la relecture a trouvé

**La route du catalogue des règles se contredisait.** Sa docstring : « le rulebook est le produit, exactement ce que le
cabinet vend et ce qu'un concurrent recopierait en une après-midi ». Elle n'exigeait pourtant que `LIRE_DOSSIER`, que
l'adhérent détient sur son propre dossier. Essai : **l'adhérent de SARL BATIMENT PLUS lisait le catalogue entier,
prédicats exécutables compris**. Et depuis la souscription en ligne (pas 83), devenir adhérent est à la portée de tous.

La réponse de l'état des canaux était un dictionnaire libre, que l'outil de contrat ne pouvait pas vérifier.

### Les corrections

- **Le catalogue est réservé au cabinet** : `LIRE_DOSSIER` reste exigée, et `interne` en plus. Le refus est un 403 : aucune
  donnée de dossier n'est en jeu. L'inspecteur des impôts, externe, est refusé lui aussi : il lit les dossiers qu'on lui
  ouvre, pas la mécanique de contrôle du cabinet.
- **L'état des canaux déclare son modèle** ; la réponse est identique.

`tests/test_catalogue_des_regles_reserve.py`, 5 cas (adhérent et inspecteur refusés, trois rôles du cabinet servis avec
les prédicats). **La mutation qui retire la garde est détectée.**

### Ce qui a été fait, à l'écran

- **Référentiel et règles** : le **catalogue**, chaque règle dépliable avec son fondement, sa source, son message, sa
  remédiation et **le prédicat tel que le moteur l'exécute** (le traduire en français ferait une seconde version de la
  règle) ; et **Éprouver les règles sur une facture** (`CONTROLER_CONFORMITE`) : une facture de démonstration, modifiable
  à la main, contrôlée à une date. Rien n'est enregistré, et le périmètre de la session s'applique au destinataire.
- **Clôture** : le **plan de la liasse**, système normal ou minimal de trésorerie : chaque poste et les comptes qui s'y
  ventilent, pour répondre à « pourquoi ce montant est-il là ? ».
- **Demandes entrantes** : les **canaux de contact**, exploités ou non, et pourquoi.
- **Veille des seuils** : chaque dénomination ouvre la **veille du dossier**, exercice clos et exercice en cours, sans
  extrapolation.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Référentiel, compte C-004 | catalogue avec FAC-ACH-007 et son prédicat ; panneau d'essai |
| Essai sur F-2026-0412, réglée en espèces | constat FAC-ACH-007 |
| La même, réglée par virement | « Conforme, aucun constat » |
| JSON cassé ; destinataire d'un dossier non suivi | « La facture n'est pas du JSON lisible… » ; « aucun dossier P019876543210K accessible… » |
| Clôture, système minimal puis normal | plan affiché ; « Immobilisations incorporelles » |
| Demandes entrantes, chargée de clientèle et direction | canaux, et le motif de WhatsApp non exploité |
| Veille de SARL BATIMENT PLUS | exercice clos 2025 et en cours 2026, lus dans les livres |
| Adhérent, catalogue par l'API | 403 |

Limite dite : le chiffre d'affaires de SARL BATIMENT PLUS est nul dans les données de démonstration, qui ne portent pas de
ventes ; la veille est juste, mais sans enjeu à l'essai.

### État à la fin du pas 90

**3 104 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 92 %** (134 gestes sur 145), soit **100 % de ce que le backend permet**, contre 89 % au pas 89.
Contrat des écrans : 138 appels, 0 écart. Couverture des routes : 135 sur 142 (95 %).

**Ce qui reste n'est plus du branchement.** Les onze gestes sans backend demandent une décision du cabinet ou un produit
qui n'existe pas :

| Geste | Ce qu'il attend |
| --- | --- |
| Écarter un constat | motif, second regard, conséquence sur la liasse (pas 74) |
| Modifier un paramètre, valider une version, construire une règle sans syntaxe | l'écriture du référentiel, aujourd'hui en fichiers YAML relus par un fiscaliste |
| Rétablir un compte suspendu | exposer un cas d'usage qui existe au domaine, avec son contrôle |
| Marquer des pièces comme lues | une transition de lecture, retirée faute de backend au pas 75 |
| Lire ses notifications ; recherche globale | un service de notifications et une recherche transversale |
| Photographier ; file hors ligne ; rejeu au retour du réseau | l'application mobile |

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une permission dit ce qu'on peut lire ; elle ne dit pas pour qui l'on travaille.*

## Pas 91 — Rétablir un compte et lire une pièce : deux transitions du domaine enfin exposées

### Pourquoi

Au pas 90, tout ce que le backend permettait était à l'écran. Parmi les onze gestes restants, deux ne demandaient
**aucune décision du cabinet** : leur règle existait déjà au domaine, sans route. Lever la suspension d'un compte
(`retablir_compte`), et passer une pièce reçue à l'état LUE après l'avoir identifiée (`marquer_lue`).

### Ce que la relecture a trouvé

- **Rétablir un compte actif était accepté**, et écrivait « compte.retabli » au journal d'audit : une levée de suspension
  qui ne levait rien. Essai sur C-004, actif : état inchangé, ligne ajoutée au journal. Le journal est la pièce qu'on
  produit à un contrôle ; une ligne fausse y vaut pire qu'une absence.
- **« Relire » une pièce déjà lue réécrivait ses données** : la transition du domaine accepte LUE vers LUE avec de nouveaux
  montant et numéro, sur lesquels un contrôle ou une écriture a pu s'appuyer.
- Le titulaire d'un compte suspendu est prévenu par courriel ; celui d'un compte rétabli ne l'était pas (aucun gabarit).

### Les corrections

- **`retablir_compte` refuse un compte qui n'est pas suspendu** (`RetablissementRefuse`, 409). Les habilitations ne sont
  pas touchées, et c'est écrit : un collaborateur parti a les siennes fermées à sa date de départ, et rétablir son compte
  ne lui rend aucun dossier.
- **`POST /transverse/comptes/{identifiant}/retablissement`** (`GERER_COMPTES`), motif d'au moins dix caractères dans un
  corps fermé ; le titulaire reçoit le nouveau gabarit **`compte.retabli`**.
- **`application/lecture.py`** : `lire_une_piece` ne lit qu'une pièce **reçue** ; seuls les champs fournis complètent la
  pièce, un champ absent n'efface pas ce que l'adhérent avait déclaré ; la règle du domaine (une pièce ne se lit
  qu'identifiée) reste entière.
- **`POST /collecte/pieces/{identifiant}/lecture`** (`IDENTIFIER_PIECE`) ; hors portefeuille, la même réponse qu'une pièce
  inconnue (pas 88).

`tests/test_retablir_et_lire.py`, 11 cas. **Six mutations tuées** : rétablir un compte actif, titulaire non prévenu,
relire une pièce lue, champ absent qui efface, lecture hors périmètre qui nomme le dossier, motif non exigé.

### Ce qui a été fait, à l'écran

- **Comptes et habilitations** : « Rétablir » sur chaque compte suspendu, avec motif ; le message rappelle que les
  habilitations fermées ne sont pas rouvertes.
- **Boîte de réception** : « N pièces reçues à identifier », replié en tête de la boîte pour qui identifie ; pour chaque
  pièce, son document à télécharger et un formulaire prérempli de ce que l'adhérent avait déclaré. Un geste par pièce :
  « marquer comme lu » en groupe, qui avait été retiré au pas 75, reviendrait à dire lues des pièces non identifiées.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Administration, C-008 suspendu, motif « oups » | « Écrivez pourquoi la suspension est levée… » |
| Motif complet | « Compte rétabli, titulaire prévenu. Ses habilitations fermées ne sont pas rouvertes… » ; courriel à a.tchinda@cga-brcg.cm |
| Rétablir C-004, actif | « le compte C-004 n'est pas suspendu (état ACTIF) : il n'y a rien à rétablir. » |
| Comptable, boîte de réception | « 1 pièce reçue à identifier » |
| PJ-2026-0028 sans données, puis identifiée | « lecture impossible, il manque [type, reference_document…] » ; « identifiée et lue » ; plus aucune pièce à identifier |
| La relire avec un autre montant | « est à l'état LUE : seule une pièce reçue se lit… » |
| Direction ; réviseur | pas de panneau ; panneau présent |

### État à la fin du pas 91

**3 115 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 94 %** (136 gestes sur 145), 100 % de ce que le backend permet, contre 92 % au pas 90.
Contrat des écrans : 140 appels, 0 écart. Couverture des routes : 137 sur 144 (95 %).

**Restent neuf gestes**, qui ne se construisent plus sans décision : écarter un constat (motif, second regard,
conséquence sur la liasse), écrire et valider le référentiel et construire une règle sans syntaxe (un circuit de
validation par un fiscaliste), les notifications et la recherche globale (deux services), et l'application mobile
(photographier, file hors ligne, rejeu).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une transition que le domaine sait faire et qu'aucune route n'expose n'est pas une fonctionnalité : c'est une promesse
qu'on n'a pas encore éprouvée.*

## Pas 92 — Écarter un constat : motif, second regard, et une politique que le code ne décide pas

### Pourquoi

« Écarter un constat » figurait au pied de l'écran E02 depuis le premier jour, sous la forme d'un bouton sans action.
Au pas 74, la note de la grille disait ce qui manquait : *motif, second regard, conséquence sur la liasse*. C'est le
seul contournement légitime d'un contrôle de conformité, et donc le geste le plus délicat du contexte : mal construit,
il vide tout le produit de son sens.

La permission existait (`ECARTER_CONSTAT`, réviseur seul, motif exigé), et le moteur l'avait prévu : une conséquence
*décrit*, elle n'applique rien. Mais aucune route, aucun stockage, et aucun consommateur ne savait qu'un constat pouvait
être écarté.

### Ce que la relecture a établi

- **Un rapport ne se conserve pas, il se recalcule** sur le référentiel daté. Ce qui doit se conserver, c'est la
  *décision* du cabinet sur ce rapport. La conformité n'avait aucune table : elle en a désormais une.
- **Trois consommateurs décident sur un rapport** : l'écran de la pièce, la boîte de réception, et la proposition
  d'écriture de la comptabilité (qui pose l'attribut fiscal, lu ensuite par les réintégrations de la liasse). Un écart
  que l'écran afficherait et que la proposition ignorerait serait le pire des états : « écarté » à l'écran, TVA rejetée à
  l'écriture, et un comptable qui irait saisir à la main pour « corriger ».
- **Trois questions relèvent du cabinet** et non du logiciel : quelles sévérités s'écartent, lesquelles exigent un
  second regard, et qui peut le donner.

### Les choix

- **La politique est au référentiel** (`Docs/referentiel/ecarts/politique.yaml`), avec le réglage le plus prudent par
  défaut : sans fichier, rien n'est écartable ; une sévérité non nommée est fermée ; une clé mal orthographiée fait
  échouer le chargement plutôt que d'être ignorée. Le fichier livré est une proposition (question **Q26**) : BLOQUANT
  fermé, MAJEUR avec second regard, AVERTISSEMENT et INFORMATION sans, second regard par le réviseur (autre que l'auteur)
  ou le fiscaliste, motif d'au moins 20 caractères.
- **Écarter n'efface rien.** Le rapport arbitré est un nouveau rapport : le constat passe de `constats` à
  `constats_ecartes`, avec l'identifiant de la décision. Toutes les propriétés (`conforme`, `tva_deductible`,
  `comptabilisation_interdite`, `enjeu_total`) lisent `constats` et suivent sans rien savoir des écarts.
- **Un écart vaut pour le constat examiné.** Il retient une empreinte (règle, sévérité, enjeu normalisé, conséquence).
  Si la facture ou le référentiel change l'enjeu, l'écart devient *caduc* et le constat revient. Un arrondi différent du
  même montant ne rend pas caduc.
- **La politique est relue au moment d'appliquer.** La durcir suspend les écarts qui ne la respectent plus ;
  l'assouplir ne confirme pas ce qui attend un second regard.
- **Celui qui propose ne tranche pas**, et la vérification est au domaine (`EcartDeConstat.trancher`), pas dans la route.
- **L'adhérent voit qu'un constat est écarté, jamais le motif** : `ConstatEcarte` ne porte ni auteur ni motif, et la
  liste des écarts n'est rendue qu'au cabinet.
- **Une décision, une ligne** : un écart refusé puis reproposé fait deux lignes (le rang est dans l'identifiant), et
  chaque geste écrit au journal d'audit (`conformite.ecart_propose`, `_confirme`, `_refuse`, `_leve`) avec son motif.

### Ce qui a été fait, au backend

- Domaine : `conformite/domaine/ecarts.py` (`PolitiqueDEcart`, `RegleDEcart`, `EcartDeConstat`, `StatutEcart`,
  `empreinte_du_constat`, `MotifInsuffisant`), `ConstatEcarte` et `RapportConformite.constats_ecartes`, port `DepotEcarts`.
- Application : `conformite/application/ecarts.py` (`proposer_un_ecart`, `trancher_un_ecart`, `lever_un_ecart`,
  `etat_des_ecarts`, `appliquer_les_ecarts`).
- Adaptateurs : chargement de la politique, dépôts mémoire (rangé par locataire) et SQL, table `ecart_de_constat`
  (clé `(locataire, identifiant)`, sécurité par ligne) et sa migration ; la conformité entre au recensement des tables.
- Surface : `politique_d_ecart()` et **`rapport_arbitre(rapport, dossier)`**, par lequel passe tout consommateur qui
  décide sur un rapport. La proposition d'écriture de la comptabilité l'emploie.
- Routes : `GET /conformite/ecarts/politique` (cabinet), `GET /conformite/ecarts/en-attente` (restreinte au périmètre),
  `POST /conformite/pieces/{reference}/ecarts`, `…/{identifiant}/second-regard`, `…/{identifiant}/levee`. Motif trop court
  pour la politique : 422 ; refus de la politique ou de l'état : 409 ; pièce ou écart inconnu, ou hors périmètre : 404.
- Les trois routes qui contrôlent passent par un seul chemin (`_reponse`) : la boîte de réception et le détail rendent le
  même verdict. **Le verdict dit l'écart** : « Conforme après écart, 1 constat écarté » et non « aucun constat ».

### Les défauts trouvés en chemin

- **Le second regard du réviseur tombait en 403** : `ECARTER_CONSTAT` exige un motif, et la route ne le transmettait pas
  au contrôle de périmètre. Corrigé, et le cas « le réviseur tente de confirmer son propre écart » rend bien 409.
- **Le test de surface des permissions a refusé la route du second regard** : le contrôle de périmètre était caché dans
  une aide. Il est désormais écrit dans le corps de chaque route, là où un relecteur le cherche.
- **La mesure de conformité disait « Conforme, aucun constat »** sur une facture dont un constat venait d'être écarté.

`tests/test_ecart_de_constat.py`, 28 cas dont un sur PostgreSQL. **Dix-sept mutations tuées** ; trois survivaient à une
première batterie et ont imposé des cas nouveaux : fermer une sévérité ne suspendait pas l'écart effectif, le dépôt mémoire
ne séparait pas les cabinets, et un écart en attente n'avait pas de raison propre.

### Ce qui a été fait, à l'écran

- **Détail d'une pièce** : le bouton décoratif propose désormais les seuls constats que la politique permet d'écarter, dit
  ceux qu'elle ferme, et annonce avant l'envoi si un second regard sera nécessaire. Un panneau « Écarts décidés sur cette
  pièce » donne pour chaque décision son auteur, son motif, son second regard, et la raison pour laquelle elle ne
  s'applique pas (en attente, caduc, suspendu). Le second regard n'est jamais proposé à l'auteur ; la levée l'est à qui
  détient le droit d'écarter. Les constats écartés restent lisibles, repliés, hors de tout calcul.
- **Boîte de réception** : « N écarts de constat en attente d'un second regard », pour qui la politique désigne.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Réviseur, F-2026-0412 (MAJEUR), motif « Vu au dossier. » | « le motif doit compter au moins 20 caractères… » |
| Motif complet | « Écart F-2026-0412:FAC-ACH-007:1 proposé : le constat compte jusqu'au second regard. » |
| Réviseur, la même pièce | panneau présent, « En attente du second regard », « Le second regard viendra d'une autre personne que vous », pas de bouton Confirmer |
| Fiscaliste, boîte de réception | « 1 écart de constat en attente d'un second regard » |
| Fiscaliste, confirme | « Écart … confirmé. » ; verdict « Conforme après écart, 1 constat écarté » |
| Comptable, proposition d'écriture | comptabilisable, aucun attribut fiscal (la TVA était rejetée avant l'écart) |
| Adhérent de SARL BATIMENT PLUS | ni panneau ni motif |
| Réviseur, lever | « Écart … levé : le constat FAC-ACH-007 compte de nouveau. » ; statut Levé, bouton Écarter revenu |

### État à la fin du pas 92

**3 146 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 95 %** (141 gestes sur 149), 100 % de ce que le backend permet, contre 94 % au pas 91.
Contrat des écrans : 145 appels, 0 écart. Couverture des routes : 142 sur 149 (95 %). L'écran E02, « le plus important
du produit », est complet.

**Restent huit gestes**, qui ne se construisent pas sans décision : écrire et valider le référentiel et construire une
règle sans syntaxe (un circuit de validation par un fiscaliste), les notifications et la recherche globale (deux
services), et l'application mobile (photographier, file hors ligne, rejeu).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Le seul contournement légitime d'un contrôle se reconnaît à ce qu'il laisse une trace plus lourde que le contrôle
lui-même.*

## Pas 93 — La recherche globale, fédérée : chaque service cherche chez lui

### Pourquoi

« Recherche globale » figurait en tête de chaque écran depuis la première coquille, avec son raccourci affiché, sous la
forme d'un bouton sans action. La grille notait : *aucune route de recherche transversale*. Des huit gestes restants,
c'était le seul qui ne demandait ni décision du cabinet ni application mobile.

### Le choix : fédérer plutôt que centraliser

La tentation était un module qui lirait les dossiers, les pièces, les comptes et les prospects pour les chercher lui-même.
Il aurait dû importer tous les contextes (le graphe des dépendances le refuse), recopier le périmètre de chacun (un
comptable ne voit que son portefeuille, un adhérent que son dossier), tomber avec le premier service en panne, et être
modifié à chaque source ajoutée.

La recherche est donc **fédérée** :

- **Chaque service qui a quelque chose à trouver expose sa route**, sous son préfixe, avec sa permission et son périmètre :
  `GET /portefeuille/recherche` (dossiers, `LIRE_DOSSIER`), `GET /collecte/recherche` (pièces, `LIRE_PIECE`),
  `GET /transverse/recherche` (comptes, `GERER_COMPTES`), `GET /acquisition/recherche` (demandes, `LIRE_PROSPECT`).
- **Il la déclare au registre des services** (`SourceDeRecherche` : chemin, libellé, permission). Déclarer, c'est
  brancher : `GET /transverse/services/recherche` rend les sources que la session peut appeler et qui sont montées, et
  l'écran les interroge toutes en parallèle.
- **Le contrat et la mécanique sont communs** (`app/partage/recherche.py`) : une seule normalisation (accents, casse,
  espaces), tous les termes exigés, les identifiants avant les libellés (100 identique, 80 préfixe d'identifiant,
  60 préfixe de libellé, 40 contenu), une requête trop courte refusée une fois (422), une liste bornée qui dit qu'elle
  l'est.
- **Les réglages sont au référentiel** (`Docs/referentiel/recherche/reglages.yaml`) : trois caractères significatifs,
  dix résultats par source ; sans fichier, les mêmes valeurs ; une clé mal orthographiée fait échouer le chargement.

Ajouter une source demain (les écritures, les obligations) : écrire la route sous le préfixe du service et la déclarer.
Ni la coquille ni un module central ne changent ; l'écran l'interroge par son chemin déclaré, et le test « déclarer,
c'est brancher » vérifie qu'elle existe, sous le bon préfixe, accepte `q` et rend le contrat commun.

### Les défauts trouvés en chemin

- **Une fonction importée masquait une route** : la collecte a une route `classer` (classer une demande sans suite) ;
  importer `classer` de la recherche l'avait remplacée, et la recherche des pièces tombait en erreur interne en appelant
  un contrôle d'accès sur une chaîne. L'import est renommé partout (`classer_les_resultats`).
- **L'outil de contrat confrontait un chemin entièrement dynamique à une route tirée au hasard** : `${source.chemin}`
  devenait `{}{}`, que le motif large faisait correspondre à n'importe quelle route, d'où un faux ABSENT. Sans segment
  littéral, l'appel est désormais déclaré ILLISIBLE, ce qu'il est.
- **Deux outils de mesure lisaient mal une chaîne de requête interpolée** collée au chemin : `/conformite/controler${requete}`
  passait pour un appel sans route depuis le pas 90, et l'essai des règles manquait à la couverture. Une interpolation
  collée à un mot est une chaîne de requête ; seule celle qui suit une barre est un segment. La couverture passe de 145 à
  148 routes appelées.
- **Une requête trop courte s'affichait « recherche indisponible »** sous chaque groupe. Ce n'est pas une panne : la
  phrase du réglage s'affiche une fois, en tête.

`tests/test_recherche_globale.py`, 35 cas dont un sur PostgreSQL. **Seize mutations tuées**, dont une qui survivait à la
première batterie (une source déclarée mais non montée restait proposée) et a imposé un cas. La liste close des routes
d'acquisition a fait son travail : la nouvelle route y est entrée, avec sa protection.

### Ce qui a été fait, à l'écran

- **La coquille** : le bouton décoratif est un champ de recherche ; le raccourci affiché (Ctrl K ou ⌘ K) lui donne le focus.
- **`/recherche`** : un groupe par source, chacun avec son état propre (résultats, aucun résultat, liste tronquée,
  indisponible). « Aucun résultat » et « la source n'a pas répondu » ne se confondent pas : un comptable conclurait qu'une
  pièce n'existe pas alors que la collecte est en panne. Chaque résultat ouvre son écran (fiche du dossier, pièce, comptes,
  demande).

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Comptable de l'industrie, « bâtiment » | « 1 résultat dans 2 sources », SARL BATIMENT PLUS ; groupes Dossiers et Pièces |
| « F-2026-0412 » | 2 pièces (le doublon de démonstration), lien vers l'écran de la pièce |
| Réviseur, « 2026 » | « D'autres résultats existent : précisez la recherche » |
| « a » | « Précisez : la recherche demande au moins 3 caractères significatifs. », sans « indisponible » |
| Comptable des services, « batiment » | 0 résultat : le dossier est hors de son portefeuille, et rien ne le révèle |
| Administration, « leonard » | Léonard FOTSO ; groupes Comptes du cabinet et Demandes et prospects |

### État à la fin du pas 93

**3 181 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 95 %** (146 gestes sur 153), 100 % de ce que le backend permet. Contrat des écrans : 150 appels
vérifiés, 0 écart, 1 appel générique déclaré illisible. Couverture des routes : 148 sur 154 (96 %).

**Restent sept gestes** : les notifications (un service à concevoir), écrire et valider le référentiel et construire une
règle sans syntaxe (un circuit de validation par un fiscaliste), et l'application mobile (photographier, file hors ligne,
rejeu).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une recherche qui voit tout est un contournement de chaque périmètre ; une recherche fédérée n'en voit aucun de plus que
la liste qu'elle remplace.*

## Pas 94 — Les notifications : une lecture du journal d'audit, déclarée au référentiel

### Pourquoi

La cloche de l'en-tête était un bouton sans action ; son compteur écrit en dur (« 4 ») avait été retiré au pas 76, faute de
backend. Au pas 92, le second regard sur un écart de constat a rendu le manque concret : un écart en attente attendait
qu'un fiscaliste tombe dessus en ouvrant la pièce.

### Le choix : ne rien stocker que la position de lecture

La tentation était que chaque geste écrive une notification pour chaque destinataire. Chaque contexte aurait dû savoir qui
prévenir, **au moment du geste** : un réviseur affecté le lendemain ne recevrait rien, un collaborateur parti garderait ses
avis, et chaque nouvelle notification demanderait de modifier le code d'un geste qui marchait.

Or tout geste qui compte écrit déjà au **journal d'audit**. Une notification est donc une **lecture** de ce journal,
filtrée par une question : *cette entrée concerne-t-elle la personne qui regarde ?*

- **Les abonnements sont au référentiel** (`Docs/referentiel/notifications/abonnements.yaml`) : pour une action du
  journal, les destinataires (une permission détenue, le périmètre du dossier nommé dans l'entrée, ou un compte nommé
  dans l'entrée), des conditions (`si: {statut: EN_ATTENTE}`), un titre, un texte et un lien écrits en gabarits.
- **Le moteur** (`transverse/domaine/notifications.py`) résout les destinataires **pour la session qui lit, à l'instant
  de la lecture** : une habilitation retirée ce matin ne voit plus rien. On ne reçoit jamais l'avis de son propre geste.
  Pour une entrée, le **premier abonnement qui correspond** décide, et non le premier qui concerne le lecteur.
- **Ce qui est conservé** : la position de lecture, un **rang** du journal (unique et croissant, jamais une heure), qui
  n'avance que vers l'avant et s'arrête à la tête du journal. Table `lecture_des_notifications`, clé `(locataire, compte)`.
- **Prudence par défaut** : sans fichier, aucune notification (un texte que personne n'a relu, à des destinataires que
  personne n'a choisis, serait pire que le silence) ; un abonnement sans permission ni compte est refusé au chargement
  (il notifierait tout le cabinet) ; une clé mal orthographiée fait échouer le chargement.
- **Le motif d'une entrée n'est jamais lisible par un gabarit** : c'est souvent une note interne, et les notifications
  sont lues par des personnes qui n'ont pas `LIRE_AUDIT`.

Dix abonnements livrés : l'écart à trancher et l'écart écarté sans second regard (la même action, selon son statut),
l'écart confirmé, refusé ou levé, la déclaration déposée (pour l'adhérent comme pour le cabinet), l'accès accordé, le
dossier confié, la souscription dont l'identité est à vérifier, le paiement rejeté et le paiement sans référence.

### Ce que la relecture a demandé au journal

Deux entrées ne nommaient pas leur destinataire en clair : `dossier.affecte` ne disait pas **à qui** le dossier était
confié (seulement l'identifiant d'habilitation), et `obligation.deposee` ne portait le dossier que dans `objet_id`
(« NIU/CODE »). Elles portent désormais `compte`, et `dossier` et `obligation`. Découper un identifiant composé aurait
fait dépendre un avis d'un format.

### Routes et écrans

- `GET /transverse/notifications` : les notifications de la session dans la fenêtre du réglage (30 jours), le nombre de
  non lues, et la source des abonnements. `POST /transverse/notifications/lecture` : avancer sa position. Toutes deux
  inscrites à la liste des routes sans permission, avec leur motif : chacun ne lit que les siennes.
- **La cloche** mène à `/notifications` ; sa pastille vient du gabarit, lu une fois, et dit le nombre en clair au lecteur
  d'écran. « Tout marquer comme lu » envoie le rang de la plus récente **affichée** : une notification arrivée entre
  l'affichage et le clic reste non lue.
- **L'espace adhérent** montre « Du nouveau sur votre dossier », les non lues seulement, **sans liens** : ils mèneraient
  aux écrans de travail du cabinet, qui refuseraient l'adhérent.

`tests/test_notifications.py`, 18 cas dont un sur PostgreSQL : chaque action abonnée est bien écrite par le code, aucun
gabarit ne lit le motif, et deux gestes réels (l'écart en attente, le dossier confié) s'annoncent à la bonne personne et à
elle seule. **Quatorze mutations tuées**, dont une (la fenêtre par défaut) qui survivait et a demandé une assertion.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Fiscaliste, avant tout geste | cloche sans pastille |
| Réviseur écarte FAC-ACH-007 sur F-2026-0412 | « proposé : le constat compte jusqu'au second regard » |
| Fiscaliste | « Notifications, 1 non lue » ; « Écart à trancher sur F-2026-0412 », marqué « Nouveau », sans le motif |
| « Tout marquer comme lu » | pastille disparue, plus de « Nouveau » |
| Réviseur, auteur de l'écart | « Aucune notification » |
| Direction confie la clinique à Léonard FOTSO | le comptable lit « Le dossier M093344556677N vous est confié » |
| Adhérent sans nouvelle | espace entier, pas de section vide |

### État à la fin du pas 94

**3 202 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 96 %** (148 gestes sur 154), 100 % de ce que le backend permet ; **priorité 1 à 100 %**.
Contrat des écrans : 152 appels vérifiés, 0 écart. Couverture des routes : 150 sur 156 (96 %).

**Restent six gestes**, qui ne se construisent pas sans décision ou sans application : écrire un paramètre, valider une
version et construire une règle sans syntaxe (un circuit de validation par un fiscaliste, et l'écriture d'un référentiel
aujourd'hui versionné en fichiers), et l'application mobile (photographier, file hors ligne, rejeu).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Le journal savait déjà tout ce qui s'était passé ; il manquait seulement de savoir à qui le dire.*

## Pas 95 — Décider sur le référentiel : effet immédiat, pour le seul cabinet

### Pourquoi, et la décision du propriétaire

Des gestes restants, trois touchaient l'écriture du référentiel (modifier un paramètre, valider une version, construire
une règle sans syntaxe). Ils ne se construisaient pas sans une décision : une validation faite à l'écran doit-elle changer
les calculs tout de suite, et pour qui ? La question a été posée ; **le propriétaire a choisi l'effet immédiat, par
cabinet**, plutôt qu'un circuit suivi d'un report au fichier commun.

Neuf valeurs légales attendent d'ailleurs leur validation depuis le 18 août (délai de dépôt de la DSF, format du NIU,
plafond de l'abattement CGA…) : elles ne pouvaient l'obtenir qu'en éditant un fichier.

### Le choix : une surcouche du cabinet, jamais une réécriture du fichier

- **Le référentiel commun reste `parametres.yaml`**, versionné, lu par tous les cabinets. Les décisions d'un cabinet
  forment une **surcouche** (`referentiel/domaine/surcouche.py`), appliquée à la lecture pour lui seul : un autre cabinet
  lit le fichier intact.
- **Trois gestes** : valider une version livrée « à valider » (un seul geste, au nom de la personne qualifiée) ; proposer
  une nouvelle version datée, **sans effet** jusqu'à sa validation ; trancher une proposition (valider ou refuser).
- **Chaque version issue d'une décision porte qui l'a validée, quand, et sur quel texte**, exactement comme une version du
  fichier : c'est ce que le rapport de conformité recopie.
- **Les dates** : une nouvelle version s'insère à sa date, interrompt celle qui la couvrait, conserve les versions
  postérieures du fichier, reprend la **borne** du seuil (« dès » ou « au-delà de »). Une date passée est refusée : les
  calculs déjà rendus changeraient sans que personne ne les relise. À la même date qu'une version du fichier, la décision
  du cabinet la remplace. Une validation que le fichier commun a entre-temps rendue inutile est **sans objet** et ne
  réécrit pas sa signature.
- **La valeur est vérifiée à l'unité** : « 19,25 % » en texte pour un pourcentage, un jour du mois à 32, une expression
  régulière invalide sont refusés à celui qui peut les corriger.

### Le circuit, au référentiel

`Docs/referentiel/validation/circuit.yaml` dit qui propose et qui valide, selon la nature du paramètre. **Sans fichier,
personne ne décide rien** ; une nature absente est fermée ; une clé mal orthographiée fait échouer le chargement.

| Nature | Propose | Valide | Quatre yeux |
| --- | --- | --- | --- |
| LOI (un texte fixe la valeur) | `MODIFIER_PARAMETRE` (fiscaliste) | `MODIFIER_PARAMETRE`, `DEPOSER_DECLARATION` (réviseur) | oui |
| POLITIQUE_CABINET (aucun texte) | `MODIFIER_PARAMETRE`, `ARRETER_POLITIQUE` | `ARRETER_POLITIQUE` (direction) | non |

**Nouvelle permission `ARRETER_POLITIQUE`**, détenue par la direction : la direction n'a pas qualité pour attester un taux
légal, le fiscaliste n'a pas qualité pour décider du poids d'un retard dans une note interne. ⚠️ Le premier jet du circuit
désignait `CLOTURER_EXERCICE` pour valider un taux légal ; la direction la détient aussi, et un test l'aurait laissée
signer la TVA. C'est `DEPOSER_DECLARATION`, détenue par le seul réviseur, qui désigne celui qui dépose les déclarations
calculées avec ce taux.

### Ce qu'il a fallu corriger dans tout le produit : dix montages du référentiel

**Dix modules construisaient chacun leur lecture du fichier**, et la plupart la mémoïsaient (portefeuille, social,
obligations, création d'entreprise, pilotage, clôture, référentiel lui-même, et le moteur de conformité entier). Tant que
le fichier était la seule source, c'était sans conséquence. Avec une décision du cabinet, un montage mémoïsé aurait gardé
l'ancien taux jusqu'au redémarrage : la conformité aurait rejeté une TVA que l'échéancier acceptait.

Tous passent désormais par **`service_parametres()`**, le point de montage unique de la surface publique du référentiel :
le fichier commun est relu seulement quand il change (sa date de modification est dans la clé du cache), les décisions du
cabinet courant sont appliquées à chaque lecture. Le moteur de conformité garde ses **règles** en cache et prend les
**paramètres** du cabinet à chaque montage. La suite complète est restée verte après ce seul changement, avant tout geste
nouveau.

### Deux contraintes d'architecture, et comment elles ont été tenues

- **Le référentiel appartient au socle et ne lit pas le transverse** (le transverse le lit, l'inverse ferait un cycle). Il
  lui fallait pourtant une session SQL pour conserver les décisions. La session est désormais posée **là où elle naît**,
  dans l'infrastructure : `session_courante()`, ouverte et refermée par `session_du_locataire`.
- **Décider suppose de savoir qui parle**, ce que le référentiel ignore. Les routes vivent donc **au transverse**
  (`/transverse/referentiel/...`), qui identifie, confronte la session au circuit, journalise, et appelle les cas d'usage
  par la surface publique du référentiel. Le référentiel conserve et applique.

Routes : `GET /transverse/referentiel/circuit` (ce que ma session peut décider), `GET /transverse/referentiel/decisions`,
`POST …/parametres/{code}/versions/{applicable_du}/validation`, `POST …/parametres/{code}/propositions`,
`POST …/decisions/{identifiant}/tranchage`. Réservées au cabinet ; 403 hors du circuit, 404 inconnu, 409 refusé.
Journal : `referentiel.version_validee`, `version_proposee`, `proposition_validee`, `proposition_refusee`, avec la nature.
Notifications : une proposition sur une valeur légale s'annonce au fiscaliste et au réviseur, une proposition de politique
à la direction.

`tests/test_decisions_referentiel.py`, 38 cas dont un sur PostgreSQL : la surcouche, le cloisonnement entre cabinets,
le circuit, et la valeur validée **vue par la paie et par le moteur de conformité au calcul suivant**. **Vingt et une
mutations tuées**, dont deux qui survivaient à la première batterie (la décision qui remplace une version du fichier à la
même date, la validation devenue sans objet) et ont imposé chacune un cas.

### Ce qui a été fait, à l'écran

L'écran du référentiel disait « il ne modifie rien ». Il porte désormais un panneau **« Décisions du cabinet »** :
propositions à trancher (jamais proposées à leur auteur quand le circuit exige quatre yeux), versions livrées à valider,
formulaire de proposition (valeur, date d'effet, texte et source du fondement, motif, avec l'avertissement « sans effet
tant qu'elle n'est pas validée »), et historique avec les décisions devenues sans objet. Rien n'est affiché que le circuit
refuserait : l'écran le lit.

### L'essai réel

| Essai | Résultat |
| --- | --- |
| Fiscaliste | panneau, versions à valider, formulaire de proposition |
| Proposer « vingt » pour la TVA | « une valeur numérique est attendue pour l'unité POURCENTAGE » |
| Proposer « 20,0 » au 01/01/2027 | « Proposition … enregistrée : sans effet tant qu'elle n'est pas validée » ; l'auteur lit « Une autre personne désignée par le circuit la validera » |
| Direction | pas de bouton de validation : « Le circuit ne vous désigne pas pour la trancher » |
| Réviseur valide | « nouvelle valeur appliquée aux calculs du cabinet » ; TVA au 02/01/2027 : 20 |
| Réviseur valide le délai DSF livré à valider | validé pour le cabinet ; 8 paramètres restent à valider au lieu de 9 |
| Comptable | l'historique des décisions se lit, sans aucun geste |

### État à la fin du pas 95

**3 243 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 97 %** (153 gestes sur 157), 100 % de ce que le backend permet. Contrat des écrans : 157 appels
vérifiés, 0 écart. Couverture des routes : 155 sur 161 (96 %).

**Restent quatre gestes** : construire une règle de conformité sans syntaxe (les règles restent des fichiers relus en revue,
et une règle mal écrite rejette des TVA à tort) et l'application mobile (photographier, file hors ligne, rejeu).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un cabinet peut désormais calculer autrement que ses confrères ; il ne peut pas le faire sans qu'on sache qui l'a décidé,
quand, et sur quel texte.*

## Pas 96 — Photographier, garder sans réseau, rejouer sans rien casser

### Pourquoi

Trois gestes restaient à l'application mobile : photographier le document, mettre un dépôt en file sans réseau, rejouer
la file au retour du réseau. L'inventaire décrit un adhérent qui photographie sa facture là où il la reçoit (au marché,
sur un chantier), et le réseau y manque souvent. Sans file, la photo est perdue au premier « échec d'envoi ».

Il n'existe pas d'application mobile, et il n'en faut pas pour ces trois gestes : l'espace adhérent est déjà conçu pour
le téléphone. Ils se construisent dans le navigateur.

### Ce que la relecture a trouvé d'abord : le rejeu effaçait le travail du cabinet

Une file rejoue par construction : une réponse perdue après un envoi réussi fait renvoyer le même dépôt. Avant de la
construire, le rejeu a été essayé. La route promettait : « un client dont la connexion tombe après l'envoi peut
recommencer sans crainte ».

| Essai | Résultat avant le pas 96 |
| --- | --- |
| L'adhérent dépose une facture | 201, pièce RECUE |
| Le comptable la lit : facture d'achat, numéro, montant | 200, pièce LUE |
| L'adhérent rejoue le même envoi | **201, pièce redevenue RECUE, sans type, sans numéro, sans montant, avec une nouvelle heure de réception** |

L'identifiant dérive du fichier et du dossier ; le détecteur de doublons écarte, à raison, la pièce de même identifiant
(ce n'est pas un doublon, c'est elle) ; et la route l'enregistrait par-dessus. L'heure de réception réécrite est celle
dont le domaine dit que « seule celle-ci fait foi ». Une file hors ligne aurait effacé la lecture du cabinet à chaque
retour du réseau.

**Correction, au domaine** : `receptionner` rend une pièce de même identifiant déjà au dossier **telle quelle**, avec
`rejeu: true`, et la route ne l'enregistre pas et répond **200** (rien n'a été créé). Un test existant affirmait le 201 du
rejeu ; il a été mis à jour, avec la raison. `tests/test_depot_rejoue.py`, 6 cas dont un sur PostgreSQL ; **quatre
mutations tuées**.

Au passage, la déclaration de la réponse 200 sans son modèle avait vidé le schéma de la route, et l'outil de contrat
l'avait signalée illisible : le modèle est déclaré.

### Ce qui a été fait, à l'écran

- **Prendre une photo** : un second champ ouvre directement l'appareil photo (`capture="environment"`), et la photo prend
  la place du document choisi. Le champ principal garde la galerie et le PDF : forcer l'appareil photo sur le champ unique
  interdisait d'envoyer un PDF reçu par courriel.
- **Sans réseau, le dépôt est gardé sur le téléphone** (`lib/file-hors-ligne.ts`, IndexedDB : le fichier entier et les
  champs saisis), avec **le jour de la capture**. Le message le dit : « Pas de réseau : la pièce est gardée sur ce
  téléphone et partira dès le retour du réseau. » Un envoi qui échoue faute de joindre le serveur est gardé de même.
- **La file se rejoue seule** au retour du réseau et à l'ouverture de l'espace, ou d'un geste (« Envoyer maintenant »),
  dépôt après dépôt. Un échec réseau arrête le rejeu ; un **refus du cabinet** (fichier illisible, trop lourd) reste
  affiché avec sa phrase, avec « Réessayer » et « Retirer » : un dépôt ne disparaît jamais en silence.
- **Le jour de la capture devient la date de dépôt** : la photo prise lundi sans réseau et partie mercredi a été déposée
  lundi. Le backend borne l'antériorité et refuse l'avenir ; l'heure de réception reste celle du serveur.
- Un dépôt rejoué dit « Ce document était déjà arrivé au cabinet : rien n'a été envoyé une seconde fois. »

⚠️ **Ce que la file ne fait pas** : elle ne rouvre pas l'espace sans réseau. Il faut qu'il ait été ouvert, et qu'il reste
ouvert ou revienne avec le réseau. Un service worker qui le mettrait en cache placerait des données de dossier dans le
cache du téléphone : ce choix n'est pas pris. Un navigateur qui refuse IndexedDB (navigation privée) rend une file vide,
et le dépôt direct reste possible.

### L'essai réel, dans un vrai navigateur

Chromium sans affichage, écran de téléphone (400 × 860), session d'adhérent de SARL BATIMENT PLUS :

| Essai | Résultat |
| --- | --- |
| L'espace adhérent | champ « prendre une photo » présent |
| Coupure du réseau, envoi d'une facture | « Pas de réseau : la pièce est gardée sur ce téléphone… » ; « 1 pièce gardée sur ce téléphone », « En attente de réseau » |
| Retour du réseau | file vidée d'elle-même ; la pièce est au backend, datée du jour de la capture |
| Même fichier remis en file, puis réseau rétabli | file vidée ; **toujours une seule pièce** au dossier |

### État à la fin du pas 96

La suite complète a tourné : 3 248 cas verts, un seul rouge, le test qui affirmait l'ancien 201 du rejeu. Il a été mis à
jour et repasse. **3 249 tests** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 99 %** (156 gestes sur 157) ; priorités 1 à 4 à 100 %. Contrat des écrans : 157 appels
vérifiés, 0 écart. Couverture des routes : 155 sur 161 (96 %).

**Reste un geste** : construire une règle de conformité sans syntaxe. Les règles sont des fichiers relus en revue, et une
règle mal écrite rejette des TVA à tort chez tous les adhérents d'un cabinet.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une file hors ligne ne vaut que si rejouer ne casse rien ; il fallait d'abord que le dépôt le promette pour de vrai.*

## Pas 97 — Construire une règle de conformité sans syntaxe

### Pourquoi, et le cadre retenu

C'était le dernier geste de la grille. Une règle du référentiel porte un prédicat JSONLogic dont la convention est
contre-intuitive (**VRAI = conforme, FAUX = constat**) ; une personne pense « constat *si* … ». Écrire le prédicat à la
main, c'est inverser la phrase sans se tromper, choisir entre `and` et `or` après l'inversion, citer le bon fait, comparer
à un paramètre de la bonne unité. Chacune de ces fautes produit une règle qui charge sans erreur et **accuse toutes les
factures**, ou n'en accuse aucune.

La question posée à la fin du pas 96 n'a pas reçu de réponse contraire ; le constructeur suit donc le cadre que le
propriétaire a choisi au pas 95 pour les paramètres (effet immédiat, pour le seul cabinet, validation par une autre
personne), avec **une exigence en plus : la mise à l'épreuve sur les factures avant toute proposition**.

### Ce qui a été construit

- **Le constructeur** (`conformite/domaine/constructeur.py`) prend des **conditions d'anomalie** en clair (fait,
  opérateur, et une valeur, un paramètre du référentiel ou un autre fait), reliées par « toutes » ou « au moins une ».
  Chaque condition est confrontée au schéma des faits (le fait existe, l'opérateur a un sens pour son type, la valeur
  appartient à l'énumération) et au référentiel (le paramètre existe, son unité convient). Il pose **lui-même** la
  négation, une fois, autour de l'anomalie entière. Un motif (expression régulière) ne s'écrit jamais : il se prend au
  référentiel, où il a été validé. Il produit aussi la **phrase** que relit le valideur, à partir des mêmes conditions.
- **Ce qu'il ne sait pas exprimer est dit** : les lignes de détail (« une ligne » ou « toutes les lignes » ?) restent
  des règles écrites en fichier et relues en revue.
- **L'essai** joue la règle seule sur les factures connues, et rend la phrase, le prédicat produit, le nombre de
  factures éprouvées et celles sur lesquelles elle réagit. Une règle qui réagirait sur **toutes** est refusée à la
  proposition : condition inversée ou seuil mal choisi.
- **La proposition** rejoue l'essai côté serveur et le conserve ; le valideur tranche sur ce résultat. Aucun effet avant
  validation ; quatre yeux ; une date d'effet passée refusée. Validée, la règle entre au moteur **du cabinet** (codes
  `CAB-…`), signée par le valideur, et contrôle les factures à compter de sa date d'effet. Le circuit est l'entrée
  `regles` de `validation/circuit.yaml` (propose : `MODIFIER_REGLE` ; valide : un autre fiscaliste ou le réviseur).
- Routes : `GET /conformite/constructeur/catalogue`, `POST /conformite/constructeur/essai`,
  `POST|GET /conformite/regles/propositions`, `POST /conformite/regles/propositions/{identifiant}/tranchage`. Journal et
  notifications (`conformite.regle_proposee`, `regle_validee`). Table `proposition_de_regle` et sa migration.

### Ce que l'essai a trouvé, dans le constructeur lui-même

- **L'essai ne voyait rien.** Une règle du cabinet prend effet aujourd'hui ; les factures connues sont antérieures. Jouée
  telle quelle, elle n'était en vigueur sur aucune, et « total TTC supérieur à 0 » ne réagissait « sur rien » : la garde
  contre une règle qui accuse tout était aveugle. L'essai juge désormais la condition comme si la règle avait toujours été
  en vigueur (les paramètres restent résolus à la date de chaque facture).
- **La portée manquait.** La même règle « espèces au-delà du seuil » construite à l'écran réagissait sur 7 factures,
  celle du fichier (FAC-ACH-007) sur 3. La différence : les adhérents au régime synthétique, qui ne récupèrent jamais la
  TVA, et à qui annoncer « TVA non déductible » énonce un préjudice inexistant. Le constructeur porte désormais la
  portée par régime de l'adhérent. **La règle construite réagit maintenant exactement sur les mêmes factures que la règle
  du fichier**, et un test le garde.
- **Un refus de validation arrivait brut** (« Value error, … ») : le test existant des messages lisibles l'a vu côté
  backend ; l'écran ôte désormais aussi ce préfixe des refus de validation de requête.
- **Un composant client importait une constante d'un module serveur** : la construction de production a échoué ; les
  libellés des opérateurs ont leur module, sans dépendance serveur.

### Le défaut d'affichage que seul le navigateur a montré

L'essai du constructeur dans un vrai navigateur ne pouvait pas cliquer « Construire une règle » : **la page du
référentiel écrasait chaque panneau à son en-tête**. La coquille verrouille la hauteur de l'écran, et `.page-travail`
laissait ses panneaux se comprimer pour tenir. Le panneau « Décisions du cabinet » du pas 95 était ainsi **réduit à son
titre depuis sa création** : les essais de ce pas passaient par les actions, pas par l'écran.

La mesure sur neuf pages de travail, avant et après une seule correction de la classe (la page défile, ses panneaux ne
se compriment plus, un panneau qui doit remplir la hauteur le déclare lui-même) :

| Page | Avant | Après |
| --- | --- | --- |
| Référentiel | 3 panneaux sur 6 coupés, dont les décisions et le constructeur | aucun |
| Comptes | « Inviter un collaborateur » invisible, 5 comptes sur 12, le compte suspendu et « Rétablir » hors de vue | tout visible |
| Exploitation, fiche 360°, déclarations | bas de page coupé | tout visible |
| Souscriptions, portefeuille, social, veille | identiques (pixel près) | identiques |

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Fiscaliste, « Construire une règle » | « Proposer » absent tant qu'aucun essai n'a été fait |
| Mode de règlement égal à ESPECES, et total TTC supérieur ou égal au paramètre SEUIL_ESPECES_DEDUCTIBILITE_TVA, adhérents au réel | « Constat si mode de règlement est égal à ESPECES et total toutes taxes comprises est supérieur ou égal à la valeur du paramètre … » ; « Réagit sur 3 des 22 factures éprouvées : F-2026-0412, F-2026-0424, F-2026-0434 » |
| Modifier l'intitulé après l'essai | « La règle a changé depuis cet essai » ; « Proposer » masqué |
| Nouvel essai, motif, proposer | « Règle CAB-… proposée : sans effet tant qu'une autre personne ne l'a pas validée » |
| Réviseur valide | appliquée ; la règle figure au catalogue |
| Facture de juillet / la même datée du 20/09 | pas de constat de la nouvelle règle (antérieure à sa prise d'effet) / constat émis |

`tests/test_constructeur_de_regles.py`, 26 cas dont un sur PostgreSQL. **Dix-neuf mutations tuées**, dont une qui
survivait (l'essai comptait les factures hors portée) et a demandé une assertion.

### État à la fin du pas 97

**3 277 tests passent** sur PostgreSQL réel. **Avancement des écrans : 100 %** (161 gestes sur 161). Contrat des écrans : 162 appels vérifiés, 0 écart. Couverture des
routes : 160 sur 166 (96 %). Frontend : typage, lint, construction de production.

⚠️ **Cent pour cent de la grille n'est pas un produit fini.** La grille déclare les gestes proposés au pas 80. Restent hors
de sa mesure : les écrans des parcours par profil absents de l'inventaire (journal des dérogations, statistiques de
règles, vue risque), les questions ouvertes du cabinet (Q24 preuve d'identité en ligne, Q25 groupe de risque CNPS, Q26
politique d'écart), l'abrogation d'une règle ou d'une version du cabinet (aujourd'hui, une décision validée ne se retire
pas depuis l'écran), et la validation des paramètres légaux par un professionnel nommé.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une règle qu'on ne peut pas éprouver avant de la valider est une accusation qu'on signe sans avoir lu le dossier.*

## Pas 98 — Retirer une décision validée, vers l'avant seulement

### Pourquoi

Aux pas 95 et 97, un cabinet valide une valeur du référentiel ou une règle de conformité, avec effet immédiat. **Aucune
route ne permettait d'y revenir.** Une valeur validée par erreur (un taux mal recopié, une règle trop large) était
définitive : la seule issue était d'éditer la base, sans trace au journal. C'était le trou le plus concret laissé par ces
deux pas, et il ne demandait aucune décision du cabinet.

### Le choix : un retrait daté, qui ne remonte pas le temps

Une décision validée a servi à des calculs rendus : une TVA rejetée, une échéance annoncée, un constat émis. La retirer
rétroactivement changerait ces résultats sans que personne ne les relise, la faute exacte que la date d'effet d'une
proposition interdit déjà. Le retrait prend donc effet **aujourd'hui au plus tôt**.

- **Une nouvelle valeur retirée** s'arrête à la date du retrait, et la version du référentiel commun qu'elle avait
  interrompue **reprend** jusqu'à sa propre échéance. Retirée à sa propre date d'effet, elle ne s'applique jamais. Une
  version postérieure du fichier commun reste intacte.
- **Une validation retirée** : la version redevient « à valider » pour le cabinet.
- **Une règle retirée** cesse de contrôler à compter de la date ; une facture contrôlée avant garde son constat.
- **Rien n'est effacé** : la décision reste APPLIQUEE, avec `fin_d_effet`, l'auteur, la date et le motif du retrait.
- **Qui retire** : qui peut valider selon le circuit du cabinet (revenir sur une valeur engage autant que l'arrêter). Un
  seul geste, sans second regard : le retrait rend la valeur commune, déjà relue, et c'est le sens où l'erreur coûte le
  moins.

Routes : `POST /transverse/referentiel/decisions/{identifiant}/retrait` et
`POST /conformite/regles/propositions/{identifiant}/retrait` (`a_compter_du`, `motif`). Refus : 403 hors du circuit, 404
inconnue, 409 si rien n'est à retirer, si la date est passée ou antérieure à la date d'effet. Journal
(`referentiel.decision_retiree`, `conformite.regle_retiree`) et notifications à ceux qui calculent avec la valeur ou la
règle.

`tests/test_retrait_des_decisions.py`, 11 cas dont un sur PostgreSQL. **Douze mutations tuées.**

### Ce qui a été fait, à l'écran

Sur l'écran du référentiel, chaque décision appliquée de l'historique et chaque règle en vigueur du cabinet porte
« Retirer », pour qui peut valider : date proposée à aujourd'hui (aucune date antérieure admise), motif, et la phrase
« À compter de cette date, la valeur du référentiel commun reprend. Les calculs déjà rendus ne changent pas. » Une décision
retirée l'affiche : date, auteur et motif.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| TVA 20 % au 01/01/2027, proposée par le fiscaliste, validée par le réviseur | au 01/07/2027 : 20 |
| Comptable, historique des décisions | pas de bouton « Retirer » |
| Réviseur, « Retirer » à compter du 01/06/2027, motif | la note avant envoi ; l'historique affiche « retirée à compter du 01/06/2027 par Aïcha BOUBA : « … » » |
| Valeurs lues après le retrait | 31/05/2027 : 20 ; 01/07/2027 : 19,25 |

### État à la fin du pas 98

**3 288 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (163 gestes sur 163). Contrat des écrans : 164 appels vérifiés, 0 écart. Couverture des
routes : 162 sur 168 (96 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une décision qu'on ne peut pas retirer n'est pas une décision, c'est une gravure ; et un retrait qui réécrirait le passé
serait une seconde erreur.*

## Pas 99 — Le journal des dérogations et la qualité des règles

### Pourquoi

L'entrée « Conformité » du menu était marquée « à venir » depuis la première coquille. La maquette du parcours réviseur
(`Docs/Parcours reviseur CGA.html`) y place deux écrans absents de l'inventaire E00 à E13 : le **journal des
dérogations** (« consultable par la DGI en cas de contrôle ») et la **qualité des règles** (« repérer les règles
bruyantes et alerter le fiscaliste »). Leurs données existent depuis le pas 92 : chaque écart de constat est conservé,
avec son motif et ses auteurs.

### Ce qui a été construit

**Le journal des dérogations** (`GET /conformite/derogations`) :
- tous les écarts du périmètre, du plus récent au plus ancien, avec leurs auteurs **en clair** (un vérificateur ne connaît
  pas les identifiants de comptes), des filtres (règle, auteur, dossier, statut), le nombre de dérogations effectives et
  **l'enjeu levé**, qui ne totalise que les effectives ;
- l'enjeu est désormais **relevé au moment de l'écart** et conservé sur l'écart : le relire sur le rapport d'aujourd'hui
  donnerait un montant que le réviseur n'a jamais vu ;
- **l'export pour contrôle** (`GET /conformite/derogations/export`) : le même journal en CSV, séparé par des
  points-virgules, en UTF-8 avec marque d'ordre des octets, sans laquelle un tableur lit « Ã© » dans les motifs ;
- **`LIRE_AUDIT`** : le réviseur, la direction, et l'inspecteur **sur son seul dossier**. Un comptable contrôle sans
  auditer, et ne le lit pas.

**La qualité des règles** (`GET /conformite/regles/qualite`) :
- pour chaque règle en vigueur, sur les pièces du périmètre émises dans la période (90 jours par défaut) : constats
  **émis** (lus sur le rapport brut), constats **écartés** (lus sur le rapport arbitré), enjeu retenu, taux d'écartement ;
- une **lecture** selon des seuils lus au référentiel (`ecarts/politique.yaml`, entrée `revue_des_regles`) : à recalibrer
  au-delà de 34 %, trop bruyante au-delà de 60 %, jamais jugée sur moins de 5 constats. Des seuils inversés sont refusés
  au chargement ;
- « peu contestée » et non « saine » : un taux faible dit que personne n'a écarté les constats, pas qu'ils étaient justes.

**Le signalement au fiscaliste** (`POST /conformite/regles/{code}/signalement`) : un fait au journal d'audit, que les
notifications (pas 94) lisent pour prévenir le fiscaliste, qui corrige la règle au constructeur (pas 97). La boucle de
qualité de la maquette est fermée : le réviseur mesure, le fiscaliste corrige, la file d'anomalies s'allège.

`tests/test_derogations_et_qualite.py`, 17 cas dont un sur PostgreSQL. **Treize mutations tuées**, dont une qui survivait
(le journal ne restreignait pas au périmètre) et a demandé un cas : l'inspecteur en mission sur AGRO-NKOLO ne lit que les
dérogations de ce dossier.

### Ce qui a été fait, à l'écran

- **Le menu** : « Conformité » est construit, avec deux sous-entrées, et s'ouvre aussi par `LIRE_AUDIT` (la direction lit
  le journal sans contrôler de pièce).
- **`/conformite`** : en-tête (nombre, effectives, enjeu levé), filtres, « Exporter pour contrôle » (le fichier suit les
  filtres affichés), tableau (date, règle, dossier nommé, pièce liée, motif et auteurs, enjeu, statut), et la phrase de la
  maquette : une dérogation ne se modifie ni ne se supprime, elle se lève depuis la pièce.
- **`/conformite/qualite`** : période, seuils du référentiel rappelés, tableau par règle (les plus contestées d'abord), et
  « Signaler au fiscaliste » sur les règles à recalibrer ou trop bruyantes.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Réviseur écarte FAC-DOC-011 sur trois pièces, ouvre « Conformité » | « 3 dérogations dont 3 effectives · 0 FCFA d'enjeu levé » (des avertissements, sans enjeu chiffré) |
| Exporter pour contrôle | `journal-des-derogations.csv`, motifs accentués lisibles |
| Filtre « en attente du second regard » | « Aucune dérogation » |
| Qualité des règles | « Du 17/06/2026 au 15/09/2026 · 29 pièces contrôlées · 12 constats · taux d'écartement global 25 % » ; FAC-DOC-011 : 3 constats, 3 écartés (100 %), « Trop peu de constats » |
| Comptable | journal refusé en nommant `LIRE_AUDIT` ; qualité des règles lisible |

⚠️ Le jeu de démonstration ne compte que 29 pièces : aucune règle n'y atteint cinq constats, et le bouton de signalement
ne s'y montre donc pas. C'est le seuil qui l'exige, et c'est voulu : trois écarts sur trois constats ne disent rien d'une
règle.

### État à la fin du pas 99

**3 305 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (167 gestes sur 167, dont les 4 de la revue de conformité). Contrat des écrans : 168
appels vérifiés, 0 écart. Couverture des routes : 166 sur 172 (96 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une règle ne se juge pas à ce qu'elle accuse, mais à ce que le cabinet, pièce en main, refuse d'en retenir.*

## Pas 100 — La vue risque d'un dossier et les décisions de la direction

### Pourquoi

La grille était à 100 % depuis le pas 97, mais le pas 99 notait ce qui restait hors de la grille : **la vue risque du
parcours direction** (`Docs/Pilotage direction CGA.html`, vue B). Le tableau de bord du pilotage classait les dossiers
et citait les éléments de chaque composante ; la maquette va plus loin : un dossier s'ouvre, le score s'explique
composante par composante jusqu'à la pièce, et l'écran **se termine par des décisions** (« Renforcer le suivi »,
« Exiger une régularisation datée », « Convoquer un rendez-vous de cadrage », « Envisager la fin d'adhésion »), avec
une note : « décisions datées, signées, visibles dans la chronologie de la fiche adhérent ».

Une direction qui décide oralement en comité ne laisse aucune trace. Six mois plus tard, personne ne sait si la fin
d'adhésion avait été envisagée, par qui, ni sur quel score.

### Ce qui a été construit

**Le domaine** (`pilotage/domaine/decisions.py`) :
- `MesureDeDirection` et `CatalogueDesMesures` : **ce que la direction peut décider**, lu au référentiel
  (`Docs/referentiel/pilotage/mesures.yaml`, jamais dans le code). Chaque mesure dit pour quels niveaux de risque elle est
  permise et si elle exige une échéance. Sans fichier, aucune mesure ; un fichier mal écrit (clé inconnue, code en double)
  fait échouer le chargement ;
- `DecisionDeDirection` : datée, signée par la personne connectée, motivée (30 caractères au moins, à la prise **et** à
  la clôture), avec le libellé du jour et **l'instantané du score** qui l'a fondée ;
- ⚠️ l'instantané ne contredit pas la règle « le score se calcule, il ne se stocke pas » : il n'est jamais affiché comme
  le risque du dossier. Il répond à « sur quoi la direction s'est-elle fondée ? ». Une fin d'adhésion envisagée à
  88 points, relue quand le dossier est redescendu à 20, doit dire 88.

**Les cas d'usage** (`pilotage/application/decisions.py`) : `prendre_une_mesure` refuse une mesure hors de ses niveaux
(« Envisager la fin d'adhésion » sur un dossier sous contrôle n'est pas du pilotage), sans échéance quand elle en exige
une, avec une échéance du jour ou passée, ou **en double d'une même mesure en cours** (deux régularisations ouvertes, c'est
deux échéances et un collaborateur qui ne sait plus laquelle tenir). `clore_une_decision` ne clôt qu'une fois. Clore puis
reprendre la même mesure fait une nouvelle ligne : l'histoire garde les deux.

**La persistance** : première table du pilotage, `decision_de_direction` (clé `(locataire, identifiant)`, sécurité par
ligne), migration `d8e3a6b27c14`. Le pilotage n'écrivait rien jusqu'ici ; il n'écrit que ce que la direction décide.

**Les routes** (`/pilotage/dossiers/{niu}/…`) :
- `GET …/risque` (`LIRE_PILOTAGE`) : le score calculé **exactement comme au tableau de bord** (même relevé, même
  pondération : deux calculs finiraient par diverger), les quatre composantes y compris celles à zéro, les seuils, les
  mesures proposées à ce niveau, et les décisions de la plus récente à la plus ancienne ;
- `POST …/decisions` et `POST …/decisions/{identifiant}/cloture` : nouvelle permission **`DECIDER_SUR_DOSSIER`**,
  direction seule, **avec motif exigé**. Distincte de `LIRE_PILOTAGE` : une lecture n'engage personne, une décision engage
  le cabinet envers l'adhérent. ⚠️ Le score est **recalculé à l'instant** de la décision, jamais pris de l'écran : une vue
  restée ouverte depuis la veille montrerait un niveau qui n'est peut-être plus le bon ;
- `GET …/decisions` (`LIRE_DOSSIER`, **cabinet seulement**) : pour la fiche adhérent. Le collaborateur qui porte le dossier
  doit savoir qu'une régularisation a été exigée, puisque c'est lui qui la suivra. L'adhérent et l'inspecteur reçoivent
  404 : l'existence même d'une décision de direction est une information.

**Le journal et les notifications** : `pilotage.decision_prise` et `pilotage.decision_close` au journal d'audit, le motif
dans l'entrée mais **hors des données** que lisent les notifications. Deux abonnements dans
`notifications/abonnements.yaml` préviennent ceux qui travaillent sur le dossier (saisie ou relance), jamais l'adhérent.

`tests/test_decisions_de_direction.py`, 29 cas dont un sur PostgreSQL. **26 mutations, toutes tuées.**

### Ce qui a été fait, à l'écran

- **`/pilotage`** : le nom de chaque dossier ouvre sa vue risque.
- **`/pilotage/[niu]`** : le score, son niveau et les seuils qui le classent ; « Ce qui compose le risque », chaque
  composante avec son action attendue et ses éléments **liés** (la pièce s'ouvre, un retard mène à l'échéancier). Les
  33 retards d'un dossier ne se lisent pas un à un : ils sont regroupés par obligation (« TVA : 01/2026, 02/2026… »), sans
  rien perdre de la traçabilité. « Décider » liste les mesures du catalogue, formulaire fermé par défaut (une décision ne
  se prend pas d'un clic distrait), échéance demandée quand la mesure l'exige. « Décisions de la direction » : statut
  (en cours, échue, close), motif, auteur, score du jour, clôture motivée.
- **`/portefeuille/[niu]`** : un panneau « Décisions de la direction » quand il y en a, avec un lien vers la vue risque
  pour qui peut la lire.

### Trois défauts trouvés en chemin

1. **Des tests à retardement.** Lancée le 16/09/2026, la suite a échoué sur 8 tests des pas 97 et 98 qui posaient des
   dates d'effet en dur (« 2026-09-15 ») : le système refuse, à raison, une règle qui prend effet dans le passé, et ces
   tests devenaient faux dès le lendemain de leur écriture. Corrigé en figeant l'horloge des deux modules au jour de leur
   écriture, par la couture `horloge_figee` prévue pour cela. Le même essai a révélé que la base PostgreSQL de test n'était
   plus démarrée (297 tests ignorés sans bruit) : relancée par `outils/postgres-local.sh start`.
2. **Un motif perdu sur un refus.** Dans le navigateur, après un refus (mesure déjà en cours), le formulaire se vidait :
   React réinitialise un formulaire soumis par action, et la direction perdait le motif qu'elle venait d'écrire. Les champs
   sont désormais contrôlés ; motif et échéance survivent au refus.
3. **Des en-têtes de panneau qui débordaient sur téléphone, sur tous les écrans.** Le composant commun `Panneau` avait une
   hauteur fixe de 40 px et un interligne de 1 : un titre long suivi de son aide passait à la ligne et chevauchait la
   bordure. Corrigé à la source (hauteur minimale, retour à la ligne permis) ; sur ordinateur, les en-têtes gardent leurs
   40 px, mesurés.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Direction, `/pilotage`, clic sur CABINET NGUEMA CONSEIL | vue risque : 65 pts, « À traiter », seuils 25 et 60 ; 2 composantes actives, 2 à zéro ; lien vers PJ-2026-0026 et vers l'échéancier |
| « Exiger une régularisation datée », motif et échéance 15/10/2026 | « décidée et inscrite au journal » ; la décision apparaît « en cours · échéance 15/10/2026 » |
| Même mesure une seconde fois | refus « déjà en cours … La clore d'abord » ; motif et échéance saisis conservés |
| Clore avec motif | « close le 16/09/2026 par Bernadette MBALLA » |
| Comptable du dossier | panneau « Décisions de la direction » sur la fiche, deux notifications (prise, clôture) ; vue risque « Accès réservé » au profil Direction |
| Adhérent de SARL BATIMENT PLUS | aucun panneau de décisions sur sa fiche |
| Téléphone (390 px) | aucun débordement horizontal, en-têtes de panneau lisibles |

### État à la fin du pas 100

**3 335 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (171 gestes sur 171). Contrat des écrans : 172 appels vérifiés, 0 écart (1 appel
illisible par construction, la recherche générique). Couverture des routes : 170 sur 176 (96 %).
Nouvelle question ouverte **Q27** (le catalogue des mesures, qui prévenir, le seuil de comité, les rubriques absentes du
score).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un score dit où regarder ; seule une décision signée dit ce que le cabinet a choisi d'en faire.*

## Pas 101 — Le rapprochement bancaire

### Pourquoi

La grille des écrans était à 100 %, mais les maquettes décrivent davantage qu'elle. Relues vue par vue, elles montrent un
geste central du comptable qu'aucun écran ni aucune route ne portait : le **rapprochement bancaire** (`Docs/Parcours
comptable CGA.html`, vue B, « UC06 : confronter le relevé aux écritures, lettrer, expliquer les écarts »). Le code
l'attendait pourtant depuis longtemps : le compte 521 est marqué « rapprochable », et un journal de trésorerie doit
déclarer son compte « sans quoi le rapprochement est impossible ».

C'est le contrôle le plus efficace qui existe en comptabilité : la banque et le cabinet tiennent le même compte, chacun de
son côté ; s'ils ne disent pas la même chose, l'un des deux se trompe, ou une opération manque d'un côté.

### Ce qui a été construit

**Le domaine** (`comptabilite/domaine/rapprochement.py`), écrit pour qui n'en a jamais fait :
- **Le signe, une fois pour toutes.** Le relevé est tenu du point de vue de la banque (« crédit » pour un versement reçu) ;
  tout le reste, du point de vue de l'entreprise, comme la comptabilité (un encaissement est au débit du 521). Le profil de
  lecture traduit une seule fois, à l'import.
- **Le rapprochement ne marque pas les écritures.** Une écriture validée ne se réécrit pas ; le rapprochement est un objet à
  part qui désigne les lignes d'écriture par leur clé et leur rang.
- **Les profils de relevé** : un fichier par format au référentiel (`rapprochement/releves/`), colonne signée ou colonnes
  débit et crédit. Le moteur ne connaît aucune banque. Une ligne illisible fait échouer tout l'import en la nommant (« ligne
  12 : date « 32/07/2026 » illisible »), plutôt que d'importer un relevé incomplet.
- **Le relevé qui ne tombe pas juste est refusé** : solde initial plus opérations doit donner le solde final recopié. Sans ce
  contrôle, une ligne manquante du fichier serait cherchée dans la comptabilité.
- **Les propositions motivées** : montant exact et sens identique sont une condition, jamais un argument ; viennent ensuite
  la référence retrouvée dans le libellé bancaire (« FACT 0412 » pour « F-2026-0412 », sans ponctuation, jamais sur moins de
  trois chiffres), la proximité des dates, l'écriture encore en brouillon, l'écriture déjà prise par une autre ligne. Les
  fenêtres de dates sont au référentiel (`rapprochement/reglages.yaml`).
- **L'automatique prudent** : il n'apparie qu'une correspondance forte **unique**, jamais deux lignes sur la même écriture.
  Deux virements de 250 000 le même jour restent au comptable.
- **Aucun écart de montant absorbé** : 2 350 000 contre 2 349 000 n'est pas un rapprochement, c'est une question.
- **Les justifications** d'une ligne sans écriture : pièce demandée à l'adhérent (la règle du contrôle en amont : pas
  d'écriture d'attente sans justificatif), écriture à passer sur la période suivante, erreur de la banque.
- **L'état de rapprochement** : solde du relevé, neutralisation des opérations du relevé sans écriture, ajout des écritures
  absentes du relevé, solde rectifié, solde comptable, écart inexpliqué. **L'arrêt** est refusé tant qu'une ligne n'est pas
  expliquée, qu'un écart demeure, qu'une écriture rapprochée est en brouillon, ou qu'elle a été corrigée depuis (son montant
  ne correspond plus). Arrêté, l'état est figé et plus aucun geste n'est possible.
- **Les périodes** : deux relevés du même journal ne se chevauchent pas ; un relevé importé par erreur s'abandonne, avec
  motif, et libère la période. La caisse ne se rapproche pas d'un relevé : elle se contrôle par un comptage.

**Persistance** : table `rapprochement_bancaire` (clé locataire, dossier, identifiant ; sécurité par ligne), migration
`e9f4b7c38d25`. **Routes** : 9, dans un module à part monté sous `/comptabilite`. Lire : `LIRE_COMPTABILITE` ; préparer
(importer, rapprocher, dissocier, justifier, abandonner) : `SAISIR_ECRITURE` ; arrêter : `VALIDER_ECRITURE`. Le journal
d'audit porte l'import, l'arrêt, l'abandon et chaque pièce demandée ; un abonnement fait arriver cette dernière à qui relance
l'adhérent. Le rapprochement retient le nom des personnes, le journal leur compte.

`tests/test_rapprochement_bancaire.py`, 44 cas dont un sur PostgreSQL. **39 mutations, toutes tuées** ; trois survivaient
d'abord et ont demandé des cas : l'état arrêté vérifié sur un exemple qui ne le distinguait pas, un mouvement postérieur à
la fin du relevé, deux correspondances fortes ex æquo.

### Ce qui a été fait, à l'écran

- **Menu** : « Rapprochement bancaire » sous Comptabilité.
- **`/comptabilite/rapprochement`** : les relevés du dossier (période, compte, état, lignes à traiter, écart), et l'import :
  compte de banque (banque ou Mobile Money), période, soldes recopiés du relevé, format, fichier.
- **`/comptabilite/rapprochement/[identifiant]`** : en tête, solde du relevé, solde comptable, écart inexpliqué, lignes à
  traiter (dont combien automatiquement) ; les lignes non traitées d'abord ; la ligne choisie (dans l'adresse, pour pouvoir la
  partager) avec ses écritures proposées, chacune avec sa force et ses motifs, et « Rapprocher » ; sans proposition, le
  rappel de demander la pièce, « Créer l'écriture » et la justification ; les écritures absentes du relevé ; l'état de
  rapprochement écrit comme une addition ; « Valider le rapprochement » et « Abandonner ce relevé ».

⚠️ **Hors du pas, et écrit** : pas de lecture de relevé PDF (la reconnaissance de texte ferait chercher ses erreurs dans la
comptabilité) ; pas de raccourcis clavier de la maquette ; « Créer l'écriture » ouvre la saisie sur le bon journal sans la
préremplir.

### Six défauts trouvés en chemin

1. **Le garde-fou d'architecture** a refusé `model_copy` sur le rapprochement, qui porte un invariant (le relevé qui tombe
   juste) : les gestes passent par `transiter`, qui revalide.
2. **Un brouillon corrigé après avoir été rapproché** aurait laissé arrêter un état juste en apparence : l'arrêt compare
   désormais les montants.
3. **Des écritures en mémoire qui fuyaient d'un test à l'autre**, et se faisaient rapprocher automatiquement dans le suivant.
4. **Un état de rapprochement trompeur** à l'écran : « − opérations du relevé sans écriture : 18 500 » se lisait comme une
   soustraction alors que le calcul ajoutait. Chaque ligne affiche désormais le montant qui s'ajoute.
5. **Des libellés invisibles sur téléphone** : les colonnes fixes ne leur laissaient aucune largeur. Les lignes du relevé sont
   une liste qui passe à la ligne.
6. **Cinq gestes invisibles à la mesure** : une aide commune recevait le chemin en paramètre, et l'outil du contrat comme la
   mesure d'avancement ne lisent que les chemins littéraux (97 % au lieu de 100 %). Chaque geste écrit son chemin.

### L'essai réel, dans un vrai navigateur

Relevé de juillet de SARL BATIMENT PLUS, quatre lignes, et cinq écritures de banque validées, dont un règlement en double
(F-2026-0409) et deux versements d'espèces de même montant.

| Essai | Résultat |
| --- | --- |
| Import avec un solde final faux d'un franc | refus « le relevé ne tombe pas juste », soldes saisis conservés |
| Import juste | 2 lignes rapprochées automatiquement (même jour ; référence F-2026-0412 dans « FACT 0412 »), 2 à traiter, écart 0 |
| Versement d'espèces | 2 propositions « Possible » ; rapproché à la main du versement du 27 |
| Frais de tenue de compte | aucune proposition, « Pièce demandée à l'adhérent » proposée d'abord ; motif trop court bloqué par le navigateur |
| État de rapprochement | 5 211 600 + 18 500 − 1 169 900 = 4 060 200 = solde comptable ; écart 0 |
| Valider | « arrêté le 16/09/2026 par Léonard FOTSO », plus aucun geste |
| Chargée de clientèle | notification « Pièce à demander : FRAIS TENUE DE COMPTE » ; lit les relevés, n'importe pas |
| Téléphone (390 px) | aucun débordement, libellés lisibles |

### État à la fin du pas 101

**3 382 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (180 gestes sur 180, dont les 9 du rapprochement). Contrat des écrans : 181 appels
vérifiés, 0 écart (1 appel illisible par construction). Couverture des routes : 179 sur 185 (96 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Deux tiers tiennent le même compte ; tout ce qui les sépare doit porter un nom.*

## Pas 102 — La revue d'un mois transmis

### Pourquoi

Confrontées vue par vue, les maquettes décrivent un circuit qu'aucun code ne portait : les **passages de relais** entre
comptable et réviseur. Le plan de travail du comptable (`Parcours comptable`, vue A) affiche « 2 dossiers attendent le
réviseur · 1 dossier vous revient avec des remarques » ; la vue D du parcours réviseur montre la **revue d'un dossier
transmis** : un échantillonnage assisté, des remarques rattachées à des objets précis, « renvoyer » ou « valider ». Sans ce
circuit, le second regard sur la tenue comptable n'existait que par oral.

### Ce qui a été construit

**Le domaine** (`comptabilite/domaine/revue.py`) :
- **Le circuit** : TRANSMISE (chez le réviseur), RENVOYEE (au comptable, avec des remarques), VALIDEE. Chaque geste est refusé
  hors de son état, avec un message qui le dit.
- **L'échantillon** des écritures atypiques, **figé à la transmission** : montant rond et élevé, parmi les plus gros montants
  du mois, compte rarement mouvementé sur l'exercice, contre-passation. Les plus signalées d'abord, dans la limite d'un plafond.
  Les seuils sont au référentiel (`revue/echantillon.yaml`). Recalculé à la retransmission, parce que les écritures ont pu
  changer.
- **La remarque rattachée à un objet** : une écriture, une pièce ou un compte **de la période revue**. Une remarque sur un
  objet qui n'existe pas, ou d'un autre mois, est refusée : elle ne se retrouverait pas.
- **Le cycle d'une remarque** : ouverte, répondue par le comptable (corrigé ou expliqué), close par le réviseur.
- **Les règles de passage** : on ne renvoie pas sans remarque ouverte ; on ne retransmet pas sans avoir répondu à chacune ; on
  ne valide pas tant qu'une remarque n'est pas close ; et **celui qui a transmis ne valide jamais sa propre revue**, même
  réviseur. Une revue validée ne peut, par invariant, garder aucune remarque non close.

**La transmission** refuse un mois vide, un mois qui garde des brouillons (un brouillon peut encore changer), et un mois qui
chevauche une revue existante.

**Les points de contrôle**, automatiques et informatifs : aucun brouillon apparu depuis la transmission, numérotation continue,
balance du mois équilibrée, et **comptes de banque rapprochés à la fin du mois**, qui s'appuie sur le rapprochement arrêté du
pas 101.

**Persistance** : table `revue_de_dossier`, migration `f1a5c8d49e36`. **Permission** nouvelle : `REVISER_DOSSIER`, au seul
réviseur. **Routes** : 9, dans un module à part sous `/comptabilite`. Lire et la file : `LIRE_COMPTABILITE`, restreinte au
périmètre ; transmettre, répondre, retransmettre : `SAISIR_ECRITURE` ; remarquer, clore, renvoyer, valider : `REVISER_DOSSIER`.
**Notifications** : trois abonnements, sans code de plus ; la transmission arrive aux réviseurs du dossier, le renvoi et la
validation au comptable qui a transmis.

`tests/test_revue_de_dossier.py`, 18 cas dont un sur PostgreSQL. **31 mutations, toutes tuées** ; trois survivaient d'abord et
ont demandé des cas : la borne du compte rare, l'échantillon recalculé à la retransmission, le filtre de la file par statut.

### Ce qui a été fait, à l'écran

- **Menu** : « Revue des dossiers » sous Comptabilité.
- **`/comptabilite/revues`** : trois files, « À réviser » (ou « Chez le réviseur » pour le comptable), « Revenus avec des
  remarques », « Validés », chaque mois avec son dossier, qui l'a transmis, l'échantillon et l'état des remarques ; et
  « Transmettre un mois ».
- **`/comptabilite/revues/[identifiant]`** : le dernier mot laissé, les points de contrôle, l'échantillon avec ses raisons et
  « Remarquer » à côté de chaque écriture, les remarques (réponse sous chacune pour le comptable, « Clore » pour le réviseur),
  l'histoire des passages et le geste permis à cet état : renvoyer, valider, retransmettre. L'objet d'une remarque se choisit
  dans les listes du mois, jamais saisi.

⚠️ **Hors du pas, et écrit** : « Corriger moi-même » de la maquette est la contre-passation existante ; « Tout ouvrir en
file » du plan de travail n'est pas construit.

### Quatre défauts trouvés en chemin

1. **Trois trous de test** révélés par les mutations (voir plus haut).
2. **Un historique trompeur** : « Chez le réviseur : Léonard FOTSO » laissait croire que le comptable était le réviseur.
   L'historique nomme désormais l'acte : « Transmis par Léonard FOTSO ».
3. **Un bandeau cassé** : le nom de l'auteur du message passait seul sur sa ligne et la phrase commençait par une virgule.
4. **Le NIU en titre** au lieu du nom du dossier.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Comptable, mars 2026 | « aucune écriture du 01/03/2026 au 31/03/2026 : il n'y a rien à réviser », mois conservé |
| Comptable, juillet, avec un mot | redirigé vers la revue « Chez le réviseur » ; aucun geste de réviseur affiché |
| Réviseur, depuis la notification | la revue ; 4 points conformes ; 3 écritures atypiques avec leurs raisons |
| Remarque sur 2026/AC/000001, renvoi | « Renvoyée au comptable » |
| Comptable | le mois dans « Revenus avec des remarques » ; retransmettre masqué tant qu'une remarque est sans réponse ; répond, retransmet |
| Réviseur | clôt la remarque, valide ; histoire : transmis, renvoyé, transmis, validé |
| Notifications du comptable | « Mois renvoyé avec 1 remarque(s) », « Mois validé » |
| Téléphone (390 px) | aucun débordement |

### État à la fin du pas 102

**3 403 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production. **Avancement des écrans :
100 %** (189 gestes sur 189). Contrat des écrans : 190 appels vérifiés, 0 écart (1 illisible par construction). Couverture des
routes : 188 sur 194 (96 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un mois tenu par une personne et relu par une autre ; entre les deux, chaque remarque porte le nom de ce qu'elle désigne.*

## Pas 103 — Écarter des constats en masse

### Pourquoi

Vue B de la maquette du parcours réviseur, confrontée au code : depuis le pas 92, un constat s'écarte **pièce par pièce**.
Quatre fournisseurs dont le NIU a été vérifié hors facture, c'est pourtant **une** décision, prise pour **une** raison, sur
quatre constats ; la prendre quatre fois produit quatre motifs recopiés, et le réviseur cesse de les écrire vraiment. La
maquette exige aussi ce qui manquait : un **motif type** qui accélère, un **motif détaillé** obligatoire et jamais prérempli,
l'**enjeu levé et la portée annoncés** avant de signer, et les **comptables prévenus**.

### Ce qui a été construit

**Au référentiel** (`ecarts/politique.yaml`) : les **motifs types**, chacun avec son code, son libellé et les règles pour
lesquelles il est proposé (vide : toutes). Deux motifs de même code sont refusés au chargement. L'écart garde désormais son
`motif_type`, et le journal d'audit aussi.

**Le geste** (`conformite/application/ecarts_en_masse.py`) :
- **Tout ou rien.** Si un seul constat ne peut pas être écarté (politique, écart déjà ouvert, constat absent de la pièce),
  aucun ne l'est, et le message nomme chaque pièce refusée. Écarter trois constats sur quatre en silence laisserait croire que
  la décision est appliquée. Faute de transaction dans le dépôt en mémoire, chaque écart est proposé contre un **tampon** qui
  lit le dépôt réel ; le tampon n'est versé qu'une fois tous acceptés.
- **La même politique qu'à l'unité** : chaque écart est un écart ordinaire (sévérité, règles non écartables, second regard,
  même levée depuis la pièce). Le motif et le motif type sont vérifiés une fois, avant tout : « motif trop court » plutôt que
  « 4 refus sur 4 ».
- **Les conséquences** rendues après la décision : écarts effectifs et en attente, enjeu levé (effectifs seuls), dossiers,
  pièces redevenues comptabilisables.

**Les routes** :
- `GET /conformite/regles/{code}/constats` (`CONTROLER_CONFORMITE`) : sur la période et le périmètre, chaque constat de la
  règle avec son fournisseur, la **vérification DGI** (actif, radié, indisponible), l'enjeu, et s'il peut être choisi, sinon
  pourquoi ; avec les chiffres de la maquette : constats, enjeu cumulé, adhérents concernés, taux d'écartement.
- `POST /conformite/regles/{code}/ecarts` (`ECARTER_CONSTAT`, motif exigé) : toute pièce hors périmètre fait échouer la
  demande entière en 404, sans dire laquelle existe ailleurs.

**Les comptables prévenus** : l'abonnement d'un écart effectif s'étend à `SAISIR_ECRITURE` sur le dossier, parce qu'un écart
effectif change la proposition d'écriture de la pièce. Cela vaut aussi pour l'écart à l'unité.

`tests/test_ecarts_en_masse.py`, 16 cas dont un sur PostgreSQL. **23 mutations : 22 tuées**, et une équivalente, écrite comme
telle : retirer le contrôle de permission en tête de route ne change rien, puisque chaque pièce repasse par `exiger_dossier`
avec la même permission. Quatre autres survivaient d'abord : une lecture du tampon qui était du code mort (supprimée), une
pièce qui reste bloquée après un écart en attente, le motif type vérifié à l'unité, le filtre de période de la vue.

### Ce qui a été fait, à l'écran

- **La qualité des règles** : chaque code de règle ouvre sa page.
- **`/conformite/regles/[code]`** : sévérité, période et politique appliquée ; les quatre chiffres ; si la règle n'est pas
  écartable, un bandeau qui dit que l'action attendue est la rectificative. Chaque constat avec son dossier, son fournisseur,
  la pièce, l'enjeu et la vérification DGI, les plus gros enjeux d'abord ; une ligne qui ne se choisit pas dit pourquoi.
- **La décision** : « Tout choisir » les écartables ; dès qu'une case est cochée, l'annonce (enjeu en jeu, levé seulement après
  le second regard si la politique l'exige, dossiers concernés), l'avertissement de la maquette (« vous engagez la signature du
  centre agréé »), le motif type facultatif, le motif détaillé vide, et « Écarter les N constats et journaliser ». Après la
  décision, l'écran affiche les conséquences rendues par le backend, à la place de l'annonce.

⚠️ **Hors du pas, et écrit** : « Demander des rectifications » en masse et la pièce d'appui jointe à l'écart ne sont pas
construits ; la portée « ces constats uniquement » est la seule.

### Trois défauts trouvés en chemin

1. **La lecture morte du tampon**, trouvée par une mutation qui survivait.
2. **Un bloc de décision qui débordait sur téléphone** : montants, raisons, annonce et champs coupés à droite. Une grille
   prend la largeur de son contenu le plus long tant qu'on ne lui impose pas une largeur minimale nulle ; mesuré ensuite à
   0 élément débordant, à 390 et à 1 400 pixels.
3. **« Écarter les 1 constat »** au singulier.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Qualité des règles, clic sur FAC-ID-003 | « BLOQUANT · non écartable selon la politique du cabinet », aucune case active |
| FAC-ACH-007 | 3 constats, 579 935 FCFA, 2 adhérents, 0 % ; F-2026-0424 « vérification DGI : indisponible » |
| Deux constats cochés | « Enjeu fiscal en jeu : 459 815 FCFA, levé seulement après le second regard » ; motif détaillé vide, même après le choix du motif type |
| Un collègue écarte F-2026-0424 entre-temps, puis envoi | « aucun constat n'a été écarté (1 refus sur 2). F-2026-0424 : un écart est déjà EN_ATTENTE » ; motif conservé |
| FAC-DOC-011, tout choisir, envoi | « 3 constats écartés et journalisés · 3 effectifs · 3 dossiers » ; taux d'écartement 100 % |
| Comptable du dossier | notifié « Constat écarté sur F-2026-0435 » ; la page sans case à cocher, avec les liens vers les pièces |
| Téléphone (390 px) | aucun débordement |

### État à la fin du pas 103

**3 419 tests passent** sur PostgreSQL réel. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (191 gestes sur 191). Contrat des écrans : 192 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 190 sur 196 (96 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Le motif type dit de quelle sorte de décision il s'agit ; le motif détaillé dit ce qui a été vérifié, et c'est lui qu'on signe.*

## Pas 104 — Mon plan de travail, et trois défauts silencieux

### Pourquoi

Vue A de la maquette du parcours comptable : « ouvrir sa journée et savoir dans quel ordre travailler ». Le tableau de bord
E01 **compte** (dossiers, échéances, pièces, anomalies) ; il ne dit pas **par quoi commencer**. La maquette demande une file
de tâches sur les seuls dossiers du collaborateur, ordonnée par échéance puis par gravité, et les « passages de relais »
avec le réviseur, que les pas 101 et 102 rendent enfin calculables.

### Ce qui a été construit

**Le domaine** (`pilotage/domaine/plan_de_travail.py`), pur : il reçoit l'état relevé des dossiers et en déduit des tâches.
- **Six natures** : traiter les pièces reçues (échéance : plus ancienne réception plus un délai), relancer les pièces
  manquantes (demandes échues ou à escalader), préparer les déclarations (à venir dans un horizon), **régulariser les
  déclarations en retard** (regroupées en une tâche par dossier), rapprocher un relevé bancaire (journal de banque mouvementé
  le mois précédent sans rapprochement arrêté), reprendre les remarques d'une revue renvoyée (aujourd'hui), transmettre le
  mois précédent au réviseur.
- **L'ordre** : par échéance, puis selon l'ordre de gravité du référentiel ; une tâche sans échéance en dernier.
- **La priorité** : urgente, élevée, normale, selon des seuils en jours.
- **Rien ne se coche.** Une tâche disparaît quand l'état change (la pièce est traitée, la déclaration déposée, le mois
  transmis), jamais parce qu'on la déclare faite.

**Au référentiel** (`pilotage/plan_de_travail.yaml`) : les délais internes du cabinet, l'horizon, les seuils de priorité et
l'ordre de gravité, qui doit nommer chaque nature exactement une fois. Les jours limites sont bornés à 28 : tout mois les
contient.

**La route** `GET /pilotage/plan-de-travail` (`SAISIR_ECRITURE`, restreinte au périmètre) : les tâches, « mes dossiers »
(tâches, prochaine échéance, état de la revue du mois précédent) et les passages de relais. Elle vit dans le pilotage, seul
contexte qui lit tous les autres, et réutilise ses relevés.

⚠️ **Un regroupement décidé au vu du résultat.** La première version faisait une tâche par déclaration non déposée : 79 tâches
pour trois dossiers sur le jeu de démonstration, qui ne compte aucun dépôt. Une file de 79 lignes ne dit plus par quoi
commencer. Les déclarations en retard sont désormais une tâche par dossier, avec la plus ancienne échéance.

### À l'écran

`/plan-de-travail`, entrée « Mon plan de travail » en tête du menu pour qui saisit : la journée (« jeudi 17 septembre 2026 ·
3 dossiers · 9 tâches, dont 6 urgentes »), la file numérotée (tâche liée à l'écran qui la fait, dossier, volume, échéance,
priorité), les passages de relais et mes dossiers. « Tout ouvrir en file » n'est pas construit.

### Trois défauts silencieux trouvés en chemin

1. **La composante « demandes sans réponse » du score de risque valait toujours zéro** (depuis le pas du pilotage). La lecture
   appelait `demandes.du_dossier`, que le dépôt des demandes n'a jamais eu ; l'erreur était avalée par l'agrégateur, si bien que
   le filtre sur `StatutDemande.EN_ATTENTE`, **un statut qui n'existe pas**, n'était jamais évalué. Deux défauts qui se
   masquaient. Corrigé (demandes ouvertes, échues ou à escalader) ; test : le 17 août, DP-2026-002 et DP-2026-009 pèsent sur SARL
   BATIMENT PLUS.
2. **L'agrégateur avalait les erreurs de programmation.** `_sans_echouer` absorbait toute exception pour qu'un contexte
   indisponible ne fasse pas tomber le tableau de bord ; il absorbait aussi une méthode inexistante. Il relance désormais
   `AttributeError`, `TypeError` et `NameError`. Aucune autre erreur n'y dormait : le tableau de bord et la vue risque passent.
3. **Six dépôts échappaient au contrôle de conformité des ports.** `test_conformite_des_ports` confronte les réalisations en
   mémoire et SQL aux protocoles de `domaine/ports.py`, et **ignore silencieusement** un contexte qui n'en a pas. Les dépôts des
   lectures de notifications (94), des décisions sur le référentiel (95), des règles du cabinet (97, sans aucun protocole), des
   décisions de direction (100), des rapprochements (101) et des revues (102) avaient leur protocole ailleurs, ou nulle part.
   Ils ont rejoint leurs ports ; le test ne saute plus rien, et aucune méthode ne manquait.

Et deux défauts d'affichage, trouvés en construisant l'écran : **`--ink-700` et `--ink-400`**, employés par 35 déclarations de
style, et **`--surface-2`**, employé par la clôture et la paie pour surligner une ligne, n'étaient définis nulle part. Ces
textes n'étaient pas atténués, ces lignes pas surlignées, sans aucune erreur. Les jetons sont définis en clair et en sombre ;
`--ink-400`, d'abord proposé à 3,97:1 sur blanc, a été assombri à 4,8:1. Un recensement de toutes les variables utilisées
et non définies n'en laisse aucune sans valeur de secours.

`tests/test_plan_de_travail.py`, 14 cas, et un cas de plus au pilotage. **26 mutations, toutes tuées** ; cinq survivaient d'abord
et ont conduit à supprimer deux lignes inutiles (un calcul de fin de mois que le réglage rend superflu, une clé de tri
redondante) et à ajouter trois cas (pièces déjà traitées, déclaration déposée qui sort du plan, relance des erreurs de
programmation).

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Comptable, menu « Mon plan de travail » | « jeudi 17 septembre 2026 · 3 dossiers · 9 tâches, dont 6 urgentes » |
| La file | régulariser les déclarations en retard (33, 17, 33), traiter les pièces (5, 4, 2), relancer (3, 1, 3) |
| « Traiter les pièces reçues » | ouvre `/pieces?dossier=M081234567890P` ; « Régulariser » ouvre l'échéancier du dossier |
| Transmission de juillet puis renvoi par le réviseur | « 1 dossier vous revient avec des remarques » ; la tâche « Reprendre les remarques du réviseur » mène à la revue |
| Chargée de clientèle | pas d'entrée de menu ; l'adresse directe rend « Accès réservé » |
| Téléphone (390 px) | aucun élément débordant |

### État à la fin du pas 104

**3 437 tests passent** sur PostgreSQL réel, **aucun n'est ignoré** (trois l'étaient, faute de port au pilotage). Frontend :
typage, lint, construction de production.
**Avancement des écrans : 100 %** (192 gestes sur 192). Contrat des écrans : 193 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 191 sur 197 (96 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un tableau de bord compte ce qui existe ; un plan de travail dit ce qu'il faut faire en premier, et se vide à mesure qu'on le fait.*

## Pas 105 — Charge et production, et la réaffectation d'un dossier

### Pourquoi

Vue C de la maquette de direction : « qui est saturé, ce qui avance, ce qu'il faut réaffecter ». Le tableau de bord du
pilotage montrait déjà combien de dossiers et quel risque chacun porte. Il ne disait ni si c'était **trop**, ni **quoi faire**,
et aucun geste ne permettait de faire passer un dossier d'un comptable à un autre : on pouvait confier un dossier, jamais le
retirer.

Confrontées elles aussi : la vue D (rentabilité par dossier) reste **écartée à dessein**. La maquette le dit elle-même : sans
la grille d'honoraires et le coût horaire par profil, fournis par le cabinet, la rentabilité serait un chiffre plausible et
faux. La vue E (rapport mensuel archivé) viendra après celle-ci, puisqu'elle doit reprendre exactement ses chiffres.

### Ce qui a été construit

**La charge** (`pilotage/domaine/charge_et_production.py`) : des points (dossier, pièce en attente, échéance du mois, retard)
rapportés à la **capacité du rôle**, en pour cent ; saturé au-delà d'un seuil. Un rôle sans capacité au référentiel n'a pas de
pourcentage. Points, capacités et seuils sont dans `pilotage/charge.yaml`.

**La production du mois**, mesurée **sur les dossiers portés** : pièces reçues et traitées, écritures validées, remarques de
revue. ⚠️ La plateforme **ne sait pas qui a traité une pièce** (la pièce ne le retient pas) ; attribuer cette production à une
personne serait inventer une mesure individuelle. La doctrine du pilotage vaut plus que jamais : la charge décrit la
répartition du travail, et sa seule action est de la rééquilibrer.

**Les réaffectations proposées**, par un algorithme qu'un directeur peut refaire à la main : les saturés du plus chargé au moins
chargé ; leurs dossiers du plus lourd au plus léger ; pour chacun, le collègue **du même rôle** qui resterait le moins chargé,
pourvu qu'il ne dépasse pas le seuil cible et ne suive pas déjà le dossier ; on cesse de soulager dès le seuil cible atteint ;
les charges sont recalculées après chaque proposition, pour que deux propositions ne comptent pas deux fois la même marge.

**Le retrait daté** (`Habilitation.retirer`), symétrique exact de l'affectation du pas 70 : une habilitation qui a déjà couru
est fermée ce jour et relayée par une successeur sans le dossier. Retirer le NIU sur place ferait dire à l'historique que le
comptable n'a jamais suivi le dossier.

**La réaffectation** (`POST /transverse/dossiers/{niu}/reaffectation`, `AFFECTER_DOSSIER`, motif exigé) : retirer à l'un et
confier à l'autre **le même jour**, entre collaborateurs du même rôle. Trois faits au journal, parce qu'une entrée n'est
annoncée qu'à un seul public : `dossier.retire` au collaborateur qui cède, `dossier.affecte` à celui qui reçoit,
`dossier.reaffecte` au chargé de clientèle du dossier. L'adhérent n'est pas prévenu. Le pilotage propose ; il ne modifie aucun
accès.

`GET /pilotage/charge-et-production` (`LIRE_PILOTAGE`) rend les collaborateurs, les propositions et les réglages.

### Un défaut du tableau de bord, visible depuis sa création

**Des adhérents et l'inspecteur figuraient parmi les « collaborateurs »** du panneau « Charge par collaborateur » : Jean-Pierre
NKOA, Georges ATANGANA, Marie-Claire ESSOMBA, Émile TCHOUMBA. La règle « une habilitation à portée explicite porte le dossier »
les comptait, parce que leur portée (leur dossier, leur mission) est explicite. Seuls les rôles internes au cabinet comptent
désormais, au tableau de bord comme dans la nouvelle vue ; un test le garde.

### À l'écran

`/pilotage/charge`, sous-entrée « Charge et production » du pilotage : le mois, les échéances, le seuil ; chaque collaborateur
avec sa charge en pour cent et une barre, ce qui la compose, et la production du mois sur ses dossiers ; chaque proposition
avec sa raison chiffrée et les charges avant et après, puis « Valider » (motif demandé, jamais prérempli) ou « Écarter » (pour
la séance : une proposition se recalcule à chaque lecture). « Production par agence » n'est pas construite : le cabinet n'a pas
d'agence dans le système.

`tests/test_charge_et_production.py`, 23 cas, et un cas de plus au pilotage. **26 mutations** : les 25 applicables tuées, la
dernière visant une condition supprimée parce que redondante (ne pas proposer un dossier à celui qui le cède : il le porte
déjà, donc il est exclu). Quatre autres survivaient d'abord : la division par la capacité (les tests prenaient une capacité de
100, où points et pourcentage coïncident), les deux seuils jamais départagés, et une échéance déposée.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Tableau de bord, charge | Patricia MOUKOURI, Léonard FOTSO, Christelle NDONGO ; plus aucun adhérent |
| Charge et production, 17/09/2026 | Léonard FOTSO « 103 % · saturé » (3 dossiers, 11 pièces en attente, 10 échéances, 83 retards) ; Christelle NDONGO 19 % |
| Proposition | « SARL BATIMENT PLUS : Léonard FOTSO → Christelle NDONGO », 103 % → 63 %, 19 % → 59 % |
| Valider avec motif | plus aucune proposition ; Léonard FOTSO à 63 %, 2 dossiers |
| Notifications | FOTSO « ne vous est plus confié », NDONGO « vous est confié », MOUKOURI « Nouvel interlocuteur comptable » ; l'adhérent rien |
| Léonard FOTSO ouvre la fiche du dossier | 404 : le dossier n'est plus dans son périmètre |
| Téléphone (390 px) | aucun élément débordant |

### État à la fin du pas 105

**3 462 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (194 gestes sur 194). Contrat des écrans : 195 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 193 sur 199 (96 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une charge dit qui porte trop ; elle ne dit jamais qui travaille mal, et sa seule suite est de redistribuer.*

## Pas 106 — Le rapport mensuel de la direction, et une trace qui s'effaçait

### Pourquoi

Vue E de la maquette de direction : « sommes-nous défendables, et que présente-t-on au comité ». Le rapport mensuel y est
**la trace du pilotage exigible en cas de contrôle de l'agrément**, avec deux exigences écrites dans les notes de la maquette :
« le rapport reprend exactement les chiffres affichés : pas de second calcul, pas d'écart possible entre l'écran et le document
de comité », et « le rapport est daté et archivé ».

### Ce qui a été construit

**Aucun second calcul, par construction.** Chaque section est la réponse de la lecture qui alimente l'écran correspondant,
appelée au moment de la génération : le tableau de bord du risque, la charge et la production, le journal des dérogations
(filtré sur le mois), la qualité des règles (sur le mois), les décisions de direction du mois. Pour que le pilotage puisse
appeler les deux lectures de la conformité sans entrer dans ses adaptateurs, elles ont **quitté le corps des routes** pour
`conformite/api.py` : la route de l'écran et le rapport appellent désormais la même fonction. Le journal des dérogations
accepte une période (`du`, `au`).

**Figé et archivé.** Le rapport est un document : ses sections sont gardées telles que les écrans les ont rendues, et relues
sans rien recalculer. Une dérogation levée après la génération change l'écran, pas le rapport. Regénérer un mois crée une
**version suivante** : la précédente est peut-être celle qui a été présentée au comité. Un mois à venir est refusé.

**Intègre.** Le rapport porte l'empreinte SHA-256 de son contenu **canonique** (clés triées : un contenu intact relu dans un
autre ordre ne doit pas paraître altéré), recalculée à chaque lecture (« Intègre » ou « Contenu altéré »), et inscrite au
journal d'audit chaîné.

**Au référentiel** (`pilotage/rapport_mensuel.yaml`) : le numéro d'agrément (laissé « à renseigner » plutôt qu'inventé : un
numéro plausible et faux sur un document de contrôle serait pire qu'une mention vide), l'engagement de sincérité, les
sections incluses.

**Persistance** : table `rapport_mensuel`, migration `a7c2e9f15b48`, port `DepotRapports` dans `pilotage/domaine/ports.py`
(sans méthode de modification ni de suppression). **Routes** : générer, lister, relire ; `LIRE_PILOTAGE` **et** `LIRE_AUDIT`,
puisque le rapport contient le journal des dérogations.

### À l'écran

- **`/pilotage/rapports`** (« Rapport mensuel » sous Pilotage) : générer le rapport d'un mois, puis la liste des rapports
  archivés avec leur version, leur date, leur auteur, le début de leur empreinte et leur intégrité.
- **`/pilotage/rapports/[identifiant]`** : l'agrément, la version, la date des chiffres, l'intégrité et l'empreinte complète,
  l'engagement, puis les cinq sections, lues dans le document figé.
- **« Exporter en PDF »** passe par l'impression du navigateur : aucune bibliothèque de rendu PDF n'est ajoutée au backend. À
  l'impression, la coquille (menu, en-tête, boutons) disparaît et le document s'imprime entier.

⚠️ **Hors du pas, et écrit** : « Envoyer au comité » (le cabinet n'a désigné ni comité ni destinataire), la colonne « pièce
d'appui » des dérogations (l'écart ne retient pas encore de pièce d'appui) et la « revue trimestrielle ».

### Deux défauts trouvés en chemin

1. **L'empreinte du rapport n'aurait jamais été inscrite au journal.** Le journal d'audit expurge toute donnée rangée sous la
   clé `empreinte` (c'est le nom de l'empreinte d'un mot de passe), et l'expurgation a lieu **avant** l'écriture. Le test l'a
   vu : l'entrée portait « «expurgé» ». La donnée prend le nom `sha256_du_contenu` ; la liste d'expurgation, garde-fou de
   sécurité, n'est pas assouplie.
2. **Le même défaut existait depuis le dépôt de TVA.** L'empreinte du bordereau déposé, présentée en tête du module comme
   « ce qui permettra de se défendre », était effacée de la trace chaînée à chaque dépôt, aux deux endroits où le journal
   l'écrit. Elle est désormais inscrite sous `sha256_du_bordereau` ; un test le garde. Un balayage de tout le code ne trouve
   aucune autre donnée de journal rangée sous une clé expurgée.

`tests/test_rapport_mensuel.py`, 12 cas dont un sur PostgreSQL (le rapport relu en base reste intègre), et un cas au dépôt de
TVA. **18 mutations : 17 tuées**, et une équivalente, écrite comme telle : aucun rôle ne détient aujourd'hui `LIRE_PILOTAGE` sans
`LIRE_AUDIT`, le second contrôle ne refuse donc personne de plus ; il reste pour le jour où un tel rôle naîtra. Quatre autres
survivaient d'abord : aucun fait n'était hors du mois du rapport, si bien que ni le filtre de période des dérogations ni celui
des décisions n'étaient éprouvés.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Rapport de décembre 2026 | « le mois 2026-12 n'a pas commencé : il n'y a rien à rapporter » |
| Rapport de septembre, après trois écarts | « version 1 · chiffres au 17/09/2026 » ; « Rapport intègre. Empreinte SHA-256 06b17651… inscrite au journal d'audit » |
| Section des dérogations | « 3 dérogations, dont 3 effectives », les mêmes chiffres que l'écran du journal sur la même période |
| Impression | menu et boutons masqués ; PDF A4 de deux pages, lisible |
| Rapport d'août généré ensuite | la liste montre les deux rapports, chacun « Intègre » |
| Réviseur | « Accès réservé » |
| Téléphone (390 px) | aucun élément débordant |

### État à la fin du pas 106

**3 478 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (197 gestes sur 197). Contrat des écrans : 198 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 196 sur 202 (97 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un rapport de comité ne vaut que s'il dit, dans un an, exactement ce que la direction a vu ce jour-là.*

## Pas 107 — La clôture mensuelle, le mois verrouillé, et des pièces qui ne finissaient jamais

### Pourquoi

Les quatre maquettes de parcours avaient été confrontées vue par vue pour le réviseur et la direction.
Le parcours comptable, lui, s'arrêtait à ses vues A (plan de travail) et B (rapprochement). Sa vue G,
« Clôture mensuelle d'un dossier » (UC10, UC12), dit : **vérifier, verrouiller la période, passer la main
au réviseur**. Le produit savait passer la main (pas 102) ; il ne vérifiait rien avant, et **ne verrouillait
rien après** : un mois transmis, puis validé par le réviseur, restait ouvert à la saisie, à la correction et à
la contre-passation. « Le mois validé » ne désignait plus le mois qu'on avait relu.

### Ce qui a été construit

**Les points de contrôle du mois** (`comptabilite/domaine/cloture_mensuelle.py`), tous calculés sur les faits,
aucun coché à la main :

| Point | Ce qui est vérifié | Par défaut |
| --- | --- | --- |
| Pièces du mois | les pièces datées du mois (date du document, sinon réception) sont comptabilisées ou classées | bloquant |
| Brouillons | aucune écriture du mois en brouillon | toujours bloquant |
| Rapprochement | un rapprochement arrêté couvre la fin du mois, par compte de banque mouvementé | bloquant |
| Caisse | aucun compte 57 négatif **en fin de journée**, en cumul depuis l'ouverture | bloquant |
| Balance | le mois est équilibré | bloquant |
| Numérotation | les journaux de l'exercice sont sans trou ni doublon | bloquant |
| Pièces attendues | les demandes encore ouvertes auprès de l'adhérent | informatif |
| Écarts en suspens | un écart proposé sur une pièce du mois attend encore le second regard | bloquant |

Brouillons, rapprochement, balance et numérotation **ne sont pas recalculés** : la revue du réviseur et la
clôture du comptable appellent la même fonction (`points_de_la_periode`), pour que les deux écrans ne puissent
pas se contredire. La caisse se juge en fin de journée, parce que l'ordre de saisie d'une même journée ne dit rien
de l'ordre des opérations. Le point « écart en suspens » remplace l'« anomalie écartée sans motif » de la maquette :
un écart sans motif ne peut pas exister (pas 92), mais un écart proposé et pas encore tranché, si.

**Le référentiel décide** (`Docs/referentiel/cloture_mensuelle/reglages.yaml`) : chaque point actif ou non,
bloquant ou informatif, les statuts de revue qui verrouillent, les racines des comptes de caisse et d'achats. Un
réglage qui mentirait est refusé au chargement : les brouillons non bloquants (la transmission les refuse de
toute façon), un mois renvoyé qui verrouillerait (on demande au comptable de le corriger), un code inconnu.

**Le verrou se déduit des revues**, il n'est pas une donnée à part : il ne peut ni survivre à la revue, ni lui
manquer. Transmis ou validé, le mois est verrouillé ; renvoyé par le réviseur, il se rouvre. Le refus
`MoisVerrouille` s'applique à **un seul endroit** de `tenue_du_journal.py`, commun aux quatre gestes qui
écrivent :

- saisir une écriture datée du mois ;
- corriger un brouillon, **vers** le mois comme **depuis** le mois (le sortir de juillet change juillet autant
  que d'y ajouter une écriture) ;
- valider ;
- contre-passer à une date du mois. La contre-passation datée d'un mois ouvert reste permise, même sur une
  écriture d'un mois verrouillé : c'est le moyen de corriger, visible au grand livre.

Le paramètre `periodes_verrouillees` est **exigé sans défaut**, pour la leçon du pas 71 : un contrôle dont
l'argument vaut « rien de verrouillé » par défaut est un contrôle qu'un nouvel appelant oublie sans bruit. La
reprise d'un fichier le rencontre écriture par écriture. La clôture d'exercice passe `()` et le dit : l'écriture
d'à-nouveau reporte la balance par obligation, souvent des mois après la transmission de janvier.

**La transmission exige la clôture.** `transmettre_un_mois` prend les points de clôture, sans défaut, et refuse
en nommant chaque point bloquant ; la retransmission après un renvoi rencontre le même contrôle. Un mois
**pas encore fini** ne se transmet plus : le transmettre le verrouillerait avant ses derniers jours.

### À l'écran

- **`/comptabilite/cloture`** (« Clôture mensuelle » sous Comptabilité) : dossier et mois ; « Clôture de juillet
  2026 · 7 points sur 8 traités » ; chaque point avec son glyphe (✓ traité, ⬣ bloquant, ▲ à savoir), son détail
  et l'écran où il se traite ; le mois en chiffres (pièces reçues, écritures validées, achats nets, TVA rejetée) ;
  les réviseurs habilités qui recevront le mois ; le bandeau du verrou quand il est posé.
- **Le bouton** dit ce qui manque : « Transmettre au réviseur · 1 point restant », désactivé. « Jamais de refus
  muet » (maquette, note 1).
- **« Enregistrer et continuer plus tard »** : les points se recalculent sur les faits à chaque visite, il n'y a
  rien à garder au serveur. Le commentaire au réviseur est gardé **dans le navigateur**, par dossier et par mois,
  et proposé au retour (« Le reprendre »). L'écran le dit.
- La page des revues ne transmet plus directement : elle mène à la clôture. Transmettre sans voir les points,
  c'est ce que ce pas retire.

### ⚠️ Le défaut que la clôture a mis au jour : aucune pièce ne finissait son traitement

En préparant l'essai réel, aucun mois d'aucun dossier ne pouvait se clore. La cause est ancienne : le domaine de la
pièce avait ses deux fins de traitement, `comptabiliser` et `archiver`, et **aucune route ne les appelait**. Seul
le jeu de démonstration posait des pièces comptabilisées. Une pièce lue, saisie, dont l'écriture était validée,
restait « en attente de traitement » pour toujours :

- la boîte de réception ne se vidait jamais, et son compteur au menu non plus ;
- la charge du pilotage (pas 105) comptait ces pièces comme du travail restant ;
- un doublon, un relevé bancaire, un contrat, qui ne produisent pas d'écriture, n'avaient **aucune issue**.

Corrigé dans `collecte/application/traitement.py` :

- **À la validation d'une écriture**, la pièce qu'elle cite (par identifiant, ou par la référence du document,
  qui est ce que la proposition d'écriture inscrit) passe à COMPTABILISEE, rattachée à l'écriture, et l'acte est
  au journal d'audit. À la validation et non à la saisie : un brouillon peut encore changer de pièce. **Deux
  pièces candidates, aucune n'est rattachée** : un doublon non classé porte la même référence que l'original, et
  choisir au hasard rattacherait peut-être la copie.
- **`POST /collecte/pieces/{identifiant}/classement`** : classer sans écriture, avec un motif d'au moins
  10 caractères, inscrit au journal d'audit. Écran : « N pièces lues à comptabiliser ou classer » dans la boîte
  de réception.

La question de savoir si ce classement demande un second regard est posée au cabinet (**Q28**, avec qui rouvre un
mois validé et la liste des points bloquants).

### Les tests existants qui transmettaient juillet

Juillet, au jeu de démonstration, a des pièces lues et non comptabilisées : il ne se transmet plus, et c'est voulu.
Deux fichiers le transmettaient pour éprouver autre chose (le circuit de la revue, la tâche du plan de travail).
Ils lèvent désormais le caractère bloquant des points, **en le disant**, comme un cabinet le ferait au référentiel ;
les brouillons restent bloquants. Un test garde, lui, le chemin réel sans aucun réglage assoupli : LA COLOMBE,
juillet, une pièce classée, une écriture validée qui comptabilise l'autre, la transmission, le verrou, le renvoi, un
écart proposé qui bloque la retransmission jusqu'au second regard.

`tests/test_cloture_mensuelle.py`, 35 cas dont un sur PostgreSQL. **34 mutations : 34 tuées**, dont trois après
coup : le filtre des écarts « en attente » (un écart tranché ne suspend plus rien), la date du document plutôt que
la réception (une pièce reçue le 5 août, datée du 30 juillet, appartient à juillet), et le contrôle de la
retransmission.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Revues → « Clôturer un mois », LA COLOMBE, juillet | « Clôture de juillet 2026 · 7 points sur 8 traités » ; « 2 pièces du mois à comptabiliser ou classer » |
| Le bouton | « Transmettre au réviseur · 1 point restant », désactivé ; « 1 point bloquant à traiter d'abord » |
| Enregistrer et continuer plus tard | « Commentaire gardé dans ce navigateur » |
| Boîte de réception, classer avec « court » | « Dites pourquoi la pièce ne produira pas d'écriture (10 caractères au moins) » |
| Classer PJ-2026-0003 avec un motif | 10 → 9 pièces à comptabiliser ou classer ; le compteur du menu passe de 11 à 9 |
| Valider l'écriture qui cite F-2026-0434 | 200 ; « 8 points sur 8 traités » |
| Retour sur la clôture | « Un commentaire est gardé dans ce navigateur », « Le reprendre » ; bouton actif |
| Transmettre | la revue s'ouvre ; la clôture affiche « Période du 01/07/2026 au 31/07/2026 verrouillée : transmis au réviseur (Léonard FOTSO, le 17/09/2026) » |
| Saisir une écriture datée du 30 juillet | 409 : « le 30/07/2026 tombe dans la période […] : elle est verrouillée. Passer la correction dans un mois ouvert, par une contre-passation, ou demander au réviseur de renvoyer le mois. » |
| Téléphone (390 px) | aucun élément débordant |

### État à la fin du pas 107

**3 514 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (199 gestes sur 199 : lire la clôture, transmettre depuis elle, classer une
pièce). Contrat des écrans : 200 appels vérifiés, 0 écart (1 illisible par construction). Couverture des routes :
198 sur 204 (97 %).

Restent hors du pas, et écrits : la saisie des ventes et des encaissements des dossiers au réel et la paie
(« reste à concevoir côté comptable », note 4 de la maquette) ; la clôture annuelle qui ne recalculerait plus les
mois verrouillés (note 2), puisque le produit ne recalcule déjà rien d'un exercice clos.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un mois qu'on a relu ne vaut que s'il ne peut plus changer sans laisser de trace.*

## Pas 108 — Le lettrage, la balance filtrée, et des cases qui se décochaient toutes seules

### Pourquoi

Vue C du parcours comptable, « Grand livre et balance » (UC07 : retrouver un compte, un montant, la pièce
d'origine). Le produit avait la balance et le grand livre depuis longtemps ; confrontés à la maquette, il
leur manquait :

- **le lettrage**. La ligne d'écriture avait un champ `lettrage`, et le grand livre une colonne « Lettrage »,
  mais **aucun geste ne lettrait**. « 2 écritures non lettrées », ce qui reste réellement ouvert chez un
  fournisseur, ne se lisait nulle part ;
- la **période** et le **journal** (« Période : janvier à juillet », « Journal : tous ») ;
- **le lien de chaque ligne vers sa pièce** (« c'est la traçabilité exigée jusqu'à la liasse ») ;
- la **balance et le compte côte à côte** (« le comptable ne perd jamais le contexte pour ouvrir un compte »).

### Le lettrage vit à part de l'écriture

Remplir le champ `lettrage` de la ligne serait **réécrire une écriture validée**, que le dépôt refuse à juste
titre. Le lettrage n'est pas un fait comptable, c'est un appariement de travail qui se fait et se défait : il a
son propre objet (`comptabilite/domaine/lettrage.py`), sa table (`lettrage`, migration `b3d8f1a26c59`), et le grand
livre **superpose** sa lettre aux lignes. Le champ de la ligne garde ce qu'il portait : la lettre **reprise** du
logiciel du client (pas 85), affichée « reprise », qui ne se défait pas ici.

Les règles, chacune pour une erreur précise :

| Règle | Ce qu'elle empêche |
| --- | --- |
| Compte lettrable du plan (fournisseurs, clients, personnel) | apparier des charges, où il n'y a rien à apparier |
| Écritures validées | lettrer un brouillon dont le montant peut encore changer |
| Lignes du compte, désignées par `(écriture, rang)` | lettrer la ligne 601 d'une facture au lieu de sa ligne 401 |
| Une ligne lettrée une fois à la fois | un règlement qui solderait deux factures |
| Même tiers (réglable) | effacer la dette d'ALPHA avec le règlement de BÊTA |
| Débit égal au crédit, à l'écart toléré près (0 par défaut) | cacher un reste dû |
| Une lettre jamais réutilisée, même défaite | « la lettre C » qui désignerait deux appariements selon la date |

Le **verrou mensuel du pas 107 ne s'applique pas** : lettrer ne change ni un montant ni une date, la balance du mois
relu reste la même. Au référentiel : `lettrage/reglages.yaml` (écart toléré, même tiers exigé).

Routes : `POST /comptabilite/dossiers/{e}/lettrages` et `…/lettrages/{identifiant}/delettrage`, `SAISIR_ECRITURE`,
inscrites au journal d'audit.

### La balance et le grand livre filtrés, sans une addition à l'écran

- Le grand livre accepte `du`, `au`, `journal` et `lettrage` (toutes, lettrées, non lettrées). ⚠️ Les filtres
  s'appliquent **après** le calcul du solde progressif : filtrer avant ferait partir le solde de zéro au premier jour
  de la période, et le solde d'un fournisseur en août ne serait plus ce qu'on lui doit. Un compte mouvementé dont
  aucune ligne ne passe le filtre rend une liste vide, et non « aucun mouvement ».
- Chaque ligne porte son **rang**, la **pièce** de l'écriture, l'origine et l'identifiant de sa lettre.
- La balance accepte `du` et `journal`. **Son pied aussi** : `/sante` prend les mêmes filtres pour les totaux,
  l'équilibre et le résultat, parce que le frontend a pour règle écrite de ne rien additionner. La numérotation se
  contrôle toujours sur l'exercice entier : un trou ne disparaît pas parce qu'on regarde un autre mois.
- L'écran n'additionne pas non plus la sélection à lettrer : il envoie les lignes cochées, et c'est le refus du backend
  qui donne « 100 000 au débit, 1 669 500 au crédit, écart de 1 569 500 FCFA ».

### À l'écran

- **`/comptabilite`** : recherche (numéro ou intitulé de compte, qui masque des lignes sans rien recalculer), période,
  journal ; « totaux contrôlés à l'affichage ». Un numéro de compte ouvre son **détail à côté de la balance** (5/12 et
  7/12 au-delà de 1 400 px, l'un sous l'autre en deçà), sans perdre les filtres.
- **Le détail du compte** (`DetailDuCompte`, partagé avec `/comptabilite/grand-livre`) : toutes, non lettrées,
  lettrées ; une case par ligne non lettrée d'un compte de tiers ; « Lettrer la sélection » ; « Délettrer » sur une
  lettre posée ici ; « N lignes non lettrées » ; le libellé mène à la pièce par la recherche globale, qui trouve une
  pièce reçue (PJ-…) comme un document (F-…).

Hors du pas, et écrits : les raccourcis clavier de la maquette (L pour lettrer, Ctrl+Z pour délettrer), la recherche
par montant ou numéro de pièce **dans** la balance (la recherche globale du pas 93 les trouve), l'export.

### ⚠️ Le défaut que l'essai réel a trouvé, et qui existait depuis le pas 103

Premier essai du lettrage dans un navigateur : une sélection refusée, puis corrigée d'une case, partait avec **trois**
lignes au lieu de deux. Cause : avec `<form action={…}>`, React **réinitialise le formulaire après chaque action,
refus compris**. Les champs de texte contrôlés s'en remettent (la leçon du pas 100), **pas les cases à cocher ni les
boutons radio** : la case se décoche à l'écran alors que l'état React la tient toujours cochée. La case qu'on croyait
décocher se recochait.

Balayage de tous les formulaires à cases : le même mécanisme touchait trois écrans. Le premier a été reproduit puis
vérifié corrigé dans un navigateur ; les deux autres sont déduits de la lecture du code (une case ou un bouton radio
contrôlé dans un `<form action>` qui peut être refusé), et corrigés de la même façon.

| Écran | Ce que l'écran montrait après un refus |
| --- | --- |
| Écarter en masse (pas 103) | les pièces décochées, et toujours « Écarter 2 constats », qui les écartait au renvoi |
| Clôture d'exercice (pas 55) | la confirmation décochée, le bouton « Clore » actif |
| Inviter un collaborateur (pas 69) | le choix « Des dossiers / Tout le cabinet » revenu au défaut |

L'écran mentait sur ce qui allait partir, et le premier cas engage la signature du centre agréé. Correction commune,
`app/lib/soumission.ts` : `soumettreSansReinitialiser` empêche la soumission native, construit les données depuis le
formulaire affiché et appelle l'action dans une transition ; la validation du navigateur a déjà eu lieu. Le lettrage
construit son envoi depuis l'état.

En chemin aussi, sur téléphone : la balance était coupée après la colonne « Débit » sans barre de défilement, depuis sa
création ; le libellé du détail tombait à zéro. Les deux tableaux défilent désormais dans leur panneau.

### Les tests

`tests/test_lettrage.py`, 25 cas dont un sur PostgreSQL. **28 mutations : 28 tuées**, dont quatre après coup : le
doublon de ligne refusé par l'entité (l'application dédoublonne déjà, l'entité seule le garde), le filtre de journal
seul, le filtre de début de période, et la requête SQL des lettrages d'un compte (sans le filtre sur le compte, le
premier lettrage du 411 prenait la lettre B parce que le 401 avait déjà un A).

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Deux règlements d'août saisis et validés (1 669 500 et un acompte de 100 000) | 401 : « 5 lignes non lettrées » |
| Cocher la facture de 1 669 500 et l'acompte, lettrer | « la sélection ne se solde pas : 100 000 au débit, 1 669 500 au crédit, écart de 1 569 500 FCFA » ; **toujours 2 sélectionnées** |
| Décocher l'acompte, cocher le virement, lettrer | 3 lignes non lettrées ; filtre « Non lettrées » : 3 lignes |
| « Lettrées », puis « Délettrer » | plus aucune ligne lettrée |
| Balance, journal BQ | « journal BQ · 2 comptes mouvementés » ; totaux 1 769 500 / 1 769 500, équilibrée |
| Recherche « 52 » | le seul compte 521 |
| Clic sur un libellé | la recherche trouve « F-2026-0419 · Pièce PJ-2026-0008 · … COMPTABILISEE » |
| Chargée de clientèle | le détail se lit, aucune case, aucun bouton |
| Écarter en masse, motif refusé (pas 103) | la pièce reste cochée, le motif et le motif type restent |
| Téléphone (390 px) | aucun élément débordant hors des tableaux qui défilent |

### État à la fin du pas 108

**3 542 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (201 gestes sur 201). Contrat des écrans : 202 appels vérifiés, 0 écart (1 illisible
par construction). Couverture des routes : 200 sur 206 (97 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Ce qui reste ouvert chez un fournisseur ne se lit qu'une fois le reste apparié, et une case qui ment sur ce qui part
vaut moins qu'aucune case.*

## Pas 109 — La déclaration de TVA préparée, et un crédit qui se perdait chaque mois

### Pourquoi

Vue D du parcours comptable, « Préparation d'une déclaration de TVA » (UC08 : constituer, contrôler, transmettre au
réviseur). L'écran de la déclaration existait depuis longtemps, avec la ligne qui fait la valeur du produit (la TVA
rejetée par le contrôle, pièce par pièce) et la recevabilité du dépôt. Confronté à la maquette, il lui manquait :

- **la déclaration ligne par ligne** (ventes taxables et leur base, exonérées, collectée, déductible sur biens et sur
  services, rejetée, crédit reporté), et la note : « chaque ligne renvoie aux écritures qui la composent » ;
- **les quatre étapes** : pièces du mois, constitution, contrôles, dépôt par le réviseur « verrouillé jusqu'à
  transmission » ;
- **ce qui alimente la déclaration** : pièces reçues et comptabilisées, complétude, pièces attendues ;
- et la règle : « **le comptable transmet, il ne dépose pas** ».

### ⚠️ Deux défauts trouvés à la lecture, avant d'écrire une ligne

1. **Le crédit de TVA se perdait d'un mois sur l'autre.** Le crédit reporté arrivait en **paramètre de la requête**,
   avec zéro pour défaut, et aucun écran ne le passait. Un mois de gros achats laissait un crédit ; le mois suivant le
   déclarait perdu, **surestimait la TVA à payer d'autant**, au détriment de l'adhérent, et le bordereau déposé le
   figeait. N'importe quel appelant pouvait aussi y écrire le montant de son choix. Chez SARL BATIMENT PLUS, juillet
   laisse 500 500 FCFA de crédit ; août le déclarait à zéro.
2. **La réserve « pièces reçues et non comptabilisées » n'avait jamais été levée.** `pieces_en_souffrance` avait une
   valeur par défaut, zéro, et la route ne le passait pas. Même classe de défaut que le pas 104 : un contrôle
   silencieusement nul, que rien ne signalait.

### Ce qui a été construit

**Le crédit se calcule** (`credit_reporte_au_debut_de`) : mois après mois, depuis l'ouverture du premier exercice
connu, chaque déclaration reçoit le crédit que la précédente laisse. Seuls comptent les mois où le dossier était
assujetti ; un mois sans régime connu (un exercice ouvert avant l'adhésion) n'est pas déclarable
(`mois_declarables_avant`). Le paramètre de requête a disparu des trois routes : préparer et consigner le dépôt
calculent le même crédit, donc la même empreinte. ⚠️ Un dossier repris avec un crédit antérieur à la plateforme ne le
retrouve pas encore : il faudra l'inscrire comme une donnée de reprise, datée et justifiée.

**Les lignes du formulaire** (`obligations/application/formulaire_tva.py`) : la plateforme calcule des **grandeurs** ;
leurs **codes et libellés** sont au référentiel (`obligations/formulaire_tva.yaml`), parce que le formulaire de la DGI
change et que les codes L01 à L30 de la maquette **restent à confirmer** par le fiscaliste. Chaque ligne porte sa base,
son montant et ses écritures.

- Une vente (70 au crédit) va aux ventes **taxables** si l'écriture porte de la TVA collectée, sinon aux **exonérées**.
- La TVA déductible (445 au débit) va à sa catégorie par son compte : biens (4451), immobilisations (4452), services
  (4454), autres. La base d'une catégorie est la somme **nette** des classes 6 et 2 des écritures dont toute la TVA est
  de cette catégorie : un rabais porté au 609 la réduit. Une écriture qui mêle deux catégories ne se répartit pas sans
  inventer une clé ; sa base n'est comptée nulle part, et la ligne le dit (« base partielle »).
- Les montants de TVA sont ceux du décompte : les lignes ventilent et justifient, elles ne recalculent rien. Un test
  vérifie que la somme des lignes déductibles est la TVA déductible du décompte.

**La complétude** : pièces de la période (par la date du document, sinon la réception, comme à la clôture mensuelle),
pièces en souffrance, pièces attendues de l'adhérent. Nouvelle réserve **PIECES-ATTENDUES** : « Déposer maintenant
expose à une déclaration rectificative : relancer l'adhérent, ou documenter le choix. »

**La revue du mois exigée avant le dépôt**, au référentiel (`obligations/depot_tva.yaml`) : `revue_du_mois_exigee`
(AUCUNE, TRANSMISE, VALIDEE ; TRANSMISE par défaut) et `niveau_si_manquante` (BLOQUANT par défaut, ou RESERVE). Le mois
doit être couvert **entièrement** par une revue : celle de juin ne vaut pas pour juillet. Un mois renvoyé ne suffit pas.
Anomalie **REVUE-DU-MOIS**, avec le remède : clôturer le mois, puis le transmettre. Les paramètres `completude`, `revue`
et `reglages` sont exigés **sans défaut**, pour la leçon qui vient d'être répétée.

### À l'écran (`/obligations/declarations`)

- **Les quatre étapes**, lues sur ce que le backend a calculé : « 3 traitées sur 7 · 0 attendue », « Montants issus des
  journaux », « 1 bloquant · 3 réserves », « Fermé jusqu'à transmission » puis « Mois transmis ».
- **La déclaration**, L01 à L30, base, montant (les grandeurs qui se retranchent entre parenthèses), nombre d'écritures,
  la liste des écritures dépliable, et en pied la TVA à payer ou le crédit à reporter.
- **Ce qui alimente la déclaration** : pièces reçues et traitées, complétude, TVA rejetée ; les pièces attendues avec
  « relancer l'adhérent », les pièces à comptabiliser ou classer avec la boîte de réception.
- **« Transmettre au réviseur »** mène à la clôture du mois (pas 107), où la transmission se fait avec ses points de
  contrôle. Le lien disparaît une fois le mois transmis.
- Sur téléphone, le tableau des rejets était coupé depuis sa création ; il défile désormais dans son panneau.

Hors du pas, et écrits : « Enregistrer » (il n'y a rien à enregistrer, tout se recalcule sur les journaux), « Relancer
les contrôles » (ils sont relancés à chaque affichage), le même gabarit pour l'IGS, l'acompte d'IS et la CNPS (note 4
de la maquette), et l'annonce de l'impact d'une correction sur une déclaration en préparation (vue E, note 3).

### Les tests existants qui déposaient sans transmettre

Six fichiers déposaient une TVA pour éprouver autre chose (le bordereau, l'accusé, l'échéancier, la persistance, la
charge, le plan de travail). Ils demandent désormais la fixture `depot_tva_sans_revue_exigee`, qui règle le référentiel
comme un cabinet n'exigeant rien, **et le dit** ; les cas unitaires de la recevabilité passent un mois transmis.
L'exigence elle-même est gardée par `tests/test_declaration_tva_preparee.py`.

`tests/test_declaration_tva_preparee.py`, 18 cas dont un sur PostgreSQL. **27 mutations : 27 tuées.** Quatre
survivaient d'abord, et l'une a changé le calcul : la base déductible ne comptait que les débits, et rien ne le
vérifiait ; en l'écrivant, la base nette est apparue comme la bonne. Les trois autres : la réserve des pièces attendues,
la revue d'un autre mois qui ne couvre pas la période, un mois sans régime connu compté comme déclarable.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| SARL BATIMENT PLUS, juillet | étapes « 3 traitées sur 7 · 0 attendue », « 1 bloquant · 3 réserves », « Fermé jusqu'à transmission » |
| Recevabilité | « Le mois doit être transmis au réviseur avant le dépôt : le mois n'a pas été transmis au réviseur. » |
| La déclaration | L20 base 4 570 650, TVA 879 850, 3 écritures ; L24 (379 350), 1 écriture ; crédit à reporter 500 500 FCFA |
| Ce qui l'alimente | 7 reçues · 3 traitées, complétude 43 %, « 4 pièces reçues à comptabiliser ou classer » |
| Août | L30 (500 500) : le crédit de juillet est reporté |
| LA COLOMBE, juillet | « Transmettre au réviseur » mène à `/comptabilite/cloture?dossier=…&mois=2026-07` |
| Classer une pièce, valider l'écriture, transmettre depuis la clôture | étapes « 0 bloquant · 1 réserve », « Mois transmis » ; « Déposable, sous 1 réserve à assumer » ; le lien a disparu |
| Téléphone (390 px) et 1 400 px | aucun élément débordant hors des tableaux qui défilent |

### État à la fin du pas 109

**3 561 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (201 gestes sur 201 ; aucun geste nouveau, l'écran existait). Contrat des écrans :
202 appels vérifiés, 0 écart (1 illisible par construction). Couverture des routes : 200 sur 206 (97 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une déclaration ne vaut que si chaque case remonte à ses écritures, et un crédit qu'on oublie de reporter est un impôt
qu'on fait payer deux fois.*

## Pas 110 — La fiche d'une écriture, et deux annulations qui n'annulaient rien ou annulaient deux fois

### Pourquoi

Vue E du parcours comptable, « Correction d'une écriture et plan de comptes » (UC05 : contre-passer ; UC11 : trouver un
compte SYSCOHADA au clavier). Le produit savait contre-passer depuis le pas 71, **en ligne**, dans la liste du journal :
un motif, une date, « Enregistrer l'inverse ». La maquette demande davantage :

- une **fiche** de l'écriture : ses lignes et leurs attributs fiscaux, « Validée, non modifiable », **son historique**,
  l'état de sa période, et quatre actions (contre-passer, dupliquer, ouvrir la pièce, signaler au réviseur) ;
- une contre-passation dont les **lignes inversées se voient avant d'être créées**, et dont « l'impact sur une
  déclaration en préparation est annoncé avant validation » ;
- une **palette de comptes** (F2), où « les comptes déjà utilisés dans le dossier passent avant le plan SYSCOHADA général ».

### ⚠️ Deux défauts de la contre-passation, trouvés en la construisant

1. **Une écriture se contre-passait deux fois.** Rien ne l'empêchait. Essai : deux envois sur 2026/AC/000001
   produisaient les écritures 4 et 5, deux annulations d'une même facture ; validées, la charge et la TVA déductible
   passaient **en négatif**. Un double clic ou deux onglets suffisaient. Refus `ContrepassationEnDouble`, qui nomme
   l'inverse existante et dit si elle est encore en brouillon.
2. **Une contre-passation d'achat ne changeait pas la déclaration de TVA.** Le décompte (`etablir_declaration_tva`) ne
   comptait que les **crédits** du 443 et les **débits** du 445. Une contre-passation d'achat (le 445 au crédit), un avoir
   reçu, une vente annulée (le 443 au débit) étaient ignorés. Essai : la facture 2026/AC/000003, dont la TVA de
   269 500 FCFA avait été déduite en juillet, contre-passée et validée en août : la déclaration d'août restait à 500 500
   FCFA de crédit au lieu de 231 000. **La TVA d'une facture annulée restait déduite**, exposée au redressement. Le calcul
   est désormais **net** de sens, dans le décompte comme dans les lignes du formulaire (pas 109) ; l'inverse d'une ligne
   rejetée annule aussi le rejet, qui apparaît en négatif au détail des rejets.

En chemin aussi : `AttributFiscal` acceptait un nom de champ inconnu sans rien dire. Un attribut construit avec
`deductibilite_tva=False` (le vrai nom est `tva_deductible`) ne rejetait aucune TVA, et la faute ne se serait vue qu'à la
déclaration. Il refuse désormais tout champ inconnu, et les 773 tests qui touchent la comptabilité et la TVA passent.

### Ce qui a été construit

**L'aperçu de la contre-passation** (`apercevoir_la_contrepassation`) : les mêmes contrôles que le geste, **par le même
corps** (`_controler_la_contrepassation`), et le même constructeur d'inverse ; rien n'est écrit, le numéro est pressenti
et jamais réservé (réserver ferait un trou si le comptable renonce). Un aperçu qui accepterait ce que le geste refuse
serait pire que pas d'aperçu.

**L'impact sur la TVA** (`GET /obligations/dossiers/{e}/impact-contrepassation`) : la déclaration du mois de la
contre-passation est établie **deux fois** par le même calcul, sans puis avec l'inverse, comme si elle était validée.
Réponses : « ne mouvemente pas de TVA », « pas assujetti ce mois-là », « sera recalculée », ou « déjà déposée : cette
correction demandera une déclaration rectificative », avec la TVA à payer et le crédit, avant et après. Il est lu chez les
obligations, parce que c'est leur calcul de la déclaration et que l'arête `comptabilite → obligations` n'existe pas.

**La fiche** (`GET …/fiche`) : l'écriture, et un historique assemblé des faits qui existent déjà : saisie, validation,
contre-passations, lettrages faits et défaits (pas 108), passages de relais de la revue de son mois (pas 102),
signalements. ⚠️ L'heure de la saisie n'est pas conservée par l'écriture : l'historique dit « date non conservée » plutôt
que d'en inventer une. S'y ajoutent le verrou de la période (pas 107), l'exercice clos, et si la contre-passation est
possible, sinon pourquoi.

**Signaler au réviseur** (`POST …/signalement`, `SAISIR_ECRITURE`) : pas une remarque de revue (l'acte du réviseur sur un
mois transmis), l'inverse, le comptable qui dit « regarde celle-ci », à tout moment. Aucun objet nouveau : une entrée du
journal d'audit, que la fiche relit, et **un abonnement** (`notifications/abonnements.yaml`) qui l'annonce aux réviseurs
du dossier, sans une ligne de code de notification.

**Les comptes les plus employés** (`GET /dossiers/{e}/comptes-utilises`) : du plus au moins employé, brouillons compris.

⚠️ L'aperçu demande `SAISIR_ECRITURE` et non `CONTRE_PASSER` : cette permission-là exige un motif **au contrôle
d'accès**, qui l'inscrit au journal. Un aperçu n'engage rien et ne se motive pas ; le motif est demandé au geste.

### À l'écran

- **`/comptabilite/ecritures`** (ouverte depuis le numéro de l'écriture au journal, et depuis la notification du
  réviseur) : « Écriture 2026/AC/000003 · journal AC · validée le 03/08/2026 par … », le bandeau « Validée, non modifiable »
  et l'état de la période, les lignes avec leur attribut fiscal, l'historique, les actions.
- **Contre-passer** ouvre le panneau d'aperçu : la date (le navigateur refuse une date antérieure à l'écriture, le backend
  aussi), « Recalculer », les lignes proposées « inversées et non modifiables », l'impact sur la TVA, le motif obligatoire,
  « Créer la contre-passation ». Une fois créée, l'action disparaît au profit de « Déjà contre-passée par … Ouvrir ».
- **Dupliquer pour une nouvelle saisie** ouvre la saisie préremplie (journal, libellé, lignes), datée d'aujourd'hui et
  **sans pièce** : une pièce justifie une écriture, pas deux.
- **La palette F2** sur un champ « Compte » : les comptes du dossier d'abord (« utilisé 4 fois »), puis le plan général ;
  ↑ ↓, Entrée, Échap.
- Un défaut d'affichage commun, corrigé à la racine : un lien habillé en bouton (`a.action-principale`) n'était pas
  centré, ici comme à la clôture mensuelle et sur l'écran de TVA.

Hors du pas, et écrits : le choix du journal de la contre-passation (la maquette propose OD ; elle reste dans le journal
de l'écriture annulée, pour que la numérotation de chaque journal dise tout ce qui l'a touché) ; « Ctrl+N crée un compte
auxiliaire » (ouvrir un compte au plan est un paramétrage, que la saisie refuse pour ne pas créer de comptes jumeaux) ; la
recherche d'un compte par le nom du tiers (« 401 quinc »), faute de comptes auxiliaires au plan ; l'heure de saisie, que
l'écriture ne conserve pas.

### Les tests

`tests/test_fiche_d_ecriture.py`, 10 cas dont un sur PostgreSQL. **19 mutations : 19 tuées**, dont quatre après coup : la
TVA collectée nette dans les lignes du formulaire, le signalement d'une écriture qui aurait paru sur la fiche d'une autre,
l'ordre des comptes employés (que les données de démonstration, rangées dans l'ordre des numéros, ne départageaient pas),
et le refus d'un champ inconnu de l'attribut fiscal.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Saisie → « AC n° 3 » | « Écriture 2026/AC/000003 · SARL BATIMENT PLUS · journal AC · du 03/07/2026 · validée le 03/08/2026 par Rodrigue BIYA'A » |
| Bandeau | « Validée, non modifiable. » ; « La période de juillet 2026 n'est pas encore verrouillée. » |
| Historique | « date non conservée · Saisie en brouillon », « 03/08/2026 · Validée » |
| Signaler au réviseur | l'historique porte « Signalée au réviseur : Compte 622 : location d'engins ou sous-traitance ? » ; le réviseur reçoit « Écriture signalée : 2026/AC/000003 » |
| Contre-passer au 01/07/2026 | champ limité au 03/07 ; forcé : « la contre-passation serait datée du 01/07/2026, avant l'écriture … » |
| Au 10/08/2026 | lignes inversées « AC n° 4 pressenti » ; « La déclaration de TVA de 08/2026, en préparation, sera recalculée » ; crédit à reporter 500 500 → 231 000 FCFA |
| Créer la contre-passation | « Déjà contre-passée par 2026/AC/000004. Ouvrir 2026/AC/000004 » ; plus d'action « Contre-passer » |
| Dupliquer | « Dupliquée de AC n° 3 : vérifiez la date, et renseignez la pièce, qui n'est pas reprise » ; pièce vide, compte 622 repris |
| F2 sur un compte | 401, 4451 « utilisé 4 fois », 604, 622 ; « 52 », ↓, Entrée : 523 choisi, palette fermée |
| Téléphone (390 px) | aucun élément débordant hors des tableaux qui défilent |

### État à la fin du pas 110

**3 571 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (208 gestes sur 208). Contrat des écrans : 208 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 206 sur 211 (97 %).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une correction se voit avant de se faire, et une annulation ne vaut que si elle annule une fois, jusque dans la TVA.*

## Pas 111 — Relancer un adhérent de ce qui manque, déduit et non saisi

### Pourquoi

Vue F du parcours comptable, « Relance des pièces manquantes » (UC09 : « demander en un message ce qui manque, sur le canal
que l'adhérent lit »). Le produit savait lister les demandes de pièces, les rattacher, les classer, et **tracer** une
relance faite hors de la plateforme (pas 74) ; il savait prévenir l'adhérent d'une facture rectificative (pas 74). Il ne
savait pas :

- **déduire** ce qui manque au mois. La maquette le dit en note : « l'attente est déduite, pas saisie : mouvements bancaires
  sans pièce, séries habituelles du dossier, obligations du mois ». Le cabinet ne pouvait relancer que ce qu'un
  collaborateur avait pensé à demander ;
- **composer et envoyer** une relance : un message, les pièces cochées insérées, un modèle, des canaux, et la conséquence
  annoncée (« votre déclaration sera établie sans elles : c'est ce qui fait revenir les pièces ») ;
- montrer **l'historique** des relances d'un dossier, et si elles ont été lues.

### Où vit l'attente, et pourquoi là

Ce qui manque se lit chez quatre voisins : la collecte (pièces, demandes), la comptabilité (relevés importés, lignes non
rapprochées), les obligations (le mois) et la conformité (anomalies bloquantes). La collecte ne peut pas lire la
comptabilité ; **le pilotage lit tous les contextes** et construit déjà le plan de travail du comptable (pas 104). L'attente
se déduit donc dans `pilotage/domaine/pieces_manquantes.py`. Les **gestes**, eux, restent à la collecte : la demande et sa
relance y sont créées par sa surface publique (`demander_une_piece`, `tracer_une_relance`).

### Les six origines d'une attente

| Origine | Ce qui est relevé |
| --- | --- |
| Demande ouverte | une demande déjà émise, pas satisfaite, datée du mois ou avant |
| Relevé bancaire | un journal de banque mouvementé dans le mois, sans relevé **importé** couvrant sa fin |
| Mouvement sans pièce | une ligne de relevé du mois ni rapprochée d'une écriture, ni justifiée (ou justifiée « pièce demandée ») |
| Série habituelle | un émetteur présent dans au moins 3 des 3 mois précédents, absent du mois ; montant estimé : sa moyenne |
| Obligation du mois | une obligation du mois dont le référentiel dit quelle pièce elle appelle |
| Anomalie bloquante | une pièce du mois que le contrôle interdit de comptabiliser |

Chaque attente porte un **code stable** (`releve-bq`, `serie-eneo`, `rectificative-pj-2026-0013`). La demande qu'elle crée
s'appelle `ATT-2026-07-releve-bq` : relancer deux fois la même attente relance la **même** demande
(`demander_une_piece` est idempotente, et refuse un identifiant qui désignerait le dossier d'un autre). Une attente déduite
dont la demande existe déjà (même identifiant, ou rectificative de la même pièce) n'apparaît qu'une fois, portant sa
demande : l'adhérent ne reçoit pas deux fois la même exigence sous deux noms.

⚠️ L'anomalie bloquante n'est relevée, comme ailleurs dans le produit, que pour les factures que le moteur de conformité
sait contrôler : celles du jeu de démonstration, tant que l'extraction des pièces réelles n'alimente pas le moteur.

### Au référentiel (`pilotage/pieces_manquantes.yaml`)

Les origines actives, les seuils de la série, la pièce appelée par chaque obligation (vide par défaut : à arrêter par le
cabinet), la date limite (l'échéance de l'obligation de référence, la TVA, moins trois jours), les **canaux** (application,
courriel ; WhatsApp inactif, avec le motif repris de `messagerie/canaux.yaml`), deux **modèles** (amiable, ferme) et le nom du
cabinet sous la signature. Un réglage qui mentirait est refusé au chargement : un modèle dont la conclusion n'annonce pas
`{date_limite}`, un canal inactif sans motif, ou coché d'office.

⚠️ **Jamais une date limite passée.** Relancer juillet le 17 septembre en écrivant « avant le 12/08/2026 » ne ferait revenir
aucune pièce : la date est alors reportée de cinq jours après l'envoi, et l'écran dit que l'échéance est dépassée. Le défaut
s'est vu en écrivant les tests, avant que l'écran n'existe.

### Les deux routes, et ce qu'elles refusent

- `GET /pilotage/dossiers/{niu}/relance?mois=&attentes=&modele=` : ce qui manque, la sélection, la date limite, les canaux,
  les destinataires, l'historique, et **l'aperçu du message**, rendu par la même fonction que l'envoi.
- `POST /pilotage/dossiers/{niu}/relance` : pour chaque pièce cochée, la demande est créée si besoin, la relance est tracée
  **par canal**, l'adhérent est prévenu dans son espace (une entrée du journal par compte adhérent, annoncée par un
  abonnement) et par courriel (gabarit `piece.relance`, texte échappé), et l'envoi est inscrit au journal d'audit.

Refusés, **avant tout envoi** : une pièce hors de l'attente recalculée (la sélection du navigateur n'est jamais crue), un
canal inactif (avec son motif), un dossier sans compte adhérent actif (« envoyé » serait faux : relancer par téléphone,
puis tracer), et une pièce **déjà relancée aujourd'hui par le même canal** : un double clic ne fait pas partir deux messages,
et rien ne part si une seule pièce est dans ce cas.

**L'historique** relit les envois du journal : « Lu » quand chaque adhérent destinataire a lu la notification (sa position de
lecture dépasse l'entrée qui le concernait), « Non lu » sinon, « Envoyé » pour le courriel, « Tracée » pour une relance
consignée à la main.

**Une permission nouvelle, `RELANCER_PIECES`** : au comptable, au chargé de clientèle et au réviseur. La maquette fait
relancer le comptable, et `RELANCER_ADHERENT` ne convenait pas : elle ouvre aussi la relance des **honoraires impayés** du
cabinet, qui ne regarde pas le comptable.

### À l'écran (`/pieces/relancer`, « Relancer un adhérent » sous Pièces justificatives)

- « SARL BATIMENT PLUS · juillet 2026 · 2 pièces attendues · dernière relance le … ».
- **Ce qui manque** : case, pièce attendue, origine de l'attente, montant estimé, demandée le ; « Tout sélectionner ».
- **Le message** : le modèle, « Mettre à jour l'aperçu », l'aperçu tel qu'il partira, et ce qu'il faut savoir (notification
  dans l'espace de l'adhérent nommé, échéance dépassée ou date estimée).
- **Envoyer** : les canaux cochés d'office, WhatsApp grisé avec son motif, « Envoyer maintenant ».
- Cocher et choisir le modèle passent par un **formulaire ordinaire** qui recharge la page : l'écran ne compose rien. Les canaux
  sont des cases dans un formulaire d'action : soumis sans réinitialisation (leçon du pas 108), ils restent cochés après un
  refus.
- La clôture mensuelle (point « pièces attendues »), la déclaration de TVA (« relancer l'adhérent ») et la liste des pièces
  attendues mènent désormais ici.

Hors du pas, et écrits : « Programmer le 11/08 » (un envoi différé demande un ordonnanceur de messages, qui n'existe que pour la
souscription) ; WhatsApp (compte de la plateforme d'envoi non ouvert) ; l'accusé de lecture du courriel, que rien ne fournit ;
l'édition libre du message (le modèle est au référentiel, le message part tel que l'aperçu le montre).

### Les tests

`tests/test_relance_des_pieces.py`, 13 cas dont un sur PostgreSQL ; `tests/test_courriel.py` reçoit le contexte de référence
du nouveau gabarit. Les cas de routes figent l'horloge au 5 août, pour que l'échéance de juillet ne soit pas passée selon le
jour où la suite tourne. **25 mutations : 25 tuées**, dont trois après coup : des pièces vues hors des mois observés ne font
pas une série, l'origine « demande ouverte » se désactive, et un relevé importé cesse d'être attendu tandis que sa ligne non
rapprochée le devient.

### L'essai réel, dans un vrai navigateur

| Essai | Résultat |
| --- | --- |
| Un virement de juillet saisi, sans relevé importé ; Pièces attendues → « relancer un adhérent » | « SARL BATIMENT PLUS · juillet 2026 · 2 pièces attendues » |
| Ce qui manque | « Relevé bancaire du journal BQ, juillet 2026 · Banque mouvementée, relevé non reçu » ; « Facture rectificative SABLIÈRE DU MOUNGO (FAC-ID-003) · Anomalie bloquante · 498 465 · 03/08/2026 » |
| Aperçu, le 17 septembre | « Sans ces pièces avant le 22/09/2026… » ; « L'échéance du mois est passée : la date annoncée est reportée après l'envoi » |
| Décocher la rectificative, modèle ferme, mettre à jour | « Malgré nos précédentes demandes, il manque toujours pour juillet 2026 : Relevé bancaire… » |
| Canaux | Application et Courriel cochés ; « WhatsApp (inactif) » grisé, « Compte de la plateforme d'envoi non ouvert » |
| Envoyer maintenant | « Relance envoyée à 1 adhérent : 1 pièce demandée, dont 1 nouvelle. » ; historique « APPLICATION · Non lu », « COURRIEL · Envoyé » |
| L'adhérent | « Pièces manquantes pour juillet 2026 : 1 pièce(s) attendue(s) avant le 22/09/2026, faute de quoi votre déclaration sera établie sans elles. » ; il la lit : l'historique passe à « Lu » |
| Envoyer à nouveau | « déjà relancée aujourd'hui : … Rien n'est envoyé » ; les canaux restent cochés |
| Téléphone (390 px) | aucun élément débordant |

### État à la fin du pas 111

**3 585 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (210 gestes sur 210). Contrat des écrans : 210 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 208 sur 213 (97 %). **Les sept vues du parcours comptable sont confrontées.**

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Le cabinet ne relance bien que ce qu'il sait attendre, et une relance ne fait revenir les pièces que si elle dit ce qui arrive
sans elles.*

## Pas 112 — L'adhérent sait ce qu'on attend de lui, et il répond

### Pourquoi

Le parcours comptable est confronté (pas 111). Reste la maquette « Espace adhérent CGA » : six vues (A accès, B savoir ce
qu'on attend de moi, C mes justificatifs, D échéances et paiement, E mes documents, F réglages et états). Confrontée à
l'espace construit aux pas 81, 94 et 96 (une seule page `/mon-espace`) :

| Maquette | Avant le pas 112 |
| --- | --- |
| B · un bandeau qui ne dit qu'une chose : « Il manque 3 justificatifs, avant le 12 août », ou « Votre dossier de juillet est complet » | rien : les demandes ouvertes, plus bas, sans rien dire du mois ; un adhérent sans demande ne savait pas si son dossier était complet ou si personne ne l'avait regardé |
| B · « Votre mois de juillet » : justificatifs envoyés, achats enregistrés, « montants indicatifs » | rien |
| C · répondre à une demande : « Je l'aurai la semaine prochaine », « Je n'ai pas ce document », un message | rien : l'adhérent lisait la demande et appelait le cabinet |
| C · une facture refusée dit à qui s'adresser : le fournisseur | la demande, telle quelle |
| C · mes justificatifs d'un mois, par statut, cherchés par fournisseur ; « Reçu par le cabinet » | les vingt dernières pièces, avec l'état interne du traitement (« Lue », « Rapprochée ») |
| F · l'état vide prescriptif : « Aucun justificatif pour août… Voir le mois de juillet » | « Aucune pièce reçue pour l'instant » |

Le pas construit **B et C**, et l'état vide de F. Les vues A (accès par téléphone), D (paiement), E (documents du cabinet,
fiche de l'entreprise) et le reste de F attendent des décisions ou des pièces qui n'existent pas : elles sont écrites en
question ouverte (**Q29**), pas simulées.

### Le bandeau du mois : quatre états, et « complet » seulement s'il est vrai

`GET /pilotage/dossiers/{niu}/mon-mois` (`LIRE_DOSSIER`). Le mois observé est **le mois précédent** : c'est sa déclaration
que le cabinet prépare. Le bandeau croise quatre contextes (demandes et pièces de la collecte, attentes déduites du pas 111,
verrou des mois revus de la comptabilité) : il vit donc **au pilotage**, qui lit tout et n'est lu par personne.

| État | Quand | Ce que lit l'adhérent |
| --- | --- | --- |
| À envoyer | au moins une demande ouverte, de n'importe quel mois | « Il manque 3 justificatifs » ; « Envoyez-les avant le 12/08/2026 » (la date **la plus proche**), ou « La date prévue est passée : envoyez-les dès que possible », ou sans date |
| Le cabinet vérifie | aucune demande, mais une attente déduite que le cabinet n'a pas encore demandée | « Le cabinet vérifie votre mois de juillet 2026. Il vous écrira s'il lui manque une pièce. » |
| Aucun justificatif | aucune demande, aucune attente, aucune pièce du mois | « Aucun justificatif pour juillet 2026. Si vous avez acheté ou vendu en juillet 2026, envoyez vos factures » |
| Complet | aucune demande, aucune attente, des pièces reçues | « Votre dossier de juillet 2026 est complet. Le cabinet prépare votre déclaration. » |

⚠️ **Les attentes déduites ne sont pas montrées à l'adhérent**, seulement comptées. Tant que le cabinet ne les a pas
demandées, ce sont des présomptions (le comptable sait peut-être que la série de factures s'arrête). Mais elles
**interdisent de dire « complet »**.

⚠️ **Un mois sans aucune pièce n'est pas « complet »** : l'annoncer à l'adhérent qui a oublié d'envoyer ses factures est
l'erreur la plus coûteuse de l'écran.

⚠️ **Les achats du mois ne sont rendus que pour un mois verrouillé par la revue** (pas 107), avec la date du verrou
(« Montants indicatifs, arrêtés au 04/08/2026 »). Le rôle ADHÉRENT « ne voit pas la comptabilité tant qu'elle est en cours
d'établissement » : un montant en cours de saisie, lu comme définitif, fonde une décision de trésorerie sur un brouillon.
Sinon : « après la revue du mois ». Les écritures en brouillon ne comptent pas, un avoir se déduit.

Les mots sont au référentiel (`pilotage/espace_adherent.yaml`). Refusés au chargement : un bandeau « à envoyer » qui tairait
`{date_limite}`, un bandeau qui citerait `{date_limite}` là où il n'y en a pas, une valeur que l'écran ne connaît pas (un
`{moi}` mal orthographié partirait tel quel sur le téléphone), et « de {mois} » (voir l'essai réel).

### La réponse au cabinet, qui ne ferme jamais la demande

`POST /collecte/demandes/{identifiant}/reponse`, avec `PLUS_TARD`, `INTROUVABLE` ou `MESSAGE` et un message facultatif. La
demande garde **toutes** ses réponses, datées et nommées (« il avait dit la semaine prochaine, il y a trois semaines » est une
information pour la relance suivante).

- **« Plus tard » ne fait pas choisir une date** : le référentiel (`collecte/reponses_adherent.yaml`) dit ce que « la semaine
  prochaine » veut dire (sept jours), et le cabinet lit un jour annoncé.
- **Une réponse ne ferme jamais la demande.** « Je n'ai pas ce document » ne dit pas que la pièce n'existe pas. C'est le cabinet
  qui classe sans suite, avec son motif (pas 74), ou cherche ailleurs.
- **Refusés** : un message vide (422, dès la requête), une réponse à une demande satisfaite ou classée (409, « le cabinet
  n'attend plus cette pièce »), une réponse datée d'avant la demande, et **la même réponse le même jour** (409 : sur un
  réseau lent, l'adhérent appuie deux fois, et le cabinet recevrait deux avis). La même réponse le lendemain, ou une autre
  précision le même jour, passent.
- **Une permission nouvelle, `REPONDRE_AU_CABINET`, à l'adhérent seul.** Un collaborateur qui répondrait à sa place écrirait
  au dossier une parole que l'adhérent n'a pas dite, et la relance suivante s'appuierait dessus. Un adhérent d'un autre
  dossier reçoit 404.
- **Le cabinet est prévenu** : l'entrée `collecte.demande_repondue` est annoncée, par un abonnement, à ceux qui relancent les
  pièces du dossier (« Réponse de l'adhérent : … », « Jean-Pierre NKOA (M081234567890P) : Je l'aurai la semaine prochaine ·
  annoncée pour le 24/09/2026 »). **Une seule rédaction** de la réponse (`texte_de_la_reponse`) sert l'avis, l'accueil de
  l'adhérent et l'écran de relance.
- La relance des pièces (pas 111) et les pièces attendues montrent la réponse : on ne relance pas celui qui a dit « la semaine
  prochaine » avant-hier.

⚠️ Un garde-fou existant a refusé la première écriture : l'entrée portait la clé `motif`, et **aucun gabarit d'avis ne lit une
clé `motif`** (souvent une note interne, pas 94). La clé s'appelle `piece`.

### Mes justificatifs : le statut de l'adhérent n'est pas l'état du traitement

`GET /collecte/dossiers/{entreprise}/justificatifs?mois=&statut=&recherche=` (`LIRE_PIECE`). Quatre statuts, un seul demande un
geste :

| Statut | Quand | Lu |
| --- | --- | --- |
| À corriger | une demande de rectificative ouverte vise la pièce, **quel que soit son état** | « À corriger », avec ce qui est à corriger et la consigne |
| Reçu | reçue, lue ou rapprochée | « Reçu par le cabinet », en vert (vue B, note 2) |
| Enregistré | comptabilisée | « Enregistré par le cabinet » |
| Classé | gardée au dossier sans écriture | « Gardé au dossier » : pas de corbeille où perdre une facture (vue C, note 4) |

- **Le mois d'une pièce est celui du document**, sinon celui de la réception : une facture de juillet envoyée le 3 août est
  une pièce de juillet.
- **Le compte par statut porte sur le mois entier, avant filtre** : « 7 justificatifs envoyés · 2 à corriger · 2 reçus par le
  cabinet · 3 enregistrés par le cabinet » ne change pas quand on filtre. La liste vient triée : à corriger d'abord.
- La recherche lit le fournisseur, le numéro de facture **et le nom du fichier envoyé**, seul repère d'une pièce pas encore lue.
- Sans mois demandé : le mois en cours. Vide, l'écran propose le mois précédent qui porte des pièces.

### Un défaut du pas 111, corrigé en passant

Le libellé d'une anomalie bloquante, qui part **dans le message envoyé à l'adhérent**, portait le code de la règle : « Facture
rectificative SABLIÈRE DU MOUNGO (FAC-ID-003) ». La maquette de l'espace adhérent l'interdit (« ni FAC-ID-003, ni CGI art.
150-5 »). Le libellé devient « Facture rectificative de SABLIÈRE DU MOUNGO (facture F-2026-0424) », et la règle passe dans un
champ `regle`, lu par le seul cabinet (« · règle FAC-ID-003 » sur l'écran de relance).

### À l'écran

- **`/mon-espace`** : le bandeau (couleur **et** glyphe selon l'état, « ＋ Envoyer un justificatif »), « Ce qu'on attend de
  vous » (une facture à corriger dit « Facture à corriger » puis « Ce que vous devez faire : demandez à votre fournisseur une
  nouvelle facture corrigée, puis envoyez-la ici » ; la date passée en rouge ; la réponse déjà envoyée ; deux boutons et
  « Écrire un message au cabinet » replié ; « Votre réponse arrive directement dans le dossier, sans passer par WhatsApp »),
  l'envoi d'un justificatif, les nouvelles, « Votre mois », les échéances, les cinq derniers envois et « Tous mes
  justificatifs, mois par mois », la fiche du dossier.
- **`/mon-espace/justificatifs`** : recherche, mois, statut par un formulaire ordinaire (sans JavaScript, le lien se
  partage), le compte du mois, la liste, l'état vide prescriptif, et « Impossible d'afficher vos justificatifs… Réessayer »
  si la lecture échoue.
- **Deux onglets** en bas de l'écran du téléphone, Accueil et Justificatifs. La maquette en porte cinq : **seuls les écrans
  construits ont un onglet**, un onglet vers une page vide ferait croire à une panne.
- Si le mois ne se lit pas, l'accueil retombe sur la liste des demandes du pas 81 : l'adhérent garde l'essentiel.

### Les tests

`tests/test_espace_adherent.py`, 24 cas : la réponse (message vide, « plus tard » sans jour à venir, date sur une réponse qui
n'en porte pas, demande close, double appui, autre dossier, semaine du référentiel), les réglages, le statut et le mois d'une
pièce, les comptes avant filtre, le bandeau (quatre états, date la plus proche, date passée, élision) et les routes (accueil,
réponse et avis au cabinet, refus du collaborateur, demande classée, justificatifs, achats d'un seul mois revu, brouillon
exclu). `tests/test_relance_des_pieces.py` suit le nouveau libellé.

**44 mutations : 43 tuées.** Sept survivaient au premier passage et ont fait écrire un test : le double appui qui ne compare
plus le jour, ou plus le message ; le filtre de statut ignoré ; l'autre dossier au cas d'usage ; les sept jours écrits en dur ;
les brouillons comptés dans les achats ; la date de la réponse à l'écran de relance. **Le dernier survivant est équivalent** :
retirer le filtre « attentes pas encore demandées » ne change rien aujourd'hui, parce qu'une attente rattachée suppose une
demande ouverte, et l'état est déjà « à envoyer ». Le filtre est gardé, et le code dit pourquoi.

### L'essai réel, dans un vrai navigateur (le 17 septembre, téléphone de 390 px)

| Essai | Résultat |
| --- | --- |
| Jean-Pierre NKOA ouvre son espace | bandeau « Il manque 3 justificatifs · La date prévue est passée : envoyez-les dès que possible, le cabinet vous attend. » |
| Ce qu'on attend | « Facture à corriger · Facture rectificative … SABLIÈRE DU MOUNGO · Attendue pour le 12/08/2026 : la date est passée · Ce que vous devez faire : … » |
| « Je l'aurai la semaine prochaine » | « Votre réponse est arrivée au cabinet : il attend la pièce pour le 24/09/2026. » ; après rechargement, « Votre réponse du 17/09/2026 : Je l'aurai la semaine prochaine · annoncée pour le 24/09/2026 » |
| Un message, puis « Envoyer le message » à vide | arrivé ; puis « Écrivez votre message avant de l'envoyer. » |
| Votre mois | « Votre mois d'août 2026 · Justificatifs envoyés 1 · Achats enregistrés : après la revue du mois » |
| Onglet Justificatifs | « Aucun justificatif pour septembre 2026 · Dès que vous recevez une facture, prenez-la en photo… · Envoyer le premier · Voir le mois d'août 2026 » |
| Juillet | « 7 justificatifs envoyés · 2 à corriger · 2 reçus par le cabinet · 3 enregistrés par le cabinet » ; à corriger en tête |
| Statut « À corriger », puis recherche « zzz » | MENUISERIE BAFOUSSAM et SABLIÈRE DU MOUNGO, le compte inchangé ; « Aucun justificatif de ce mois ne correspond à votre recherche. Tout afficher » |
| Le comptable | deux avis « Réponse de l'adhérent » ; relance : « Facture rectificative de SABLIÈRE DU MOUNGO (facture F-2026-0424) · règle FAC-ID-003 » et « L'adhérent a répondu le 17/09/2026 : … » ; pièces attendues : « Le 17/09/2026, l'adhérent l'aura plus tard (annoncée pour le 24/09/2026) » |
| Débordements à 390 px | aucun, sur les deux pages |

**Deux défauts de langue, trouvés à l'essai et corrigés** : « Votre mois de août 2026 » (l'élision manquait, aussi pour avril
et octobre : le référentiel cite désormais `{de_mois}`, et refuse « de {mois} ») et « 2 reçu par le cabinet » (l'accord).

### État à la fin du pas 112

**3 611 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (214 gestes sur 214). Contrat des écrans : 214 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 212 sur 217 (97 %). **Vues B et C de l'espace adhérent confrontées** ; A, D, E et F
restent, avec la question Q29.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un adhérent qui ne sait pas s'il doit quelque chose appelle le cabinet ; celui qui lit « complet » quand c'est vrai, et
« il manque » quand il manque, envoie ses pièces.*

## Pas 113 — L'adhérent comprend ce qu'il doit, et prouve qu'il a payé

### Pourquoi

Vue D de la maquette « Espace adhérent CGA », « Échéances et paiement » (UC08, UC09 : « comprendre ce que je dois, payer
par monnaie électronique, garder la preuve »). Confrontée à la liste « Mes échéances » du pas 81 :

| Maquette | Avant le pas 113 |
| --- | --- |
| « Impôt trimestriel · En retard de 24 jours · 3e trimestre 2026 » | le libellé du catalogue (« Impôt général synthétique — versement trimestriel ») et le retard, sans période lisible |
| « De quoi s'agit-il ? », en langage courant, et ce qu'entraîne un retard | rien |
| « Trimestre précédent : payé le 14 avril » ; « Prochaine échéance : 15 novembre » | rien |
| « J'ai déjà payé — envoyer la preuve » (note 5 : « le règlement au guichet : l'adhérent photographie la quittance, elle rejoint le dossier ») | rien : une quittance partait comme une pièce quelconque, sans dire ce qu'elle réglait |
| « Payer maintenant » par MTN Mobile Money ou Orange Money, frais annoncés, repli USSD | rien, **et rien à ce pas** |

**Le paiement en ligne n'est pas construit**, volontairement : la maquette elle-même demande au cabinet si l'encaissement
passe par un agrégateur ou si l'adhérent paie directement l'administration (question **Q29**). Un parcours de paiement faux
engage le cabinet ; un bouton qui ne mène nulle part est pire qu'une phrase vraie. L'écran dit : « Le paiement en ligne
n'est pas encore ouvert. Réglez au guichet, puis envoyez ici la quittance. »

### Une carte par obligation, et pourquoi pas une par période

`GET /obligations/dossiers/{entreprise}/mes-echeances` (`LIRE_DOSSIER`). **Le premier essai a rendu soixante-dix lignes
« en retard »** sur le dossier de démonstration, qui ne porte aucun dépôt de 2025 : douze mois de CNPS, de TVA, d'acomptes,
de retenues. Une liste pareille ne se lit pas, et l'adhérent n'y trouve pas quoi faire en premier. Pour chaque obligation :

| Carte | Quand |
| --- | --- |
| **En retard** | la plus ancienne période échue, sans preuve : c'est elle qu'on règle d'abord ; « et 19 autres périodes en retard » |
| **Preuve envoyée** | une carte par période dont la quittance est envoyée : « le cabinet la vérifie » |
| **À venir** | s'il n'y a rien en retard : la prochaine, dans l'horizon (60 jours) |
| **Déposée** | le dernier dépôt de l'obligation, pendant 90 jours : l'effet visible du travail du cabinet |

Ordre : ce qui demande un geste d'abord (les retards les plus anciens en tête), puis les preuves, puis ce qui vient, puis
ce qui est fait. La fiche d'une carte donne la **période lisible** (« juillet 2026 », « 3e trimestre 2026 », « année 2025 »),
le montant estimé s'il existe (sinon « le cabinet vous indique le montant », jamais zéro), la période précédente (déposée
le…, avec le montant de l'accusé), la prochaine échéance et la preuve envoyée.

⚠️ **Un défaut trouvé à l'essai réel** : « Prochaine échéance : 15 mars 2025 » sur une carte en retard depuis février 2025.
La prochaine échéance était la période suivante, elle-même en retard. C'est désormais la prochaine **à venir**, et une
période déjà déposée est sautée.

### « De quoi s'agit-il ? » : au référentiel, et à valider

`obligations/explications_adherent.yaml` : pour chacune des sept obligations du catalogue, un titre courant (« Impôt
trimestriel », « Cotisations sociales CNPS », « Déclaration annuelle »), ce qu'elle est et ce qu'entraîne un retard, sans
article de loi. Ces textes sont **une proposition** rédigée à partir de la maquette : le fichier porte `statut: A_VALIDER`,
et l'écran dit « Explication en cours de validation par le cabinet ». Passer à `VALIDE` exige de nommer qui a validé (refusé
sans nom) : une phrase fausse sur un impôt, lue par un adhérent, devient une décision. Un test vérifie que le fichier
n'explique que des obligations du catalogue, et toutes.

### La preuve de paiement, qui ne déclare rien

`POST /obligations/dossiers/{entreprise}/preuves-de-paiement` (`DEPOSER_PIECE`), avec l'obligation, sa période et la pièce.
À l'écran, un seul geste : l'adhérent choisit la photo ou le PDF, et **deux temps** se suivent. La quittance est d'abord
déposée comme toute pièce, par les mêmes contrôles (type lu dans les octets, taille, empreinte), avec le type
`QUITTANCE_IMPOT` ; puis la route dit ce qu'elle règle. Le dépôt en deux étapes reste une seule implémentation
(`deposerFichierEtPiece` reçoit ce qui suit la réception) : recopier son corps aurait fait diverger les contrôles.

- **Refusés** : une obligation absente de l'échéancier du dossier (404, avec les périodes à régler), une obligation déjà
  déposée (409, « il n'y a rien à prouver »), une pièce inconnue ou d'un autre dossier (404, la même réponse), la même pièce
  déjà envoyée pour la même échéance (409). Une **autre** quittance pour la même échéance est reçue : la première était
  peut-être illisible.
- Si le second temps est refusé, la pièce reste reçue, et l'adhérent le lit (« Votre document est bien arrivé au cabinet
  (pièce …), mais il n'a pas pu être rattaché à cette échéance : … ») : rien ne se perd.
- **La preuve ne déclare pas l'obligation.** Elle reste « à faire » au calendrier du cabinet tant qu'un collaborateur
  habilité, en session renforcée (pas 59), n'a pas consigné l'accusé. L'adhérent lit « le cabinet la vérifie », pas
  « réglé » : une quittance d'un autre trimestre ne règle rien.
- Les preuves se relisent **au journal d'audit** (`obligations.preuve_de_paiement_recue`), qui date et nomme l'envoi : un
  second registre divergerait.
- **Le cabinet est prévenu** : un abonnement annonce la preuve à ceux qui consignent les dépôts du dossier
  (`DEPOSER_DECLARATION`) : « Preuve de paiement reçue : Cotisations sociales CNPS, janvier 2025 », « … envoie la pièce PJ-….
  La vérifier, puis consigner le dépôt avec elle en pièce jointe. »
- **La page des obligations** montre un panneau « Preuves de paiement envoyées par l'adhérent », et le formulaire « Constater
  un dépôt » reçoit enfin le champ **« Pièce jointe »** : le backend l'acceptait depuis le pas 59, l'écran ne l'envoyait pas.
  Une fois le dépôt consigné, la carte de l'adhérent passe à « Déposée le … », avec le montant de l'accusé.

⚠️ Le panneau ne lie pas la pièce à `/pieces/[reference]` : cette fiche est désignée par la référence d'une facture, et une
quittance n'en a pas. Il renvoie à la boîte de réception.

### À l'écran

- **`/mon-espace/echeances`**, troisième onglet de l'espace : les cartes, puis la fiche (`?echeance=CODE|début|fin`) avec son
  bandeau (retard, preuve, dépôt), « De quoi s'agit-il ? », les faits (période précédente, prochaine échéance, preuve), et
  « Vous avez réglé ? ».
- L'accueil garde sa liste et mène à « Toutes mes échéances, et envoyer une preuve de paiement ».
- Après l'envoi, la fiche passe en « Preuve envoyée le 17/09/2026 : le cabinet la vérifie » et le formulaire disparaît :
  c'est le bandeau qui confirme (leçon du pas 110, un geste réussi peut démonter son composant).

### Les tests

`tests/test_echeances_adherent.py`, 13 cas : la période lisible, la carte par obligation (la plus ancienne en retard et le
nombre des autres, la prochaine à venir qui saute les dépôts, l'horizon, la preuve qui garde sa carte, le dernier dépôt seul
et son montant, l'ordre), les réglages (explication en double, validation sans nom, fichier livré à valider et aligné sur
le catalogue) et les routes (lecture, preuve puis avis au réviseur puis dépôt consigné avec la pièce jointe, et les refus).

**30 mutations : 29 tuées.** Quatre survivaient au premier passage et ont fait écrire un test : l'horizon ignoré, la
prochaine échéance qui ne saute plus les dépôts, une seconde quittance refusée pour la même échéance ; la quatrième est
**équivalente** (le filtre sur l'action lue au journal : c'est aujourd'hui la seule écrite sur ce type d'objet), et le code
le dit.

### L'essai réel, dans un vrai navigateur (le 17 septembre, téléphone de 390 px)

| Essai | Résultat |
| --- | --- |
| Jean-Pierre NKOA, onglet Échéances | six cartes : « Cotisations sociales CNPS · janvier 2025 · En retard de 579 jours · et 19 autres périodes en retard », …, « Patente · année 2025 · … et 1 autre période en retard », « Déclaration annuelle · année 2025 · En retard de 185 jours » |
| La fiche CNPS | « Le cabinet vous indique le montant. Était à régler le 15 février 2025 » ; « 19 autres périodes… Commencez par celle-ci, la plus ancienne » ; « De quoi s'agit-il ? » ; « Explication en cours de validation par le cabinet » ; « Prochaine échéance : 15 octobre 2026 » ; « Le paiement en ligne n'est pas encore ouvert… » |
| Une quittance PDF, « J'ai déjà payé : envoyer la preuve » | « Preuve envoyée le 17/09/2026 : le cabinet la vérifie » ; « Preuve envoyée : le 17/09/2026 (pièce PJ-M08123-…) » |
| Mes justificatifs, septembre | « quittance.pdf · Reçu par le cabinet » |
| Le réviseur | l'avis « Preuve de paiement reçue : Cotisations sociales CNPS, janvier 2025 » ; sur les obligations, « Cotisations sociales CNPS · janvier 2025 · pièce PJ-…, envoyée le 17/09/2026 · boîte de réception » |
| Débordements à 390 px | aucun |

### État à la fin du pas 113

**3 625 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (216 gestes sur 216). Contrat des écrans : 216 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 214 sur 219 (97 %). **Vues B, C et D (hors paiement) de l'espace adhérent
confrontées** ; A, E et F restent, avec la question Q29 (six points).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un adhérent qui comprend ce qu'il doit règle au guichet ; celui qui peut le prouver d'une photo donne au cabinet de quoi
consigner le dépôt.*

## Pas 114 — Mon entreprise, mon interlocuteur, mes documents

### Pourquoi

Vue E de la maquette « Espace adhérent CGA », « Mes documents » et « Mon entreprise » (UC10 : « récupérer une attestation,
une déclaration, un reçu, et l'envoyer à un tiers »). Confrontée à la fiche de l'accueil (pas 81) :

| Maquette | Avant le pas 114 |
| --- | --- |
| Forme « Établissement », activité, NIU, RCCM, adresse, centre des impôts | NIU, « Réel » ou « Impôt libératoire », « CDI » en sigle |
| « Votre régime fiscal : Impôt Général Synthétique, depuis 2019 », et une phrase qui l'explique | le code du régime |
| « Votre interlocutrice : Aïcha MBALLA, 699 114 208 · Appeler · Écrire » | rien : l'adhérent ne savait pas qui appeler |
| « Signaler un changement : adresse, gérant, activité, numéro de téléphone : le cabinet fait les démarches » | rien |
| « Vos documents » : attestations, reçus de dépôt, déclarations, états financiers, contrat de mission | rien |
| « Votre régime va changer » (vos ventes dépassent le plafond) | rien, **et rien à ce pas** (voir plus bas) |

### Mon entreprise : lire, appeler, signaler ; jamais modifier

`GET /portefeuille/entreprises/{niu}/mon-entreprise` (`LIRE_DOSSIER`) rend la fiche **rédigée** : la forme, le centre et le
régime en toutes lettres (« Société à responsabilité limitée », « Centre divisionnaire des impôts », « Régime du réel, depuis
le 01/01/2023 » avec son explication), l'adhésion et son numéro, les dirigeants **en fonction** (un ancien gérant ou un
cogérant nommé pour l'an prochain n'y figure pas), l'interlocuteur et les derniers signalements.

Les mots sont au référentiel (`portefeuille/espace_adherent.yaml`), **à valider** comme ceux des échéances : la nomenclature
des régimes elle-même attend le fiscaliste (question Q12). Sans fichier, les codes s'affichent, jamais une traduction
inventée. **Un test a trouvé une forme juridique oubliée** dans le fichier livré (`PERSONNE_PHYSIQUE`, « Entreprise
individuelle ») : il vérifie désormais que le fichier nomme toutes les formes, tous les centres et tous les régimes.

**L'interlocuteur** est choisi parmi les habilitations actives du dossier, sur un compte actif : le chargé de clientèle, sinon
le comptable ; à rôle égal, une habilitation **nommée sur le dossier** avant une habilitation transverse, puis la plus
récente. Personne : « le cabinet n'a pas encore désigné votre interlocuteur », jamais un nom inventé. « Appeler » n'apparaît
que si le compte porte un téléphone (dans la démonstration, Patricia MOUKOURI n'en a pas : seul « Écrire » s'affiche, et la
question est posée en Q29).

**Signaler un changement** : `POST /portefeuille/entreprises/{niu}/signalements`, avec la nature et quelques mots.

- **Rien ne change au dossier.** « L'adhérent ne modifie jamais lui-même son NIU, son RCCM ou son régime : il signale un
  changement, le cabinet instruit » (note 2). Une adresse change le centre, donc les échéances ; un régime est un statut daté
  aux conséquences fiscales. Le signalement est une parole datée au journal, et le message de retour le dit : « votre dossier
  n'est pas encore modifié ».
- **Une permission nouvelle, `SIGNALER_UN_CHANGEMENT`, à l'adhérent seul** : un collaborateur qui apprend un changement
  l'instruit directement, il ne se l'annonce pas à lui-même.
- Chaque nature porte son aide, du référentiel : « Une nouvelle adresse peut changer votre centre des impôts, donc vos dates
  limites : le cabinet vérifie. »
- **Refusés** : le même signalement le même jour par le même compte (409, un double appui), un message vide (422), un
  collaborateur (403), un autre dossier (404).
- **Le chargé de clientèle est prévenu** (abonnement `RELANCER_ADHERENT` sur le dossier) : « Changement signalé : Adresse, SARL
  BATIMENT PLUS ». L'essai réel a fait reformuler le texte, dont la ponctuation donnait « … octobre. ». ».
- ⚠️ **Deux signalements de la même seconde** se rangeaient dans le mauvais ordre : le tri sur l'horodatage seul gardait le
  plus ancien en tête. Le rang au journal départage désormais (vu en test, horloge figée).

### Mes documents : des reçus de dépôt, pas des attestations

La maquette montre des attestations « émises par le cabinet », « dont une banque peut vérifier l'authenticité ». **La
plateforme n'en émet aucune**, et ce pas n'en simule pas : une attestation suppose un modèle, un signataire, une durée de
validité et un moyen de vérification arrêtés par le cabinet (Q29, point 7). Un faux document officiel serait pire que pas de
document.

Ce qui existe, et qui est vrai, ce sont **les accusés de dépôt** consignés au dossier. `GET
/obligations/dossiers/{entreprise}/mes-documents` (`LIRE_DOSSIER`) les rend, du seul dossier (la référence du document porte le
NIU), avec le titre courant de l'obligation (pas 113), la période lisible, le guichet (« Impôts (DGI) », « CNPS »), le numéro,
la date opposable, le montant. À l'écran, chaque reçu s'imprime ou s'enregistre en PDF par le navigateur (les onglets et le
bouton disparaissent à l'impression), et **dit ce qu'il est** : « Relevé de l'accusé consigné par le cabinet à votre dossier.
Il ne remplace pas l'accusé délivré par l'administration », et si un justificatif est archivé ou non. Une mention renvoie les
attestations à l'interlocuteur.

**« Votre régime va changer »** n'est pas construit : la veille des seuils lit la comptabilité (`LIRE_COMPTABILITE`), que
l'adhérent ne détient pas, et la maquette le lie à un rendez-vous et à un plan en quatre étapes que le cabinet n'a pas arrêté.

### Les cinq onglets

Accueil, Justificatifs, Échéances, **Documents**, **Entreprise** : ceux de la maquette. Ils tiennent sur un téléphone de
360 px (le libellé rétrécit plutôt que de déborder). L'accueil mène aussi à « Mon entreprise, mon interlocuteur, signaler un
changement ».

### Les tests

`tests/test_mon_entreprise.py`, 14 cas : l'interlocuteur (rôle, nommé avant transverse, plus récent, personne, compte suspendu
qui passe la main), les réglages (natures de la maquette toujours présentes, doublons, validation sans nom, fichier livré
complet), le double appui, les routes (fiche, dirigeants en fonction, signalement et avis, refus, signalements les plus
récents et codes sans fichier) et les documents (les accusés du seul dossier, un dépôt d'un autre dossier exclu).

**28 mutations : 27 tuées.** Cinq survivaient au premier passage ; quatre ont fait écrire un test (le compte suspendu, la
portée nommée, les dirigeants hors fonction, le dépôt d'un autre dossier). La cinquième est **équivalente**, comme au pas 113 :
le filtre sur l'action lue au journal, seule écrite aujourd'hui sur ce type d'objet ; le code le dit.

### L'essai réel, dans un vrai navigateur (le 17 septembre, téléphone de 360 px)

Le backend de démonstration est lancé avec un dépôt CNPS de juillet consigné par le réviseur, en session renforcée par le lien
de confirmation et le code, comme dans les tests.

| Essai | Résultat |
| --- | --- |
| Les onglets | « Accueil · Justificatifs · Échéances · Documents · Entreprise », aucun débordement |
| Mon entreprise | « Société à responsabilité limitée », « Centre divisionnaire des impôts », « Gérant : NKOA Jean-Pierre », « Adhésion au CGA : n° ADH-2022-014, depuis le 01/06/2022 », « Régime du réel, depuis le 01/01/2023 », l'explication et « en cours de validation », « Votre chargé(e) de clientèle : Patricia MOUKOURI · Écrire » |
| Signaler : Adresse | l'aide s'affiche ; « Changement signalé (adresse). Le cabinet l'instruit et vous contacte : votre dossier n'est pas encore modifié. » ; « Adresse · reçu par le cabinet le 17/09/2026 » |
| Le même, à nouveau | « ce changement a déjà été signalé aujourd'hui : le cabinet l'a reçu. » |
| La chargée de clientèle | l'avis « Changement signalé : Adresse, SARL BATIMENT PLUS » |
| Mes documents | « Reçu de dépôt · Cotisations sociales CNPS · juillet 2026 · déposé le 12/08/2026 · 184 500 FCFA » ; la mention sur les attestations |
| Le reçu | entreprise et NIU, déclaration, guichet CNPS, n° CNPS-2026-DIPE-00418, date, montant, « Il ne remplace pas l'accusé délivré par l'administration ; aucun justificatif n'est encore archivé » |
| À l'impression | onglets et bouton masqués |

### État à la fin du pas 114

**3 640 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (219 gestes sur 219). Contrat des écrans : 219 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 217 sur 222 (97 %). **Vues B, C, D (hors paiement) et E (hors attestations) de
l'espace adhérent confrontées** ; A et F restent, avec la question Q29 (huit points).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un adhérent sait qui appeler, dit ce qui change sans rien casser, et garde la trace de ce qui a été déposé en son nom.*

## Pas 115 — L'adhérent est prévenu avant ses échéances, et sait quand il est hors ligne

### Pourquoi

Vue F de la maquette « Espace adhérent CGA », « Réglages et états » (UC12 et les états obligatoires : hors ligne, erreur,
vide). Confrontée à l'espace existant :

| Maquette | Avant le pas 115 |
| --- | --- |
| « Rappels avant les échéances · 7 jours et 2 jours avant » | **rien n'envoyait de rappel à l'adhérent** : le cabinet relançait les retards (pas 55), une fois le mal fait |
| « Recevoir aussi par WhatsApp · Au 699 902 184 » | rien |
| « Envoyer uniquement en Wi-Fi », « Qualité des photos », « Langue », « Code secret et empreinte » | rien |
| « Hors ligne · 2 envois en attente · Voir », en tête de l'accueil | la file des dépôts sans réseau (pas 96), visible seulement sous le formulaire de dépôt |
| états vides prescriptifs, erreurs avec action et repli | construits aux pas 112 à 114, page par page |

### Seuls les réglages qui commandent quelque chose

Un interrupteur qui ne commande rien est pire qu'une absence : l'adhérent croit avoir économisé ses données, et ne l'a pas
fait. La page « Réglages » (`/mon-espace/reglages`, depuis l'en-tête de l'accueil) porte donc :

| Réglage de la maquette | Au pas 115 |
| --- | --- |
| Rappels avant les échéances | **construit, avec le travail qui les envoie** |
| Recevoir aussi par WhatsApp | affiché **grisé**, avec son motif : aucun envoi WhatsApp n'existe |
| Envoyer uniquement en Wi-Fi | non : le navigateur ne dit pas de façon fiable le type de réseau |
| Qualité des photos | non : aucune réduction d'image n'est faite avant l'envoi |
| Langue | non : l'espace adhérent n'est rédigé qu'en français |
| Code secret et empreinte | non : l'accès se fait par mot de passe (vue A, question Q29) |

### Le réglage des rappels

`GET` et `POST /obligations/dossiers/{entreprise}/mes-rappels`, **`REGLER_SES_RAPPELS`, à l'adhérent seul** : un collaborateur qui
couperait les rappels d'un adhérent le priverait d'un avertissement qu'il a choisi. Le réglage est **au compte** (un adhérent
qui suit deux entreprises choisit une fois), et c'est **une entrée datée du journal** : la dernière fait foi, et le journal
répond à « qui a coupé les rappels, et quand », la première question le jour où un adhérent dit n'avoir jamais été prévenu.

- Tant que l'adhérent n'a rien réglé, le défaut du référentiel vaut (`obligations/rappels_adherent.yaml` : actifs, 7 et 2
  jours), et l'écran le dit : « Réglage proposé par le cabinet : vous ne l'avez pas encore modifié ».
- **Refusés** : des rappels actifs sans aucun moment (« choisissez au moins un moment pour être prévenu, ou désactivez les
  rappels »), un moment non proposé, un collaborateur (403), un autre dossier (404).
- **POST et non PUT** : le projet n'emploie aucune route PUT, ni le client `appeler` ni l'outil de contrat ; le geste reste
  idempotent.
- Les cases sont soumises **sans réinitialisation** (leçon du pas 108) : après le refus, l'écran montre exactement ce qui
  repartira.

### Le travail qui envoie les rappels

`rappels-d-echeance`, inscrit à l'ordonnanceur **après** les travaux de la souscription (un rappel à J-7 n'est pas à la
minute, et il ne doit retarder ni l'ouverture d'un tenant payé ni une relance), au rythme du référentiel (une heure). Pour
chaque dossier qui a un compte adhérent actif, pour chaque compte et chaque échéance à venir, **le jalon dû** part par
courriel (gabarit `echeance.rappel`) et dans l'espace (une entrée du journal, annoncée au compte).

**Un jalon est un seuil, pas une date.** Le rappel « 7 jours avant » est dû dès que l'échéance est à 7 jours ou moins, et part
une fois : un travail arrêté le bon jour rattrape le lendemain au lieu de perdre le rappel. Quand deux jalons sont franchis
sans envoi (reprise à J-1), **seul le plus proche part**. Rien pour une échéance en retard : c'est la relance du cabinet.

La clé d'un rappel (dossier, obligation, période, jalon) est écrite au journal avec lui : le travail peut tourner toutes les
heures, redémarrer ou être relancé à la main sans doubler un message. Le courriel part avant l'écriture, dans la transaction
du tour : un envoi qui lève empêche l'écriture, et le rappel repartira.

**Deux défauts trouvés en le construisant :**

- ⚠️ **Le premier essai n'envoyait aucun rappel.** Le travail lisait les cartes de « Mes échéances » (pas 113), et une carte par
  obligation montre la plus ancienne période en retard : la CNPS d'août était cachée derrière la CNPS de janvier 2025, impayée
  dans le jeu de démonstration. Un adhérent en retard sur une période doit être prévenu de la suivante, pas moins. Le travail
  lit désormais chaque période à venir, non déposée et sans preuve (`echeances_a_rappeler`), avec les mêmes titres et périodes.
- ⚠️ **La clé ne portait pas le dossier** : un adhérent qui suit deux entreprises employeuses a deux CNPS d'août, et le rappel
  de la seconde passait pour déjà envoyé. Vu en écrivant la batterie de mutations.

### Le bandeau hors ligne

En tête de l'accueil : « Hors ligne · 1 envoi en attente · Vous pouvez continuer à photographier vos factures : elles
partiront dès le retour du réseau. Rien ne se perd. » Rien quand tout va bien (un bandeau permanent « tout va bien » est un
bandeau qu'on cesse de lire). **L'essai réel a montré un retard** : au retour du réseau, le dépôt de la page rejoue la file au
même moment, et le bandeau, relu tout de suite, annonçait encore « 1 envoi en attente » pendant vingt secondes alors que
l'envoi était parti. Il relit désormais 3 et 10 secondes après le retour du réseau.

⚠️ **Ce que ce pas ne fait pas** : garder lisibles, sans réseau, les documents et montants déjà consultés (vue F, note 1). Il
faudrait un service de mise en cache des pages, qui n'existe pas.

### Les tests

`tests/test_rappels_adherent.py`, 16 cas : le jalon dû (seuil, plus proche, rien en retard), les réglages et la préférence qui
mentiraient, les routes (défaut dit comme tel, réglage au compte, dernier réglage qui fait foi, refus) et le travail (une fois
par jalon, le suivant à son jalon, rattrapage du plus proche seul, rappels coupés même avec des jalons, jalons choisis
honorés, seuls les adhérents, preuve envoyée ou dépôt consigné non rappelés, clé qui porte le dossier). Deux tests
d'ordonnancement listent le nouveau travail, avec son rang ; `tests/test_courriel.py` reçoit le contexte du nouveau gabarit.

**22 mutations : 21 tuées.** Cinq survivaient au premier passage ; quatre ont fait écrire un test (un dépôt à venir, le
dernier réglage, les collaborateurs, des rappels coupés avec des jalons) et la cinquième a révélé la clé sans dossier. Le
dernier survivant est **équivalent** : l'ajout de la clé à « déjà envoyé » pendant un même passage, dont les clés sont
distinctes ; le code le dit.

### L'essai réel, dans un vrai navigateur (le 17 septembre, téléphone de 360 px)

| Essai | Résultat |
| --- | --- |
| Accueil → Réglages | « Me prévenir avant mes échéances, par courriel et dans mon espace », 7 / 3 / 2 / 1 jours, « Réglage proposé par le cabinet », « Recevoir aussi par WhatsApp (Le compte d'envoi WhatsApp du cabinet n'est pas encore ouvert.) » grisé |
| Décocher 7 et 2, enregistrer | « choisissez au moins un moment pour être prévenu, ou désactivez les rappels. » ; les cases restent décochées, les rappels actifs |
| Cocher 3 et 1, enregistrer | « Rappels enregistrés : 3 jours et 1 jour avant chaque échéance, par courriel et dans votre espace. » ; après rechargement 3 et 1, la mention du défaut disparaît |
| Réseau coupé, un dépôt | « Hors ligne · 1 envoi en attente · Vous pouvez continuer à photographier vos factures… » |
| Réseau rétabli | l'envoi part ; 4 secondes après, le bandeau a disparu |
| Débordements à 360 px | aucun |

L'envoi des rappels lui-même est vérifié par les tests, horloge figée : le 17 septembre, aucune échéance du dossier de
démonstration n'est à moins de 7 jours.

### État à la fin du pas 115

**3 657 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (221 gestes sur 221). Contrat des écrans : 221 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 219 sur 224 (97 %). **Vues B à F de l'espace adhérent confrontées** (avec ce qui
attend une décision, écrit en Q29) ; la vue A (accès par téléphone) reste.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un réglage qui ne commande rien ment ; un rappel qui part une fois, au bon seuil, fait qu'un adhérent règle avant d'être
en retard.*

## Pas 116 — Rendre l'accès, choisir son entreprise, et ne jamais demander un mot de passe

### Pourquoi

Vue A de la maquette « Espace adhérent CGA », « Accès au compte ». Elle décrit un accès par téléphone : numéro, code reçu par
WhatsApp ou SMS, code à quatre chiffres, empreinte. **Rien de cela n'est construit** : aucun compte d'envoi SMS ou WhatsApp
n'existe, et la question est posée depuis le pas 112 (Q29, point 4). Trois choses de cette vue ne dépendent de personne, et
manquaient :

| Maquette | Avant le pas 116 |
| --- | --- |
| Note 4 : « un même téléphone peut porter plusieurs entreprises : le sélecteur apparaît alors sous le titre de l'accueil » | **les six pages de l'espace prenaient `dossiers[0]`** : un adhérent habilité sur deux entreprises ne voyait que la première, sans rien qui le lui dise |
| Note 5 : « perte de téléphone : réinitialisation par le chargé de clientèle, jamais en autonomie » | rien : le lien d'activation part au paiement, une fois ; personne au cabinet ne pouvait le renvoyer |
| Note 3 : le message anti-fraude | rien, et la page de connexion portait trois phrases devenues fausses |

### Le sélecteur d'entreprise

Le NIU choisi vit dans un témoin (`cga_entreprise`), relu par chaque page de l'espace et **confronté à la liste des dossiers
rendue par le backend** : un témoin forgé sur un dossier hors périmètre est ignoré au profit du premier dossier (vérifié à
l'essai réel). Le témoin ne protège rien, il retient une préférence ; la protection reste côté serveur, route par route.

⚠️ **Un `defaultValue` n'est pas relu au rendu suivant** : après le choix, la page affichait bien la nouvelle entreprise et la
liste déroulante gardait l'ancienne. Une `key` sur le sélecteur le reconstruit.

### Rendre l'accès, sans ouvrir une porte

`GET /portefeuille/entreprises/{niu}/acces-adherents` et `POST …/{compte}/lien`, **`RELANCER_ADHERENT`** : le chargé de
clientèle, pas le comptable ni l'administrateur. C'est lui qui connaît l'adhérent et répond à son appel.

Le type du lien **se déduit de l'état du compte**, jamais de la requête : en attente d'activation, un lien d'activation
(7 jours) ; actif, un lien de réinitialisation (2 heures) ; suspendu, rien (sa levée est un acte d'administration, avec son
motif). L'en-tête de `jetons.py` prévenait qu'un geste de renvoi trop facile donne « l'habitude de renvoyer des liens sans
vérifier qui demande ». D'où trois garde-fous :

1. **Le lien part à l'adresse déjà au dossier, jamais à une autre.** « J'ai changé d'adresse, envoyez-le sur celle-ci » est
   exactement le scénario d'usurpation ; changer d'adresse est un signalement (pas 114), instruit à part. L'écran le dit sous
   chaque compte.
2. **La vérification est écrite** : comment le chargé de clientèle s'est assuré de parler au bon interlocuteur (« rappelé au
   numéro du dossier, gérant confirmé »). Quinze caractères au moins, au journal, à son nom, et relue sur la fiche du dossier.
3. **Deux renvois par jour au plus** pour un même compte (référentiel) : « au-delà, chaque lien valide de plus est un risque :
   faites venir l'adhérent au cabinet ».

Le courriel (`compte.acces_renvoye`) nomme l'entreprise, dit qui l'envoie, la durée du lien, et porte l'avertissement :
« Vous n'avez rien demandé ? N'ouvrez pas ce lien et appelez le cabinet. Le cabinet ne vous demandera jamais votre mot de
passe. » Le **jeton est émis au nom du chargé de clientèle**, pas du système : le journal dit qui a ouvert l'accès.

Les règles (type du lien, limite du jour) vivent au **transverse**, qui garde les comptes ; la route vit au **portefeuille**,
parce que le courriel nomme l'entreprise et que le transverse ne lit pas les dossiers.

### Trois phrases fausses à la connexion

La page de connexion promettait « Adresse électronique **ou téléphone** » (la session n'accepte que le courriel), annonçait un
lien envoyé « par courriel **et par message** » (aucun SMS ne part), et portait encore : « Accès de démonstration : la
vérification a lieu dans le navigateur, elle ne protège rien. L'authentification réelle sera assurée par le backend avant
toute mise en ligne de données clients. » L'authentification est côté serveur depuis longtemps (Argon2, sessions, second
facteur). Les trois sont corrigées, en français et en anglais, et la note devient le **message anti-fraude** ; l'aide dit
désormais quoi faire quand le lien n'arrive pas : appeler son chargé de clientèle.

### Les tests

`tests/test_acces_adherent.py`, 8 cas : le type du lien selon l'état, le geste de bout en bout (le lien renvoyé à A-003,
« payé, mot de passe jamais défini », sert vraiment à définir le mot de passe **et à se connecter**), la réinitialisation d'un
compte actif, la vérification trop courte, la limite du jour puis le lendemain, le compte suspendu, le compte d'un autre
dossier, et le rôle. `tests/test_courriel.py` reçoit le contexte du nouveau gabarit.

**13 mutations : 12 tuées.** Deux survivaient : l'une a fait écrire un test (le jeton émis au nom du chargé), l'autre a fait
**supprimer un contrôle redondant** (la portée de l'habilitation, déjà garantie par la lecture des habilitations du dossier) :
un code mort est un code qu'on croit protecteur.

### L'essai réel, dans un vrai navigateur (le 17 septembre)

Le backend de démonstration est lancé avec une habilitation de plus : Jean-Pierre NKOA suit aussi LA COLOMBE.

| Essai | Résultat |
| --- | --- |
| Page de connexion | « Le cabinet ne vous demandera jamais votre mot de passe, ni par téléphone, ni par WhatsApp, ni par courriel » ; « Vous ne l'avez pas reçu ? Appelez votre chargé de clientèle » ; plus de « ou téléphone », plus de « ne protège rien » |
| Accueil de l'adhérent | le sélecteur « Entreprise affichée » avec les deux entreprises ; le choix de BATIMENT PLUS suit sur les onglets Échéances, Documents et Entreprise |
| Témoin forgé sur un dossier hors périmètre | ignoré : la première entreprise du compte s'affiche |
| Le chargé de clientèle, fiche du dossier TCHOUMBA | « Émile TCHOUMBA · e.tchoumba@tchoumbaetfils.cm · En attente d'activation : le mot de passe n'a jamais été défini » |
| Vérification « ok, c'est lui » | « écrivez comment vous avez reconnu votre interlocuteur… Ce texte va au journal, à votre nom. » |
| Vérification complète | « Lien d'activation envoyé à l'adresse du compte, valable 7 jours » ; puis la trace « renvoyé le 17/09/2026 par Patricia MOUKOURI : « Rappelé au numéro du dossier, gérant confirmé » » |
| Le lien reçu (boîte de recette) | « Bienvenue, activez votre espace » ; mot de passe défini ; connexion acceptée |
| Débordements à 390 px | aucun |

### État à la fin du pas 116

**3 666 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (223 gestes sur 223). Contrat des écrans : 223 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 221 sur 226 (97 %). **Les six vues de l'espace adhérent sont confrontées**, avec ce qui
attend une décision ou un compte d'envoi écrit en Q29.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Rendre un accès est un geste dangereux : il se fait au nom de quelqu'un, vers l'adresse déjà connue, et il se compte.*

## Pas 117 — La file d'anomalies du réviseur, par gravité et par enjeu

### Pourquoi

Maquette « Parcours réviseur CGA », vue A (UC01 et UC02 : « traiter les constats de tout le portefeuille, en file, au
clavier »). Les cinq autres vues de ce parcours étaient construites, par morceaux, au fil des pas : écarter en masse (vue B,
pas 103), journal des dérogations (vue C, pas 92), revue d'un dossier transmis (vue D, pas 102), dépôt d'une déclaration
(vue E, pas 87 et 109), qualité des règles (vue F, pas 92). La première manquait, et c'est l'écran de travail quotidien du
profil :

| Le produit savait | Il ne savait pas |
| --- | --- |
| la boîte de réception, avec une pastille de conformité par pièce, **dossier par dossier** | dire « voici vos quatre constats bloquants, le plus coûteux d'abord » |
| les constats d'**une** règle, sur une période (écart en masse) | croiser toutes les règles d'un portefeuille en une file |
| les taux d'écartement, **règle par règle** | montrer ce qui dort depuis six semaines |

### Ce que la file ordonne, et pourquoi

`GET /pilotage/file-d-anomalies` (`CONTROLER_CONFORMITE`), restreinte au périmètre de l'appelant. Quatre clés, dans cet
ordre : **la gravité** (un bloquant interdit la comptabilisation, il coûte tous les jours), **ce qui dort** (au-delà de
quinze jours au référentiel), **l'enjeu fiscal** décroissant, puis **l'ancienneté**. Un constat sans enjeu chiffré passe
après ceux qui en ont un : on ne fait pas passer l'inconnu devant le connu.

⚠️ **Un premier essai faisait monter d'un cran le constat qui dort.** Un avertissement de deux mois, sans enjeu chiffré,
passait alors devant un constat bloquant du jour à 500 000 F. Un constat qui dort passe désormais devant **dans sa
gravité**, et n'en franchit jamais la frontière ; sa gravité affichée, elle, ne bouge pas, car la surclasser serait mentir.

⚠️ **Un constat déjà écarté n'est plus à décider** : le rapport est arbitré (`rapport_arbitre`), et ce qui reste est ce qui
attend une décision. Les écarts en attente d'un second regard restent sur leur écran : les remettre dans la file les ferait
traiter deux fois. Un écart d'avertissement, effectif sans second regard, fait sortir sa ligne immédiatement.

**Le regroupement par règle** est le gain du profil (note 3 de la vue A) : pour chaque règle, ses constats, les dossiers
concernés et l'enjeu cumulé, la plus grave et la plus fournie d'abord, avec le lien vers l'écart en masse.

### Pourquoi au pilotage

La file croise trois contextes : les constats (conformité, qui ne lit personne), la pièce et son déposant (collecte), la
raison sociale (portefeuille). Le pilotage lit tous les contextes et n'est lu par aucun : c'est sa place, comme les pièces
manquantes du pas 111.

⚠️ **« Déposée par », et non « Collaborateur ».** La maquette prévoit une colonne « Collaborateur » ; dans les données, une
pièce déposée au portail porte **le nom de l'entreprise**. Nommer cette colonne « collaborateur » ferait chercher un
coupable au cabinet pour une facture envoyée par l'adhérent lui-même.

### À l'écran (`/conformite/file`, en tête du menu Conformité)

- Le titre compte ce qu'il y a à traiter : « 4 bloquantes · 4 majeures · 4 avertissements · un constat de plus de 15 jours
  passe devant dans sa gravité ». **Les compteurs ne bougent pas quand on filtre** : filtrer ne fait pas disparaître le
  travail.
- Les filtres (gravité, entreprise, règle, déposant, période des pièces) sont des paramètres d'adresse : le lien d'une file
  filtrée se colle dans un message.
- **Au clavier** : ↑↓ parcourent les lignes, ↵ ouvre la pièce. Les lignes sont de vrais liens ; le composant n'ajoute que les
  flèches, et **ne capture rien quand la frappe vise un champ** (les filtres sont sur la même page).
- Ce qui dort s'affiche en rouge avec le mot « dort », jamais par la couleur seule.

### Les tests

`tests/test_file_d_anomalies.py`, 12 cas : l'ordre (gravité, sommeil, enjeu, ancienneté ; sans enjeu après ; le bloquant du
jour devant l'avertissement endormi), les compteurs et les groupes (gravité la plus forte du groupe, dossiers, enjeu
cumulé), les réglages qui mentiraient (gravité inconnue, file vide, file sans bloquants), et la route (ordre réel du jeu de
démonstration, périmètre du comptable plus étroit que celui du réviseur, chaque filtre, bornes de dates incluses, gravités
du référentiel, constat écarté qui sort, rôle).

**24 mutations : 24 tuées.** Cinq survivaient au premier passage et ont fait écrire quatre cas : l'ancienneté qui range les
avertissements sans enjeu, les gravités lues au référentiel, la borne de date incluse, les compteurs comptés avant filtre.

### L'essai réel, dans un vrai navigateur (le 17 septembre)

| Essai | Résultat |
| --- | --- |
| Conformité → File d'anomalies | « Tout votre périmètre · 4 bloquantes · 4 majeures · 4 avertissements », 12 lignes |
| Les deux premières lignes | « 66 jours · dort », « 60 jours · dort » |
| Grouper par règle | « FAC-ID-003 · NIU du fournisseur présent, valide et actif · 4 constats · 3 dossiers · enjeu cumulé 5 951 529 FCFA » |
| Deux flèches, puis Entrée | la ligne se focalise (« AGRO-NKOLO SA »), puis la fiche de la pièce F-2026-0431 s'ouvre |
| Filtre « bloquantes » | 4 lignes, et les compteurs de l'en-tête inchangés |
| Flèche dans un champ de date | le focus reste dans le champ : la file ne défile pas |
| Le comptable | 11 lignes au lieu de 12 : son périmètre |

### État à la fin du pas 117

**3 679 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (224 gestes sur 224). Contrat des écrans : 224 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 222 sur 227 (97 %). **Les six vues du parcours réviseur sont confrontées.**

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un réviseur ne travaille pas dossier par dossier : il traite ce qui coûte le plus, puis ce qui dort depuis le plus
longtemps.*

## Pas 118 — La pièce d'appui d'une dérogation

### Pourquoi

Deux maquettes le demandent au même endroit : « Parcours réviseur », vue B, sous le motif de l'écart en masse (« Pièce
d'appui : 4 attestations jointes ▾ ») ; « Pilotage direction », vue E, en avertissement du comité (« 3 dérogations sans
pièce d'appui : à régulariser avant la revue trimestrielle du 30 septembre »).

Le produit savait tout du **motif** d'un écart depuis le pas 92 : obligatoire, long, journalisé, opposable. Il ne savait
rien de **la preuve**. Or le motif dit ce que le cabinet affirme avoir vérifié (« NIU obtenu hors facture et vérifié au
fichier DGI ») ; la pièce d'appui est ce qu'il montrera au vérificateur. Sans elle, un écart repose sur la seule parole de
celui qui l'a posé, et l'en-tête du module des jetons disait déjà, pour un autre geste, ce que coûte une facilité sans
trace.

### Ce qui est construit

**Sur l'écart** : `piece_appui`, avec sa date et son auteur. L'identifiant d'une pièce du dossier (« PJ-2026-0042 ») ou la
référence d'un document conservé ailleurs (« attestation DGI du 09/08 ») : le cabinet garde des documents que la plateforme
ne détient pas, et prétendre le contraire ferait saisir des références fausses.

- **Joindre est permis tant que la décision vit**, avant ou après le second regard. Sur un écart **levé ou refusé**, c'est
  refusé : une preuve jointe à une décision sans effet ferait croire, au journal, qu'elle en a un.
- **Remplacer est permis, et daté** : une première pièce jointe par erreur se corrige, et le journal d'audit garde les deux
  gestes. L'écart porte la dernière, avec son auteur.
- **Aucun motif n'est demandé pour ce geste** : la décision est déjà motivée. Exiger un second motif ferait écrire « pièce
  jointe » vingt fois par mois et diluerait les vrais motifs.

**À la politique** (`ecarts/politique.yaml`) : `piece_appui_exigee` par sévérité, et `delai_de_regularisation_jours`.
Livré : exigée pour un **majeur** (ce qui coûte de l'argent au dossier se défend avec une preuve, pas avec un souvenir),
facultative pour un avertissement ; trente jours. **Le défaut est prudent** : une sévérité que la politique n'a pas nommée
exige une preuve, comme elle exige un second regard.

**Au journal des dérogations** : `a_regulariser`, la liste des écarts qui exigent une preuve, n'en ont pas, et dont le
délai est passé, la plus ancienne d'abord. ⚠️ **Le jour même n'est pas un retard** : la pièce arrive souvent après la
décision, le fournisseur envoyant son attestation le lendemain.

### À l'écran

- **Fiche d'une pièce** : le formulaire d'écart reçoit un champ « Pièce d'appui (facultative ici) » ; chaque écart affiche
  « Pièce d'appui : … , jointe par … » ou « Aucune pièce d'appui jointe », avec le bouton « Joindre » ou « Remplacer »
  (même permission que la levée : qui décide l'écart en fournit la preuve).
- **Journal des dérogations** : une colonne « Pièce d'appui », et, **au-dessus du journal**, le panneau « À régulariser »
  quand il y a lieu : c'est ce qu'une revue trimestrielle regarde en premier, et ce qui se défend le plus mal.

### Les tests

`tests/test_piece_d_appui.py`, 10 cas : la transition (joindre, remplacer, refus sur un écart levé ou refusé, référence
vide, écart effectif qui accepte encore sa preuve), la politique (exigée par sévérité, défaut prudent, écart sans effet qui
n'exige plus rien, délai strictement dépassé, fichier livré), et les routes (pièce donnée à la proposition avec sa double
entrée au journal, pièce jointe après coup, refus du comptable, journal qui compte puis se vide quand la preuve arrive, et
un avertissement qui n'exige rien).

**18 mutations : 17 tuées.** La survivante est le **contrôle de surface** de la route, redondant avec le contrôle par
dossier qui suit : c'est la convention du projet (l'outil de relecture des permissions lit le corps de la route), et le code
le dit désormais.

### L'essai réel, dans un vrai navigateur (le 18 septembre)

| Essai | Résultat |
| --- | --- |
| Écarter un constat majeur avec « PJ-2026-0042 » | sur la fiche : « Proposé par C-003 le 18/09/2026 : « Attestation… » » puis « Pièce d'appui : PJ-2026-0042, jointe par C-003 » |
| Journal des dérogations | la colonne « Pièce d'appui » ; « aucune » pour la dérogation posée sans preuve |
| Une dérogation de quarante jours sans preuve | panneau « À régulariser (1) » : « F-2026-0412 · FAC-ACH-007 · majeur · SARL BATIMENT PLUS · proposée par Aïcha BOUBA il y a 40 jours » |

⚠️ Le décor du dernier essai est écrit **directement au magasin** par le lanceur : le produit ne permet pas d'antidater une
décision, et c'est très bien ainsi. Le comportement lui-même est tenu par les tests, horloge figée.

### État à la fin du pas 118

**3 689 tests passent** sur PostgreSQL réel, aucun ignoré. Frontend : typage, lint, construction de production.
**Avancement des écrans : 100 %** (225 gestes sur 225). Contrat des écrans : 225 appels vérifiés, 0 écart (1 illisible par
construction). Couverture des routes : 223 sur 228 (97 %). **Les quatre maquettes de parcours sont confrontées** : comptable,
réviseur, adhérent, direction (sauf la rentabilité par dossier, qui attend la grille d'honoraires et le coût horaire).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un motif dit ce qu'on affirme ; une pièce d'appui est ce qu'on montre. Le vérificateur demande la seconde.*

## Pas 119 — La recette rattrape le produit, et cesse d'accuser à tort

### Pourquoi

Les quatre maquettes de parcours sont confrontées (pas 111 à 118). Restait à confronter le produit à
**sa propre recette** : `Docs/recette/cas_usage.py`, le registre des cas d'usage, « chacun avec sa
preuve exécutée », que le cabinet reçoit imprimé. Ce registre s'était arrêté au pas 105 : il ne
disait rien des sept écrans de l'espace adhérent, ni de la file d'anomalies, ni de la pièce d'appui.
Un registre qui valide soixante-quatre cas d'un produit qui en compte soixante-quatorze annonce
« tout va bien » d'une moitié qu'il n'a jamais regardée.

### Le premier passage, et ce qu'il a trouvé

`UC-19 · Enregistrer une pièce déposée au cabinet` : **HTTP 422**, pour le comptable comme pour le
fiscaliste. Le produit avait raison, la recette avait vieilli : depuis le pas 81, une pièce se
dépose **en deux temps** (le fichier, puis la pièce avec l'empreinte que le magasin a calculée), et
le corps que le registre envoyait, avec `identifiant` et `recue_le`, est refusé par un modèle en
`extra="forbid"`. Le cas est réécrit sur le vrai parcours : envoi multipart du PDF, puis déclaration,
et le refus du fiscaliste vérifié sur le geste entier.

### Dix cas d'usage de plus

| Cas | Ce qu'il exécute |
| --- | --- |
| UC-65 | l'accueil de l'adhérent rend un bandeau parmi les quatre états, avec son titre |
| UC-66 | répondre au cabinet : 201, **la demande reste ouverte**, le double appui 409, le comptable 403 |
| UC-67 | les justificatifs d'un mois, quatre statuts connus, le dossier voisin en 404 |
| UC-68 | les échéances : une carte par obligation, période et titre lisibles |
| UC-69 | la preuve de paiement : quittance déposée, rattachée, carte passée à « preuve envoyée », seconde fois 409 |
| UC-70 | le signalement de changement : reçu, visible, **le dossier inchangé**, le collaborateur 403 |
| UC-71 | les rappels réglés par l'adhérent seul, sans moment 422, moment non proposé 422 |
| UC-72 | le lien d'accès rendu par le chargé de clientèle : vérification courte 422, lien envoyé, comptable 403 |
| UC-73 | la file d'anomalies ordonnée par gravité, fermée à l'adhérent, périmètre du comptable inclus dans celui du réviseur |
| UC-74 | la pièce d'appui jointe à une dérogation, référence trop courte refusée, comptable 403 |

Chacun est une **preuve directe** : exécutée contre la pile qui tourne, pas déléguée à un test.

### Le défaut de l'outil, qui accusait le produit

Le second passage a rendu **vingt-cinq cas en échec**, tous directs, sur une pile saine. Cause : le
**limiteur de connexions** (trente par cinq minutes) refusait la recette elle-même, et chaque cas
tombait ensuite en 401. Le README le prévoyait depuis longtemps (« le cahier de recette a été imprimé
une fois dans cet état, avec trente cas en échec qui n'accusaient que l'outil ») ; l'outil, lui, ne
s'en apercevait pas.

`session()` lève désormais `RecetteLimitee` : le registre **s'arrête** avec un bandeau « RECETTE
INTERROMPUE » et le moyen d'y remédier, et le cahier **n'est pas réécrit**. Un cahier d'hier, juste,
vaut mieux qu'un cahier d'aujourd'hui qui accuse le produit d'échecs provoqués par la recette.
Corrigé aussi : la colonne du profil, large de dix-sept caractères, collait « Chargé de
clientèle » à l'intitulé du cas.

### Le verdict

Sur une pile neuve (`pile-de-demonstration.sh neuve`), registre complet, preuves directes **et**
preuves déléguées à la suite :

    74/74 cas validés (74 exécutés)

Le cahier de recette (`Docs/cahier-de-recette-cga.html` et son PDF) est régénéré depuis ce passage :
c'est le même registre qui le remplit, donc les mêmes verdicts que ceux montrés à l'écran.

### État à la fin du pas 119

**3 689 tests** passent sur PostgreSQL réel (inchangés : ce pas ne touche pas au code du produit,
sauf rien). **74 cas d'usage sur 74** validés contre la pile qui tourne. Avancement des écrans :
100 % (225 gestes sur 225).

⚠️ **Un geste que je n'aurais pas dû faire** : pour savoir si des alertes de style préexistaient,
j'ai lancé `git stash` sur `Docs/recette`. La commande a échoué sans rien modifier (les fichiers ne
sont pas suivis), mais elle touchait à l'index, ce qui est exclu sans accord. Consigné ici parce
qu'une règle tenue n'a pas besoin d'être écrite, et qu'une règle enfreinte, si.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une recette qui ne suit pas le produit finit par le certifier sur ce qu'il faisait l'an dernier ;
une recette qui s'accuse elle-même vaut mieux qu'une recette qui accuse le produit.*

## Pas 120 — Le document de conception devient un site, et se partage par une adresse

### Pourquoi

Le document de conception est publié comme artefact, c'est-à-dire comme une page privée du compte
qui l'a engendrée. Le propriétaire du dépôt a demandé qu'il **se partage**, et, mieux, qu'il sorte
en projet Next déployable sur Vercel, « avec les mêmes informations et images jointes ».

Deux choses distinctes se cachaient derrière cette demande, et il faut les séparer :

1. **L'artefact devient public par un geste que je ne peux pas faire.** Il s'ouvre depuis la page de
   l'artefact, menu *Partager*. C'est un réglage du compte, pas du document ; aucun outil ne me le
   donne. Cela est redit au propriétaire, avec l'adresse.
2. **Le document devient un site**, hébergé par le dépôt, déployable sans compte Claude, indexable
   par personne mais partageable par tous. C'est ce que construit ce pas.

### Le choix de forme, tranché avec le propriétaire

Deux questions posées, deux réponses :

| Question | Réponse retenue |
| --- | --- |
| Quelle forme pour le site ? | **Une page, fidèle au document** (plutôt qu'un découpage en chapitres navigables) |
| Où vit le projet ? | **Un nouveau dossier du dépôt** : `Site_conception/` |

Le découpage en chapitres aurait été plus agréable à lire et plus coûteux à tenir : chaque section
ajoutée au document aurait demandé une route, un titre, une place dans une navigation. « Une page,
fidèle » garde la propriété qui compte : **il n'y a qu'un document**, et le site ne fait que le
servir.

### La mécanique : une seule source, un importateur

    Docs/architecture/document-de-conception/architecture-multitenant-cga.html   la source
                        │  node outils/importer-le-document.mjs   (joué par prebuild et predev)
                        ▼
            contenu/document.html   le corps seul
            contenu/document.css    la feuille de style, thème sombre dupliqué
            contenu/document.json   titre, version, compteurs, sommaire
            public/document.html    la page complète, servie telle quelle

L'importateur ne réécrit pas le texte. Il fait trois choses, et pas une de plus : il découpe la
source, il duplique le bloc sombre `:root:not([data-theme="light"])` en `:root[data-theme="dark"]`
pour que le bouton de thème puisse le forcer, et il pose `id="sommaire"` sur la navigation qui
existe déjà. ⚠️ Un attribut ajouté ne change pas le texte ; un sommaire réécrit en changerait le
sens, et c'est exactement la seconde version du document que ce pas cherche à ne pas créer.

### Le défaut mesuré : le document partait deux fois

Le premier site rendait le document par un composant serveur React. Mesuré sur la version 119 du document,
qui pèse 966 Ko de texte :

| Rendu | Servi (brut) | gzip | brotli |
| --- | --- | --- | --- |
| Par composant serveur React | 2 177 075 o | 491 Ko | 340 Ko |
| Par fichier engendré | 970 888 o | 239 Ko | 218 Ko |

Un composant serveur envoie le document **deux fois** : une fois en HTML, une fois dans la charge
utile de navigation que React rejoue côté client. Pour 966 Ko de texte, cela double le poids sans
rien apporter : la page ne porte aucun état, aucune donnée à rafraîchir, aucun rendu qui dépende du
lecteur. La racine `/` est donc réécrite vers `/document.html`, et `app/page.tsx` a été supprimé
plutôt que gardé « au cas où » : une page morte finit toujours par être remise en service.

Next garde le reste, et c'est pour cela qu'il reste : les métadonnées de partage, la page
« introuvable », le thème posé **avant** le premier rendu (posé après, la page clignoterait en
clair), et la construction, qui rejoue l'import à chaque déploiement.

### Ce qui a été corrigé dans le document lui-même

Le site a montré au téléphone un défaut que le document avait déjà : les tableaux larges défilent
horizontalement, et **rien ne le disait**. Le lecteur voyait une colonne coupée et croyait la
page fautive. `.tbl-enveloppe` porte désormais l'ombre de défilement classique, deux dégradés fixés
au conteneur et deux ombres qui glissent avec le contenu. Corrigé **dans la source**, donc dans
l'artefact **et** dans le site : c'est l'intérêt d'avoir une seule source.

Vérifié dans un vrai navigateur à 390 px : les ombres sont présentes, et le défilement horizontal de
la page vaut zéro. À 1440 px : 129 sections, 91 figures, le bouton de thème pose bien
`data-theme=dark`, l'ancre du sommaire répond, aucune erreur en console.

### Le déploiement

`Site_conception/README.md` dit le seul réglage qui ne se devine pas : **Root Directory =
`Site_conception`**. Vercel clone tout le dépôt puis se place dans ce dossier, et l'importateur
remonte d'un cran pour lire `../Docs/...`.

⚠️ **Le rabattement est un filet, pas une solution.** Si la source est hors de portée,
l'importateur ne fait pas échouer la construction : il reprend le dernier import présent dans
`contenu/` et écrit un avertissement bruyant sur la sortie d'erreur. Le site part alors avec une
version périmée, sans que le visiteur puisse le voir. C'est pourquoi `contenu/` et
`public/document.html` sont **versionnés** et non ignorés, et pourquoi le README demande de lire cet
avertissement dans le journal de construction.

Le site n'est pas indexé (`robots: { index: false }`) : le document décrit l'architecture interne
d'un cabinet, il se partage par son adresse, il ne se cherche pas sur un moteur. Il ne porte aucune
donnée du produit : ni base, ni API, ni session. Le rendre public n'expose que le document.

### État à la fin du pas 120

**3 689 tests** passent sur PostgreSQL réel (inchangés : ce pas ne touche pas au code du produit).
**74 cas d'usage sur 74**. Avancement des écrans : 100 % (225 gestes sur 225). Le document de
conception passe en version 120 : 126 sections numérotées, quatre annexes, 92 figures.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un document qui ne se partage que par un fichier joint vieillit dans les boîtes aux lettres ; un
document servi par une adresse ne peut vieillir qu'à un seul endroit.*

## Pas 121 — Les noms que la plateforme se garde, et que personne ne lisait

### Pourquoi ce pas

Question posée au produit : **est-ce que la solution est complète ?** Plutôt que de relire le
tableau « ce qui tourne, et ce qui reste à brancher », qui est écrit à la main et qui dérive, j'ai
interrogé le système : `GET /transverse/services`, la grille des écrans, la recette, le référentiel.

Le registre a répondu ceci : treize services sur quatorze `EN_SERVICE`, et **six sans sonde**. La
composition explique cette absence depuis longtemps, dans `main.py` :

> La Collecte, la Clôture, le Social, la Création d'entreprise, le Pilotage et les Tenants n'ont
> aujourd'hui aucune configuration propre dont l'absence les empêcherait de travailler.

C'était vrai le jour où la phrase a été écrite. Ce ne l'était plus :

| Service | Ce qu'il a pris depuis | Depuis |
| --- | --- | --- |
| C · Collecte | le magasin des fichiers déposés, et les réponses de l'adhérent | pas 81 et 113 |
| J · Pilotage | sept fichiers de réglages | pas 100 à 117 |
| N · Tenants | la liste des noms réservés | chantier multi-tenant |

⚠️ **Un commentaire qui explique une absence doit être relu le jour où l'absence cesse, et rien ne
le rappelle.** C'est le vrai enseignement de ce pas, et il vaut au-delà des sondes.

### Le défaut, trouvé en tirant ce fil

En cherchant ce que la sonde des Tenants pouvait bien surveiller, j'ai suivi
`Docs/referentiel/tenants/noms-reserves.yaml` jusqu'à son lecteur. **Il n'en avait pas.**

```
Docs/referentiel/tenants/noms-reserves.yaml      la liste : api, www, admin, blog, cdn…
    charger_les_noms_reserves(dossier)           l'adaptateur, écrit, testé
        ↓ appelé par                             PERSONNE
    domaine.slug.valider(slug, reserves=())      le paramètre, facultatif
        ↑ appelé par
    routes_acquisition.py, deux fois             valider_le_slug(corps.slug)
```

Le second paramètre était facultatif, l'`api` réexportait la fonction du domaine telle quelle, et
les deux seuls appelants l'appelaient avec un seul argument. Conséquence : **un client pouvait se
voir attribuer `api.cga.cm`, `www.cga.cm` ou `admin.cga.cm`**, et les requêtes de la plateforme
seraient parties chez lui.

Le fichier existait, l'adaptateur existait, le paramètre du domaine existait, le test du domaine
existait. Il manquait le fil entre les quatre, et **rien ne pouvait le signaler** : chaque pièce,
prise seule, était juste.

### La correction : supprimer la façon de se tromper

Corriger les deux appels aurait laissé le troisième à écrire. `tenants/api.py` — la seule porte
ouverte aux autres contextes — porte désormais sa propre `valider_le_slug(slug)`, sans second
paramètre, qui va chercher la liste elle-même.

Le domaine garde son paramètre facultatif, et c'est délibéré : il doit rester vérifiable sans
fichier, et lui donner la liste en dur ferait revenir au code ce qui vit au référentiel « parce
qu'elle grandit ».

⚠️ **Sans liste, on refuse.** `NomsReservesIndisponibles` est levée et les routes rendent `503`. Le
choix n'est pas symétrique : une souscription refusée se rejoue, un slug attribué est
inréattribuable, et le reprendre enverrait les anciens liens chez quelqu'un d'autre.

⚠️ `noms_reserves()` **n'est pas mémoïsée**. Un nom ajouté au référentiel doit interdire tout de
suite, sans quoi la promesse « la faire grandir ne demande pas une livraison » devient « ne demande
qu'un redémarrage ».

### Quatre sondes, et trois absences qui restent justes

| Service | Ce qu'elle constate | Verdict |
| --- | --- | --- |
| C · Collecte | le magasin des pièces existe et s'écrit | **panne** : un dépôt serait accusé puis perdu, et l'adhérent croirait avoir remis sa pièce |
| C · Collecte | les réponses de l'adhérent se chargent | suspect : le cabinet reçoit et contrôle encore |
| J · Pilotage | les sept réglages se chargent | suspect : le Pilotage lit tous les contextes et n'est lu par aucun |
| N · Tenants | les noms réservés se lisent, et il y en a | **panne** : plus aucun tenant ne s'ouvre |
| A · Référentiel | les barèmes, en plus des paramètres | suspect, et seulement si le fichier est **présent** |

Le magasin est constaté par `os.access`, pas par un fichier témoin : déposer un octet toutes les
dix secondes salirait le magasin pour demander au système ce qu'il sait déjà.

Les barèmes sont vérifiés par le **Référentiel** et non par le Social : c'est le dépôt du
Référentiel que le Social emprunte par l'`api`. Deux sondes sur un même fichier finissent par
diverger, et le jour venu personne ne sait laquelle croire. Pour la même raison, la **Clôture** et
la **Création d'entreprise** restent sans sonde : elles n'ont aucune ressource à elles.

⚠️ Un fichier de barèmes **absent** ne dit rien : un déploiement qui ne fait pas de paie n'en a pas.
Un fichier **présent et vide de barèmes** est suspect : quelqu'un l'a posé, donc quelqu'un compte
dessus.

### Une sonde n'est pas une porte d'entrée

Poser une sonde dans `tenants/adaptateurs/entrant/` aurait fait passer le contexte N de
`CAS_D_USAGE` à `EN_SERVICE` : le registre compte les modules de la couche entrante pour dire si un
service est joignable. Il aurait annoncé une façade sur du vide, « le plus coûteux des deux
mensonges possibles » selon ses propres termes.

`MODULES_QUI_N_OUVRENT_RIEN` exclut `sonde.py` de ce décompte. Une sonde est appelée par
l'exploitation, jamais par un utilisateur, et elle ne rend joignable aucune fonctionnalité. Le
contexte N reste donc `CAS_D_USAGE`, ce qui est la vérité : il n'expose toujours aucune route.

### Vérifié

**25 cas** dans `tests/test_noms_reserves_et_sondes.py`, et une batterie de mutation de **onze
mutations, toutes tuées**, dont la première est le défaut d'origine remis en place
(`_valider_la_forme(slug)` sans les réserves).

Deux tests existants sont tombés, et ils avaient raison de tomber : ils affirmaient « pilotage est
sans sonde ». Ils affirment désormais la **liste exacte** des trois services sans sonde, pas
« au moins ceux-là » : une liste fermée oblige à revenir le jour où un service change de camp, dans
un sens comme dans l'autre. C'est précisément ce qui a manqué pendant quatre pas.

### Ce que l'inventaire a dit d'autre, et qui n'est pas de ce pas

La réponse honnête à « est-ce complet » est : **le produit l'est, ses branchements extérieurs ne le
sont pas.** Mesuré ce jour :

* **225 gestes d'écran sur 225**, **74 cas d'usage sur 74**, **3 689 tests** avant ce pas ;
* **40 valeurs légales sur 91 restent `A_VALIDER`** (51 sont `VALIDE`) : rien n'est opposable tant qu'un fiscaliste
  nommé n'a pas contresigné ;
* **la DGI n'expose aucune interface** : le port existe, l'adaptateur manuel fonctionne, et les
  cinq questions du dossier des questions ouvertes attendent le cabinet ;
* **WhatsApp est modélisé comme canal, sans connecteur** ; seuls le courriel et le prestataire de
  paiement sortent réellement du processus ;
* **l'application mobile Flutter n'existe pas** : aucun fichier `.dart` au dépôt ;
* **quatre restes du chantier multi-tenant** sont écrits à sa dernière section, dont les deux rôles
  PostgreSQL en exploitation, sans lesquels la sécurité au niveau des lignes ne s'applique pas ;
* **les manifestes Kubernetes existent et sont vérifiés contre la configuration**, mais rien ne dit
  qu'ils aient été appliqués sur un serveur.

### État à la fin du pas 121

**3 714 tests** passent sur PostgreSQL réel. **Onze services sur quatorze** portent une sonde, et
les trois autres disent pourquoi. Avancement des écrans : 100 % (225 gestes sur 225).

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un fichier que personne ne lit, un paramètre facultatif et deux appels distraits suffisent à donner
le nom de la plateforme à un client. Aucune des quatre pièces n'était fautive.*

## Pas 122 — Le répertoire des tenants se tient à jour, sans redémarrage

### Le reste que ce pas solde

Le chantier multi-tenant s'était terminé en écrivant ce qu'il laissait derrière lui. Premier de
la liste :

> **Le rafraîchissement du répertoire.** Il se garnit au démarrage ; il ne se met pas à jour quand
> un tenant s'ouvre ou change d'état. Un redémarrage suffit tant qu'il y a une souscription par
> jour, et ne suffira plus à dix.

Deux moitiés, et la seconde est la plus grave :

| Ce qui arrive | Ce que la plateforme faisait |
| --- | --- |
| un tenant **s'ouvre** après le démarrage | le client qui vient de payer clique sur son lien d'activation et reçoit `404` |
| un tenant est **suspendu ou résilié** | on continue de servir les données d'un client qu'on a cessé de servir |

La seconde est un manquement, pas une gêne : un cabinet qui a résilié un adhérent doit cesser de
l'être, et « jusqu'au prochain redémarrage » n'est pas une réponse.

### Pourquoi une fenêtre, et non un événement

C'est la décision du pas, et elle tient à un fait d'architecture : **le répertoire vit dans chaque
processus**. Trois répliques d'API, trois répertoires.

| Mécanisme envisagé | Pourquoi il ne convient pas |
| --- | --- |
| un abonné en mémoire, sur l'événement d'ouverture | ne prévient que la réplique qui a ouvert le tenant. Les deux autres rendent encore `404` : une panne **intermittente**, donc la pire à diagnostiquer |
| un travail périodique | l'ordonnanceur tourne dans **une** réplique, et ne connaît pas la mémoire des autres |
| un aller-retour en base à chaque requête | rendrait le répertoire inutile : il existe pour que la résolution d'un nom d'hôte soit une lecture de dictionnaire, sur le chemin critique de **tout** le trafic |
| **une fenêtre de fraîcheur** | n'a rien à propager. Chaque processus se remet à jour tout seul, et le fait quand on lui parle |

`CGA_FENETRE_REPERTOIRE_TENANTS_SECONDES`, trente secondes par défaut. Ce n'est pas un réglage de
performance : c'est **le temps pendant lequel la plateforme s'autorise à se tromper**, et c'est à ce
titre qu'il est écrit dans la configuration, avec ce qu'il borne.

Trente secondes tiennent des deux côtés : aucun humain ne le remarque, puisqu'un lien d'activation
met plus longtemps à arriver par courriel ; et trois répliques servant mille requêtes par minute ne
font que six lectures de la table par minute à elles trois. ⚠️ **Zéro est refusé par la
configuration** : ce serait exactement l'aller-retour par requête que le répertoire existe pour
éviter.

Le jour où un bus d'événements traversera les processus, il rendra la mise à jour immédiate. La
fenêtre restera comme filet, et c'est très bien ainsi.

### Trois détails qui ne sont pas des détails

**Remplacer, et non verser par-dessus.** Un rechargement qui appellerait `inscrire` en boucle
garderait les entrées que la table ne porte plus : un tenant retiré continuerait d'être résolu,
c'est-à-dire le défaut corrigé, retourné dans l'autre sens. `RepertoireEnMemoire.remplacer` construit
un dictionnaire neuf et l'affecte.

⚠️ **Sur un dictionnaire neuf, jamais par un `clear()` suivi d'un remplissage.** Le répertoire est lu
par toutes les requêtes ; entre le vidage et la fin du remplissage, chaque lecture aurait rendu
`None`, et un tenant parfaitement valide aurait reçu `404` pendant que son répertoire se
reconstruisait. L'affectation d'un nom, elle, est atomique pour les lecteurs. Cette propriété-là ne
se prouve pas par un test en un seul fil, et c'est dit plutôt que sous-entendu.

**L'instant du dernier essai est noté même quand l'essai échoue.** Sans cela, une base en difficulté
serait interrogée par chaque requête qui arrive, c'est-à-dire martelée au moment précis où elle a
besoin qu'on la laisse respirer. C'est la discipline d'`INTERVALLE_APRES_PANNE` dans la boucle de
fond, appliquée ici. Et pendant la panne, **le répertoire précédent continue de servir** : servir ce
qu'on sait vaut mieux que ne rien servir.

### Vérifié

**13 cas** dans `tests/test_repertoire_a_jour.py`, sur **PostgreSQL réel** : le rechargement lit la
table des tenants, et un test qui le simulerait ne prouverait rien du chemin que prend la production.

Deux cas comptent les ouvertures de session plutôt que d'observer un état : cinquante requêtes dans
la fenêtre n'en provoquent **aucune**, et dix requêtes après la fenêtre n'en provoquent **qu'une**.
C'est la seule façon de prouver qu'un cache est encore un cache.

Batterie de mutation : **sept mutations, toutes tuées**, dont le retour à `inscrire` au lieu de
`remplacer`, la fenêtre stricte au lieu de large, et l'instant noté seulement en cas de succès.

⚠️ Une mutation avait d'abord survécu : retirer la mise en minuscules des clés du remplacement.
Aucun test ne pouvait la tuer, parce que tous construisaient leurs tenants par `ouvrir`, qui refuse
une capitale. Or `Tenant` l'accepte : une ligne écrite avant que la règle n'existe, ou par une
migration, porterait une capitale, et le client verrait `404` sur une adresse correcte. Le cas est
désormais écrit sur ce qui peut réellement se trouver en base, et non sur ce que le code écrit.

### État à la fin du pas 122

**3 727 tests** passent sur PostgreSQL réel. Il reste trois points au chantier multi-tenant : la
double vérification du jeton contre le domaine, l'audit sous mandat, et les deux rôles PostgreSQL en
exploitation.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un cache qui ne se périme jamais n'est pas un cache, c'est une copie qui vieillit.*

## Pas 123 — Le site devient une documentation, et deux défauts de rendu tombent

### Ce qui était demandé

Le site ne portait qu'une chose : le document de conception, servi tel quel. La demande du
propriétaire du dépôt tient en six points : embellir la documentation et mieux expliquer les
concepts intégrés ; des **onglets** pour les prérequis, côté concepts comme côté langages employés ;
en faire une **séance pratique de développement** plutôt qu'une brochure ; un rendu **responsif dans
sa globalité**, avec une interface soignée ; aucun tiret cadratin ; et le nom du concepteur,
**TCHAMBA TCHAKOUNTE Edwin, ingénieur informaticien**, porté par le site comme par le document.

### Le site, maintenant

| Adresse | Ce qu'elle porte | Comment elle est rendue |
| --- | --- | --- |
| `/` | Ce que fait la plateforme, les chiffres mesurés, et comment lire le site | page React, 6 Ko compressés |
| `/prerequis` | Quatre onglets : concepts, langages, outils, poste de travail | page React, 24 Ko compressés |
| `/document` | Le document de conception complet | fichier engendré, 239 Ko compressés |
| `/mise-en-oeuvre` | Les neuf étapes du lancement, chacune avec son état | page React, 9 Ko compressés |

Le document quitte la racine pour `/document`. Le choix du pas 120 tient toujours, mais il ne
s'applique qu'à lui : **c'est la taille du contenu qui décide**, et les trois autres pages ne portent
rien qui justifie de renoncer au cadre.

### Deux sources uniques de plus

`contenu/theme.css` : les seules variables de couleur, extraites du document à l'importation. Les
pages React ne partagent pas la feuille du document, qui met en forme un texte long et n'a rien à
faire sur une page d'accueil ; elles partagent ses couleurs. Les recopier à la main aurait donné deux
identités qui divergent au premier ajustement, et un lecteur qui passe d'une page au document verrait
le sol bouger sous lui.

`donnees/site.json` : la navigation, lue à la fois par l'importateur, qui la pose dans la page
statique du document, et par les pages React. ⚠️ Une barre recopiée dans deux langages diverge au
premier onglet ajouté : l'un des deux l'oublie, et la page devient introuvable autrement qu'en la
devinant.

### Le contenu, écrit comme une séance et non comme une brochure

Les neuf notions du projet suivent toutes le même plan : **le problème**, puis la réponse, puis
l'adresse dans le dépôt. Une définition qui ne répond à aucun problème ne se retient pas, et une
notion sans adresse dans le code reste une idée.

Le poste de travail est une séance d'une heure, en huit étapes, et chacune se termine par **ce qu'on
doit voir**. Une instruction sans résultat attendu laisse le lecteur incapable de savoir s'il a
réussi, et il continue en traînant une erreur qui se manifestera trois étapes plus loin. La huitième
étape est la discipline du projet, dont le quatrième geste est celui qu'on saute quand on est pressé :
muter son propre code pour vérifier que le test qu'on vient d'écrire vérifie bien quelque chose.

La mise en œuvre porte neuf étapes étiquetées **en place**, **à faire** ou **bloquant**. Une page de
lancement qui n'énumère que ce qui est prêt se lit agréablement et laisse découvrir les obstacles un
par un, au pire moment, c'est-à-dire devant le client.

### Ce que la mesure du responsif a trouvé

La responsivité n'a pas été regardée, elle a été **mesurée** : quarante combinaisons de page et de
largeur (320, 360, 390, 430, 768, 1024, 1280 et 1600 pixels), chacune chargée dans un vrai cadre du
navigateur, en relevant le débordement horizontal et les éléments qui dépassent sans conteneur qui
défile.

Deux défauts sont sortis, et **tous deux étaient dans le document**, donc dans l'artefact publié
depuis des semaines :

1. **Un mot poussait toute la page.** La feuille du document déclarait `white-space: nowrap` sur le
   code en ligne. Un identifiant long, ici un nom d'événement, débordait la colonne de texte et
   élargissait la page entière : au téléphone, tout le document défilait de travers à cause d'un
   mot. Remplacé par `overflow-wrap: break-word`, qui ne coupe que lorsque le mot ne tient pas seul.
   Dans les tableaux, le `nowrap` reste : ils ont leur propre enveloppe qui défile.
2. **Huit pixels de marge par défaut.** Le document est un fragment : il ne porte ni `<html>` ni
   `<body>`, donc aucune remise à zéro de la marge du corps. Publié comme artefact, il hérite d'une
   page qui la remet à zéro ; servi seul, il gardait huit pixels de chaque côté, ce qui décollait la
   barre des bords et faisait déborder la page sous 340 pixels de large.

Après correction, sur les quarante combinaisons : **un seul pixel de débordement**, sur le document à
320 pixels, ce qui est un arrondi sous-pixel.

### Un commentaire faux, corrigé

Le composant d'onglets rend les panneaux cachés plutôt que de les retirer. J'avais justifié ce choix
par la recherche du navigateur, qui « trouverait alors tout le contenu ». **C'est faux** : `hidden`
vaut `display: none`, et Ctrl+F ne descend pas dedans. Vérifié dans le navigateur plutôt que supposé.

Le commentaire dit maintenant ce que ce choix apporte réellement, et une règle d'impression rend les
panneaux cachés sur papier : un document imprimé amputé de trois quarts de son contenu serait une
surprise désagréable, découverte après l'impression.

### Les tirets cadratins, et où ils restent

Zéro dans le document de conception, zéro dans les quatre pages du site, zéro dans les sources du
site. Ce qui est publié n'en porte aucun.

Ils restent dans les commentaires du code et dans les journaux, où ils séparent des propositions :
environ 1 480 dans le serveur, 480 dans l'interface, 330 dans les tests, 617 dans les journaux
d'architecture. Un remplacement mécanique de trois mille occurrences, sans relire les phrases,
produirait des tournures fautives dans un texte dont la précision est justement la valeur. C'est un
passage à faire, et à faire délibérément.

### Vérifié

Construction sans erreur, typage compris. Quatre adresses servies plus la page introuvable. Les
onglets répondent au clic, aux flèches gauche et droite avec bouclage, aux touches Début et Fin, et
un seul d'entre eux est atteignable par tabulation, comme le veut la convention. La bascule de thème
pose bien son attribut et survit au rechargement. Le concepteur est nommé dans le pied du site et
dans l'en-tête du document.

### État à la fin du pas 123

**3 727 tests** passent sur PostgreSQL réel, inchangés : ce pas ne touche pas au code du produit. Le
document de conception passe en version 123.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une documentation qu'on n'ose plus modifier parce qu'elle est illisible en source cesse d'être mise
à jour, et une documentation périmée est pire qu'absente.*

## Pas 124 — La documentation devient un cours, et cinq simulations

### Ce qui était demandé

Quatre points : donner **un cours complet** pour chaque prérequis, rendre l'interface plus vivante
et plus soignée, embellir le rendu dans son ensemble, et joindre des **simulations** pour que le
système soit compréhensible par quelqu'un qui ne lit pas le code.

### Ce qui existe maintenant

| Adresse | Contenu | Poids compressé |
| --- | --- | --- |
| `/prerequis` | Le sommaire des quatre cours, en onglets : durée, plan, acquis | 8 Ko |
| `/prerequis/concepts` | 9 chapitres, 4 simulations, 5 exercices | 23 Ko |
| `/prerequis/langages` | 8 chapitres, 1 simulation, 2 exercices | 18 Ko |
| `/prerequis/outils` | 7 chapitres, 2 exercices | 11 Ko |
| `/prerequis/poste` | 9 étapes à faire, 2 exercices | 10 Ko |

⚠️ **Les onglets présentent, les pages enseignent.** Mettre les quatre cours entiers dans quatre
onglets d'une seule page aurait donné une page de plusieurs centaines de kilo-octets dont le lecteur
ne voit jamais les trois quarts, et dont le plan latéral, qui suit la lecture, n'aurait plus de sens.

### Le plan de chaque cours suit la lecture

`IntersectionObserver` plutôt qu'un calcul au défilement. Suivre la lecture en écoutant chaque
événement de défilement oblige à mesurer la position des trente-trois chapitres à chaque pixel
parcouru, et chaque mesure force le navigateur à recalculer sa mise en page : le défilement devient
saccadé sur un téléphone d'entrée de gamme, c'est-à-dire exactement sur les appareils du public visé.

La barre de progression, elle, écoute bien le défilement, parce qu'elle a réellement besoin d'une
valeur continue ; elle ne lit que deux nombres déjà connus du navigateur, et son écoute est déclarée
passive.

### Cinq simulations, et ce qu'elles ne montrent pas

| Simulation | Ce qu'elle rend tangible |
| --- | --- |
| Contrôler une facture | Un contrôle ne répond pas par oui ou par non : il rend des constats gradués, chacun chiffré |
| Résoudre un sous-domaine | Quatre situations très différentes rendent la même réponse, et c'est délibéré |
| Modifier le journal | Réécrire une entrée ancienne rompt la chaîne, et la rupture se voit au rang près |
| Ouvrir un espace client | Les étapes déjà faites se défont dans l'ordre inverse |
| Résoudre un paramètre à une date | Le même montant, deux dates, deux réponses |

⚠️ **Les empreintes du journal sont de vraies empreintes**, calculées par le navigateur avec la même
fonction que le serveur. Un simulacre, par exemple une somme de caractères, aurait montré le
mécanisme et enseigné une fausse idée : que l'empreinte est un résumé approximatif qu'on pourrait
reproduire à la main.

⚠️ **La simulation de conformité ne contient pas le moteur**, et son pied le dit. Les règles y sont
une transcription lisible, avec des valeurs d'illustration. Une simulation qui embarquerait une copie
des règles finirait par en donner une version périmée, c'est-à-dire exactement le défaut que le
projet combat.

### Deux débordements introduits, et trouvés par la mesure

Le pas 123 avait laissé le site à zéro débordement. Les ajouts de ce pas en ont introduit deux, que
les quarante mesures d'alors n'auraient pas vus puisqu'elles portaient sur des pages qui n'existaient
pas encore.

1. **Le décor du bandeau élargissait la page de cent pixels, à toutes les largeurs.** La lueur du
   haut de page déborde volontairement de cent vingt pixels de chaque côté pour ne pas montrer ses
   bords ; sans coupe, elle élargit le document, et le lecteur défile de travers à cause d'un
   élément purement décoratif.
2. **La colonne des cours ne pouvait pas rétrécir.** Une colonne de grille déclarée `1fr` a une
   largeur minimale automatique, celle de son contenu le plus large. Un bloc de code ou une frise,
   même enveloppés dans un conteneur qui défile, élargissaient la page de trois cent quatre-vingts
   pixels sous 400 px. `minmax(0, 1fr)` le corrige.

Après correction, sur **cinquante-quatre combinaisons** de page et de largeur, de 320 à 1280 pixels :
**aucun débordement**.

### Ce que l'animation ne fait pas

Le composant qui fait surgir les cartes au défilement rend son contenu **visible par défaut**, et ne
pose la classe qui l'efface qu'une fois monté dans le navigateur. L'ordre inverse, cacher en CSS et
révéler en JavaScript, donne une page blanche à quiconque n'exécute pas le script : une documentation
invisible est pire qu'une documentation sans animation. La préférence système « animations réduites »
neutralise les transitions.

### Une limite de l'outillage, et comment elle a été contournée

Les vérifications se font dans un navigateur piloté. Or, dans ce contexte, un défilement demandé par
script ne délivre **aucun événement de défilement** à la page : le plan et la barre de progression
paraissaient figés alors qu'ils fonctionnaient. C'est un vrai défilement, à la molette, qui l'a
montré : deux événements reçus, barre à 87,9 %, chapitre 7 marqué comme courant. Une conclusion tirée
de la première mesure aurait fait « corriger » du code qui n'avait rien.

### Vérifié

Construction sans erreur, typage compris. Neuf adresses servies. Le plan suit la lecture, la barre de
progression avance, les onglets répondent au clavier, les simulations sont interactives et le journal
calcule de vraies empreintes. Zéro tiret cadratin dans les sources du site. Le concepteur, **TCHAMBA
TCHAKOUNTE Edwin**, est nommé au pied de chaque page.

### État à la fin du pas 124

**3 727 tests** passent sur PostgreSQL réel, inchangés : ce pas ne touche pas au code du produit. Le
document de conception passe en version 124.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une notion qu'on peut essayer se retient mieux qu'une notion qu'on a lue, et une notion dont on a vu
le mécanisme se casser se retient pour de bon.*

## Pas 125 — La palette, refaite pour être vue

### Ce qui était demandé

Les couleurs étaient jugées ternes, et le rendu devait gagner en force. C'est une demande
d'apparence, mais elle se traite comme le reste : en mesurant plutôt qu'en regardant, parce que
« plus percutant » et « illisible » se ressemblent beaucoup sur un écran bien calibré.

### Une palette, deux thèmes, une seule source

L'ancienne palette était une gamme d'olive et de sauge : fond `#f4f6f2`, encre `#161d21`, accent
`#1d6b50`. Lisible, sobre, et sans relief. La nouvelle repose sur un papier presque blanc, une encre
bleu-nuit, et trois teintes franches, plus une quatrième famille introduite pour varier sans salir.

| Rôle | Avant | Après | Ce que cela change |
| --- | --- | --- | --- |
| fond | `#f4f6f2` | `#f7f8fa` | un papier froid, qui fait ressortir le blanc des cartes |
| surface | `#fbfcfa` | `#ffffff` | les cartes se détachent du fond au lieu de s'y fondre |
| encre | `#161d21` | `#0f1720` | contraste porté de 13,9 à **17,0** sur le fond |
| accent | `#1d6b50` | `#0b7a53` | un vert plus saturé, et toujours 5,0 sur le fond |
| ambre | `#8d6009` | `#a35200` | une alerte qui se voit comme une alerte |
| rouge | `#94302a` | `#b81f1f` | un piège qui se voit comme un piège |
| azur | absent | `#1360bd` | une quatrième famille, pour les figures et les cartes |

⚠️ **Tout part du document**, comme depuis le pas 120 : le site n'écrit aucune couleur, il lit celles
que l'importateur extrait. Une palette refaite à deux endroits aurait divergé au premier ajustement.

### Les teintes choisies par le calcul, pas par le goût

Chaque couleur a été retenue après avoir calculé son contraste sur son fond réel, et rejetée quand
elle ne passait pas. Trois candidates ont ainsi été écartées :

| Candidate | Sur son fond | Verdict |
| --- | --- | --- |
| encre très douce `#6b7a89` | 4,14 | refusée, remplacée par `#5f6d79` (4,92) |
| accent `#0e8a5f` | 4,10 | refusé, remplacé par `#0b7a53` (5,04) |
| blanc sur accent `#0e8a5f` | 4,36 | refusé ; sur `#0b7a53`, 5,35 |

Les **cent seize teintes littérales des figures** ont été remplacées par cinq tons choisis pour rester
lisibles sur les deux fonds, ce qu'aucune couleur du document ne garantissait jusque-là : un objet
graphique doit tenir 3:1, et une même valeur doit le tenir sur papier blanc comme sur fond nuit.

| Usage | Ton | Sur fond clair | Sur fond sombre |
| --- | --- | --- | --- |
| vert | `#0e9463` | 3,64 | 4,91 |
| azur | `#2b7fd4` | 3,88 | 4,60 |
| rouge | `#d8382b` | 4,37 | 4,08 |
| rouille | `#c95a2b` | 3,97 | 4,50 |
| ambre | `#c47a06` | 3,22 | 5,54 |

### Le relief vient des éléments, pas d'un voile

Une nappe de dégradés avait été posée en haut de page pour donner de la profondeur. Elle a été
**retirée après l'avoir regardée** : sur un fond presque blanc, trois teintes superposées à faible
opacité ne donnent pas de la profondeur, elles donnent un voile gris. Et comme son conteneur devait
la couper, sa coupe se lisait comme un bandeau posé de travers, d'abord en bas, puis sur les côtés
après une première correction.

Ce qui la remplace se voit mieux et ne salit rien : un filet de couleur en tête de chaque carte,
quatre familles distinguées d'un coup d'œil, un trait dégradé sous chaque titre, des chiffres en
dégradé, un bouton principal en dégradé, et des ombres tirées de l'encre du thème.

⚠️ **Les chiffres en dégradé ont un repli.** Le rognage du fond sur le texte laisse, s'il n'est pas
rendu, un texte transparent, c'est-à-dire invisible. La couleur pleine est donc posée d'abord, et le
dégradé ne s'applique que là où la propriété est comprise.

⚠️ **Les ombres ne sont plus un gris écrit en dur.** Elles sont tirées de l'encre du thème : sur fond
sombre, une ombre noire ne se voit pas, et la carte perd son relief au moment précis où le contraste
est le plus faible. Même correction pour les ombres qui signalent qu'un tableau défile, dans le site
comme dans le document.

### Un bloc oublié, trouvé en cherchant les restes

Le document porte **trois** déclarations de couleurs : la claire, la sombre au goût du système, et une
sombre explicite, ajoutée pour que l'artefact publié ait son propre bouton de thème. Les deux
premières ont été refaites ; la troisième a été oubliée.

Conséquence, si personne n'avait cherché : le site aurait montré la nouvelle palette, et **l'artefact
publié aurait gardé l'ancienne dès qu'un lecteur aurait basculé en sombre**. Trouvé en cherchant les
occurrences restantes des anciennes valeurs, pas en regardant la page.

### Vérifié, et ce que la vérification a d'abord raconté de faux

Un audit de contraste a parcouru **4 694 textes**, sur six pages et deux thèmes, en calculant pour
chacun sa couleur et son fond réellement peint. Il a d'abord signalé des barres de navigation à 1,96
en thème sombre. Deux fois, la cause était dans l'outil et non dans la page :

* `color(srgb 0.07 0.1 0.13 / 0.88)` rend des composantes entre 0 et 1, là où `rgb(11, 17, 23)` les
  rend entre 0 et 255. Les confondre faisait mesurer un gris moyen là où le fond est presque noir ;
* et les cadres hors écran ne recalculent pas toujours leurs styles, si bien qu'un thème posé après
  chargement y restait sans effet.

Mesuré sur la page vivante, la même barre donne **8,93**, l'onglet actif **11,51**, l'onglet voisin
**7,58**. Une conclusion tirée de la première mesure aurait fait éclaircir des couleurs qui n'avaient
rien. ⚠️ Un outil de vérification est du code comme un autre : il se trompe, et il faut le vérifier
avant de croire ce qu'il accuse.

Par ailleurs, **cinquante-quatre combinaisons** de page et de largeur, de 320 à 1280 pixels : aucun
débordement. Les quatre-vingt-seize figures du document emploient exactement les cinq tons retenus.

### État à la fin du pas 125

**3 727 tests** passent sur PostgreSQL réel, inchangés : ce pas ne touche pas au code du produit. Le
document de conception passe en version 125.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une couleur se choisit par le calcul et se juge à l'œil, dans cet ordre : l'inverse donne une page
qui plaît sur l'écran de celui qui l'a faite.*

## Pas 126 — Le jeton dit d'où il vient, et le bord le vérifie

### Le reste que ce pas solde

Deuxième de la liste laissée par le chantier multi-tenant : « la double vérification du tenant du
jeton contre celui du domaine, dans le chemin d'authentification ».

Avant d'écrire une ligne, le défaut a été **mesuré** sur la pile de démonstration, avec deux
locataires servis par le même processus :

```
session ouverte sur   cabinet.cga.cm            → 200
le même témoin sur    station-bonaberi.cga.cm   → 200
                                                  et l'accès rendu dit « locataire CGA-BRCG »
```

La requête était donc servie **dans le périmètre de station-bonaberi**, avec les permissions d'un
compte du cabinet. Les lectures qui suivaient étaient filtrées sur un locataire, les droits venaient
d'un autre, et rien ne le signalait.

### Ce qui fermait la porte, et pourquoi cela ne suffisait pas

En base, la table des sessions est cloisonnée : sous un autre locataire, la ligne n'est pas trouvée,
et l'appelant reçoit 401. La porte était donc fermée, **par accident**.

⚠️ Un bon résultat obtenu par un mécanisme qui ne visait pas cela disparaît le jour où l'on change ce
mécanisme, et personne ne s'en aperçoit : mettre les sessions en cache pour économiser une requête,
les partager entre répliques, ou les sortir de la base suffirait à rouvrir la porte, sans qu'aucun
test ne devienne rouge.

En mémoire, c'est-à-dire en démonstration et dans une partie des tests, il n'y avait **aucune porte
du tout** : l'atelier est unique pour le processus.

### La correction : le jeton déclare, le bord vérifie

Le témoin prend la forme `locataire~identifiant`. À chaque requête, le bord confronte le locataire
déclaré à celui que le domaine a établi, et refuse s'ils diffèrent.

⚠️ **Rien n'est chiffré ni signé, et c'est volontaire.** Le secret reste l'identifiant de session,
exactement comme avant. Le préfixe n'est pas une protection, c'est une **déclaration** que le bord
vérifie. Le présenter faussement ne donne rien : ou bien il désigne le locataire de la requête, et la
recherche en base tranche comme avant, ou bien il en désigne un autre, et il est refusé.

⚠️ **Le refus ne dit pas pourquoi.** L'appelant reçoit ce qu'il recevrait d'un jeton expiré. Lui dire
que son jeton appartient à un autre locataire confirmerait que ce locataire existe, ce que la règle
du projet interdit. La trace part au journal du serveur, où elle sert l'exploitation.

⚠️ **Un identifiant nu reste accepté**, et la limite est écrite plutôt que sous-entendue. L'outillage
en ligne de commande présente l'identifiant sans préfixe, et les sessions déjà ouvertes doivent
survivre à un déploiement au lieu de déconnecter tout le cabinet. Un jeton nu est alors lu comme
appartenant au locataire de la requête, donc soumis à la recherche en base, qui le refuse ailleurs.
En mémoire, cette recherche ne tranche rien : le cas est **écrit comme tel dans les tests**, avec sa
raison, et la production refuse la persistance mémoire au démarrage.

### Une décision de forme, et son motif

Le corps de la réponse de connexion rend toujours l'identifiant **nu**. C'est lui qui désigne la
session partout ailleurs, dans le journal comme dans la fermeture de session ; y mettre le témoin
composé obligerait chaque appelant à le découper pour retrouver l'identifiant, et le premier qui
l'oublierait écrirait un rang de journal qui ne correspond à aucune session.

La coupe se fait sur la **première** occurrence du séparateur. Couper sur la dernière ferait d'un
identifiant fantaisiste un moyen de déclarer un autre locataire que le sien.

### Vérifié

**12 cas** dans `tests/test_jeton_de_session.py`, dont cinq sur le composer et le relire, sans rien
monter, et sept sur l'application réelle avec deux sous-domaines.

⚠️ Ces sept-là s'exécutent **en mémoire, et c'est le seul endroit où ce cas se prouve** : l'atelier y
est unique, donc ce qui refuse le jeton est bien la vérification, et rien d'autre. En base, la même
requête serait refusée pour une seconde raison, et le test ne dirait plus laquelle des deux agit.

Batterie de mutation : **sept mutations, toutes tuées**, dont le défaut d'origine remis en place, la
confrontation inversée, le témoin privé de son préfixe, la coupe sur la dernière occurrence, et un
refus bavard qui nommerait le locataire.

**3 739 tests** passent sur PostgreSQL réel, aucun ignoré, aucune régression.

### État à la fin du pas 126

Il reste deux points au chantier multi-tenant : **l'audit sous mandat** et **les deux rôles
PostgreSQL en exploitation**. Le mandat lui-même, écrit et éprouvé dans le domaine depuis le
chantier, n'est toujours branché nulle part : c'est le prochain pas, et cette confrontation du jeton
est précisément l'endroit où il rendra autre chose qu'un refus.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Une porte fermée par accident s'ouvre le jour où l'on déplace le meuble qui la retenait.*

## Pas 127 — Le mandat quitte le domaine et entre en service

### Ce qui existait, et ce qui manquait

Le mandat est la réponse du projet au cas le plus courant de la plateforme : **le centre tient la
comptabilité d'une entreprise qui dispose aussi de son propre accès**. Deux locataires, deux jeux de
données, et pourtant les mêmes écritures. Sans lui, la seule façon de faire travailler le centre
serait de donner à ses collaborateurs un accès transversal à tous les locataires, et le jour d'un
litige personne ne saurait dire qui a touché quoi ni au nom de qui.

Il était écrit, validé, documenté et éprouvé **dans le domaine** depuis le chantier multi-tenant. Il
n'était branché nulle part : aucune table, aucun dépôt, aucune route, et aucun endroit du code ne
l'interrogeait. Un mécanisme de sécurité qui n'existe que dans son fichier de test protège
exactement autant qu'une note dans un cahier.

### La chaîne, de bout en bout

| Pièce | Ce qu'elle apporte |
| --- | --- |
| `DepotMandats` et sa table | Les mandats **accordés** par un locataire, rangés chez lui |
| Trois routes | Lister, accorder, révoquer. Celles du mandant, et de lui seul |
| Le bord d'authentification | Un compte d'ailleurs agit ici si un mandat couvre son rôle |
| Le journal | Chaque entrée écrite sous mandat le nomme |

⚠️ **Le mandat est rangé chez le mandant, pas chez le mandataire.** C'est lui qui l'accorde, lui qui
le retire, et c'est dans son périmètre que la vérification a lieu. Le ranger chez le mandataire
obligerait à sortir du périmètre servi pour savoir si l'on a le droit d'y entrer, ce qui est l'ordre
inverse de celui qu'on veut.

⚠️ **Aucune route pour le mandataire.** Lui en donner une reviendrait à laisser un locataire
s'octroyer un accès chez un autre, ce que le mandat existe précisément pour empêcher.

### Ce que le bord fait, dans cet ordre

1. la session se lit **chez le mandataire**, puisque c'est là que vit le compte du centre. C'est le
   seul endroit de l'application qui lit hors du périmètre servi, et il est borné à cette lecture ;
2. les mandats se lisent **chez le mandant**, c'est-à-dire dans le périmètre servi ;
3. les rôles ne sont gardés que si un mandat les couvre.

⚠️ **UN MANDAT N'AJOUTE AUCUN RÔLE.** Il autorise l'exercice, ailleurs, de rôles déjà tenus. Un
comptable mandaté reste comptable et ne devient pas réviseur en franchissant la frontière. Le test
le vérifie sur un compte qui tient deux rôles et un mandat qui n'en couvre qu'un : un seul passe.

⚠️ **Le périmètre de dossiers n'est pas repris.** Les habilitations du compte désignent des dossiers
**de son propre locataire** ; les transporter désignerait des dossiers qui n'existent pas, ou pire,
des homonymes. C'est le mandat qui borne, pas la liste.

⚠️ **Le refus reste indistinct.** Dire « aucun mandat » apprendrait que le locataire visé existe. Le
motif exact, que le domaine sait produire, part au journal du serveur.

### Trois défauts trouvés en branchant, et aucun par relecture

**1. Le mandat n'atteignait pas le journal.** Il était résolu, l'accès était rendu, et les entrées ne
portaient rien. Cause : une dépendance **synchrone** est exécutée par le cadre dans un fil de la
réserve, avec une **copie** du contexte. La variable posée là est perdue au retour. Déclarée
asynchrone, la dépendance s'exécute dans la tâche de la requête, et ce qu'elle pose est vu par tout
ce qui suit. Un test l'a montré, pas une relecture.

**2. La déconnexion ne déconnectait pas.** Sous mandat, la session vit chez le mandataire. Fermée
dans le périmètre du mandant, où elle n'existe pas, le geste rendait `204` **sans rien faire** :
`fermer_session` est volontairement silencieux sur une session absente, parce qu'une déconnexion ne
doit pas échouer sur une session déjà expirée. L'utilisateur restait connecté en croyant le
contraire. La session se ferme désormais là où elle vit.

**3. Un fichier de test qui passait seul et échouait dans la suite.** Le répertoire des locataires et
l'instant de son dernier chargement sont des états de processus ; sans remise à zéro, le fichier
héritait du répertoire d'un autre cas, et la fenêtre de fraîcheur du pas 122 empêchait le
rechargement de le corriger. Un test vert en isolement n'est pas un test vert.

### Le journal chaîné, et un champ ajouté sans rien casser

⚠️ **Le corps canonique ne porte la clé `mandat` que lorsqu'un mandat existe.** C'est ce que
l'empreinte hache : y ajouter une clé toujours présente, fût-elle nulle, changerait l'empreinte
recalculée de **toutes les entrées déjà écrites**, et la vérification échouerait sur un journal que
personne n'a touché. Un champ s'ajoute à un journal chaîné en ne pesant que sur les entrées qui le
portent, et un cas de test relit la chaîne des deux locataires pour le prouver.

### Vérifié

**12 cas** dans `tests/test_mandat_exerce.py`, **sur PostgreSQL réel et rien d'autre** : en mémoire,
l'atelier est unique pour le processus et tous ses dépôts sont liés au locataire par défaut, si bien
que deux locataires n'y existent pas vraiment et que le mandat n'aurait rien à franchir.

Les cas couvrent le refus sans mandat, l'exercice avec, le rôle non couvert, le compte non désigné,
le compte désigné, le mandat expiré, **le mandat révoqué qui tombe à la requête suivante** (la
promesse faite à l'adhérent : pas au prochain redémarrage, tout de suite), l'audit qui nomme le
mandat, l'action chez soi qui n'en porte aucun, la déconnexion, et la chaîne du journal qui reste
vérifiable.

Batterie de mutation : **sept mutations, toutes tuées**, dont le mandat ignoré, le mandat qui
ajouterait des rôles, le mandant pris dans le jeton au lieu du domaine, et la clé toujours présente
dans le corps canonique.

**3 752 tests** passent sur PostgreSQL réel, aucun ignoré.

### État à la fin du pas 127

Il reste **un** point au chantier multi-tenant : les deux rôles PostgreSQL en exploitation, qui est
un geste d'installation et non de code.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un mécanisme de sécurité qui n'existe que dans son fichier de test protège exactement autant qu'une
note dans un cahier.*

## Pas 128 — Le script d'installation est joué, et le chantier du socle se ferme

### Ce qui restait, et ce que ce n'était pas

Dernier reste du chantier multi-tenant : « les deux rôles PostgreSQL en exploitation ».

Tout était là **sauf l'exécution** :

| Pièce | État avant ce pas |
| --- | --- |
| `outils/roles-postgresql.sql` | écrit, relu, commenté, **jamais joué** |
| Le diagnostic au démarrage | écrit et testé |
| Le refus de démarrer en production sur un contournement | écrit et testé |
| Les deux adresses séparées dans les manifestes | écrites et vérifiées |
| Le cloisonnement avec un rôle non propriétaire | prouvé par `test_isolation` |

⚠️ **Un script d'installation qui n'a pas tourné est une hypothèse.** Celui-ci fait cent trente
lignes de SQL, et ses propres commentaires racontent qu'une première rédaction échouait sur
`permission denied for schema public` : depuis PostgreSQL 15, le schéma `public` n'accorde plus
`CREATE` au pseudo-rôle `PUBLIC`, et un script écrit pour la 14 crée deux rôles parfaitement
configurés dont l'un ne peut rien créer. Rien ne garantissait qu'une seconde erreur du même genre
n'y dormait pas.

### Ce que le pas ajoute

Le script est **joué à chaque passage de la suite**, dans une base créée pour l'occasion et détruite
après, par `psql`, avec ses variables `-v` et ses méta-commandes, exactement comme un exploitant le
lancera. Le transcrire en Python aurait éprouvé autre chose que ce qui sera lancé le jour venu.

⚠️ **L'ordre des étapes est le cœur du cas.** Le script est joué **avant** que la moindre table
n'existe. Les droits de l'application sur les tables futures ne peuvent donc venir que de la clause
`ALTER DEFAULT PRIVILEGES FOR ROLE cga_migration`. Jouer le script après avoir créé les tables aurait
masqué l'oubli de cette clause, et la panne serait apparue à la première migration d'après le
déploiement, c'est-à-dire des semaines plus tard.

⚠️ **Les rôles sont retirés avant chaque passage**, pour que ce soit la branche de **création** qui
s'exécute, et non celle de correction. Les deux existent, les deux comptent, et un décor qui
n'exercerait que la seconde laisserait la première non vérifiée : c'est pourtant elle qui tourne le
jour de l'installation. Un cas distinct éprouve la branche de correction, en donnant à la main
l'attribut `BYPASSRLS` au rôle applicatif avant de rejouer le script.

### Ce que les neuf cas constatent

| Constat | Pourquoi il compte |
| --- | --- |
| Le script s'exécute sans erreur | l'hypothèse devient un fait |
| Son constat final ne rend aucune ligne | ses deux dernières requêtes ne parlent que si quelque chose ne va pas |
| `cga_app` est soumis aux politiques | c'est l'état attendu, et il est nommé |
| `cga_migration` les contourne, et le diagnostic le dit | c'est le revers, et la raison d'être des deux rôles |
| L'application écrit et lit **sans qu'on lui ait rien accordé** | la clause des droits par défaut fonctionne |
| Sans locataire posé, elle ne voit rien | la ceinture, sans les bretelles de l'ORM |
| Avec le locataire voisin, elle ne voit rien | le cloisonnement, en SQL nu |
| Un rôle existant qui contourne est corrigé | la seconde branche du script |
| Il se rejoue sans dommage | une installation se rejoue : mise à jour, reprise, second environnement |

Batterie de mutation : **cinq mutations, toutes tuées**, et quatre d'entre elles portent sur le
**script SQL** lui-même, pas sur le code Python. Retirer la clause des droits par défaut, donner
`BYPASSRLS` à la création, retirer `CREATE` sur le schéma, laisser la branche de correction passer un
rôle fautif : chacune est rattrapée.

### Une mutation qui a d'abord survécu, et ce qu'elle a appris

Donner `BYPASSRLS` au rôle applicatif **à la création** ne changeait rien : le rôle existait déjà
d'un passage précédent, et c'est la branche de correction qui tournait. Le script était donc plus
robuste que le décor ne le montrait, et le décor ne prouvait qu'une moitié. La suppression des rôles
avant chaque passage a rendu les deux branches vérifiables.

### État à la fin du pas 128

**3 761 tests** passent sur PostgreSQL réel, aucun ignoré.

**Le chantier du socle multi-tenant est clos.** Ses quatre restes ont été soldés aux pas 122, 126,
127 et 128 : le répertoire qui se tient à jour, le jeton confronté au domaine, le mandat branché de
bout en bout, et le script des deux rôles joué pour de vrai.

⚠️ **Ce que cela ne veut pas dire.** La plateforme n'est **pas en ligne**. Aucun serveur ne la porte,
les manifestes n'ont jamais été appliqués, et les cent vingt-huit pas de ce journal ne sont ni
commités ni poussés. Ce qui est clos, c'est un chantier de conception et de code, pas une mise en
service.

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt.

*Un script d'installation qui n'a pas tourné est une hypothèse, et une hypothèse se vérifie le jour
de l'installation, devant le client.*

## Pas 129 — Le mandat à l'écran, et l'invariant que le pas précédent avait cassé

### Pourquoi ce pas suit immédiatement le précédent

Le pas 127 a branché le mandat de bout en bout et lui a donné trois routes. Il a donc, sans le dire,
**cassé un invariant du projet** : « tout ce que le backend permet est à l'écran », vérifié depuis le
pas 106 par un outil qui compare les routes montées aux appels du frontend.

⚠️ **La grille des écrans, elle, ne l'a pas vu.** Elle affichait toujours 100 %, parce qu'elle est
déclarée à la main : un geste qui n'y figure pas n'existe pas pour elle. C'est l'outil de
**couverture**, qui part des routes réellement montées, qui a nommé les trois manquantes :

```
226 routes appelées par le frontend sur 231 (97 %)
  GET    /transverse/mandats
  POST   /transverse/mandats
  POST   /transverse/mandats/{identifiant}/revocation
```

Deux mesures du même objet, dont l'une part du déclaratif et l'autre du réel. Quand elles divergent,
c'est toujours la déclarative qui a tort.

### L'écran

Le panneau **Mandats accordés** rejoint l'écran des comptes et des habilitations, où il a sa place :
c'est le même écran qui décide qui a accès à quoi. Trois gestes, et une façon de les présenter qui
tient à ce qu'ils sont.

⚠️ **C'est le seul geste de cet écran qui ouvre les données du cabinet à des comptes qu'il ne gère
pas.** Inviter, suspendre, confier un dossier portent tous sur des comptes du cabinet ; celui-ci
autorise des comptes d'un autre locataire à travailler ici. Il est donc replié par défaut, il nomme
ce qu'il ouvre, et il rappelle les deux choses qu'on croit à tort :

* **un mandat n'accorde aucun rôle.** Cocher « Comptable » ne rend personne comptable : cela laisse
  un comptable du mandataire l'être aussi chez nous ;
* **le champ des comptes vide veut dire « tous »**, et non « aucun ». C'est la règle du domaine, et
  elle est contre-intuitive : un champ vide se lit d'habitude comme une restriction. Un administrateur
  qui croit restreindre alors qu'il ouvre est le pire malentendu possible sur cet écran, donc la
  phrase est sous le champ, en gras.

Les mandats retirés et expirés **restent affichés**, en retrait. Un mandat retiré est une trace :
c'est la première chose qu'un litige demande, et une liste qui ne montrerait que les mandats en
vigueur donnerait l'impression qu'il n'y en a jamais eu d'autre.

### Un module de plus, et la raison mécanique

La construction du frontend a échoué : le composant interactif importait les libellés depuis
`administration.ts`, qui entraîne le client HTTP, qui lit le témoin de session côté serveur. Un module
serveur se retrouvait dans le paquet du navigateur.

`lib/mandats.ts` ne porte donc que la **forme** et les **libellés**, et n'appelle rien. La lecture
reste avec les autres appels. La frontière n'est pas une préférence de rangement : elle est vérifiée
par le compilateur du cadre, et c'est très bien ainsi.

### Le registre de recette, et un verdict qui ne servait à rien

`UC-75` rejoue le parcours complet contre la pile qui tourne : le mandat s'accorde, il se lit, un
mandat sans rôle est refusé, un comptable ne peut ni le voir ni le poser, il se retire, et un second
retrait rend `409`.

Le premier passage a rendu **74 sur 75**, et le cas en échec n'était pas le nouveau : `UC-31`, délégué
à la suite de concurrence, disait « aucun test exécuté ». Le registre avait raison de ne pas le
compter pour bon — c'est exactement la garde écrite au pas 119 — mais son verdict n'apprenait rien :
la cause était que la base de test n'était pas jointe, et les cas s'étaient **ignorés** au lieu de
tourner.

⚠️ **« Aucun test exécuté » est exact et parfaitement inutile à celui qui doit corriger.** Le registre
demande désormais à pytest la raison des ignorances et la met à la suite du verdict. Un problème
d'installation cesse d'être un mystère.

### Vérifié

* **228 gestes d'écran sur 228** : la grille est à jour, et l'outil de couverture ne signale plus que
  les cinq routes qui n'ont légitimement pas d'écran, une sonde de santé et un rappel de prestataire
  parmi elles ;
* **75 cas d'usage sur 75**, sur une pile neuve, base de test jointe ;
* typage et style du frontend sans erreur, 157 pages construites ;
* **3 761 tests** inchangés : ce pas ne touche pas au code du serveur.

### État à la fin du pas 129

**Rien n'est commité** : les pas en attente attendent l'accord du propriétaire du dépôt. Et rien
n'est en ligne : aucun serveur ne porte la plateforme, aucun des cent vingt-neuf pas n'est poussé.

*Deux mesures du même objet, l'une déclarée et l'autre constatée : quand elles divergent, c'est
toujours la déclarée qui a tort.*

## Pas 130 — Le journal dit à quel titre, et un écran qui compile n'est pas un écran qui marche

### Ce que ce pas ajoute

Le pas 127 a donné au journal d'audit un champ `mandat`, et le pas 129 a donné au mandat son écran.
Restait la jonction : **le champ existait en base et ne se lisait nulle part**. Une colonne « À quel
titre » rejoint donc le journal d'audit, et l'en-tête de l'écran compte ce qui vient d'ailleurs.

⚠️ **« chez lui » est écrit, et non laissé vide.** Une colonne vide se lit comme une donnée
manquante ; ici, l'absence de mandat est une information, et c'est même la plus fréquente. La
distinction que l'audit exploite est exactement celle-là : une entrée sans mandat dit qu'un compte du
cabinet a agi sur les données du cabinet, une entrée avec mandat nomme le titre auquel quelqu'un
d'ailleurs y a touché.

⚠️ **Le décompte se fait sur le journal, pas sur les mandats.** Un mandat accordé dit ce qui est
**permis** ; le journal dit ce qui a été **fait**. C'est l'écart entre les deux qu'un adhérent inquiet
vient chercher, et le donner demande de compter les actions, pas les autorisations.

### Le défaut que seul l'écran ouvert a montré

`lireMandats` appelait la route **sans transmettre le témoin de session**. Conséquence : `401`, et la
page entière en erreur.

Ce qui n'a rien vu :

| Contrôle | Verdict | Pourquoi il ne pouvait pas voir |
| --- | --- | --- |
| Le typage | vert | la fonction est bien typée, elle rend la bonne forme |
| La construction du frontend | verte | rien d'invalide dans le code |
| L'outil de couverture | vert | il compare des **adresses appelées**, pas des en-têtes envoyés |
| La grille des écrans | verte | elle est déclarative, et la ligne y était |

Ce qui l'a vu : **ouvrir la page**. Une requête, un journal d'API, une ligne `401` au milieu de six
`200`.

⚠️ La leçon n'est pas « il faut plus d'outils », c'est que **chaque outil mesure ce qu'il mesure**.
Aucun de ces quatre ne prétendait vérifier qu'un appel est authentifié ; croire le contraire parce
qu'ils sont verts, c'est leur prêter une portée qu'ils n'ont jamais annoncée.

### Vérifié dans la pile qui tourne

L'extension de navigateur n'étant pas disponible, la vérification s'est faite par requêtes, ce qui
prouve la même chose : session ouverte sur l'API, page demandée au serveur du front avec son témoin,
et lecture de ce que le serveur a réellement rendu.

| Constat | Résultat |
| --- | --- |
| La page des comptes | `200`, 188 ko servis |
| L'appel aux mandats | `200` dans le journal de l'API, après le `401` corrigé |
| Sans mandat | « Aucun mandat accordé », et la colonne dit « chez lui » |
| Après un mandat accordé | la ligne porte le locataire, « Comptable, Réviseur », « tous ses comptes », « Contrat de suivi », « En vigueur » et le geste de retrait |
| L'en-tête | « 1 mandat en vigueur » |

Le journal de l'API a par ailleurs rappelé, au démarrage de la pile, que le rôle employé en
démonstration est superutilisateur et contourne donc les politiques de cloisonnement. C'est le
diagnostic du pas 128 qui parle, et il a raison : une pile de démonstration n'est pas une
installation de production, et il vaut mieux qu'il le dise à chaque démarrage.

### Vérifié aussi

**228 gestes d'écran sur 228**, contrat des écrans inchangé, typage et style du frontend sans erreur.
**3 761 tests** côté serveur : ce pas n'y touche pas.

### État à la fin du pas 130

**Rien n'est commité, rien n'est en ligne.** Cent trente pas attendent l'accord du propriétaire du
dépôt.

*Un écran qui compile n'est pas un écran qui marche, et quatre outils verts ne valent pas une page
ouverte.*
