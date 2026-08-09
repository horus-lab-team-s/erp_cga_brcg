# 01 · Contextes bornés

Découpage en contextes métier autonomes communiquant par événements. Le projet démarre en
**monolithe modulaire** — un package Python par contexte — mais les frontières restent nettes.
Pas de microservices : l'équipe est réduite et le besoin de scalabilité n'existe pas.

```
┌─────────────────────────────────────────────────────────────────┐
│  A. RÉFÉRENTIEL NORMATIF (rulebook fiscal et comptable)          │
│     Le noyau. Versionné dans le temps. Alimente tous les autres. │
└─────────────────────────────────────────────────────────────────┘
        │              │              │              │
┌───────▼───────┐ ┌────▼────────┐ ┌───▼──────────┐ ┌─▼──────────────┐
│ B. Portefeuille│ │ C. Collecte │ │ D. Conformité│ │ E. Comptabilité│
│    adhérents   │ │  de pièces  │ │ documentaire │ │   SYSCOHADA    │
└────────────────┘ └─────────────┘ └──────────────┘ └────────────────┘
        │                                │                │
┌───────▼──────────┐  ┌──────────────────▼───┐  ┌────────▼─────────┐
│ F. Obligations et│  │ G. Social / Paie      │  │ H. Clôture et DSF│
│    déclarations  │  │    (CNPS, DIPE)       │  │                  │
└──────────────────┘  └───────────────────────┘  └──────────────────┘

┌──────────────────┐  ┌───────────────────────┐  ┌──────────────────┐
│ I. Création      │─▶│ J. Pilotage CGA       │  │ K. Transverse    │
│    d'entreprise  │  │  (KPI, charge, risque)│  │ IAM, GED, audit, │
│  (produit d'appel)│ └───────────────────────┘  │ notif, honoraires│
└──────────────────┘                             └──────────────────┘
```

Chaque contexte correspond à un package `Backend_erp_cga/app/contexts/<nom>/`, expose sa
surface publique dans `api.py`, et n'importe des autres que leur `api.py`.

Le graphe de dépendances autorisé est établi flux par flux dans
[10-flux-fonctionnels.md](10-flux-fonctionnels.md) et vérifié à chaque exécution des
tests par `Backend_erp_cga/tests/test_architecture.py`.

---

## A · Référentiel normatif — le contexte pivot

C'est ici que se joue la pérennité du produit. Chaque loi de finances modifie taux, seuils et
règles. Si ces éléments sont dispersés dans le code, la plateforme est morte en trois ans.

Entités : `ParametreFiscal`, `Bareme` / `TrancheBareme`, `TypeObligation`, `RegleConformite`,
`PlanComptableReference`, `MappingPosteDSF`, `TexteLegal`.

**Principe non négociable** : toute lecture de paramètre se fait à une date donnée.
`parametres.valeur_numerique('TVA_TAUX_GENERAL', date_operation)`. Une facture de 2024 se contrôle
avec les règles de 2024.

Détail : [02-referentiel-normatif.md](02-referentiel-normatif.md). **Implémenté.**

## B · Portefeuille adhérents

`Entreprise` (dénomination, forme juridique, NIU, RCCM, capital, activité, siège,
établissements), `Dirigeant`, `Associe`, `Exercice` (attention aux exercices décalés et au
premier exercice long), `RattachementFiscal` (CDI / CIME / DGE, historisé), `RegimeFiscal`
(historisé), `Adhesion`, `MandatDeclaratif` — ce que le CGA fait au nom de l'adhérent, objet
juridiquement important.

Le régime est un **statut daté**, pas un attribut : `dateDebut`, `dateFin`, motif du
changement. Le reclassement automatique en cas de dépassement de seuil et la période
probatoire de deux exercices sont un cas d'usage à part entière.

## C · Collecte de pièces

Le point de friction réel. Quatre canaux prévus : portail web, PWA mobile avec mode hors
ligne, **WhatsApp Business API** — le plus réaliste pour beaucoup de TPE —, import de relevés
bancaires et d'historiques Mobile Money.

`PieceJustificative` avec cycle de vie `Reçue → Lue → Rapprochée → Comptabilisée → Archivée`,
`DemandePiece` avec relance automatique, extraction OCR assortie d'un **score de confiance**
et d'une validation humaine.

## D · Conformité documentaire

Le moteur de règles de facture. Détail : [03-moteur-conformite.md](03-moteur-conformite.md).
**Implémenté.**

## E · Comptabilité SYSCOHADA

