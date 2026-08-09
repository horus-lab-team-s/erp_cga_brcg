# 03 · Moteur de conformité de facture

Le cœur du produit.

## 1. Principe directeur

Une facture ne se juge pas « conforme / non conforme » de façon binaire. Elle produit un
**rapport de conformité** contenant des constats gradués, chacun assorti d'une **conséquence
fiscale** exploitable en aval. C'est cette conséquence qui fait la valeur : elle alimente
automatiquement la TVA déductible du mois et les réintégrations de la DSF.

```
Facture ──▶ Moteur ──▶ Rapport ──▶ Constats ──▶ Conséquences fiscales
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    ▼                 ▼                 ▼
                            Attributs fiscaux   Déclaration TVA   Tableau de passage
                            sur l'écriture        du mois          de la DSF
```

## 2. Anatomie d'une règle

Fichier YAML par règle, dans `Docs/referentiel/regles/`. Format identique en base.

```yaml
code: FAC-ID-003
libelle: NIU du fournisseur présent et valide
categorie: IDENTIFICATION
version: '2026.1'
applicableDu: 2026-01-01
applicableAu: null
severite: BLOQUANT
statut: A_VALIDER
fondement:
  texte: CGI art. 150 (5) ; conditions d'exercice du droit à déduction de la TVA
  source: Document de cadrage § 2.4
portee:
  typeDocument: [FACTURE_ACHAT]
  exclusions: [FOURNISSEUR_ETRANGER]
predicat:                       # VRAI = conforme. FAUX = constat émis.
  and:
    - '!!': { var: emetteur.niu }
    - regex: [{ var: emetteur.niu }, { param: FORMAT_NIU }]
    - '==': [{ var: emetteur.niuActif }, true]
consequence:
  tvaDeductible: false
  chargeDeductible: false
  posteReintegration: TAB_PASSAGE.CHARGES_NON_DEDUCTIBLES
message: NIU du fournisseur absent ou non reconnu.
remediation: >-
  Demander une facture rectificative mentionnant le NIU.
  Vérifier l'activité du NIU sur le portail DGI.
```

### Le prédicat exprime la conformité

`predicat` vrai ⇒ la règle est respectée, aucun constat. `predicat` faux ⇒ constat émis avec
la sévérité et la conséquence déclarées. C'est la convention du document de cadrage. Elle est
contre-intuitive et donc rappelée partout dans le code.

### Les sept points de conception

