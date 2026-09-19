# Déploiement en orchestrateur de conteneurs

Ce dossier porte les manifestes. Ils sont **versionnés avec le code** parce qu'ils
en dépendent : les variables qu'ils posent doivent exister dans `Configuration`, et
`tests/test_manifestes_kubernetes.py` le vérifie à chaque proposition.

⚠️ **Ce contrôle a trouvé deux défauts dans ces manifestes le jour où il a été
écrit** : une variable inventée, et une clé de secret nommée comme une variable
d'environnement. *Un manifeste qui nomme une clé inexistante ne fait rien, en
silence.*

## L'ordre d'application

| | Fichier | Ce qu'il pose |
| --- | --- | --- |
| 1 | `00-espace-et-configuration.yaml` | L'espace de noms, la configuration, le **gabarit** de secret |
| 2 | `10-fichiers-deposes.yaml` | Le volume des justificatifs |
| 3 | `15-migration.yaml` | `alembic upgrade head`, **avant tout le reste** |
| 4 | `20-api.yaml` | L'API en trois répliques, et son service |
| 5 | `30-ordonnanceur.yaml` | La boucle de fond, **une** réplique |
| 6 | `40-entree-et-tls.yaml` | L'entrée et le certificat générique |

⚠️ Le secret n'est **pas** dans cette liste : il se crée hors du dépôt.

```
kubectl -n cga create secret generic cga-secrets \
  --from-literal=CGA_URL_BASE_DE_DONNEES='postgresql+psycopg://cga_app:...' \
  --from-literal=url-base-migration='postgresql+psycopg://cga_migration:...' \
  --from-literal=CGA_CLE_CHIFFREMENT='...'
```

## Les six décisions qui comptent

**La vivacité ne teste jamais la base.** `/sante` rend 503 quand la base est
injoignable : c'est ce qu'il faut pour retirer un pod du service, et exactement ce
qu'il ne faut pas pour le redémarrer. Redémarrer ne répare pas une base tombée ; on
obtient une flotte en redémarrage et des journaux perdus à chaque cycle. La vivacité
teste donc le port, rien d'autre.

**Deux rôles PostgreSQL, deux clés de secret.** `cga_migration` possède les tables,
`cga_app` ne les possède pas — et c'est ce qui l'empêche de contourner les
politiques de cloisonnement. Le même rôle pour les deux rend le cloisonnement
inopérant *sans qu'aucune erreur ne se produise*.

**Le volume est `ReadWriteMany`.** `ReadWriteOnce` marche à une réplique et casse à
la seconde, sans message utile. Le défaut n'apparaît jamais en essai.

**La migration est un `Job`.** Un conteneur d'initialisation tournerait sur chaque
pod : trois répliques, trois migrations simultanées, et une migration qui s'exécute
pendant qu'une ancienne version sert le trafic.

**Le certificat est générique, donc DNS-01.** Chaque cabinet a son sous-domaine, qui
répond dans la seconde sans redéploiement. HTTP-01 ne délivre pas de générique — il
prouve la possession d'un nom en le servant, et un nom qu'on ne connaît pas encore ne
sert rien. ⚠️ C'est une contrainte sur le choix du registrar, à décider **avant**
l'achat du domaine.

**L'ordonnanceur est séparé, à une réplique.** Le verrou consultatif rend deux
répliques *correctes* — c'est ce qui rend la mise à jour progressive sûre — mais le
gain est nul et le bruit réel.

## Ce que ces manifestes ne font pas

- **Ils ne déploient pas PostgreSQL.** Une base de production se prend administrée,
  ou s'installe avec un opérateur qui sait sauvegarder et restaurer. Un `StatefulSet`
  écrit à la main donne l'illusion des deux.
- **Ils ne portent ni supervision ni journalisation centralisée.** Ce sont des choix
  d'exploitation, pas de code.
- **Ils ne sont pas éprouvés sur un cluster réel.** Ils sont lus, contrôlés contre la
  configuration, et mutés — pas appliqués. C'est écrit plutôt que sous-entendu.

⚠️ **La section 37 du dossier de conception arrête l'hébergement sur un serveur
unique**, et dit qu'*« une machine ne fait pas de la haute disponibilité »*. Ces
manifestes sont la marche suivante, préparée pour que l'ajout de machines ne coûte
rien au code. Ils ne la remplacent pas.
