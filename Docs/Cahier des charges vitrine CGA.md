# Cahier des charges — Site vitrine CGA Broad Range Consulting Group

Document de reprise pour développement. Décrit exactement les deux maquettes validées :
`Site vitrine CGA.dc.html` (bureau, 1440 px) et `Site vitrine mobile CGA.dc.html` (mobile, 390 px).
Rien dans ce document n'est optionnel : chaque valeur chiffrée est celle de la maquette.

---

## 0. Prompt de départ à coller

> Je te confie deux maquettes HTML d'un site vitrine : version bureau (1440 px) et version mobile
> (390 px). Tu dois les reproduire fidèlement en Next.js + React + Tailwind, sans réinterpréter le
> design. Le cahier des charges ci-dessous décrit chaque couleur, chaque animation, chaque
> comportement et chaque état. Respecte-le à la lettre.
>
> Règles absolues :
> 1. Aucune couleur, taille de police, rayon ou durée d'animation inventée. Tout est dans la
>    section « Jetons de design ».
> 2. Le site est bilingue français/anglais avec un dictionnaire unique. Aucune chaîne en dur dans
>    les composants.
> 3. Le site a deux thèmes, clair et sombre, pilotés par un jeu de jetons commutés. Aucun
>    `dark:` codé au cas par cas : on remplace l'objet de jetons.
> 4. Les cibles tactiles font 44 px minimum sur mobile, 48 px pour les actions principales.
> 5. Le mobile n'est pas un rétrécissement du bureau : il a sa propre composition, décrite en
>    partie 8.
> 6. Toutes les données chiffrées du site (tarifs, dates, coordonnées) viennent d'un fichier de
>    données unique, jamais du JSX.

---

## 1. Identité et jetons de design

### Palette, thème clair

| Rôle | Valeur |
|---|---|
| Fond de page | `#FAF9FC` |
| Fond alterné, cartes sur fond gris | `#FFFFFF` |
| Carte | `#FFFFFF` |
| Bordure | `#E5E1EC` |
| Texte principal | `#1A1523` |
| Texte secondaire | `#6B6480` |
| Indigo, fonds sombres | `#2E1B4D` |
| Magenta, action principale | `#8C2D86` |
| Violet, action secondaire | `#492F79` |
| Teinte violette, pastilles | `#EDE9F5` |
| Teinte magenta, encarts | `#F7E9F6` |
| Pied de page | `#1A1523` |
| Barre supérieure | `#1A1523` |
| Kicker, surtitre | `#8C2D86` |

### Palette, thème sombre

| Rôle | Valeur |
|---|---|
| Fond de page | `#14101C` |
| Fond alterné | `#1B1626` |
| Carte | `#221C30` |
| Bordure | `#332B46` |
| Texte principal | `#F4F1F8` |
| Texte secondaire | `#A79FB8` |
| Indigo | `#0F0B16` |
| Magenta | `#C05FB8` |
| Violet | `#C0A6E0` |
| Teinte violette | `#2A2340` |
| Teinte magenta | `#37223D` |
| Pied de page | `#0B0810` |
| Barre supérieure | `#0B0810` |
| Kicker | `#D9A3D6` |

### Sémantique de couleur

- **Magenta** : uniquement les actions du cabinet et ce qui lui appartient (honoraires, boutons
  principaux, pastille de menu actif).
- **Violet** : ce qui appartient à l'administration (frais officiels, actions secondaires).
- **Indigo** : fonds de bannière et de section pédagogique.
- Vert `#1E7A4C` pour les coches d'inclusion, rouge `#B3261E` pour les erreurs de saisie.

### Typographie

- Titres : **Poppins 600**.
- Textes courants et interface : **Inter 400, 500, 600**.
- Échelle bureau : titres de section 34 px / 1.25, titres de bannière 44 à 46 px / 1.16,
  titres de carte 18 px / 1.3, texte 13 à 15 px / 1.7, surtitre 12 px majuscules
  `letter-spacing: .08em`.
