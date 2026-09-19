# Séance de démonstration

Une séance conduite dans cet ordre tient environ **45 minutes**. Elle suit un seul
dossier du début à la fin, plutôt que de sauter d'écran en écran : c'est ce qui la
rend cohérente, et c'est ce qui permet à quelqu'un qui ne connaît pas le produit de
suivre sans qu'on lui explique la structure.

---

## Avant de commencer

```bash
Backend_erp_cga/outils/pile-de-demonstration.sh neuve
```

Quatre secondes. La base est **recréée**, le jeu de démonstration versé, l'API et le
front démarrés.

⚠️ **Lancer `neuve` avant chaque séance, pas seulement la première.** Deux raisons,
et la seconde surprend toujours :

1. Une séance précédente a laissé des écritures, des dépôts, des contre-passations.
   Les compteurs annoncés plus bas ne correspondront plus.
2. **Le limiteur de connexions retient 30 tentatives par tranche de 5 minutes, en
   mémoire.** Une séance qui enchaîne les changements de compte l'épuise, et les
   connexions suivantes sont refusées. Le produit a alors l'air cassé alors qu'il
   se défend. `neuve` redémarre l'API, ce qui remet le compteur à zéro.

| Commande | Effet |
|---|---|
| `neuve` | recrée la base, verse la démo, démarre tout. **À faire avant chaque séance.** |
| `demarrer` | monte ce qui manque sans rien détruire |
| `etat` | ce qui tourne, sur quels ports, dans quel mode |
| `arreter` | coupe API et front, laisse la base |

Le mot de passe de tous les comptes de démonstration est celui du fichier
`Docs/recette/verifier_profils.py`. Le front est sur **http://localhost:3011**.

---

## Le fil conducteur

Deux dossiers, et deux seulement. En ajouter brouille le propos.

| Dossier | NIU | Rôle dans la séance |
|---|---|---|
| **AGRO-NKOLO SA** | `M065544332211L` | le dossier de production : pièces, écritures, paie, liasse |
| **SARL BATIMENT PLUS** | `M081234567890P` | le dossier de l'adhérent connecté, pour prouver le cloisonnement |

---

## Acte I · Ce qu'un cabinet fait tous les jours (12 min)

**Compte : `l.fotso@cga-brcg.cm`, comptable.**

| # | Écran | Ce qu'il faut montrer |
|---|---|---|
| 1 | Tableau de bord | Le portefeuille du comptable, et lui seul. Quatre dossiers, pas six. |
| 2 | Pièces justificatives | La boîte de réception. Une pièce arrive, elle attend un contrôle. |
| 3 | Pièce `F-2026-0412` | Le rapport de conformité : chaque constat nomme sa règle, son fondement et le paramètre employé. |
| 4 | **Comptabilité › Saisie** | Passer une écriture en direct devant le client. |

**Sur l'écran de saisie, trois choses à dire pendant qu'on tape :**

- Le compteur débit/crédit s'affiche en direct **mais n'autorise rien**. Le bouton
  n'est jamais désactivé par une addition faite dans le navigateur. Un formulaire
  qui se bloque tout seul refuserait un jour une écriture juste, et le comptable
  n'aurait aucun recours.
- **Aucun équilibrage automatique de la dernière ligne.** C'est le confort qu'on
  attend, et il est écarté : complété d'office, le montant n'est plus relu, et une
  erreur amont donne une écriture équilibrée et fausse. Plus aucun contrôle ne la
  rattrape.
- L'écran **fonctionne sans JavaScript**. C'est ce qui a dicté sa forme : huit
  lignes offertes plutôt qu'un bouton « ajouter une ligne ».

**Puis provoquer un refus, délibérément.** Saisir 150 000 au débit et 140 000 au
crédit. Le refus dit : « écriture AC/n déséquilibrée : débit 150000, crédit 140000,
écart 10000. » Pas un dump technique : une phrase qu'un comptable lit.

---

## Acte II · Ce qu'aucun tableur ne fait (10 min)

C'est l'acte qui vend. Tout le reste, un client pense pouvoir le faire autrement.

**Toujours `l.fotso`.** Ouvrir la pièce **`F-2026-0424`** du dossier BATIMENT PLUS :
sable de rivière, **418 000 FCFA hors taxes, soit 498 465 TTC, réglés en espèces**.

