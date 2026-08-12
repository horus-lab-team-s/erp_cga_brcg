# Journal de bord — ERP et vitrine CGA Broad Range Consulting

Ce journal consigne les échanges avec le cabinet, les décisions prises et leur
motif. Il est versionné avec le code : une décision sans son pourquoi se perd en
quelques semaines, et le code seul ne dit jamais ce qui a été écarté.

L'entrée la plus récente est en tête. Chaque entrée dit : ce qui a été demandé,
ce qui a été décidé et pourquoi, ce qui a été livré, ce qui reste.

---

## 12 août 2026 (suite) — Le contenu du site passe au backend

### Ce qui a été demandé

Quatre choses, dans le désordre où elles sont venues.

1. Pouvoir **revenir au site** depuis la page de connexion à l'ERP.
2. **Vérifier que le site a un backend**, et sinon l'y brancher, de façon que
   tout soit modifiable depuis le backend — le site n'étant qu'une vitrine.
3. L'annonce doit apparaître **sur toutes les pages** : en passant d'une page à
   l'autre, on doit la revoir.
4. Respecter la **Clean Architecture** déjà appliquée, bien organiser le backend,
   et **commenter le code partout** pour qu'on comprenne ce qui a été fait.

### Ce qui a été constaté, et qui change la réponse

