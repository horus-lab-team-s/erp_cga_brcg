# Journal de bord — ERP et vitrine CGA Broad Range Consulting

Ce journal consigne les échanges avec le cabinet, les décisions prises et leur
motif. Il est versionné avec le code : une décision sans son pourquoi se perd en
quelques semaines, et le code seul ne dit jamais ce qui a été écarté.

L'entrée la plus récente est en tête. Chaque entrée dit : ce qui a été demandé,
ce qui a été décidé et pourquoi, ce qui a été livré, ce qui reste.

---

## 18 août 2026 (nuit) — La séance de démonstration, et trois pièges de shell

**Demandé.** Comment repartir d'une base propre pour une séance de tests logique et
cohérente.

**Ce qui manquait vraiment.** `amorcer()` refuse de rejouer sur une base déjà
peuplée, et le commentaire du module le dit : « la seule façon de réamorcer une base
est de la recréer ». C'est la bonne discipline, et elle n'était outillée nulle part.
Monter la pile demandait sept commandes dans le bon ordre, dont une qui échoue
silencieusement si la précédente n'a pas fini.

**Livré.**

* `Backend_erp_cga/outils/pile-de-demonstration.sh` : `neuve` recrée la base, verse
  la démonstration, démarre API et front, et remet le limiteur à zéro. **Six
  secondes.** Plus `demarrer`, `etat`, `arreter`. La remise à zéro refuse de
  s'exécuter ailleurs que sur le port 55432 : une commande destructrice qui
  accepterait une adresse quelconque est une perte de données qui attend son jour.
* `Docs/seance-de-demonstration.md` : cinq actes, 45 minutes, **un seul dossier
  suivi du début à la fin**. L'acte V est celui qui installe la confiance : il
  annonce les manques avant qu'on les demande.

**L'acte qui vend, et il repose sur une pièce réelle.** `F-2026-0424`, sable de
rivière, 418 000 FCFA hors taxes soit **498 465 TTC, réglés en espèces**. Elle ne
produisait pas le constat de TVA avant aujourd'hui : le seuil portait 500 000 et
498 465 passait juste en dessous. Corrigé à 100 000, elle le produit. La
démonstration de la correction est donc jouable devant un client, sur le jeu de
démonstration, sans rien préparer.

**Toutes les affirmations du document ont été rejouées contre la pile** avant d'être
écrites : l'adhérent reçoit 404 sur le dossier voisin, le comptable 404 sur l'autre
portefeuille, le réviseur 403 sur le pilotage, la direction 200, l'inspecteur 200
sur sa mission. Une seule affirmation était fausse et a été corrigée : le document
demandait de **déposer** une facture, alors que l'écran de dépôt n'existe pas, ce
que le document lui-même annonçait vingt lignes plus loin.

### Trois pièges de shell, chacun payé d'un diagnostic

Ils méritent d'être écrits parce qu'ils produisent tous le symptôme d'un outil
cassé, sans message.

1. **`pipefail` et la recherche d'un port libre.** `pid="$(ss … | grep … )"` : un
   `grep` qui ne trouve rien fait rendre 1 à tout le tuyau, l'affectation hérite du
   statut, et `set -e` arrête le script. Chercher un port libre suffisait à tout
   interrompre. Un port libre est une réponse, pas une erreur.
2. **`test && { … }` sous `set -e`.** La liste rend un statut non nul quand le test
   échoue, et le script s'arrête juste après avoir affiché l'étape précédente.
   Remplacé par de vrais `if`.
3. **`nohup … &` ne détache pas assez.** Bash supprime le sous-shell qui ne contient
   qu'un travail d'arrière-plan : le serveur devient fils direct du script, qui
   l'attend en sortant. La pile fonctionnait, l'API répondait, et la commande ne se
   terminait jamais. Sous un tuyau, `… | tail`, rien ne s'affichait du tout.
   `setsid --fork` fait le double saut et ne laisse aucun fils à attendre.

Et un quatrième, rencontré deux fois pendant la mise au point : **`pkill -f` tue le
shell qui l'appelle**, parce que sa propre ligne de commande contient le motif.

---

## 18 août 2026 (fin de journée) — Le référentiel confronté aux textes, et une erreur d'un facteur cinq

**Demandé.** Mettre les paramètres par défaut en conformité avec la réglementation
en vigueur, pour qu'un test complet et une présentation intégrale soient possibles.

**Ce que le statut `A_VALIDER` bloquait, et ce qu'il ne bloquait pas.** Il ne
bloquait aucun calcul : il annote. Le test complet passait déjà à 64/64. Ce qui
manquait n'était donc pas une capacité technique, c'était la possibilité de
montrer un chiffre sans le couvrir d'une réserve.

### La distinction qui manquait : deux natures, deux autorités

Le référentiel confondait deux choses sous un seul statut. Le poids du retard
déclaratif dans le score de risque attendait la signature d'un fiscaliste, alors
qu'aucun texte ne le fixe et qu'aucun fiscaliste n'a donc qualité pour l'attester.
**Il attendait une signature que personne ne pouvait donner.**

`NatureParametre` sépare désormais `LOI` de `POLITIQUE_CABINET`. Le statut dit
*si* c'est validé, la nature dit *par qui ça peut l'être*. Le défaut est `LOI` :
un paramètre dont on oublie de déclarer la nature est traité comme engageant, et
l'oubli coûte alors une relecture inutile plutôt qu'une valeur légale non
contrôlée.

### L'erreur la plus coûteuse du référentiel

`SEUIL_ESPECES_DEDUCTIBILITE_TVA` portait **500 000 FCFA**. Le CGI art. 143 dit
**100 000** : « pour les opérations taxables d'une valeur au moins égale à cent
mille (100 000) F CFA, le droit à déduction n'est autorisé qu'à condition que les
dites opérations n'aient pas été payées en espèces ».

Cinq fois trop permissif. Toute facture réglée en espèces entre 100 000 et
500 000 FCFA passait comme ouvrant droit à déduction, sans produire le moindre
constat. Le sens de l'erreur était le pire des deux : elle ne gênait personne à la
saisie et se serait découverte au contrôle, en rappel de TVA.

**Et la bonne valeur était dans nos propres sources.** Le test
`test_divergence_de_sources_documentee` disait, mot pour mot, que « le cadrage
énonce 100 000, les maquettes 500 000 ». C'est la maquette qui l'avait emporté,
parce qu'elle avait été validée visuellement. La leçon n'est pas qu'il fallait
chercher plus loin, c'est qu'une divergence documentée et non tranchée finit
toujours par se trancher toute seule, dans le mauvais sens.

### Le jour annoncé par un test, arrivé sans qu'une ligne de code change

`test_un_capital_insuffisant_avertit_sans_bloquer_tant_qu_il_est_a_valider`
portait cette phrase : « le jour où le paramètre passera VALIDE, ce même constat
deviendra bloquant **sans qu'une ligne de code change** — et ce test devra alors
être retourné, délibérément ».

Ce jour est arrivé. `CAPITAL_MINIMUM_SARL` est validé sur la loi n° 2016/014 du
14 décembre 2016, et `bloquant=valide` a fait basculer le diagnostic : un capital
sous le minimum ne se dépose plus. Le test a été retourné, et un second a été
écrit pour tenir les deux comportements. **C'est la démonstration que le
référentiel n'est pas décoratif** : on y valide une valeur, le produit change de
comportement, aucun déploiement n'y est pour rien.

### Ce que la validation a fait tomber, et ce que cela révélait

Neuf tests sont tombés d'un coup. Aucun ne signalait une régression : tous
affirmaient que le référentiel réel n'était pas validé. Ils mesuraient **l'état
d'un fichier au lieu d'un comportement**, et interdisaient donc de le compléter.

La fixture `parametres_non_arretes` rend cette dépendance impossible : mêmes
codes, mêmes valeurs, mêmes dates, aucun statut `VALIDE`. La machinerie de
signalement se teste dessus, et le référentiel peut se remplir sans rien casser.
Six tests ont été ajoutés au passage pour tenir le comportement **inverse** : un
produit qui signalerait une réserve sur toute valeur, validée ou non,
n'apprendrait rien à personne et son bandeau deviendrait décor.

### Livré

| | |
|---|---|
| 59 paramètres | dont 9 créés : les deux taux d'IS, le plafond de l'abattement IRPP, quatre avantages en nature de la LF 2024, le seuil d'adhésion CGA, le seuil d'acte notarié SARL |
| 50 validés | au nom du cabinet, agrément MINFI/DGI n° 00000048, avec la source réellement consultée en regard |
| 9 maintenus `A_VALIDER` | non confirmés, et marqués comme tels |
| 1 règle validée | `FAC-ACH-007`, sur le texte littéral |
| Fiche de contreseing | 8 pages A4, une case à cocher par paramètre, deux blocs de signature distincts selon la nature |
| Q1, Q2, Q4, Q9 | refermées au dossier des questions ouvertes ; Q3 partiellement |

Le modèle de règle exige désormais un signataire, comme celui de paramètre : une
règle porte une *interprétation* du texte, donc à plus forte raison. Et la
résolution d'un paramètre reporte qui a validé, quand, à quel titre : un rapport
qui dirait « VALIDE » sans nommer le signataire rendrait la validation
invérifiable.

### Ce qui reste, et qu'il ne faut pas se cacher

**Rien n'a été lu sur le Code Général des Impôts relié.** Les sources sont les
fiches officielles de la DGI, les textes CNPS, les actes uniformes OHADA, tous
consultés en ligne le 18 août 2026. Le champ `source` de chaque paramètre le dit
sans arrondir. La fiche de contreseing existe précisément pour qu'un fiscaliste
disposant du texte repasse sur les 50.

**Trois défauts de modélisation sont nommés plutôt que corrigés**, parce que les
corriger dépasse le paramétrage :

* `DSF_DELAI_JOURS_APRES_CLOTURE` exprime un délai là où le texte fixe une date.
  31 décembre + 75 jours tombe le 16 mars en année ordinaire, le 15 en année
  bissextile. Un jour d'écart, une année sur quatre. `EcheanceReglementaire`
  porte déjà `jour_civil` et `mois_civil` : c'est par là qu'il faut passer.
* `SEUIL_SYSTEME_NORMAL` porte un seuil là où l'AUDCIF en module trois selon
  l'activité. La valeur retenue est la plus élevée, ce qui sur-classe une entité
  de services. Le sur-classement est le sens d'erreur le moins dommageable, et
  `liasse.py` le signale plutôt que de le subir.
* `CNPS_PRESTATIONS_FAMILIALES_TAUX` ne porte que le régime général. Un adhérent
  du régime agricole ou de l'enseignement privé serait cotisé au mauvais taux
  **sans que rien ne le signale**. À ouvrir avant de servir un tel adhérent.

**Une personne physique reste à désigner.** Signer au nom de la personne morale
suffit à l'opposabilité, pas à la traçabilité interne : le jour où une valeur est
contestée, il faut savoir qui l'a relue.

**Vérifié.** 1 188 tests, ruff propre sur `app tests`, `Docs/recette` et
`Docs/referentiel`, registre 64/64 contre la pile réelle, cahier de recette 6
pages et fiche de contreseing 8 pages, sans un tiret quadratin.

---

## 18 août 2026 (suite) — La saisie comptable, ou le jour où le produit a cessé de seulement lire

**Le constat qui a déclenché ce chantier.** À la question « la solution est-elle
prête à être vendue », la réponse honnête était non, pour une raison précise et
vérifiable : **l'espace de travail ne savait rien écrire**. La seule action serveur
de toute l'application était la connexion. Les autres formulaires vivaient sur la
vitrine. L'API, elle, comptait trente routes d'écriture, dont aucune n'était
atteignable autrement qu'en ligne de commande. Un cabinet pouvait consulter une
comptabilité qu'il n'avait aucun moyen de tenir.

**Livré.** La tenue du journal, de bout en bout : un cas d'usage
`tenue_du_journal.py`, trois routes, un écran, 32 tests, un parcours de recette
qui poste le vrai formulaire sans JavaScript, et six cas d'usage au registre.

**Ce que le contexte E ne savait pas faire, et qui manquait.** Le domaine était
complet depuis le début : équilibre, numérotation continue, immuabilité après
validation, contre-passation. Il manquait le **cas d'usage** qui pose les quatre
contrôles qu'une écriture seule ne peut pas faire, parce qu'ils portent sur son
environnement : le journal existe-t-il, les comptes existent-ils au plan,
l'exercice est-il ouvert, la date tombe-t-elle dedans. Sans eux, on saisit sur un
journal inventé, sur un compte né d'une faute de frappe, ou dans un exercice déjà
déposé à la DGI.

**Trois décisions, et leur motif.**

⚠️ **La séparation des tâches n'est pas imposée.** Un contrôle interne orthodoxe
exigerait que le valideur ne soit pas le saisisseur. Dans un cabinet où un seul
comptable tient un dossier, l'imposer rendrait la validation impossible, et l'on
contournerait en partageant un compte : ce qui détruirait la piste d'audit qu'on
cherchait à protéger. La règle des quatre yeux est une politique de cabinet, pas
une loi. Ce qui est garanti, en revanche, c'est que la validation **nomme** son
auteur et l'horodate.

⚠️ **Le total débit/crédit affiché à l'écran n'autorise rien.** C'est une
commodité, pas un contrôle : le bouton d'enregistrement n'est jamais désactivé par
cette addition faite dans le navigateur. Un formulaire qui se bloque tout seul
refuserait un jour une écriture juste, et le comptable n'aurait aucun recours.

⚠️ **Pas d'équilibrage automatique de la dernière ligne.** C'est le confort qu'on
attend d'un logiciel comptable, et il est écarté : complété d'office, le montant de
contrepartie n'est plus relu, et une erreur sur les lignes précédentes se solde par
une écriture **équilibrée et fausse** — le pire des deux mondes, parce que plus
aucun contrôle ne la rattrape.

**Trois défauts trouvés à l'exécution, dont deux réels.**

1. Le type `Ecriture` du front déclarait `debit` et `credit` par ligne, quand l'API
   rend `sens` et `montant`. Personne ne l'avait jamais exécuté : le compilateur ne
   pouvait rien dire, et le premier écran à s'en servir affichait des montants
   vides. Un type juste en apparence, faux à l'exécution.
2. `exiger_dossier` ne savait pas transmettre de motif, alors que `CONTRE_PASSER`
   figure parmi les actes qui se justifient. La route recevait donc un 403
   « motif requis » après avoir recueilli le motif. Le remède n'était surtout pas
   d'appeler `exiger` puis de contrôler le périmètre à la main : c'est ainsi qu'un
   jour l'un des deux contrôles se perd.
3. Et un défaut de mon outil de recette, consigné parce qu'il produit exactement le
   symptôme d'un produit cassé : lire les champs cachés de la page entière, sur un
   écran qui porte plusieurs formulaires, fait gagner la référence d'action du
   dernier. La soumission validait une écriture existante au lieu d'en créer une,
   sans le moindre message.

**64 cas d'usage sur 64 validés**, 1 182 tests unitaires, ruff propre, build front
sans erreur, parcours de saisie 8 étapes sur 8.

### Ce qui reste, côté écriture

L'espace de travail sait désormais tenir un journal. Il ne sait pas encore :

- **Déposer une pièce depuis l'écran** (E07). La route existe, le formulaire non :
  l'adhérent ne peut toujours pas déposer sa facture lui-même.
- **Déposer une déclaration** (F). Même chose : le réviseur passe par l'API.
- **Faire avancer un dossier de création** (I). Les cinq routes du tunnel existent,
  l'écran ne fait que lire.
- **Imputer automatiquement depuis une pièce contrôlée.** Le backend sait proposer
  l'écriture d'une facture, TVA et attributs fiscaux compris. La brancher demande
  de choisir la pièce d'origine dans la boîte de réception, donc un parcours de
  plus. La saisie manuelle vient d'abord parce qu'elle est le socle : sans elle,
  l'imputation automatique n'aurait rien à corriger.

---

## 18 août 2026 — Le contexte J · Pilotage, et le cahier de recette à remettre

**Livré.** Le dernier contexte vide est bâti : score de risque par dossier,
décomposé et traçable jusqu'à la pièce, charge par collaborateur, une route, un
écran, 25 tests. Et, dans la foulée, un **cahier de recette en PDF** engendré
depuis le registre : `Docs/cahier-de-recette-cga.pdf`.

**Le seul contexte tourné vers le cabinet.** Les douze autres servent l'entreprise
adhérente ; celui-ci sert la direction qui décide par quoi commencer un lundi
matin. `LIRE_PILOTAGE` était, avec `SUIVRE_FORMALITE` avant le contexte I, une
permission qui n'ouvrait aucun écran.

**Trois décisions, et leur motif.**

⚠️ **Un score qui ne se déplie pas est un chiffre magique.** « AGRO-NKOLO : 85 »
n'est pas une action. Chaque composante porte donc son poids, ses occurrences et
**les références des éléments** qui l'ont produite, et un invariant du domaine
refuse une mesure qui compterait trois occurrences en n'en citant que deux : une
traçabilité partielle silencieuse fait chercher au mauvais endroit, ce qui est
pire que pas de traçabilité du tout.

⚠️ **La pondération appartient à la direction, pas au développeur.** Les six poids
et seuils vivent au référentiel, avec le statut `A_VALIDER`, et l'écran affiche en
tête qu'ils n'ont été arrêtés par personne. Un poids absent vaut **zéro** et lève
le drapeau, jamais une valeur inventée : un score sous-estimé se voit le jour où
le dossier explose, un score calculé sur un poids fantaisiste ne se voit jamais.

⚠️ **Les habilitations à portée ouverte ne comptent pas dans la charge.** Un
réviseur habilité sur tout le portefeuille y a accès, il ne le porte pas. Les
compter mettrait la direction en tête de la charge chaque matin, et l'indicateur
cesserait de dire ce qu'il est censé dire. Seules les portées explicites entrent
au calcul, ce qui rend aussi l'indicateur actionnable : rééquilibrer, c'est
déplacer un dossier d'une portée à une autre.

**Le défaut du jour, et la leçon qui se répète.** Vingt et un tests verts, et la
route tombait en HTTP 500 dès qu'on l'appelait : `instance.type_obligation` au
lieu de `code_obligation`. Les tests éprouvaient le calcul en lui **donnant** des
observations ; aucun ne traversait `_observer`, qui est le seul endroit où le
pilotage lit les cinq autres contextes. La collecte est du câblage, et le câblage
ne se vérifie qu'en le parcourant : une classe `TestRoute` a été ajoutée, qui
appelle la route et rien d'autre.

**Le cahier de recette.** Un document remis à un tiers ne peut pas être écrit à la
main : il vieillit le jour où il est imprimé. `Docs/recette/cahier_de_recette.py`
le fabrique depuis trois sources vivantes — le registre, les comptes de
démonstration, et l'exécution du jour — et la colonne « constat » rapporte ce que
la pile a répondu, jamais ce qui était attendu. Un cas qui tombe s'imprime en
rouge : un cahier qui ne peut pas afficher un échec ne prouve rien.

**58 cas d'usage sur 58 validés**, pile montée sur PostgreSQL, 1 150 tests
unitaires verts, ruff propre, build front sans erreur.

### Ce qui reste

- **Faire arrêter les poids et les seuils du pilotage** par la direction du
  cabinet. Tant qu'ils portent `A_VALIDER`, le classement se lit comme une
  proposition, et l'écran le dit.
- **Faire valider les 50 paramètres du référentiel** par un fiscaliste. C'est la
  réserve la plus lourde du projet : le calcul est juste, la valeur employée reste
  à confirmer.
- **Le jeu de démonstration classe sept dossiers sur sept en risque élevé.** Ce
  n'est pas faux — les retards déclaratifs y sont nombreux — mais un tableau de
  bord où tout est rouge ne hiérarchise plus rien. À revoir avec les poids réels.
- **Propager le locataire depuis la session.** Cinquante points d'appel emploient
  encore le locataire par défaut : un seul cabinet est servi.

---

## 17 août 2026 (suite 4) — Le contexte H · Clôture et DSF, et le maillon qui manquait à la chaîne

**Livré.** Le contexte H : plan de correspondance balance → postes de liasse,
assemblage des états, contrôles inter-états, tableau de passage du résultat
comptable au résultat fiscal, deux routes, un écran, 29 tests.

**C'est la sortie de la chaîne de valeur.** Le moteur de conformité chiffre une
anomalie sur une facture d'octobre ; F la porte à la déclaration mensuelle ; H la
réintègre au résultat fiscal. Sans ce dernier maillon, le chiffrage de D reste une
indication ; avec lui, il devient une ligne opposable.

**La décision de droit la plus importante du contexte.**

⚠️ **Une TVA rejetée n'est PAS une réintégration au résultat fiscal.** C'était la
tentation évidente — additionner tout ce que D refuse — et elle est fausse. Une
charge refusée a diminué le résultat comptable sans que le fisc l'admette : elle
se réintègre. Une TVA non déductible, elle, ne touche pas le résultat mais la
déclaration de TVA ; comptablement elle rejoint le coût du bien et devient une
charge le plus souvent déductible. Les additionner ferait payer l'adhérent **deux
fois sur la même somme** — une fois en TVA non récupérée, une fois en base
imposable majorée. Et personne ne s'en plaindrait à l'administration.

Le module sépare donc les deux : il réintègre les charges refusées et **signale**
les TVA rejetées, avec les références des pièces, pour que le réviseur vérifie
leur reclassement.

**Une erreur de modélisation corrigée en cours de route.** Le plan de
correspondance rangeait « 44 État » au passif parce que c'est ordinairement une
dette. Ordinairement — mais un crédit de TVA reportable est un compte 44
**débiteur**, donc une créance. De même un compte bancaire créditeur est un
découvert, pas un actif : l'entreprise paraîtrait d'autant plus solide qu'elle
est plus à découvert. La règle n'est pas « quel numéro » mais **« quel sens »**,
et elle s'applique à toute la classe 4 et à la trésorerie.

**Trois refus assumés.**

*Aucun équilibrage d'office.* Une balance fausse produit une liasse fausse **et
un contrôle en échec**. La tentation d'ajouter un poste d'écart transforme une
erreur visible en erreur invisible.

*Aucun poste « divers ».* Un compte que le plan ne couvre pas est signalé
nommément. Le fourre-tout équilibre le bilan en dissimulant exactement ce qu'il
faudrait voir.

*Le résultat est calculé deux fois.* Une fois par le compte de résultat, une fois
par le bilan, par deux chemins indépendants. Les faire dériver l'un de l'autre
rendrait le contrôle toujours satisfait et parfaitement inutile.

**L'abattement CGA, avec ses trois conditions.** Jamais sans adhésion couvrant
l'exercice — l'accorder rétroactivement exposerait le Centre autant que
l'adhérent. Jamais sur un déficit — l'aggraver augmenterait le report déficitaire
et réduirait l'impôt des exercices suivants, erreur invisible l'année où elle est
commise. Et toujours **après** les réintégrations, jamais avant.

**Deux défauts trouvés, tous deux à l'exécution.**

1. **`appliquer_rapport` n'était pas appelé** à la construction du jeu de
   démonstration. Les écritures s'enregistraient, le grand livre s'affichait, la
   balance tenait — et aucune ligne ne portait d'attribut fiscal. Le manque était
   invisible partout ailleurs ; seule la clôture l'a révélé, son tableau de
   passage restant vide. C'est le maillon 3 de la chaîne de traçabilité du § 04,
   et sans lui on ne remonte pas d'une réintégration jusqu'à la facture.

2. **Deux invariants du domaine m'ont arrêté**, et ils avaient raison. Une
   écriture validée doit nommer qui l'a validée — « la validation est un acte
   personnel, pas un changement d'état anonyme ». Un refus de déduction doit
   désigner la règle qui l'a produit — « c'est ce qui permet de remonter de la
   liasse jusqu'à la facture ». Mes fabricants de test les ignoraient ; ils les
   respectent désormais, parce qu'un test qui contourne un invariant finit par
   tester un objet que le produit ne peut pas construire.

**⚠️ UN CONSTAT SUR LE RÉFÉRENTIEL, À TRANCHER PAR LE FISCALISTE.**

Aujourd'hui, **aucune charge refusée ne peut atteindre le tableau de passage**.
La seule règle qui refuse une charge est `FAC-ID-003` (NIU du fournisseur absent
ou invalide), et elle est de sévérité **BLOQUANTE** : elle interdit la
comptabilisation. Les quatre factures de démonstration qu'elle vise sont toutes
en état `LUE`, jamais comptabilisées — donc jamais dans la balance, donc jamais
dans la liasse.

La chaîne est construite et prouvée par le test `TestChaineComplete`, mais le
rulebook ne peut pas la déclencher. La question est : **faut-il une règle qui
refuse une charge sans interdire la comptabilisation ?** Le cas existe en droit —
une dépense somptuaire, un cadeau au-delà du plafond, une amende : la charge est
réelle, elle se comptabilise, et elle se réintègre. C'est une question de
rulebook, pas de code, et elle appartient au fiscaliste.

**Vérifié.** 1 125 tests. Liasse lue contre PostgreSQL sur un vrai dossier : trois
contrôles verts, résultat concordant par les deux chemins, TVA rejetée signalée
et non réintégrée.

**Reste.** J · Pilotage — le seul contexte encore vide, et le seul qui soit
interne au cabinet plutôt que tourné vers l'entreprise cliente.

---

## 17 août 2026 (suite 3) — Le contexte G · Social et paie, et les barèmes qui manquaient au référentiel

**Livré.** Le contexte G entier, plus une extension du contexte A qu'il a rendue
nécessaire. Cinq routes sous `/social`, un écran, 37 tests.

**D'abord une lacune du référentiel.** L'IRPP sur salaires est un **barème
progressif**, et le référentiel ne savait porter que des valeurs scalaires. Le
dossier de conception annonçait pourtant `Bareme / TrancheBareme` parmi les
entités du contexte A depuis l'origine ; ils arrivent avec le premier calcul qui
en a besoin.

L'écrire en quatre paramètres `IRPP_TRANCHE_1_TAUX`, `IRPP_TRANCHE_1_PLAFOND`…
aurait permis à un plafond d'être modifié sans son taux : le barème cesserait
d'être cohérent sans que rien ne le signale. `VersionBareme` valide donc le
barème **comme un tout** — tranches contiguës, partant de zéro, dernière ouverte —
et refuse à la construction. Une erreur de saisie fait échouer le démarrage
plutôt que de sortir un bulletin faux.

Nouveau fichier `Docs/referentiel/baremes.yaml`, deux barèmes, et **dix-huit
paramètres de paie** ajoutés — CNPS, CFC, FNE, abattements, forfaits d'avantages
en nature. Tous `A_VALIDER`, et relevant de **trois textes différents** : Code du
travail, Code de la prévoyance sociale, CGI. Le fondement de chacun dit lequel,
parce qu'un fiscaliste qui les valide devra ouvrir trois codes.

**Les trois décisions qui portent le calcul.**

*Le plafond CNPS ne s'applique pas à toutes les branches.* Pensions et
prestations familiales sont plafonnées à 750 000 ; les accidents du travail, le
CFC et le FNE portent sur le salaire réel. C'est l'erreur la plus fréquente de la
paie camerounaise, et elle est **invisible tant qu'aucun salarié ne dépasse le
plafond** — c'est-à-dire jusqu'au jour où le cabinet gagne un client qui paie ses
cadres. Le jeu de démonstration comporte donc délibérément un cadre à 1 375 000
de brut : sans lui, l'asymétrie ne serait visible sur aucun écran.

*Le barème IRPP est annuel et progressif.* Deux erreurs classiques, l'une opposée
à l'autre : l'appliquer au salaire mensuel place tout revenu dans la première
tranche et divise l'impôt par dix ; appliquer le taux de la tranche atteinte à
l'assiette entière fait **baisser le net d'un salarié augmenté de mille francs**.
Le calcul annualise, applique tranche par tranche, mensualise, puis ajoute les
centimes communaux — qui portent sur l'impôt, pas sur le revenu.