- Échelle mobile : titres de section 22 px, titre de bannière 26 à 27 px, carte 16 px,
  texte 12 à 13,5 px.
- Chiffres et montants : toujours `font-variant-numeric: tabular-nums`.
- Titres et paragraphes : `text-wrap: pretty`.

### Rayons et ombres

- Cartes : `border-radius: 10px` à `12px`.
- Boutons et champs : `8px` à `9px`.
- Barre de navigation flottante et méga-menu : `14px`.
- Pastilles et badges : `10px` à `14px`.
- Ombre au survol : `0 16px 32px rgba(0,0,0,.14)`, méga-menu `0 20px 44px rgba(0,0,0,.3)`.

---

## 2. Animations — la liste exhaustive

Deux animations nommées, définies une seule fois en CSS global :

```css
@keyframes cgaPoint {
  0%, 100% { transform: scale(1);    opacity: 1; }
  50%      { transform: scale(1.65); opacity: .45; }
}
@keyframes cgaMonte {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### 2.1 Pastille de menu actif
Chaque entrée de navigation porte à sa gauche une pastille de 6 px, `border-radius: 50%`.
Sur la page courante elle est magenta et anime `cgaPoint 1.6s ease-in-out infinite`.
Sur les autres entrées elle est `transparent` et `animation: none` — la pastille occupe
donc toujours sa place, seule sa visibilité change, ce qui évite tout décalage du menu.

### 2.2 Traits de défilement des bannières
Barres de 6 px de haut, `border-radius: 3px`.
- Trait actif : largeur **34 px**, fond magenta, `animation: cgaPoint 1.6s ease-in-out infinite`.
- Traits inactifs : largeur **12 px**, fond `rgba(255,255,255,.42)`, pas d'animation.
- Transition entre les deux : `transition: width .3s ease`.
- Toujours centrés horizontalement, à 22 px du bas sur l'accueil, 30 px sur les pages internes.
- Cliquables : un clic sélectionne la vue correspondante.

### 2.3 Fondu enchaîné des bannières
Chaque vue est en `position: absolute; inset: 0` avec `transition: opacity .8s ease`
(`.9s` sur les pages internes). La vue active a `opacity: 1` et `z-index: 2`, les autres
`opacity: 0` et `z-index: 1`. Rotation automatique toutes les **5 secondes**.
**La rotation se met en pause au survol de la bannière et reprend à la sortie du curseur.**

### 2.4 Ouverture du méga-menu
Le panneau apparaît avec `animation: cgaMonte .25s ease`. Il s'ouvre au survol de
« Nos services » et se ferme quand le curseur quitte l'ensemble barre + panneau.

### 2.5 Survols de cartes
Trois intensités selon le poids de la carte :

| Type de carte | Effet |
|---|---|
| Services, formations | `transform: translateY(-4px)` + `box-shadow: 0 16px 32px rgba(0,0,0,.14)`, `transition: transform .2s ease, box-shadow .2s ease` |
| Étapes « Comment ça se passe » | `translateY(-6px)` + ombre + `border-color` magenta, `transition .22s ease` |
| Avantages, formules, parcours, équipe, canaux, sous-menus | `translateY(-4px)` seul, `transition: transform .2s ease` (les sous-menus : `-2px`) |
| Avantages sur fond indigo | `translateY(-4px)` + `background: rgba(255,255,255,.1)` |
| Liens de pied de page | passage de `rgba(255,255,255,.78)` à `#fff` |
| Réseaux sociaux | fond magenta plein + `border-color` magenta |

### 2.6 Transition de thème
Le conteneur racine porte `transition: background .3s ease` : le basculement clair/sombre
n'est jamais brutal.

### 2.7 Ce qui ne doit pas être animé
Pas de parallaxe, pas d'apparition au défilement, pas de compteur qui s'incrémente,
pas de rotation d'icône. Le site est sobre : les seules animations sont celles listées ci-dessus.

---

## 3. Structure du site — huit pages