`Journal`, `EcritureComptable`, `LigneEcriture`, `Compte`, `Balance`, `GrandLivre`,
`Lettrage`, `RapprochementBancaire`, `Amortissement`, `Provision`, `EcritureInventaire`.

Règles structurantes : équilibre débit/crédit au niveau de l'écriture ; numérotation
chronologique continue par journal et par exercice ; **aucune modification après validation**,
contre-passation motivée uniquement ; chaque écriture porte l'identifiant de la pièce
justificative ; chaque ligne peut porter des **attributs fiscaux** (TVA déductible ou non,
motif, montant à réintégrer).

## F · Obligations et déclarations

Moteur d'échéancier : à partir du profil de l'adhérent — régime, rattachement, activité,
présence de salariés, assujettissement TVA — il génère automatiquement le calendrier de
l'exercice.

`ObligationInstance` (statut `À faire / En préparation / Prête / Déclarée / Payée / En
retard`), `Declaration`, `Paiement`, `Penalite`. Deux vues indispensables : échéancier
consolidé du portefeuille (cabinet) et « mes échéances » (adhérent). Relances J-15, J-7, J-2,
J+1.

## G · Social et paie

Phase 6. Bulletins, IRPP sur salaires, cotisations CNPS, génération du DIPE, avantages en
nature à barème forfaitaire.

## H · Clôture et DSF

Travaux de fin d'exercice, balance définitive, **mapping balance → postes de la liasse**
(Système Normal ou Système Minimal de Trésorerie selon la taille), **tableau de passage du
résultat comptable au résultat fiscal** — c'est là qu'atterrissent les factures marquées non
conformes par le contexte D ainsi que l'abattement CGA —, contrôles de cohérence inter-états,
génération du fichier de dépôt et archivage de l'accusé.

## I · Création d'entreprise — le produit d'appel

À traiter comme un vrai tunnel :
`Prospect → Qualification → Devis → Constitution → Dépôt CFCE → Suivi (RCCM, NIU, patente,
CNPS) → Livraison → Conversion en adhérent`.

Checklist de pièces dynamique selon la forme juridique (ETS, SARL, SARLU, SAS, SA) — **même
moteur de règles que le contexte D, autre jeu de règles**. Vérification de disponibilité du
nom, génération assistée des statuts, suivi des délais.

Tout l'intérêt est dans la conversion : le jour où le RCCM et le NIU sont obtenus,
l'entreprise bascule dans le portefeuille **avec son calendrier d'obligations déjà généré**.

## J · Pilotage CGA

Charge par collaborateur, complétude des dossiers, dossiers à risque avec **score décomposé
et traçable jusqu'à la pièce**, retards, rentabilité par adhérent, dossier de gestion à
restituer à l'adhérent au titre de la mission d'assistance.

La pondération des composantes du score appartient à la direction : elle se règle au
référentiel, pas dans le code.

## K · Transverse

Multi-tenant (cabinet → adhérents), RBAC fin, **journal d'audit inaltérable**, GED avec
conservation 10 ans, notifications multicanal (courriel, SMS, WhatsApp) et — à ne pas oublier
— la **facturation des honoraires du CGA lui-même**, qui doit être conforme aux mêmes règles
que celles qu'il contrôle.

Détail : [05-securite-multitenant.md](05-securite-multitenant.md).

---

## Ports et adaptateurs

Toutes les intégrations passent derrière une interface abstraite, avec **systématiquement un
mode manuel de secours**.

| Port | Adaptateur initial | Adaptateur cible |
|---|---|---|
| `FiscalInvoiceGateway` | PDF / manuel | e-facturation DGI, dès publication des spécifications |
| `NiuVerificationPort` | Saisie manuelle + cache | Portail DGI |
| `TeledeclarationPort` | Dépôt manuel + archivage de l'accusé | Portail DGI |
| `CnpsPort` | Manuel | Télédéclaration DIPE |
| `PaiementMobilePort` | Justificatif photographié | MTN MoMo, Orange Money |
| `RelevesBancairesPort` | Import de fichier | API bancaires |
| `NotificationPort` | Courriel | SMS, WhatsApp Business API |

Le port `FiscalInvoiceGateway` est à concevoir **dès maintenant**, avec les champs qui seront
exigés — identifiant unique de transmission, horodatage, statut de validation par
l'administration, empreinte — même si l'implémentation reste manuelle. La LF 2026 institue la
facturation électronique et le déploiement commence par les grandes entreprises au réel.
