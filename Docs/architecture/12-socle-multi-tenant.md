# 12 · Socle multi-tenant

Journal du chantier qui fait passer la plateforme d'un système mono-cabinet à un système
où chaque client dispose de son sous-domaine et de ses données cloisonnées.

**Convention.** Comme pour [11](11-generalisation-du-moteur.md), les entrées sont en ordre
chronologique croissant : c'est une séquence de pas dont chacun dépend du précédent.

**Pourquoi ce chantier maintenant.** Le multi-tenant n'est pas une couche qu'on pose au
dessus d'un système existant : il change la façon dont chaque requête ouvre sa session de
base. **Plus on écrit de code métier avant de l'avoir posé, plus on écrit de code à
reprendre.** C'est pourquoi il vient avant le parcours d'acquisition et avant la production
comptable, et pourquoi il se construit **sans aucun métier** : on veut que le cloisonnement
soit démontré par un test avant qu'il y ait quoi que ce soit à cloisonner.

**L'écart de départ**, corrigé au pas 3 après relecture attentive du code. Ma revue
initiale disait « le multi-tenant n'existe pas ». **C'était faux.** Ce qui n'existait pas,
c'était le *multi* : le mécanisme, lui, était là et éprouvé. Voir le pas 3, qui en tire les
conséquences jusqu'à réviser une décision.

**Les pas.**

| Pas | Objet | État |
|---|---|---|
| 1 | Le slug : normalisation, contraintes, noms réservés | ✅ fait |
| 2 | Le tenant : états, cycle de vie, reprise après incident | ✅ fait |
| 3 | Le locataire, établi au bord et lu partout | ✅ fait |
| 4 | La sécurité au niveau des lignes, en ceinture | ✅ fait |
| 5 | Le test d'isolation, en boucle sur les tables | ✅ fait |
| 6 | La passerelle : résolution du sous-domaine | ✅ fait |
| 7 | Le mandat entre deux tenants | ✅ fait |
| 8 | La table des tenants, pour que le répertoire cesse d'être vide | ✅ fait |
| 9 | Le garnissage au démarrage, qui ferme la boucle | ✅ fait |

---

## 9 septembre 2026 — Point de départ

```
1256 passed, 38 skipped
```

---

## Pas 1 — Le slug

**Fait.** Un quatorzième contexte borné, **N · Tenants**, déclaré dans le test
d'architecture et documenté dans [01](01-contextes-bornes.md). Son premier module est le
slug : normalisation, validation, proposition.

* `app/contextes/tenants/domaine/slug.py`
* `app/contextes/tenants/adaptateurs/sortant/noms_reserves.py`
* `Docs/referentiel/tenants/noms-reserves.yaml` — trente-cinq noms, avec leur fondement

### Pourquoi un contexte de plus, et pas dans K · Transverse

K porte déjà l'identité, et la tentation était d'y loger le tenant. Les deux n'ont pas le
même profil : ouvrir un tenant est une opération longue, rare, transactionnelle sur
plusieurs systèmes ; vérifier un jeton est courte, constante, sur le chemin critique de
chaque requête. Si le provisionnement tombe, les tenants déjà ouverts doivent continuer de
fonctionner.

**N ne déclare aucune arête. Il ne lit même pas le référentiel** : un slug n'a pas de
fondement légal, une suspension non plus. C'est le seul contexte qui ne dépend de rien, et
cette ignorance est ce qui lui permettra de servir un autre secteur sans bouger.

### Le slug est inréattribuable, et c'est ce qui justifie vingt cas limites

Une fois donné, un slug appartient à ce tenant pour toujours. Le libérer enverrait les
anciens liens, les signets et les courriels archivés d'un client chez un concurrent.

Une erreur de validation ne se corrige donc pas en changeant une ligne : elle laisse une
adresse gelée. D'où le nombre de tests sur un module de cent cinquante lignes.

### Trois décisions prises en écrivant

**Les accents sont dépliés, pas supprimés.** « Société Générale » donne `societe-generale`
et non `socit-gnrale`. C'est la différence entre un nom qu'un client reconnaît et un nom
qu'il refuse. Le dépliage passe par la normalisation Unicode de la bibliothèque standard,
sans dépendance.

**Le refus porte un motif nommé, pas seulement un message.** L'interface de souscription
doit dire au client *ce qu'il faut corriger*, et traduire un texte français en consigne
utile demande de savoir de quel cas il s'agit. Six motifs : vide, trop court, trop long,
forme invalide, préfixe international, réservé.

**La liste des noms réservés est passée en argument, jamais constante.** Le domaine ne
réserve rien par défaut : un domaine qui réserverait des noms sans qu'on le lui demande
refuserait des slugs pour une raison invisible à l'appelant. La liste vit au référentiel,
chargée par un adaptateur, et un test interdit son retour dans le code.

