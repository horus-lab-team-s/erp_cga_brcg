# Journal de bord — Plateforme CGA Broad Range Consulting Group

Registre chronologique des sessions de travail, des décisions prises et des points laissés
ouverts. Une entrée par session. Les décisions structurantes sont reprises et développées
dans `Docs/architecture/`, les questions non tranchées dans
`Docs/architecture/09-questions-ouvertes.md`.

**Convention d'écriture.** Chaque entrée porte une date absolue, la demande telle qu'elle a
été formulée, ce qui a été produit, les décisions arrêtées et ce qui reste en suspens. On
n'y consigne pas ce que le dépôt raconte déjà par lui-même (structure des fichiers,
historique Git) : uniquement le *pourquoi*.

---

## 2026-08-09 — Session 1 · Cadrage, lecture des maquettes, socle Phase 0+1

### Demande

1. Créer un journal des conversations.
2. Prendre connaissance de l'architecture globale des fichiers, puis des wireframes de `Docs/`.
3. Importer le projet Claude Design `CGA Broad Range Consulting Group`
   (`8fff8f63-4f00-4a32-bdf9-c765969d87e0`) et appliquer le document de cadrage fourni :
   plateforme de suivi fiscal et comptable pour Centre de Gestion Agréé camerounais,
   conception modulaire en contextes bornés.
4. Initialiser le dépôt Git et pousser sur `github.com/horus-lab-team-s/erp_cga_brcg`.

### État trouvé

Dépôt non versionné. Une application `create-next-app` (Next.js 16 / React 19 / Tailwind 4)
à la racine, deux dossiers `Backend_erp_cga/` et `Frontend_erp_cga/` vides, et six maquettes
dans `Docs/`.

Les six fichiers de `Docs/` ne sont pas des pages HTML ordinaires : ce sont des bundles
Claude Design auto-extractibles (~600 Ko chacun), où le contenu réel est une chaîne JSON et
les ressources des blobs base64. Il a fallu les décompresser pour les lire.

### Ce que le projet Claude Design distant contenait en plus de `Docs/`

La lecture du projet distant a révélé des fichiers absents du dossier local, dont deux
essentiels :

| Fichier distant | Nature | Statut |
|---|---|---|
| `uploads/dossier-design-CGA-pour-claude-design.md` | **Dossier de design v1.0, § 0 à § 14** — document de référence unique | Lu, intégré |
| `Wireframes CGA.dc.html` | Wireframes E00 à E13 | Repéré, non extrait |
| `Transverse CGA.dc.html` | Écrans transverses | Repéré, non extrait |
| `uploads/Cahier_des_charges_TECHNIQUE_CGA_BRC_Group.pdf` | Cahier des charges technique | **Repéré, non lu** |
| `uploads/Cahier_des_charges_Plateforme_CGA_BRC_Group.pdf` | Cahier des charges fonctionnel | **Repéré, non lu** |
| `uploads/Cahier_des_charges_CGA_BRC_Group_version_synthetique.pdf` | Synthèse | **Repéré, non lu** |

Le dossier de design est le document le plus important trouvé : il fixe le vocabulaire
métier (§ 3), les formats de données (§ 4), l'architecture de l'information (§ 6),
l'inventaire des quatorze écrans (§ 7), les fiches d'écran (§ 8), le système de gravité
(§ 9), le design system (§ 10) et un jeu de données de démonstration cohérent (§ 13).

> **À faire au prochain tour** : les trois cahiers des charges PDF n'ont pas été lus. Ils
> peuvent contenir des exigences contractuelles qui contredisent ou complètent le cadrage.
> À dépouiller avant d'aller plus loin que le socle.

### Décisions arrêtées

