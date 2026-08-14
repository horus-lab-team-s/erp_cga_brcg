# Journal de bord — ERP et vitrine CGA Broad Range Consulting

Ce journal consigne les échanges avec le cabinet, les décisions prises et leur
motif. Il est versionné avec le code : une décision sans son pourquoi se perd en
quelques semaines, et le code seul ne dit jamais ce qui a été écarté.

L'entrée la plus récente est en tête. Chaque entrée dit : ce qui a été demandé,
ce qui a été décidé et pourquoi, ce qui a été livré, ce qui reste.

---

## 14 août 2026 — Le lot part sur le dépôt personnel

### Ce qui a été demandé

Pousser le projet sur `github.com/LoicTonba/erp_cga_brcg`, sur une branche
destinée à être fusionnée.

### Ce qui a été fait

Le dépôt de travail est `horus-lab-team-s/erp_cga_brcg`. Le dépôt personnel a
été ajouté comme second remote sous le nom `loic` plutôt que de détourner
`origin` : deux destinations différentes doivent porter deux noms différents,
sinon un `git push` distrait envoie le travail au mauvais endroit.

Son `main` est le résultat de la fusion de la demande de tirage n° 1 et porte
exactement l'arbre de `819e5a3`, qui est un ancêtre direct de la branche
courante. La fusion se fera donc sans conflit et sans historique étranger — la
branche poussée n'apporte que les deux commits qui manquent : le passage du
contenu au backend avec le blog, et la revue de design.

### Ce qui reste hors du dépôt, et pourquoi

Trois éléments étaient présents dans le répertoire de travail sans être suivis.
Ils sont désormais nommés dans `.gitignore`, pour que leur exclusion soit une
décision écrite et non un oubli reconduit à chaque commit.

- **`Docs/publications-facebook-blog/`** — 74 Mo de captures d'écran. C'est la
  matière première des articles, pas le produit. Git ne sait pas oublier un
  binaire : une fois entré dans l'historique, il pèse sur chaque clone à venir,
  y compris ceux qui n'ont que faire des captures.
- **`mail+paiement/` et `mail+paiement.zip`** — modules Django d'envoi de
  courriels et d'encaissement mobile money, extraits d'un autre projet en vue
  d'une greffe future. Ils ne sont branchés à rien ici, et le dossier traîne ses
  `__pycache__`. Ils entreront au dépôt quand ils seront intégrés, adaptés au
  backend FastAPI, et non avant — voir le rappel Taramoney plus bas dans ce
  journal.

### Vérifications avant envoi

`tsc` sans erreur, `eslint` sans avertissement, 237 tests backend au vert.

---

## 13 août 2026 — Revue de design, page par page

### Ce qui a été demandé, et ce qui a été fait

Une revue complète du rendu, après parcours du site. Point par point.

**Les bannières.** Contenu centré, sur l'accueil comme sur les pages
intérieures. Sur l'accueil, le texte est centré dans la place que lui laisse le
formulaire, qui garde sa colonne — le centrer sur la largeur entière l'aurait
fait passer dessous. Le chapeau passe en `text-wrap: balance` : sur un texte
centré, ce qui se voit d'abord est l'inégalité des lignes.

**Deux boutons magenta dans la même bannière.** C'était le cas sur l'accueil —
l'action du carrousel et l'envoi du formulaire — et sur la connexion. Deux
boutons de la couleur primaire ne hiérarchisent plus rien : l'œil ne sait plus
lequel est l'action principale. Nouvelle variante `bouton--inverse`, blanc plein,
pour la seconde action forte d'un écran sombre. Elle garde le même poids visuel
sans disputer la couleur de marque.

**Les cartes de service.** L'icône était accrochée en bas à gauche de la
photographie, où elle passait pour une vignette de coin. Elle est désormais
ronde, centrée en tête, et **logée dans une échancrure** du corps de la carte.
L'entaille est faite au masque plutôt qu'à la bordure : elle découpe réellement
le fond, si bien que la photographie transparaît dans l'arc — une bordure de la
couleur du fond aurait donné un anneau plat, pas un creux.