### Ce que le module ne fait pas, et pourquoi c'est écrit

Il ne vérifie pas l'unicité. Deux souscriptions simultanées sur le même slug se départagent
par un **index unique en base**, jamais par une lecture suivie d'une écriture : entre les
deux, l'autre a eu le temps d'écrire. `proposer` évite les collisions connues ; elle ne les
empêche pas, et sa docstring le dit pour que personne ne s'y fie.

### Deux cas limites que les tests ont fait apparaître

**La coupe d'un nom trop long peut tomber sur un tiret**, ce qui produirait un nom d'hôte
invalide. La coupe rogne donc les tirets de bord après avoir tronqué.

**Un nom long et déjà pris doit rester dans la limite** une fois suffixé. Le suffixe est
réservé avant la troncature, pas ajouté après : `proposer` coupe à `LONGUEUR_MAXIMALE`
moins la taille du suffixe.

### Le préfixe qu'on interdit sans que personne y pense

`xn--` est le préfixe des noms de domaine internationalisés. Un slug qui le porte est
interprété comme du punycode par certains clients, qui affichent alors **autre chose que
le nom saisi**. Le refuser coûte une ligne ; le découvrir en production coûte un client qui
ne comprend pas ce qu'il voit.

```
1309 passed, 39 skipped — 45 nouveaux tests, 8 tests d'architecture pour le contexte N
ruff : All checks passed
```

---

## Pas 2 — Le tenant, ses états et sa reprise

**Fait.** La machine à états du provisionnement, écrite dans l'idiome maison : entités
immuables au domaine, cas d'usage qui rendent un **nouveau** tenant plutôt que de modifier
sur place.

* `app/contextes/tenants/domaine/tenant.py` — `Tenant`, `StatutTenant`, `EtapeOuverture`,
  `NatureTenant`, `TransitionInterdite`, `etape_suivante`.
* `app/contextes/tenants/application/cycle_de_vie.py` — huit cas d'usage.

### Cinq statuts, sept étapes, et pourquoi ce sont deux choses

Le statut dit où en est le tenant : en ouverture, actif, suspendu, résilié, en échec.
L'étape ne concerne que l'ouverture : slug réservé, ligne créée, schéma créé, métier
amorcé, stockage ouvert, administrateur créé, prêt.

Les confondre aurait donné douze statuts dont sept ne servent qu'une fois. Les séparer
permet à un tenant en échec de **garder son étape**, ce qui est toute la valeur du champ.

### La reprise, et ce qu'elle évite

C'est le point du pas. Une ouverture qui échoue à la cinquième étape laisse un tenant en
échec **à l'étape quatre**. `reprendre` le remet en ouverture sans toucher à l'étape.

Recommencer à zéro créerait un second schéma pour le même tenant, et le premier resterait
là sans que personne sache à quoi il sert. Un test le vérifie nommément : après reprise,
l'étape atteinte est `SCHEMA_CREE` et non `SLUG_RESERVE`.

Les reprises se comptent, et s'arrêtent à cinq. Une reprise qui boucle indéfiniment masque
un défaut au lieu de le signaler, et consomme une file pour rien.

### L'idempotence est une transition permise, pas une erreur rattrapée

Rejouer l'étape courante rend le tenant tel quel. C'est la condition pour qu'une livraison
au moins une fois sur le bus soit acceptable : l'appelant a bien fait son travail, il
l'avait simplement déjà fait.

### Le test a révélé un message imprécis, et le code a changé

Le premier jet traitait de la même façon deux situations différentes : demander une étape
antérieure à un tenant déjà prêt rendait « l'ouverture est au bout, il reste à activer ».
C'est faux comme diagnostic — le problème est un retour en arrière, pas une avance
impossible.

Les trois refus sont désormais distingués, parce qu'ils appellent trois diagnostics
différents :

| Refus | Ce qu'il signale |
|---|---|
| Retour en arrière | Un ordonnancement fautif |
| Saut d'étape | Une étape oubliée |
| Avance au delà du bout | Une activation manquante |

C'est le genre de correction qu'un test fait apparaître et qu'une relecture ne fait pas :
le code était juste, seul son message mentait.

### Quatre règles que le modèle refuse d'enfreindre

**Un tenant actif porte sa date d'ouverture.** Un tenant suspendu, résilié ou en échec
porte un **motif** : un tenant coupé sans motif est un incident qu'on ne saura pas
expliquer au client qui appelle.

**Une suspension n'est pas une résiliation anticipée.** Les données restent intactes, la
date d'ouverture ne bouge pas, et la réactivation est instantanée. Le client qui régularise
doit retrouver son espace exactement comme il l'a laissé.

**Une ouverture en cours s'abandonne, elle ne se résilie pas.** La distinction compte : un
abandon n'a jamais eu de client à prévenir.

**Le slug reste porté par un tenant résilié.** Il n'est jamais libéré.

