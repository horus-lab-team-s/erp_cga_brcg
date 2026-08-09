# 00 · Vision et métier

## 1. Ce qu'est un Centre de Gestion Agréé

Association agréée par le Ministre des Finances, partenaire de l'administration fiscale, qui
tient la comptabilité et gère les obligations fiscales de PME adhérentes. Broad Range
Consulting Group opère sous l'agrément MINFI/DGI n° 00000048 — Douala Akwa, Yaoundé
Elig-Essono, Bafoussam.

Cette nature juridique change tout pour le système :

| Caractéristique du CGA | Conséquence pour la plateforme |
|---|---|
| L'adhésion ouvre des avantages fiscaux (abattement sur le bénéfice, exonération temporaire de patente, précompte réduit, contrôle sur pièces) | Le statut d'adhérent et sa **date d'effet** modifient le calcul de l'impôt : données historisées, jamais écrasées |
| L'administration attend du CGA qu'il garantisse la **sincérité** des comptes | Piste d'audit inaltérable, contrôles de vraisemblance, notion explicite de « dossier revu par un réviseur » |
| Le CGA engage sa responsabilité et son agrément | Traçabilité de qui a saisi, revu, validé, déclaré. **Jamais de suppression physique** : contre-passation motivée uniquement |
| Un inspecteur assistant rattaché à l'administration intervient | Rôle de lecture et d'avis, distinct des collaborateurs internes |

## 2. Le problème

Portefeuille de 128 adhérents en croissance, exigences réglementaires qui se durcissent,
effectifs constants. Cinq difficultés : justificatifs tardifs et dispersés, contrôle des
factures manuel et inégal, échéances suivies sur plusieurs supports, clôture annuelle
concentrée sur trois mois, direction sans vision consolidée du risque.

## 3. La proposition de valeur

**Déplacer le contrôle en amont.** Une facture non conforme détectée à sa réception se
régularise auprès du fournisseur ; découverte trois mois plus tard, elle ne laisse qu'une
perte fiscale sèche.

Le cœur du produit est un moteur de conformité qui produit, pour chaque anomalie, une
**conséquence fiscale chiffrée** — « TVA non déductible, 379 350 FCFA » — qui se propage
automatiquement jusqu'à la déclaration mensuelle puis jusqu'à la liasse annuelle. C'est cette
chaîne, du constat jusqu'au chiffre, que les écrans doivent rendre visible.

## 4. Acteurs

**Internes** — chargé de clientèle (Aïcha MBALLA), comptables (Serge NKOULOU, Estelle FOTSO),
réviseur (Rodrigue BIYA'A), fiscaliste (Charles ATANGANA), chargé de formalités, direction
(Paule Diane HIMSTA).

**Externes** — adhérent ; clients et fournisseurs de l'adhérent, modélisés comme tiers à part
entière puisque ce sont eux qui émettent les factures contrôlées ; DGI via le centre de
rattachement (CDI, CIME, DGE) ; CNPS ; CFCE, greffe RCCM, OAPI ; expert-comptable ONECCA ;
banques et opérateurs Mobile Money.

## 5. Deux populations, deux ergonomies

| | Collaborateur | Adhérent |
|---|---|---|
| Support | Bureau, 1440 × 900 sans défilement | Mobile d'abord, 390 px |
| Usage | Plusieurs heures par jour | Quelques minutes par semaine, debout, réseau instable |
| Attente | Densité, tableaux, clavier | Une action principale par écran, langage courant |
| Ligne de tableau | 36 px | 52 px |
| Champ et bouton | 32 px | 44 px minimum (impératif tactile) |
| Largeur de contenu | Pleine | 640 px |
| Vocabulaire | Terminologie métier exacte | « justificatif », pas « pièce comptable » |

Cette distinction est portée dans le code par les jetons de densité de
`Frontend_erp_cga/app/styles/tokens.css`.

## 6. Contexte d'usage local

Connexion lente et intermittente, coupures d'électricité, parc Android d'entrée de gamme,
monnaie électronique omniprésente, WhatsApp comme canal professionnel dominant.

Conséquences non négociables : PWA avec **mode hors ligne** et synchronisation différée ;
pas d'image lourde ni d'animation coûteuse ; **rien ne se perd** — toute action hors ligne
est mise en file avec son état visible ; un **mode manuel de secours** derrière chaque
intégration, les API publiques camerounaises étant irrégulières.

## 7. Les huit pièges à éviter

1. **Coder la loi en dur.** Taux de TVA, seuils, abattement, dates limites : tout changera.
2. **Se fier aux sources secondaires.** Y compris celles de ce dossier. Chaque règle est
   validée sur le texte officiel par le fiscaliste, et la référence conservée.
3. **Traiter le régime fiscal comme un attribut figé.** Le reclassement automatique de l'IGS
   impose un historique daté.
4. **Oublier que le libératoire n'est pas total.** Retenues à la source, taxes de services et
   charges sociales subsistent sous l'IGS. Le moteur d'obligations ne raisonne jamais
   « régime X ⇒ rien à faire ».
5. **Concevoir le contrôle de facture comme un booléen.** La valeur est dans la conséquence
   fiscale chaînée jusqu'à la DSF.
6. **Sous-estimer la collecte des pièces.** C'est le vrai goulot d'étranglement.
7. **Négliger le premier exercice et les exercices décalés.** Systématiquement oubliés,
   systématiquement bloquants en production.
8. **Ignorer la responsabilité du CGA.** Un dépôt sans traçabilité de la revue expose
   l'agrément du cabinet.