**Le prix.** En simple ligne de texte au bas de la carte, il se lisait comme une
mention légale et se perdait à côté du lien d'action. Il est passé dans sa propre
pastille cerclée, qui s'inverse au survol. C'est l'information que le visiteur
cherche en premier ; elle devait se voir en premier.

**Le ruban des témoignages** passe de 11 à 18 secondes par carte. Régler les deux
bandes sur la même cadence était une erreur de raisonnement : un logo se
*reconnaît* d'un coup d'œil, un témoignage se *lit*. À vitesse égale, la seconde
bande passait avant qu'on ait fini la première phrase.

**« Parlons de votre projet ».** Tout sur l'axe central, et les boutons **sous**
le texte. Auparavant le texte était à gauche et les boutons à droite : sur un
écran large, un mètre séparait la phrase de l'action qu'elle appelait. Le
bandeau étant commun aux pages, la correction vaut partout d'un coup.

**La navigation reste à l'écran.** `fixed`, et non `sticky` : les deux gardent la
barre visible, mais `sticky` occupe sa place dans le flux et pousserait toute la
page de 126 px vers le bas — or les bannières compensent **déjà** un en-tête en
superposition. Le fond ne se teinte qu'une fois la page défilée : sur la
photographie, une barre opaque couperait l'image ; plus bas, du blanc sur fond
clair serait illisible.

**Flèche de retour en haut**, en bas à droite, au-delà d'un écran et demi de
défilement. Posée plus haut que le bandeau d'annonce pour ne pas recouvrir son
bouton de fermeture.

**La page de connexion reçoit l'en-tête et le pied.** Décision qui **renverse**
le choix initial. Elle vivait sans navigation, au motif qu'une page de connexion
offrant dix autres chemins détourne de la seule action attendue. Le raisonnement
valait pour la concentration, mais il coûtait plus cher ailleurs : dépouillée de
tout repère, la page donnait le sentiment d'avoir quitté le site pour un service
tiers — exactement l'inquiétude qu'on ne veut pas susciter au moment de saisir un
identifiant. Elle ne porte toujours ni bandeau d'appel, ni annonce : on ne
relance pas commercialement quelqu'un qui se connecte.

**La direction générale mise en avant** sur la page Le CGA, hors de la grille de
l'équipe — une carte identique à celles de ses collaborateurs l'aurait noyée
parmi eux. Portrait, fonction, présentation, et lien vers son site personnel.

**Les agences** reprennent le dispositif de l'échancrure, et leurs trois lignes
sont hiérarchisées : ville, quartier en capitales, précision. Elles se suivaient
auparavant au fer à gauche dans un même paragraphe, où l'adresse se confondait
avec la note.

**Contact** — la phrase « le téléphone reste le champ principal : beaucoup de nos
clients n'utilisent pas de messagerie électronique » est retirée. Le retrait est
juste : c'était une note de conception, pas un argument de vente, et lue par un
prospect elle donnait de la clientèle du cabinet une image peu flatteuse. Le
constat guide toujours la mise en page — le téléphone reste le champ exigé — mais
il n'est plus écrit.

### Seconde passe du 13 août — reprise de l'échancrure, et fin des impasses

**L'échancrure était au mauvais endroit.** Premier essai : l'icône logée à la
jonction entre la photographie et le texte, au milieu de la carte. Ce n'était pas
le dessin demandé. L'icône doit chevaucher **l'arête haute** de la carte — moitié
au-dessus, moitié dedans — et l'échancrure se creuser juste sous elle, dans le
bord supérieur.

Le point technique qui commande toute la structure : **un masque s'applique à
toute la descendance de l'élément masqué**. L'icône placée dans la carte aurait
donc été rognée par l'échancrure même qui doit l'accueillir, c'est-à-dire coupée
en deux. D'où une enveloppe qui n'est masquée par rien et porte les deux — la
carte échancrée d'un côté, l'icône de l'autre.

Trois mesures vont ensemble et ne se changent pas séparément : icône de 60 px,
échancrure de rayon 38, réserve haute de 30 px — exactement la moitié de l'icône.
Le soulèvement au survol a été retiré des cartes échancrées : la carte montait de
3 px pendant que l'icône restait en place, et le liseré devenait inégal.