| Page | Rôle |
|---|---|
| `accueil` | Bannière à 3 vues, chiffres, services, pédagogie CGA, étapes, témoignages, questions |
| `creation` | Créer mon entreprise : pièces du dossier, questions propres à la création |
| `estimation` | L'estimateur de coût, page à part entière |
| `adherent` | Devenir adhérent : avantages, formules, parcours, conditions |
| `formations` | Calendrier des sessions, formation sur mesure |
| `cabinet` | Histoire, équipe, agences, partenaires |
| `contact` | Trois canaux, formulaire, coordonnées |
| `connexion` | Page de connexion au SaaS, atteinte par « Espace client » |

**L'accueil n'est pas une entrée de menu** : on y revient en cliquant le logo.

---

## 4. Barre de navigation

### Composition, de gauche à droite
1. **Logo** — version couleur en thème clair, version blanche en thème sombre. Cliquable,
   ramène à l'accueil. Deux fichiers distincts affichés sous condition, jamais une source
   calculée dynamiquement.
2. **Nos services** — ouvre le méga-menu au survol, mène à `creation` au clic.
   Porte un chevron vers le bas.
3. **Devenir adhérent**, **Formations**, **Le cabinet**, **Estimation**, **Contactez-nous**.
4. À droite : **sélecteur de langue**, **bascule de thème**, **Espace client**, **Nous joindre**.

### Comportement
- La barre est **flottante** : elle se superpose à la bannière, `position: absolute`, à 48 px
  des bords latéraux, ancrée sous la barre supérieure. Hauteur 72 px, `border-radius: 14px`,
  **sans bordure**, fond opaque de la couleur « carte » du thème.
- Au-dessus d'une bannière sombre, les entrées de menu sont **blanches** :
  entrée active `#FFFFFF` pur, entrées inactives `rgba(255,255,255,.82)`.
- La barre supérieure, au-dessus de la barre de navigation, fait 38 px : téléphone,
  courriel à gauche, mention d'agrément à droite.

### Sélecteur de langue
Une **liste déroulante** avec deux entrées : `🇫🇷 Français` et `🇬🇧 English`. Le drapeau
précède le nom, jamais de doublon de code. Le choix bascule l'intégralité du site.

### Bascule de thème
**Un seul bouton**, pas deux. Il affiche l'icône du mode vers lequel on va basculer :
en thème clair il montre la lune, en thème sombre il montre le soleil. Un clic bascule.

### Espace client
Mène à la page `connexion` du site. Ce n'est pas un lien externe : c'est la porte d'entrée
du SaaS, décrite en partie 7.

### Méga-menu « Nos services »
Carte arrondie de 14 px, à 48 px des bords latéraux, à 112 px du haut (soit 22 px sous la barre).
Composition : grille de deux colonnes de six cartes de prestation à gauche, encart indigo à droite.
Chaque carte : icône de 36 px sur fond teinté, titre, description brève, prix d'appel en magenta.
L'encart : « Vous hésitez ? », texte court, bouton magenta « Estimer mon projet » vers `estimation`,
bouton bordé « Être rappelé » vers `contact`.

**Les six prestations et leur destination :**

| Prestation | Prix d'appel | Destination |
|---|---|---|
| Création d'entreprise | dès 165 000 FCFA | `creation` |
| Suivi comptable et fiscal | dès 12 500 FCFA par mois | `adherent` |
| Prestations ponctuelles | dès 100 000 FCFA | `creation` |
| Domiciliation commerciale | dès 180 000 FCFA par an | `creation` |
| Formations | dès 75 000 FCFA par personne | `formations` |
| Conseil et mise en relation | sur devis | `contact` |

Attention : la carte « Création d'entreprise » **de l'accueil** mène à `estimation`
(son action est « Estimer »), tandis que le **sous-menu du même nom** mène à `creation`.
Ce sont deux destinations distinctes pour un même intitulé.

---

## 5. La bannière d'accueil

### Géométrie
Hauteur **plein écran** (`100vh`, minimum 800 px). La barre de navigation se superpose.
Trois vues en fondu enchaîné.

