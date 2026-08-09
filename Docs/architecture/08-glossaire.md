# 08 · Glossaire métier

Vocabulaire à employer **exactement**, sans traduction ni approximation, dans le code, les
écrans collaborateur et la documentation. Référence : § 3 du dossier de design.

| Terme | Sens | Où il apparaît |
|---|---|---|
| **Adhérent** | Entreprise cliente du cabinet | Partout |
| **NIU** | Numéro d'identifiant unique, identité fiscale délivrée par la DGI | Fiches entreprise, factures, contrôles |
| **RCCM** | Registre du commerce et du crédit mobilier | Fiches entreprise, factures |
| **DGI** | Direction Générale des Impôts | Références réglementaires |
| **CDI, CIME, DGE** | Centres des impôts de rattachement, du plus petit au plus grand | Fiche entreprise, calcul des échéances |
| **IGS** | Impôt Général Synthétique, régime des petites entreprises, unique et libératoire | Régime fiscal |
| **Régime du réel** | Régime des entreprises plus importantes, assujetties à la TVA | Régime fiscal |
| **TVA** | Taxe sur la valeur ajoutée | Factures, déclarations |
| **Précompte, retenue à la source** | Prélèvements opérés par certains clients | Factures, déclarations |
| **DSF** | Déclaration Statistique et Fiscale, déclaration annuelle des états financiers | Clôture |
| **Liasse fiscale** | Ensemble des tableaux composant la DSF | Clôture |
| **SYSCOHADA** | Référentiel comptable applicable, révisé, en vigueur depuis 2018 | Comptabilité, plan de comptes |
| **Réintégration** | Ajout au résultat comptable d'une charge non déductible fiscalement | Conformité, clôture |
| **Tableau de passage** | État de détermination du résultat fiscal à partir du résultat comptable | Clôture |
| **Contre-passation** | Écriture d'annulation, **seul mode de correction admis** | Comptabilité |
| **Exercice** | Période couverte par les comptes annuels | Partout |
| **CFCE** | Centre de formalités de création d'entreprises, guichet unique | Création d'entreprise |
| **CNPS** | Caisse Nationale de Prévoyance Sociale | Obligations sociales |
| **DIPE** | Déclaration d'information sur le personnel employé, déposée à la CNPS | Social, paie |
| **ONECCA** | Ordre National des Experts-Comptables du Cameroun | Visa des états financiers |
| **OAPI** | Organisation Africaine de la Propriété Intellectuelle | Antériorités de nom, création |
| **SMT** | Système Minimal de Trésorerie, comptabilité de trésorerie des très petites entités | Comptabilité |
| **Système Normal** | Bilan, compte de résultat, tableau des flux, notes annexes | Comptabilité, DSF |
| **CAC** | Centimes additionnels communaux, majoration de certains impôts | TVA, IS |

## Vocabulaire adhérent

Le vocabulaire technique **disparaît** des écrans destinés aux adhérents. Correspondances à
respecter :

| On écrit… | …et jamais |
|---|---|
| justificatif | pièce comptable, pièce justificative |
| votre déclaration de TVA de juillet | obligation déclarative périodique |
| ce que vous devez payer | montant exigible |
| votre dossier est complet | complétude à 100 % |
| une facture a été refusée | anomalie bloquante détectée |
| il manque le numéro d'identification du fournisseur | NIU émetteur absent — FAC-ID-003 |
| le cabinet | le Centre de Gestion Agréé |

## Nommage dans le code

Le domaine est écrit en français : `RapportConformite`, `severite`, `consequence_fiscale`,
`date_emission`. Mélanger un domaine fiscal camerounais avec des identifiants anglais produit
des traductions approximatives à chaque relecture — `finding`, `severity`, `deductible`
n'ont pas exactement le sens de constat, gravité, déductible.

L'infrastructure (HTTP, base, tests) suit les conventions habituelles de chaque outil.
