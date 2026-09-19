# Le document de conception, en local

`architecture-multitenant-cga.html` est la source du document publié à
l'adresse <https://claude.ai/code/artifact/246aed40-fb27-4074-809d-c4b4e2c96750>.

Il s'ouvre directement dans un navigateur : aucune dépendance, aucun script,
tout est dans le fichier hormis deux polices chargées depuis Google Fonts.

## Pourquoi une copie ici

Le fichier de travail vivait dans un répertoire temporaire, qui a été vidé une
fois en cours de projet. La copie est versionnée avec le code pour que le
document survive à cela, et pour qu'un développeur puisse le lire sans compte.

## L'écart avec la version publiée

**Aucun.** La version publiée est la **119**, et ce fichier la porte.

La publication a longtemps buté sur une erreur réseau du service de publication
(`artifact content fetch failed`), qui a refusé les versions 9, 10, 12, 13, 17 et 18
plusieurs fois chacune, puis de nouveau la 27. Le refus est intermittent : la même
publication, tentée une seconde ou une troisième fois sans rien changer au fichier,
finit par passer. Il n'y a donc rien à corriger dans le document quand cela arrive, seulement
à réessayer.

## Comment republier

Modifier ce fichier, puis republier **à la même adresse** en passant l'URL
ci-dessus. Publier sans elle créerait un second document au lieu de mettre celui-ci
à jour, et le lien déjà partagé continuerait de montrer l'ancienne version.

⚠️ Avant de republier, vérifier trois choses que le document tient depuis le début :
aucun tiret quadratin dans le texte, et le numéro de version de l'en-tête
incrémenté d'un seul cran par rapport à ce qui est en ligne. La version en ligne
se lit en tête du document publié ; elle n'est pas toujours celle que ce fichier
porte, puisqu'un refus de publication laisse le fichier en avance.

La troisième est née au pas 40 : **les identifiants d'ancre ne suivent pas les
numéros affichés.** `s20` est la section 36, `s21` la section 40. Ajouter une
section en prenant l'identifiant libre suivant a produit six ancres en double,
et un sommaire qui renvoyait ailleurs que là où il disait. Contrôler donc aussi :
pas de `id` de section en double, aucun lien de sommaire sans cible, aucune
section absente du sommaire.