### Ce que la passerelle lira

Deux propriétés, et elles ne disent pas la même chose. `sert_les_requetes` vaut vrai pour
un tenant actif seulement. `existe_publiquement` vaut vrai aussi pour un tenant suspendu,
dont le sous-domaine doit répondre une page de régularisation plutôt qu'un 404 : le client
doit comprendre pourquoi il n'entre plus, et savoir quoi faire.

Un tenant en cours d'ouverture, lui, n'existe pas publiquement. Son sous-domaine rend 404,
ce qui est exactement le bon comportement puisqu'il **répond déjà** grâce à
l'enregistrement DNS générique, bien avant qu'aucun tenant ne soit créé.

```
1347 passed, 39 skipped — 38 nouveaux tests
ruff : All checks passed
app/contextes/tenants/ : 690 lignes
```

---

## Pas 3 — Le locataire, et une décision révisée

### Ce que la relecture a montré, et que ma revue avait manqué

En ouvrant la couche de persistance pour y poser le schéma par tenant, j'ai trouvé un
cloisonnement déjà en place et bien fait :

* une colonne `locataire` sur **dix-sept tables**, portée par un mixin dont on ne peut
  pas l'oublier — la seule omission possible est celle du mixin, qui se lit sur la ligne de
  déclaration ;
* un filtre ORM automatique par `with_loader_criteria`, greffé sur `do_orm_execute`,
  **jamais écrit donc jamais oubliable** ;
* un second filtre explicite dans le dépôt documentaire, en ceinture ;
* le magasin de fichiers cloisonné par dossier ;
* des tests dédiés, dont un qui vérifie que le cloisonnement **tient à travers les routes
  HTTP**.

Et une seule valeur : `"CGA-BRCG"`, constante importée dans quinze modules.

**Le mécanisme existait, il n'avait jamais eu qu'un locataire.** Ma revue de code disait le
contraire ; elle confondait le cloisonnement par locataire avec le périmètre de
portefeuille, qui est autre chose.

### Ce que cela a coûté à la décision D3

J'avais recommandé le schéma par tenant sur trois arguments. Deux ne tiennent plus une fois
le code lu :

| Argument donné | Ce que le code montre |
|---|---|
| « Une requête mal écrite ne peut pas fuir » | Déjà vrai : le filtre est inoubliable. Vérifié aussi qu'aucune lecture par SQL textuel n'existe — le seul `text()` sur une table cloisonnée est un verrou consultatif |
| « Exporter un client : un dump » | Les entités sont stockées en documents JSON. Un export filtré est plus utile au client qu'un dump de schéma, qui ne sert qu'à réimporter dans le même système |
| « Rétention par client » | Une suppression filtrée suffit |

La décision a été remise au cabinet avec ces faits, et **révisée** : on garde la colonne, on
la rend dynamique, et la sécurité au niveau des lignes de PostgreSQL viendra en ceinture
fermer la seule faille théorique restante.

C'est la deuxième fois sur ce projet qu'une conception écrite sur papier se corrige au
contact du code. La première portait sur les schémas de faits. Le motif est le même : on
ne connaît le coût réel d'une décision qu'en ouvrant les fichiers.

### Ce qui a été fait

* `app/partage/locataire.py` — la variable de contexte, `etabli()`, `courant()`,
  `courant_ou_none()`.
* `locataire_par_defaut` déplacé dans la configuration : c'est une valeur de déploiement,
  elle change avec l'installation et non avec le code.
* L'intergiciel d'unité de travail **établit** le locataire ; il ne le constate plus.
* Les vingt et un dépôts SQL des neuf modules de routes le **lisent** au lieu de le
  constanter.

### La décision qui porte le module

`courant()` **lève** quand aucun locataire n'est établi. Elle ne rend pas de valeur par
défaut, et c'est tout l'intérêt.

Un défaut servirait silencieusement les données d'un locataire à un autre, et rien ne le
signalerait : la requête n'échoue pas, elle rend les lignes du mauvais client. Personne ne
s'en aperçoit avant qu'un adhérent ne reconnaisse le nom d'un concurrent sur son écran.

Une exception, elle, se voit tout de suite, en développement, à la première requête.

### Deux propriétés de la variable de contexte, et une limite

**L'imbrication restitue.** Un travail interne mené au nom d'un autre locataire rend le
locataire extérieur en sortant, pas `None`. D'où la restitution par jeton plutôt que la
remise à zéro.

**Les fils ne se marchent pas dessus.** Deux requêtes traitées en parallèle gardent chacune
son locataire, et un fil qui n'a rien établi **lève** plutôt que d'hériter de la dernière
requête servie. Un test le vérifie avec une barrière.

⚠️ **Elle ne franchit pas une frontière de processus.** Un travail déporté sur une file doit
porter son locataire dans le message et le rétablir à la consommation. C'est la règle
« chaque message porte son tenant », et ce module n'en dispense pas.