**Quatre entrées du méga-menu menaient à la page Contact.** Prestations
ponctuelles, domiciliation, assistance juridique, conseil et audit : autant
d'impasses. Un visiteur qui clique sur « Domiciliation » veut savoir ce que
couvre la domiciliation, pas remplir un formulaire — on lui demandait de
s'engager avant de lui avoir dit ce qu'on vendait.

Chacune a désormais sa fiche, à `/services/<slug>`, sur un gabarit unique :
qu'est-ce que c'est, ce qui est compris, pour qui, comment ça se passe, combien.
Quatre pages écrites séparément auraient divergé au premier ajout ; le contenu
vit donc dans les messages et la mise en page une seule fois. L'ordre des
sections est l'argumentaire : ce qui est compris **avant** pour qui, et le tarif
en dernier — un montant lu avant ce qu'il couvre paraît toujours cher.

Les trois services qui ont déjà une page propre — création, adhésion, formations
— n'y passent pas.

**Deux chapeaux de bannière sur deux lignes** (Estimation, Blog). Le nombre de
lignes ne se décrète pas : on élargit la colonne de lecture et `text-wrap:
balance` répartit les deux lignes à longueur voisine. Sous 900 px la contrainte
tombe et le texte se replie sur ce qu'il faut — deux lignes sur un téléphone
donneraient des caractères minuscules.

⚠️ **Le contenu anglais des quatre fiches est encore en français.** Le gabarit et
l'interface sont bilingues, mais les textes n'ont pas été traduits : les faire
passer à la machine sur un contenu commercial aurait produit de l'anglais
approximatif au nom du cabinet. À faire traduire.

### 14 août 2026 — Le pied de page, et trois liens qui tombaient dans le vide

**Vérification demandée, et elle a trouvé quelque chose.** Le cabinet a demandé
de contrôler que les liens du pied mènent bien quelque part. Les vingt entrées
des trois colonnes fonctionnaient — les six formes juridiques vers l'estimateur
pré-rempli, les ancres du CGA, le blog, les formations. Mais les **trois liens de
la dernière ligne — mentions légales, confidentialité, conditions générales —
tombaient en 404 depuis le premier jour.** Ils étaient liés sans jamais avoir été
écrits.

C'est le genre de défaut qui passe inaperçu longtemps et se paie d'un coup : ce
sont précisément les pages qu'un visiteur méfiant va vérifier avant de confier
son numéro, et elles sont par ailleurs obligatoires.

Les trois pages existent maintenant, sur un gabarit commun. **Tout ce que le
dépôt sait de façon vérifiable y figure** — dénomination, agrément, boîte
postale, contacts — et **tout le reste est marqué « à compléter » en toutes
lettres** : numéro RCCM, capital social, hébergeur, responsable de publication
nommé, durées de conservation, clause de médiation. Rien n'a été inventé, et
c'est délibéré : une mention légale fausse est pire qu'une mention absente, parce
qu'elle engage le cabinet sur des informations qu'il n'a pas données et qu'elle
passe inaperçue précisément parce qu'elle a l'air complète.

**Le cabinet doit relire et compléter ces trois pages avant toute mise en ligne.**

Corrigé au passage : « Domiciliation » pointait encore vers la page Contact,
du temps où elle n'avait pas de fiche. Elle mène désormais à la sienne.

**Le panneau des services s'ajuste à son contenu.** Il gardait la largeur héritée
de l'ancien méga-menu à trois colonnes, alors qu'il ne porte plus qu'une liste de
sept intitulés : la moitié de sa surface était vide. `width: max-content` le fait
mesurer sa plus longue entrée, borné pour ne pas déborder de la fenêtre.

**Le pied de page, troisième allègement.** La bande « Suivez-nous » — encadrée de
deux filets, sur toute la largeur, pour trois logos et un numéro — a disparu ;
les logos ont rejoint la première colonne. Le téléphone fixe et le courriel en
sont retirés, pour la même raison que l'agrément la veille : la barre utilitaire
est désormais **fixe**, donc lisible à tout moment, y compris au bas d'une page
longue. Répéter une coordonnée qui ne quitte jamais l'écran n'apprend rien.

