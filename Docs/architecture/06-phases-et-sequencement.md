# 06 · Phases et séquencement

## Vue d'ensemble

| Phase | Objet | État |
|---|---|---|
| **0** | Cadrage métier | **Partielle** — documentation faite, ateliers non tenus |
| **1** | Socle : référentiel normatif, portefeuille, IAM, GED, audit | **En cours** — référentiel et conformité livrés |
| **2** | Création d'entreprise, le produit d'appel | À faire |
| **3** | Collecte + moteur de conformité en production | Moteur livré, collecte à faire |
| **4** | Comptabilité + obligations déclaratives | À faire |
| **5** | Clôture et DSF | À faire |
| **6** | Paie / CNPS, pilotage, e-facturation DGI | À faire |

---

## Phase 0 — Cadrage métier

**Quatre à six semaines, à ne pas compresser.** Ateliers avec le fiscaliste et les
comptables.

| Livrable | État |
|---|---|
| Glossaire métier partagé | **Fait** — [08-glossaire.md](08-glossaire.md) |
| Matrice RACI par processus | **Non fait** — demande trois à quatre ateliers |
| Cartographie des processus actuels | **Non fait** |
| Catalogue initial de règles avec fondement légal | **Amorcé** — 5 règles sur les 15 à 20 visées |
| Jeu de données réel anonymisé pour les tests | **Non fait** — seul le jeu fictif du § 13 existe |

> Les responsabilités ne se déduisent pas des textes. La façon dont *ce* CGA travaille est ce
> qu'il faut outiller. Tant que les ateliers n'ont pas eu lieu, le modèle de données reste une
> hypothèse.

## Phase 1 — Socle

Sans valeur visible pour l'utilisateur, mais rien ne tient sans lui.

| Brique | État |
|---|---|
| Référentiel normatif — paramètres datés | **Fait** |
| Moteur de règles de conformité | **Fait** |
| Portefeuille adhérents | À faire |
| IAM, RBAC, multi-tenant | À faire |
| GED | À faire |
| Journal d'audit chaîné | À faire |
| Jetons du design system | **Fait** |

## Phase 2 — Le produit d'appel

Module création d'entreprise, avec **conversion automatique en adhérent**. C'est ce qui fera
adopter la plateforme par le cabinet en premier, et c'est le module le moins risqué
techniquement : peu de droit fiscal, beaucoup de suivi de dossier.

## Phase 3 — Collecte et conformité en production

Le cas d'usage phare. Portail, PWA hors ligne, WhatsApp, OCR avec score de confiance.

> Démarrer avec **quinze à vingt règles solides et bien fondées** plutôt que quatre-vingts
> approximatives. Une règle mal calibrée qu'on écarte à 68 % — cas de `FAC-VRA-005` dans le
> jeu de démonstration — coûte plus cher qu'une règle absente : elle use la confiance du
> réviseur.

## Phase 4 — Comptabilité et obligations

Le cœur lourd. Balance, grand livre, lettrage, rapprochement, échéancier, TVA mensuelle.

## Phase 5 — Clôture et DSF

**À caler impérativement hors de la période janvier–mars**, qui est le pic de charge du
cabinet.

## Phase 6 — Paie, pilotage, e-facturation

Le port `FiscalInvoiceGateway` est conçu dès la phase 1 avec ses champs cibles, même si son
implémentation reste manuelle : le jour où la DGI publie ses spécifications, on branche un
adaptateur sans toucher au domaine.

---

## Ce qui déclenche un jalon

Trois conditions bloquantes, indépendantes du calendrier :

1. **Les cahiers des charges PDF doivent être dépouillés** avant d'aller plus loin que le
   socle. Ils peuvent contenir des exigences contractuelles contredisant le cadrage.
2. **Un référent de validation des règles fiscales doit être nommé** chez le client avant
   toute mise en production. Aucun paramètre au statut `A_VALIDER` ne doit produire un chiffre
   opposable.
3. **Les wireframes doivent être validés par la direction du cabinet avant développement des
   écrans.** Un wireframe se corrige en dix minutes, un écran développé en trois jours.