### Un test qui empêche le retour en arrière

Il parcourt les neuf modules de routes et échoue si l'un d'eux reprend la constante pour un
dépôt SQL. Sans lui, la prochaine route écrite reprendrait le motif d'à côté.

```
1362 passed, 39 skipped — 15 nouveaux tests
ruff : All checks passed
Aucune régression sur les 1 347 tests existants
```

---

## Pas 4 — La sécurité au niveau des lignes

**Fait.** La garantie descend dans la base. Elle s'applique désormais à toute requête,
quelle qu'en soit l'origine : l'ORM, un `text()`, un rapport, une console
d'administration ouverte un dimanche pour dépanner.

* `app/infrastructure/securite_lignes.py` — le SQL, dérivé des métadonnées.
* `session_du_locataire` pose la variable de session par transaction.
* `alembic/versions/20260909_1500_securite_au_niveau_des_lignes.py` — dix-sept politiques.

### Ce qui a été trouvé en démarrant une vraie base

PostgreSQL ne tournait pas sur le poste, et trente-huit tests étaient ignorés depuis le
début du chantier. Un conteneur monté pour éprouver les politiques les a réveillés :
**trois échouaient, et c'était ma régression du pas 3.**

Les tests appelaient `unite_de_travail()` hors requête — usage légitime pour relire la
base après un redémarrage simulé — et `courant()` levait, exactement comme prévu. Le coût
que j'avais annoncé dans la docstring s'est présenté, et il se paie en nommant le
locataire dans ces trois tests.

**Sans ce conteneur, la régression partait en production.** Elle ne se voyait pas parce
que les tests qui l'auraient attrapée ne tournaient pas.

### Le piège qui annule tout ce mécanisme

**Le propriétaire d'une table contourne ses politiques par défaut.** Une application qui
se connecte avec le rôle propriétaire est donc protégée par une politique qui ne
s'applique jamais à elle — et le test qui la vérifierait, exécuté avec le même rôle,
passerait au vert **en ne testant rien**.

Les tests de ce pas créent donc un rôle applicatif restreint et s'y connectent. C'est la
seule façon de ne pas tomber dans le piège, et cela impose une exigence de déploiement :

    cga_migration   propriétaire, joue les migrations, contourne les politiques
    cga_app         non propriétaire, droits de manipulation seulement, y est soumis

`FORCE ROW LEVEL SECURITY` existe pour soumettre aussi le propriétaire, et c'est tentant
parce que cela évite le second rôle. On ne l'emploie pas : il empêcherait les migrations
et les exports d'administration de voir les données, ce qui déplace le problème au lieu
de le résoudre.

### Trois soins qui font toute la valeur de la politique

**`WITH CHECK` autant que `USING`.** Sans le premier, une insertion mal formée créerait
une ligne au nom d'un autre client, que son propriétaire légitime verrait apparaître sans
l'avoir demandée. Plus rare qu'une lecture fautive, et plus difficile à défaire.

**`current_setting(..., true)` rend NULL plutôt que de lever** quand la variable n'est pas
posée. Une comparaison à NULL n'est jamais vraie : **une session qui n'a pas dit son
locataire ne voit rien.** C'est le bon défaut, et l'inverse de celui qu'on obtiendrait
sans ce soin.

**`set_config(..., true)` limite la portée à la transaction.** Posée pour la connexion, la
variable survivrait à la requête et serait héritée par la suivante, servie à un autre
client. Le défaut serait intermittent, dépendrait de la charge, et ne se reproduirait
jamais en développement. Un test le vérifie en rouvrant une transaction sur la même
connexion.

Et `set_config` plutôt que `SET LOCAL` parce que `SET` n'accepte pas de paramètre lié :
concaténer un nom de locataire dans du SQL serait une injection en attente.

### Ce qui a été éprouvé, et non supposé

Six tests sur une vraie base, avec un rôle non propriétaire :

| Ce qui est vérifié | Pourquoi il compte |
|---|---|
| Le rôle applicatif ne voit que son locataire, **en SQL textuel** | C'est le chemin même qui échappe au filtre ORM |
| Sans variable posée, il ne voit rien | Le défaut sûr |
| Il ne peut pas écrire pour un autre locataire | `WITH CHECK` |
| Il ne peut pas supprimer les lignes d'un autre | La ligne visée survit |
| La variable ne survit pas à la transaction | Sûreté du bac de connexions |
| Le propriétaire contourne, et c'est voulu | Migrations et exports |

La migration a été **réellement appliquée** sur une base neuve : dix-sept politiques
posées, et le retour arrière les retire toutes.

### Le SQL se dérive, il ne s'énumère pas

