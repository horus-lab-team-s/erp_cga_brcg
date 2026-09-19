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

┌──────────────────────────────────────────────────────────────────┐
│  L. VITRINE PUBLIQUE (contenu éditorial du site)                 │
│     Articles, annonces, institutions. Ne lit aucun autre         │
│     contexte, et n'est lu par aucun.                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  M. SOUSCRIPTION (offre, devis, encaissement, ouverture d'accès) │
│     Le seul contexte qui traverse la frontière entre le site     │
│     public et l'ERP : on y entre sans compte, on en sort avec.   │
└──────────────────────────────────────────────────────────────────┘
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

**La présence de salariés se lit au contexte G, période par période** (pas 56). F lit G
pour cette seule question, `a_employe_sur`, et la lecture ne bloque jamais : le social en
panne laisse l'échéancier entier, obligations sociales marquées « effectif à confirmer ».
Jusqu'au pas 56, la présence de salariés était un booléen faux par défaut, et la CNPS
n'apparaissait nulle part.

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

## L · Vitrine publique

Le contenu éditorial du site public : les articles du blog, l'annonce du bandeau, et les
institutions dans le cadre desquelles le cabinet exerce.

**Pourquoi un contexte, et pas des fichiers dans le frontend.** Le site est la première
chose qu'un prospect voit du cabinet. Son contenu vieillit — une offre expire, un texte
fiscal change, une faute se corrige — et il ne doit pas falloir un développeur et un
déploiement pour le tenir à jour. Le contenu appartient donc au backend, sous la même
discipline que le reste.

**Ce qu'il ne fait pas, et pourquoi c'est structurant.** La Vitrine ne lit aucun contexte
métier : ni le Référentiel, ni le Portefeuille. Du contenu qui aurait besoin d'un paramètre
légal ne serait plus du contenu, ce serait un calcul — et il appartiendrait au contexte qui
le porte. Le jour où l'on voudra afficher un barème sur le site, la bonne réponse sera une
route du Référentiel appelée par le site, pas une arête ajoutée au graphe.

Personne ne le lit non plus : le contenu éditorial n'a rien à dire au métier fiscal. C'est
le seul contexte, avec J · Pilotage, à être ainsi isolé — mais pour la raison inverse : J
agrège tout et n'est lu par personne, L ne lit rien et n'est lu par personne.

**Source aujourd'hui, source demain.** Le contenu vit dans `Contenu_vitrine/`, trois
fichiers YAML versionnés en Git : le cabinet corrige une phrase, la revue de code voit le
changement, l'historique dit qui a écrit quoi. Le port `DepotContenuVitrine` est déclaré
dans le domaine ; le jour où un écran d'administration s'imposera, un
`DepotContenuVitrineSql` réalisera le même port et seul l'adaptateur changera.

**Lecture seule et sans authentification.** Tout ce que ces routes rendent est déjà destiné
à être affiché publiquement. L'écriture, quand elle viendra, aura son propre routeur : une
route publique et une route d'administration n'ont ni le même public, ni les mêmes
garanties.

---

## M · Souscription

L'offre commerciale du cabinet, le devis, l'encaissement mobile et l'ouverture de l'accès
adhérent. Le parcours qui va de la page de tarifs du site public au premier écran de
l'espace personnel.

**Pourquoi un treizième contexte.** Ce dossier en décrivait douze. L'ajout se justifie par
l'échec des trois autres placements possibles :

* **L · Vitrine** est du contenu éditorial, et son isolement est délibéré — « du contenu qui
  aurait besoin d'un paramètre légal ne serait plus du contenu ». Un encaissement encore
  moins.
* **I · Création d'entreprise** est une prestation parmi cinq. Y loger la souscription
  obligerait à passer par la création pour vendre une domiciliation.
* **A · Référentiel** porte des valeurs **légales**. Les honoraires du cabinet n'en sont pas :
  il les fixe librement, et les mêler aux taux du Code général des impôts brouillerait la
  seule chose que le référentiel doit garantir.

Ce que M détient et que personne d'autre ne détient : **combien coûte notre service, et
comment on l'encaisse**.

**Ses arêtes.** `souscription → portefeuille`, pour une seule question — ce NIU est-il déjà
suivi ? —, plus le socle. Personne ne le lit, sauf J · Pilotage le jour où il existera.

**Une souscription n'est pas un dossier.** Elle dit qu'un accès a été payé, pas que
l'entreprise existe, ni qu'elle a un régime, ni qu'elle a un exercice. La création du dossier
reste un geste du chargé de clientèle, sur pièces. Verser automatiquement chaque souscription
au portefeuille y ferait entrer des entreprises dont on ne sait rien — et le contexte B tout
entier repose sur l'idée qu'on ne sait d'une entreprise que ce qu'on a constaté.