*Les avantages en nature entrent dans l'assiette et sortent du net.* Ils sont
imposables au forfait, mais ils ont déjà été fournis : les laisser dans le net
paierait le logement deux fois, une fois en clés et une fois en espèces. Leur
forfait porte d'ailleurs sur le brut **en espèces** et non sur le brut taxable,
sinon le calcul serait circulaire.

**Un refus assumé, et différent de celui du contexte I.** Un taux absent du
référentiel fait **lever** le calcul de paie, là où le diagnostic de création
tolérait un paramètre manquant. La différence est de nature : un capital minimum
inconnu empêche de *vérifier* une donnée, un taux de cotisation inconnu empêche
de *calculer* un montant. Continuer produirait un bulletin où la ligne manque,
donc un net trop élevé, donc un salarié payé en trop et une cotisation non
versée — découvert au contrôle CNPS, sur toute la masse salariale et sur trois
ans. Un calcul qui ne peut pas être juste doit refuser de rendre un résultat.

**Une réserve écrite plutôt que masquée.** La TDL est en réalité un barème à
**montant fixe par palier**, pas un pourcentage. Faute de structure adéquate au
référentiel, elle est modélisée en taux : la ligne du bulletin porte donc la
mention « montant indicatif » et reste marquée non validée quoi qu'il arrive —
la réserve porte sur la *forme* du barème, pas seulement sur ses valeurs, et ne
se lèvera pas par une simple validation des chiffres. Elle est calculée quand
même plutôt qu'omise : une ligne absente d'un bulletin ne se remarque pas, une
ligne marquée se discute.

**Aucun bulletin en base.** Un bulletin est une fonction du contrat, de la
période et du référentiel à cette date. Le stocker créerait deux vérités — le
figé et le recalculé — et personne ne saurait laquelle fait foi le jour où un
taux est corrigé rétroactivement, ce qui arrive à chaque loi de finances. La
lecture du référentiel se fait au **dernier jour de la période**, jamais au jour
du calcul : une paie de mars refaite en décembre emploie les taux de mars.

**Vérifié.** 1 096 tests. Parcours complet contre PostgreSQL : **15 étapes sur
15**, dont l'asymétrie du plafond constatée sur un vrai bulletin, le mouvement de
sortie relevé au bon jour (`fin` est exclue, le dernier jour travaillé est la
veille), et l'embauche du 10 juillet entrée dans la déclaration du mois.

**Ce qui manquait à l'échéancier est désormais calculable.** F · Obligations
écrivait en toutes lettres : « cet échéancier suppose que le dossier n'a pas de
salariés ». G ne lui est délibérément **pas** branché — la route prend
`a_des_salaries` en paramètre, et lui faire lire G ajouterait une arête au graphe
pour répondre par oui ou non. Mais la donnée existe maintenant, et l'écran peut
la passer.

**Reste.** H · Clôture et DSF, J · Pilotage.

---

## 17 août 2026 (suite 2) — Le contexte I · Création d'entreprise, de la coquille au parcours complet

**Demandé.** Construire la capacité manquante : « le système doit être complet
côté clients entreprise, que ce soit pour leur suivi fiscal et comptable ou même
pour les créations d'entreprise ». Quatre contextes sur treize étaient des
coquilles vides — un `__init__.py` de dix lignes chacun, zéro route, zéro
domaine. Ordre retenu, celui du parcours client : **I · Création**, puis
G · Social, H · Clôture, et J · Pilotage en dernier parce qu'il est interne au
cabinet.

**Ce qui a été livré.** Le contexte I entier : domaine, application, deux
réalisations de dépôt, routes, table, migration, jeu de démonstration, écran E13,
47 tests. Neuf routes sous `/creations`, toutes gardées par `SUIVRE_FORMALITE` —
qui était jusqu'ici **la seule permission du produit à n'ouvrir aucun écran** :
le rôle existait, son droit existait, et il n'y avait rien derrière.

**Les décisions qui portent le contexte.**

*Un dossier de création n'est pas une entreprise.* C'est une intention
d'entreprise : ni NIU, ni RCCM, ni exercice, ni régime. Les confondre obligerait
le portefeuille à porter des dossiers qui ne sont pas des contribuables, et
chaque calcul d'obligation devrait alors se demander « est-ce une vraie
entreprise ? ». C'est cette question qu'on évite en séparant.

*Le tunnel ne se saute pas.* On avance d'un cran, on ne revient pas, l'abandon
est ouvert de partout et porte toujours son motif. Le saut le plus tentant — « le
RCCM est là, passons à la livraison » — est le plus coûteux : il efface la trace
du dépôt, donc le délai tenu ou non par le guichet, donc le seul chiffre que le
cabinet puisse opposer au CFCE.

*La checklist est figée à l'ouverture.* La recalculer à chaque affichage ferait
apparaître, du jour au lendemain, une pièce jamais demandée au fondateur — et le
cabinet passerait pour négligent sur un dossier qui était complet.

*Le capital minimum vit au référentiel, avec son statut.* Quatre paramètres
ajoutés (`CAPITAL_MINIMUM_SA`, `CAPITAL_MINIMUM_SARL`, `CFCE_DELAI_ANNONCE_JOURS`,
`CREATION_DELAI_ALERTE_JOURS`), tous `A_VALIDER`, tous fondés sur le droit OHADA
et non sur le CGI — le fiscaliste devra donc les confirmer sur un autre texte que
les précédents. Le minimum de la SARL est **la valeur la plus incertaine du
référentiel** : la révision de 2014 a supprimé le minimum uniforme et renvoyé sa
fixation aux États parties. Conséquence directe dans le code : tant que le statut
est `A_VALIDER`, un capital insuffisant **avertit sans bloquer**. Refuser un dépôt
sur un chiffre non confirmé coûterait un client, sur une règle dont on n'est pas
sûr. Le jour où le paramètre passera VALIDE, le même constat deviendra bloquant
sans qu'une ligne de code change.

**Le défaut trouvé — et il n'a été trouvé qu'à l'exécution.**

La conversion ne fabriquait ni exercice ni calendrier, au motif que
« F · Obligations calcule déjà le calendrier depuis le portefeuille ; le
dupliquer produirait deux calendriers qui divergeraient ». Le raisonnement était
juste et la conclusion fausse.

Les **45 tests unitaires du contexte passaient**. L'un d'eux affirmait même
`entreprise.exercices == []` avec un commentaire expliquant pourquoi — il
encodait l'erreur. Puis le parcours complet, exécuté contre PostgreSQL :

    ✓  9. Conversion en entreprise du portefeuille    HTTP 200
    ✓ 11. Entreprise lisible au portefeuille          HTTP 200
    ✗ 12. Échéancier fiscal calculé d'office          HTTP 404

`404 : exercice 2026 inconnu`. F calcule les échéances **sur un exercice** ; sans
exercice, il n'a rien sur quoi calculer. L'entreprise entrait bien au
portefeuille, et la promesse annoncée du contexte — « elle bascule avec son
calendrier déjà généré » — était creuse.

La ligne juste passe entre **le fait et le calcul**. La période couverte par les
premiers comptes est un fait, décidé à la constitution et écrit dans les statuts :
elle appartient au dossier de création. Les échéances qui en découlent sont un
calcul, refait à chaque lecture au vu du régime du jour : elles appartiennent à F.
Créer l'exercice n'est pas une duplication, c'est la donnée sans laquelle le
calcul n'a pas d'objet.

Ajouté avec lui : `premiere_cloture`, explicite plutôt que déduite. Une entreprise
immatriculée en octobre clôture souvent au 31 décembre de l'année suivante, soit
quinze mois. Le deviner d'après le mois de création reviendrait à prendre, dans le
code, une décision qui appartient aux statuts. Et le libellé de l'exercice suit
l'année de **clôture** : c'est sous elle que la liasse est déposée.

Après correction : **14 étapes sur 14**, dont l'échéancier à **14 obligations
calculées d'office** sur une entreprise créée l'instant d'avant.

**Autres décisions notables.** La conversion est le seul cas d'usage du produit
qui franchit une frontière de contexte ; elle est isolée dans son propre module, et
l'écriture au portefeuille se fait dans l'adaptateur entrant — la couche qui
connaît la transaction, et la seule où la frontière reste visible. L'ordre des
deux écritures compte : portefeuille d'abord, dossier clos ensuite. En cas
d'échec, le geste se rejoue ; dans l'ordre inverse, on laisserait un client
immatriculé, payant, et absent du portefeuille.

**Vérifié.** 1 058 tests. Registre de cas d'usage porté à **40/40**, dont sept
neufs pour ce contexte — UC-38 vérifiant l'enchaînement complet jusqu'à
l'échéancier, précisément parce que la version fautive aurait passé les six
autres.

**Reste.** G · Social, H · Clôture et DSF, J · Pilotage.

---

## 17 août 2026 (suite) — Fermeture du contexte Conformité

**Demandé.** Stabiliser, puis produire un jeu de cas d'usage montrant comment
les flux sont validés.

**Ce qui a été corrigé.**

**1 · Le contexte Conformité ne répond plus sans session.** Cinq routes
répondaient `200` à un appelant anonyme : `POST /conformite/controler`,
`GET /conformite/regles` et les trois routes de démonstration. Chacune reçoit
désormais `AccesRequis` et une permission :

| Route | Permission | Périmètre |
|---|---|---|
| `GET /conformite/regles` | `LIRE_DOSSIER` | — |
| `POST /conformite/controler` | `CONTROLER_CONFORMITE` | destinataire de la facture |
| `GET /conformite/demonstration` | `LIRE_PIECE` | restreint |
| `GET /conformite/demonstration/rapports` | `LIRE_PIECE` | restreint |
| `GET /conformite/demonstration/{réf}` | `LIRE_PIECE` | 404 hors périmètre |

Le catalogue des règles n'est pas public, et la raison mérite d'être écrite :
les taux sont dans la loi, les publier ne révèle rien, mais **le rulebook est le
produit**. C'est la traduction du texte en contrôles exécutables avec, pour
chaque anomalie, sa conséquence chiffrée — exactement ce que le cabinet vend.

Le périmètre se lit sur le **destinataire** de la facture, jamais sur
l'émetteur. Se tromper de côté ferait voir à un adhérent toutes les factures
qu'il a émises chez les autres.

`restreindre` pour les listes, `exiger_dossier` pour les lectures unitaires. Une
liste se restreint ; refuser toute la boîte de réception parce qu'une ligne sort
du périmètre la rendrait vide pour tout le monde. Et le `404` d'une pièce hors
périmètre est désormais indiscernable de celui d'une référence inexistante : le
message ne liste plus les références disponibles, ce qui revenait à publier
l'inventaire des pièces des autres dossiers.

**2 · Gardes d'écran sur `/pieces` et `/pieces/{référence}`.** Ces deux pages ne
lisaient ni session ni accès. Elles portent maintenant la même garde
`LIRE_PIECE` que les neuf autres écrans.

**3 · `/mon-espace` refuse les rôles sans dossier.** L'administrateur y lisait
« si vous venez de souscrire, le cabinet finalise l'ouverture de votre dossier ».
Il n'a pas souscrit et rien ne se finalise : un message d'attente adressé à qui
n'attend rien fait chercher une panne là où il n'y a qu'une habilitation
absente. Le refus est écrit dans la langue de l'espace adhérent, sans la
coquille collaborateur — mais il **reprend le mot du produit**, « Accès
réservé », pour que la recette le distingue d'un écran vide et qu'un adhérent au
téléphone lise la même formule que le collaborateur en face de lui.

**4 · Deux tests erraient au lieu de se sauter.** `TestCouplageAuDepot` porte
maintenant `@exige_postgresql`. Un vert franc ou un rouge franc, jamais deux
ERROR qui se lisent comme une chaîne cassée.

**Ce que les tests ont révélé sur eux-mêmes.** Fermer les routes a fait échouer
**onze tests** de `TestConformite`. Ils appelaient l'API sans session et
passaient — ils ont donc été verts pendant tout le temps où le moteur était une
API publique. C'est le pire mode de panne d'une suite : elle ne signalait pas
l'absence de garde, elle la certifiait. Ils reçoivent désormais un client
authentifié en réviseur, et une classe `TestConformiteFermee` de neuf tests
affirme les **refus** — sans session, sans permission, hors périmètre. Une suite
qui ne vérifie que des chemins nominaux valide aussi bien un système sans
serrure.

Un piège au passage : les fixtures de client appelaient chacune
`reinitialiser_atelier()`, qui vide le magasin de sessions. Créées l'une après
l'autre, la seconde révoquait la première, et un test comparant deux profils
voyait un `401` là où il n'y avait qu'un atelier remis à zéro sous ses pieds.
Une seule application par module, désormais.

**Vérifié.** `1 010 tests` (dix de plus). Recette A→E rejouée sur la pile
corrigée. Le limiteur de débit a de nouveau refusé mes propres connexions au
passage — trente en cinq minutes — ce qui reste la bonne réponse.

**Ce qui reste.** Les écrans E02 et E03 restent alimentés par le jeu de
démonstration : les brancher sur les vraies pièces suppose l'extraction
automatique des montants, qui est en veille. Ils sont désormais **gardés et
restreints**, ce qui n'était pas le cas, mais un adhérent y voit un flux fictif
correctement filtré, pas ses propres factures.

---

## 17 août 2026 — La matrice complète : neuf profils, chaque écran, chaque route

**Demandé.** « Est-ce que tu as déjà fait les différents tests suivant les
profils et validé les différents cas d'usage […] pour que tous les flux soient
ok ? » La réponse honnête était **non**. Les vérifications en direct de la veille
portaient sur un seul compte de direction : sept écrans ouverts et quatre refus
constatés. Sept écrans sur onze, un profil sur neuf.

**Ce qui a été construit.** Une recette en cinq passes, chacune répondant à une
question qu'un défaut coûte cher à laisser ouverte :

| Passe | Question | Étendue |
|---|---|---|
| A | qui entre, qui doit être refusé | 13 comptes |
| B | quel écran s'ouvre pour quel profil | 11 écrans × 10 profils |
| C | **le refus tient-il sans l'interface** | 10 routes × 10 profils |
| D | un habilité voit-il le dossier voisin | 10 profils × 6 dossiers |
| E | les actes qui modifient l'état | 12 appels, refus **et** accords |

La passe C est celle qui compte. Une garde qui ne vit que dans la page Next
protège l'écran, pas la donnée : le front transmet le même témoin `cga_session`
à l'API, donc tout refus constaté à l'écran devait être rejoué directement
contre le backend. Résultat : **100 appels, 100 % conformes**. Le refus ne
dépend pas de l'interface.

La passe D vaut, pour un centre de gestion, ce que vaut l'isolation dans une
banque. Un comptable habilité sur trois dossiers qui lit le quatrième n'est pas
une gêne d'ergonomie, c'est une violation du secret professionnel. **60 lectures
croisées, aucun débordement** : `l.fotso` lit ses trois dossiers et pas le
quatrième, `c.ndongo` ses deux, chaque adhérent le sien, l'inspecteur le sien,
l'administrateur aucun.

La passe E vérifie aussi des **accords**, pas seulement des refus. Une recette
qui ne constate que des refus valide tout aussi bien un système qui refuse tout.

**Trois erreurs d'outillage, aucune imputable au produit.** Elles méritent
d'être notées parce que chacune, dans un journal, ressemble exactement à une
panne :

1. Une expression régulière relevait les champs du formulaire avec `name` avant
   `value`. Sur les champs visibles l'ordre est inverse, le groupe optionnel
   n'était jamais capturé, **toutes les valeurs revenaient vides** — dont la
   référence d'action serveur de Next. Dix connexions en HTTP 500. Remplacée par
   un vrai parseur HTML.
2. Le champ d'identifiant s'appelle `courriel`, pas `identifiant`.
3. Le classement des réponses cherchait la classe CSS
   `avertissement-ecran--reserve` pour détecter un refus. Cette classe sert
   **aussi** de bandeau de mise en garde ordinaire sur cinq écrans qui, eux,
   s'ouvrent normalement — d'où trente faux refus. Seul le titre « Accès
   réservé » est probant.

Le limiteur de débit a par ailleurs refusé mes propres connexions au-delà de
trente en cinq minutes. Comportement correct ; la recette ouvre désormais une
session par compte et la réutilise partout.

**Ce que le check a réellement trouvé.**

1. **`/pieces` et `/pieces/{référence}` n'ont aucune garde.** Ces deux pages ne
   lisent ni la session ni les accès. Elles appellent
   `/conformite/demonstration/rapports` — le jeu de démonstration, pas les
   pièces du dossier. Conséquence constatée : un **adhérent habilité au seul
   dossier BATIMENT PLUS** ouvre la boîte de réception et y voit les six
   sociétés du portefeuille. Même défaut de câblage que celui corrigé la veille
   sur les obligations, sur un autre contexte.

2. **Le contexte Conformité répond sans aucune session.** `POST
   /conformite/controler`, `GET /conformite/regles` et les trois routes de
   démonstration n'ont pas de dépendance d'accès. Soixante appels anonymes du
   moteur en 0,3 seconde, tous en 200, aucun limiteur — le moteur de conformité,
   qui est le différenciateur du produit, est une API publique gratuite.

3. **`/mon-espace` s'ouvre pour l'administrateur**, seul rôle explicitement
   privé de `LIRE_DOSSIER`. Aucune donnée n'apparaît, mais le texte affiché est
   faux pour lui : « si vous venez de souscrire, le cabinet finalise
   l'ouverture de votre dossier ».

4. **Deux tests erreurs au lieu de skips.** `TestCouplageAuDepot` de
   `test_coffre.py` emploie la fixture `session_sql` sans porter le marqueur
   `exige_postgresql`. Sans base de test, `pytest` sort deux ERROR — ce qui se
   lit comme une chaîne cassée.

**Ce qui est validé.** Suite complète : **1 000 tests** sur PostgreSQL réel.
Flux M · Souscription de bout en bout : **10 étapes sur 10** — catalogue, devis,
engagement avec encaissement d'office, courriel d'activation, définition du mot
de passe par le formulaire, première connexion, espace adhérent, et refus sur
les comptes du cabinet. Le refus d'engagement sans NIU est un **refus métier
correct** : une adhésion ouvre un accès à un dossier. La route de simulation de
paiement répond 409 dès que des identifiants Tara réels sont configurés — elle
ne peut pas s'endormir en production.

**Ce qui reste.** Les quatre défauts ci-dessus. Le premier demande un arbitrage :
brancher la boîte de réception sur les vraies pièces change le comportement de
l'écran, ce n'est pas une garde à ajouter. Les trois autres sont mécaniques.

---

## 16 août 2026 (suite 6) — Les formulaires soumis pour de vrai, et le témoin qui ne revenait pas

L'extension navigateur n'étant pas connectée, j'ai fait autrement : soumettre les
formulaires **exactement comme le ferait un navigateur sans JavaScript** — lire la
page, recopier tous ses champs cachés, poster le tout.

C'était la seule chose qui n'avait jamais été éprouvée. J'avais vérifié que le
*balisage* du formulaire d'activation était identique à celui de la connexion, ce
qui ne prouve rien sur ce qui se passe à la soumission.

### Deux fois, mon banc d'essai a produit le symptôme d'un produit cassé

**Premier essai :** les quatre formulaires rendent `200` et ne font rien. Aucun
témoin, aucun courriel. J'ai soupçonné la protection contre la falsification
inter-site et ajouté l'en-tête `Origin`. Sans effet.

La vraie cause : le `<form>` rendu par Next porte `encType="multipart/form-data"`, et
je postais de l'`application/x-www-form-urlencoded`. Le gestionnaire d'action
serveur n'analyse que la première forme.

C'est la deuxième fois de la journée qu'un banc d'essai mal réglé imite parfaitement
un défaut — après le `HOSTNAME=127.0.0.1` de ce matin. La leçon se répète : **avant
d'accuser le produit, vérifier le client.**

Une fois corrigé, tout passe : connexion `303` vers le tableau de bord avec témoin
posé ; mot de passe faux refusé **sans témoin** ; confirmation divergente signalée
**sans consommer le lien** ; activation `303` vers la connexion, puis accès au bon
dossier ; mot de passe oublié confirmé et courriel produit.

Les quatre formulaires fonctionnent donc sans JavaScript, comme trois commentaires du
dépôt l'affirmaient — désormais vérifié plutôt que supposé.

### Le vrai défaut : `Secure` posé sur une connexion en clair

En suivant les redirections comme un navigateur, la connexion réussissait puis
**rebondissait sur l'écran de connexion**. Chaque écran affichait « Se connecter ».

```
Set-Cookie: cga_session=…; Secure; HttpOnly; SameSite=lax
```

`secure` valait `process.env.NODE_ENV === "production"`. Or `NODE_ENV` décrit la
**compilation**, pas le transport : la sortie autonome de Next le pose à
`production` quoi qu'il arrive. Servie en clair — `docker compose up`, une recette
derrière un simple port, une démonstration sur un poste — l'application posait un
témoin `Secure` que le navigateur refusait ensuite de renvoyer.

**Le symptôme est parfaitement silencieux.** La connexion réussit, la redirection
part, et la page suivante renvoie au formulaire. Aucune erreur, aucune trace, rien à
chercher. Quelqu'un qui aurait lancé `docker compose up` aurait conclu que le produit
était cassé — et n'aurait pas eu tort de le croire.

⚠️ Ce défaut ne pouvait apparaître que là. Tous mes contrôles précédents passaient le
témoin **à la main** dans un en-tête `Cookie`, en le tenant de l'API. Aucun ne faisait
l'aller-retour complet du navigateur.

### Le correctif : lire le transport, pas l'environnement

`x-forwarded-proto` dit la vérité : un mandataire qui termine le TLS le pose à
`https`, une connexion directe en clair ne le pose pas. Le témoin est donc `Secure`
exactement quand il peut l'être.

⚠️ Le mandataire **doit** poser cet en-tête. La même exigence pèse déjà sur l'API,
dont la limitation de débit lit l'adresse qu'il reconstitue — c'est la même ligne de
configuration, signalée dans les deux `Dockerfile`. `HttpOnly` et `SameSite=Lax` ne
dépendent d'aucun transport et s'appliquent dans tous les cas.

### Vérifié après correctif

Parcours complet du navigateur : connexion → **atterrissage sur le tableau de bord**,
témoin conservé, sept écrans rendus au nom du connecté. Et les refus tiennent —
comptable refusé sur `/comptes`, administrateur servi là et refusé sur
`/portefeuille`, adhérent servi sur son espace.

---

## 16 août 2026 (suite 5) — Le test en charge, et un commentaire qui mentait

Demande : éprouver le système sur plusieurs sessions simultanées. Tout ce qui avait
été vérifié jusque-là était séquentiel.

### Ce qui a tenu

| Épreuve | Résultat |
|---|---|
| 600 requêtes entrelacées, 10 sessions, 24 en parallèle | **0 confusion d'identité, 0 fuite de périmètre** |
| 150 pages du front, 5 sessions simultanées | **0 fuite entre sessions** |
| 20 dépôts simultanés du même fichier | 1 seule empreinte, aucun fichier partiel |
| 50 lectures authentifiées en parallèle | toutes abouties, chaîne d'audit intacte |
| Révocation d'une session en vol | `200` avant, **`401` après** |

La confusion de session était le risque principal : le contexte K fait circuler
l'atelier de la requête dans une `ContextVar`, et uvicorn exécute les routes
synchrones dans un réservoir de fils. Une propagation défaillante aurait fait
recevoir à un comptable la réponse destinée à un adhérent. Rien de tel.

### Ce qui a cassé

**Cinq souscriptions simultanées sur huit en `500`.**

```
UniqueViolation: uq_journal_audit_locataire_rang
Key (locataire, rang) = (CGA-BRCG, 40) already exists
```

Aucune corruption : la contrainte d'unicité a fait son travail et refusé la seconde
écriture. Mais l'opération métier entière échouait — devis, paiement, ouverture
d'accès.

### La cause : un commentaire qui affirmait le contraire de la vérité

`JournalAuditSql` lisait la tête de chaîne avec `SELECT … FOR UPDATE`, en expliquant
que « deux transactions concurrentes ne peuvent pas lire le même rang maximal ».

**C'était faux.** `FOR UPDATE` verrouille les lignes **que la requête a lues** ; il ne
dit rien de celles qui n'existent pas encore :

* T1 lit la ligne de rang 39 et la verrouille ;
* T2 veut la même ligne et attend ;
* T1 insère le rang 40 et valide ;
* T2 repart — et ne re-vérifie que la ligne 39, qui existe toujours. Elle ne
  redécouvre jamais la ligne 40.

T2 calcule donc 39 + 1 = 40. C'est le problème classique du **fantôme** : un verrou
de ligne ne protège pas d'une insertion.

Ce qui rend ce défaut instructif, c'est qu'il était **documenté à l'envers**. Le
raisonnement était écrit, plausible, et faux. Aucune relecture ne l'aurait attrapé —
seule une exécution concurrente pouvait le dire.

### Le correctif : un verrou consultatif, par locataire

`pg_advisory_xact_lock` ne porte sur aucune ligne : les insertions ne lui échappent
pas. Il est pris pour la durée de la transaction et libéré à la validation comme à
l'annulation — rien à relâcher à la main.

Sérialiser n'est pas un pis-aller. **Une chaîne de hachage est séquentielle par
nature** : chaque entrée porte l'empreinte de la précédente, on ne peut pas en
ajouter deux à la fois. Le verrou énonce cette contrainte au lieu de la heurter.

⚠️ Il est **par locataire** : deux cabinets n'attendent pas l'un pour l'autre.

Après correctif : **8 souscriptions simultanées sur 8**, chaque jeton ouvrant le bon
compte avec le bon périmètre.

### Le test de régression, et la vérification qu'il sert à quelque chose

`test_concurrence.py` — sept tests, avec des fils réels, des sessions distinctes et
une **barrière** pour qu'ils partent ensemble. Un test qui simulerait la concurrence
en séquence ne reproduirait rien.

J'ai retiré le verrou pour vérifier : **six tests sur sept rougissent**. Remis : tous
verts. Un test de concurrence qui n'a jamais échoué ne prouve rien ; celui-ci a été
vu échouer sur le défaut qu'il surveille.

L'un d'eux est répété trois fois — un défaut de concurrence est intermittent par
nature, et un seul passage vert n'établit pas grand-chose.

### Ce que cette journée aura confirmé

Cinq défauts trouvés aujourd'hui, **aucun par les tests** : dépôt SQL incomplet,
contexte F lisant la mémoire, refus d'habilitation en `500`, deux pages manquantes,
et maintenant la collision de rang. Tous sont apparus en **exécutant** le logiciel —
dans un conteneur, par les écrans, sous charge.

**1000 tests.**

---

## 16 août 2026 (suite 4) — Le mode de recette, et deux trous béants dans le parcours

Demande : pouvoir dérouler les parcours à la main, avec des paiements et des
courriels validés automatiquement. Le faire a mis au jour ce qu'aucun des 981 tests
ne voyait.

### Deux pages n'existaient pas

**`/activation`.** Le paiement validé faisait partir un courriel dont le lien menait
là. Là n'existait pas. Un adhérent qui venait de payer tombait sur un **404**, et le
seul chemin vers son espace était mort.

**`/mot-de-passe-oublie`.** « Mot de passe oublié ? » figurait dans les traductions
depuis l'origine et n'était **rendu nulle part**. La route backend, le gabarit de
courriel et le jeton de deux heures existaient tous — sans aucun moyen de les
déclencher depuis le site.

Les deux extrémités étaient complètes dans les deux cas. Le backend émettait les
jetons, traçait l'audit, exposait les routes ; le front avait sa page de connexion.
**Chaque moitié fonctionnait, les tests de chaque moitié passaient, et personne
n'avait parcouru le chemin entier.**

C'est la classe de défaut la plus coûteuse, et la plus banale : elle ne se voit ni en
relecture, ni en test unitaire, ni en test d'intégration d'un contexte. Elle se voit
en cliquant.

