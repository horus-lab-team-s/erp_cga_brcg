# 02 · Référentiel normatif

Le contexte pivot. Tout le reste en dépend.

## 1. Le principe non négociable

> **Aucune valeur légale en dur dans le code. Aucune lecture de paramètre sans date.**

```python
# Interdit
tva = montant_ht * Decimal("0.1925")

# Obligatoire
taux = parametres.valeur_numerique("TVA_TAUX_GENERAL", facture.date_emission)
tva = montant_ht * taux / Decimal(100)
```

Une facture de 2024 se contrôle avec les règles de 2024. Le référentiel est donc une
**fonction du temps**, pas une table de constantes.

## 2. Le modèle

Un `ParametreFiscal` est identifié par son `code` et possède une ou plusieurs **versions**,
chacune valide sur un intervalle `[applicableDu, applicableAu[` — borne haute exclue,
`applicableAu: null` signifiant « toujours en vigueur ».

```yaml
- code: TVA_TAUX_GENERAL
  libelle: Taux général de la TVA, centimes additionnels communaux inclus
  categorie: TVA
  unite: POURCENTAGE
  versions:
    - valeur: 19.25
      applicableDu: 2019-01-01
      applicableAu: null
      statut: A_VALIDER
      fondement:
        texte: CGI, taux de 17,5 % majoré de 10 % de centimes additionnels communaux
        source: Documentation DGI
      note: Décomposition à confirmer ; certaines sources traitent le CAC séparément.
```

Trois éléments sont **obligatoires sur chaque version** :

| Champ | Pourquoi |
|---|---|
| `applicableDu` | Sans date d'effet, le paramètre est inutilisable |
| `fondement` | Sans fondement, on ne saura pas quoi mettre à jour à la loi de finances suivante, ni justifier un rejet à un adhérent mécontent |
| `statut` | `A_VALIDER` tant que le fiscaliste n'a pas confirmé sur le texte officiel ; `VALIDE` ensuite, avec `valideLe` et `validePar` |

Le statut `A_VALIDER` n'empêche pas le calcul : il le **marque**. Un rapport de conformité
produit à partir d'un paramètre non validé le signale. C'est ce qui permet de livrer sans
attendre la validation juridique complète, sans pour autant faire croire à une exactitude
qui n'existe pas.

## 3. Où vivent les paramètres

| Étape | Emplacement | Édition |
|---|---|---|
| Aujourd'hui | `Docs/referentiel/parametres.yaml`, chargé au démarrage | Fichier versionné en Git |
| Cible | Table `parametre_fiscal` en PostgreSQL | Back-office fiscaliste, avec journalisation |

Le fichier YAML est la **source d'amorçage** ; le format est identique en base. Le service
de lecture ne connaît pas l'origine.

## 4. Le service de lecture

```python
parametres.valeur_numerique("SEUIL_ESPECES_DEDUCTIBILITE_TVA", date_operation)
parametres.resoudre("SEUIL_ESPECES_DEDUCTIBILITE_TVA", date_operation)
# → ParametreResolu(code, valeur, unite, applicable_du, statut, fondement)
```

`resoudre` rend la version **et son contexte**. C'est cette forme que le moteur de conformité
emploie, afin de conserver dans le rapport la valeur exacte utilisée et sa date d'effet. Un
rapport de juillet 2026 reste reproductible même si le seuil change en janvier 2027.

Une lecture sans version applicable à la date demandée lève une erreur. Elle ne rend jamais
`undefined` ni une valeur par défaut : une valeur légale silencieusement absente est un bug
fiscal.

## 5. Autres objets du référentiel

| Objet | Rôle | État |
|---|---|---|
| `ParametreFiscal` | Taux, seuils, délais, seuils de régime | **Implémenté** |
| `RegleConformite` | Règles de contrôle de facture | **Implémenté**, voir [03](03-moteur-conformite.md) |
| `Bareme` / `TrancheBareme` | IGS par classes, IRPP progressif, patente | À faire |
| `TypeObligation` | Code, périodicité, formule d'échéance, régimes et centres concernés | À faire |
| `PlanComptableReference` | Plan OHADA importable et versionnable | À faire |
| `MappingPosteDSF` | Balance → postes de la liasse | À faire |
| `TexteLegal` | Loi de finances, article CGI, circulaire | Réduit à un champ `fondement` pour l'instant |

### Plan comptable : une précision de conception

Chaque adhérent peut avoir un **plan de comptes dérivé** — ses propres sous-comptes —
rattaché au plan OHADA de référence. Le mapping vers les postes de la DSF se fait sur le
**compte de référence**, jamais sur le sous-compte. Sans cela, chaque nouveau sous-compte
créé par un comptable casserait la liasse.

## 6. Ce que le référentiel contient aujourd'hui

Voir `Docs/referentiel/parametres.yaml`. Quinze paramètres couvrant la TVA, les seuils de
déductibilité, les régimes, les délais déclaratifs, les pénalités et les formats
d'identifiant.

**Tous sont au statut `A_VALIDER`.** Aucun n'a été confirmé sur le Code Général des Impôts.
Ils proviennent du document de cadrage, du dossier de design et des maquettes — c'est-à-dire
de sources secondaires. Le paramètre `SEUIL_ESPECES_DEDUCTIBILITE_TVA` porte même deux
valeurs contradictoires selon la source ; voir
[09-questions-ouvertes.md](09-questions-ouvertes.md), question Q1.

## 7. Le rôle de référent de validation

Le cabinet doit **nommer** une personne responsable de la validation des règles et
paramètres fiscaux. Ce rôle est la protection juridique du projet : c'est lui qui engage
l'exactitude des valeurs, pas l'éditeur. Chaque version validée porte `validePar` et
`valideLe`.