Le rapport émet deux constats, de deux natures différentes, et c'est ce contraste
qu'il faut faire voir :

| Constat | Sévérité | Ce qu'il dit |
|---|---|---|
| `FAC-ID-003` | **Bloquant** | La facture ne porte pas le NIU du fournisseur. Mention obligatoire : la pièce n'est pas recevable. |
| `FAC-ACH-007` | **Majeur** | Le règlement en espèces dépasse le seuil légal. La TVA n'est pas déductible. |

Puis dérouler le rapport jusqu'aux **paramètres employés** : il conserve
`SEUIL_ESPECES_DEDUCTIBILITE_TVA = 100000`, statut `VALIDE`, avec sa date d'effet.
Un contrôle de 2026 reste ainsi reproductible en 2028, même si le seuil change
entre-temps.

> **La phrase à dire, et elle est vraie, vérifiable, datée.** Cette facture ne
> produisait **pas** le constat de TVA avant le 18 août 2026. Le référentiel portait
> 500 000 FCFA, et 498 465 passait juste en dessous. Le seuil légal est de 100 000 :
> CGI art. 143, « pour les opérations taxables d'une valeur au moins égale à cent
> mille (100 000) F CFA, le droit à déduction n'est autorisé qu'à condition que les
> dites opérations n'aient pas été payées en espèces ». Cinq fois trop permissif.
> L'erreur ne se voyait pas à la saisie ; elle se serait vue au contrôle, en rappel
> de TVA sur trois exercices.

Enchaîner sur **Référentiel et règles**, chercher `SEUIL_ESPECES_DEDUCTIBILITE_TVA`,
et montrer ce que porte la fiche : la valeur, l'article visé, **la source réellement
consultée**, la date d'effet, le nom du signataire, et la note qui garde la trace de
la correction.

**Le point à marteler :** aucune valeur légale n'est écrite dans le code. Elles sont
datées, sourcées, signées. Une loi de finances se répercute en modifiant un fichier,
pas en attendant une version du logiciel.

**Si on veut pousser la démonstration d'un cran**, ouvrir aussi `F-2026-0422`, une
facture en espèces du CABINET NGUEMA CONSEIL, accessible au compte
`c.ndongo@cga-brcg.cm`. Elle **ne produit aucun constat**, et c'est voulu : NGUEMA
relève du régime synthétique, qui ne récupère jamais la TVA. Elle est un coût
définitif, incorporé au prix d'achat, que le règlement soit en espèces ou non. Lui
annoncer une « TVA non déductible » énoncerait un préjudice inexistant, et une règle
écartée à chaque fois finit par être ignorée le jour où elle a raison.

## Acte III · Ce qui protège le cabinet (10 min)

**Changer de compte, et le faire voir.**

| # | Compte | Ce qu'on prouve |
|---|---|---|
| 5 | `jp.nkoa@batimentplus.cm`, adhérent | Il ne voit que **son** dossier. Ouvrir l'autre dossier renvoie 404, pas 403 : on ne lui apprend même pas qu'il existe. |
| 6 | `c.ndongo@cga-brcg.cm`, second comptable | Un autre portefeuille. `l.fotso` recevrait 404 sur ses dossiers. Ce n'est pas de l'ergonomie, c'est le secret professionnel. |
| 7 | `a.bouba@cga-brcg.cm`, réviseur | Voit tout le portefeuille, **et n'accède pas au pilotage**. Voir les dossiers n'est pas piloter le cabinet. |
| 8 | `g.atangana@inspection.cm`, inspecteur | Externe en mission datée : lecture et avis, rien d'autre. |

**Puis revenir sur l'écriture de l'acte I, en comptable :**

- La valider. Elle se fige, et porte le nom de qui l'a validée et quand.
- Tenter de la revalider : **409**.
- La contre-passer : le motif est **exigé avant l'acte**, pas après. Reconstitué
  plus tard, un motif n'est plus un motif, c'est une justification.
- **Il n'y a aucun bouton « supprimer », et il n'y en aura jamais.** Le port du
  registre ne déclare aucune méthode de suppression. Une comptabilité d'où l'on
  peut retirer une ligne n'est pas une comptabilité : un vérificateur le voit au
  premier trou de numérotation.

---