### Pourquoi elle avait survécu si longtemps

Parce que le lien d'activation était **illisible**. En développement les courriels
sont retenus au lieu d'être envoyés — c'est ce qui empêche une suite de tests
d'écrire à de vraies adresses —, mais rien ne permettait de les lire. Le lien
disparaissait dans un tableau en mémoire.

Personne ne pouvait donc aller au bout, et l'absence de la page d'arrivée n'avait
aucun moyen de se manifester. **Le trou dans l'outillage cachait le trou dans le
produit.**

### Le mode de recette, et pourquoi c'est un drapeau à part

`CGA_MODE_DEMONSTRATION` valide les paiements d'office et rend lisibles les courriels
retenus.

L'en-tête de `fournisseur_tara.py` posait déjà la règle, bien avant ce mode : « un
mode simulé qui validerait automatiquement finirait un jour en production ». Elle est
juste, et je ne l'ai pas contournée. Ce que je n'ai **pas** fait : déduire la
validation automatique de l'absence de clé Tara. L'absence de clé est un **accident
de configuration** ; elle ne vaut pas consentement à fabriquer des encaissements.

Le drapeau se déclare, et trois choses le rendent visible :

* `/sante` l'annonce ;
* la boîte aux lettres affiche un bandeau d'avertissement ;
* **la production refuse de démarrer** avec — pas un avertissement, pas une
  dégradation : `Configuration` lève.

⚠️ La validation d'office n'est pas un court-circuit : elle emprunte exactement le
chemin d'une vraie notification, celui que le prestataire déclenchera. Ce qui est
simulé, c'est **l'appel du prestataire**, rien d'autre.

### La boîte aux lettres n'est pas protégée par une session, délibérément

Exiger une connexion serait absurde : on vient précisément y chercher de quoi se
connecter la première fois. La protection est ailleurs, et elle est plus solide qu'un
contrôle d'accès — **la route n'existe pas** hors du mode, et rend `404` plutôt que
`403`. Un point d'entrée absent se distingue mal d'un point d'entrée qui refuse.

### Un refus qui n'en est pas un

Premier essai du parcours : la définition du mot de passe a été refusée. Motif — « le
mot de passe contient ESSAI. Nom, prénom et adresse sont les premiers essais de
quiconque vous vise nommément. » J'avais choisi un mot de passe contenant le nom du
prospect.

**Le refus était correct**, et le message disait exactement pourquoi. C'est le
comportement qu'on veut d'une politique de mot de passe : refuser, et expliquer — la
personne qui choisit son mot de passe est légitime, un refus muet la fait essayer au
hasard. Consigné ici parce que, pendant dix secondes, je l'ai pris pour un défaut.

### Vérifié

Les deux parcours, **par les écrans**, sur PostgreSQL :

* devis → paiement validé d'office → courriel retenu → lien ouvert → mot de passe
  défini → connexion en `ADHERENT` sur le seul dossier souscrit ; le lien rejoué rend
  `410` ;
* « mot de passe oublié » → courriel → lien → nouveau mot de passe → reconnexion.

Et les deux comptes qui **doivent** échouer — le suspendu, le jamais activé —
échouent tous deux avec le message indifférencié d'un compte inexistant.

**993 tests** (contre 981), 95 pages compilées, `ruff` et types propres.

Le guide de recette est dans [`Docs/recette.md`](recette.md) : comment démarrer, les
deux parcours pas à pas, les douze comptes de test et ce que chacun sert à vérifier.

⚠️ Ce que ce mode **ne prouve pas** : que le paiement fonctionne — Tara n'a jamais
été appelé pour de vrai ; que les courriels arrivent — ils ne partent pas ; que les
chiffres sont justes — le référentiel n'est toujours pas validé.

---

## 16 août 2026 (suite 3) — La vérification totale, et ce qu'elle a sorti

Passe complète : lint, migrations dans les deux sens, 981 tests, types, lint et
compilation du front, puis **l'application servie comme elle le sera en production**
— sortie autonome de Next devant l'API dans son image, sur PostgreSQL.

### La faute que j'ai commise, et ce qu'elle a failli coûter

J'ai d'abord démarré la sortie autonome avec `HOSTNAME=127.0.0.1`. Toutes les pages
sont parties en boucle de redirection, et j'en ai conclu — à voix haute — que le
`Dockerfile` livrerait un front cassé.

**C'était mon test qui était faux.** `HOSTNAME` renseigne l'interface d'écoute *et*
sert à construire l'origine des réécritures internes ; une valeur d'interface
spécifique fabrique une réécriture inter-origine que Next dégrade en redirection.
Avec `HOSTNAME=0.0.0.0` — la valeur que le `Dockerfile` pose, et la valeur
documentée pour un conteneur — tout rend 200.

La leçon vaut d'être écrite : **un diagnostic tiré d'un banc d'essai mal réglé se
présente exactement comme un défaut du produit.** Le réflexe qui a sauvé la mise est
d'avoir comparé au comportement de `next start` avant de conclure — l'écart entre les
deux disait où chercher.

### Le vrai défaut : un refus d'habilitation rendait un `500`

Les écrans appelaient l'API sans vérifier la permission. L'API répondait `403`,
l'erreur remontait à travers le composant serveur, et le visiteur voyait un `500`.

C'est-à-dire **« le logiciel est cassé »** là où la réponse juste était **« ce n'est
pas pour vous »**. La différence n'est pas cosmétique : un `500` fait appeler le
cabinet, ouvrir un incident, chercher une panne inexistante — et il noie les vrais
`500` dans les journaux.

Mesuré rôle par rôle, en interrogeant l'application réelle :

| Rôle | Écrans en `500` avant |
|---|---|
| Comptable | `/comptes` |
| Adhérent | `/comptes`, `/comptabilité` |
| **Administrateur** | **tous, sans exception** |

### Le cas de l'administrateur est le plus instructif

L'administrateur n'a **délibérément aucune permission** sur les dossiers ni sur la
comptabilité : il distribue les droits, il ne s'en sert pas. C'est une décision de
conception du contexte K, et elle est juste.

Sauf que la **coquille** de l'espace de travail appelait `lireDossiers()` sans
condition. Résultat : `403` dans le gabarit, donc `500` sur **chaque écran** — y
compris celui des comptes, qui est précisément le sien. Le seul rôle capable de
réparer une situation d'habilitation était le seul à ne pouvoir ouvrir aucune page.

Une décision de conception juste, contredite en silence par une hypothèse implicite
d'un gabarit. Aucun test ne pouvait l'attraper : ils tournent tous avec des comptes
qui ont les droits.

### Deux couches, et il faut les deux

**Le garde d'écran** évite l'appel : il sait *avant* d'interroger l'API que ce rôle
n'y a pas droit, et il peut nommer le profil qui ouvrirait la page. Sept écrans en
portent un désormais, plus le gabarit.

**La frontière d'erreur** rattrape ce que le garde ne prévoit pas — notamment un
refus qui dépend du **dossier** demandé et non du rôle, qu'aucune vérification de
permission ne peut anticiper.

⚠️ Elle n'affiche jamais le message d'erreur, seulement le `digest`. Le détail d'un
refus dit quel dossier existe, et c'est exactement ce que l'API tait en rendant `404`
plutôt que `403` sur un dossier hors périmètre. Elle se replie prudemment : en cas de
doute elle annonce une panne, jamais un refus — annoncer « accès refusé » sur une
vraie panne enverrait chercher une habilitation au lieu d'un incident.

### Pourquoi on nomme le profil, alors que l'API ne dit jamais rien

Une **permission** est attachée à un rôle, pas à un dossier. Dire « cet écran est
ouvert au profil administrateur » ne révèle aucune donnée et évite un appel au
support. La discrétion de l'API porte sur l'existence des dossiers ; elle n'a pas à
s'étendre à l'organigramme du cabinet.

### Ce qui a été vérifié, et comment

**30 combinaisons** — 3 rôles × 10 écrans — plus 14 pages publiques bilingues, sur le
serveur autonome devant l'API conteneurisée. Résultat : **aucun `500`, aucune erreur
serveur**, et le contenu correspond au rôle — « BATIMENT PLUS » au portefeuille,
« Balance équilibrée », `19,25 %` au référentiel, `FAC-ACH-007` et ses 379 350 F à la
déclaration, un refus lisible partout où le rôle ne suffit pas.

Les huit écrans protégés renvoient toujours vers la connexion sans session.

**981 tests, migrations montées et défaites entièrement, 87 pages compilées.**

⚠️ L'image du front n'est toujours pas construite sur cette machine : le registre npm
expire à répétition. Ce que cette passe prouve en revanche, et qui n'était pas acquis :
la **sortie `standalone` fonctionne** — 64 Mo, `node_modules` tracé à 38 Mo, structure
`Frontend_erp_cga/server.js` exactement celle que le `Dockerfile` recopie. Ce qui
reste non vérifié tient à l'image de base et à l'installation des dépendances, pas à
la logique du fichier.

---

## 16 août 2026 (suite 2) — Stabilisation : ce qui manquait pour que ça tourne ailleurs

La question posée était « le système est-il opérationnel ? ». La réponse était non,
et pour trois raisons qui n'avaient rien à voir avec le métier : personne ne recevait
de courriel, aucun document n'était stocké, et rien ne permettait de déployer.

### 1 · Les courriels partent vraiment

Le port `ServiceNotification` n'avait qu'une réalisation : celle qui **retient** les
messages en mémoire. Conséquence directe et jamais mesurée — **aucun compte réel
n'aurait pu être activé.** L'adhérent paie, le compte se crée, le lien d'activation
part dans un tableau Python et n'en sort jamais.

`ServiceNotificationSmtp` poste par SMTP. SMTP et non l'API d'un prestataire : Brevo,
SES, un relais chez l'hébergeur camerounais du cabinet parlent tous SMTP, et changer
de fournisseur devient un changement de variable d'environnement.

**Deux règles de sûreté valent plus que la mise en page.**

*Une clé manquante annule l'envoi.* `str.format` sur un gabarit auquel il manque
`{lien}` produirait un message affichant `{lien}` en toutes lettres. Le destinataire
croirait avoir été servi et n'aurait aucun recours ; un échec journalisé se rejoue.

*Le contexte est échappé avant d'entrer dans le HTML.* Une dénomination sociale
contenant `<` casserait la mise en page ; un contexte hostile y logerait un lien.

**Un défaut trouvé en écrivant les gabarits.** Deux des trois sites d'appel passaient
`secret` — le jeton nu — là où le troisième passait `lien`. Un courriel qui affiche
« votre code : xY7… » apprend à l'adhérent qu'un secret se recopie, et c'est
exactement le geste qu'un hameçonnage lui demandera ensuite. Les trois passent
désormais un lien.

⚠️ Ce que rien de tout cela ne règle : **la délivrabilité**. Il y faut SPF, DKIM et
DMARC publiés sur le domaine du cabinet. Un courriel d'activation classé en
indésirable équivaut à un courriel non envoyé, et aucun test ne le dira.

### 2 · Les justificatifs existent

Le port `MagasinFichiers` était déclaré depuis le début. Il n'avait aucune
réalisation : une « pièce justificative » n'était qu'un nom de fichier et une
empreinte. Le rapport de conformité désignait des constats sans que rien ne permette
de les vérifier sur la facture.

**Le fichier est adressé par son contenu.** La clé *est* l'empreinte SHA-256 — le
domaine l'affirmait déjà : « deux fichiers de même empreinte sont le même fichier ».
Trois propriétés en découlent gratuitement : la dédoublonnage est acquise, le dépôt
est idempotent, et l'altération se détecte.

**Trois contrôles sur les deux routes exposées**, chacun réparant une faille
distincte :

| Contrôle | Sans lui |
|---|---|
| Le type est lu dans les **octets** | Un HTML étiqueté `image/jpeg`, rendu plus tard avec cette étiquette, exécute son script dans le domaine du cabinet — sur la page où un comptable est connecté |
| La taille est bornée **avant** lecture | Un seul envoi épuise la mémoire du processus |
| La clé est validée par **liste blanche** | `../../etc/passwd` en lecture, et l'écrasement de n'importe quel fichier du serveur |

Neuf tentatives de traversée de chemin sont testées nommément. La protection est une
liste blanche — tout ce qui n'est pas 64 caractères hexadécimaux minuscules n'existe
pas — parce que les listes noires se contournent toutes, par encodage, par lien
symbolique, par séparateur exotique.

**L'écriture passe par un temporaire puis `os.replace`.** Sans cela, une coupure au
milieu d'un dépôt laisse un fichier **partiel** à une clé valide : il se relit sans
erreur, s'affiche comme un PDF tronqué, et rien n'a échoué.

### 3 · Le système se déploie

Deux `Dockerfile`, un `docker-compose.yml`, une chaîne d'intégration.

Le point qui a demandé le plus d'attention n'est pas Docker mais **ce que les images
ne doivent pas faire** :

* elles n'appliquent **pas** les migrations au démarrage — trois instances
  lanceraient trois `alembic upgrade` sur la même base ; c'est un service à part qui
  s'exécute une fois ;
* elles ne tournent **pas** en `root` ;
* elles n'embarquent **pas** de compilateur — une exécution de code arbitraire y
  trouverait de quoi compiler ce qu'elle veut.

⚠️ Un piège attrapé avant qu'il ne morde : le conteneur tourne sans privilège, et
Docker initialise un volume nommé d'après les droits du chemin dans l'image. Sans
`chown` explicite du point de montage, le volume aurait appartenu à `root` et **le
premier dépôt de fichier aurait échoué** — à l'usage, jamais au démarrage.

Côté front, `output: "standalone"` et `outputFileTracingRoot`. Le second est
indispensable : par défaut le traçage prend le dossier du projet pour racine et
**ignore tout ce qui est au-dessus**, or avec pnpm les dépendances réelles sont dans
le `node_modules` hissé du parent. Sans cette ligne, l'image se construit sans erreur
et le serveur meurt au premier import manquant.

### 4 · La configuration refuse de démarrer plutôt que de mentir

Cinq réglages font désormais échouer le démarrage en production. Chacun est
**silencieux à l'exécution**, et c'est tout l'argument :

| Refus | Ce qui se passerait sinon |
|---|---|
| `CGA_PERSISTANCE` ≠ `postgresql` | L'application répond correctement à tout, et perd la comptabilité au premier redéploiement |
| `CGA_SMTP_HOTE` vide | Aucun lien d'activation ne part, aucun compte ne s'active |
| `CGA_CLE_CHIFFREMENT` vide | Les secrets TOTP en clair : une fuite de base livre tous les seconds facteurs |
| Adresse publique en `http://` | Les liens d'activation portent un secret d'usage unique |
| Origine CORS en clair | Le témoin de session est exposé |

Un démarrage refusé se voit immédiatement, pendant qu'un ingénieur regarde. C'est la
seule fenêtre où ces fautes coûtent peu.

### 5 · Deux durcissements

**La limitation de débit.** Le verrouillage de compte existait — cinq échecs, quinze
minutes — et défend *un compte*. Trois attaques passaient au travers, dont une bien
plus sérieuse que les autres : **Argon2id est conçu pour être lent**, environ cent
millisecondes par vérification. Sans limite, cent requêtes de connexion par seconde
saturent les cœurs de la machine. Aucun compte n'est compromis, et plus personne ne
se connecte — la fonction qui protège les mots de passe devient l'arme qui coupe le
service.

Fenêtre glissante et non seau à jetons : le seau se recharge en continu, un attaquant
patient trouve le rythme qui le maintient sous le seuil indéfiniment. Et **une requête
refusée n'est pas comptée** — sinon celui qui continue de marteler maintiendrait la
fenêtre pleine, bloquant l'utilisateur légitime qui partage cette adresse bien après
la fin de l'attaque.

⚠️ Le compteur est **par processus**. Trois instances donnent trois fois la limite.
Un compteur partagé exigerait Redis, donc un service de plus à exploiter, pour un
cabinet de quelques dizaines d'utilisateurs.

**Le chiffrement du secret TOTP.** Un mot de passe se hache — irréversible, donc
mieux protégé. Un secret TOTP doit être **relu** à chaque connexion pour recalculer
le code : le hacher rendrait le second facteur inopérant. Il restait donc en clair.

AES-256-GCM, et GCM parce qu'il **authentifie** : une valeur altérée est rejetée au
lieu de produire des octets quelconques qu'on prendrait pour un secret — un second
facteur qui vérifie contre des octets quelconques refuse tout le monde, sans que la
cause soit visible nulle part.

⚠️ La migration est **partielle et assumée** : un compte dont le second facteur n'est
jamais retouché garde son secret en clair. Chiffrer l'existant demande de réactiver
le second facteur des comptes concernés — geste d'exploitation, pas de migration.

### Un test qui a viré au rouge sans qu'une ligne bouge

À minuit, `test_une_souscription_ne_fabrique_pas_un_reviseur` est passé au rouge. Le
code n'avait pas changé : la route lisait l'horloge murale — le 16 août — pendant que
le test comparait à une date figée au 15.

L'en-tête de `horloge.py` affirmait depuis l'origine qu'il fallait « pouvoir la
remplacer », et **rien ne le permettait**. C'est fait : `horloge_figee`, une variable
de contexte — et non une globale, parce que les routes synchrones de FastAPI
s'exécutent dans un réservoir de fils où une globale figerait aussi les requêtes
voisines.

Un test qui change de verdict avec le calendrier est pire qu'un test absent : il
échoue un jour où personne ne cherche un défaut, et l'équipe apprend à le ressusciter
en modifiant sa date au lieu de lire ce qu'il dit.

### Deux nettoyages du même genre

Le sondage « PostgreSQL est-il joignable ? » vivait dans `test_persistance.py`.
J'allais en écrire une seconde copie pour `test_coffre.py` — deux copies qui divergent
donneraient une suite annonçant « tout passe » sans avoir vérifié un seul
cloisonnement. Il vit maintenant dans `conftest.py`, une seule fois, et la chaîne
d'intégration **compte** les tests de persistance passés pour attraper le cas où le
sondage échouerait à tort.

`cryptography` était présent par transitivité et rien ne le garantissait : une mise à
jour de la dépendance qui l'apportait aurait cassé toutes les connexions à second
facteur. Il est déclaré.

### Deux défauts que seul le conteneur a révélés

Les tests passaient tous. C'est en interrogeant l'application réelle, dans son image,
contre PostgreSQL, que deux fautes sont sorties — et elles se ressemblent.

**`DepotPiecesSql` ne réalisait pas son port.** Trois méthodes manquaient :
`par_identifiant`, `recues_entre`, `par_empreinte`. La route de téléchargement d'un
justificatif rendait un `500`. Un `Protocol` de Python ne vérifie **rien à
l'exécution** — c'est un contrat pour l'analyse statique —, et les tests exerçaient
la réalisation *mémoire*, qui était complète.

**Le contexte F lisait toujours la mémoire.** Ses deux fabriques de dépôt rendaient
le jeu de démonstration sans jamais consulter la session, y compris en mode
PostgreSQL. L'échéancier et la déclaration de TVA se calculaient donc sur des
dossiers et des écritures de démonstration pendant que la comptabilité réelle vivait
en base.

Rien ne le montrait : les écrans affichaient des chiffres plausibles, et personne ne
rapprochait la déclaration de la balance. **C'est une déclaration fiscale qui en
serait sortie fausse.**

La cause profonde est la même dans les deux cas, et elle mérite d'être nommée :
`comptabilite/api.py` et `portefeuille/api.py` n'exportaient que leur réalisation
**mémoire**. Un contexte voisin n'avait littéralement pas d'autre choix. *Ce que le
port expose commande ce que les voisins peuvent faire* — l'asymétrie n'était pas un
oubli cosmétique, c'était la cause.

Garde-fou posé : `test_conformite_des_ports.py` rapproche chaque réalisation de son
port. Il **découvre** ses cas au lieu de les énumérer — la première version supposait
deux noms de module fixes alors que le dépôt en emploie cinq, et laissait donc quatre
contextes sur six hors contrôle, en vert. Il couvre aujourd'hui 26 couples, contre 11.

### Vérifié en exécution réelle

**981 tests** (contre 868 ce matin), `ruff` propre, migration montée **et** descendue.

L'image de l'API a été construite, **démarrée contre PostgreSQL**, et interrogée :
`/sante` rend `base_de_donnees: joignable`, la connexion aboutit, le référentiel est
bien embarqué dans l'image.

⚠️ La construction de l'image du front n'a pas abouti sur cette machine : le registre
npm expire à répétition — quatre-vingt-dix secondes par requête, `fetch failed` sur un
paquet différent à chaque tentative. Le cache de magasin pnpm fait converger les
essais, mais la liaison est le facteur limitant, pas le `Dockerfile`. **À reconstruire
sur une liaison correcte avant de considérer le déploiement vérifié.**

### Ce qui reste, et ce n'est plus technique

**Le référentiel n'est toujours pas validé.** Aucun chiffre produit n'est opposable
tant qu'un fiscaliste nommé n'a pas confirmé chaque paramètre sur le Code général des
impôts. Rien de ce qui précède ne change cela, et c'est le seul point qui décide si le
système peut servir.

---

## 16 août 2026 (suite) — Les écrans manquants

### Ce qui est livré

**Sept écrans sur onze sont construits.** Quatre restent inertes, et pour une raison
simple : leur contexte backend n'existe pas.

| Écran | État | Ce qu'il montre |
|---|---|---|
| Tableau de bord | ✓ | Identité réelle ; indicateurs encore fictifs, et l'écran le dit |
| Portefeuille | ✓ | Les dossiers du **périmètre**, statuts résolus à une date |
| Pièces justificatives | ✓ | La boîte de réception |
| Comptabilité | ✓ | Balance, santé d'avant dépôt, grand livre par compte |
| Obligations | ✓ | Échéancier calculé, déclaration de TVA, recevabilité du dépôt |
| Référentiel et règles | ✓ | Les 19 paramètres, leur fondement, leur statut |
| Comptes et habilitations | ✓ | Comptes, rôles datés, journal d'audit chaîné |
| Conformité, Clôture, Création, Pilotage | · | Contextes D partiellement, H, I, J — non implémentés |

### L'écran le moins spectaculaire est le plus important

Le **référentiel**. Tant qu'aucun paramètre n'est confirmé sur le Code général des impôts,
aucun chiffre produit par la plateforme n'est opposable — et c'est le seul endroit où cela
se voit d'un coup d'œil, paramètre par paramètre.

Il répond à une question, et une seule : **« sur quoi repose ce chiffre ? »** Un adhérent
redressé la posera, un vérificateur aussi, et il faut pouvoir répondre autrement que par
« le logiciel l'a calculé ». Chaque ligne porte son fondement en clair et sa source ; les
notes affichent les divergences, dont celle du seuil espèces qui varie d'un facteur cinq
entre deux documents.

⚠️ Il ne modifie rien. Le fiscaliste valide encore dans le YAML versionné, où la revue de
code voit le changement. Un écran d'édition devra journaliser chaque changement de valeur
légale — exigence plus lourde que l'écran lui-même.

### L'écran qui vend le produit

La **déclaration de TVA**, et une ligne en particulier : « dont écartée par le contrôle ».

Dans une déclaration ordinaire, une TVA rejetée est **invisible** — la case porte un
chiffre plus faible, et rien n'explique pourquoi. Ici chaque rejet est isolé, chiffré et
justifié pièce par pièce, avec le code de la règle et le motif en clair :

```
PJ-2026-0001   FAC-ACH-007   Le règlement en espèces dépasse le seuil légal…   379 350
```

C'est ce que l'adhérent aurait payé, et ce que le cabinet lui a évité.

### Trois décisions d'affichage

**Le sous-titre dit toujours à quelle date et sur quel périmètre on lit.** Sans lui, un
comptable qui compte trois dossiers là où le cabinet en suit six croit à une panne. Le
portefeuille annonce « affectés à votre portefeuille » ; les écrans datés affichent le jour
de résolution.

**Un tiret vaut mieux qu'un zéro.** Un montant estimé absent, un compte non lettré, un
exercice inconnu : le tiret dit « on ne sait pas », le zéro dirait « il n'y a rien à
payer ». Sur une échéance fiscale, la différence est celle d'une pénalité.

**Le ton d'alerte est réservé à ce qui bloque.** Une échéance dépassée le porte — la
pénalité court. Un compte non lettré, non : c'est du travail qui reste, pas une anomalie.

### Ce que les écrans avouent

Trois avertissements sont **écrits dans l'interface**, pas enfouis dans la documentation :

* le référentiel n'est pas validé, donc rien n'est opposable ;
* l'échéancier suppose que le dossier n'a **pas de salariés**, faute de contexte Social —
  l'impôt libératoire n'efface pas les cotisations CNPS, et un dossier avec salariés doit
  donc davantage d'obligations que ce qui s'affiche ;
* un accusé de dépôt sans justificatif archivé repose sur la seule saisie du numéro.

Un écran qui tait ses limites les fait découvrir par un contrôle.

### L'écran d'administration ne modifie rien, délibérément

Inviter, suspendre, affecter un dossier, fermer une habilitation : les routes existent, les
formulaires non. Ces gestes réclament des confirmations explicites — suspendre coupe les
sessions ouvertes, fermer une habilitation n'est pas réversible — et une confirmation
bâclée sur ces actes-là vaut moins que pas de bouton du tout.

Il montre en revanche trois signaux que rien d'autre ne montre : les comptes **jamais
activés** — l'état le plus fréquent en production et le plus oublié —, les collaborateurs
**habilités sans dossier**, et l'état de la chaîne d'audit.

### Vérifié en exécution réelle

Backend sur PostgreSQL, front compilé et démarré contre lui, connexion par vraie session,
sept écrans visités : tous rendent des données réelles — « SARL BATIMENT PLUS », le compte
401, `TVA_TAUX_GENERAL` à 19,25 %, la règle `FAC-ACH-007` et ses 379 350 F.

**868 tests backend, 87 pages compilées, types et `eslint` propres.**

⚠️ Une différence de comportement relevée au passage : le dépôt SQL trie les dossiers par
dénomination, le dépôt mémoire par ordre d'insertion. L'écran affiche donc AGRO en premier
et non BATIMENT. Le tri SQL est le bon — il est déterministe —, mais les deux réalisations
d'un même port devraient rendre le même ordre.

---

## 16 août 2026 — Les treize autres dépôts, et un piège refermé pour de bon

### Ce qui est livré

Les cinq contextes qui produisent des données vivent en base : le portefeuille, la
collecte, la comptabilité, la souscription, et le socle déjà migré. **Quatorze tables,
868 tests, aucun ignoré.**

L'application entière tourne sur PostgreSQL et survit au redémarrage — dossiers, pièces,
écritures, balance, déclaration de TVA, devis, souscription, paiement, compte adhérent créé
par l'encaissement.

### La forme retenue : document plus colonnes promues

Les entités de ce système sont des **agrégats immuables**. Une entreprise porte ses
régimes, ses rattachements, ses adhésions, ses exercices, ses mandats, ses dirigeants. Une
écriture porte ses lignes. Trois faits ont décidé :

* **On les lit toujours entières.** Aucun cas d'usage ne charge « les lignes d'une
  écriture » sans l'écriture. Normaliser produirait une trentaine de tables et autant de
  jointures pour rendre exactement le même objet.
* **Elles sont immuables.** Un changement produit un nouvel exemplaire, pas une mise à jour
  de sous-ligne.
* **Les calculs sont déjà en Python.** La balance et le grand livre sont calculés sur les
  écritures et jamais stockés — décision du contexte E. Rendre les lignes interrogeables en
  SQL ne servirait aujourd'hui personne.

Ce sur quoi on filtre, trie ou pose une contrainte sort du document et devient une vraie
colonne. Elle est alors écrite **deux fois**, et le dépôt les écrit ensemble : une colonne
promue qui ne suivrait pas le document ferait mentir toutes les requêtes sans qu'aucune
lecture d'entité ne le montre.

