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

## 2026-08-09 — Session 2 · Audit des flux, puis E00, E01 et E02

### Demande

Vérifier d'abord que les flux des maquettes sont couverts côté modularité et
fonctionnalité, puis réaliser le frontend en commençant par E00, E01, E02.

### Audit de couverture

Trente parcours confrontés au découpage. **Six arêtes manquaient au graphe.** La plus
grave : `obligations → conformite`. La ligne L24 de la déclaration de TVA — « TVA rejetée
par le contrôle de conformité » — n'avait aucun chemin pour exister. Le moteur produisait
des constats que personne ne consommait : la chaîne « constat → attribut fiscal → TVA du
mois → réintégration DSF », qui est la proposition de valeur du produit, était rompue au
deuxième maillon.

Détail complet dans `Docs/architecture/10-flux-fonctionnels.md`, qui devient la source du
graphe déclaré dans les tests.

| # | Décision | Motif |
|---|---|---|
| D8 | **Surface publique obligatoire** : un contexte n'importe que `<autre>.api` | Au premier `from ..autre.service import _helper`, la frontière est morte. Vérifié par les tests. |
| D9 | `referentiel` et `transverse` forment un **socle** lisible par tous ; `pilotage` est un **puits** lu par personne | Exiger une arête depuis chacun des dix contextes vers le socle n'apprendrait rien. Un contexte qui lirait le pilotage signalerait un indicateur ayant pris une valeur métier, à redescendre. |
| D10 | Les **surfaces d'agrégation** — plan de travail comptable, accueil adhérent — seront une couche de composition en lecture seule à la façade HTTP, pas un douzième contexte | Un contexte « espace de travail » deviendrait le fourre-tout que `test_aucun_paquet_hors_nomenclature` cherche à empêcher. **À confirmer avec le cabinet avant E01 définitif et E06.** |

Le test d'acyclicité a détecté un cycle `referentiel ↔ transverse` introduit en cours de
refonte du graphe. Le garde-fou fonctionne.

### Écrans livrés

| Écran | État | Données |
|---|---|---|
| **E00** Structure et navigation | Coquille, barre latérale repliable, sélecteur d'entreprise, en-tête | Statiques |
| **E01** Tableau de bord collaborateur | Quatre indicateurs, trois tableaux denses, tient en 1440 × 900 | `lib/donnees-demo.ts` |
| **E02** Pièce et rapport de conformité | Deux colonnes, verdict, données extraites, constats dépliables, trace du contrôle | **Vrai moteur de conformité** |
| E03 | Ébauche seulement — la liste qui mène à E02 | Vrai moteur |

E02 est le seul écran branché sur le backend : les constats affichés sont produits par
l'évaluation des prédicats sur le référentiel daté. Le bloc « Trace du contrôle » restitue
les paramètres employés, leur valeur et leur date d'effet — c'est ce qui rendra un rapport
défendable des années plus tard.

Le § 8.0 demandait **deux propositions d'organisation du menu**. Elles sont rédigées en tête
de `Frontend_erp_cga/app/lib/navigation.ts` : « par nature de travail », appliquée, et « par
rôle », argumentée et écartée. Basculer revient à réécrire un seul tableau.

### Points techniques

- Le backend renvoie désormais la facture avec le rapport : E02 affiche les données
  extraites à côté des constats, les séparer en deux appels obligerait l'écran à recoller
  deux états qui doivent rester cohérents.
- Deux lectures de systèmes externes — préférence de repli, modificateur clavier — passent
  par `useSyncExternalStore` et non par un effet. Le lint l'a signalé à raison : lire dans
  un effet puis appeler `setState` produit un rendu en cascade et un clignotement visible.
- **La vérification visuelle par capture d'écran n'a pas pu être faite** : l'extension
  Chrome affiche une page d'erreur sur `localhost` alors que le serveur répond 200 en
  ligne de commande — vraisemblablement une permission de site non accordée. Le contrôle a
  porté sur le HTML rendu, ce qui valide le contenu et la structure, pas l'aspect.

### Reste ouvert

- Les trois cahiers des charges PDF, toujours non lus, désormais versionnés dans `Docs/`.
- D10 à confirmer avant de figer E01 et de commencer E06.
- E03 à reprendre en entier : filtres à puces, sélection multiple, aperçu latéral,
  25 lignes visibles, navigation clavier.
