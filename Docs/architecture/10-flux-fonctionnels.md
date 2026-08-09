# 10 · Flux fonctionnels et couverture modulaire

Audit de couverture : chaque parcours des maquettes est confronté au découpage en
contextes. Objectif — vérifier qu'aucun flux n'est orphelin, et qu'aucune arête de
dépendance n'existe sans un flux qui la justifie.

Ce document est **la source du graphe** déclaré dans
`Backend_erp_cga/tests/test_architecture.py`. Ajouter une arête là-bas sans l'inscrire
ici, c'est perdre la trace du pourquoi.

---

## 1. Le graphe corrigé

```
                    ┌──────────────────┐
                    │ A · Référentiel  │  ne connaît personne
                    └────────▲─────────┘
                             │  socle, lisible par tous
                    ┌────────┴─────────┐
                    │ K · Transverse   │  IAM, audit, GED, notifications
                    └────────▲─────────┘
                             │
   ┌────────────┐   ┌────────┴─────────┐
   │ B · Porte- │◀──│ D · Conformité   │  fonction pure : facture + droit
   │  feuille   │   └────────▲─────────┘
   └─────▲──────┘            │
         │        ┌──────────┴─────────┐
         └────────│ C · Collecte       │  possède le cycle de vie de la pièce
                  └──────────▲─────────┘
                             │
                  ┌──────────┴─────────┐
                  │ E · Comptabilité   │
                  └──────────▲─────────┘
                             │
                  ┌──────────┴─────────┐    ┌──────────────────┐
                  │ F · Obligations    │    │ G · Social       │
                  └──────────▲─────────┘    └────────▲─────────┘
                             │                       │
                  ┌──────────┴─────────┐    ┌────────┴─────────┐
                  │ H · Clôture / DSF  │    │ I · Création     │
                  └──────────▲─────────┘    └────────▲─────────┘
                             │                       │
                        ┌────┴───────────────────────┴────┐
                        │ J · Pilotage — puits, lu par    │
                        │ personne                        │
                        └─────────────────────────────────┘
```

Trois invariants, tous vérifiés par les tests :

| Invariant | Pourquoi |
|---|---|
| **A ne dépend de rien** | Le noyau normatif doit rester réutilisable et testable isolément. La mise à jour annuelle de la loi de finances ne doit pas être un chantier transverse. |
| **J n'est lu par personne** | Le pilotage agrège. Si un contexte métier venait à le lire, c'est qu'un indicateur y aurait pris une valeur métier : il faudrait le redescendre chez son responsable. |
| **Le graphe est acyclique** | Deux contextes qui s'appellent mutuellement n'en font qu'un, mal découpé. Le remède est un événement ou un déplacement de responsabilité, jamais une arête de plus. |

**Règle de dialogue.** Un contexte n'importe que `app.contexts.<autre>.api`, jamais un
module interne. C'est ce qui permet de réorganiser l'intérieur d'un contexte sans casser
les dix autres.

---

## 2. Couverture des parcours

### Prototype cliquable — le parcours phare

| Étape | Contexte propriétaire | Contextes lus | État |
|---|---|---|---|
| Liste des pièces reçues, filtres, canal (E03) | **C** Collecte | B, D | Moteur ✅, collecte 🔲 |
| Rapport de conformité, constats, référence légale (E02) | **D** Conformité | A | ✅ **Implémenté** |
| Une pièce bloquante refuse la comptabilisation | **D** décide, **E** applique | — | ✅ Règle en place |
| Demande de facture rectificative → portail + WhatsApp | **C** Collecte | K notifications | 🔲 |
| Saisie, imputation, attribut fiscal hérité (E10) | **E** Comptabilité | D, C | 🔲 |
| Dépôt mobile, mode hors ligne, file d'attente (E06, E07) | **C** Collecte | — | 🔲 |

> La chaîne « constat → attribut fiscal sur la ligne → TVA du mois → réintégration DSF »
> est **la** proposition de valeur du produit. Elle traverse D → E → F → H. C'est la
> raison pour laquelle ces quatre arêtes existent.

### Parcours comptable

| Flux | Propriétaire | Lit | Arête requise |
|---|---|---|---|
| A · Mon plan de travail | *voir § 3* | C, D, E, F, K | ⚠️ **Décision ouverte** |
| B · Rapprochement bancaire | **E** | C — relevés importés | ✅ `comptabilite → collecte` |
| C · Grand livre et balance | **E** | A plan de comptes | ✅ |
| D · Préparation d'une déclaration de TVA | **F** | E balance, **D** TVA rejetée, C complétude | ✅ `obligations → conformite`, `obligations → collecte` |
| E · Contre-passation et plan de comptes | **E** | A | ✅ |
| F · Relance des pièces manquantes | **C** | K notifications multicanal | ✅ socle |
| G · Clôture mensuelle d'un dossier | **E** | C complétude, D anomalies ouvertes | ✅ |

La ligne **L24 « TVA rejetée par le contrôle de conformité — (591 750) »** de la maquette
est ce qui impose `obligations → conformite`. Sans cette arête, le moteur de conformité
produirait des constats que personne ne consommerait : le produit perdrait sa valeur.

### Parcours réviseur

| Flux | Propriétaire | Lit | Arête requise |
|---|---|---|---|
| A · File d'anomalies du portefeuille | **D** | B, C | ✅ |
| B · Écarter des constats en masse | **D** | K audit | ✅ socle |
| C · Journal des dérogations | **D** | K audit | ✅ socle |
| D · Revue d'un dossier transmis | **E** | C, D | ✅ |
| E · Validation et dépôt d'une déclaration | **F** | D contrôles, K port de télédéclaration et archivage de la preuve | ✅ socle |
| F · Qualité des règles | **J** | D statistiques de constats | ✅ |