**Ce que ça coûte, et comment on en sort** : aucune intégrité référentielle sur le contenu
imbriqué, aucune requête SQL directe dessus. Le jour où « quels dossiers étaient au réel en
2024 » devra se répondre en SQL, les périodes prendront leur table — et la colonne document
restera, parce que `JSONB` se requête aussi.

⚠️ La contrepartie qui compte : **le document doit rester relisable**. Un champ retiré d'une
entité fait échouer la validation des lignes anciennes. Une évolution s'ajoute, elle ne
retranche pas.

### La clé d'écriture porte enfin le dossier

`2026/AC/000042` n'est unique qu'à l'intérieur d'un dossier — défaut relevé au premier
branchement des adaptateurs, contourné jusqu'ici par un dépôt en mémoire ouvert *pour un
dossier*. La clé primaire est désormais composite : locataire, entreprise, exercice,
journal, numéro. **La question ouverte depuis le lot 4 est close.**

### Le piège des tables non chargées, trois fois

Les métadonnées SQLAlchemy ne connaissent que les modules importés. Une table dont le
module n'est pas chargé n'existe pas de leur point de vue.

Je l'ai documenté dans `alembic/env.py`, puis je m'y suis pris **trois fois** : à
l'amorçage, à la première migration métier — qui n'a rien généré —, puis dans les tests. À
chaque fois, l'oubli était le même, à un endroit différent.

Il ne suffit pas de documenter un piège pour le refermer. Il y a maintenant **un
recensement unique**, `app/tables.py`, et un test qui vérifie qu'il est complet : il compare
le recensement aux fichiers `tables.py` présents sur le disque, vérifie que chaque table est
cloisonnée, et qu'aucune table déclarée n'est sans migration.

### Un défaut préexistant révélé par le parcours réel

`GET /comptabilite/dossiers/{niu}/balance` appelait `balance()` avec `inclure_brouillons`,
alors que le paramètre s'appelle `brouillons_inclus`. La route échouait en 500 **à chaque
usage réel** — et aucun test ne l'appelait.

Une route sans test n'est pas une route livrée : c'est du code qui compile. Quatre routes
de comptabilité sont maintenant couvertes.

### Deux décisions sur ce qui ne va pas en base

**Les catalogues restent en code.** Plan SYSCOHADA, journaux, catalogue d'obligations,
offre commerciale : ce sont des données de configuration, identiques pour tous les
locataires. Leur donner une table ne servirait qu'à devoir les y remettre à chaque nouvelle
base. Le plan d'**imputation**, lui, est propre à chaque dossier — il a sa table.

**Le magasin de fichiers n'aura pas de table.** Des documents scannés en base feraient
grossir les sauvegardes d'un facteur cent pour des données qui ne se requêtent jamais, et
rendraient chaque restauration inutilisable. La cible est un stockage objet ; ce qui va en
base est l'empreinte, déjà portée par la pièce. La classe existe et lève, pour que l'absence
soit nommée plutôt que découverte.

### L'amorçage refuse de s'exécuter deux fois

Il pose des comptes dont le mot de passe est en clair dans le dépôt. Rejoué sur une base qui
contient déjà des comptes, il écraserait des mots de passe réels par ceux de la
démonstration — et personne ne s'en apercevrait avant qu'un collaborateur ne se retrouve
dehors. Il refuse, et le message le dit.

Il a par ailleurs dû quitter `app/infrastructure/` : le garde-fou d'architecture a rappelé
que le cercle externe est appelé par le métier et ne l'appelle pas. Un amorçage connaît tous
les contextes — c'est de la **composition**, comme `app/main.py`.

### Ce qui reste

Le mode `postgresql` n'est toujours pas le défaut, et ce n'est plus par prudence technique :
la bascule est désormais une décision d'exploitation — base administrée, sauvegardée,
amorçage maîtrisé. `CGA_PERSISTANCE=postgresql` suffit.

⚠️ Une limite reste écrite dans le code : `prochain_numero` lit le maximum et ajoute un.
Deux transactions concurrentes obtiendraient le même, et la seconde échouerait sur la clé
primaire au lieu de prendre le suivant. Rien de faux n'est écrit ; l'appelant doit
recommencer. Une séquence par journal supprimerait ce cas.

---

## 15 août 2026 (suite 11) — La base tourne, et l'exécution réelle trouve ce que les tests ne voyaient pas

### Comment j'ai obtenu une base sans toucher au poste

Le serveur PostgreSQL du poste tourne, mais aucun rôle ne m'y donne accès et `sudo` réclame
un mot de passe. Créer un rôle dessus aurait de toute façon été discutable : on modifierait
la configuration d'une machine partagée pour faire tourner des tests.

J'ai donc monté **une instance à moi** : `initdb` dans un répertoire temporaire, port 55432,
socket dans un chemin court. Elle vit hors du dépôt et se jette. `outils/postgres-local.sh`
la démarre et l'arrête.

Un détail a coûté un essai : PostgreSQL refuse de démarrer si le chemin du socket dépasse
107 octets, et le message ne dit pas que c'est la longueur qui pose problème. Le répertoire
de travail temporaire dépassait largement ; le socket vit donc dans `/tmp/cga-pg`.

### Les 24 tests en attente, et les deux qui ont échoué

Vingt-deux sont passés du premier coup. Les deux échecs étaient **le même défaut** : mes
dépôts SQL ne filtraient que par l'écouteur de session, et fuyaient dès qu'on les
construisait sur une session ordinaire — un test, un script de reprise, une tâche de fond.

Le cloisonnement est désormais posé **deux fois**. L'écouteur protège de ce qu'on écrira
demain, sans qu'on ait à y penser. Le filtre explicite dans chaque requête rend le module
correct quelle que soit la session qui le porte. Ce n'est pas une redondance : ce sont deux
défauts différents qu'on ferme.

### Le mixin n'était pas un mixin

`Cloisonne` ne déclarait qu'une annotation, `locataire: str`. `with_loader_criteria`
inspecte l'expression `entite.locataire` et lui faut un attribut **mappé** : il levait au
premier filtrage réel.

La correction améliore le dessin. La colonne est maintenant portée par le mixin, donc une
table cloisonnée ne peut plus l'**oublier** : le seul oubli possible devient celui du mixin,
qui se lit sur la ligne de déclaration de la classe. Six déclarations de colonne ont
disparu au passage.

### Le défaut que seule l'exécution réelle pouvait révéler

L'application tournait sur PostgreSQL : connexion, second facteur, dépôt de TVA, refus du
second dépôt, journal d'audit intact. Puis j'ai **redémarré** — et l'accusé de réception
n'était pas là.

La route de dépôt avait son propre registre en mémoire, un `lru_cache` local que la base ne
voyait pas. Tout fonctionnait : le refus du second dépôt passait, les 830 tests étaient
verts. Et **la preuve de dépôt — la pièce la plus critique du système — disparaissait au
redémarrage pendant que tout le reste persistait**.

Aucun test unitaire ne pouvait le voir : chaque dépôt était juste pris isolément. Il fallait
faire tourner l'application réelle sur une vraie base, **puis redémarrer**. C'est
maintenant un test, et son message dit ce qu'il attrape.

### Alembic n'était pas installé, et ma vérification ne le voyait pas

`import alembic` réussissait parce que mon propre dossier `alembic/` masquait le paquet.
Mon contrôle du lot précédent — « alembic configuré » — ne testait donc que mon répertoire.
Un test qui passe pour la mauvaise raison est un test qui ment.

Installé, la migration initiale s'est générée et **s'applique sur une base vierge**. Les
quatre contraintes qui portent les garanties sont là :

```
uq_journal_audit_locataire_rang           deux processus ne peuvent pas écrire le même rang
uq_accuse_reception_locataire_reference   un second dépôt de la même période se heurte à la base
uq_compte_locataire_courriel              deux porteurs d'une adresse rendraient l'un inaccessible
uq_jeton_empreinte                        un lien d'activation est unique
```

Les migrations générées sont exemptées des règles de mise en forme : les reformater à la
main les ferait diverger de ce que l'outil régénère, et une migration relue doit ressembler
à sa voisine.

### Ce qui est vérifié maintenant

**857 tests, aucun ignoré.** Le socle vit en base — comptes, habilitations, jetons,
sessions, journal chaîné, registre des accusés — et l'application entière tourne dessus.

Le journal d'audit se relit après redémarrage et sa chaîne se vérifie : c'était la propriété
la plus incertaine, parce qu'une conversion JSON instable aurait fait déclarer toute la base
altérée au premier démarrage.

### Ce qui reste

Le défaut du registre en mémoire est instructif au-delà de son cas : **les treize autres
dépôts sont dans le même état**. Le mode `postgresql` ne doit donc pas devenir le défaut
avant qu'ils n'aient suivi — une application dont le socle persiste et dont la comptabilité
disparaît serait pire que tout en mémoire, parce que l'incohérence ne se verrait qu'à
l'usage.

---

## 15 août 2026 (suite 10) — Les échéances d'abonnement, et deux décisions commerciales

### Pourquoi celle-ci

La base PostgreSQL n'étant toujours pas accessible sur ce poste, empiler d'autres tables
non vérifiables aurait été le mauvais choix : du code non testé qui s'accumule. J'ai pris
le manque que j'avais signalé deux fois comme « le plus important du contexte M ».

**La première mensualité était encaissée, et plus rien ne se passait.** Un abonnement dont
la deuxième échéance n'est jamais appelée n'est pas un abonnement : c'est une vente unique
déguisée, et le cabinet travaille onze mois gratuitement.

### L'échéancier se calcule, il ne se stocke pas

Même discipline qu'au contexte F. Il découle de trois choses — date d'effet, périodicité,
date de résiliation — toutes trois déjà portées par la souscription. Le persister figerait
un calendrier qui deviendrait faux à la première résiliation, et personne ne verrait qu'il
l'est devenu.

Ce qui est stocké, ce sont les **paiements**. Une échéance est identifiée par sa période, et
son état se lit en confrontant l'échéancier aux paiements reçus.

### Les périodes suivent la date d'effet, pas le mois civil

Une souscription du 17 mars produit des périodes du 17 au 16. C'est ce qui **évite le
prorata** — et le prorata est ce qui rend une première facture incompréhensible. « Vous
payez 12 500 F par mois » doit vouloir dire exactement cela dès le premier prélèvement.

Le cas limite est traité et testé : le 31 janvier est ramené au 28 février, puis **le 31
revient** en mars. Le calcul se fait toujours depuis la date d'effet, jamais de proche en
proche — sans quoi un abonnement souscrit un 31 glisserait au 28 pour toujours après un
seul février.

### Deux distinctions portent tout le sens

`A_APPELER` contre `A_VENIR` : la première réclame une action aujourd'hui. Les confondre
produirait soit des prélèvements prématurés, soit une liste de travail qui ne se vide
jamais.

`IMPAYEE` contre `EN_DEFAUT` : la première est un incident — on relance. La seconde a
dépassé le délai de grâce et arrête le service. **Les confondre couperait le service au
premier échec de prélèvement**, alors qu'un solde momentanément insuffisant n'est pas un
défaut de paiement.

### Première décision : suspendre n'est pas séquestrer

Passé la grâce, le cabinet cesse de traiter les pièces et de préparer les déclarations.
L'adhérent **conserve l'accès en lecture** à son dossier.

Ce n'est pas de la mansuétude commerciale. Les pièces déposées et les écritures produites
sont **ses** documents comptables, qu'il est légalement tenu de conserver dix ans. Les lui
retenir pour obtenir un règlement l'exposerait à un manquement dont il n'est pas
responsable, et exposerait le cabinet à devoir s'en expliquer.

⚠️ La distinction n'est pas encore **appliquée** : le contexte K ne sait aujourd'hui que
suspendre un compte, ce qui coupe tout. La route rend donc une **décision** portant sa
consigne, que le cabinet applique à la main — plutôt qu'exécuter une coupure trop large.
Ce qu'il faudrait est une habilitation restreinte à la lecture, et c'est écrit dans le code.

### Seconde décision : un prélèvement refusé n'est pas rappelé automatiquement

C'est le test qui m'a forcé à trancher. La machine à états écarte déjà une échéance dont un
prélèvement est en cours ; la garde par clé d'échéance ne sert donc que dans un cas — après
un refus.

Rappeler chaque jour un prélèvement refusé produirait un menu de paiement quotidien sur le
téléphone de l'adhérent. C'est vécu comme du harcèlement, et chaque tentative peut lui être
facturée. Le rattrapage passe par la relance, qui l'informe, et par un règlement qu'il
déclenche lui-même.

La contrepartie est écrite : une échéance refusée reste due et ne sera **jamais** rappelée
par la tâche. C'est la relance qui la porte, et l'arrêt du service qui la sanctionne.

### Un vrai défaut trouvé par les tests

L'échéancier s'arrêtait sur le **début de période** au lieu de la **date d'appel**. Une
échéance devenait donc visible le jour de son exigibilité — c'est-à-dire trop tard pour
l'appeler cinq jours à l'avance. Le mécanisme entier était inopérant, et il compilait très
bien.

### Les relances informent avant de presser

Jalons J+1, J+7, J+14. Le premier n'est pas de la pression : **l'adhérent ignore souvent que
le prélèvement a échoué**, parce que l'opérateur ne le lui dit pas.

Le retard doit tomber **exactement** sur un jalon. Sans ce « exactement », un impayé de
vingt jours déclencherait les trois relances à chaque passage, et l'adhérent recevrait un
message par jour jusqu'au règlement — une relance quotidienne se filtre en trois jours et
cesse d'être lue.

Le champ `derniere` distingue le jalon qui annonce une conséquence de ceux qui informent :
les envoyer sur le même gabarit ferait passer l'avertissement pour un rappel de plus.

### Ce qui est livré

Quatre routes, 31 tests, **830 au total**. Et toujours 24 en attente de PostgreSQL.

---

## 15 août 2026 (suite 9) — La persistance, et la couture qui la rend inoffensive

### Pourquoi celle-ci maintenant

C'est le manque que je signale depuis six lots, et le dernier était le plus net : « le
registre des accusés est en mémoire — c'est le dépôt le plus critique du système à faire
passer en base. Une comptabilité se refait ; une preuve de dépôt, non. »

Un système qui perd les identités et les preuves de dépôt à chaque redémarrage n'est pas un
système auquel on confie des données fiscales.

### Le socle passe le premier, et ce n'est pas arbitraire

Sans identité persistante, rien d'autre ne sert : un redémarrage renvoie tout le monde à la
page de connexion avec des comptes qui n'existent plus. Et sans journal d'audit persistant,
la chaîne de hachage repart de la genèse à chaque démarrage — **elle n'atteste plus de
rien**.

Six tables : comptes, habilitations, jetons, sessions, journal d'audit, accusés de
réception.

### Le cloisonnement s'applique tout seul, et c'est ce que la doc exigeait

`05-securite-multitenant.md` § 1 : « Filtrage appliqué **dans la couche de persistance** —
session SQLAlchemy avec filtre systématique —, jamais laissé au développeur qui écrit la
requête. »

C'est fait par un écouteur `do_orm_execute` avec `with_loader_criteria` : toute requête ORM
sur une table marquée `Cloisonne` reçoit son critère. **On ne peut pas l'oublier parce
qu'on ne l'écrit jamais.**

Un filtre qu'il faut penser à écrire est un filtre qu'on oubliera, et l'oubli ne se voit
pas : la requête ne plante pas, elle rend simplement les lignes d'un autre cabinet.

⚠️ Ce que cela ne couvre pas, et c'est écrit dans l'en-tête : le SQL textuel échappe au
filtre et doit porter son `WHERE locataire = …` en toutes lettres.

Une lecture y échappe aussi, et elle est signalée en commentaire : `session.get()` interroge
par clé primaire sans passer par l'évènement. Les trois dépôts qui l'emploient vérifient le
locataire à la main.

### Deux garanties qui n'existaient pas, et qui étaient promises

**Le rang du journal d'audit est unique par locataire**, et la tête est lue avec
`FOR UPDATE`. L'en-tête du port `JournalAudit` réclamait cette atomicité depuis le premier
jour, avec la mention « une réalisation en mémoire ne peut pas le garantir ». C'est ici que
ce n'est plus vrai : le verrou sérialise, la contrainte d'unicité sert de ceinture.

**Le dépôt d'une déclaration est unique par référence**, garanti par la base et non par la
mémoire de celui qui saisit.

Les deux sont **par locataire** : deux cabinets ont chacun leur chaîne, et le dépôt de l'un
ne bloque jamais l'autre.

### Le piège que j'ai traité avant qu'il ne morde

Les entrées d'audit portent dates, décimaux et énumérations, que la colonne JSON ne sait pas
écrire. La conversion `default=str` est **stable pour l'empreinte** : `corps_canonique`
sérialise déjà ainsi, si bien qu'une entrée relue depuis la base recalcule exactement la
même empreinte.

Sans cette propriété, `verifier_chaine` aurait déclaré **toute la base altérée au premier
redémarrage** — un journal d'audit qui s'accuse lui-même. Un test l'exige explicitement, sur
une entrée portant les trois types.

### La couture : « la transaction est la requête »

`Atelier` avait une seule réalisation, mémoire, vivant le temps du processus. Il en a
maintenant deux, et leur **durée de vie diffère par nature** : l'atelier SQL porte une
session, et la transaction se ferme avec la requête.

Le point de bascule est un intergiciel. J'ai hésité, parce qu'une variable de contexte est
de l'état ambiant et que l'état ambiant se défend mal en général. Il se défend ici pour une
raison précise : faire traverser une session à dix-huit signatures de route ne donnerait
toujours pas la validation en fin de requête — **chaque route devrait y penser, et l'une
d'elles oublierait**. Le point d'ouverture et de fermeture est unique.

Hors requête, en mode PostgreSQL, `atelier()` **lève**. Un atelier fabriqué à la volée
ouvrirait une transaction que personne ne fermerait, et ses verrous sur la table du journal
bloqueraient toutes les écritures suivantes. Mieux vaut une erreur immédiate qu'une
application qui se fige au bout d'une heure.

### Le défaut reste la mémoire, et c'est délibéré

Basculer maintenant donnerait une application dont le socle persiste et dont la comptabilité
disparaît au redémarrage — **pire que tout en mémoire**, parce que l'incohérence ne se
verrait qu'à l'usage. Le mode `postgresql` s'allumera quand les treize autres dépôts auront
suivi.

### Alembic, parce que `create_all` n'est pas une migration

Il ne modifie aucune table déjà présente : une colonne ajoutée au modèle n'apparaîtrait pas,
et le code échouerait sur une colonne absente sans que rien n'explique pourquoi. C'est écrit
dans la fonction elle-même.

Trois choix consignés dans `env.py` : l'adresse de la base vient de la configuration et non
du `.ini` — c'est là qu'on met un mot de passe par habitude, et qu'il finit versionné ;
`compare_type` est activé, sans quoi un `String(64)` devenu `String(120)` ne produit aucune
migration ; et **toutes les tables sont importées**, faute de quoi `autogenerate` propose de
supprimer celles qu'il ne voit pas — le piège classique.

Le gabarit de migration rappelle que `downgrade` rétablit le schéma, jamais le contenu, et
que sur les tables append-only il n'y a rien à défaire.

### Ce que j'ai livré, et ce que je n'ai pas pu vérifier

**799 tests verts**, dont cinq nouveaux sur la couture. Et **24 tests ignorés** faute de
base : le rôle PostgreSQL n'a pas été créé sur ce poste.

Ils ne sont pas silencieusement passés — le message d'ignorance porte le motif exact et la
commande à lancer. Un test vert parce qu'il ne s'est pas exécuté est pire qu'un test rouge.

Trois des propriétés qu'ils vérifient n'existent ni en mémoire ni sur SQLite : le verrou de
ligne, l'unicité du rang sous concurrence, l'unicité du dépôt. Les tester sur SQLite aurait
reviendrait à tester autre chose — c'est pourquoi j'ai posé la question plutôt que de
prendre le raccourci.

---

## 15 août 2026 (suite 8) — L'interopérabilité DGI, et ce que je ne sais pas

### Ce qui a été demandé

Que le système soit interopérable avec la télédéclaration de la DGI — « c'est aussi ça
l'intérêt ». Et, avant cela : est-ce que tout est ok ?

### Non, et voici ce qui ne l'est pas

**Aucune valeur légale n'est validée.** Dix-neuf paramètres au statut `A_VALIDER`. La
question Q1 porte sur une divergence d'un facteur cinq — 100 000 contre 500 000 FCFA — sur
la règle qui produit le plus gros enjeu du jeu de démonstration. Personne n'est nommé
référent de validation. **Rien de ce que produit le système n'est opposable.**

**Rien n'est persistant.** Quatorze dépôts en mémoire. Un redémarrage vide tout.

**Treize écrans sur seize n'existent pas.**

**Les échéances d'abonnement du contexte M** ne sont ni appelées ni relancées.

**Aucune limitation de débit** sur les routes publiques.

### La réponse honnête sur la DGI, et elle détermine tout le reste

**La DGI ne publie aucune interface programmatique.** Ni adresse d'API documentée, ni
format d'échange, ni jeu d'essai, ni environnement de recette. Le portail de
télédéclaration est un site que l'on remplit à la main.

Inventer une charge utile, des noms de champs et des codes de retour aurait produit un
adaptateur qui compile, qui se teste contre lui-même, et qui ne fonctionnera jamais. Ce
serait pire que de ne rien écrire : **le système paraîtrait branché**.

J'ai donc modélisé le **dépôt**, pas l'interface de la DGI. Ce qui suit est vrai que le
dépôt se fasse par formulaire à l'écran ou par appel réseau — et c'est précisément ce qui
permettra de substituer l'un à l'autre sans toucher au métier.

Cinq questions sont consignées en Q1 bis. La plus lourde : **existe-t-il un compte de
rattachement CGA permettant de déposer *pour* un adhérent ?** Elle décide si la plateforme
pourra déposer, ou seulement préparer. Sans elle, il faudrait détenir les identifiants de
chaque adhérent — ce qu'aucun cabinet sérieux ne veut faire.

### Il fallait d'abord lever un blocage qu'on s'était imposé

`EXIGE_MFA` déclarait depuis le premier jour que le dépôt d'une déclaration réclame une
authentification forte. Aucun second facteur n'existait, donc l'action était refusée.
Blocage assumé, visible, et sans conséquence **tant qu'il n'y avait rien à déposer**.

Il y a maintenant quelque chose à déposer. On lève l'obstacle, pas la garde.

**TOTP, et rien d'autre.** Le SMS ne convient pas : l'échange de carte SIM est le mode
d'attaque le plus courant sur les comptes qu'il protège, et il est d'autant plus praticable
là où l'identification à l'achat d'une puce est inégale. Il suppose en outre un réseau, un
fournisseur et un coût par envoi — donc une panne possible la veille d'une échéance.

TOTP fonctionne hors ligne, sans tiers et sans coût. L'algorithme est public — RFC 6238 —
et tient en quinze lignes. Écrire soi-même de la cryptographie est une faute ; recopier une
norme dont chaque étape est spécifiée n'en est pas une, et évite une dépendance.

**Le piège du fuseau, et il est réel.** `datetime.timestamp()` sur un horodatage naïf
suppose le fuseau local de la machine. Le Cameroun étant à UTC+1, un serveur mal configuré
produirait des codes décalés de cent vingt tranches — jamais valides, sans le moindre
message d'erreur. Un test le protège, et un autre vérifie l'implémentation contre le
**vecteur d'essai publié de la RFC** : sans référence externe, générateur et vérificateur
partagent l'erreur et le test passe quand même.

**Le second facteur renforce une session, il ne la crée pas.** On ne réclame pas de code à
la connexion : pour un outil ouvert dix fois par jour, cela conduit à une seule chose — le
téléphone posé déverrouillé à côté du clavier. Il est réclamé **au moment de l'acte
sensible**, et élève la session pour quinze minutes.

### Deux fuites trouvées en chemin, et elles étaient graves

`Compte` sérialisait `empreinte_mot_de_passe`. La route **publique** de définition du mot
de passe rendait donc le compte, empreinte Argon2 comprise, à un appelant non authentifié.
Une empreinte livrée est de la matière à casser hors ligne, tranquillement, sans limite de
tentatives et sans que rien ne l'enregistre.

Le secret TOTP allait suivre le même chemin. Les deux champs sont désormais exclus **au
niveau du champ**, et non route par route : une exclusion à écrire route par route est une
exclusion qu'on oubliera à la prochaine.

### Ce qui a le plus de valeur n'est pas le transport

Un CGA n'est pas un tuyau vers la DGI. Son agrément l'engage sur la sincérité de ce qu'il
transmet, et un adhérent redressé sur une déclaration visée par son centre se retourne
contre le centre. **Refuser un dépôt est un service, pas une entrave.**

Trois niveaux, et la distinction est tout le sujet :

* **`BLOQUANT`** — la déclaration serait fausse. Balance déséquilibrée, rupture de
  numérotation, période déjà déposée, dossier hors assujettissement.
* **`RESERVE`** — elle peut partir, mais quelqu'un doit l'assumer. TVA écartée par le
  moteur de conformité, pièces non traitées, **et le référentiel non validé**.
* **`INFORMATION`** — échéance dépassée, déclaration à néant.

Les confondre produirait l'un des deux échecs symétriques : un système qui ne dépose jamais
rien parce qu'un détail traîne toujours, ou un système qui dépose tout et ne sert à rien.

Sur le jeu de démonstration, la préparation rend :

```
déposable            : true
exige une décision   : true
[RESERVE] REFERENTIEL-NON-VALIDE
[RESERVE] TVA-REJETEE-PAR-LE-CONTROLE   enjeu = 379 350
```

Cette seconde ligne **est** la valeur du produit : 379 350 FCFA de TVA qui auraient été
réclamés et refusés.

### L'accusé de réception est la seule preuve qui compte

Une obligation n'est pas déposée parce que le système le croit : elle l'est parce qu'un
accusé existe. Trois décisions en découlent.

**`declaree_le` reçoit la date de l'accusé**, jamais celle de la saisie. Un réviseur qui
dépose le 14 et consigne le numéro le 17 doit voir le 14 : c'est cette date que
l'administration retient pour calculer une pénalité.

**L'accusé porte l'empreinte de ce qui a été déposé.** On prépare, on découvre une écriture
à corriger, on corrige, on régénère — et l'on colle le numéro obtenu **avant** la
correction. Les chiffres déposés ne sont alors pas ceux du système, et plus personne ne le
sait. L'empreinte le refuse.

**La référence n'inclut pas la date de dépôt** — dossier, obligation, période. Un second
dépôt de la TVA de juillet se heurte au premier quel que soit le jour : redéposer produit
une déclaration rectificative non demandée, parfois un double appel de paiement.

### Le portail manuel n'est pas un pis-aller

Il ne dépose rien, et `deposer()` lève. Ce n'est pas une lacune : un adaptateur qui
feindrait de déposer produirait des accusés inventés — de faux justificatifs, dans un
système dont c'est la raison d'être d'en produire de vrais.

Ce qu'il fait est la moitié utile : il **consigne** l'accusé rapporté du portail, après
avoir vérifié qu'il porte bien sur le document préparé.

### Le parcours, joué de bout en bout

```
enrôlement TOTP        → secret rendu une fois
code faux              → 401
code juste             → facteur_fort = true
dépôt sans renforcement→ 403 SecondFacteurRequis
dépôt                  → DECLAREE, déclarée le 2026-08-14 (date de l'accusé)
second dépôt           → 409 DEPOT-DEJA-EFFECTUE
journal d'audit        → chaîne intacte
```

**794 tests.** Quarante-trois nouveaux.

### Ce qu'il faut savoir avant d'y croire

**Le registre des accusés est en mémoire.** C'est le dépôt le plus critique du système à
faire passer en base — avant les écritures, avant les pièces. Une comptabilité se refait ;
une preuve de dépôt, non.

**Le secret TOTP est stocké en clair.** Contrairement à un mot de passe, il doit être relu
pour recalculer le code : on ne peut pas n'en garder que l'empreinte. Il devra être chiffré
au repos, avec une clé qui ne figure pas dans la base.