`tables_cloisonnees` lit les métadonnées et rend les tables qui portent la colonne. Une
liste écrite serait juste le jour où on l'écrit, et fausse à la table suivante — et la
table oubliée serait précisément celle qui fuit.

```
1411 passed, 1 skipped — avec PostgreSQL
1367 passed, 45 skipped — sans
ruff : All checks passed
```

---

## Pas 5 — Le test d'isolation

**Fait.** `tests/test_isolation.py` : une boucle sur les métadonnées, un cas par table
cloisonnée, dix-sept aujourd'hui et autant que demain en comptera.

### La propriété qui compte

**Il est engendré, jamais écrit table par table.** Une table cloisonnée ajoutée demain
sera couverte sans que personne y pense. Écrit à la main, il ne couvrirait que ce qui
existait le jour où on l'a écrit, et la table oubliée serait précisément celle qui fuit.

Un test de garde vérifie d'ailleurs cette propriété elle-même : il compare la liste des
cas engendrés à la liste des tables cloisonnées, et échoue si l'une manque.

### Constater qu'on ne voit rien ne prouve rien

C'est le piège de ce genre de test. Une table vide donne le même résultat qu'une politique
qui fonctionne, et un semis défaillant ferait passer la suite au vert **en ne testant
rien**.

Chaque cas vérifie donc les deux sens : la ligne existe et est visible à son locataire,
puis elle est invisible à l'autre. Le premier est ce qui rend le second probant.

### Le semis se dérive lui aussi

Une ligne minimale par table, engendrée depuis les types des colonnes. Cinq soins ont été
nécessaires, chacun découvert en la faisant échouer :

| Ce qui a cassé | Ce qu'on en apprend |
|---|---|
| Une colonne non nulle avec valeur d'office Python | **Un `default` Python n'est pas un `server_default`.** L'ORM l'applique, la base non : une insertion en SQL direct s'y heurte. Invisible tant qu'on écrit par l'ORM, et se paie au premier script de reprise |
| Un dictionnaire passé à une colonne JSON | Le pilote ne sait pas l'adapter en SQL direct. Une chaîne, et le transtypage dans la requête |
| `::json` laissé intact | SQLAlchemy prend les deux-points pour un paramètre lié. `CAST(... AS json)` |
| Une clé étrangère devinée | La valeur se **dérive de la colonne visée**, sinon elle ne correspond pas à ce que le semis a écrit |
| Deux clés primaires entières à zéro | Les valeurs dépendent du locataire. Et une clé primaire à colonne unique se laisse à la base, une clé composite non : seule la première devient une séquence |

Aucun de ces cinq points n'a de rapport avec le cloisonnement, et c'est précisément
pourquoi ils méritaient d'être réglés plutôt que contournés en excluant les tables
récalcitrantes. Une table exclue est une table qui cesse d'être vérifiée.

### La boucle a été éprouvée en la faisant échouer

Une politique retirée d'une seule table, et deux cas passent au rouge : celui de la table
elle-même, et celui qui vérifie qu'aucune table ne se laisse lire sans locataire annoncé.
Politique remise, les vingt repassent au vert.

Un test d'isolation qu'on n'a pas vu échouer ne prouve rien.

### Ce qu'il ne couvre pas, et pourquoi ce n'est pas grave

Il travaille au niveau des tables, pas des routes HTTP. Le pas 4 a montré que la garantie
vit dans la base et s'applique à toute requête, quelle qu'en soit l'origine : une route
qui lirait une table cloisonnée est couverte par construction, sans qu'il faille la
rejouer une à une.

Ce qui resterait à couvrir au niveau des routes, c'est le **404 plutôt que 403** sur une
ressource d'un autre locataire. Cela relève du pas 6, avec la passerelle.

```
1431 passed, 1 skipped — avec PostgreSQL
1369 passed, 63 skipped — sans
ruff : All checks passed
```

---

## Pas 6 — La passerelle

**Fait.** Le locataire vient désormais du **sous-domaine**, plus de la configuration. Un
sous-domaine inconnu ne sert rien, un tenant suspendu obtient de quoi comprendre.

* `app/contextes/tenants/domaine/resolution.py` — `slug_depuis_hote`, `verdict_pour`.
* `app/contextes/tenants/domaine/ports.py` et son répertoire en mémoire.
* `app/contextes/tenants/api.py` — la surface publique du contexte.
* L'intergiciel résout, tranche, puis établit.

### Le verdict **est** le code de statut

`Verdict` est une énumération d'entiers valant 200, 402, 410 et 404. Les traduire ailleurs
ajouterait une table de correspondance à tenir à jour, et le jour où l'on ajoute un statut
de tenant, l'oubli de la traduction se verrait en production.

**Aucun verdict n'est un 403**, et deux tests le vérifient — un dans le domaine, un sur
l'application réelle. Un 403 apprendrait au demandeur que le tenant existe, et énumérer
les sous-domaines deviendrait un moyen de découvrir le portefeuille du cabinet.

