# Dossier d'architecture — Plateforme CGA Broad Range Consulting Group

Documentation de conception de la plateforme. À lire dans l'ordre.

| Fichier | Contenu |
|---|---|
| [00-vision-et-metier.md](00-vision-et-metier.md) | Ce qu'est un CGA, pourquoi cela change la conception, acteurs à modéliser |
| [01-contextes-bornes.md](01-contextes-bornes.md) | Découpage en onze contextes autonomes A → K |
| [02-referentiel-normatif.md](02-referentiel-normatif.md) | Le contexte pivot : paramètres légaux datés, barèmes, textes |
| [03-moteur-conformite.md](03-moteur-conformite.md) | Moteur de règles de facture, sévérités, conséquences fiscales |
| [04-modele-donnees.md](04-modele-donnees.md) | Entités, invariants, immutabilité comptable |
| [05-securite-multitenant.md](05-securite-multitenant.md) | Cloisonnement, RBAC, audit inaltérable, rétention |
| [06-phases-et-sequencement.md](06-phases-et-sequencement.md) | Les six phases, ce qui est fait, ce qui reste |
| [07-inventaire-ecrans.md](07-inventaire-ecrans.md) | E00 à E13, correspondance avec les maquettes livrées |
| [08-glossaire.md](08-glossaire.md) | Vocabulaire métier à employer sans traduction |
| [09-questions-ouvertes.md](09-questions-ouvertes.md) | Ce qui doit être tranché par le cabinet |

## Sources

Trois documents fondent cette architecture, par ordre d'autorité décroissante :

1. **Le dossier de design v1.0** (`§ 0` à `§ 14`), présent dans le projet Claude Design
   distant sous `uploads/dossier-design-CGA-pour-claude-design.md`. Fait autorité sur le
   vocabulaire, les formats, les écrans et le design system.
2. **Le document de cadrage** transmis en session 1, repris ici. Fait autorité sur le
   découpage fonctionnel et les principes d'architecture.
3. **Les maquettes** de `Docs/` : bibliothèque de composants, parcours comptable, réviseur,
   direction, espace adhérent, prototype cliquable.

Trois cahiers des charges PDF existent dans le projet distant et **n'ont pas encore été
dépouillés**. Voir `JOURNAL.md`.

## Avertissement méthodologique

> Aucune valeur légale citée dans ce dossier — taux, seuil, délai, pénalité — ne doit être
> considérée comme exacte. Toutes proviennent de sources secondaires. Elles illustrent la
> **structure** du système. Chacune doit être validée sur le Code Général des Impôts en
> vigueur et la loi de finances de l'année par le fiscaliste du cabinet avant mise en
> production, et la référence conservée dans le système.
>
> C'est précisément pourquoi le principe d'architecture n° 1 est : **aucune valeur légale en
> dur dans le code**.