**`piece_jointe` n'est pas résolue** tant que la GED n'existe pas. Un accusé sans
justificatif archivé repose sur la seule parole de celui qui a saisi le numéro, et
`verifiable` le dit à l'écran plutôt que de l'enfouir.

---

## 15 août 2026 (suite 7) — Le front branché, et les portes enfin fermées

### Ce qui a été demandé

Continuer. L'objectif posé au départ était de brancher le front ERP, une fois la logique
de connexion et d'accès aux ressources correctement implémentée. K et M étant faits, le
verrou était levé.

### Ce que j'ai trouvé en commençant, et qui a changé le plan

Les routes de **B, C, E et F étaient ouvertes**. Vingt-quatre routes, aucune session
exigée, aucun périmètre vérifié. Le contexte K portait toute la mécanique du cloisonnement
— habilitations datées, portées, `Acces` résolu — et **personne ne l'appelait**.

Un front qui filtrerait par-dessus une API ouverte est du théâtre : n'importe qui sachant
lire l'onglet réseau appelle `/comptabilite/dossiers/{niu}/balance` directement. J'ai donc
fermé les portes avant de dessiner les écrans.

### La décision de sécurité de ce lot : hors périmètre rend 404

Deux outils ont été ajoutés à K, et la distinction entre eux **est** le sujet :

* `restreindre(acces, elements, niu)` — **une liste se restreint**. Refuser toute la boîte
  de réception parce qu'elle contient les pièces d'un autre dossier la rendrait vide en
  permanence.
* `exiger_dossier(acces, permission, niu)` — **une lecture unitaire se refuse**. On ne rend
  pas « une version amputée » d'un dossier.

Et le refus est un **404**, pas un 403. Un 403 dit « ce dossier existe, et il ne vous
regarde pas » : c'est une information, et elle a de la valeur. Un adhérent apprendrait par
essais successifs quels NIU le cabinet suit, c'est-à-dire la liste de ses clients — laquelle
intéresse un concurrent. Du point de vue de qui n'y a pas accès, un dossier hors périmètre
est un dossier qui n'existe pas.

Le 403 reste employé quand c'est la **permission** qui manque, sans dossier en jeu : rien
n'y est révélé qu'on ne sache déjà, la table des rôles étant publiée.

Un détail qui compte : le filtre explicite `?entreprise=` est contrôlé **avant** d'être
appliqué. Sans cela, demander le NIU d'un dossier hors portefeuille rendrait une liste
vide, et l'absence de résultat se distinguerait mal du refus.

### Un manque réel que le branchement a révélé

Le réviseur ne pouvait pas déposer de pièce. Ni le comptable, ni le chargé de clientèle :
`DEPOSER_PIECE` n'était accordée qu'à l'adhérent.

Or `CanalDepot.DEPOT_CABINET` existe dans le contexte C. Ce canal décrit ce qui se passe
réellement — un adhérent apporte ses factures en main propre, et un collaborateur les
saisit. Réserver la permission aux seuls adhérents rendait ce canal inutilisable, et la
faute n'était visible qu'au moment de brancher.

Trois rôles l'ont reçue, avec la justification écrite dans la table.

### Le front : le navigateur ne parle jamais au backend

Tous les appels passent par le serveur Next — composants serveur pour les lectures, actions
serveur pour les écritures. Trois raisons, et la troisième est la plus importante :

1. **Le témoin de session reste sur une seule origine.** Pas de CORS avec identifiants, pas
   de `domain=.cga-brcg.cm` à configurer, pas de différence de comportement entre le
   développement et la production — donc pas de bogue qui n'apparaît qu'après déploiement.
2. **L'adresse du backend reste privée**, et l'API n'a pas à être exposée publiquement.
3. **Le témoin est `HttpOnly`.** Un jeton que le JavaScript de la page devrait lire pour
   l'envoyer lui-même ne peut pas l'être — et cesserait d'être protégé d'une injection.

Conséquence concrète : `NEXT_PUBLIC_API_URL` est devenu `API_URL`. Le préfixe `NEXT_PUBLIC_`
publiait l'adresse dans le code livré au visiteur.

### Le formulaire de connexion authentifie réellement

Il en portait l'aveu en tête : « ⚠️ CE N'EST PAS UNE AUTHENTIFICATION. La comparaison se
fait **dans le navigateur**, contre deux constantes présentes dans le code livré au
visiteur. » Les deux constantes ont disparu, ainsi que le bloc qui les affichait à l'écran.

Il fonctionne **sans JavaScript** : `action={...}` sur un `<form>` produit un POST ordinaire
tant que le script n'a pas pris la main. Sur les connexions visées, c'est la différence
entre « je peux me connecter » et « la page ne fait rien ».

Le message d'échec est celui du backend, **tel quel** — le même quelle que soit la cause. Le
préciser côté front rouvrirait l'oracle d'énumération que le backend prend soin de refermer.

Et le routage après connexion n'est pas un choix offert : le backend rend `interne`, l'action
serveur route en conséquence. Demander « êtes-vous collaborateur ou adhérent » apprendrait
au visiteur qu'il existe deux espaces, et laisserait un adhérent atterrir sur des écrans dont
aucune donnée ne le concerne.

### La porte est gardée dans le gabarit

`exigerAcces()` est appelé dans le gabarit `(collaborateur)`, donc **avant tout rendu**.
Taper `/tableau-de-bord` sans session renvoie à la connexion, et aucun écran n'est produit —
ni son balisage, ni ses données.

Le gabarit est le bon endroit : il enveloppe tous les écrans du groupe, y compris ceux qui
n'existent pas encore. Le mettre dans chaque page reviendrait à parier qu'on n'en oubliera
aucune.

⚠️ Cela **ne remplace pas** le contrôle côté API. Un gabarit protège des écrans ; il ne
protège pas des données, qui s'obtiennent aussi bien par un appel direct.

### Les treize liens morts : une troisième voie

Le menu comptait seize entrées et trois écrans. Trois façons de traiter le problème :

1. **Les laisser cliquables** — on tombe sur une 404. C'était l'état précédent, et c'est le
   pire : le collaborateur ne sait pas s'il a mal cliqué, si le serveur est tombé, ou si
   l'écran n'existe pas.
2. **Les retirer** — le menu est honnête mais muet. Le cabinet ne peut plus suivre
   l'avancement sur l'écran qu'il utilise tous les jours.
3. **Les montrer inertes, et le dire.** C'est ce qui est fait : grisées, non cliquables,
   marquées « à venir ». Le menu dit à la fois où l'on en est et où l'on va.

Rendues en `<span>` et non en `<a>` désactivé : un lien mort reste annoncé comme lien par un
lecteur d'écran, et se traverse au clavier pour n'aboutir nulle part.

Le menu est par ailleurs filtré sur les permissions réelles. ⚠️ **Masquer n'est pas
protéger** — c'est écrit à trois endroits du code, parce que c'est l'erreur qu'on commet
ensuite.

### Ce qui a quitté le jeu de démonstration du front

* L'utilisateur connecté et son rôle → `GET /transverse/moi`
* Les six entreprises et leurs régimes → `GET /portefeuille/entreprises`
* Les deux compteurs de la barre latérale → contexte C

Restent les indicateurs du tableau de bord, les échéances et les anomalies. Ils relèvent du
contexte **J · Pilotage**, qui n'existe pas — aucune route ne rend d'indicateurs consolidés,
et les recalculer dans un écran ferait descendre du métier dans une page. L'en-tête du
tableau de bord dit désormais **quelle moitié est vraie** : un tableau de bord dont on
l'ignore est un tableau de bord qu'on ne peut pas montrer au cabinet.

Une notion a disparu sans être remplacée : les « dossiers récents » du sélecteur, qui étaient
une constante en dur. La rétablir suppose de savoir ce que **ce** collaborateur a ouvert
récemment — une préférence par compte, affaire de K. Inventer un ordre plausible ferait
croire à une mémoire qui n'existe pas.

### L'espace adhérent, qui n'existait pas

L'action de connexion routait les adhérents vers `/mon-espace`, page introuvable. Le
parcours de souscription construit au lot précédent s'arrêtait donc sur une 404, une étape
avant la fin.

L'écran existe maintenant : son dossier avec les statuts résolus, ses pièces avec leur état.
Groupe de routes distinct, cibles de 44 px — l'adhérent ouvre son téléphone entre deux
clients, le collaborateur travaille à deux écrans. Ce sont deux produits qui partagent un
backend, pas un produit avec deux thèmes.

Il n'y voit pas de comptabilité : `ADHERENT` ne porte pas `LIRE_COMPTABILITE`, et l'API
refuserait. Un solde intermédiaire lu comme définitif conduit à des décisions de trésorerie
fondées sur un brouillon.

### Ce qui est livré, et vérifié

**750 tests** côté backend, dont onze nouveaux qui prouvent le cloisonnement **par les
routes réelles** : aucune route métier ouverte, deux comptables aux listes disjointes, le
dossier d'un collègue en 404, la boîte de réception restreinte, un adhérent limité à son
dossier et refusé sur la comptabilité, le comptable parti qui ne se connecte plus.

Le parcours a été rejoué de bout en bout contre le backend, pour les deux profils :

```
Léonard FOTSO   comptable  interne=true   3 dossiers   6 pièces   11 en souffrance
Jean-Pierre NKOA adhérent  interne=false  1 dossier    8 pièces   doublons: 403
```

### La compilation, et ce qu'elle a coûté

L'installation de `node_modules` était incomplète : le `node_modules` de la racine du
workspace était **vide**, et seules les dépendances directes du front existaient. D'où
`@swc/helpers` introuvable et les types de `next-intl` non résolus.

Le réseau s'est révélé très instable — délais dépassés en série sur le registre npm. Trois
tentatives ont été nécessaires :

1. `pnpm install` refuse de purger `node_modules` sans terminal interactif. `CI=true` lève
   la garde ; l'installation échoue en cours de route sur des délais dépassés. **Rien n'est
   perdu** : la purge n'ayant pas eu lieu, l'état d'origine est intact.
2. `--offline` : 359 paquets sur 373 sont déjà dans le store local de 488 Mo. Quatorze
   manquent.
3. `--prefer-offline --network-concurrency=2` : passe en quatre minutes.

Restait un binaire natif, `@swc/core-linux-x64-gnu`, dont le tarball de 12 Mo n'était jamais
descendu. Comme c'est une dépendance **optionnelle**, pnpm avait absorbé l'échec en silence
et déclarait ensuite « already up to date » sur un répertoire vide. Récupéré à la main et
déposé à sa place — le lien symbolique l'attendait déjà.

### Un défaut réel que seule la compilation pouvait révéler

```
Error: You're importing a module that depends on "next/headers" into a
React Client Component module.
  ./app/lib/api.ts → ./app/lib/session.ts → ./app/components/coquille/EnteteTravail.tsx
```

`EnteteTravail` est un composant client et importait `initiales` depuis `session.ts`, lequel
importe `api.ts`, lequel lit le témoin de session. Le compilateur avait raison : **un module
qui lit des en-têtes de requête n'a rien à faire dans un paquet envoyé au navigateur**.

Le contrôle de types ne pouvait pas le voir — les deux modules sont valides pris séparément,
c'est leur combinaison qui ne l'est pas. Seule la frontière client/serveur, que le
compilateur seul connaît, le fait apparaître.

La correction est une meilleure frontière, pas un contournement :

* **`acces.ts`** — les types `Acces`, `Role`, `Permission` et les fonctions pures
  `detient`, `voit`, `initiales`, `LIBELLES_ROLE`. Rien qui lise, rien qui appelle.
  Importable de partout.
* **`session.ts`** — `acces()` et `exigerAcces()`, qui lisent le témoin. Serveur seulement.

### Résultat

```
✓ Compiled successfully in 190ms
✓ Generating static pages (73/73) in 1159ms
```

Soixante-treize pages statiques, aucune erreur, `eslint` propre. Les écrans de l'espace de
travail et de l'espace adhérent sont marqués **`ƒ` — rendus à la demande**, ce qui est
exactement ce qu'on veut : ils lisent le témoin de session, ils ne peuvent pas être
pré-rendus.

### Ce qui reste

* **Les écrans de portefeuille, comptabilité et obligations** — treize entrées de menu.
* **Le dépôt de pièce par l'adhérent.** La permission est détenue, la route existe, mais
  elle réclame l'empreinte du fichier et le magasin de fichiers n'a pas d'adaptateur réel.
  Un bouton qui ouvrirait un sélecteur sans savoir où déposer serait un mensonge d'interface.
* **Le contexte J · Pilotage**, dont dépend la moitié encore fictive du tableau de bord.
* **Les échéances d'abonnement** du contexte M, toujours le manque le plus important.

---

## 15 août 2026 (suite 6) — Le contexte M, et l'argent qu'on ne perd pas

### Ce qui a été demandé

Le parcours de souscription : le service choisi sur la vitrine, le paiement, et le lien de
définition envoyé une fois le règlement validé.

### La décision qui a coûté le plus de réflexion : un treizième contexte

Le dossier d'architecture en décrit douze. Trois placements étaient possibles pour la
souscription, et les trois échouent :

* **L · Vitrine** est du contenu éditorial, et son isolement est délibéré — la doc écrit
  elle-même que « du contenu qui aurait besoin d'un paramètre légal ne serait plus du
  contenu ». Un encaissement encore moins.
* **I · Création d'entreprise** est une prestation parmi cinq. Y loger la souscription
  obligerait à passer par la création pour vendre une domiciliation.
* **A · Référentiel** porte des valeurs **légales**. Les honoraires du cabinet n'en sont
  pas : il les fixe librement, et les mêler aux taux du Code général des impôts brouillerait
  la seule chose que le référentiel doit garantir.

Ce que M détient et que personne d'autre ne détient : **combien coûte notre service, et
comment on l'encaisse**. Il lit le portefeuille pour une seule question — ce NIU est-il déjà
suivi ? — et n'est lu par personne.

Une souscription n'est **pas** un dossier. Elle dit qu'un accès a été payé, pas que
l'entreprise existe. Créer automatiquement l'entreprise au portefeuille y ferait entrer des
dossiers dont on ne sait rien, alors que le contexte B tout entier repose sur l'idée qu'on ne
sait d'une entreprise que ce qu'on a constaté.

### Le barème sort des fichiers de traduction

Les prix vivaient dans `messages/fr/vitrine.json` et `messages/fr/pages.json`. Un tarif rangé
dans un fichier de traduction ne se change pas sans redéploiement, n'a aucune date d'effet,
et **vit en double dès qu'une seconde langue existe** — la version anglaise et la française
auraient chacune leur prix, et rien ne dirait lequel fait foi.

Il est désormais daté, `[du, au[`, comme un paramètre du référentiel. Deux versions
coexistent au catalogue, 2024 et 2026, pour que le mécanisme se prouve : un test lit le prix
au 31 décembre 2025 puis au 1er janvier 2026 et obtient deux réponses.

⚠️ Les montants antérieurs à 2026 sont **reconstitués** — le cabinet n'a pas fourni son
historique tarifaire. Ils démontrent le mécanisme, ils ne facturent rien.

### Le devis fige le prix du jour

Ses lignes portent des **montants recopiés**, pas des renvois au catalogue. C'est ce qui
distingue un devis d'une page de tarifs : la page affiche le prix d'aujourd'hui, le devis
engage sur celui d'hier.

Sans cette copie, un devis reçu le 20 mars et ouvert le 2 avril afficherait le barème
d'avril. La page d'estimation du site signalait déjà ce défaut en commentaire.

Validité trente jours. Passée cette date, le devis devient **caduc**, il n'est pas supprimé :
le prospect qui revient voit ce qu'on lui avait proposé plutôt qu'une page introuvable.

### La règle de facturation qu'il a fallu corriger en cours de route

J'avais d'abord écrit : `montant_a_regler` exclut les abonnements. Un devis d'adhésion seule
tombait alors à zéro, donc non payable — le produit principal devenait insouscriptible.

La règle correcte est conditionnelle, et elle est celle du métier : un abonnement n'est
encaissé que **s'il est seul au devis**, sa première échéance mettant la prestation en route.
Adossé à une création d'entreprise, il ne gonfle pas le total — c'est exactement ce que la
page d'estimation annonce en note : « cet abonnement se règle mensuellement, il n'entre pas
dans le total à régler à la création ».

Le backend doit dire la même chose que la vitrine. Un client qui lit 165 000 sur le site et
voit 177 500 au moment de payer n'achète pas, et il a raison.

### La création d'entreprise n'est pas souscriptible en ligne, et c'est assumé

Ses frais officiels — caisse du guichet unique, droits d'enregistrement, RCCM, journal
officiel, timbres — sont des **valeurs légales**. Elles relèvent du contexte A, elles n'y sont
pas, et il y a une seconde raison de ne pas les y verser en l'état : `bareme-creation.ts`
signale lui-même que les montants de la maquette, agrégés en trois lignes, **divergent de la
proforma réelle du cabinet**, qui en compte huit pour le même total.

Verser des chiffres qu'on sait approximatifs dans un référentiel dont la raison d'être est
l'exactitude serait pire que de ne rien y verser. **Encaisser un montant qu'on sait faux
serait pire que ne rien encaisser.**

La création produit donc une demande de devis. C'est déjà ce que la vitrine annonce : « Le
devis définitif vous est confirmé après examen de votre projet, sans frais de dossier. »

### Le paiement : ce qui est repris du module Django, et pourquoi ligne à ligne

Le module `mail+paiement/` a été durci en production, et chacune de ses particularités a été
payée d'un incident. Sont conservés **à l'identique** :

* l'adresse de base est **`www.dklo.co`**, et non `taramoney.com` ;
* `productPrice` est un **entier**, pas une chaîne ;
* `phoneNumber` s'écrit `2376xxxxxxx`, sans « + » ;
* `network` part **vide** : Tara déduit l'opérateur du préfixe, et le lui imposer route vers
  le mauvais réseau — décision client du 25 juin 2026 ;
* Tara répond parfois **200 avec une erreur dans le corps**, qu'il faut lire.

Ce qui a changé : le modèle Django et son ORM disparaissent derrière nos ports. Ce qui reste :
les invariants.

### Les quatre garanties contre le double-encaissement

**La clé d'idempotence est la nôtre**, tirée chez nous et transmise comme identifiant de
produit. C'est elle qui permet de retrouver l'opération même quand le prestataire ne rend pas
la sienne.

**Le rapprochement a trois stratégies**, parce que la première ne suffit pas : le champ
`productId` revient parfois vide selon le chemin emprunté chez l'opérateur. La troisième —
téléphone plus récence — exige **le même montant**, sans quoi deux souscriptions engagées
depuis le même téléphone dans la demi-heure se croiseraient et la moins chère validerait la
plus chère.

**La validation est rejouable.** Le prestataire renvoie la même notification plusieurs fois ;
un paiement déjà validé se rend inchangé. Une seconde garde existe côté souscription :
`activee_le` refuse d'être reposée. Un test rejoue quatre fois la notification et vérifie
qu'un seul compte a été créé.

**La réconciliation renverse la charge : c'est nous qui appelons.** L'adresse de rappel est
injoignable pendant un redéploiement, une notification se perd — et dans ces cas l'abonné a
été débité pendant que rien ne bouge chez nous. Au bout d'un moment **il repaie**, et c'est là
que naît le double-encaissement : non par un défaut de notre code, mais par notre silence.

### Une décision d'ordre d'écriture qui paraît absurde et ne l'est pas

La souscription et le paiement sont enregistrés **avant** l'appel au prestataire.

Appeler d'abord et écrire ensuite laisserait, en cas de panne entre les deux, une opération
vivante chez l'opérateur dont nous n'aurions aucune trace. Écrire d'abord produit le défaut
inverse, bénin : un paiement en attente sans opération réelle, que la réconciliation périme
au bout de vingt-quatre heures.

**Entre un enregistrement de trop et un encaissement perdu, on choisit l'enregistrement de
trop.**

### Deux états au lieu d'un, et c'est tout le sujet

`PAYEE` signifie que l'argent est arrivé. `ACTIVEE` signifie que le compte existe et que le
lien est parti. Les fondre en un seul état rendrait invisible le seul cas qui compte :
**encaissé mais pas activé**.

Ce cas se produit — le service de courriel tombe, l'adresse est déjà prise, le processus
redémarre entre deux écritures. Avec un état unique, le client a payé, n'a rien, personne ne
le sait, et il rappelle trois jours plus tard. Avec deux états, `GET /souscription/a-activer`
le fait apparaître sans qu'on ait à le chercher.

L'échec d'activation ne rejette donc **jamais** le paiement. On ne rejette pas un encaissement
réel parce qu'un serveur de courriel était indisponible.

### Une factorisation faite avant d'écrire le second chemin

La notification entrante et la réconciliation aboutissent toutes deux à « appliquer un
évènement à un paiement ». J'ai extrait `appliquer_evenement` avant d'écrire la seconde :
deux copies de cette logique auraient fini par diverger, et l'une aurait activé là où l'autre
rejette. Un test vérifie que les deux chemins n'ouvrent qu'un seul compte.

### Ce que le garde-fou d'architecture a attrapé

Les routes de M importaient `transverse.adaptateurs.entrant.dependances`, un module interne.
Le test l'a refusé. La correction a produit deux améliorations réelles :

**L'horloge est sortie du contexte K.** `maintenant()` y vivait ; un instant en UTC n'est pas
une affaire d'identité. Elle est passée dans `app/partage/horloge.py`, où les deux contextes
la lisent.

**Les dépendances HTTP sont passées en surface publique.** Résoudre un `Acces` depuis une
requête est un service du socle, que toutes les routes de tous les contextes emploieront.

Au passage, un cycle d'import est apparu — `api.py` important `dependances`, qui important
`api`. Réglé en faisant lire à `dependances` les modules concrets de son propre contexte : la
surface publique est faite pour les *autres*, pas pour soi-même.

### Ce qui est livré

**Dix routes, quatre dépôts, un fournisseur de paiement, 97 tests.** Le total passe à **739**.

Le parcours complet est prouvé de bout en bout par un test : devis → engagement → notification
→ compte créé → lien envoyé → mot de passe défini → connexion, avec vérification finale que
l'adhérent voit son dossier et seulement le sien.

### Ce qui manque, et qu'il faut dire

**Les échéances d'abonnement.** La première mensualité est encaissée ; les suivantes ne sont
ni appelées, ni relancées. C'est le manque le plus important de ce lot.

**Aucune limitation de débit** sur les routes publiques. Rien n'empêche d'établir dix mille
devis. La limitation appartient à la couche d'entrée ; l'oublier au déploiement exposerait le
prestataire à un flot d'initiations.

**Tara ne renvoie pas le montant dans sa notification.** Le contrôle de cohérence ne peut donc
pas s'exercer sur ce chemin : une notification forgée par quelqu'un qui aurait deviné
l'adresse de rappel et l'identifiant marchand validerait le paiement sans qu'aucun montant ne
soit confronté. Le filet est la réconciliation, par appel sortant.

**Aucun remboursement** n'est représenté.

---

## 15 août 2026 (suite 5) — Le contexte K, et la question que pose un contrôle

### Ce qui a été demandé

Brancher le front sur le backend, « mais sauf qu'il y a une logique de connexion et
d'accès ressource qui doit être bien implémentée » — tant pour la souscription à un
service, avec le lien de définition envoyé une fois le paiement validé, que pour le
volet administrateur, avec les rôles et l'allocation de dossiers. Avec une référence
explicite au fonctionnement d'Odoo, adapté au contexte camerounais.

L'ordre s'est imposé de lui-même : brancher des écrans sans savoir **qui demande**
reviendrait à les construire deux fois. Le contexte K vient donc avant le front.

### La décision de départ : porter, pas greffer

Le dépôt contient `mail+paiement/`, deux applications Django extraites d'un projet en
production. Le module de paiement est solide — `idempotency_key` envoyée à Tara comme
`productId`, webhook atomique et rejouable, matching à trois stratégies, cron de
réconciliation, timeout à 24 h. Ce sont exactement les garanties qui empêchent le
double-encaissement, et elles ont été durcies en prod.

Mais elles sont en Django, et l'ERP est en FastAPI. Deux options :

* **garder Django à côté** — rien à réécrire, mais deux backends, deux bases, deux
  authentifications à réconcilier, et le lien entre un paiement et un dossier qui
  traverse le réseau ;
* **porter le cœur** — reprendre l'algorithme à l'identique derrière nos ports,
  remplacer le modèle Django et l'admin par nos dépôts.

Le choix est le second. Ce qui a de la valeur dans ce module n'est pas son ORM, c'est sa
mécanique anti-compensation, et elle est indépendante du framework. Le port
`ServiceNotification` a d'ailleurs été **dessiné sur la signature de `send_template`** —
un code de gabarit, un destinataire, un contexte — pour que le branchement du courriel
soit une substitution d'adaptateur et non une réécriture des appelants.

### Ce qui est livré

Le contexte **K · Transverse**, quatorze routes, cinq dépôts, 119 tests. Le total passe
à **634**.

**L'identité.** Un `Compte` qui ne porte ni rôle, ni mot de passe. Le rôle est une
habilitation datée ; le mot de passe est une empreinte opaque, dérivée par un service que
le domaine ne connaît pas. Un troisième état existe, et c'est le plus utile :
`EN_ATTENTE_ACTIVATION` — créé, lien parti, mot de passe jamais défini. C'est l'état le
plus fréquent en production, et celui qu'on oublie de traiter dans les écrans.

**L'habilitation datée.** C'est le cœur du lot, et le raisonnement mérite d'être écrit :

> La question qu'un contrôle pose n'est jamais « qui est comptable ? » mais **« qui était
> habilité le 12 mars, jour où cette déclaration a été déposée ? »**. Un rôle stocké en
> colonne ne sait répondre qu'à la première. Le jour où un réviseur quitte le cabinet et
> qu'on supprime son rôle, toutes les déclarations qu'il a déposées apparaîtraient
> rétroactivement comme déposées par quelqu'un qui n'y était pas habilité. Le cabinet
> aurait fabriqué lui-même la preuve de son propre manquement.

On ne supprime donc jamais une habilitation : on la ferme. Le port n'offre pas de
méthode `retirer`, et c'est délibéré.

**Le cloisonnement par portefeuille.** Une habilitation porte une portée — une liste de
NIU, ou `null` pour l'ensemble du cabinet. Deux comptables du jeu de démonstration
détiennent **exactement les mêmes permissions** et ne voient pas les mêmes dossiers ; le
test le montre en deux lectures.

Deux rôles ne peuvent jamais obtenir la portée universelle : l'adhérent et l'inspecteur.
Un adhérent dont la portée serait `null` lirait la comptabilité de ses concurrents —
c'est la faute la plus coûteuse que ce contexte puisse laisser passer, et elle est
refusée à la construction plutôt que vérifiée à la lecture.

**Les sessions côté serveur.** Le réflexe courant est de tout mettre dans un jeton signé
et de ne rien garder. C'est séduisant, et cela rend la révocation impossible. Or un
collaborateur qui part le matin doit perdre son accès le matin, pas ce soir. Le coût est
une lecture par requête ; le bénéfice est qu'un administrateur peut réellement fermer une
porte, et un test le démontre : suspendre un compte coupe la session déjà ouverte.

**Les liens à usage unique.** Activation après souscription, réinitialisation,
invitation. Le secret n'existe en clair qu'une fois, le temps d'entrer dans le courriel ;
ce qui est conservé est son SHA-256. **Une copie de la base ne doit donner accès à aucun
compte.**

Trois durées, parce que trois risques : sept jours pour l'activation — celui qui la
reçoit vient de payer et n'ouvrira peut-être pas sa boîte avant le week-end —, deux
heures pour la réinitialisation, qui permet de prendre un compte déjà actif, quatorze
jours pour l'invitation d'un collaborateur, émise avant sa prise de poste.

**Le journal d'audit chaîné.** Chaque entrée porte l'empreinte de la précédente. Modifier
une entrée ancienne invalide toutes les suivantes. Append-only : ni `modifier`, ni
`supprimer`, y compris pour un administrateur — une correction s'écrit comme une nouvelle
entrée, exactement comme une contre-passation comptable.

