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
└── JOURNAL.md            Journal de bord des sessions et des décisions
```

Stack : **FastAPI** · **Next.js** · **PostgreSQL**.

## Démarrer

```bash
# Frontend
pnpm install
pnpm dev                          # http://localhost:3000 — bibliothèque de composants

# Backend
cd Backend_erp_cga
python -m venv .venv && .venv/Scripts/activate    # source .venv/bin/activate sous Unix
pip install -e ".[dev]"
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
pytest                            # 130 tests
```

## Les onze contextes bornés

Découpage en contextes métier autonomes. Monolithe modulaire, pas de microservices :
l'équipe est réduite et le besoin de scalabilité n'existe pas.

| | Contexte | Paquet | État |
|---|---|---|---|
| **A** | Référentiel normatif — *le pivot* | `contexts/referentiel/` | ✅ Implémenté |
| **B** | Portefeuille adhérents | `contexts/portefeuille/` | Squelette |
| **C** | Collecte de pièces | `contexts/collecte/` | Squelette |
| **D** | Conformité documentaire — *le cœur* | `contexts/conformite/` | ✅ Implémenté |
| **E** | Comptabilité SYSCOHADA | `contexts/comptabilite/` | Squelette |
| **F** | Obligations et déclarations | `contexts/obligations/` | Squelette |
| **G** | Social et paie | `contexts/social/` | Squelette |
| **H** | Clôture et DSF | `contexts/cloture/` | Squelette |
| **I** | Création d'entreprise — *produit d'appel* | `contexts/creation_entreprise/` | Squelette |
| **J** | Pilotage CGA | `contexts/pilotage/` | Squelette |
| **K** | Transverse — IAM, GED, audit | `contexts/transverse/` | Squelette |

Le graphe de dépendances autorisé est déclaré dans `Backend_erp_cga/tests/test_architecture.py`
et **vérifié à chaque exécution des tests** : le référentiel ne dépend d'aucun contexte, le
graphe reste acyclique, aucun paquet hors nomenclature. Ajouter une arête impose de la
justifier dans [`Docs/architecture/01-contextes-bornes.md`](Docs/architecture/01-contextes-bornes.md).

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

## Documentation

| Document | Contenu |
|---|---|
| [`Docs/architecture/`](Docs/architecture/README.md) | Vision, contextes, référentiel, moteur, données, sécurité, phases, écrans, glossaire, questions ouvertes |
| [`Docs/referentiel/`](Docs/referentiel/regles/README.md) | Paramètres datés et catalogue de règles |
| [`Backend_erp_cga/README.md`](Backend_erp_cga/README.md) | API, moteur, tests, ajout d'une règle |
| [`JOURNAL.md`](JOURNAL.md) | Décisions de session, avec leur motif |

## État d'avancement

Phase 0 partielle et Phase 1 en cours. Les ateliers de cadrage métier avec le cabinet — la
matrice RACI, la cartographie des processus réels — **n'ont pas eu lieu** : le modèle de
données reste une hypothèse tant qu'ils ne sont pas tenus. Trois cahiers des charges
contractuels restent par ailleurs à dépouiller. Détail dans
[`Docs/architecture/06-phases-et-sequencement.md`](Docs/architecture/06-phases-et-sequencement.md).
