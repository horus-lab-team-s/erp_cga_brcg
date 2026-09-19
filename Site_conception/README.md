# Site de conception de la plateforme CGA Broad Range

Conception et réalisation : **TCHAMBA TCHAKOUNTE Edwin**, ingénieur informaticien.

Ce projet sert la documentation de conception comme un site, déployable sur Vercel,
afin qu'elle se partage par une adresse plutôt que par un fichier joint.

## Les quatre pages

| Adresse | Ce qu'elle porte | Comment elle est rendue |
| --- | --- | --- |
| `/` | Ce que fait la plateforme, les chiffres mesurés, et comment lire le site | Page React, quelques kilo-octets |
| `/prerequis` | Quatre onglets : les concepts, les langages, les outils, le poste de travail | Page React, onglets au clavier |
| `/document` | Le document de conception complet | **Fichier engendré**, servi tel quel |
| `/mise-en-oeuvre` | Ce qu'il faut faire pour lancer la solution, et ce qui bloque | Page React |

⚠️ **Seul le document est servi comme fichier**, et l'encadré plus bas dit pourquoi.
Les trois autres pages sont légères et restent des pages React : c'est la taille du
contenu qui décide, pas une préférence de principe.

## Le principe : une seule source

⚠️ **Le document ne vit pas ici.** Il vit dans `Docs/architecture/document-de-conception/`.
Ce projet ne fait que le prendre et le servir. Rien, dans ce dossier, ne doit être
modifié à la main pour changer le texte, un chiffre ou une figure : cela créerait une
seconde version du document, et c'est celle-là que les lecteurs liraient, tandis que
l'équipe continuerait de mettre à jour la première.

```
Docs/architecture/document-de-conception/architecture-multitenant-cga.html   la source
                    │
                    │  node outils/importer-le-document.mjs   (joué par `prebuild`)
                    ▼
        contenu/document.html    le corps du document, seul
        contenu/document.css     sa feuille de style, avec le thème sombre dupliqué
        contenu/theme.css        les seules variables de couleur, pour les pages React
        contenu/document.json    son titre, sa version, ses compteurs, son sommaire
        public/document.html     la page complète du document, servie telle quelle
```

⚠️ **`theme.css` existe pour qu'il n'y ait qu'une palette.** Les pages du site ne
partagent pas la feuille du document, qui met en forme un texte long ; elles partagent
ses couleurs. Les recopier à la main aurait donné deux identités qui divergent au
premier ajustement, et un lecteur qui passe d'une page au document verrait le sol
bouger sous lui.

⚠️ **La navigation vient de `donnees/site.json`**, lu à la fois par l'importateur, qui
la pose dans la page du document, et par les pages React. Une barre recopiée dans deux
langages diverge au premier onglet ajouté : l'un des deux l'oublie, et la page devient
introuvable autrement qu'en la devinant.

## Pourquoi la page est un fichier, et non un composant React

Mesuré au pas 120, sur la version 119 du document (966 Ko de texte) :

| Rendu | Servi (brut) | gzip | brotli |
| --- | --- | --- | --- |
| Par React (composant serveur) | 2 177 075 o | 491 Ko | 340 Ko |
| Par fichier engendré | 970 888 o | 239 Ko | 218 Ko |

Un composant serveur envoie deux fois le document : une fois en HTML, et une fois dans
la charge utile de navigation que React rejoue côté client. Sur un document de 966 Ko
de texte, cela double le poids sans rien apporter : la page ne porte aucun état, aucune
donnée à rafraîchir, aucun rendu qui dépende du lecteur. Elle est donc assemblée à la
construction et servie comme fichier statique, et `next.config.ts` réécrit la racine
`/document` vers `/document.html`.

Next reste utile pour le reste : les métadonnées (titre, description, aperçu de partage),
la page « introuvable », le thème posé avant le premier rendu, et surtout la
construction, qui rejoue l'import à chaque déploiement.

## Les commandes

```bash
npm install
npm run dev     # importe le document, puis sert sur http://localhost:3000
npm run build   # importe le document, puis construit
npm start       # sert la construction
npm run importer   # réimporte seul, après avoir modifié le document source
```

⚠️ `dev` et `build` rejouent l'import (`predev`, `prebuild`). Après avoir modifié le
document source pendant que `next dev` tourne, il faut donc soit rejouer
`npm run importer`, soit relancer `npm run dev` : le serveur de développement ne
surveille pas un fichier qui vit hors du projet.

## Le déploiement sur Vercel

1. Importer le dépôt dans Vercel.
2. **Root Directory** : `Site_conception`. C'est le seul réglage qui n'est pas deviné.
3. Framework preset : *Next.js* (détecté), commande de construction `npm run build`
   (détectée), commande d'installation `npm install` (détectée).
4. Aucune variable d'environnement : le site ne parle à aucun service.

⚠️ **Ne pas cocher « Include files outside the root directory » comme facultatif : il
est nécessaire.** Vercel clone tout le dépôt, puis se place dans `Site_conception` ;
l'importateur remonte d'un cran pour lire `../Docs/...`. Si cette remontée est coupée,
la construction ne s'arrête pas : l'importateur se rabat sur le dernier import présent
dans `contenu/` et **écrit un avertissement bruyant sur la sortie d'erreur**. Le site
part alors avec une version périmée du document, silencieusement pour le visiteur.
C'est pourquoi il faut lire cet avertissement dans le journal de construction.

C'est aussi la raison pour laquelle `contenu/` et `public/document.html` sont versionnés
et non ignorés : ils sont le filet du rabattement. Ils pèsent environ 1,9 Mo et changent
à chaque version du document ; c'est le prix d'un déploiement qui ne casse pas quand la
source est hors de portée.

## Ce que le site n'est pas

- Il **n'est pas indexé** (`robots: { index: false }` dans `app/layout.tsx`). Le document
  décrit l'architecture interne d'un cabinet : il se partage par son adresse, il ne se
  cherche pas sur un moteur.
- Il **ne porte aucune donnée** du produit : ni base, ni API, ni session. Le rendre public
  n'expose rien d'autre que le document lui-même.
- Il **ne reformate rien** : ni coupe, ni résumé, ni découpage en pages. Ce que le lecteur
  voit est ce que l'équipe écrit.

## Les fichiers, et à quoi chacun sert

| Fichier | Rôle |
| --- | --- |
| `outils/importer-le-document.mjs` | Découpe la source, duplique le thème sombre en `[data-theme]`, pose l'ancre `#sommaire`, écrit `contenu/` et `public/document.html`. |
| `next.config.ts` | La réécriture de `/` vers le fichier engendré, et la raison mesurée de ce choix. |
| `app/layout.tsx` | Les métadonnées, les polices, le thème posé avant le premier rendu. Il **ne sert pas** le document. |
| `app/composants/` | La coquille partagée, les onglets, et les petits blocs de contenu. |
| `app/prerequis/` | Les quatre onglets de la prise en main, un fichier chacun. |
| `app/mise-en-oeuvre/` | Les neuf étapes du lancement, avec leur état. |
| `donnees/site.json` | La navigation, le concepteur, les chiffres. Source unique des deux barres. |
| `app/not-found.tsx` | La seule page réellement rendue par React. |
| `contenu/`, `public/document.html` | Engendrés. Versionnés comme filet, jamais modifiés à la main. |