### Trois décisions qui méritent d'être défendues

**L'administrateur n'est pas tout-puissant.** Il crée les comptes, distribue les rôles,
affecte les dossiers, lit le journal. Il ne valide **aucune** écriture, ne dépose
**aucune** déclaration, n'écarte **aucun** constat. C'est la séparation des tâches : la
personne qui peut s'octroyer un droit ne doit pas être celle qui l'exerce. Un
administrateur qui voudrait valider devrait d'abord s'attribuer le rôle de comptable — et
cette attribution laisse une trace datée. Le contournement reste possible ; ce qui compte,
c'est qu'il soit **visible**.

**Une seule réponse pour tous les échecs de connexion.** Compte inconnu, mot de passe
faux, compte suspendu, jamais activé, verrouillé : le même message. Distinguer les cas
offrirait un oracle d'énumération — on essaie une liste d'adresses, on note ce qui répond
différemment, et l'on obtient la liste des adhérents du cabinet. Chez un CGA, cette liste
a une valeur commerciale propre. Le temps de réponse est égalisé lui aussi : une
dérivation est exécutée même quand le compte n'existe pas, contre une empreinte leurre.
`POST /mot-de-passe/oubli` rend **202 dans tous les cas**.

**Douze caractères, aucune règle de composition.** Exiger « une majuscule, un chiffre, un
caractère spécial » produit `Douala2026!` chez tout le monde : la majuscule est la
première lettre, le chiffre est l'année, le symbole est le point d'exclamation final. Le
résultat est un mot de passe de onze caractères que n'importe quel dictionnaire de
mutations casse, et que son porteur note sur un papier. `chemise bleue mardi tarif` fait
vingt-cinq caractères, se retient, ne se note pas, et résiste incomparablement mieux.

Ce qui est refusé, en revanche : les mots de passe contenant le nom, le prénom ou
l'adresse de leur porteur — accents retirés pour empêcher le contournement.

### Deux détails qui décident de la moitié des appels au support

**On valide le mot de passe avant de consommer le lien.** Une faute de frappe ne doit pas
détruire un lien à usage unique et obliger l'adhérent à téléphoner au cabinet.

**Le verrou est une date, pas un drapeau.** Cinq échecs verrouillent quinze minutes. Un
booléen exigerait une tâche de fond pour le lever, et le compte resterait bloqué si cette
tâche tombait. Une date se périme toute seule.

### Ce que les tests ont corrigé

Deux échecs, et tous deux disaient quelque chose de juste.

**Une habilitation qui commence le 1er septembre ne donne rien le 15 août.** Le test
attendait l'accès immédiat ; le code avait raison. La propriété a gagné son propre test :
un contrat signé pour septembre n'ouvre pas les dossiers en août.

**La description d'une route contredisait la table des permissions.** Elle affirmait que
`AFFECTER_DOSSIER` appartenait à la direction seule ; la table la donne aussi à
l'administration. La table a raison — la direction décide de la répartition,
l'administration l'exécute. Ce qui compte est que ni le comptable ni le réviseur ne
l'aient : quelqu'un qui pourrait s'ajouter un dossier n'aurait plus de périmètre du tout.
C'est la documentation qui a été corrigée, et deux tests couvrent désormais les deux
versants.

### Ce qui est bloqué, et le reste visible

**Le second facteur n'existe pas.** `EXIGE_MFA` le déclare pour le dépôt d'une
déclaration ; aucune session n'est renforcée ; l'action est donc **refusée**. Un défaut
qui bloque vaut mieux qu'un défaut qui laisse passer : le premier se constate le jour où
l'on en a besoin, le second se découvre après le dépôt.

**Le chaînage ne protège pas de tout.** Quelqu'un qui contrôle la base et le code peut
recalculer la chaîne entière après avoir modifié une entrée. Il faudrait ancrer
périodiquement l'empreinte de tête sur un support que le cabinet ne contrôle pas. Ce n'est
pas fait, et c'est écrit dans le module plutôt que sous-entendu.

**L'atomicité du journal ne vaut que dans un processus.** Le verrou ordonne les fils d'une
même instance ; deux instances derrière un répartiteur écriraient deux entrées de même
rang. Seule une contrainte d'unicité en base le garantira. Le port l'exige, l'adaptateur
en mémoire ne le tient pas, et il le dit.

### Une contrainte d'architecture qui a de la valeur

K appartient au **socle** : lisible par les onze autres contextes, il n'en lit aucun. Il
ne peut donc pas importer le portefeuille, et un dossier y est désigné par son **NIU**,
une chaîne. K sait dire « ce compte a le droit d'ouvrir `M081234567890P` » ; il ne sait
pas ce que ce dossier contient.

Conséquence visible : les six NIU du jeu de démonstration sont recopiés dans K. Ce n'est
pas une duplication tolérée faute de mieux — c'est ce qui empêche le cycle. La cohérence
est garantie par un test, qui lui a le droit d'importer les deux.

### Le jeu de démonstration met en scène ce qu'il faut savoir traiter

Onze comptes, treize habilitations. Deux comptables aux portefeuilles disjoints. **Un
dossier orphelin** — la clinique n'est affectée à personne, et c'est ce que l'écran
d'administration doit remonter. **Une habilitation fermée** — un comptable parti le 30
avril, dont la ligne demeure : résoudre ses droits au 1er mars et au 1er juin donne deux
réponses. **Un adhérent jamais activé.** **Un inspecteur** en mission sur un seul dossier.

Le journal d'audit, lui, est rendu **vierge** : fabriquer un historique d'audit
produirait une chaîne de hachage qui n'atteste de rien.

### Ce qui vient ensuite

Le parcours de souscription — service, devis, paiement Tara, lien, accès —, qui appellera
`ouvrir_acces_adherent`. Cette fonction ne prend aucun `Acces` : elle est déclenchée par
le système à la validation d'un paiement, et ce qui la rend sûre est qu'elle n'a **aucun
degré de liberté** — le rôle est `ADHERENT`, la portée est le seul NIU souscrit, et rien
de tout cela n'est paramétrable. Une souscription ne peut pas fabriquer un réviseur.

Reste aussi à noter : les cinq services du cabinet et leurs prix vivent aujourd'hui dans
`messages/fr/vitrine.json`, en dur dans les traductions. Un tarif dans un fichier de
traduction est un tarif que le cabinet ne peut pas changer sans redéploiement, et qui n'a
aucune date d'effet. C'est le premier point à traiter au lot suivant.

---

## 15 août 2026 (suite 4) — Les adaptateurs, et ce que le premier branchement révèle

### Ce qui est livré

**Vingt-huit routes HTTP, huit dépôts, trois jeux de démonstration. 512 tests.**

Les quatre contextes récents — B, C, E, F — sont branchés : chacun a sa
persistance, ses données, et son API. Le backend expose désormais la chaîne
complète, du dossier jusqu'au montant à verser.

    /portefeuille/entreprises        qui est qui, à une date
    /collecte/pieces                 la boîte de réception
    /collecte/doublons               les arbitrages en attente
    /conformite/controler            le verdict
    /comptabilite/…/balance          la comptabilité
    /obligations/…/declaration-tva   la TVA du mois, rejets isolés

### La persistance est en mémoire, et ce n'est pas un pis-aller

La cible est PostgreSQL, et le dossier d'architecture la nomme depuis le premier
jour. Ces dépôts-ci ne sont pas la cible : ils **prouvent que les ports sont
utilisables** avant qu'un schéma de base ne les fige.

Un port qu'aucun adaptateur ne réalise est une hypothèse. Le réaliser une première
fois révèle immédiatement ce qui manque à l'interface. Écrire d'abord les tables
SQL, c'est découvrir ces manques après la migration, quand ils coûtent une
migration de plus.

Et ce qu'ils ne tiennent pas est écrit noir sur blanc. `DepotEcritures` exige une
numérotation continue **même en accès concurrent** : le dépôt en mémoire calcule le
maximum plus un, et deux appels simultanés rendraient le même numéro. Seule une
séquence de base de données le garantira. Un doublon de numérotation est aussi
grave qu'un trou, et c'est la première chose qu'un vérificateur contrôle.

### Trois défauts que seul le branchement pouvait révéler

**1 · La clé d'écriture n'est unique qu'à l'intérieur d'un dossier.**

`EcritureComptable` ne porte pas d'identifiant d'entreprise, et le port n'en prend
pas non plus. La conséquence n'était visible nulle part tant qu'un seul dossier
existait : `2026/AC/000042` désigne six écritures différentes sur six adhérents.

Le dépôt est donc ouvert **pour un dossier**, et les routes sont toutes préfixées
par le NIU. Le jour où les écritures partageront une table, il faudra une colonne
`entreprise` dans la clé primaire — ou dans l'entité et dans `cle`. La question est
posée maintenant plutôt qu'après la migration.

**2 · La patente est payable d'avance, et le modèle l'interdisait.**

`ObligationInstance` refusait toute échéance antérieure à la fin de sa période :
« on ne déclare pas une période avant qu'elle ne soit écoulée ». C'est vrai d'une
déclaration, et **faux d'une contribution payée d'avance**. La patente est due en
début d'année pour l'année en cours : c'est un droit d'exercer, pas la déclaration
d'un passé.

Le premier catalogue réel a fait tomber le modèle. Un champ `payable_d_avance`
distingue désormais les deux familles. Sans lui, l'un de ces deux défauts était
inévitable : soit l'échéancier refusait de produire la patente, soit il acceptait
des déclarations antidatées.

**3 · Les décisions du domaine ne franchissaient pas HTTP.**

Une `@property` d'un modèle Pydantic est calculée en mémoire et **absente du
JSON**. `depot_possible`, `total` d'une pénalité, `credit_a_reporter`, `solde` d'un
compte : rien de tout cela n'arrivait au front, qui aurait dû les recalculer.

Le jour où la règle change, le front et le back diraient alors deux choses
différentes sans que personne ne sache lequel a raison — c'est exactement le
travers que tout le reste du projet évite. Les propriétés qui portent une décision
métier sont donc passées en `@computed_field` : elles voyagent avec l'objet, et il
n'existe qu'une implémentation de la règle. Les autres restent de simples
propriétés.

### La divergence des régimes est corrigée

Le jeu de démonstration du frontend classait ETS TCHOUMBA & FILS et CABINET NGUEMA
CONSEIL au synthétique ; celui du backend mettait tous les destinataires au réel.
Deux portefeuilles différents, et l'écart se voyait là où il compte : une facture
reçue par un adhérent au synthétique n'ouvre **aucun** droit à déduction, et
`FAC-ACH-007` n'a alors rien à dire.

Le portefeuille du contexte B est désormais la source unique, et les factures s'y
alignent. **Un test le vérifie facture par facture** — c'est la même garde que
celle qui avait rattrapé le bug de `Regle.concerne()`.

Effet immédiatement visible : deux adhérents sur six ont des écritures d'achat à
**deux lignes** au lieu de trois, la TVA s'incorporant au coût. Même facture, même
fournisseur, deux écritures différentes — c'est la démonstration que le régime
commande la forme de l'écriture, et elle est maintenant dans les données.

### Les jeux de démonstration dérivent les uns des autres

Trente pièces, quatorze écritures, huit demandes. Aucun de ces jeux n'est écrit à
la main indépendamment des autres :

    portefeuille (B)  →  factures (D)  →  pièces (C)  →  écritures (E)

Les écritures sont construites **à partir des pièces**, en faisant tourner le vrai
moteur de conformité et la vraie imputation. L'arête `comptabilite → collecte`
existe pour cela et va dans le bon sens : la collecte n'a pas le droit de connaître
la comptabilité.

Conséquence : il n'y a aucune convention à maintenir en double. Une écriture porte
la clé que sa pièce annonce, parce qu'elle est construite à partir d'elle.

Cinq pièces restent en attente, pour deux raisons qu'il ne faut pas confondre :
quatre parce que le contrôle **interdit** la comptabilisation — NIU du fournisseur
absent ou radié —, une parce que ses lignes ne totalisent pas son hors-taxes et que
**l'imputation refuse de deviner**. Répartir l'écart produirait une écriture
équilibrée mais fausse. Le contrôle est moins sévère et la pièce n'avance pas
davantage : ce sont bien deux mécaniques distinctes.

### Une décision d'exposition à défendre

**Rien ne se lit sans date.** `a_la_date` est obligatoire partout où un statut est
rendu. Une route qui rendrait « le régime de l'entreprise » sans dire à quelle date
obligerait l'écran à supposer « aujourd'hui », et l'écran qui affiche une facture de
2022 afficherait le régime de 2026. C'est l'erreur que le contexte B a été bâti pour
rendre impossible : elle ne se voit pas, et elle fausse tout ce qui suit.

Corollaire assumé : `GET /portefeuille/entreprises` sans date répond **422**, et un
test le protège.

La seule exception est la fiche complète d'un dossier, qui rend **toutes** les
périodes. C'est l'écran où l'on répond à « depuis quand ? » et « pourquoi ? », et
ces deux questions n'ont de réponse que dans les motifs des périodes.

### Ce qui reste

- **PostgreSQL** : les huit dépôts en mémoire attendent leurs tables. Les ports ne
  bougeront pas ; c'est tout l'intérêt de les avoir réalisés d'abord.
- Le contexte **K · Transverse** : authentification et cloisonnement multi-tenant.
  Aujourd'hui la séparation est portée par l'instance de dépôt, ce qui suffit à un
  monolocataire et ne suffira pas au second.
- **H · Clôture**, toujours bloqué par le fiscaliste et non par la technique.
- Le service d'extraction réel derrière le port `ServiceExtraction`.

## 15 août 2026 (suite 3) — Le contexte C, et la chaîne prise par son commencement

### Ce qui est livré

**1 350 lignes, 58 tests. La suite passe de 397 à 455.**

Sept contextes sur douze portent maintenant du code : **A, B, C, D, E, F, L**.

Le parcours phare des maquettes — E03 boîte de réception → E02 rapport → E10
saisie — est complet de bout en bout. La facture n'apparaît plus par magie dans une
constante de démonstration : elle entre par le canal qu'un artisan de Bonabéri
emploiera réellement.

### Le contrôle qui rapporte le plus, et que personne n'écrit

**Le doublon.**

Un adhérent photographie sa facture et l'envoie par WhatsApp. Trois jours plus
tard, sans souvenir de l'avoir fait, il la redépose sur le portail. Deux pièces,
un seul achat — et **la TVA déduite deux fois**.

Ce contrôle est absent de presque tous les logiciels de gestion, pour une raison
qui mérite d'être comprise : le doublon **ne ressemble pas à une anomalie**. Les
deux pièces sont parfaitement conformes, chacune prise séparément. C'est leur
coexistence qui est fautive, et **aucune règle du contexte D ne peut la voir** — le
moteur de conformité contrôle *une* facture, jamais un ensemble.

Deux niveaux, et il ne faut pas les confondre :

| | Ce qui est comparé | Décision |
|---|---|---|
| **Certain** | empreinte SHA-256 identique | dépôt refusé |
| **Probable** | même émetteur, même numéro, même montant | accepté, **soumis à arbitrage** |

Le second est le cas fréquent, et c'est celui qui échappe à une comparaison
d'empreintes : deux photographies du même papier n'ont pas le même fichier. On
refuse donc uniquement sur la certitude mathématique — refuser à tort ferait perdre
une charge déductible le jour où un fournisseur réutilise ses numéros d'une année
sur l'autre, et personne ne s'en apercevrait puisque la pièce n'existerait jamais.

Les pièces **archivées restent dans le champ de la comparaison**. Une pièce archivée
a été traitée : c'est justement pour cela qu'un second exemplaire serait un doublon.
Les exclure serait la faute exacte que ce module doit empêcher — et c'est une faute
qu'on commet sans y penser, en filtrant « les pièces actives ».

### Une valeur lue par une machine n'est pas une valeur

Le score de confiance ne dit pas « ce montant est juste ». Il dit « j'ai bien lu ces
caractères-là ». Un moteur qui lit `1 500 000` avec 98 % de confiance sur une
facture portant `1 800 000` mal imprimé est très sûr de sa lecture, et il a tort.
**La confiance mesure la netteté de l'image, pas la véracité du document.**

D'où la règle du module : le score sert à trier le travail humain, jamais à le
supprimer. Et deux familles de champs, qui ne se traitent pas pareil :

- un **libellé** mal lu donne une écriture approximative — ça se corrige ;
- un **montant** ou un **NIU** mal lu donne une déclaration fausse. Le montant part
  dans la TVA du mois ; le NIU décide de la déductibilité elle-même.

Les seconds sont à validation humaine obligatoire **quel que soit le score, y
compris à 100 %**. Ce n'est pas de la défiance envers la technique : c'est que
l'erreur y est irrattrapable en aval, et qu'aucun gain de productivité ne vaut une
déclaration fausse signée par le Centre.

L'accès à la valeur passe par une propriété qui **lève** tant qu'elle n'est pas
retenue. Il n'existe aucun contournement, et c'est délibéré : un avertissement se
contourne par distraction, une exception non.

### Trois décisions de modélisation à défendre

**L'état « en anomalie » n'existe pas.** Le cycle décrit un *traitement*, jamais une
*qualité*. La qualité est dite par le rapport de D, daté et immuable. Les confondre
rendrait impossible le cas le plus banal du métier : une charge parfaitement
comptabilisée et fiscalement réintégrée. Elle est non conforme, et son traitement
est pourtant achevé.

**Le canal n'affecte pas la valeur probante.** Une facture envoyée par WhatsApp vaut
la même déposée sur le portail : ce qui fait foi, c'est le document, pas le tuyau.
Traiter WhatsApp comme un canal de seconde zone reviendrait à dégrader le seul canal
que beaucoup de TPE utiliseront réellement. Le canal ne sert qu'à savoir par où
relancer, et à mesurer d'où vient le retard.

**Deux dates, et elles ne disent pas la même chose.** `depose_le` est déclarée par
l'expéditeur, `recue_le` horodatée par le système. En mode hors ligne — une pièce
photographiée dans un atelier sans réseau, synchronisée neuf jours plus tard —
l'écart entre les deux est le délai de transmission. Une seule date les confondrait
et ferait disparaître la mesure la plus utile que le cabinet puisse produire sur un
adhérent.

### La phrase que le système ne dira jamais

**« Le dossier est complet. »**

Un logiciel ne peut pas le savoir. Il connaît les pièces reçues et les demandes
émises ; il ignore les factures que l'adhérent n'a mentionnées à personne. Un taux
de 100 % ne prouve qu'une chose : *tout ce qu'on savait attendre est arrivé*.

La distinction n'est pas de la prudence oratoire. Un comptable qui lit « dossier
complet » cesse de chercher, et c'est précisément là que la facture oubliée devient
un redressement. La propriété s'appelle donc `attentes_satisfaites`, et le libellé
affiché le dit en toutes lettres. Un test vérifie que le mot « complet » n'y figure
pas.

Ce qui décide d'un dépôt n'est d'ailleurs pas le taux : c'est l'absence de demande
**bloquante** ouverte. Dix demandes non bloquantes en souffrance pèsent sur la
qualité du dossier, pas sur la possibilité de déclarer.

### Pourquoi le contrôle part à la réception, et pas à la saisie

C'est l'arête `collecte → conformite`, et elle existe pour une raison de délai, non
d'architecture.

Une facture non conforme découverte au moment de la saisie — deux mois après sa
réception — ne se corrige presque jamais : le fournisseur a été payé, la relation
commerciale est passée à autre chose. La TVA est perdue. La même facture contrôlée
le jour de sa réception se corrige souvent : le fournisseur est encore en contact,
la facture rectificative coûte un appel téléphonique.

**Le seul moment où une facture est corrigeable, c'est tout de suite.** Toute la
valeur du contexte D dépend de ce que le contrôle arrive tôt.

La collecte ne retient du verdict que **la référence du rapport** — ni la sévérité,
ni l'enjeu, ni le nombre de constats. Dupliquer le verdict le ferait diverger dès la
première réévaluation, et c'est la copie périmée qui s'afficherait sur l'écran de la
boîte de réception.

### Le test qui tient tout

Le dernier test du fichier déroule le parcours entier sur la facture F-2026-0412 :

1. la pièce arrive par WhatsApp, deux jours après avoir été photographiée ;
2. l'OCR lit `2 530 000` avec 99 % de confiance — et se trompe d'un chiffre ;
3. l'identification est **refusée** : personne n'a retenu ce montant ;
4. le comptable corrige, la correction est tracée et nominative ;
5. le contrôle part aussitôt : enjeu **379 350 F**, correction à demander au
   fournisseur, comptabilisation autorisée ;
6. l'écriture est proposée, validée, la pièce rattachée à `2026/AC/000012` ;
7. trois jours plus tard le redépôt par le portail est **signalé** — fichier
   différent, facture identique, l'indice cite l'écriture déjà passée ;
8. et le même fichier, lui, n'entre même pas.

### Ce qui reste

- Les **adaptateurs** : persistance et exposition HTTP pour B, C, E et F. C'est
  désormais le chantier le plus rentable — quatre contextes attendent la même chose.
- **H · Clôture**, toujours bloqué par le fiscaliste et non par la technique.
- Le service d'extraction réel derrière le port `ServiceExtraction`.

## 15 août 2026 (suite 2) — Le contexte F, et la chaîne enfin fermée

### Ce qui est livré

**1 021 lignes, 36 tests. La suite passe de 361 à 397.**

F · Obligations était débloqué par B : il avait désormais tout ce qu'il lui faut
chez A (paramètres datés), B (rattachement, exercice, régime) et E (écritures).

### La règle qui commande tout le contexte

**Une date limite se calcule, elle ne se stocke pas.**

Elle dépend du type d'obligation, de la date de clôture et du centre de
rattachement. Le 15 mars n'est pas une constante : pour un exercice clos au
30 juin, l'échéance tombe en septembre. Et le dépôt est échelonné par centre —
`TypeObligation.decalage_par_centre` matérialise ce que la note du paramètre
`DSF_DELAI_JOURS_APRES_CLOTURE` réclamait déjà : « doit devenir un paramètre par
centre, pas une constante ».

Stocker des dates figées est la faute la plus courante d'un module d'échéancier.
Elle ne se voit pas tant que tous les adhérents clôturent au 31 décembre, et elle
se révèle au premier exercice décalé — c'est-à-dire au pire moment.

### Trois décisions de modélisation à défendre

**« En retard » n'est pas un statut stocké.** Le dossier de conception en listait
six ; il en reste cinq. Le retard est une comparaison entre une échéance et une
date, pas une propriété de l'obligation. Le stocker obligerait à balayer le
portefeuille chaque nuit, et une obligation deviendrait « en retard » avec un jour
de décalage selon l'heure du traitement.

**L'échéancier se génère depuis le profil, jamais depuis les pièces reçues.** Une
déclaration néant est due même sans opération : l'obligation naît de
l'assujettissement, pas de l'activité. Un échéancier alimenté par les factures
serait structurellement faux — et il le serait précisément pour les dossiers
dormants, ceux dont personne ne s'occupe et qui accumulent les pénalités en silence.

**Le profil est réévalué à la fin de chaque période, pas une fois pour toutes.**
C'est ce qui rend le franchissement de seuil correct : une entreprise assujettie
à partir de septembre a quatre déclarations de TVA sur l'exercice, pas douze et
pas zéro. Évaluer le régime une seule fois produirait dans un cas huit
déclarations fantômes, dans l'autre quatre obligations manquées.

### Le troisième maillon est posé

`etablir_declaration_tva` isole la ligne **« TVA rejetée par le contrôle de
conformité »**. C'est la ligne L24 de la maquette du parcours comptable, celle qui
avait imposé l'arête `obligations → conformite` lors de l'audit du 9 août.

Le rejet n'est pas recalculé : il est **lu** sur les attributs fiscaux que E a
posés à partir des constats de D. Ce module ne connaît aucune règle de
déductibilité, et c'est ce qui garantit que la déclaration dit exactement la même
chose que le rapport de conformité.

Le test final déroule la chaîne entière sur juillet 2026 :

| | |
|---|---|
| TVA collectée | 1 000 000 |
| TVA déductible théorique | 879 850 |
| **dont rejetée par la conformité** | **(379 350)** |
| TVA déductible admise | 500 500 |
| **Solde à verser au Trésor** | **499 500** |

Et chaque rejet est justifié pièce par pièce, avec le code de la règle et le motif
en clair. Dans une déclaration ordinaire, une TVA rejetée est **invisible** : la
case « TVA déductible » porte simplement un chiffre plus faible, et rien n'explique
pourquoi. C'est exactement l'argument commercial du cabinet.

### Une imprécision relevée dans le référentiel

Le calcul a fait apparaître un écart d'un jour. Le paramètre
`DSF_DELAI_JOURS_APRES_CLOTURE` vaut 75 et sa note dit : « 15 mars pour un
exercice clos au 31 décembre, soit 75 jours après clôture ».

Or 31 décembre + 75 jours donne le **16 mars**. Le 15 mars correspond à 74 jours.

Trois lectures possibles, et elles ne se valent pas :

1. le délai est de 74 jours, et la note contient une coquille ;
2. le décompte commence le lendemain de la clôture, ce qui décale d'un jour ;
3. **le 15 mars est une date civile fixe**, et la formule « clôture + N jours » ne
   vaut que pour les exercices décalés.

La troisième hypothèse changerait le modèle : il faudrait une périodicité
supplémentaire, ou une règle mixte. **À faire trancher par le fiscaliste** — c'est
ajouté aux questions ouvertes.

### Question ouverte sur les pénalités

Le décompte des mois de retard — mois calendaires ou périodes de trente jours,
fraction comptée ou non — n'est pas au référentiel. Le traitement retenu est le
plus défavorable au contribuable, donc le plus prudent pour le Centre : mieux vaut
annoncer une pénalité légèrement surestimée qu'une surprise au paiement. À
confirmer.

### État du backend

Six contextes sur douze portent du code : **A, B, D, E, F, L**. La chaîne de valeur
du produit est complète de bout en bout, du contrôle de la facture jusqu'au montant
à verser :

    facture → constat → attribut fiscal sur la ligne → TVA du mois

Il manque le dernier maillon — la réintégration au tableau de passage — qui
appartient à H · Clôture, lequel dépend des six questions fiscales encore ouvertes.

### Ce qui reste

- Les **adaptateurs** : persistance et exposition HTTP pour B, E et F.
- Le contexte **C · Collecte**, seul manquant du parcours E03 → E02 → E10.
- **H · Clôture**, bloqué par le fiscaliste, pas par la technique.

## 15 août 2026 (suite) — Le contexte B, et le patron du statut daté

### Pourquoi B après E

E · Comptabilité pouvait s'écrire sans le fiscaliste ; B · Portefeuille aussi, et
il était le **dernier prérequis avant F · Obligations**. Presque tous les contextes
le lisent : D pour la portée des règles, E pour l'assujettissement, F pour le
rattachement et l'exercice, H pour l'adhésion. C'est une feuille du graphe — il ne
dépend d'aucun contexte métier — et c'est justement ce qui en fait le goulot.

**1 200 lignes, 40 tests. La suite passe de 321 à 361.**

### Le patron : le statut daté

C'est la décision structurante, et elle est la même que celle du référentiel
normatif : **une donnée légale est une fonction du temps, pas une constante.**

Une entreprise n'*est* pas au régime du réel. Elle y est **depuis une date**, pour
un motif, et elle peut en sortir. Modéliser le régime comme une colonne est une
erreur qui ne se voit pas la première année et devient irréparable la troisième :
le jour où l'on contrôle une facture de 2024 pour une entreprise passée au réel en
2025, le rapport est faux — et faux **en silence**.

`Periode` porte l'intervalle `[debut, fin[`, borne haute exclue comme au
référentiel. `verifier_succession` distingue deux régimes de continuité, et la
distinction compte :

* régime et rattachement sont **continus** — une entreprise en relève à chaque
  instant de son existence, un trou est une erreur ;