1. **Sévérité en quatre niveaux** (cinq états d'affichage avec « Conforme »).
2. **Séparation stricte règle / moteur / données.** Les règles vivent en base, éditables par
   le fiscaliste via l'écran E11, pas dans le code source.
3. **Fondement légal obligatoire.** Sans lui, impossible de savoir quoi mettre à jour à la
   loi de finances suivante, ni de justifier un rejet à un adhérent mécontent. C'est ce qui
   distingue cet outil d'un validateur de formulaire.
4. **Versionnement temporel.** Le moteur charge le jeu de règles valide à la date de
   l'opération.
5. **Conséquence fiscale déclarative.** La règle ne fait pas d'effet de bord : elle *décrit*
   la conséquence. Un service en aval l'applique. C'est ce qui rend le tout testable.
6. **Aucun `eval`.** Prédicats en JSONLogic, évalués par une bibliothèque sûre.
7. **Un test unitaire par règle**, cas passant et cas échouant, exécuté en intégration
   continue.

## 3. Les niveaux de gravité

| Niveau | Sens métier | Effet | Traitement visuel |
|---|---|---|---|
| `BLOQUANT` | Interdit l'émission (vente) ou la déduction (achat) | La comptabilisation est refusée. L'action principale devient la demande de rectification. | Fond `#B3261E` plein, texte blanc, glyphe ⬣ |
| `MAJEUR` | Comptabilisable, mais conséquence fiscale automatique | L'attribut fiscal est propagé à l'écriture | Fond `#B4690E` plein, texte blanc, glyphe ▲ |
| `AVERTISSEMENT` | Risque en cas de contrôle, à documenter | Aucun effet automatique, constat conservé au dossier | Fond `#FBF0E2`, bordure et texte `#B4690E`, glyphe △ |
| `INFORMATION` | Bonne pratique | Aucun | Fond `#EDE9F5`, texte `#492F79`, glyphe ⓘ |
| *(Conforme)* | Aucun constat | — | Fond `#E6F2EC`, texte `#1E7A4C`, glyphe ✓ |

**Règle absolue** : la couleur ne porte jamais seule l'information. Glyphe et libellé sont
toujours présents, y compris dans les tableaux les plus denses.

## 4. Chiffrage de l'enjeu

Le montant affiché dans le bandeau de verdict découle mécaniquement de la conséquence :

| Conséquence | Enjeu chiffré |
|---|---|
| `tvaDeductible: false` seul | Montant de TVA de la facture |
| `chargeDeductible: false` seul | Montant HT |
| Les deux | Montant TTC |
| Aucune des deux | Non chiffré — le constat reste qualitatif |

Exemples tirés du jeu de démonstration : `FAC-ACH-007` sur F-2026-0412 → 379 350 FCFA (la
TVA) ; `FAC-ID-003` sur F-2026-0414 → 536 625 FCFA (le TTC, TVA et charge rejetées).

## 5. Résolution des paramètres

Un prédicat peut référencer un paramètre du référentiel par `{ param: CODE }`. Avant
évaluation, le moteur **parcourt l'arbre du prédicat, résout chaque référence à la date de
l'opération et substitue la valeur littérale**.

Cette pré-résolution, plutôt qu'un opérateur dynamique, a trois vertus :

- l'évaluation reste une fonction pure de JSONLogic, testable sans base ;
- le rapport conserve la **liste des paramètres utilisés avec leur valeur et leur date
  d'effet** — traçabilité défendable devant la DGI ;
- un paramètre manquant échoue à la résolution, avant l'évaluation, avec un message clair.

Le rapport signale par ailleurs si l'un des paramètres ou l'une des règles employés est
encore au statut `A_VALIDER`.

## 6. Portée d'une règle

Avant évaluation, le moteur filtre sur la `portee` :

- `typeDocument` — facture d'achat, facture de vente, avoir…
- `regimesEmetteur` — une règle de TVA ne s'applique pas à un émetteur à l'IGS
- `exclusions` — `FOURNISSEUR_ETRANGER` notamment : la LF 2025 exclut de la déduction les
  charges justifiées par des factures sans mentions obligatoires, **sauf** fournisseurs
  étrangers

Une règle hors portée n'est ni évaluée ni comptée dans le total de règles appliquées.

## 7. Catalogue de règles à constituer

Huit catégories. Démarrer avec quinze à vingt règles solides et bien fondées plutôt que
quatre-vingts approximatives.

| Catégorie | Objet | Exemples |
|---|---|---|
| 1 · Identification de l'émetteur | Raison sociale, forme juridique, **NIU présent, valide et actif**, RCCM cohérent, adresse, régime cohérent avec le contenu | `FAC-ID-003`, `FAC-ID-008`, `FAC-ID-012` |
| 2 · Identification du client | Dénomination, adresse, **NIU obligatoire en B2B**, cohérence avec le tiers comptable | — |
| 3 · Identification du document | Numérotation **unique, continue, chronologique** (les trous sont un signal d'alerte majeur), date dans l'exercice, nature explicite (une proforma n'est jamais comptabilisable), devise et **contre-valeur en XAF** si facturation en devise | `FAC-DOC-002`, `FAC-DOC-011` |
| 4 · Contenu des lignes | Désignation précise (« divers », « prestations » ⇒ alerte), quantité, prix unitaire HT, montant par ligne, taux de TVA explicite | `FAC-DOC-011` |
| 5 · Cohérence arithmétique | Σ lignes = total HT ; TVA = base × taux ; TTC = HT + TVA + accises ; remises et escomptes dans la base taxable ; montant en chiffres et en lettres | `FAC-CAL-002` |
| 6 · Traitement fiscal | IGS ⇒ pas de TVA facturée, mention « TVA non applicable » exigée ; exonération ⇒ fondement mentionné ; droits d'accises ; **retenue à la source** si le client figure sur la liste des entités habilitées ; précompte réduit pour les adhérents CGA | — |
| 7 · Déductibilité — la plus rentable | Fournisseur immatriculé **au régime du réel** ; mentions de l'art. 150 (5) ; **règlement en espèces au-delà du seuil ⇒ TVA non déductible** ; délai d'exercice du droit à déduction ; charges exclues ; charges plafonnées (contrôle à l'exercice, pas à la facture) | `FAC-ACH-007` |
| 8 · Vraisemblance et anti-fraude | Doublon, montant aberrant, fournisseur nouvellement créé pour une seule facture, écart facture / bon de commande / bon de livraison, séquence manquante, ratio charges/CA hors norme sectorielle | `FAC-VRA-005`, `FAC-VRA-009` |

Les règles des catégories 3 (séquence), 7 (plafonds) et 8 (ratios) demandent une **vision
d'ensemble** : elles ne s'évaluent pas sur une facture isolée. Voir § 8.

**Implémenté à ce jour** : les cinq règles du § 13.6 du dossier de design — `FAC-ACH-007`,
`FAC-ID-003`, `FAC-DOC-011`, `FAC-CAL-002`, `FAC-VRA-005`.

## 8. Trois moments d'exécution, un seul moteur

| Moment | Jeu de règles | Comportement |
|---|---|---|
| **À l'émission** d'une facture de vente | Règles de vente | **Bloquant** : on n'émet pas une facture non conforme |
| **À la réception** d'une facture d'achat | Règles d'achat | Non bloquant mais **qualifiant** : produit les indicateurs de déductibilité |
| **En revue périodique** — contrôle de masse avant déclaration TVA, contrôle annuel avant DSF | Règles nécessitant une vision d'ensemble | Séquences, plafonds d'exercice, ratios |

## 9. Écarter un constat

Le réviseur peut lever une anomalie. C'est un acte engageant : il porte la signature du
Centre.

- **Motif obligatoire**, choisi dans une liste fermée puis précisé en texte libre.
- **Pièce d'appui** attendue. Une dérogation sans pièce est signalée en anomalie et doit être
  régularisée.
- Inscription au **journal des dérogations** : date, règle, entreprise, motif, enjeu levé,
  auteur, pièce d'appui.
- Restitution mensuelle à la direction (écran E de la maquette Direction) : combien de
  dérogations, par qui, pour quel enjeu, combien sans pièce.

## 10. Qualité des règles

Une règle trop souvent écartée est une règle mal calibrée, pas un portefeuille indiscipliné.
Le tableau de bord du réviseur suit, par règle : nombre de constats, taux d'écartement, enjeu
cumulé, et une lecture — `Saine`, `À surveiller`, `À recalibrer`, `Trop bruyante`.

Exemple du jeu de démonstration : `FAC-VRA-005` (doublon possible) produit 31 constats
écartés à 68 % — trop bruyante, à recalibrer par le fiscaliste.

## 11. Choix technique

Pas de moteur de règles lourd type Drools : l'équipe est réduite.

- Règles stockées en YAML puis en base (JSON), éditables via l'écran E11.
- Prédicats évalués par **JSONLogic** — jamais d'`eval` sur du code arbitraire.
- Un test unitaire par règle, cas passant et cas échouant, en intégration continue.
- Un **bac à sable** dans le back-office pour que le fiscaliste éprouve une règle sur des
  factures réelles avant activation, et voie combien seraient concernées.
- Toute activation ou modification de règle est journalisée et versionnée.

## 12. L'écran E11 — constructeur de règle

Le fiscaliste n'est pas informaticien. L'écran ne montre **aucune syntaxe technique, aucun
code, aucune expression à taper** : constructeur visuel de blocs `ET` / `OU`, chaque bloc
proposant un champ, un opérateur et une valeur pouvant être un paramètre du référentiel.

Une **traduction en langage naturel s'affiche en permanence** sous le constructeur :

> « Si le montant TTC est supérieur ou égal au seuil espèces ET que le mode de règlement est
> Espèces, alors la TVA n'est pas déductible. »

Le JSONLogic est le format de stockage, jamais l'interface.