### Contenu de chaque vue
Photographie en fond `object-fit: cover`, dégradé par-dessus :
`linear-gradient(90deg, rgba(20,12,32,.97) 0%, rgba(20,12,32,.9) 46%, rgba(20,12,32,.5) 100%)`.
Puis, dans une colonne de 600 px à gauche : surtitre en pastille translucide, titre 44 px,
paragraphe, bouton magenta.

| Vue | Surtitre | Titre | Bouton |
|---|---|---|---|
| 1 | Centre de gestion agréé · Douala | Créez votre entreprise, nous tenons vos comptes | Estimer ma création → `estimation` |
| 2 | Adhésion au centre agréé | Un abattement de 50 % sur votre bénéfice imposable | Découvrir l'adhésion → `adherent` |
| 3 | Trente ans auprès des entrepreneurs camerounais | Plus de 500 entrepreneurs déjà accompagnés | Découvrir le cabinet → `cabinet` |

### Les quatre cartes de chiffres
**En pied de bannière**, pas dans une section séparée. Positionnées en `absolute`,
à 48 px des bords, 56 px du bas, en grille de quatre colonnes, 14 px d'écart.
Chaque carte : fond translucide en verre dépoli, icône dans une pastille, valeur en Poppins,
libellé en dessous. Elles réagissent au survol.

| Valeur | Libellé | Icône |
|---|---|---|
| 1994 | Création du cabinet | bâtiment |
| 500+ | Entrepreneurs accompagnés | groupe de personnes |
| 2020 | Agrément du ministère des Finances | bouclier avec coche |
| TPE, PME | Notre cœur de métier | mallette |

### Le formulaire « Lancer une démarche »
À droite de la bannière, 376 px de large, centré verticalement, en **verre dépoli sombre**
(`backdrop-filter: blur`) — il conserve ce fond sombre quel que soit le thème, puisqu'il est
toujours posé sur une photographie.

Champs, dans l'ordre :
1. **Votre démarche** — liste déroulante réellement fonctionnelle, six entrées correspondant
   aux six prestations.
2. **Nom et prénom** — champ de saisie libre, marque substitutive « Paule Diane Himsta ».
3. **Téléphone ou WhatsApp** — champ international : à gauche une liste déroulante de pays
   avec drapeau, qui renseigne automatiquement l'indicatif ; à droite le numéro.
   Par défaut le Cameroun, indicatif +237, marque substitutive « 699 902 184 ».
   La liste doit couvrir un large ensemble de pays, avec le drapeau visible dans le champ fermé.
4. Bouton magenta **Être rappelé** → ouvre le client de messagerie vers
   `contact@cga-brcgroup.com`, sujet et corps pré-remplis avec les valeurs saisies.

Sous le bouton : « Ou écrivez directement sur WhatsApp au 699 902 184. »

Important : le conteneur du formulaire ne doit pas capter le pointeur sur son rembourrage
transparent — seule la carte le capte, faute de quoi les cartes de chiffres situées dessous
deviennent insensibles au survol.

---

## 6. Sections de l'accueil, dans l'ordre

### 6.1 Nos services
Titre et sous-titre **centrés**. Le sous-titre « De la première idée à la déclaration annuelle »
et la ligne « Cabinet comptable, d'audit et de conseil… » tiennent chacun **sur une seule ligne**.
Grille de trois colonnes, six cartes. Chaque carte porte une **photographie de 158 px** en
en-tête avec dégradé, puis titre, description, et un pied avec le prix et l'action en magenta.

### 6.2 Comprendre le centre de gestion agréé
Fond indigo. Titre centré. Le paragraphe explicatif est réparti **sur exactement deux lignes**,
en deux éléments distincts, chacun en `white-space: nowrap`.
Puis quatre cartes d'avantages en fond translucide, puis un bouton centré vers `adherent`.