**Le barème est daté**, exactement comme un paramètre légal. Un devis établi en mars et payé
en juin est honoré au prix de mars. Le devis **recopie** les montants plutôt que de les
référencer : c'est ce qui distingue un devis d'une page de tarifs.

**Ce qui n'est pas souscriptible en ligne, et pourquoi.** La création d'entreprise. Ses frais
officiels sont des valeurs légales qui relèvent de A, ils n'y sont pas, et l'on sait déjà que
les montants employés par la vitrine sont approximatifs. Encaisser un montant qu'on sait faux
serait pire que ne rien encaisser. La création produit une demande de devis — ce que la
vitrine annonce déjà.

**Le paiement mobile.** Le module `mail+paiement/` du dépôt, éprouvé en production, est en
Django. Ce qui en est repris n'est pas son code mais ses **invariants** : clé d'idempotence
propre transmise au prestataire, traitement de notification atomique et rejouable,
rapprochement à trois stratégies, réconciliation par appel sortant, péremption à
vingt-quatre heures. Voir `domaine/paiements.py`, dont l'en-tête détaille chacun.

---

## N · Tenants

Le plan de contrôle. Cycle de vie d'un tenant : slug, ouverture, quotas, suspension,
résiliation. C'est lui qui décide qu'un sous-domaine répond, et à qui.

**Pourquoi il est séparé de K · Transverse**, qui porte déjà l'identité. Ouvrir un tenant
est une opération longue, rare, transactionnelle sur plusieurs systèmes. Vérifier un jeton
est une opération courte, constante, sur le chemin critique de chaque requête. Les deux
n'ont ni le même profil de charge, ni la même exigence de disponibilité : si le
provisionnement tombe, les tenants déjà ouverts continuent de fonctionner, seules les
nouvelles souscriptions attendent.

**Ses arêtes : aucune.** Il ne lit même pas le référentiel. Un slug n'a pas de fondement
légal, une suspension non plus. C'est le seul contexte qui ne dépend de rien, et cette
ignorance est ce qui lui permettra de servir un autre secteur sans bouger.

**Un tenant n'est pas un déploiement.** C'est une ligne en base, un schéma PostgreSQL et
un préfixe de stockage. Aucun conteneur ne démarre, aucun enregistrement DNS ne s'écrit,
aucun certificat ne se demande quand un client arrive. C'est cette propriété qui rend la
souscription instantanée au trois-centième client comme au premier, et son absence est ce
qui transforme une souscription en ticket d'exploitation.

**Le slug est attribué une fois et jamais réattribué.** Le libérer pour le donner à
quelqu'un d'autre enverrait les anciens liens, les signets et les courriels archivés d'un
client chez un concurrent. C'est le pire incident de confidentialité que la plateforme
puisse produire, et il n'a aucune contrepartie : un slug coûte quelques octets à
conserver. Un changement laisse une redirection permanente, jamais une réattribution.

**L'unicité est arbitrée par la base**, par un index unique insensible à la casse, jamais
par une lecture suivie d'une écriture : entre les deux, une autre souscription a eu le
temps d'écrire. La fonction de proposition évite les collisions connues ; elle ne les
empêche pas, et l'appelant doit être prêt à recevoir le refus de la base.

**Les noms réservés sont une donnée.** `www`, `api`, `admin` et une trentaine d'autres
vivent dans `Docs/referentiel/tenants/noms-reserves.yaml`. La liste grandit — un
sous-domaine technique de plus, une marque à protéger — et la faire grandir ne doit pas
demander une livraison.

---

## Ports et adaptateurs

Toutes les intégrations passent derrière une interface abstraite, avec **systématiquement un
mode manuel de secours**.

| Port | Adaptateur initial | Adaptateur cible |
|---|---|---|
| `FiscalInvoiceGateway` | PDF / manuel | e-facturation DGI, dès publication des spécifications |
| `NiuVerificationPort` | Saisie manuelle + cache | Portail DGI |
| `PortailDeclaratif` | ✅ **`PortailManuel`** — consigne l'accusé rapporté du portail, après vérification de référence **et** d'empreinte | Appel réseau, dès publication des spécifications (voir Q1 bis) |
| `CnpsPort` | Manuel | Télédéclaration DIPE |
| `PaiementMobilePort` | Justificatif photographié | MTN MoMo, Orange Money |
| `RelevesBancairesPort` | Import de fichier | API bancaires |
| `NotificationPort` | Courriel | SMS, WhatsApp Business API |

Le port `FiscalInvoiceGateway` est à concevoir **dès maintenant**, avec les champs qui seront
exigés — identifiant unique de transmission, horodatage, statut de validation par
l'administration, empreinte — même si l'implémentation reste manuelle. La LF 2026 institue la
facturation électronique et le déploiement commence par les grandes entreprises au réel.