Sur téléphone, les colonnes passent à deux au lieu de quatre empilées, avec des
interlignes resserrés — un pied de page se parcourt du pouce, il ne se lit pas.
En dessous de 420 px, retour à une colonne, mais le pied est alors déjà bien plus
court qu'avant.

**La signature est centrée et cliquable**, vers `horus-lab.com`.

### Troisième passe du 13 août — direction artistique, et le passage à l'action

**Les boutons deviennent carrés et sans bordure.** Direction arrêtée par le
cabinet, dans la ligne de la pilule de navigation dont les angles avaient déjà
été redressés le 10 août. Les bordures partent avec les arrondis : elles
doublaient le fond des boutons pleins et faisaient bavocher les angles vifs. Une
seule exception, dictée par la lisibilité et non par le goût : `bouton--clair`
garde son contour, car sur une photographie un bouton clair sans contour se
dissout dans l'image.

**Le panneau des services est réduit à une liste.** Il portait sept fiches
détaillées, les six formes juridiques et un encart « Vous hésitez ? » à deux
boutons : la moitié de l'écran, pour redire ce que la page du service allait de
toute façon expliquer. Un menu conduit quelque part, il n'informe pas. Reste une
liste séparée d'un filet magenta, où l'on choisit et où l'on part. Les formes
juridiques ont disparu d'ici : la page Création les présente déjà toutes, et les
répéter revenait à tenir deux inventaires de la même chose.

**Le passage à l'action manquait.** C'est le vrai défaut que le cabinet a
relevé : les fiches expliquaient bien, puis renvoyaient vers une page Contact
générique où tout était à ressaisir — y compris le service qu'on venait de passer
trois minutes à lire. Un formulaire unique, `FormulaireService`, est désormais au
bas de chaque page, **pré-rempli sur ce que le visiteur regarde**.

Le sujet voyage dans l'adresse (`?service=…#demande`) plutôt que dans un état
client. Trois avantages : « Réserver une place » et « Demander mon bulletin »
restent de simples liens, les pages demeurent rendues par le serveur, et une
demande portant sur une session ou une formule précise se partage telle quelle.
Le service est **affiché et modifiable**, pas caché dans un champ masqué : le
visiteur doit voir sur quoi part sa demande, et l'on se trompe de page.

Branché sur les quatre fiches de service, la page Création, la page Formations
(chaque session) et la page Adhérent (chaque formule).

⚠️ **La demande n'est pas envoyée par le serveur.** Elle compose un message et
ouvre le client de messagerie du visiteur, à destination de
`contact@cga-brcgroup.com` ; il doit appuyer sur « Envoyer ». Un envoi réellement
automatique suppose un point d'entrée FastAPI **et des identifiants SMTP** que le
cabinet n'a pas fournis. Entre-temps, deux options : ce `mailto`, où la demande
part vraiment, ou un formulaire qui affiche « merci, c'est envoyé » alors que la
saisie est jetée en silence. La seconde est pire. Le bouton WhatsApp est là pour
la même raison, et il sera sans doute le plus utilisé.

**Les proformas sont téléchargeables** sur la page Création — les deux devis type
fournis par le cabinet, servis depuis `public/documents/` sous un nom normalisé.
Les fichiers d'origine portaient espaces et majuscules, qui font des adresses
fragiles une fois partagées par message. Le motif du `proxy` a dû être élargi :
sans cela, la négociation de langue interceptait `/documents/…` et rendait un 404.

**Un texte invisible, corrigé.** La carte `avantage` est dessinée pour le fond
indigo de l'accueil : texte blanc sur voile blanc translucide. Reprise telle
quelle sur les fiches de service, qui sont sur fond clair, elle donnait du blanc
sur blanc — le texte n'était tout simplement pas lisible. D'où `avantage--clair`.

**Le filigrane sort entier, et deux fois par page au plus.** Il débordait de
60 px à droite, si bien que la marque était coupée ; elle est désormais
entièrement dans le cadre, un peu plus petite et un cran plus discrète. Les pages
qui l'affichaient quatre ou cinq fois sont ramenées à deux.