* l'adhésion admet des **trous** — un adhérent peut partir et revenir, et boucher
  le vide lui accorderait rétroactivement des avantages qu'il n'avait pas.

Il n'existe aucune méthode `regime_courant()` publique. On lit `regime_au(date)`,
ou l'on ne lit rien. Un statut introuvable lève `StatutIntrouvable` plutôt que de
supposer le réel : c'est la même discipline qu'`AucuneVersionApplicable`.

### L'exercice, sans présomption

Ni année civile, ni douze mois. Les deux cas que le dossier de vision cite parmi
les huit pièges sont modélisés : l'**exercice décalé** — la DSF n'est alors pas due
le 15 mars mais soixante-quinze jours après *sa* clôture — et le **premier exercice
long**, quinze mois pour une entreprise créée en octobre.

`prorata()` rapporte à la durée **réelle**, jamais à 365 jours. Sur un premier
exercice de quinze mois, l'écart est de 25 %.

### Le franchissement de seuil, annoncé avant

C'est le scénario qui coûte le plus cher aux entreprises qui réussissent, et il les
prend toujours par surprise : passées au réel en septembre, elles continuent de
facturer sans TVA jusqu'en décembre, et l'administration la réclame ensuite « en
dedans » sur un prix qu'elles ont déjà encaissé.

`diagnostiquer_seuil` porte donc un **palier d'alerte anticipée** à 80 %. Ce n'est
pas une valeur légale mais un réglage de vigilance, qui appartient au cabinet : à
80 %, il reste en général un trimestre pour s'organiser. Alerter au franchissement
lui-même serait déjà trop tard.

Aucun seuil n'est connu du module : il les reçoit, résolus au référentiel à la date
demandée.

### La période probatoire

`retour_au_synthetique_admis` compte les exercices **entièrement écoulés et clos**
depuis le début de la période au réel. Un exercice à cheval sur la bascule ne
compte pas — le retenir abrégerait la période d'un exercice complet.

> **Question ouverte.** La période probatoire s'applique-t-elle de la même façon à
> un reclassement *subi* et à une option *volontaire* pour le réel ? Le décompte
> est ici le même dans les deux cas, ce qui est le traitement le plus prudent.
> À faire confirmer.

### Les identifiants, contrôlés contre le référentiel daté

Le format du NIU et celui du RCCM sont des valeurs légales datées. Une entité du
domaine ne peut donc pas les vérifier : elle n'a le droit d'importer que les
*contrats* d'un autre contexte, jamais son service. La vérification vit dans la
couche cas d'usage, qui reçoit `ServiceParametres`.

Elle **rend des anomalies plutôt que de lever** : un portefeuille repris d'un autre
cabinet contient toujours des identifiants douteux, et il faut pouvoir les lister
pour les corriger, pas refuser de charger le dossier. Même logique que
`RegleEnEchec` dans le moteur de conformité.

### Une duplication délibérée, qui mérite d'être défendue

`RegimeFiscal` (contexte B) et `RegimeEmetteur` (contexte D) sont deux énumérations
distinctes portant les mêmes valeurs. **C'est voulu.** Chaque contexte borné garde
son vocabulaire, et la correspondance se fait à la composition. Les fusionner
créerait une dépendance de D vers B qui n'a aucune raison d'être : le moteur de
conformité évalue une règle sur une facture, il n'a pas besoin de connaître le
portefeuille.

C'est le genre de point qu'un architecte relèvera en revue. La réponse est
documentée à l'endroit où il regardera.

### La composition B → D → E, démontrée

Trois tests prennent la **même facture** — même fournisseur, même montant, réglée en
espèces — et la font passer par les trois contextes à deux dates différentes du
dossier BATIMENT PLUS :

| | Juin 2022, au synthétique | Janvier 2024, au réel |
|---|---|---|
| Régime lu chez B | IGS | RÉEL |
| `FAC-ACH-007` chez D | hors portée | déclenchée |
| Enjeu | 0 | 379 350 FCFA |
| Écriture proposée par E | `604` · `401` | `604` · `4451` · `401` |
| Première ligne | 2 350 000 (TVA incorporée) | 1 970 650 |

Les trois contextes ne se connaissent pas. C'est la couche de composition qui lit
le régime chez B et le transmet — et le résultat change du tout au tout.

### Le cloisonnement multi-tenant n'apparaît pas dans le port

`DepotEntreprises` n'a aucun paramètre `tenant`. Le filtrage est appliqué **dans la
couche de persistance**, systématiquement. Le faire remonter jusqu'à l'interface
donnerait l'illusion d'une sécurité tout en la rendant contournable : il suffirait
d'oublier l'argument une fois.

### Ce qui reste

- Les **adaptateurs** de B et de E : persistance, exposition HTTP.
- Le contexte **F · Obligations**, désormais débloqué — il a tout ce qu'il lui faut
  chez A, B et E.
- La nomenclature exacte des régimes, qui reste la question n° 12.

## 15 août 2026 — Un manuel pour tenir la conversation, puis le contexte E

### Ce qui a été demandé

Deux choses, dans cet ordre. D'abord un document de référence permettant de
comprendre les rouages de la comptabilité et de la fiscalité camerounaises sans
être du métier, et de **défendre la solution devant des experts du domaine**.
Ensuite, reprendre la conception pendant la lecture.

### Le manuel — `Docs/manuel/`

92 pages, six parties, neuf exercices corrigés, six scénarios déroulés jusqu'au
dépôt de la DSF.

**Le parti pris qui commande tout.** Chaque affirmation est marquée selon quatre
niveaux : *mécanisme* — structurel, affirmable sans réserve —, *valeur du
référentiel* — présente mais au statut `A_VALIDER` —, *inconnue* — absente, à
obtenir du fiscaliste — et *piège*.

Aucun taux camerounais n'est avancé comme une vérité. C'est la seule posture
tenable face à un expert-comptable qui exerce depuis vingt ans : vouloir rivaliser
sur les valeurs, c'est perdre sa crédibilité au premier chiffre périmé par une loi
de finances. En revanche, la question « que se passe-t-il dans votre outil quand le
seuil change en janvier ? » est notre terrain, et la réponse retourne une réunion.

La contrepartie de cette honnêteté est une **liste de 28 questions ouvertes**,
classées non par thème mais par ce que chaque réponse débloque. Six d'entre elles
empêchent tout calcul d'impôt juste. Deux étaient inconnues du référentiel :
le **minimum de perception** — qui peut annuler l'abattement CGA — et le taux d'IS.

### Le contexte E · Comptabilité

Choisi parce qu'il est le **seul module qui ne dépend d'aucune des 28 questions**.
Les taux, les seuils, l'abattement : rien de cela n'entre dans une écriture. E
pouvait s'écrire sans attendre le fiscaliste, et il débloque F et H, qui ne
peuvent rien calculer sans écritures.

**1 460 lignes, 82 tests. La suite passe de 237 à 321.**

Quatre invariants portés par le modèle, non par une note :

* équilibre **au niveau de l'écriture**, jamais de la ligne ;
* numérotation continue par journal et par exercice, avec détection des trous ;
* immuabilité après validation — le port de dépôt n'a **pas** de méthode
  `supprimer`, et il n'existe pas d'état « annulée » ;
* une écriture validée porte sa pièce et le nom de qui l'a validée, comme une
  version de paramètre au référentiel : valider engage une personne.

**La balance et le grand livre sont des projections, pas des entités.** Les
persister créerait une seconde vérité, qui divergerait au premier incident. Une
comptabilité n'a qu'une source : le journal.

**La soudure D → E.** `appliquer_rapport()` prend un rapport de conformité produit
par le vrai moteur et pose les attributs fiscaux sur les lignes concernées. C'est
le maillon qui manquait : le moteur produisait des constats que personne ne
consommait. Éprouvé de bout en bout sur `F-2026-0412` — 379 350 FCFA de TVA
rejetée, le chiffre exact du bandeau de verdict, obtenu par un chemin entièrement
différent.

**L'imputation.** `proposer_ecriture_achat()` construit l'écriture depuis une
facture contrôlée, en brouillon, déjà qualifiée. Le comptable garde la main : le
système impute, il n'enregistre pas.

### Une erreur trouvée en écrivant les tests

`controle_bouclage` calculait `situation + résultat == 0`. C'est faux : l'identité
est `situation == résultat`, puisque l'actif n'égale le passif qu'une fois le
résultat reporté. Corrigé, avec la démonstration dans la docstring.

C'est exactement pourquoi le jeu de test est un exercice minuscule mais **dont les
totaux tombent juste** — un jeu dont la balance ne s'équilibre pas ne prouve rien.

### La correction du contexte D — deux régimes, pas un

En déroulant le cas d'un adhérent au régime synthétique, un défaut réel est apparu.
`Regle.concerne()` filtrait sur le régime de l'**émetteur**, c'est-à-dire du
fournisseur. Or la déductibilité dépend du régime du **destinataire** : l'adhérent
lui-même.

Conséquence : `FAC-ACH-007` annonçait à un adhérent au synthétique une « TVA non
déductible » de plusieurs centaines de milliers de francs — **un préjudice qui
n'existe pas**, puisqu'il ne récupère jamais la TVA, en espèces comme par virement.

`Portee` porte désormais `regimes_destinataire`, et `FAC-ACH-007` est limitée au
régime du réel. Le gabarit de facture de `test_regles.py` déclarait un destinataire
au régime `INCONNU` : il a été corrigé, ce qui est de toute façon plus réaliste.

> **Question laissée ouverte.** `FAC-ID-003` n'a **pas** été restreinte. Sa
> conséquence fiscale est nulle au synthétique, mais le constat garde une valeur au
> titre de l'obligation de sincérité. Maintenir sans enjeu chiffré, ou écarter ?
> À trancher avec le cabinet.

### Deux points de variation laissés ouverts, délibérément

Le code **ne décide pas** quel compte reçoit une TVA devenue non récupérable —
charge d'origine ou compte dédié. C'est une décision d'imputation du cabinet, et
elle commande une question fiscale non tranchée : cette TVA passée en charge
est-elle elle-même déductible du résultat ? Le choix est exposé dans
`PlanImputation`, pas figé dans le code.

De même, l'inventaire permanent ou intermittent n'est pas arbitré : il changerait
les écritures d'achat elles-mêmes.

### Divergence relevée entre les deux jeux de démonstration

`donnees-demo.ts` classe TCHOUMBA et Cabinet Nguema à l'IGS ; `donnees_demo.py`
construit **tous** les destinataires au régime du réel, en dur. Sans conséquence
tant que la portée ignorait le destinataire ; visible désormais. À reprendre.

### Ce qui reste

- Les **adaptateurs** de E : persistance des écritures, exposition HTTP de la
  balance et du grand livre.
- Le **plan comptable OHADA** à importer au référentiel, préalable à
  `balance_par_racine` en conditions réelles.
- Le contexte **B · Portefeuille**, dont E lit l'exercice et le régime.
- Le `.venv` du dépôt est un venv **Windows**, inutilisable sous Linux.
  `pydantic-settings` et `fastapi` ont été installés dans le Python courant pour
  faire tourner la suite ; un venv propre reste à recréer.

## 14 août 2026 (suite) — Le front et le back prennent chacun leur dépôt

### Ce qui a été demandé

Pousser `Frontend_erp_cga` dans `horus-lab-team-s/Frontend-erp_cga` et
`Backend_erp_cga` dans `horus-lab-team-s/Backend-erp_cga`, deux dépôts vides.

### Deux décisions avant d'agir

**L'historique est conservé.** Les commandes de création fournies par GitHub
proposent un `git init` et un « first commit » : les deux dépôts seraient partis
avec un seul commit et aucun passé. `git filter-repo` extrait chaque sous-dossier
avec les commits qui l'ont touché — douze pour le front, sept pour le back — et
réécrit les chemins à la racine. `git blame` reste utilisable. Un historique ne se
reconstitue jamais après coup, et le nôtre porte le détail des décisions.

**Le backend emporte ce dont il dépend.** `config.py` désignait trois dossiers
situés au-dessus de `Backend_erp_cga/`. Poussé seul, il n'aurait pas démarré.
Sont donc partis avec lui `Contenu_vitrine/` — la matière du blog —,
`Docs/referentiel/` — les paramètres légaux — et `Docs/architecture/`, cité par
les docstrings de presque tous les contextes. `RACINE_DEPOT` remonte désormais de
deux niveaux et non plus de trois.

Le reste de `Docs/` — cahiers des charges, maquettes, ce journal — demeure au
monorepo : il ne se rattache ni au front ni au back.

### Le test qui regardait par-dessus la clôture

Un test vérifie que chaque article trouve son illustration. L'image est servie par
le front, désormais ailleurs. Le supprimer aurait été le plus simple et le plus
coûteux : c'est lui qui garantit qu'un lien partagé sur Facebook porte sa vignette.

Il cherche donc `../Frontend-erp_cga/public`, obéit à
`CGA_DOSSIER_PUBLIC_FRONTEND`, et se déclare **sauté** s'il ne trouve rien. Sauté,
pas réussi : un test qui passe faute d'avoir rien trouvé ment sur ce qu'il protège.

### Ce qui manquait au front pour tenir seul

Un lockfile — celui du monorepo était au format workspace et ne s'appliquait pas à
un paquet isolé. Un `.env.example`, parce que sans backend le blog retombe sur sa
copie de secours **sans que rien ne le dise à l'écran**. Un README qui prévient que
le texte des articles n'est pas dans ce dépôt. Et son propre
`pnpm-workspace.yaml`, pour la raison ci-dessous.

### Une trouvaille en chemin

`C:\Users\tonba\pnpm-workspace.yaml` existe, daté du 28 juillet, et contient des
valeurs jamais renseignées (« set this to true or false ») — le résidu d'un
`pnpm approve-builds` interrompu. pnpm remonte les dossiers parents jusqu'au
premier fichier de workspace : **tout projet pnpm placé sous le répertoire
personnel et dépourvu du sien est capturé par celui-là**, et son `pnpm install`
n'écrit alors ni `node_modules` ni lockfile. Le monorepo y échappe grâce au sien.
Le fichier n'a pas été supprimé — il est hors du projet, la décision revient au
propriétaire du poste.

### Vérifications

Backend : `ruff` au vert, 237 tests quand les deux dépôts sont côte à côte,
236 plus un sauté quand il est seul. Front : `tsc` et `eslint` sans un
avertissement, build complet à 58 pages, installé depuis son seul lockfile.

Le monorepo n'a pas été touché : tout le travail a eu lieu sur des clones jetables,
`git filter-repo` réécrivant l'historique en place.

### Ce qui reste

Les deux extraits ne se mettront **pas** à jour tout seuls. Une modification du
monorepo demande de rejouer l'extraction. Décider, quand le moment viendra, lequel
des trois porte la vérité — vivre longtemps avec les trois est le meilleur moyen
de les voir diverger.

---

## 14 août 2026 — Le lot part sur le dépôt personnel

### Ce qui a été demandé

Pousser le projet sur `github.com/LoicTonba/erp_cga_brcg`, sur une branche
destinée à être fusionnée.

### Ce qui a été fait

Le dépôt de travail est `horus-lab-team-s/erp_cga_brcg`. Le dépôt personnel a
été ajouté comme second remote sous le nom `loic` plutôt que de détourner
`origin` : deux destinations différentes doivent porter deux noms différents,
sinon un `git push` distrait envoie le travail au mauvais endroit.

Son `main` est le résultat de la fusion de la demande de tirage n° 1 et porte
exactement l'arbre de `819e5a3`, qui est un ancêtre direct de la branche
courante. La fusion se fera donc sans conflit et sans historique étranger — la
branche poussée n'apporte que les deux commits qui manquent : le passage du
contenu au backend avec le blog, et la revue de design.

### Ce qui reste hors du dépôt, et pourquoi

Trois éléments étaient présents dans le répertoire de travail sans être suivis.
Ils sont désormais nommés dans `.gitignore`, pour que leur exclusion soit une
décision écrite et non un oubli reconduit à chaque commit.

- **`Docs/publications-facebook-blog/`** — 74 Mo de captures d'écran. C'est la
  matière première des articles, pas le produit. Git ne sait pas oublier un
  binaire : une fois entré dans l'historique, il pèse sur chaque clone à venir,
  y compris ceux qui n'ont que faire des captures.
- **`mail+paiement/` et `mail+paiement.zip`** — modules Django d'envoi de
  courriels et d'encaissement mobile money, extraits d'un autre projet en vue
  d'une greffe future. Ils ne sont branchés à rien ici, et le dossier traîne ses
  `__pycache__`. Ils entreront au dépôt quand ils seront intégrés, adaptés au
  backend FastAPI, et non avant — voir le rappel Taramoney plus bas dans ce
  journal.

### Vérifications avant envoi

`tsc` sans erreur, `eslint` sans avertissement, 237 tests backend au vert.

---

## 13 août 2026 — Revue de design, page par page

### Ce qui a été demandé, et ce qui a été fait

Une revue complète du rendu, après parcours du site. Point par point.

**Les bannières.** Contenu centré, sur l'accueil comme sur les pages
intérieures. Sur l'accueil, le texte est centré dans la place que lui laisse le
formulaire, qui garde sa colonne — le centrer sur la largeur entière l'aurait
fait passer dessous. Le chapeau passe en `text-wrap: balance` : sur un texte
centré, ce qui se voit d'abord est l'inégalité des lignes.

**Deux boutons magenta dans la même bannière.** C'était le cas sur l'accueil —
l'action du carrousel et l'envoi du formulaire — et sur la connexion. Deux
boutons de la couleur primaire ne hiérarchisent plus rien : l'œil ne sait plus
lequel est l'action principale. Nouvelle variante `bouton--inverse`, blanc plein,
pour la seconde action forte d'un écran sombre. Elle garde le même poids visuel
sans disputer la couleur de marque.

**Les cartes de service.** L'icône était accrochée en bas à gauche de la
photographie, où elle passait pour une vignette de coin. Elle est désormais
ronde, centrée en tête, et **logée dans une échancrure** du corps de la carte.
L'entaille est faite au masque plutôt qu'à la bordure : elle découpe réellement
le fond, si bien que la photographie transparaît dans l'arc — une bordure de la
couleur du fond aurait donné un anneau plat, pas un creux.

**Le prix.** En simple ligne de texte au bas de la carte, il se lisait comme une
mention légale et se perdait à côté du lien d'action. Il est passé dans sa propre
pastille cerclée, qui s'inverse au survol. C'est l'information que le visiteur
cherche en premier ; elle devait se voir en premier.

**Le ruban des témoignages** passe de 11 à 18 secondes par carte. Régler les deux
bandes sur la même cadence était une erreur de raisonnement : un logo se
*reconnaît* d'un coup d'œil, un témoignage se *lit*. À vitesse égale, la seconde
bande passait avant qu'on ait fini la première phrase.

**« Parlons de votre projet ».** Tout sur l'axe central, et les boutons **sous**
le texte. Auparavant le texte était à gauche et les boutons à droite : sur un
écran large, un mètre séparait la phrase de l'action qu'elle appelait. Le
bandeau étant commun aux pages, la correction vaut partout d'un coup.

**La navigation reste à l'écran.** `fixed`, et non `sticky` : les deux gardent la
barre visible, mais `sticky` occupe sa place dans le flux et pousserait toute la
page de 126 px vers le bas — or les bannières compensent **déjà** un en-tête en
superposition. Le fond ne se teinte qu'une fois la page défilée : sur la
photographie, une barre opaque couperait l'image ; plus bas, du blanc sur fond
clair serait illisible.

**Flèche de retour en haut**, en bas à droite, au-delà d'un écran et demi de
défilement. Posée plus haut que le bandeau d'annonce pour ne pas recouvrir son
bouton de fermeture.

**La page de connexion reçoit l'en-tête et le pied.** Décision qui **renverse**
le choix initial. Elle vivait sans navigation, au motif qu'une page de connexion
offrant dix autres chemins détourne de la seule action attendue. Le raisonnement
valait pour la concentration, mais il coûtait plus cher ailleurs : dépouillée de
tout repère, la page donnait le sentiment d'avoir quitté le site pour un service
tiers — exactement l'inquiétude qu'on ne veut pas susciter au moment de saisir un
identifiant. Elle ne porte toujours ni bandeau d'appel, ni annonce : on ne
relance pas commercialement quelqu'un qui se connecte.

**La direction générale mise en avant** sur la page Le CGA, hors de la grille de
l'équipe — une carte identique à celles de ses collaborateurs l'aurait noyée
parmi eux. Portrait, fonction, présentation, et lien vers son site personnel.

**Les agences** reprennent le dispositif de l'échancrure, et leurs trois lignes
sont hiérarchisées : ville, quartier en capitales, précision. Elles se suivaient
auparavant au fer à gauche dans un même paragraphe, où l'adresse se confondait
avec la note.

**Contact** — la phrase « le téléphone reste le champ principal : beaucoup de nos
clients n'utilisent pas de messagerie électronique » est retirée. Le retrait est
juste : c'était une note de conception, pas un argument de vente, et lue par un
prospect elle donnait de la clientèle du cabinet une image peu flatteuse. Le
constat guide toujours la mise en page — le téléphone reste le champ exigé — mais
il n'est plus écrit.

### Seconde passe du 13 août — reprise de l'échancrure, et fin des impasses

**L'échancrure était au mauvais endroit.** Premier essai : l'icône logée à la
jonction entre la photographie et le texte, au milieu de la carte. Ce n'était pas
le dessin demandé. L'icône doit chevaucher **l'arête haute** de la carte — moitié
au-dessus, moitié dedans — et l'échancrure se creuser juste sous elle, dans le
bord supérieur.

Le point technique qui commande toute la structure : **un masque s'applique à
toute la descendance de l'élément masqué**. L'icône placée dans la carte aurait
donc été rognée par l'échancrure même qui doit l'accueillir, c'est-à-dire coupée
en deux. D'où une enveloppe qui n'est masquée par rien et porte les deux — la
carte échancrée d'un côté, l'icône de l'autre.

Trois mesures vont ensemble et ne se changent pas séparément : icône de 60 px,
échancrure de rayon 38, réserve haute de 30 px — exactement la moitié de l'icône.
Le soulèvement au survol a été retiré des cartes échancrées : la carte montait de
3 px pendant que l'icône restait en place, et le liseré devenait inégal.

**Quatre entrées du méga-menu menaient à la page Contact.** Prestations
ponctuelles, domiciliation, assistance juridique, conseil et audit : autant
d'impasses. Un visiteur qui clique sur « Domiciliation » veut savoir ce que
couvre la domiciliation, pas remplir un formulaire — on lui demandait de
s'engager avant de lui avoir dit ce qu'on vendait.

Chacune a désormais sa fiche, à `/services/<slug>`, sur un gabarit unique :
qu'est-ce que c'est, ce qui est compris, pour qui, comment ça se passe, combien.
Quatre pages écrites séparément auraient divergé au premier ajout ; le contenu
vit donc dans les messages et la mise en page une seule fois. L'ordre des
sections est l'argumentaire : ce qui est compris **avant** pour qui, et le tarif
en dernier — un montant lu avant ce qu'il couvre paraît toujours cher.

Les trois services qui ont déjà une page propre — création, adhésion, formations
— n'y passent pas.

**Deux chapeaux de bannière sur deux lignes** (Estimation, Blog). Le nombre de
lignes ne se décrète pas : on élargit la colonne de lecture et `text-wrap:
balance` répartit les deux lignes à longueur voisine. Sous 900 px la contrainte
tombe et le texte se replie sur ce qu'il faut — deux lignes sur un téléphone
donneraient des caractères minuscules.

⚠️ **Le contenu anglais des quatre fiches est encore en français.** Le gabarit et
l'interface sont bilingues, mais les textes n'ont pas été traduits : les faire
passer à la machine sur un contenu commercial aurait produit de l'anglais
approximatif au nom du cabinet. À faire traduire.

### 14 août 2026 — Le pied de page, et trois liens qui tombaient dans le vide

**Vérification demandée, et elle a trouvé quelque chose.** Le cabinet a demandé
de contrôler que les liens du pied mènent bien quelque part. Les vingt entrées
des trois colonnes fonctionnaient — les six formes juridiques vers l'estimateur
pré-rempli, les ancres du CGA, le blog, les formations. Mais les **trois liens de
la dernière ligne — mentions légales, confidentialité, conditions générales —
tombaient en 404 depuis le premier jour.** Ils étaient liés sans jamais avoir été
écrits.

C'est le genre de défaut qui passe inaperçu longtemps et se paie d'un coup : ce
sont précisément les pages qu'un visiteur méfiant va vérifier avant de confier
son numéro, et elles sont par ailleurs obligatoires.

Les trois pages existent maintenant, sur un gabarit commun. **Tout ce que le
dépôt sait de façon vérifiable y figure** — dénomination, agrément, boîte
postale, contacts — et **tout le reste est marqué « à compléter » en toutes
lettres** : numéro RCCM, capital social, hébergeur, responsable de publication
nommé, durées de conservation, clause de médiation. Rien n'a été inventé, et
c'est délibéré : une mention légale fausse est pire qu'une mention absente, parce
qu'elle engage le cabinet sur des informations qu'il n'a pas données et qu'elle
passe inaperçue précisément parce qu'elle a l'air complète.

**Le cabinet doit relire et compléter ces trois pages avant toute mise en ligne.**

Corrigé au passage : « Domiciliation » pointait encore vers la page Contact,
du temps où elle n'avait pas de fiche. Elle mène désormais à la sienne.

**Le panneau des services s'ajuste à son contenu.** Il gardait la largeur héritée
de l'ancien méga-menu à trois colonnes, alors qu'il ne porte plus qu'une liste de
sept intitulés : la moitié de sa surface était vide. `width: max-content` le fait
mesurer sa plus longue entrée, borné pour ne pas déborder de la fenêtre.

**Le pied de page, troisième allègement.** La bande « Suivez-nous » — encadrée de
deux filets, sur toute la largeur, pour trois logos et un numéro — a disparu ;
les logos ont rejoint la première colonne. Le téléphone fixe et le courriel en
sont retirés, pour la même raison que l'agrément la veille : la barre utilitaire
est désormais **fixe**, donc lisible à tout moment, y compris au bas d'une page
longue. Répéter une coordonnée qui ne quitte jamais l'écran n'apprend rien.

Sur téléphone, les colonnes passent à deux au lieu de quatre empilées, avec des
interlignes resserrés — un pied de page se parcourt du pouce, il ne se lit pas.
En dessous de 420 px, retour à une colonne, mais le pied est alors déjà bien plus
court qu'avant.

**La signature est centrée et cliquable**, vers `horus-lab.com`.

### Troisième passe du 13 août — direction artistique, et le passage à l'action

**Les boutons deviennent carrés et sans bordure.** Direction arrêtée par le
cabinet, dans la ligne de la pilule de navigation dont les angles avaient déjà
été redressés le 10 août. Les bordures partent avec les arrondis : elles
doublaient le fond des boutons pleins et faisaient bavocher les angles vifs. Une
seule exception, dictée par la lisibilité et non par le goût : `bouton--clair`
garde son contour, car sur une photographie un bouton clair sans contour se
dissout dans l'image.

**Le panneau des services est réduit à une liste.** Il portait sept fiches
détaillées, les six formes juridiques et un encart « Vous hésitez ? » à deux
boutons : la moitié de l'écran, pour redire ce que la page du service allait de
toute façon expliquer. Un menu conduit quelque part, il n'informe pas. Reste une
liste séparée d'un filet magenta, où l'on choisit et où l'on part. Les formes
juridiques ont disparu d'ici : la page Création les présente déjà toutes, et les
répéter revenait à tenir deux inventaires de la même chose.

**Le passage à l'action manquait.** C'est le vrai défaut que le cabinet a
relevé : les fiches expliquaient bien, puis renvoyaient vers une page Contact
générique où tout était à ressaisir — y compris le service qu'on venait de passer
trois minutes à lire. Un formulaire unique, `FormulaireService`, est désormais au
bas de chaque page, **pré-rempli sur ce que le visiteur regarde**.

