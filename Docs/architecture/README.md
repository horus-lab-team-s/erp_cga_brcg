# Dossier d'architecture — Plateforme CGA Broad Range Consulting Group

Documentation de conception de la plateforme. À lire dans l'ordre.

| Fichier | Contenu |
|---|---|
| [00-vision-et-metier.md](00-vision-et-metier.md) | Ce qu'est un CGA, pourquoi cela change la conception, acteurs à modéliser |
| [01-contextes-bornes.md](01-contextes-bornes.md) | Découpage en quatorze contextes autonomes A → N |
| [02-referentiel-normatif.md](02-referentiel-normatif.md) | Le contexte pivot : paramètres légaux datés, barèmes, textes |
| [03-moteur-conformite.md](03-moteur-conformite.md) | Moteur de règles de facture, sévérités, conséquences fiscales |
| [04-modele-donnees.md](04-modele-donnees.md) | Entités, invariants, immutabilité comptable |
| [05-securite-multitenant.md](05-securite-multitenant.md) | Cloisonnement, RBAC, audit inaltérable, rétention |
| [06-phases-et-sequencement.md](06-phases-et-sequencement.md) | Les six phases, ce qui est fait, ce qui reste |
| [07-inventaire-ecrans.md](07-inventaire-ecrans.md) | E00 à E13, correspondance avec les maquettes livrées |
| [08-glossaire.md](08-glossaire.md) | Vocabulaire métier à employer sans traduction |
| [09-questions-ouvertes.md](09-questions-ouvertes.md) | Ce qui doit être tranché par le cabinet |
| [10-flux-fonctionnels.md](10-flux-fonctionnels.md) | Audit de couverture : chaque parcours des maquettes confronté au découpage. **Source du graphe de dépendances** |
| [11-generalisation-du-moteur.md](11-generalisation-du-moteur.md) | Journal du chantier qui détache le moteur de règles du contexte Conformité pour en faire un noyau partagé. **Ordre chronologique croissant** |
| [12-socle-multi-tenant.md](12-socle-multi-tenant.md) | Journal du chantier qui fait passer la plateforme au multi-tenant : slug, schéma par tenant, passerelle, mandat. **Ordre chronologique croissant** |
| [13-parcours-d-acquisition.md](13-parcours-d-acquisition.md) | Journal du chantier qui construit le chemin du formulaire déposé au paiement : demande de contact, consentement, dossier commercial et ses huit états. **Ordre chronologique croissant** |

## Le document de conception, et le site qui le sert

`document-de-conception/architecture-multitenant-cga.html` est la synthèse lisible de tout ce
dossier : le produit, les principes, la carte des services, le journal de construction pas à pas et
quatre annexes. C'est **la seule source** de ce document.

Il est servi de deux façons, et aucune des deux ne le recopie :

| Où | Comment |
|---|---|
| Artefact Claude | publié depuis ce fichier, une version par pas. Privé tant que le propriétaire ne l'ouvre pas depuis le menu *Partager* de la page. |
| [`Site_conception/`](../../Site_conception/README.md) | site Next.js déployable sur Vercel. Sa construction relit ce fichier et engendre la page servie. |

⚠️ Modifier le texte ailleurs que dans ce fichier crée une seconde version du document, et c'est
celle-là qui sera lue.

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
