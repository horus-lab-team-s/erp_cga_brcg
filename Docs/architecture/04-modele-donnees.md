# 04 · Modèle de données

Schéma de référence : les modèles SQLAlchemy de `Backend_erp_cga/app/contexts/*/modeles_sql.py`.
Ce document en donne la lecture métier et les invariants qui ne se lisent pas dans le schéma.

> Ce modèle est une **hypothèse**. Les ateliers de cadrage avec le cabinet (matrice RACI,
> cartographie des processus réels) n'ont pas eu lieu. Voir
> [09-questions-ouvertes.md](09-questions-ouvertes.md).

## 1. Les quatre invariants

### I1 · Cloisonnement systématique

Chaque table métier porte `tenantId` et, quand elle est rattachée à un dossier,
`entrepriseId`. Le filtrage est appliqué **au niveau de la couche de persistance**, jamais
laissé à la charge du développeur qui écrit la requête. Un oubli ne doit pas pouvoir exposer
les données fiscales d'un autre adhérent.

Le CGA est le tenant, ses adhérents sont des sous-entités. Cette conception anticipe la
revente de la plateforme à d'autres CGA.

### I2 · Toute donnée légale est datée

Régime fiscal, rattachement fiscal, adhésion, paramètre, règle : jamais un attribut, toujours
un intervalle `[dateDebut, dateFin[` avec le motif du changement. Une lecture se fait
toujours *à une date*.

### I3 · Immutabilité comptable

Une `EcritureComptable` validée n'est plus modifiable. Correction par **contre-passation**
uniquement, avec motif et lien vers l'écriture d'origine. Aucune suppression physique nulle
part dans le domaine comptable.

### I4 · Traçabilité de bout en bout

`PieceJustificative → RapportConformite → Constat → LigneEcriture (attribut fiscal) →
LigneDeclaration → PosteLiasse`. Chaque maillon porte l'identifiant du précédent. La direction
doit pouvoir remonter d'une ligne de réintégration de la DSF jusqu'à la photo de la facture.

## 2. Entités par contexte

### B · Portefeuille

| Entité | Points d'attention |
|---|---|
| `Entreprise` | NIU, RCCM, forme juridique, activité, siège, établissements |
| `Exercice` | **Exercices décalés et premier exercice long** : `dateOuverture` / `dateCloture` libres, pas de présomption d'année civile |
| `RegimeFiscal` | Historisé. `IGS` / `REEL`. Motif : adhésion, dépassement de seuil, reclassement automatique, option |
| `RattachementFiscal` | Historisé. `CDI` / `CIME` / `DGE`. Détermine les dates limites de dépôt |
| `Adhesion` | Date d'effet — **fiscalement porteuse** : elle ouvre l'abattement |
| `MandatDeclaratif` | Ce que le CGA fait au nom de l'adhérent. Objet juridique, pas administratif |
| `Dirigeant`, `Associe`, `Tiers` | Les tiers incluent clients et fournisseurs de l'adhérent |

**La période probatoire.** En cas de dépassement de seuil, le reclassement est automatique,
mais un retour éventuel à l'IGS suppose deux exercices probatoires. Le modèle doit porter
cette notion, sinon la détection de dépassement produira des faux positifs chaque année.

### C · Collecte

`PieceJustificative` — cycle `RECUE → LUE → RAPPROCHEE → COMPTABILISEE → ARCHIVEE`, canal
(`PORTAIL`, `MOBILE`, `WHATSAPP`, `COURRIEL`), empreinte du fichier, **score de confiance de
l'extraction champ par champ**. `DemandePiece` et `Relance` pour le suivi des manquantes.

### D · Conformité

`RegleConformite` (versionnée), `RapportConformite` (une facture à une date, avec la liste des
paramètres résolus et leurs valeurs), `Constat`, `Derogation` (motif, pièce d'appui, auteur,
enjeu levé).

Un rapport est **immuable** : réévaluer une facture produit un nouveau rapport, jamais une
mise à jour de l'ancien. C'est ce qui rend la décision d'un comptable défendable six mois
plus tard.

### E · Comptabilité SYSCOHADA

`Journal`, `EcritureComptable`, `LigneEcriture`, `Compte`, `Lettrage`,
`RapprochementBancaire`.

- Numérotation chronologique **continue par journal et par exercice**. Un trou est une
  anomalie.
- Équilibre débit / crédit vérifié au niveau de l'écriture, pas de la ligne.
- Chaque écriture porte `pieceJustificativeId`.
- Chaque ligne peut porter des **attributs fiscaux** : `tvaDeductible`,
  `motifNonDeductibilite`, `montantAReintegrer`, `constatOrigineId`.
- **Plan de comptes dérivé** : `Compte.compteReferenceId` pointe vers le plan OHADA. Le
  mapping DSF se fait sur la référence, jamais sur le sous-compte.

### F · Obligations

`TypeObligation` (périodicité, formule d'échéance, régimes et centres concernés),
`ObligationInstance` (statut `A_FAIRE / EN_PREPARATION / PRETE / DECLAREE / PAYEE /
EN_RETARD`), `Declaration`, `Paiement`, `Penalite`.

**La date d'échéance est calculée**, jamais figée : elle dépend du type d'obligation, du
centre de rattachement et de la date de clôture de l'exercice. Le 15 mars de la DSF n'est pas
une constante mais le résultat d'une formule sur un exercice clos au 31 décembre.

### K · Transverse

`Tenant`, `Utilisateur`, `Role`, `Permission`, `AffectationPortefeuille`, `Document` (GED,
empreinte, rétention 10 ans), `JournalAudit`, `Notification`, `Honoraire`, `FactureCabinet`.

## 3. Le journal d'audit

Append-only, aucune mise à jour, aucune suppression. Chaque entrée : horodatage, acteur,
action, objet, valeurs avant et après, empreinte de l'entrée précédente.

Le **chaînage par hachage** rend toute altération détectable. C'est un argument fort face à
la DGI, et un coût d'implémentation faible si on le prévoit dès le départ. Le rajouter après
coup est impossible sans réécrire l'historique — donc sans détruire précisément la garantie
recherchée.

## 4. Conservation

Documents comptables : **10 ans**. Le modèle porte une date de purge calculée, jamais une
suppression manuelle. Les documents sortis de rétention sont purgés par un traitement
journalisé, pas effacés à la main.