- Aucun écran de l'espace adhérent n'existe : le groupe de routes `(adherent)` reste à
  créer, avec `data-espace="adherent"` et ses cibles tactiles de 44 px.

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
| D7 | **Les onze contextes sont matérialisés dès maintenant** en paquets Python, même vides, et le graphe de dépendances autorisé est déclaré dans `tests/test_architecture.py` | Demande explicite du client en cours de session : « je ne veux pas qu'on s'égare ». Un monolithe modulaire ne tient pas par la bonne volonté mais parce qu'une dépendance interdite fait échouer la CI. Créer les paquets plus tard, au fil de l'eau, produit toujours un fourre-tout qui absorbe tout. |

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

- Réorganisation en monorepo pnpm : Next.js migré de la racine vers `Frontend_erp_cga/`.
- `Docs/architecture/` : dix documents, de la vision aux questions ouvertes.
- `Docs/referentiel/parametres.yaml` : seize paramètres légaux datés, chacun avec son
  fondement et son statut de validation.
- `Docs/referentiel/regles/` : les cinq règles `FAC-*` du § 13.6 du dossier de design.
- Backend FastAPI, **onze contextes matérialisés** dont deux implémentés — `referentiel`
  (lecture datée) et `conformite` (moteur, rapport, conséquence fiscale chiffrée).
- Frontend : jetons du § 10 en CSS, bibliothèque de composants rendue à l'écran.
- **130 tests**, `ruff` et `eslint` au vert, `next build` sans avertissement.
- Dépôt initialisé et poussé sur `horus-lab-team-s/erp_cga_brcg`, commit `626a762`.

### Ce que les tests garantissent, au-delà du comportement

Quatre familles de tests ne vérifient pas une fonctionnalité mais empêchent une
dégradation silencieuse :

| Test | Ce qu'il rend impossible |
|---|---|
| `test_architecture.py` | Une dépendance hors du graphe déclaré, un cycle, un paquet fourre-tout, un référentiel qui dépendrait d'un autre contexte |
| `test_integrite_referentiel.py` | Une règle sans fondement légal, un paramètre référencé mais inexistant, une règle sans tests, une valeur légale codée en dur |
| `test_regles.py` | Une dérive des verdicts du § 13.5 : ce sont les chiffres que le cabinet a vus sur les maquettes |
| `test_rien_nest_encore_opposable` | Oublier de mettre à jour la documentation le jour où le fiscaliste validera le référentiel — ce test échouera alors volontairement |

### Reste ouvert

- **Les trois cahiers des charges PDF, non lus.** Ils ont été déposés dans `Docs/` en fin
  de session et sont désormais versionnés. À dépouiller **en priorité au prochain tour** :
  ce sont des documents contractuels, ils peuvent contredire le cadrage sur lequel tout
  ce qui précède repose.
- Les wireframes E00–E13 et l'écran Transverse, non extraits du projet distant.
- Q1 seuil espèces, et l'ensemble des questions de
  `Docs/architecture/09-questions-ouvertes.md`.
- **PostgreSQL n'est pas branché.** Le référentiel est lu depuis des fichiers YAML ;
  `ServiceParametres` ignore l'origine des données, la bascule n'affectera aucun appelant.
  Prévu Phase 1, non fait.
- Neuf contextes sur onze sont des squelettes : paquet et portée documentée, aucun code.
- Le logo monochrome blanc pour la barre latérale sombre n'existe pas : signalé en rouge
  dans la bibliothèque de composants, à demander au cabinet.
- Les ateliers de cadrage métier (§ 1 du cadrage : matrice RACI, processus réels) n'ont pas
  eu lieu. Le modèle de données reste une hypothèse tant qu'ils ne sont pas tenus.

---

## Session — 10 août 2026 · Composition de l'accueil, infolettre, réseaux

### Le carrousel ne défilait pas

Signalé comme « la bannière doit défiler automatiquement ». Elle en avait bien
l'intention : minuterie de cinq secondes, mise en pause au survol. Mais la
bannière occupe **toute la hauteur de l'écran**, donc la souris est presque
toujours dessus, donc la pause était permanente. Le carrousel n'avançait jamais.

La pause au survol est supprimée. Ne l'arrête plus qu'une interaction réelle —
saisir le formulaire — parce qu'on ne déplace pas le décor sous quelqu'un qui
écrit. Choisir une vue à la main relance le décompte au lieu de figer le ruban :
`setInterval` est devenu `setTimeout` avec `index` en dépendance.

**Leçon retenue.** Le « pause au survol » est un réflexe correct sur un carrousel
qui occupe une bande. Sur un élément plein écran, c'est un interrupteur toujours
enfoncé. La règle dépend de la surface, pas du composant.

### Gabarit de bannière unifié