**La frise du CGA revient au fer à gauche.** Posée dans une section centrée, elle
héritait du centrage : on ne savait plus quel récit allait avec quelle date. La
colonne est ramenée à gauche et bornée à 780 px — étalée sur toute la largeur,
l'année et son texte se retrouvaient à un mètre l'un de l'autre.

**Deux faux états actifs supprimés.** L'icône de la carte « Création
d'entreprise » s'allumait en magenta au repos, et l'entrée « Création
d'entreprise » du menu était surlignée par défaut. Dans les deux cas cela
ressemblait à une sélection en cours, alors que rien n'était sélectionné. Le
magenta est rendu au survol, où il signifie exactement une chose : le curseur est
ici.

**Le pied de page est allégé.** L'infolettre en part — elle occupait la moitié de
la largeur, avec titre et explication, sur chaque page — et rejoint le bandeau
« Parlons de votre projet », réduite au champ et au bouton : le titre de la
section dit déjà pourquoi on écrirait au cabinet. L'agrément ministériel est
retiré du pied, où il figurait pour la troisième fois après la barre du haut et
les fiches du cabinet. En dernière ligne, la signature « Powered by BïdaSoft ».

⚠️ **Le contenu anglais des quatre fiches et du formulaire de demande est en
français** pour les fiches. À faire traduire.

### Le devis en PDF — ce qui était demandé n'était pas possible tel quel

Le cabinet voulait que le bouton « Recevoir ce devis par WhatsApp » **joigne un
PDF**. Un lien `wa.me` ne transporte que du texte : aucune pièce jointe, quel que
soit le soin apporté au fichier. C'est une limite du protocole, pas un manque de
travail.

La solution retenue résout le besoin mieux qu'un fichier ne l'aurait fait : le
devis a **sa propre adresse**, `/estimation/devis?…`, mise en page pour l'écran
et pour le papier. Elle s'envoie comme un lien, s'ouvre sur n'importe quel
téléphone sans lecteur à installer, et se transforme en PDF d'un geste par la
commande d'impression du navigateur — « Enregistrer au format PDF » est proposé
sur Android comme sur iOS. Aucune bibliothèque de génération embarquée : quelques
centaines de kilo-octets épargnés à chaque visiteur.

Deux propriétés qui découlent du choix et qu'un PDF n'aurait pas eues : le devis
reste **calculé** — un lien ouvert plus tard affiche des montants cohérents avec
le barème du jour, non un chiffre figé — et il est **partageable sans base de
données**, toutes les réponses voyageant dans l'adresse.

Le message WhatsApp porte le récapitulatif chiffré **puis** le lien, dans cet
ordre : un destinataire sans réseau doit pouvoir lire les montants sans ouvrir
quoi que ce soit.

Le document dit sa date et dit qu'il **n'est pas une facture**, en clair dans le
corps et non en petits caractères : un document chiffré, daté et au nom du
cabinet sera lu comme un engagement s'il ne dit pas franchement le contraire.

### L'estimateur, vérifié

Barème éprouvé sur six cas : établissement, SARL au minimum légal, SARL à
999 999 puis à 1 000 000 FCFA — le droit proportionnel ne se déclenche qu'au-delà
de la référence, le total ne bouge donc pas entre les deux —, SA à Bafoussam
(14 semaines, les deux semaines de la ville hors guichet unique sont bien
ajoutées), et un jeu de paramètres volontairement absurdes, qui retombe sur les
valeurs sûres au lieu de produire une erreur. Les sous-totaux et le total
concordent.

### ⚠️ À rappeler au cabinet

**Le paiement Taramoney n'est pas branché.** Le cabinet a demandé que les
formules d'adhésion y renvoient, en précisant de le brancher « le moment venu »
et de le lui rappeler. Les boutons mènent toujours à la page Contact. Il faudra,
avant de commencer : les identifiants marchand, la documentation de l'API, et la
décision sur le lieu du branchement — très probablement un contexte backend dédié
à l'encaissement, et non le contexte L, qui ne porte que du contenu éditorial.

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