## Acte IV · Ce que ça donne en haut (8 min)

**Compte : `b.mballa@cga-brcg.cm`, direction.**

| # | Écran | Ce qu'il faut montrer |
|---|---|---|
| 9 | Pilotage | Les dossiers rangés **par risque, jamais par nom**. |
| 10 | Un score | Le descendre jusqu'à la pièce qui le cause. Un score qu'on ne peut pas expliquer ne sert à personne. |
| 11 | Obligations | L'échéancier calculé, pas ressaisi. |
| 12 | Clôture | La liasse, et le système de présentation **constaté** et jamais choisi. |

**À dire sur le pilotage :** les poids du score ne relèvent d'aucun texte. Ce sont
des réglages de la direction, arrêtés le 18 août 2026, et le référentiel le dit :
ils portent la nature `POLITIQUE_CABINET` là où un taux de TVA porte `LOI`. Une
direction qui devrait demander un déploiement pour changer un poids ne pilote pas.

---

## Acte V · Ce qui n'est pas fait (5 min)

**C'est l'acte qui installe la confiance.** Un vendeur qui n'a rien à concéder
inquiète, et le client trouvera les manques tout seul, plus tard, sans nous.

Poser le **cahier de recette** (`Docs/cahier-de-recette-cga.pdf`, 6 pages) et
**laisser le client le feuilleter**. Section 8 : les réserves, écrites noir sur
blanc.

Ce qu'il faut annoncer soi-même, avant qu'on le demande :

| | |
|---|---|
| **Neuf valeurs légales sur 59** ne sont pas confirmées, et tout rapport qui s'en sert le signale |
| **Le dépôt de pièce, le dépôt de déclaration et le tunnel de création** n'ont pas encore d'écran. Les routes existent, le formulaire manque |
| **La clôture d'exercice** n'a aucune route d'écriture : le cycle annuel ne se ferme pas encore dans le logiciel |
| **Un seul cabinet** est servi : 51 points d'appel emploient le locataire par défaut |
| **La DGI ne publie aucune interface** : le bordereau est fait pour être recopié sur le portail, et l'accusé revient par une route de constat |
| **La plateforme n'a jamais été déployée.** La configuration de production refuse de démarrer sans SMTP, sans identifiants de paiement réels et sans TLS |

Puis poser la **fiche de contreseing**
(`Docs/fiche-de-contreseing-referentiel.pdf`, 8 pages) : une case à cocher par
paramètre, valeur et source en regard, deux blocs de signature selon que la valeur
relève d'un texte ou d'un arbitrage interne.

> C'est le document qui transforme « faites-nous confiance » en « vérifiez, et
> signez ce que vous confirmez ».

---

## Si quelque chose casse pendant la séance

| Symptôme | Cause quasi certaine | Geste |
|---|---|---|
| Une connexion est refusée alors que le mot de passe est bon | Limiteur épuisé, 30 par 5 min | `pile-de-demonstration.sh neuve` |
| Une page renvoie « Method Not Allowed » | L'API tourne dans une version antérieure aux routes | `neuve` |
| Le front affiche un écran d'avant | Build autonome périmé | `(cd Frontend_erp_cga && npx next build)` puis `neuve` |
| Toutes les pages redirigent | Front démarré sans `HOSTNAME=0.0.0.0` | `neuve`, qui le pose |
| Les compteurs ne correspondent pas au document | Séance précédente non remise à zéro | `neuve` |

**Ne jamais déboguer devant le client.** Relancer `neuve` prend quatre secondes et
répare tout ce qui figure au tableau.

---

## Pour prouver plutôt que montrer

Si l'interlocuteur est technique, ou s'il demande sur quoi reposent ces affirmations,
faire tourner les parcours devant lui. Chacun est lisible à l'écran et sort un
compte final.

```bash
python3 Docs/recette/cas_usage.py          # les 64 cas d'usage, avec leur preuve
python3 Docs/recette/flux_saisie.py        # la saisie, du formulaire à la contre-passation
python3 Docs/recette/verifier_profils.py   # qui accède à quoi, matrice complète
```

⚠️ **Redémarrer l'API entre deux parcours** (`neuve`), sinon le limiteur produit une
trentaine de faux échecs et le produit passe pour cassé alors que c'est la
protection qui fonctionne.
