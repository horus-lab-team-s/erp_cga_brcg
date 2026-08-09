# 07 · Inventaire des écrans

Référence : § 7 et § 8 du dossier de design.

## Les quatorze écrans

| Réf. | Écran | Espace | Support | Priorité | Maquette livrée |
|---|---|---|---|---|---|
| E00 | Structure générale et navigation | Collaborateur | Bureau | 1 | `Wireframes CGA.dc.html` (distant) |
| **E02** | **Détail d'une pièce et rapport de conformité** | Collaborateur | Bureau | **1** | `Prototype cliquable CGA.html` |
| E03 | Boîte de réception des pièces | Collaborateur | Bureau | 2 | `Prototype cliquable CGA.html` |
| E06 | Accueil adhérent | Adhérent | Mobile d'abord | 2 | `Espace adherent CGA.html` |
| E07 | Dépôt d'un justificatif | Adhérent | Mobile | 2 | `Prototype cliquable CGA.html` |
| E01 | Tableau de bord collaborateur | Collaborateur | Bureau | 3 | — |
| E05 | Échéancier consolidé | Collaborateur | Bureau | 3 | — |
| E08 | File de synchronisation | Adhérent | Mobile | 3 | `Espace adherent CGA.html` |
| E09 | Mes échéances | Adhérent | Mobile | 3 | `Espace adherent CGA.html` |
| E04 | Fiche adhérent 360° | Collaborateur | Bureau | 4 | — |
| E13 | Pipeline création d'entreprise | Collaborateur | Bureau | 4 | — |
| E10 | Saisie et imputation comptable | Collaborateur | Bureau | 5 | `Prototype cliquable CGA.html` |
| E11 | Constructeur de règle de conformité | Fiscaliste | Bureau | 5 | — |
| E12 | Assistant de clôture et liasse | Collaborateur | Bureau | 5 | — |

Ordre de production recommandé par le dossier de design :
**E00, E02, E03, E01, E05, E06, E07, E08, E04, E10, E11, E12, E13.**

## E02 — l'écran le plus important du produit

> À concevoir en premier et soigner plus que tous les autres.

**Deux colonnes.** À gauche, environ 45 % : visionneuse du document, zoom, rotation,
ajustement. Quand un constat est sélectionné à droite, **la zone correspondante du document
est surlignée**.

À droite, environ 55 %, dans cet ordre exact :

1. **Bandeau de verdict** — gravité maximale rencontrée et conséquence fiscale chiffrée, en
   langage clair : « Anomalie majeure — TVA non déductible : 379 350 FCFA ».
2. **Données extraites** — fournisseur, NIU, RCCM, numéro, date, HT, TVA, TTC, mode de
   règlement. Chaque champ porte un **indice de confiance** ; les champs peu fiables sont
   signalés pour vérification. Tous sont modifiables.
3. **Liste des constats** — un par anomalie, dépliable, avec gravité, libellé, code,
   **référence légale**, message explicatif et consigne de régularisation.
4. **Actions** — valider et comptabiliser ; demander une facture rectificative ; écarter un
   constat avec motif obligatoire, réservé au réviseur.

**Contrainte forte** : la référence légale est visible sur chaque constat. C'est ce qui
distingue cet outil d'un validateur de formulaire, et ce qui permet au comptable de justifier
un rejet auprès d'un adhérent mécontent.

Trois variantes à produire : facture conforme, facture avec deux anomalies majeures, facture
avec une anomalie bloquante.

## Contraintes transversales

- **Tout tient en 1440 × 900 sans défilement** sur les écrans de production collaborateur.
- E03 : au moins 25 lignes visibles sans défilement, navigation complète au clavier.
- Chaque écran existe en état **vide, chargement, erreur**, et **hors ligne** sur mobile.
- E11 : aucune syntaxe technique visible, aucun code, aucune expression à taper — voir
  [03-moteur-conformite.md](03-moteur-conformite.md) § 12.

## Ce que les maquettes livrées couvrent en plus de l'inventaire

Les cinq maquettes de `Docs/` documentent des parcours par profil, plus larges que les fiches
d'écran :

| Maquette | Contenu |
|---|---|
| `Bibliotheque de composants CGA.html` | Jetons, typographie, gravité, actions, densité, formats, espacement |
| `Prototype cliquable CGA.html` | E03 → E02 → E10 côté bureau ; E06 → E07 côté mobile, avec coupure réseau simulée |
| `Parcours comptable CGA.html` | Plan de travail, rapprochement bancaire, grand livre, préparation TVA, contre-passation, relance, clôture mensuelle |
| `Parcours reviseur CGA.html` | File d'anomalies, traitement en masse par règle, journal des dérogations, revue de dossier, dépôt, qualité des règles |
| `Pilotage direction CGA.html` | Tableau de bord, vue risque avec score décomposé, charge et production, portefeuille et rentabilité, qualité et rapport mensuel |

Ces parcours introduisent des écrans absents de l'inventaire E00–E13 — journal des
dérogations, statistiques de règles, vue risque. Ils sont à intégrer à l'inventaire lors de
la prochaine révision du dossier de design.