Corollaire assumé : **un tenant inconnu et un tenant en cours d'ouverture rendent la même
chose.** Les distinguer dirait à un inconnu qu'un slug est pris, donc qu'un client est en
train d'arriver.

### Le cas qui justifie de comparer un suffixe et non un contenu

`cga.cm.evil.com` **contient** la racine sans en dépendre. Une comparaison par
appartenance au lieu d'un suffixe l'accepterait, et un attaquant servirait ses propres
pages sous notre nom. Le cas a son test, dans le domaine et sur l'application.

Trois autres cas limites méritaient leur test, chacun pour une raison concrète : le port
collé par l'en-tête `Host` dès qu'il n'est pas celui par défaut, le point final de la
forme pleinement qualifiée, et le sous-sous-domaine — que le certificat générique ne
couvre pas, et qui ferait donc avertir le navigateur avant même d'atteindre le code.

### Le garde-fou d'architecture a fait son travail

Brancher l'intergiciel a fait échouer deux tests d'architecture : `transverse` importait
`tenants` sans arête déclarée, et par ses entrailles plutôt que par sa surface publique.

Deux corrections, et une décision qu'ils ont forcée : **`tenants` rejoint le socle**, au
même titre que le référentiel, et pour la même raison — il ne dépend de rien. Un contexte
métier peut légitimement avoir besoin de savoir que son tenant est suspendu.

L'arête `transverse → tenants` est déclarée explicitement, l'expansion du socle ne
s'appliquant pas au socle lui-même pour éviter les cycles. Elle disparaîtra le jour où la
passerelle sera un service à part, avec l'intergiciel.

C'est exactement ce qu'on attend d'un test d'architecture : il n'a pas empêché le
branchement, il a obligé à le justifier.

### Pas 7 — Le mandat

**Fait.** L'objet qui autorise un compte du centre à agir dans le périmètre d'une
entreprise, et le contexte qui le fait voyager avec la requête.

* `app/contextes/transverse/domaine/mandats.py` — `Mandat`, `mandat_applicable`.
* `app/partage/locataire.py` — le mandat porté à côté du locataire.

### Ce qu'il remplace

Sans lui, la seule façon de faire travailler le centre sur les données d'une PME serait de
donner à ses collaborateurs un **accès transversal à tous les locataires**. Le jour d'un
litige, personne ne saurait dire qui a touché quoi ni au nom de qui.

Avec lui, la question devient triviale : chaque action exercée sous mandat est journalisée
comme telle.

### Un mandat ne donne pas de rôle, il en autorise l'exercice ailleurs

C'est la règle qui empêche le mandat de devenir une porte d'élévation de privilèges. Un
comptable mandaté reste comptable : **il ne devient pas réviseur en franchissant la
frontière.** Le mandat dit *où* les rôles déjà tenus peuvent s'exercer, jamais *lesquels*.

Un test le porte nommément, parce que c'est la confusion la plus naturelle et la plus
coûteuse.

### La révocation est distincte de la fin

Deux champs, pas un. Écraser la date de fin ferait perdre l'information qu'un mandat a été
**retiré** plutôt qu'arrivé à échéance — et c'est exactement ce qu'un litige demande de
savoir. Le modèle exige d'ailleurs que la révocation porte sa date **et** son auteur :
l'une sans l'autre laisse un retrait que personne n'assume.

### Le motif de refus sert au diagnostic, jamais à la réponse

Cinq motifs : aucun mandat, expiré, révoqué, rôle non couvert, compte non désigné. Ils
répondent à des situations différentes, et la fonction rend **le plus avancé** rencontré :
un mandat qui existe mais ne couvre pas le rôle le dit, plutôt que de répondre « aucun ».
Sans cela, un administrateur créerait un second mandat là qu'il fallait élargir le premier.

⚠️ **La réponse au demandeur reste 404 dans les cinq cas.** Un 403, ou pire un message
distinguant « révoqué » de « inexistant », apprendrait que le locataire visé existe.

### Le locataire et le mandat répondent à deux questions

Le locataire dit **dans quelles données** on travaille, le mandat dit **à quel titre**.
Ils sont donc portés séparément par le contexte d'exécution : les confondre rendrait
indistinguables « le comptable de la PME » et « le comptable du centre agissant pour
elle », qui est précisément la question qu'un litige pose.

Et `None` signifie « chez soi », pas « on ne sait pas ». C'est cette distinction que
l'audit exploitera.

### Trois choses que le modèle refuse

Un mandat **sur soi-même** — agir chez soi ne demande aucune autorisation, et l'objet
n'aurait pas de sens. Un mandat **sans rôle** — il n'autorise rien, et le laisser exister
ferait croire à un accès. Une **désignation vide** — `None` dit « tous les comptes », un
ensemble vide n'autorise personne, et confondre les deux se paie par un accès ouvert à
tort ou fermé à tort.