`.entete-page` avait pour seule contrainte `padding-top: 126px` ; l'accueil avait
`height: 100vh; min-height: 800px`. Le gabarit de l'accueil s'applique désormais
aux huit pages. La bannière est passée en **grille** et non en flex : `.bloc` doit
garder son comportement de bloc et s'étirer jusqu'à sa largeur maximale ; en
élément flex il se serait rétracté à la largeur de son texte.

### Sections sur l'axe central

Quatre sections de l'accueil — Services, Ce que change l'adhésion, Comment ça se
passe, Témoignages — passent en `section--centre`. Le corps des grilles revient
au fer à gauche : un paragraphe long centré se lit mal, les débuts de ligne ne
s'alignent plus.

Deux chapeaux ont un nombre de lignes voulu. Il ne se décrète pas, il se règle
par la largeur de ligne et l'échelle du texte :

- `chapeau--une-ligne` (services) : au-delà de 1100 px, `white-space: nowrap` et
  une taille en `clamp(12.5px, 1.15vw, 15.5px)`. Le texte se réduit avec la
  fenêtre, il ne peut donc pas déborder. En dessous il se replie seul.
- `chapeau--deux-lignes` (définition du CGA) : 260 caractères dans un bloc qui en
  affiche environ 160, donc deux lignes ; `text-wrap: balance` les égalise.

### La progression se ressent

`EtapesProgression`, composant client. Un rail continu relie les trois pastilles
et se remplit derrière le lecteur ; chaque carte s'allume quand elle est à plus
de moitié visible. Franchissement observé par `IntersectionObserver` et non
calculé au défilement : le fil principal n'est réveillé qu'aux moments utiles.
La progression ne redescend jamais — remonter la page n'éteint pas ce qui a été
lu. `prefers-reduced-motion` donne tout d'emblée : la mise en scène disparaît,
pas l'information.

### Témoignages nommés

Les quatre emplacements portaient leur propre mode d'emploi à l'écran
(« Emplacements réservés : transmettez-nous vos témoignages réels »). Le badge
est retiré, la clé `note` supprimée des deux catalogues.

Quatre témoignages nommés les remplacent, un par angle du parcours : création,
suivi comptable, formation, contrôle fiscal. **Les noms et les entreprises sont
inventés** — Estelle Mbarga, Rodrigue Fotso, Aïcha Ndongo, Serge Ekwalla — et
doivent être remplacés par des témoignages réels avec autorisation écrite avant
mise en ligne publique. Aucune entreprise existante n'est citée, précisément pour
qu'aucun tiers ne se voie attribuer une recommandation qu'il n'a pas donnée.

Même traitement pour le badge △ de la page Estimation : c'était une note interne
(« à valider par le fiscaliste »), déplacée en commentaire de code. L'estimateur
porte déjà l'avertissement destiné au client.

### Pied de page : rester en lien

Une bande dédiée, séparée de la grille de liens par un filet.

**Infolettre.** Aucun point d'entrée n'existe côté FastAPI. Le formulaire compose
le message et ouvre le client de messagerie du visiteur, à destination de
`contact@cga-brcgroup.com` : la demande part réellement, à la bonne adresse, et
personne ne se croit inscrit alors qu'un serveur aurait jeté sa saisie en
silence. Le jour où `transverse` exposera `POST /infolettre`, seule la fonction
`envoyer` change.

**Réseaux.** Facebook, LinkedIn, WhatsApp (`wa.me/237699902184`). Silhouettes
pleines et non linéaires, contrairement au reste du jeu d'icônes : un logo de
marque se reconnaît à sa forme, un contour le rendrait méconnaissable.
`rel="noopener noreferrer"` — on n'envoie pas l'adresse de la page consultée à un
tiers.

### Vérifié

25 pages prégénérées, `tsc` et `eslint` sans reproche. Sur le serveur de
développement : les seize routes en 200 dans les deux langues, et dans le HTML
servi — quatre `section--centre`, les deux modificateurs de chapeau, `etapes__rail`
avec trois `data-atteinte`, les quatre noms de témoins, zéro occurrence
d'« Emplacements réservés », le champ d'infolettre et les trois liens sociaux. Les
règles CSS correspondantes ont été relues dans la feuille effectivement servie.

**Non vérifié : le rendu visuel.** L'extension Chrome n'atteint pas `localhost`.
Le contrôle porte sur le balisage et les règles servies, pas sur ce que vous voyez.

### Reste ouvert

Inchangé, plus :

- **Le jeton GitHub est toujours invalide.** Les commits s'accumulent en local.
- L'infolettre passe par `mailto:` faute de point d'entrée serveur ; à basculer
  sur `transverse` quand il existera.
- Les quatre témoignages sont fictifs et doivent être remplacés.

---