**Écarter un constat** engage la signature du Centre : motif obligatoire, pièce d'appui
attendue, inscription au journal des dérogations. La dérogation appartient à **D**, sa
trace inaltérable à **K**.

### Pilotage direction

| Flux | Propriétaire | Lit |
|---|---|---|
| A · Tableau de bord, cinq indicateurs | **J** | tous |
| B · Vue Risque, score décomposé et traçable | **J** | D, C, F, B |
| C · Charge et production, réaffectations | **J** | K affectations, E, F |
| D · Portefeuille et rentabilité, impayés | **J** | B, I, K honoraires |
| E · Qualité, dérogations, rapport mensuel | **J** | D, K audit |

`pilotage → creation_entreprise` répond à UC10 : « où en est le pipeline de créations et
sa conversion en adhésions ». La maquette affiche « 9 entrées ce trimestre dont 5 issues
de la création d'entreprise ».

La **pondération des cinq composantes du score** appartient à la direction et se règle au
référentiel, pas dans le code — voir question Q9.

### Espace adhérent

| Flux | Propriétaire | Lit |
|---|---|---|
| A · Accès au compte, code à quatre chiffres | **K** IAM | — |
| B · Ce qu'on attend de moi | *voir § 3* | C, F, K |
| C · Mes justificatifs, refus, correction | **C** | D motif du refus |
| D · Échéances et paiement Mobile Money | **F** | K port de paiement |
| E · Mes documents | **K** GED | F déclarations, H DSF |
| F · Réglages, Wi-Fi seulement, notifications | **K** | — |

---

## 3. La décision qui reste ouverte — les surfaces d'agrégation

Trois écrans ne sont **la propriété d'aucun contexte** parce qu'ils n'ont pas de métier
propre : ils composent ce que plusieurs contextes savent déjà.

| Écran | Ce qu'il agrège |
|---|---|
| Plan de travail du comptable | Pièces (C), écritures (E), déclarations (F), anomalies (D), affectations (K) |
| Accueil adhérent | Attentes (C), échéances (F), documents (K), entreprise (B), notifications (K) |
| Tableau de bord direction | Tout — mais celui-ci a un métier propre : le pilotage, donc **J** |

Les deux premiers n'ont pas d'équivalent de **J**. Deux réponses possibles :

**Option retenue par défaut — une couche de composition en lecture seule.**
Un paquet `app/api/vues/` au niveau de la façade HTTP, qui appelle plusieurs contextes par
leur `api.py` et assemble la réponse. **Aucune logique métier, aucune persistance, aucun
calcul.** S'il faut y écrire une règle, c'est que la règle appartenait à un contexte et
qu'on l'a laissée fuir.

Avantage : les contextes restent indépendants et ignorants les uns des autres.
Inconvénient : une requête d'accueil adhérent touche cinq contextes ; il faudra
probablement un cache, puis des vues matérialisées alimentées par événements.

**Option écartée — un douzième contexte « espace de travail ».**
Il deviendrait le fourre-tout que le test `test_aucun_paquet_hors_nomenclature` cherche
justement à empêcher, et il porterait du métier volé aux dix autres.

> **À confirmer avec le cabinet** avant de développer E01 et E06. En attendant, aucune de
> ces deux surfaces n'est implémentée, et le graphe n'en dépend pas.

---

## 4. Ce que l'audit a corrigé

Six arêtes manquaient au graphe initial. Chacune correspond à un flux visible dans les
maquettes, qui aurait été découvert au développement — au pire moment.

| Arête ajoutée | Flux qui l'impose |
|---|---|
| `collecte → conformite` | Le contrôle se déclenche à la réception d'une pièce |
| `comptabilite → collecte` | Rapprochement bancaire sur relevés importés ; lien pièce ↔ écriture |
| `obligations → conformite` | Ligne L24, TVA rejetée par le contrôle de conformité |
| `obligations → collecte` | Complétude du dossier affichée avant dépôt |
| `cloture → obligations` | La DSF est elle-même une obligation déclarative |
| `creation_entreprise → conformite` | Checklist de pièces par forme juridique : même moteur, autre jeu de règles |

Et deux garde-fous ont été ajoutés : la **surface publique obligatoire** (`api.py`) et
l'interdiction pour un contexte métier de **lire le pilotage**.

---

## 5. Ce que le graphe ne dit pas encore

Trois sujets à trancher avant la Phase 4, où les contextes lourds arrivent :

1. **Import direct ou événement ?** Le graphe autorise des imports directs. Pour les flux
   asynchrones — « une pièce a été comptabilisée », « une déclaration a été déposée » —
   un bus d'événements interne serait plus juste qu'un appel. À arbitrer quand E et F
   existeront réellement ; le faire avant serait de la spéculation.
2. **Transactions inter-contextes.** Comptabiliser une pièce touche C et E. Une seule
   transaction, ou une saga avec compensation ? Le monolithe permet la première ; il ne
   faut pas s'en priver tant qu'il tient.
3. **Le cloisonnement par portefeuille** — un comptable ne voit que ses dossiers — n'est
   pas dans le graphe : c'est un filtre de persistance transverse, pas une dépendance.
   Voir [05-securite-multitenant.md](05-securite-multitenant.md).