Les quatre avantages :
1. Abattement de 50 % sur le bénéfice déclaré
2. Exonération de patente les deux premières années
3. Contrôle de vos pièces avant dépôt
4. Moins de pénalités, un dialogue facilité

### 6.3 Comment ça se passe
Titre centré « Trois étapes, et vous suivez tout en ligne », **sur une seule ligne**.
Écart titre-cartes de 14 px seulement.
Trois cartes en **escalier** : hauteurs croissantes, bord supérieur de 4 px coloré,
numéro dans un rond de 46 px.

### 6.4 Témoignages
Trois cartes à **bordure pointillée**, marquées « à recueillir » — les vrais témoignages
seront fournis par le cabinet.

### 6.5 Questions fréquentes
Deux colonnes, quatre questions.

---

## 7. Page de connexion et flux d'accès

### Le contexte à comprendre
Le site vitrine est la porte d'entrée d'un SaaS comptable à **quatre niveaux d'accès** :

| Niveau | Qui | Ce qu'il voit |
|---|---|---|
| Plateforme | l'éditeur de la solution | crée les cabinets, support ; accès aux données métier par procédure exceptionnelle tracée |
| Cabinet | le super administrateur, la directrice | crée les entreprises clientes, invite leurs administrateurs, gère ses collaborateurs |
| Entreprise cliente | le dirigeant | invite ses collaborateurs, ne voit que son entreprise |
| Souscripteur | une personne physique ayant payé une prestation | suivi de sa prestation uniquement |

Les rôles internes au cabinet : comptable, réviseur, chargé de clientèle, fiscaliste,
chargé de formalités, commercial. Chacun a une barre latérale réduite à ses permissions.

### Les trois principes du flux
1. **Point d'entrée unique.** Une seule page de connexion pour toutes ces populations.
   Le routage vers le bon espace s'opère **après** authentification, selon le profil.
2. **Aucun mot de passe n'est jamais transmis.** La création de compte se fait par invitation :
   lien à usage unique valable **sept jours**, l'utilisateur définit lui-même son mot de passe.
   Trois états à gérer : lien valide, lien expiré avec demande de renvoi, lien déjà utilisé.
3. **Sélecteur d'espace.** Un utilisateur peut appartenir à plusieurs espaces — un dirigeant
   possédant deux sociétés, ou un collaborateur du cabinet par ailleurs dirigeant d'une
   entreprise cliente. Mémorisation du dernier espace utilisé, rebascule depuis l'en-tête
   sans repasser par l'écran de sélection.

### Le second chemin, depuis la vitrine
Le prospect configure sa prestation dans l'estimateur → obtient son devis chiffré → paie →
reçoit une **référence de dossier** qu'il peut retrouver même après avoir fermé la page →
le paiement confirmé déclenche l'envoi du lien de création de mot de passe.
Le souscripteur devient entreprise cliente quand le cabinet convertit son dossier.

### La page de connexion du site
Photographie en fond, dégradé indigo, barre de navigation superposée.
Carte de connexion contenant : identifiant, mot de passe, case « rester connecté »,
bouton de connexion, rappel de la double authentification pour les collaborateurs du cabinet,
les trois populations qui s'y connectent (Cabinet, Entreprise cliente, Souscripteur),
et un renvoi vers la souscription pour ceux qui n'ont pas encore de compte.

La section doit s'étirer selon la hauteur de sa carte (`min-height: 100vh`, jamais `height`),
faute de quoi le bas est rogné sur les petits écrans.

---

## 8. Estimateur de coût

Page dédiée. Deux colonnes : les questions à gauche, le devis à droite en position collante.

### Les quatre questions

**1. Quelle forme juridique ?** Grille de trois colonnes, six cartes cliquables.
La carte sélectionnée prend une bordure magenta de 2 px et un fond teinté.