```
1515 passed — avec PostgreSQL
1453 passed, 62 skipped — sans
ruff : All checks passed
```

---

## Pas 8 — La table des tenants

Ajouté après coup. Le pas 7 clôturait le chantier prévu, mais laissait le répertoire
**vide** : tout sous-domaine rendait 404, et le parcours d'acquisition n'aurait rien eu à
ouvrir. Le fermer maintenant coûte moins cher que de le découvrir au chantier suivant.

* `app/contextes/tenants/adaptateurs/sortant/tables.py` et son dépôt SQL.
* `alembic/versions/20260909_1700_table_du_contexte_n_tenants.py`.

### La seule table du système qui n'est pas cloisonnée

Toutes les autres portent la colonne `locataire` et sa politique. Celle-ci non, pour une
raison qui tient en une phrase : **elle est lue avant qu'on sache de quel locataire il
s'agit.** C'est elle qui le dit.

La cloisonner créerait une dépendance circulaire à l'exécution — pour lire la table des
locataires il faudrait déjà connaître le locataire —, et la politique refuserait chaque
requête faute de variable posée. Le répertoire ne verrait plus rien, et tout sous-domaine
rendrait 404.

Ce qu'il faut assumer en contrepartie : un rôle qui lit cette table voit **tous** les
tenants, c'est-à-dire la liste des clients du cabinet. Elle n'a donc rien à faire dans une
réponse d'interface, et aucune route ne l'expose.

### Le garde-fou a exigé que l'exemption soit nommée

`test_toute_table_cloisonnee_porte_sa_colonne` a refusé la table, et son message disait
déjà quoi faire : « hériter de `Cloisonne`, ou justifier l'exemption ici ». Le mécanisme
d'exemption n'existait pas encore — aucune table n'en avait eu besoin. Il existe
maintenant, avec deux gardes de plus :

* une exemption **sans raison écrite** fait échouer la suite. Une exemption sans
  justification est une fuite qu'on a cessé de voir ;
* une exemption qui ne correspond plus à aucune table fait échouer la suite aussi. Elle
  laisserait croire qu'une table échappe au cloisonnement alors qu'elle a disparu, ou
  qu'elle porte désormais la colonne.

### L'unicité du slug est posée sur une expression

Un nom d'hôte est insensible à la casse : « Station » et « station » désignent le même
serveur. Une contrainte ordinaire les laisserait coexister, et deux tenants se
disputeraient le même sous-domaine — le premier trouvé gagnerait, et lequel dépendrait du
plan d'exécution.

L'index porte donc sur `lower(slug)`, et il a été **éprouvé sur la base** : la seconde
insertion est refusée.

C'est aussi lui qui arbitre deux souscriptions simultanées. La base tranche, jamais une
lecture suivie d'une écriture : entre les deux, l'autre a eu le temps d'écrire.

### Trois colonnes promues, et pourquoi ces trois-là

Un tenant est un agrégat toujours lu entier, donc conservé comme document. Sortent du
document ce sur quoi trois questions se posent en SQL : le `slug` pour la résolution et son
unicité, le `statut` et l'`etape_atteinte` pour que l'ordonnanceur retrouve les ouvertures
interrompues et sache **où** les reprendre.

Elles sont réécrites depuis le document à chaque enregistrement, jamais saisies à part :
c'est ce qui les empêche de diverger de la vérité qu'elles résument.

### Ce que le dépôt n'est pas

Il n'est **pas** destiné à être appelé à chaque requête. La résolution d'un nom d'hôte doit
rester une lecture de dictionnaire ; ce dépôt sert à garnir le répertoire en mémoire au
démarrage et à le rafraîchir. Le brancher directement sur la passerelle ajouterait un
aller-retour en base au chemin critique de tout le trafic.

Un test vérifie que les deux implémentations rendent la même chose sur les mêmes données :
la passerelle ne doit pas savoir laquelle elle emploie.

---

## Pas 9 — Le garnissage, qui ferme la boucle

La table existait, le dépôt la lisait, et **le répertoire restait vide**. Une pièce
posée sans être branchée n'est pas une pièce posée.

* `garnir_le_repertoire()` verse la table dans le répertoire en mémoire.
* Un cycle de vie sur l'application l'appelle **avant la première requête**.

### Pourquoi avant la première requête, et pas à la première

Parce que la première requête serait celle d'un vrai client, sur un vrai sous-domaine. La
faire échouer pour amorcer un cache est un compromis qu'on ne fait pas quand la
préparation ne coûte qu'une lecture au démarrage.

### Le garnissage n'échoue jamais le démarrage

Décision qui mérite d'être écrite, parce que l'instinct dit le contraire.