**Le backend existe déjà, et il est propre.** `Backend_erp_cga` est un monolithe
modulaire FastAPI en Clean Architecture : onze contextes bornés, quatre cercles
par contexte, deux surfaces publiques (`contrats.py` pour les entités, `api.py`
pour les cas d'usage), et une batterie de tests qui **refusent** une dépendance
allant d'un cercle interne vers un cercle externe. La question n'était donc pas
« faut-il un backend » mais « pourquoi le contenu de la vitrine n'y est-il pas ».

Réponse : parce qu'il avait été écrit en TypeScript, dans le frontend. Une faute
de frappe dans un article demandait un développeur et un déploiement. C'est cela
qui a été corrigé.

### Ce qui a été décidé, et pourquoi

**Un douzième contexte borné : L · Vitrine publique.** Et non un dossier de
fichiers dans le frontend, ni une extension d'un contexte existant.

* *Pourquoi un contexte à lui seul.* Le contenu éditorial n'est pas une donnée
  fiscale. Le mettre dans le Référentiel aurait mélangé « le taux de TVA au
  15 juillet 2026 » et « l'article du blog sur la patente » dans le même module.
* *Pourquoi il ne lit aucun autre contexte.* Du contenu qui aurait besoin d'un
  paramètre légal ne serait plus du contenu, ce serait un calcul — et il
  appartiendrait au contexte qui le porte. Le jour où l'on voudra afficher un
  barème sur le site, la bonne réponse sera une route du Référentiel appelée par
  le site, pas une arête ajoutée au graphe. Cette contrainte est inscrite dans
  `tests/test_architecture.py`, elle n'est pas qu'une intention.
* *Pourquoi personne ne le lit non plus.* Le contenu éditorial n'a rien à dire au
  métier fiscal.

**Les quatre cercles, sans exception.** `domaine/` porte les entités et le port
`DepotContenuVitrine` ; `application/` porte le service de lecture ;
`adaptateurs/sortant/` lit le YAML ; `adaptateurs/entrant/` expose les routes.
Le service ne lit aucun fichier : il reçoit un dépôt. C'est ce qui permet de
l'éprouver sur un dépôt en mémoire, sans disque — et les tests écrits ainsi sont
la preuve que l'inversion de dépendance sert à quelque chose plutôt que d'être
une figure de style.

**Le corps d'un article est une suite de blocs typés, pas du Markdown ni du
HTML.** Trois raisons, dans cet ordre. La sécurité d'abord : un contenu qui
arrive du backend et qui serait du HTML devrait être assaini avant affichage ;
des blocs typés ne portent que du texte, il n'y a rien à injecter. Le rendu
ensuite : chaque type de bloc a son style propre. L'édition enfin : une personne
qui corrige le YAML voit la structure de l'article.

**Le YAML plutôt qu'une base, pour commencer.** Parce que la personne qui corrige
une faute, au cabinet, doit pouvoir le faire sans qu'on ait d'abord construit un
écran d'administration. Le YAML se lit, se commente, se relit en revue, et se
versionne : on sait qui a changé quoi et quand. Le port est déclaré dans le
domaine ; le jour venu, un `DepotContenuVitrineSql` le réalisera et seul
l'adaptateur changera.

**Un fichier malformé fait échouer le chargement.** Rubrique inconnue, date
incohérente, bloc sans type : le démarrage est refusé. Mieux vaut une panne
bruyante et immédiate qu'un blog amputé de trois articles que personne ne
remarque avant des semaines.

**Le site garde un contenu de secours.** `app/lib/blog.ts`, `annonces.ts` et
`partenaires.ts` restent au dépôt, mais changent de statut : ce ne sont plus la
source, c'est le **dernier état connu**. Si le backend est arrêté, en cours de
déploiement, ou joignable une seconde trop tard, la vitrine affiche ce
contenu-là plutôt que du vide — ce qui serait pire. La source est le YAML, et
c'est écrit en tête du module de lecture pour que personne ne s'y trompe.

**Deux `null` qu'il ne faut surtout pas confondre.** « Le backend répond qu'il
n'y a pas d'annonce aujourd'hui » et « le backend ne répond pas » appellent des
conduites opposées : dans le premier cas on n'affiche rien, dans le second on
affiche le secours. Les confondre ferait réapparaître toute seule une annonce que
le cabinet vient de retirer. D'où le type `Lecture<T>` et son champ `repondu`.

**L'annonce réapparaît à chaque page — et le mécanisme n'est pas celui qu'on
croit.** Le site est une application d'une seule page : en passant de l'accueil au
blog, la coquille n'est pas reconstruite et le bandeau n'est pas remonté. Sans
traitement, l'annonce disparue au bout de trente secondes ne serait plus jamais
revenue de toute la visite. La solution retenue est une **clé React portant le
chemin courant** : changer de page remonte le composant, et tout son état repart
à neuf — décompte et animation compris. Un effet de remise à zéro aurait fait la
même chose, en moins lisible, en plus fragile, et le linter le refusait à juste
titre.

La fermeture explicite, elle, ne revient pas. C'est la différence entre « je n'ai
pas eu le temps de lire » et « je ne veux pas de ça » : le décompte redémarre, le
refus est retenu pour toute la visite.

**Deux sorties vers le site public.** Depuis la page de connexion, qui est un
cul-de-sac — ni en-tête, ni pied, ni menu — et depuis la barre latérale de
l'ERP. Dans les deux cas, un libellé explicite : le logo ramenait déjà à
l'accueil, mais un logo cliquable est une convention, pas une indication.

### Ce qui a été livré

Backend — `app/contextes/vitrine/` : `domaine/entites.py`, `domaine/ports.py`,
`application/service_contenu.py`, `adaptateurs/sortant/depot_yaml.py`,
`adaptateurs/entrant/routes_http.py`, `contrats.py`, `api.py`. Contexte enregistré
dans `main.py`, dans `config.py`, dans `tests/test_architecture.py` et dans
`Docs/architecture/01-contextes-bornes.md`. Quatre routes : sommaire du blog avec
les comptes par rubrique, article avec ses voisins de lecture, annonce à une
date, institutions.

Contenu — `Contenu_vitrine/articles.yaml`, `annonces.yaml`, `institutions.yaml` :
quatorze articles, une annonce, quatre institutions, chaque fichier ouvert par un
commentaire qui explique quoi y écrire et ce qu'il ne faut pas y casser.

Frontend — `app/lib/contenu-vitrine.ts`, seul point du site qui sait où trouver le
contenu ; blog, article, ruban d'institutions et bandeau d'annonce branchés
dessus ; bouton de retour au site sur la connexion et dans la barre de l'ERP.

Documentation — en-têtes ajoutés aux six pages de la vitrine qui n'en avaient
qu'une ligne, et à `BarreLaterale.tsx`, seul fichier du frontend qui n'avait aucun
bloc de documentation.

Vérifié : **237 tests backend** (contre 202 avant ce lot), `ruff` au vert,
`tsc` et `eslint` sans un avertissement, build Next complet à 55 pages, et les
quatre routes exercées sur le backend en marche.

### Ce qui reste

- **Un écran d'administration** pour éditer le contenu sans toucher au YAML.
  Le port est prêt ; c'est l'adaptateur et l'interface qui manquent.
- **L'invalidation du cache** : une correction du YAML n'est visible qu'après
  redémarrage du backend. Assumé tant que le cabinet corrige par lots ; à traiter
  le jour où l'édition devient quotidienne. L'endroit est identifié et commenté.
- **Le reste du corpus Facebook** : une quarantaine de publications lues sur 113.

---

## 12 août 2026 — Blog, annonces de site, et la règle des bannières

### Ce qui a été demandé

Trois choses, en plus de la finition de la vitrine déjà engagée.

1. **La hauteur des bannières.** L'accueil est désormais **la seule page** qui
   garde une bannière pleine hauteur. Toutes les autres pages ont une bannière
   réduite.

2. **Un blog.** Les 113 captures rassemblées la veille dans
   `Docs/publications-facebook-blog/` servent de matière. Le blog a deux
   fonctions : renseigner les clients et leurs conseillers sur les **textes
   administratifs qui ont changé**, et porter les **annonces** du cabinet. Le
   client a insisté : il faut que les publications soient observées de près, et
   que chaque article se partage sur **Facebook ou WhatsApp** sous une forme qui
   donne envie de cliquer et d'entrer sur le site pour lire la suite. Cela
   suppose une nouvelle entrée de menu.

3. **Une annonce de site.** Un message accrocheur qui apparaît sur toutes les
   pages, que le visiteur peut **fermer**, et qui **disparaît de lui-même au
   bout de 30 secondes** pour ne pas perturber la navigation.

Demande transversale : **tout enregistrer**, échanges et réponses, pour que le
contexte ne se reperde pas d'une séance à l'autre. D'où ce journal.

### Ce qui a été décidé, et pourquoi

**Les bannières.** La règle était déjà appliquée dans le lot en cours :
`EnteteDePage` a été ramené à la moitié de la hauteur du héros d'accueil
(`50svh`, minimum 400 px, 280 px sous 900 px de large), pendant que le composant
`Heros` — plein écran, carrousel à messages, formulaire — reste réservé à
`app/[locale]/(vitrine)/page.tsx`. La demande confirme le choix et le fige :
**toute nouvelle page passe par `EnteteDePage`, jamais par `Heros`.** Le blog et
les articles s'y conforment.

**Le corpus Facebook n'est pas republiable tel quel.** C'est la décision la plus
importante de la journée, et elle va à l'encontre de l'usage le plus direct des
fichiers. En les regardant :

- ce sont des **captures de navigateur**, pas des visuels : on y voit la colonne
  de commentaires, les boutons Facebook, et l'identité de la personne connectée
  (« Commenter en tant que Loïc Tonba ») ;
- `pub-50` contient une **conversation WhatsApp privée** avec un prospect,
  floutée seulement en partie ;
- plusieurs images appartiennent à des **tiers** : dessins signés GABS, dessin
  filigrané `ledauphine.com`, personnage des Minions. Les publier sur le site du
  cabinet exposerait celui-ci à une réclamation ;
- les plus anciens visuels portent une **adresse électronique périmée**
  (`info@brconsulting-cm.com`), remplacée depuis par `contact@cga-brcgroup.com`.

Le corpus est donc traité comme une **source rédactionnelle** : les faits sont
extraits, les textes réécrits, et les illustrations prises dans les photographies
déjà présentes au dépôt. Le jour où le cabinet fournira les exports propres de
ses visuels carrés — qui sont sa création et qui sont bons — ils remplaceront les
photographies sans rien changer d'autre que le chemin d'image dans `blog.ts`.

**La ligne éditoriale est celle du cabinet, pas une invention.** En observant les
113 publications, quatre rendez-vous reviennent, et ils deviennent les rubriques
du blog :

| Rubrique du blog | Origine dans les publications |
| --- | --- |
| Le saviez-vous ? | Visuels carrés « Le saviez-vous ? », faits fiscaux et juridiques |
| Vrai ou faux ? | Publications « Vrai ou Faux ? », idées reçues passées au crible |
| Lundi comptable | « Lundi comptable avec Aïcha », modes d'emploi comptables |
| Mercredi juridique | « Mercredi juridique », cas pratiques traités par le juriste Owona |
| Le coin du fiscaliste | « Conseils de notre fiscaliste Kamdem », l'impôt expliqué |
| Annonces | Offres, packs de formalisation, vœux, informations de service |

Reprendre les rendez-vous du cabinet plutôt qu'un découpage abstrait a un
avantage direct : l'audience Facebook reconnaît les noms **et les visages** —
Aïcha, Owona, Kamdem sont des personnages installés, avec leur jour de la semaine
— et le cabinet sait déjà alimenter ces cases, puisqu'il le fait chaque semaine.

**Le partage précède la lecture.** Un article n'est pas d'abord une page, c'est
d'abord une vignette dans un fil ou dans une conversation WhatsApp. Chaque
article porte donc ses métadonnées Open Graph — titre, résumé, image, date — et
une accroche courte, écrite pour être lue seule. Les boutons de partage visent
Facebook, WhatsApp et la copie du lien : ce sont les trois canaux réels de la
clientèle camerounaise du cabinet, et WhatsApp compte au moins autant que
Facebook.

Deux réglages en découlent, contre-intuitifs mais vérifiés sur le rendu :

- **L'illustration doit être en paysage et faire au moins 1 200 px de large.**
  En dessous de 600 px, Facebook renonce à la grande carte et met une imagette
  carrée à gauche du titre — l'inverse exact de l'effet recherché. Le premier
  jet de l'article « Lundi comptable » illustrait par le portrait de la
  comptable, un carré de 480 px : il a été remplacé par une photographie de
  1 400 px. La contrainte est écrite en tête de `blog.ts`.
- **Les dimensions ne sont pas déclarées dans les métadonnées.** Annoncer
  1200 × 630 pour une photographie qui fait 1400 × 933 fait recadrer la vignette
  de travers. Facebook mesure très bien le fichier lui-même.
- **L'adresse partagée est calculée, pas lue dans le navigateur.** Elle est
  reconstruite à partir du domaine, de la langue et du chemin. Les boutons sont
  donc bons dès le rendu serveur, et le lien partagé est la version canonique,
  sans le paramètre de campagne ni l'ancre que le visiteur traîne derrière lui.
  `NEXT_PUBLIC_SITE_URL` couvre la préproduction.

**L'annonce s'efface deux fois.** Le visiteur peut la fermer, et elle part seule
au bout de 30 secondes. La fermeture est mémorisée pour la durée de la session
(`sessionStorage`) : une annonce qui revient à chaque page est exactement le
défaut qu'on cherchait à éviter. Le décompte est suspendu quand le pointeur est
sur le bandeau ou quand le clavier y entre — retirer sous les doigts d'un
visiteur le lien qu'il allait cliquer serait pire que ne rien afficher. Et un
visiteur qui a demandé `prefers-reduced-motion` n'a pas de barre de décompte
animée.

### Ce qui a été livré

- `Docs/journal-de-bord.md` — ce journal.
- `app/lib/blog.ts` — rubriques, articles, tri, voisinage, recherche par slug.
- `app/lib/annonces.ts` — l'annonce en cours, avec sa fenêtre de validité.
- `app/components/vitrine/BandeauAnnonce.tsx` — le bandeau refermable.
- `app/components/vitrine/CarteArticle.tsx` — la vignette d'article.
- `app/components/vitrine/PartageArticle.tsx` — Facebook, WhatsApp, copie du lien.
- `app/components/vitrine/FiltreRubriques.tsx` — le filtre du sommaire, fait de
  liens et non de boutons : chaque rubrique a son adresse
  (`/blog?rubrique=lundiComptable`), donc son signet, son envoi par message et
  son bouton « précédent », et le filtrage ne coûte pas une ligne de JavaScript.
- `app/lib/site.ts` — l'adresse publique du site, et `metadataBase` posée sur la
  mise en page racine : sans elle, toute image d'aperçu déclarée par un chemin
  relatif est ignorée et le lien part nu.
- `app/[locale]/(vitrine)/blog/page.tsx` — le sommaire.
- `app/[locale]/(vitrine)/blog/[slug]/page.tsx` — l'article.
- Entrée « Blog » dans la barre de navigation, dans le menu du téléphone et dans
  le pied de page ; libellés fr et en. Elle est placée après « Le CGA » et avant
  « Estimation » : le blog relève de ce que le cabinet dit de lui-même, et le
  reléguer en fin de barre l'aurait rendu invisible, alors que c'est par lui que
  le trafic de Facebook et de WhatsApp entrera.
- Le repère de menu suit désormais la **section** et non la seule page :
  `/blog/mon-article` marque « Blog » comme courant. L'égalité stricte laissait
  la barre muette dès qu'on ouvrait un article.
- Styles dans `app/styles/vitrine.css`.

Vérifié : `npm run lint` sans avertissement, `npm run build` complet, 47 pages
générées dont les vingt pages d'articles (dix articles × deux langues), et le
rendu contrôlé page par page sur le serveur de développement — sommaire, filtre
par rubrique, article, version anglaise, et métadonnées Open Graph.

### Deuxième passe du même jour — dépouillement poursuivi

Le dépouillement a repris après la première livraison. Environ quarante des 113
publications ont maintenant été lues, réparties sur toute la période 2018-2026.
Quatre articles s'y sont ajoutés, et un a été enrichi :

- **« Pas encore de clients, donc pas d'obligations fiscales » — vrai ou faux ?**
  (pub-19). L'obligation ne naît pas de la recette mais de l'immatriculation : la
  déclaration néant est due, et la pénalité frappe le silence, pas le montant.
  C'est la publication qui a fait apparaître la rubrique « Vrai ou faux ? ».
- **À qui s'applique réellement l'IGS** (pub-22), qui a fait apparaître « Le coin
  du fiscaliste ». Point central retenu : l'IGS ne dépend pas toujours du
  bénéfice réalisé, mais de l'existence et de l'activité de l'entreprise.
- **Les huit obligations comptables de début d'année** (pub-38 et pub-25), la
  liste d'Aïcha, de la mise à jour de l'exercice écoulé à l'anticipation de la
  DSF.
- **Dossier propre, décision rapide** (pub-58), sur ce qu'une banque lit
  réellement dans un dossier de financement.
- **Adhérer au CGA** enrichi (pub-55 et pub-72) de deux choses qui manquaient et
  qui sont le vrai argument du centre agréé : l'assistance permanente d'un
  inspecteur des impôts et l'accès aux formations du centre, puis la liste des
  prestations souscriptibles à la carte.

Deux prudences de rédaction sur cette passe :

- La publication sur la **DSF 2026** annonce « jusqu'à quand payer sans
  pénalités » mais ne donne pas les dates dans la partie visible de la capture.
  Aucune échéance n'a donc été inventée : l'article dit que le délai dépend du
  régime et invite à le faire vérifier. Les dates viendront du cabinet.
- Plusieurs publications sont **inutilisables** et resteront hors du blog : les
  dessins de presse filigranés `ledauphine.com`, les dessins signés GABS, les
  images de Minions, et la citation d'Aliko Dangote illustrée par une
  photographie de tiers.

### Ce qui reste

- **Dépouiller le reste du corpus.** Une quarantaine de publications ont été
  lues ; les soixante-dix autres contiennent d'autres faits utiles. Ajouter un
  article revient à ajouter un objet dans `ARTICLES`.
- **Récupérer les dates d'échéance de la DSF** auprès du cabinet, par régime
  d'imposition, pour compléter l'article de début d'année.
- **Obtenir les visuels propres.** Demander au cabinet les fichiers d'origine de
  ses carrés « Le saviez-vous ? » et de ses affiches d'offre, sans le chrome
  Facebook et avec l'adresse électronique à jour.
- **Vérifier les faits fiscaux avec le cabinet.** Les articles citent des règles
  tirées de publications de 2017 et 2018. Le droit a pu bouger : chaque article
  porte la date de la publication d'origine, et le cabinet doit confirmer ce qui
  est encore en vigueur avant mise en ligne.
- **Traduction anglaise du corps des articles.** Les libellés d'interface sont
  bilingues ; le corps des articles est pour l'instant en français dans les deux
  langues, ce qui est le comportement voulu tant que le cabinet n'a pas fait
  traduire.

---

## 11 août 2026 — Finition de la vitrine

Passe de finition menée avant la demande du blog, encore non commitée à
l'ouverture du 12 août.

- **Ruban des institutions.** DGI, CNPS, ONECCA, OHADA, en bande défilante sur
  l'accueil. Choix assumé et consigné dans `app/lib/partenaires.ts` : ce ne sont
  **pas des partenaires commerciaux**, et le libellé de la section le dit. Afficher
  le logo d'une entreprise privée sous le mot « partenaire » affirmerait une
  relation contractuelle ; ces quatre institutions-là sont le cadre dans lequel
  un centre de gestion agréé travaille par nature, et le dire est vérifiable.
- **Connexion de démonstration.** Le formulaire de `/connexion` compare deux
  constantes **dans le navigateur**. Ce n'est pas une authentification, le fichier
  le dit en tête et la page le dit au visiteur. La vraie authentification
  appartient au backend FastAPI ; aucune donnée client réelle ne doit passer
  derrière cet écran avant.
- **Bannières des pages intérieures** ramenées à la moitié de la hauteur, avec
  fondu entre deux photographies quand la page en fournit deux.
- **Étapes de progression** rendues génériques : le composant reçoit désormais ses
  étapes, ce qui a permis de le réemployer pour le parcours d'adhésion en quatre
  temps.
- **Estimateur** — correction d'un défaut qui rendait le champ « capital »
  insaisissable : il réaffichait `Math.max(capital, capitalMin)`, si bien
  qu'effacer un chiffre réécrivait le minimum légal à chaque touche. La valeur
  saisie est maintenant conservée comme texte, et le bornage a lieu au calcul.
- **Corrections de fond** : la SA a bien une ligne au barème (le contraire avait
  été supposé à tort) ; « Le cabinet » devient « Le CGA » au menu et au pied ; le
  second mobile `+237 676 887 686` entre dans la barre utilitaire, les deux
  mobiles avant le fixe, parce qu'au Cameroun on appelle et on écrit depuis un
  mobile et que le fixe sert de repli.
