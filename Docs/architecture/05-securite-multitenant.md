# 05 · Sécurité, multi-tenant et audit

Les données manipulées sont les données fiscales de tiers. Ce sont parmi les plus sensibles
qu'une PME confie à un prestataire, et le CGA engage son agrément sur leur traitement.

## 1. Multi-tenant

Le **CGA est le tenant**, ses adhérents sont des sous-entités. Cette conception anticipe la
revente de la plateforme à d'autres centres.

- `tenant_id` sur chaque table, `entreprise_id` sur celles rattachées à un dossier.
- Filtrage appliqué **dans la couche de persistance** — session SQLAlchemy avec filtre
  systématique —, jamais laissé au développeur qui écrit la requête.
- Cloisonnement supplémentaire **par portefeuille** : un comptable ne voit que les dossiers
  qui lui sont affectés, sauf rôle transverse explicite.
- Un test d'isolation par contexte, obligatoire en intégration continue : une requête
  effectuée dans le tenant A ne doit jamais rendre une ligne du tenant B.

## 2. RBAC

Rôles calqués sur les acteurs réels du cabinet (voir [00](00-vision-et-metier.md)) :
chargé de clientèle, comptable, réviseur, fiscaliste, chargé de formalités, direction,
administrateur, plus deux rôles externes — adhérent et inspecteur assistant, ce dernier en
lecture et avis seulement.

Actions particulièrement sensibles, à protéger nominativement :

| Action | Rôle | Contrainte |
|---|---|---|
| Écarter un constat | Réviseur | Motif obligatoire, pièce d'appui attendue |
| Valider une écriture | Comptable | Devient immuable |
| Contre-passer | Comptable | Motif obligatoire, lien vers l'origine |
| Déposer une déclaration | Réviseur | **MFA exigée** |
| Modifier un paramètre ou une règle | Fiscaliste | Versionné, journalisé, validation nommée |
| Clôturer un exercice | Réviseur ou direction | Verrouille la période |
| Remplacer son second facteur | Le titulaire | **Session renforcée par l'appareil actuel** (pas 60) |
| Réinitialiser le second facteur d'un tiers | Administrateur | Motif obligatoire, jamais le sien, sessions du titulaire fermées, titulaire prévenu |

⚠️ **Le second facteur ne se remplace pas avec le mot de passe seul.** Jusqu'au pas 60,
l'enrôlement écrasait le secret de tout compte connecté et rendait le nouveau : un mot de
passe volé suffisait à enrôler son propre appareil, renforcer la session et déposer. Tout
enrôlement prévient désormais le titulaire par courriel ; un remplacement exige un code de
l'appareil actuel ; un appareil perdu se réinitialise par un tiers habilité.

**Le premier enrôlement se prouve par la boîte aux lettres** (pas 62). La demande n'affiche
aucune clé : un lien valable trente minutes part à l'adresse du compte, et la clé ne s'affiche
qu'à qui le présente depuis la session du même compte. Le lien n'est utilisé qu'au clic, jamais à
l'ouverture de la page, pour qu'un antivirus de messagerie qui l'ouvre ne le consomme pas. Un lien
d'enrôlement ne définit pas de mot de passe, et un lien de mot de passe ne confirme pas un enrôlement.

Limite connue : qui détient **à la fois** le mot de passe et la messagerie d'un collaborateur jamais
enrôlé peut enrôler à sa place. C'est la limite de toute preuve par courriel.

## 3. Journal d'audit inaltérable

Append-only : aucune mise à jour, aucune suppression, y compris pour un administrateur.

Chaque entrée porte horodatage, acteur, tenant, action, objet, valeurs avant et après, et
l'**empreinte de l'entrée précédente**. Ce chaînage par hachage rend toute altération
détectable — argument fort en cas de contrôle DGI.

Le coût est faible si on le prévoit dès le départ ; l'ajouter après coup est impossible sans
réécrire l'historique, c'est-à-dire sans détruire la garantie recherchée.

## 4. Documents et rétention

- GED sur stockage objet, chiffrement au repos, **empreinte de chaque document** enregistrée
  à l'entrée.
- Conservation **10 ans** pour les documents comptables, conformément au SYSCOHADA révisé.
- Date de purge calculée et portée par le document. Purge par traitement journalisé, jamais
  par suppression manuelle.

## 5. Points à vérifier avant mise en production

Ces éléments ne relèvent pas de la conception mais du droit applicable, et n'ont pas été
tranchés :

- Le cadre camerounais de protection des données personnelles applicable au traitement de
  données fiscales de tiers.
- L'existence éventuelle d'une **obligation d'hébergement local** des données.
- Les obligations propres au statut de CGA en matière de conservation et de communication à
  l'administration.

Voir [09-questions-ouvertes.md](09-questions-ouvertes.md).

## 6. Secrets

Aucun secret en dépôt. `.env` est ignoré par Git, `.env.example` documente les variables
attendues sans valeur. Les identifiants d'accès aux portails DGI et CNPS, quand les
adaptateurs existeront, relèvent d'un coffre et non d'une variable d'environnement.