Une base injoignable au démarrage laisse un répertoire vide, donc un 404 sur tous les
sous-domaines. C'est désagréable, mais **franc** : le client voit un refus, pas une page
qui traîne. Refuser de démarrer, en revanche, priverait aussi la vitrine publique et la
sonde de santé — qui n'ont besoin d'aucun tenant, et dont l'une est précisément ce qui
permet à la supervision de dire que quelque chose ne va pas.

La panne se voit au journal et à la sonde, pas par un processus qui ne se lève pas.

### Ce qui reste à faire, et qui se voit déjà

Un répertoire garni une fois **se périme au premier changement**. Un tenant suspendu
continuerait d'être servi jusqu'au redémarrage suivant, et un tenant fraîchement ouvert
rendrait 404 alors que son client vient de payer.

Le rafraîchissement sur événement d'ouverture ou de suspension est écrit dans la docstring
comme ce qui manque, plutôt que laissé à découvrir. En attendant le bus, un redémarrage
suffit — ce qui est acceptable pour une souscription par jour, et ne le sera plus pour
dix.

### Le garde-fou d'architecture, une troisième fois

`transverse` importait les entrailles de `tenants` au lieu de sa surface publique. Le
dépôt SQL rejoint donc `tenants/api.py`, avec sa raison écrite : il est exposé **pour le
garnissage et pour cela seulement**, pas pour le chemin critique où la résolution doit
rester une lecture de dictionnaire.

Trois fois sur ce chantier, ce test a transformé un branchement rapide en décision écrite.
C'est exactement ce qu'on lui demande.

---

## Le chantier est terminé

Neuf pas, de la mesure de référence au répertoire garni. **1 256 tests au départ, 1 515 à l'arrivée
avec PostgreSQL, aucune régression durable à aucun pas.**

Ce qui existe maintenant : un locataire résolu du sous-domaine et établi au bord, refusé
par défaut plutôt que deviné, protégé par un filtre ORM inoubliable **et** par la sécurité
au niveau des lignes, vérifié par une boucle qui couvre automatiquement les tables futures,
et un mandat qui permet au centre de travailler chez ses clients sans accès transversal.

### Ce que le chantier a corrigé en cours de route

Deux fois, le code a contredit la conception, et c'est la conception qui avait tort :

* **La décision D3** — le schéma par tenant — a été révisée après lecture du code. Le
  mécanisme de cloisonnement existait déjà, éprouvé, et deux des trois arguments que
  j'avais donnés pour les schémas ne tenaient plus. Voir le pas 3.
* **Ma revue de code** disait « le multi-tenant n'existe pas ». Il n'existait pas le
  *multi* ; le mécanisme, lui, était là.

Et une fois, l'outillage a rattrapé une régression que rien d'autre n'aurait vue :
trente-huit tests étaient ignorés faute de base, et trois d'entre eux cassaient depuis le
pas 3. Voir le pas 4.

### Ce qui reste, et qui n'est pas de ce chantier

* ~~**Le rafraîchissement du répertoire.**~~ **Fait au pas 122**, le 18 septembre 2026 :
  le répertoire se recharge tout seul quand la fenêtre de fraîcheur est passée, trente
  secondes par défaut. Voir le pas 122 du journal `13-parcours-d-acquisition.md`, qui dit
  pourquoi une fenêtre plutôt qu'un événement : le répertoire vit dans chaque processus,
  et un abonnement en mémoire ne préviendrait qu'une réplique sur trois.
* ~~**La double vérification** du tenant du jeton contre celui du domaine.~~ **Faite au
  pas 126**, le 18 septembre 2026 : le témoin de session porte le locataire où il a été
  ouvert, et le bord le confronte à celui du domaine. Mesuré avant correction, en mémoire,
  un témoin ouvert sur un sous-domaine était accepté sur un autre. Voir le pas 126 du
  journal `13-parcours-d-acquisition.md`. Le mandat, lui, reste à brancher : c'est ce qui
  permettra à cette confrontation de rendre autre chose qu'un refus.
* ~~**L'audit sous mandat.**~~ **Fait au pas 127**, le 18 septembre 2026, en même temps que
  le branchement du mandat lui-même : il se stocke, il s'accorde, il se révoque, il
  s'exerce au bord, et chaque entrée du journal écrite sous mandat le nomme. Voir le
  pas 127 du journal `13-parcours-d-acquisition.md`.
* ~~**Les deux rôles PostgreSQL** en exploitation.~~ **Fait au pas 128**, le 18 septembre
  2026 : le script d'installation `outils/roles-postgresql.sql` est désormais **joué à
  chaque passage de la suite**, dans une base neuve, et neuf cas constatent ce qu'il rend
  vrai. Il était écrit depuis le chantier et n'avait jamais été exécuté.

**Le chantier du socle multi-tenant est clos.** Ses quatre restes ont été soldés aux pas
122, 126, 127 et 128.
