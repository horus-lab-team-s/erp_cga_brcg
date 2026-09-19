# Plateforme CGA — Broad Range Consulting Group

Plateforme de suivi fiscal et comptable pour le Centre de Gestion Agréé **Broad Range
Consulting Group** — agrément MINFI/DGI n° 00000048, agences de Douala Akwa, Yaoundé
Elig-Essono et Bafoussam.

> ⚠️ **Aucune valeur légale de ce système n'a été validée sur le Code Général des Impôts.**
> Taux, seuils, délais et pénalités proviennent de sources secondaires et portent tous le
> statut `A_VALIDER`. Aucun chiffre produit n'est opposable tant qu'un fiscaliste nommé
> n'a pas confirmé chaque valeur sur le texte. Voir
> [`Docs/architecture/09-questions-ouvertes.md`](Docs/architecture/09-questions-ouvertes.md).

## Ce que fait le produit

**Déplacer le contrôle fiscal en amont.** Une facture non conforme détectée à sa réception
se régularise auprès du fournisseur ; découverte trois mois plus tard, elle ne laisse
qu'une perte fiscale sèche pour l'adhérent.

Le cœur est un moteur de conformité qui contrôle chaque facture au regard du droit fiscal
camerounais et produit, pour chaque anomalie, une **conséquence fiscale chiffrée** — « TVA
non déductible : 379 350 FCFA » — qui se propage jusqu'à la déclaration mensuelle puis
jusqu'à la liasse annuelle.

## Structure

```
erp_cga_brcg/
├── Backend_erp_cga/      FastAPI · monolithe modulaire, un paquet par contexte borné
├── Frontend_erp_cga/     Next.js 16 · React 19 · Tailwind 4
├── Docs/
│   ├── architecture/     Dossier de conception, à lire dans l'ordre 00 → 09
│   ├── referentiel/      Paramètres légaux datés et règles de conformité (YAML)
│   └── *.html            Maquettes Claude Design : composants, parcours, prototype
├── Site_conception/      Le document de conception servi comme site (Vercel, racine = ce dossier)
└── JOURNAL.md            Journal de bord des sessions et des décisions
```

Stack : **FastAPI** · **Next.js** · **PostgreSQL**.

## Démarrer

**La pile complète, en une commande.** Base PostgreSQL, migration, API et front :

```bash
docker compose up --build         # http://localhost:3000
```

⚠️ `docker-compose.yml` décrit une pile **locale**, pas une configuration de
production : mot de passe de base en clair, aucun TLS, aucune sauvegarde. Le fichier
le dit lui-même en en-tête.

**Ou service par service, pour développer :**

```bash
# Frontend
pnpm install
pnpm dev                          # http://localhost:3000

# Backend
cd Backend_erp_cga
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
pytest                            # 1000 tests
```

Copier [`Backend_erp_cga/.env.example`](Backend_erp_cga/.env.example) en `.env` pour
régler la persistance, le relais de messagerie et le chiffrement. Les valeurs par
défaut suffisent à démarrer : persistance en mémoire, jeu de démonstration amorcé,
et **aucun courriel ne part**.

⚠️ **La production refuse de démarrer** sur une configuration dangereuse — persistance
en mémoire, absence de relais de messagerie ou de clé de chiffrement, adresse publique
en clair. Un démarrage refusé se voit ; une base qui s'efface au redéploiement ne se
voit qu'après.

## Les treize contextes bornés

Découpage en contextes métier autonomes. Monolithe modulaire, pas de microservices :
l'équipe est réduite et le besoin de scalabilité n'existe pas.

| | Contexte | Paquet | État |
|---|---|---|---|
| **A** | Référentiel normatif — *le pivot* | `contextes/referentiel/` | ✅ Implémenté |
| **B** | Portefeuille adhérents | `contextes/portefeuille/` | 🟡 Statuts datés, exercices, seuils — API exposée |
| **C** | Collecte de pièces | `contextes/collecte/` | 🟡 Cycle de vie, doublons, complétude, **stockage des documents** — API exposée. ⚠️ Aucune extraction automatique |
| **D** | Conformité documentaire — *le cœur* | `contextes/conformite/` | ✅ Implémenté |
| **E** | Comptabilité SYSCOHADA | `contextes/comptabilite/` | 🟡 Écritures, balance, grand livre, imputation — API exposée |
| **F** | Obligations et déclarations | `contextes/obligations/` | 🟡 Échéancier, relances, pénalités, déclaration de TVA — API exposée |
| **G** | Social et paie | `contextes/social/` | Squelette |
| **H** | Clôture et DSF | `contextes/cloture/` | Squelette |
| **I** | Création d'entreprise — *produit d'appel* | `contextes/creation_entreprise/` | Squelette |
| **J** | Pilotage CGA | `contextes/pilotage/` | Squelette |
| **K** | Transverse — IAM, GED, audit — *socle* | `contextes/transverse/` | 🟡 Identité, habilitations datées, cloisonnement, sessions révocables, audit chaîné, **courriels SMTP**, **secrets chiffrés au repos** — API exposée |
| **L** | Vitrine publique — *contenu éditorial du site* | `contextes/vitrine/` | ✅ Implémenté |
| **M** | Souscription — *du site public à l'espace adhérent* | `contextes/souscription/` | 🟡 Barème daté, devis, paiement mobile, ouverture d'accès — API exposée |