| Forme | Frais officiels | Honoraires | Délai | Capital minimum | Associés |
|---|---|---|---|---|---|
| Établissement | 140 000 | 25 000 | 4 semaines | sans objet | 1 |
| SARL unipersonnelle | 210 000 | 35 000 | 6 semaines | 100 000 | 1 |
| SARL | 255 000 | 45 000 | 8 semaines | 100 000 | 2 et plus |
| SAS | 320 000 | 60 000 | 8 semaines | 100 000 | 2 et plus |
| SCI | 235 000 | 40 000 | 8 semaines | 100 000 | 2 et plus |
| Société anonyme | 980 000 | 220 000 | 12 semaines | 10 000 000 | 2 et plus |

**2. Capital social** — liste déroulante des montants légaux offerts pour la forme choisie,
plus une entrée « Autre montant » qui fait apparaître un champ de saisie libre.
Si le montant saisi est inférieur au minimum légal, bordure rouge et message d'aide en rouge.
Pour l'établissement : la question affiche « Sans objet pour cette forme ».

**3. Nombre d'associés** — liste déroulante de 2 à 10 selon la forme, plus « Autre nombre »
avec champ libre. Chaque associé au-delà du minimum légal ajoute **15 000 FCFA** d'honoraires.
Pour l'établissement et la SARL unipersonnelle : mention à la place du sélecteur.

**4. Ville d'immatriculation** — liste déroulante des dix-sept villes du Cameroun
(Douala, Yaoundé, Bafoussam, Garoua, Bamenda, Maroua, Ngaoundéré, Bertoua, Buéa, Ebolowa,
Kribi, Limbé, Édéa, Kumba, Dschang, Foumban, Nkongsamba), plus « Une autre ville » avec
champ libre. **Hors Douala et Yaoundé, le délai augmente de deux semaines.**

### Les deux options
Cases à cocher : suivi comptable et fiscal 12 mois à 12 500 FCFA par mois, et domiciliation
commerciale 12 mois à 180 000 FCFA. La domiciliation s'ajoute aux honoraires.

### Le devis, colonne de droite
Bordure magenta de 2 px, en-tête indigo rappelant la configuration.
Puis, dans l'ordre :
1. **Frais officiels avancés**, en violet, avec leur détail ligne à ligne et leur total.
2. **Nos honoraires**, en magenta, avec leur détail et leur total.
3. **Barre de répartition** : une seule barre de 12 px partagée en deux, la part violette
   des frais officiels et la part magenta des honoraires, avec les pourcentages en légende.
4. **Total à régler**, dans un encart teinté magenta, en 27 px.
5. Délai annoncé et suivi comptable, en deux encarts.
6. Bouton **Souscrire en ligne**, puis **Recevoir ce devis par WhatsApp**.
7. Mention : estimation indicative, devis définitif confirmé après examen, sans frais de dossier.

**La séparation entre frais officiels et honoraires est le cœur du modèle.**
Sur une création de SARL à 300 000 FCFA, 255 000 sont des frais officiels reversés aux
administrations et 45 000 seulement des honoraires. C'est un argument commercial et une
contrainte comptable : les deux masses ne doivent jamais être confondues visuellement.

Si le capital dépasse le capital de référence, une majoration de 0,4 % de l'excédent
s'ajoute à la ligne « Enregistrement des statuts » des frais officiels.

---

## 9. Version mobile — 390 px

### Ce qui change
La version mobile n'est pas une réduction : c'est une composition propre.

**En-tête** — 60 px, logo à gauche, deux boutons de 44 px à droite : le sélecteur de langue
et le bouton de menu. Langue, thème, espace client et « nous joindre » passent dans le tiroir.

**Tiroir de navigation** — glisse depuis la droite sur 214 px des 390, voile assombri derrière,
fermeture au toucher du voile. **Deux niveaux** : le premier liste les six entrées de menu,
« Nos services » ouvre le second niveau où une flèche de retour remplace le titre et où les
six prestations s'affichent en cartes de 60 px avec icône et prix.
Les entrées du premier niveau doivent tenir sans débordement.

**Bannières** — verticales, dégradé du haut vers le bas
(`rgba(20,12,32,.72)` à `rgba(20,12,32,.95)`), texte centré au-dessus de la photographie,
traits de défilement conservés et centrés. L'accueil garde ses trois vues, les pages internes
en ont deux.