Le sujet voyage dans l'adresse (`?service=…#demande`) plutôt que dans un état
client. Trois avantages : « Réserver une place » et « Demander mon bulletin »
restent de simples liens, les pages demeurent rendues par le serveur, et une
demande portant sur une session ou une formule précise se partage telle quelle.
Le service est **affiché et modifiable**, pas caché dans un champ masqué : le
visiteur doit voir sur quoi part sa demande, et l'on se trompe de page.

Branché sur les quatre fiches de service, la page Création, la page Formations
(chaque session) et la page Adhérent (chaque formule).

⚠️ **La demande n'est pas envoyée par le serveur.** Elle compose un message et
ouvre le client de messagerie du visiteur, à destination de
`contact@cga-brcgroup.com` ; il doit appuyer sur « Envoyer ». Un envoi réellement
automatique suppose un point d'entrée FastAPI **et des identifiants SMTP** que le
cabinet n'a pas fournis. Entre-temps, deux options : ce `mailto`, où la demande
part vraiment, ou un formulaire qui affiche « merci, c'est envoyé » alors que la
saisie est jetée en silence. La seconde est pire. Le bouton WhatsApp est là pour
la même raison, et il sera sans doute le plus utilisé.

**Les proformas sont téléchargeables** sur la page Création — les deux devis type
fournis par le cabinet, servis depuis `public/documents/` sous un nom normalisé.
Les fichiers d'origine portaient espaces et majuscules, qui font des adresses
fragiles une fois partagées par message. Le motif du `proxy` a dû être élargi :
sans cela, la négociation de langue interceptait `/documents/…` et rendait un 404.

**Un texte invisible, corrigé.** La carte `avantage` est dessinée pour le fond
indigo de l'accueil : texte blanc sur voile blanc translucide. Reprise telle
quelle sur les fiches de service, qui sont sur fond clair, elle donnait du blanc
sur blanc — le texte n'était tout simplement pas lisible. D'où `avantage--clair`.

**Le filigrane sort entier, et deux fois par page au plus.** Il débordait de
60 px à droite, si bien que la marque était coupée ; elle est désormais
entièrement dans le cadre, un peu plus petite et un cran plus discrète. Les pages
qui l'affichaient quatre ou cinq fois sont ramenées à deux.

**La frise du CGA revient au fer à gauche.** Posée dans une section centrée, elle
héritait du centrage : on ne savait plus quel récit allait avec quelle date. La
colonne est ramenée à gauche et bornée à 780 px — étalée sur toute la largeur,
l'année et son texte se retrouvaient à un mètre l'un de l'autre.

**Deux faux états actifs supprimés.** L'icône de la carte « Création
d'entreprise » s'allumait en magenta au repos, et l'entrée « Création
d'entreprise » du menu était surlignée par défaut. Dans les deux cas cela
ressemblait à une sélection en cours, alors que rien n'était sélectionné. Le
magenta est rendu au survol, où il signifie exactement une chose : le curseur est
ici.

**Le pied de page est allégé.** L'infolettre en part — elle occupait la moitié de
la largeur, avec titre et explication, sur chaque page — et rejoint le bandeau
« Parlons de votre projet », réduite au champ et au bouton : le titre de la
section dit déjà pourquoi on écrirait au cabinet. L'agrément ministériel est
retiré du pied, où il figurait pour la troisième fois après la barre du haut et
les fiches du cabinet. En dernière ligne, la signature « Powered by BïdaSoft ».

⚠️ **Le contenu anglais des quatre fiches et du formulaire de demande est en
français** pour les fiches. À faire traduire.

### Le devis en PDF — ce qui était demandé n'était pas possible tel quel

Le cabinet voulait que le bouton « Recevoir ce devis par WhatsApp » **joigne un
PDF**. Un lien `wa.me` ne transporte que du texte : aucune pièce jointe, quel que
soit le soin apporté au fichier. C'est une limite du protocole, pas un manque de
travail.

La solution retenue résout le besoin mieux qu'un fichier ne l'aurait fait : le
devis a **sa propre adresse**, `/estimation/devis?…`, mise en page pour l'écran
et pour le papier. Elle s'envoie comme un lien, s'ouvre sur n'importe quel
téléphone sans lecteur à installer, et se transforme en PDF d'un geste par la
commande d'impression du navigateur — « Enregistrer au format PDF » est proposé
sur Android comme sur iOS. Aucune bibliothèque de génération embarquée : quelques
centaines de kilo-octets épargnés à chaque visiteur.

Deux propriétés qui découlent du choix et qu'un PDF n'aurait pas eues : le devis
reste **calculé** — un lien ouvert plus tard affiche des montants cohérents avec
le barème du jour, non un chiffre figé — et il est **partageable sans base de
données**, toutes les réponses voyageant dans l'adresse.

Le message WhatsApp porte le récapitulatif chiffré **puis** le lien, dans cet
ordre : un destinataire sans réseau doit pouvoir lire les montants sans ouvrir
quoi que ce soit.

Le document dit sa date et dit qu'il **n'est pas une facture**, en clair dans le
corps et non en petits caractères : un document chiffré, daté et au nom du
cabinet sera lu comme un engagement s'il ne dit pas franchement le contraire.

### L'estimateur, vérifié

Barème éprouvé sur six cas : établissement, SARL au minimum légal, SARL à
999 999 puis à 1 000 000 FCFA — le droit proportionnel ne se déclenche qu'au-delà
de la référence, le total ne bouge donc pas entre les deux —, SA à Bafoussam
(14 semaines, les deux semaines de la ville hors guichet unique sont bien
ajoutées), et un jeu de paramètres volontairement absurdes, qui retombe sur les
valeurs sûres au lieu de produire une erreur. Les sous-totaux et le total
concordent.

### ⚠️ À rappeler au cabinet

**Le paiement Taramoney n'est pas branché.** Le cabinet a demandé que les
formules d'adhésion y renvoient, en précisant de le brancher « le moment venu »
et de le lui rappeler. Les boutons mènent toujours à la page Contact. Il faudra,
avant de commencer : les identifiants marchand, la documentation de l'API, et la
décision sur le lieu du branchement — très probablement un contexte backend dédié
à l'encaissement, et non le contexte L, qui ne porte que du contenu éditorial.

---

## 12 août 2026 (suite) — Le contenu du site passe au backend

### Ce qui a été demandé

Quatre choses, dans le désordre où elles sont venues.

1. Pouvoir **revenir au site** depuis la page de connexion à l'ERP.
2. **Vérifier que le site a un backend**, et sinon l'y brancher, de façon que
   tout soit modifiable depuis le backend — le site n'étant qu'une vitrine.
3. L'annonce doit apparaître **sur toutes les pages** : en passant d'une page à
   l'autre, on doit la revoir.
4. Respecter la **Clean Architecture** déjà appliquée, bien organiser le backend,
   et **commenter le code partout** pour qu'on comprenne ce qui a été fait.

### Ce qui a été constaté, et qui change la réponse

**Le backend existe déjà, et il est propre.** `Backend_erp_cga` est un monolithe
modulaire FastAPI en Clean Architecture : onze contextes bornés, quatre cercles
par contexte, deux surfaces publiques (`contrats.py` pour les entités, `api.py`
pour les cas d'usage), et une batterie de tests qui **refusent** une dépendance
allant d'un cercle interne vers un cercle externe. La question n'était donc pas
« faut-il un backend » mais « pourquoi le contenu de la vitrine n'y est-il pas ».

Réponse : parce qu'il avait été écrit en TypeScript, dans le frontend. Une faute
de frappe dans un article demandait un développeur et un déploiement. C'est cela
qui a été corrigé.

### Ce qui a été décidé, et pourquoi

**Un douzième contexte borné : L · Vitrine publique.** Et non un dossier de
fichiers dans le frontend, ni une extension d'un contexte existant.

* *Pourquoi un contexte à lui seul.* Le contenu éditorial n'est pas une donnée
  fiscale. Le mettre dans le Référentiel aurait mélangé « le taux de TVA au
  15 juillet 2026 » et « l'article du blog sur la patente » dans le même module.
* *Pourquoi il ne lit aucun autre contexte.* Du contenu qui aurait besoin d'un
  paramètre légal ne serait plus du contenu, ce serait un calcul — et il
  appartiendrait au contexte qui le porte. Le jour où l'on voudra afficher un
  barème sur le site, la bonne réponse sera une route du Référentiel appelée par
  le site, pas une arête ajoutée au graphe. Cette contrainte est inscrite dans
  `tests/test_architecture.py`, elle n'est pas qu'une intention.
* *Pourquoi personne ne le lit non plus.* Le contenu éditorial n'a rien à dire au
  métier fiscal.

**Les quatre cercles, sans exception.** `domaine/` porte les entités et le port
`DepotContenuVitrine` ; `application/` porte le service de lecture ;
`adaptateurs/sortant/` lit le YAML ; `adaptateurs/entrant/` expose les routes.
Le service ne lit aucun fichier : il reçoit un dépôt. C'est ce qui permet de
l'éprouver sur un dépôt en mémoire, sans disque — et les tests écrits ainsi sont
la preuve que l'inversion de dépendance sert à quelque chose plutôt que d'être
une figure de style.

**Le corps d'un article est une suite de blocs typés, pas du Markdown ni du
HTML.** Trois raisons, dans cet ordre. La sécurité d'abord : un contenu qui
arrive du backend et qui serait du HTML devrait être assaini avant affichage ;
des blocs typés ne portent que du texte, il n'y a rien à injecter. Le rendu
ensuite : chaque type de bloc a son style propre. L'édition enfin : une personne
qui corrige le YAML voit la structure de l'article.

**Le YAML plutôt qu'une base, pour commencer.** Parce que la personne qui corrige
une faute, au cabinet, doit pouvoir le faire sans qu'on ait d'abord construit un
écran d'administration. Le YAML se lit, se commente, se relit en revue, et se
versionne : on sait qui a changé quoi et quand. Le port est déclaré dans le
domaine ; le jour venu, un `DepotContenuVitrineSql` le réalisera et seul
l'adaptateur changera.

**Un fichier malformé fait échouer le chargement.** Rubrique inconnue, date
incohérente, bloc sans type : le démarrage est refusé. Mieux vaut une panne
bruyante et immédiate qu'un blog amputé de trois articles que personne ne
remarque avant des semaines.

**Le site garde un contenu de secours.** `app/lib/blog.ts`, `annonces.ts` et
`partenaires.ts` restent au dépôt, mais changent de statut : ce ne sont plus la
source, c'est le **dernier état connu**. Si le backend est arrêté, en cours de
déploiement, ou joignable une seconde trop tard, la vitrine affiche ce
contenu-là plutôt que du vide — ce qui serait pire. La source est le YAML, et
c'est écrit en tête du module de lecture pour que personne ne s'y trompe.

**Deux `null` qu'il ne faut surtout pas confondre.** « Le backend répond qu'il
n'y a pas d'annonce aujourd'hui » et « le backend ne répond pas » appellent des
conduites opposées : dans le premier cas on n'affiche rien, dans le second on
affiche le secours. Les confondre ferait réapparaître toute seule une annonce que
le cabinet vient de retirer. D'où le type `Lecture<T>` et son champ `repondu`.

**L'annonce réapparaît à chaque page — et le mécanisme n'est pas celui qu'on
croit.** Le site est une application d'une seule page : en passant de l'accueil au
blog, la coquille n'est pas reconstruite et le bandeau n'est pas remonté. Sans
traitement, l'annonce disparue au bout de trente secondes ne serait plus jamais
revenue de toute la visite. La solution retenue est une **clé React portant le
chemin courant** : changer de page remonte le composant, et tout son état repart
à neuf — décompte et animation compris. Un effet de remise à zéro aurait fait la
même chose, en moins lisible, en plus fragile, et le linter le refusait à juste
titre.

La fermeture explicite, elle, ne revient pas. C'est la différence entre « je n'ai
pas eu le temps de lire » et « je ne veux pas de ça » : le décompte redémarre, le
refus est retenu pour toute la visite.

**Deux sorties vers le site public.** Depuis la page de connexion, qui est un
cul-de-sac — ni en-tête, ni pied, ni menu — et depuis la barre latérale de
l'ERP. Dans les deux cas, un libellé explicite : le logo ramenait déjà à
l'accueil, mais un logo cliquable est une convention, pas une indication.

### Ce qui a été livré

Backend — `app/contextes/vitrine/` : `domaine/entites.py`, `domaine/ports.py`,
`application/service_contenu.py`, `adaptateurs/sortant/depot_yaml.py`,
`adaptateurs/entrant/routes_http.py`, `contrats.py`, `api.py`. Contexte enregistré
dans `main.py`, dans `config.py`, dans `tests/test_architecture.py` et dans
`Docs/architecture/01-contextes-bornes.md`. Quatre routes : sommaire du blog avec
les comptes par rubrique, article avec ses voisins de lecture, annonce à une
date, institutions.

Contenu — `Contenu_vitrine/articles.yaml`, `annonces.yaml`, `institutions.yaml` :
quatorze articles, une annonce, quatre institutions, chaque fichier ouvert par un
commentaire qui explique quoi y écrire et ce qu'il ne faut pas y casser.

Frontend — `app/lib/contenu-vitrine.ts`, seul point du site qui sait où trouver le
contenu ; blog, article, ruban d'institutions et bandeau d'annonce branchés
dessus ; bouton de retour au site sur la connexion et dans la barre de l'ERP.

Documentation — en-têtes ajoutés aux six pages de la vitrine qui n'en avaient
qu'une ligne, et à `BarreLaterale.tsx`, seul fichier du frontend qui n'avait aucun
bloc de documentation.

Vérifié : **237 tests backend** (contre 202 avant ce lot), `ruff` au vert,
`tsc` et `eslint` sans un avertissement, build Next complet à 55 pages, et les
quatre routes exercées sur le backend en marche.

### Ce qui reste

- **Un écran d'administration** pour éditer le contenu sans toucher au YAML.
  Le port est prêt ; c'est l'adaptateur et l'interface qui manquent.
- **L'invalidation du cache** : une correction du YAML n'est visible qu'après
  redémarrage du backend. Assumé tant que le cabinet corrige par lots ; à traiter
  le jour où l'édition devient quotidienne. L'endroit est identifié et commenté.
- **Le reste du corpus Facebook** : une quarantaine de publications lues sur 113.

---

## 12 août 2026 — Blog, annonces de site, et la règle des bannières

### Ce qui a été demandé

Trois choses, en plus de la finition de la vitrine déjà engagée.

1. **La hauteur des bannières.** L'accueil est désormais **la seule page** qui
   garde une bannière pleine hauteur. Toutes les autres pages ont une bannière
   réduite.

2. **Un blog.** Les 113 captures rassemblées la veille dans
   `Docs/publications-facebook-blog/` servent de matière. Le blog a deux
   fonctions : renseigner les clients et leurs conseillers sur les **textes
   administratifs qui ont changé**, et porter les **annonces** du cabinet. Le
   client a insisté : il faut que les publications soient observées de près, et
   que chaque article se partage sur **Facebook ou WhatsApp** sous une forme qui
   donne envie de cliquer et d'entrer sur le site pour lire la suite. Cela
   suppose une nouvelle entrée de menu.

3. **Une annonce de site.** Un message accrocheur qui apparaît sur toutes les
   pages, que le visiteur peut **fermer**, et qui **disparaît de lui-même au
   bout de 30 secondes** pour ne pas perturber la navigation.

Demande transversale : **tout enregistrer**, échanges et réponses, pour que le
contexte ne se reperde pas d'une séance à l'autre. D'où ce journal.

### Ce qui a été décidé, et pourquoi

**Les bannières.** La règle était déjà appliquée dans le lot en cours :
`EnteteDePage` a été ramené à la moitié de la hauteur du héros d'accueil
(`50svh`, minimum 400 px, 280 px sous 900 px de large), pendant que le composant
`Heros` — plein écran, carrousel à messages, formulaire — reste réservé à
`app/[locale]/(vitrine)/page.tsx`. La demande confirme le choix et le fige :
**toute nouvelle page passe par `EnteteDePage`, jamais par `Heros`.** Le blog et
les articles s'y conforment.

**Le corpus Facebook n'est pas republiable tel quel.** C'est la décision la plus
importante de la journée, et elle va à l'encontre de l'usage le plus direct des
fichiers. En les regardant :

- ce sont des **captures de navigateur**, pas des visuels : on y voit la colonne
  de commentaires, les boutons Facebook, et l'identité de la personne connectée
  (« Commenter en tant que Loïc Tonba ») ;
- `pub-50` contient une **conversation WhatsApp privée** avec un prospect,
  floutée seulement en partie ;
- plusieurs images appartiennent à des **tiers** : dessins signés GABS, dessin
  filigrané `ledauphine.com`, personnage des Minions. Les publier sur le site du
  cabinet exposerait celui-ci à une réclamation ;
- les plus anciens visuels portent une **adresse électronique périmée**
  (`info@brconsulting-cm.com`), remplacée depuis par `contact@cga-brcgroup.com`.

Le corpus est donc traité comme une **source rédactionnelle** : les faits sont
extraits, les textes réécrits, et les illustrations prises dans les photographies
déjà présentes au dépôt. Le jour où le cabinet fournira les exports propres de
ses visuels carrés — qui sont sa création et qui sont bons — ils remplaceront les
photographies sans rien changer d'autre que le chemin d'image dans `blog.ts`.

**La ligne éditoriale est celle du cabinet, pas une invention.** En observant les
113 publications, quatre rendez-vous reviennent, et ils deviennent les rubriques
du blog :

| Rubrique du blog | Origine dans les publications |
| --- | --- |
| Le saviez-vous ? | Visuels carrés « Le saviez-vous ? », faits fiscaux et juridiques |
| Vrai ou faux ? | Publications « Vrai ou Faux ? », idées reçues passées au crible |
| Lundi comptable | « Lundi comptable avec Aïcha », modes d'emploi comptables |
| Mercredi juridique | « Mercredi juridique », cas pratiques traités par le juriste Owona |
| Le coin du fiscaliste | « Conseils de notre fiscaliste Kamdem », l'impôt expliqué |
| Annonces | Offres, packs de formalisation, vœux, informations de service |

Reprendre les rendez-vous du cabinet plutôt qu'un découpage abstrait a un
avantage direct : l'audience Facebook reconnaît les noms **et les visages** —
Aïcha, Owona, Kamdem sont des personnages installés, avec leur jour de la semaine
— et le cabinet sait déjà alimenter ces cases, puisqu'il le fait chaque semaine.

**Le partage précède la lecture.** Un article n'est pas d'abord une page, c'est
d'abord une vignette dans un fil ou dans une conversation WhatsApp. Chaque
article porte donc ses métadonnées Open Graph — titre, résumé, image, date — et
une accroche courte, écrite pour être lue seule. Les boutons de partage visent
Facebook, WhatsApp et la copie du lien : ce sont les trois canaux réels de la
clientèle camerounaise du cabinet, et WhatsApp compte au moins autant que
Facebook.

Deux réglages en découlent, contre-intuitifs mais vérifiés sur le rendu :

- **L'illustration doit être en paysage et faire au moins 1 200 px de large.**
  En dessous de 600 px, Facebook renonce à la grande carte et met une imagette
  carrée à gauche du titre — l'inverse exact de l'effet recherché. Le premier
  jet de l'article « Lundi comptable » illustrait par le portrait de la
  comptable, un carré de 480 px : il a été remplacé par une photographie de
  1 400 px. La contrainte est écrite en tête de `blog.ts`.
- **Les dimensions ne sont pas déclarées dans les métadonnées.** Annoncer
  1200 × 630 pour une photographie qui fait 1400 × 933 fait recadrer la vignette
  de travers. Facebook mesure très bien le fichier lui-même.
- **L'adresse partagée est calculée, pas lue dans le navigateur.** Elle est
  reconstruite à partir du domaine, de la langue et du chemin. Les boutons sont
  donc bons dès le rendu serveur, et le lien partagé est la version canonique,
  sans le paramètre de campagne ni l'ancre que le visiteur traîne derrière lui.
  `NEXT_PUBLIC_SITE_URL` couvre la préproduction.

**L'annonce s'efface deux fois.** Le visiteur peut la fermer, et elle part seule
au bout de 30 secondes. La fermeture est mémorisée pour la durée de la session
(`sessionStorage`) : une annonce qui revient à chaque page est exactement le
défaut qu'on cherchait à éviter. Le décompte est suspendu quand le pointeur est
sur le bandeau ou quand le clavier y entre — retirer sous les doigts d'un
visiteur le lien qu'il allait cliquer serait pire que ne rien afficher. Et un
visiteur qui a demandé `prefers-reduced-motion` n'a pas de barre de décompte
animée.

### Ce qui a été livré

- `Docs/journal-de-bord.md` — ce journal.
- `app/lib/blog.ts` — rubriques, articles, tri, voisinage, recherche par slug.
- `app/lib/annonces.ts` — l'annonce en cours, avec sa fenêtre de validité.
- `app/components/vitrine/BandeauAnnonce.tsx` — le bandeau refermable.
- `app/components/vitrine/CarteArticle.tsx` — la vignette d'article.
- `app/components/vitrine/PartageArticle.tsx` — Facebook, WhatsApp, copie du lien.
- `app/components/vitrine/FiltreRubriques.tsx` — le filtre du sommaire, fait de
  liens et non de boutons : chaque rubrique a son adresse
  (`/blog?rubrique=lundiComptable`), donc son signet, son envoi par message et
  son bouton « précédent », et le filtrage ne coûte pas une ligne de JavaScript.
- `app/lib/site.ts` — l'adresse publique du site, et `metadataBase` posée sur la
  mise en page racine : sans elle, toute image d'aperçu déclarée par un chemin
  relatif est ignorée et le lien part nu.
- `app/[locale]/(vitrine)/blog/page.tsx` — le sommaire.
- `app/[locale]/(vitrine)/blog/[slug]/page.tsx` — l'article.
- Entrée « Blog » dans la barre de navigation, dans le menu du téléphone et dans
  le pied de page ; libellés fr et en. Elle est placée après « Le CGA » et avant
  « Estimation » : le blog relève de ce que le cabinet dit de lui-même, et le
  reléguer en fin de barre l'aurait rendu invisible, alors que c'est par lui que
  le trafic de Facebook et de WhatsApp entrera.
- Le repère de menu suit désormais la **section** et non la seule page :
  `/blog/mon-article` marque « Blog » comme courant. L'égalité stricte laissait
  la barre muette dès qu'on ouvrait un article.
- Styles dans `app/styles/vitrine.css`.

Vérifié : `npm run lint` sans avertissement, `npm run build` complet, 47 pages
générées dont les vingt pages d'articles (dix articles × deux langues), et le
rendu contrôlé page par page sur le serveur de développement — sommaire, filtre
par rubrique, article, version anglaise, et métadonnées Open Graph.

### Deuxième passe du même jour — dépouillement poursuivi

Le dépouillement a repris après la première livraison. Environ quarante des 113
publications ont maintenant été lues, réparties sur toute la période 2018-2026.
Quatre articles s'y sont ajoutés, et un a été enrichi :

- **« Pas encore de clients, donc pas d'obligations fiscales » — vrai ou faux ?**
  (pub-19). L'obligation ne naît pas de la recette mais de l'immatriculation : la
  déclaration néant est due, et la pénalité frappe le silence, pas le montant.
  C'est la publication qui a fait apparaître la rubrique « Vrai ou faux ? ».
- **À qui s'applique réellement l'IGS** (pub-22), qui a fait apparaître « Le coin
  du fiscaliste ». Point central retenu : l'IGS ne dépend pas toujours du
  bénéfice réalisé, mais de l'existence et de l'activité de l'entreprise.
- **Les huit obligations comptables de début d'année** (pub-38 et pub-25), la
  liste d'Aïcha, de la mise à jour de l'exercice écoulé à l'anticipation de la
  DSF.
- **Dossier propre, décision rapide** (pub-58), sur ce qu'une banque lit
  réellement dans un dossier de financement.
- **Adhérer au CGA** enrichi (pub-55 et pub-72) de deux choses qui manquaient et
  qui sont le vrai argument du centre agréé : l'assistance permanente d'un
  inspecteur des impôts et l'accès aux formations du centre, puis la liste des
  prestations souscriptibles à la carte.

Deux prudences de rédaction sur cette passe :

- La publication sur la **DSF 2026** annonce « jusqu'à quand payer sans
  pénalités » mais ne donne pas les dates dans la partie visible de la capture.
  Aucune échéance n'a donc été inventée : l'article dit que le délai dépend du
  régime et invite à le faire vérifier. Les dates viendront du cabinet.
- Plusieurs publications sont **inutilisables** et resteront hors du blog : les
  dessins de presse filigranés `ledauphine.com`, les dessins signés GABS, les
  images de Minions, et la citation d'Aliko Dangote illustrée par une
  photographie de tiers.

### Ce qui reste

- **Dépouiller le reste du corpus.** Une quarantaine de publications ont été
  lues ; les soixante-dix autres contiennent d'autres faits utiles. Ajouter un
  article revient à ajouter un objet dans `ARTICLES`.
- **Récupérer les dates d'échéance de la DSF** auprès du cabinet, par régime
  d'imposition, pour compléter l'article de début d'année.
- **Obtenir les visuels propres.** Demander au cabinet les fichiers d'origine de
  ses carrés « Le saviez-vous ? » et de ses affiches d'offre, sans le chrome
  Facebook et avec l'adresse électronique à jour.
- **Vérifier les faits fiscaux avec le cabinet.** Les articles citent des règles
  tirées de publications de 2017 et 2018. Le droit a pu bouger : chaque article
  porte la date de la publication d'origine, et le cabinet doit confirmer ce qui
  est encore en vigueur avant mise en ligne.
- **Traduction anglaise du corps des articles.** Les libellés d'interface sont
  bilingues ; le corps des articles est pour l'instant en français dans les deux
  langues, ce qui est le comportement voulu tant que le cabinet n'a pas fait
  traduire.

---

## 11 août 2026 — Finition de la vitrine

Passe de finition menée avant la demande du blog, encore non commitée à
l'ouverture du 12 août.

- **Ruban des institutions.** DGI, CNPS, ONECCA, OHADA, en bande défilante sur
  l'accueil. Choix assumé et consigné dans `app/lib/partenaires.ts` : ce ne sont
  **pas des partenaires commerciaux**, et le libellé de la section le dit. Afficher
  le logo d'une entreprise privée sous le mot « partenaire » affirmerait une
  relation contractuelle ; ces quatre institutions-là sont le cadre dans lequel
  un centre de gestion agréé travaille par nature, et le dire est vérifiable.
- **Connexion de démonstration.** Le formulaire de `/connexion` compare deux
  constantes **dans le navigateur**. Ce n'est pas une authentification, le fichier
  le dit en tête et la page le dit au visiteur. La vraie authentification
  appartient au backend FastAPI ; aucune donnée client réelle ne doit passer
  derrière cet écran avant.
- **Bannières des pages intérieures** ramenées à la moitié de la hauteur, avec
  fondu entre deux photographies quand la page en fournit deux.
- **Étapes de progression** rendues génériques : le composant reçoit désormais ses
  étapes, ce qui a permis de le réemployer pour le parcours d'adhésion en quatre
  temps.
- **Estimateur** — correction d'un défaut qui rendait le champ « capital »
  insaisissable : il réaffichait `Math.max(capital, capitalMin)`, si bien
  qu'effacer un chiffre réécrivait le minimum légal à chaque touche. La valeur
  saisie est maintenant conservée comme texte, et le bornage a lieu au calcul.
- **Corrections de fond** : la SA a bien une ligne au barème (le contraire avait
  été supposé à tort) ; « Le cabinet » devient « Le CGA » au menu et au pied ; le
  second mobile `+237 676 887 686` entre dans la barre utilitaire, les deux
  mobiles avant le fixe, parce qu'au Cameroun on appelle et on écrit depuis un
  mobile et que le fixe sert de repli.