| # | Décision | Motif |
|---|---|---|
| D1 | **Monorepo pnpm** : l'application Next.js migre de la racine vers `Frontend_erp_cga/` ; `Backend_erp_cga/` accueille le backend | Les deux dossiers existaient vides : intention manifeste de séparer. La racine devient l'orchestrateur du workspace. |
| D2 | **Backend FastAPI + SQLAlchemy + PostgreSQL**, monolithe modulaire, un package Python par contexte borné | § 5 du cadrage écarte les microservices pour un projet de cette taille. Choix de stack arrêté par le client en cours de session, après une première proposition NestJS écartée. |
| D3 | **Le prédicat d'une règle exprime la conformité, pas la violation** : `predicat` vrai ⇒ conforme ; faux ⇒ constat émis | Conforme à l'exemple `FAC-ID-003` du cadrage (§ 4.2). Contre-intuitif : documenté explicitement partout. |
| D4 | **Les paramètres légaux sont pré-résolus dans le prédicat avant évaluation**, et non lus par un opérateur dynamique | Donne une trace auditable : le rapport conserve la valeur exacte du paramètre utilisée et sa date d'effet. Défendable devant la DGI. |
| D5 | **JSONLogic** comme langage de prédicat, jamais `eval`, avec un évaluateur maison restreint | § 4.5. Sérialisable en base, éditable par un back-office, testable unitairement. Les portages Python de JSONLogic disponibles sont non maintenus : un évaluateur d'une centaine de lignes, couvrant un sous-ensemble explicite d'opérateurs, est plus sûr qu'une dépendance abandonnée. |
| D6 | Périmètre de cette itération : **socle Phase 0 + Phase 1 exécutable**. Pas de comptabilité, pas de déclaratif, pas de paie. | Le cadrage décrit six phases sur plusieurs mois. |

### Divergence relevée sur le seuil de règlement en espèces

Le document de cadrage (§ 2.4) et les maquettes ne disent pas la même chose :

- **Cadrage** : « pour les opérations ≥ **100 000 FCFA**, la déduction n'est admise que si
  l'opération n'a pas été payée en espèces ».
- **Maquettes** (`Prototype cliquable`, constat `FAC-ACH-007`) : « dépasse le seuil légal de
  **500 000 FCFA** », référence CGI art. 143.

Un facteur cinq. C'est exactement le cas d'usage qui justifie l'architecture retenue : la
valeur est stockée en paramètre daté, marquée `A_VALIDER`, et le moteur ne la connaît pas.
Voir `Docs/architecture/09-questions-ouvertes.md`, question Q1. **Aucune des deux valeurs ne
doit être considérée comme exacte tant que le fiscaliste n'a pas tranché sur le texte.**

### Produit

- Réorganisation en monorepo pnpm.
- `Docs/architecture/` : vision, contextes bornés, référentiel normatif, moteur de
  conformité, modèle de données, sécurité et multi-tenant, séquencement, inventaire des
  écrans, glossaire, questions ouvertes.
- `Docs/referentiel/parametres.yaml` : paramètres légaux datés, chacun avec son fondement et
  son statut de validation.
- `Docs/referentiel/regles/` : les cinq règles `FAC-*` du § 13.6 du dossier de design.
- Backend FastAPI : contexte `referentiel` (lecture de paramètre à une date) et contexte
  `conformite` (moteur de règles, rapport, conséquence fiscale), avec tests.
- Frontend : jetons de couleur, typographie, densité et gravité du § 10 traduits en CSS.
- Dépôt Git initialisé et poussé.

### Reste ouvert

- Les trois cahiers des charges PDF, non lus (voir ci-dessus).
- Les wireframes E00–E13 et l'écran Transverse, non extraits du projet distant.
- Q1 seuil espèces, et l'ensemble des questions de
  `Docs/architecture/09-questions-ouvertes.md`.
- Le logo monochrome blanc pour la barre latérale sombre n'existe pas : signalé en rouge
  dans la bibliothèque de composants, à demander au cabinet.
- Les ateliers de cadrage métier (§ 1 du cadrage : matrice RACI, processus réels) n'ont pas
  eu lieu. Le modèle de données reste une hypothèse tant qu'ils ne sont pas tenus.

---
