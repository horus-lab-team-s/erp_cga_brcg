# Sources documentaires

Documents récupérés le 9 septembre 2026 pour la modélisation de la plateforme.

> **Aucun chiffre issu de ces documents ne doit porter le statut `VALIDE` dans le
> référentiel avant contreseing par le fiscaliste du centre.** Ils fixent la structure et
> donnent des valeurs de travail ; ils ne remplacent pas une lecture du texte en vigueur
> par une personne qui en répond.

## Ce qui a été récupéré

| Fichier | Pages | Autorité | Ce qu'il apporte |
|---|---:|---|---|
| `CMR-LF2026-mesures-fiscales-nouvelles.pdf` | 22 | **Officielle** — DGI, Division de la législation | Les mesures fiscales nouvelles de la loi de finances 2026. **Le document le plus utile du lot** : il dit ce qui a changé cette année. |
| `CMR-arrete-retenues-a-la-source-2026.pdf` | — | **Officielle** — arrêté MINFI | Les retenues à la source applicables en 2026. Directement exploitable pour la paie et pour les acomptes. |
| `CMR-charte-du-contribuable-2026.pdf` | 33 | **Officielle** — DGI, à jour au 01/01/2026 | Droits et obligations en contrôle fiscal, délais de procédure. Utile au contexte Fiscalité. |
| `CMR-repertoire-CGA-agrees.pdf` | — | **Officielle** — DGI, au 18/09/2025 | Le répertoire des centres de gestion agréés. Permet de vérifier l'agrément du centre. |
| `CMR-CGI-2014-reference.pdf` | 291 | Secondaire — **version 2014, périmée** | Le Code général des impôts complet. Sert de **référence de structure** (numérotation des articles, plan du code), jamais de source de valeurs. |
| `OHADA-AUDCIF-acte-uniforme.pdf` | 38 | **Officielle** — Acte uniforme du 26/01/2017 | Le texte juridique du droit comptable OHADA. Obligations de tenue, états financiers exigés, durées de conservation. |
| `OHADA-plan-de-comptes-SYSCOHADA.pdf` | 49 | Secondaire — éditeur tiers | Le plan de comptes, 8 classes. Porte les marqueurs de la version révisée (comptes `4454`, `1181`, classe 8 en autres charges et produits), mais **le document ne le déclare pas** : à confronter à l'édition officielle avant usage. |

## Ce qui manque encore, et qui doit venir du centre

Ces éléments n'ont pas d'équivalent public exploitable et figuraient déjà dans les
engagements pris en réunion.

| Élément | Pourquoi il bloque | Qui le fournit |
|---|---|---|
| **Spécifications du DIPE magnétique** | Format de fichier de la déclaration du personnel employé. Sans lui, le contexte Paie ne peut rien produire d'exploitable. | Le centre, ou l'organisme social |
| **Modèles d'états financiers par type d'entité** | Bilan, compte de résultat, tableaux de flux, dans la forme attendue à Douala. L'acte uniforme les nomme sans donner les maquettes. | Le centre |
| **Barème d'honoraires du centre** | La base du moteur de tarification. Aucun document public ne peut s'y substituer. | Le centre |
| **Grille de charge** | Critères, paliers et points de la matrice d'évaluation. | Le centre |
| **Proformas types** | Déjà partiellement reçues : 9 fichiers `.docx` dans le répertoire parent. | Reçu |
| **CGI 2026 relié** | La DGI annonce une édition 2026 sans exposer de PDF direct. Le document des mesures nouvelles en tient lieu pour les changements de l'année. | À demander au centre |

## Comment s'en servir

1. Toute valeur reprise dans `Docs/referentiel/parametres.yaml` porte son `source` :
   nom du fichier, page, et date de consultation.
2. Le statut reste `A_VALIDER` tant que `valide_par` et `valide_le` ne sont pas renseignés
   par une personne nommée.
3. Une valeur issue du `CGI-2014` est **par construction suspecte** : elle sert à écrire la
   structure, pas à produire un chiffre opposable.