**Cartes de chiffres** — en pied de bannière, grille de deux colonnes.

**Toutes les grilles passent en pile verticale** : services, avantages, formules, formations,
canaux de contact, équipe, partenaires.

**Estimateur** — une colonne. Les six formes juridiques passent en grille de deux, les trois
listes déroulantes s'empilent en pleine largeur, le devis reste sous les questions.

**Champ téléphone** — même logique internationale : drapeau et indicatif à gauche,
numéro à droite.

**Pied de page** — liens en lignes de 44 px, coordonnées, deux réseaux sociaux.

### Cibles tactiles
44 px minimum pour toute zone touchable, 48 à 52 px pour les actions principales.

---

## 10. Contenu — ce qui est vrai et ce qui ne l'est pas

### Faits sourcés, à conserver tels quels
- Cabinet fondé en **1994** par Gabriel NGASSE, ancien manager de Total Cameroun, initialement
  pour aider les gérants de stations-service à tenir leur comptabilité.
- **2000** : ouverture aux TPE et PME.
- **2013** : Paule Diane HIMSTA prend la direction générale.
- **2020** : agrément du ministre des Finances, **arrêté n° 00000048 du 28 janvier 2020**.
- Plus de **500 entrepreneurs** accompagnés.
- Téléphone **+237 233 42 48 47**, WhatsApp **699 902 184**,
  courriel **contact@cga-brcgroup.com**.
- Facebook : `https://web.facebook.com/CGABroadRangeConsulting/`
- LinkedIn : `https://cm.linkedin.com/company/cga-broad-range-consulting`
- Établi à **Douala**.

### À ne jamais inventer
Aucun engagement de délai de réponse (« réponse dans la journée », « du lundi au samedi »,
« avant 16 heures ») : le cabinet ne les a jamais donnés. Aucune horaire d'ouverture précise.
Aucun nombre d'agences autre que Douala tant qu'il n'est pas confirmé.
Aucun témoignage client tant qu'il n'est pas recueilli.

### Restant à confirmer par le cabinet
Adresse exacte du bureau de Douala, horaires d'ouverture, témoignages clients,
photographies réelles de l'équipe et des locaux.

---

## 11. Liens sortants

| Élément | Destination |
|---|---|
| Tous les boutons WhatsApp | `https://wa.me/237699902184` en nouvel onglet |
| Carte téléphone | `tel:+237233424847` |
| Carte courriel, bouton « Être rappelé » | `mailto:contact@cga-brcgroup.com` |
| Facebook, LinkedIn | adresses ci-dessus, en nouvel onglet |
| Espace client | page `connexion` interne |
| Prendre rendez-vous | page `contact` interne |

---

## 12. Erreurs à ne pas reproduire

Ces défauts ont été rencontrés puis corrigés dans les maquettes. Ils sont énumérés pour
éviter de les réintroduire.

1. **Deux consommateurs d'une même donnée.** Les cartes de l'accueil et les sous-menus
   dérivent de la même liste de prestations mais n'ont pas la même destination pour
   « Création d'entreprise ». Ne pas modifier la destination commune.
2. **Bannière à hauteur figée.** Utiliser `min-height`, jamais `height`, sur les sections
   dont le contenu peut dépasser.
3. **Conteneur transparent qui capte le pointeur.** Le rembourrage du formulaire de bannière
   bloquait le survol des cartes situées dessous.
4. **Rotation qui change la cible sous le curseur.** Le diaporama doit se mettre en pause
   au survol.
5. **Texte noir sur fond sombre.** Vérifier chaque contraste après le passage en thème sombre,
   notamment les éléments dont la couleur est codée en dur.
6. **Débordement du menu.** Chaque ajout d'entrée doit être vérifié à 1440 px sur bureau
   et dans le tiroir sur mobile.
7. **Tirets cadratins.** Le français du site n'en utilise pas : virgules ou points médians.