> ⚠️ **Toutes les routes métier de B, C, E et F exigent une session** et vérifient le
> périmètre du portefeuille. Un dossier hors périmètre rend `404`, jamais `403` : un `403`
> apprendrait à un adhérent quels dossiers le cabinet suit.

Le graphe de dépendances autorisé est déclaré dans `Backend_erp_cga/tests/test_architecture.py`
et **vérifié à chaque exécution des tests** : le référentiel ne dépend d'aucun contexte, le
graphe reste acyclique, aucun paquet hors nomenclature. Ajouter une arête impose de la
justifier dans [`Docs/architecture/01-contextes-bornes.md`](Docs/architecture/01-contextes-bornes.md).

## L'interface

Sept écrans de travail sont construits et lisent le backend réel : portefeuille, pièces
justificatives et rapport de conformité, comptabilité et grand livre, obligations et
déclaration de TVA, référentiel des paramètres, comptes et habilitations. Quatre restent
inertes — conformité avancée, clôture annuelle, création d'entreprise, pilotage — parce que
leur contexte backend n'existe pas encore ; la navigation les affiche « à venir » plutôt que
de les masquer.

Deux écrans ne modifient rien **délibérément** : le référentiel, dont l'édition devra
journaliser chaque changement de valeur légale, et l'administration, dont les gestes
(suspendre, affecter, fermer une habilitation) réclament des confirmations explicites.

Détail et décisions d'affichage :
[`Docs/architecture/07-inventaire-ecrans.md`](Docs/architecture/07-inventaire-ecrans.md).

## Les trois principes non négociables

**1 · Aucune valeur légale en dur, aucune lecture sans date.**
Chaque loi de finances modifie taux, seuils et règles. Dispersés dans le code, ils tuent le
produit en trois ans.

```python
parametres.valeur_numerique("SEUIL_ESPECES_DEDUCTIBILITE_TVA", facture.date_emission)
```

Il n'existe volontairement aucune façon de lire « la valeur courante ». Une facture de 2024
se contrôle avec les règles de 2024.

**2 · Fondement légal obligatoire sur chaque règle et chaque paramètre.**
Sans lui, on ne sait pas quoi mettre à jour à la loi de finances suivante, ni justifier un
rejet auprès d'un adhérent mécontent. C'est ce qui distingue cet outil d'un validateur de
formulaire.

**3 · La conséquence fiscale est déclarative.**
La règle *décrit* ce qui se passe, un service en aval l'*applique*. Le contrôle d'une
facture n'est pas un booléen : c'est un rapport de constats gradués, chacun chiffré.

## Exploitation

| Sujet | Où |
|---|---|
| Variables d'environnement | [`Backend_erp_cga/.env.example`](Backend_erp_cga/.env.example) |
| Images | `Backend_erp_cga/Dockerfile`, `Frontend_erp_cga/Dockerfile` — ⚠️ à construire **depuis la racine** |
| Pile locale | [`docker-compose.yml`](docker-compose.yml) |
| Vérification continue | [`.github/workflows/verification.yml`](.github/workflows/verification.yml) |
| Migrations | `cd Backend_erp_cga && alembic upgrade head` — jamais au démarrage de l'application |
| Sonde de disponibilité | `GET /sante` — interroge la base, rend `503` si elle est injoignable |

**Deux choses doivent être sauvegardées**, et elles sont de nature différente :

* la **base PostgreSQL** — comptes, habilitations, écritures, déclarations, audit ;
* le dossier des **justificatifs déposés** (`CGA_DOSSIER_FICHIERS`). Sans lui, la
  comptabilité perd ses pièces et devient indéfendable devant un vérificateur.

⚠️ **Ce qui reste à faire hors du code** avant une mise en service : publier SPF, DKIM
et DMARC sur le domaine du cabinet — sans quoi les liens d'activation partent en
indésirables —, et placer l'API derrière un mandataire inverse qui termine le TLS et
réécrit `X-Forwarded-For`, dont dépend la limitation de débit.

## Documentation

| Document | Contenu |
|---|---|
| [`Docs/architecture/`](Docs/architecture/README.md) | Vision, contextes, référentiel, moteur, données, sécurité, phases, écrans, glossaire, questions ouvertes |
| [`Docs/referentiel/`](Docs/referentiel/regles/README.md) | Paramètres datés et catalogue de règles |
| [`Docs/recette.md`](Docs/recette.md) | **Dérouler les parcours à la main** : mode de recette, comptes de test, pas à pas |
| [`Backend_erp_cga/README.md`](Backend_erp_cga/README.md) | API, moteur, tests, ajout d'une règle |
| [`JOURNAL.md`](JOURNAL.md) | Décisions de session, avec leur motif |

## État d'avancement

Phase 0 partielle et Phase 1 en cours. Les ateliers de cadrage métier avec le cabinet — la
matrice RACI, la cartographie des processus réels — **n'ont pas eu lieu** : le modèle de
données reste une hypothèse tant qu'ils ne sont pas tenus. Trois cahiers des charges
contractuels restent par ailleurs à dépouiller. Détail dans
[`Docs/architecture/06-phases-et-sequencement.md`](Docs/architecture/06-phases-et-sequencement.md).
